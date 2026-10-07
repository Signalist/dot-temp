import hashlib
import tempfile
import shutil
import signal
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from w6kit.core import (analyze_run, freeze_split, integrate, read_json, read_lines,
                        validate_run, write_json, write_lines)
from w6kit.demo import demo
from w6kit.analysis import failure_budget, import_meter, fit_service, evaluate_service
from w6kit.cap import run_cap_session
from w6kit.acquire import telemetry, completion_request


class KitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)/"synthetic"
        demo(self.root)
        self.run = self.root/"run_00"
    def tearDown(self):
        self.tmp.cleanup()
    def mutate_meta(self, fn):
        m=read_json(self.run/"manifest.json"); fn(m); write_json(self.run/"manifest.json",m)
    def mutate_lines(self, name, fn):
        p=self.run/name; rows=read_lines(p); fn(rows); p.unlink(); write_lines(p,rows)
    def test_demo_labels(self):
        self.assertEqual(read_json(self.root/"SUMMARY.json")["hardware_runs"],0)
    def test_energy_cycle_decomposes(self):
        r=analyze_run(self.run); e=r['energy']['gpu_dc']
        self.assertAlmostEqual(e['dynamic_cycle_J'],125)
        self.assertAlmostEqual(e['dynamic_service_J']+e['dynamic_recovery_J'],e['dynamic_cycle_J'])
        self.assertAlmostEqual(r['EOS_delay_s'],.02)
    def test_negative_dynamic_not_clamped(self):
        rows=[{'t_ns':0,'power_W':9,'baseline_W':10},{'t_ns':1_000_000_000,'power_W':9,'baseline_W':10}]
        self.assertEqual(integrate(rows,0,1_000_000_000,True),-1)
    def test_duplicate_timestamp_rejected(self):
        self.mutate_lines('power.jsonl',lambda r:r[1].update(t_ns=r[0]['t_ns']))
        with self.assertRaisesRegex(ValueError,'duplicate'): validate_run(self.run)
    def test_gap_rejected(self):
        self.mutate_lines('power.jsonl',lambda r:r.pop(4))
        with self.assertRaisesRegex(ValueError,'gap'): validate_run(self.run)
    def test_mixed_run_rejected(self):
        self.mutate_lines('power.jsonl',lambda r:r[1].update(run_id='other'))
        with self.assertRaisesRegex(ValueError,'provenance'): validate_run(self.run)
    def test_missing_true_eos_rejected_for_dc(self):
        self.mutate_lines('events.jsonl',lambda rows:[r.update(true_eos_ns=None) for r in rows if r['type']=='eos_visible'])
        validate_run(self.run)
        with self.assertRaisesRegex(ValueError,'true EOS missing'): validate_run(self.run,'w6-dc')
    def test_no_pcc_claim_from_dc(self):
        with self.assertRaisesRegex(ValueError,'PCC channel'): validate_run(self.run,'pcc')
    def test_censoring_required(self):
        self.mutate_lines('events.jsonl',lambda rows:[r.update(stop_class='length') for r in rows if r['type']=='eos_visible'])
        with self.assertRaisesRegex(ValueError,'censored'): validate_run(self.run)
    def test_no_fabricated_restored_state(self):
        self.mutate_lines('events.jsonl',lambda rows:[r.update(state={'temperature_C':90}) for r in rows if r['type']=='terminal_state'])
        with self.assertRaisesRegex(ValueError,'not restored'): validate_run(self.run)
    def test_gpu_only_cannot_pass_dc_gate(self):
        self.mutate_meta(lambda m:m.update(tier='GPU_ONLY'))
        with self.assertRaisesRegex(ValueError,'external'): validate_run(self.run,'w6-dc')
    def test_sampling_uncertainty_required(self):
        self.mutate_meta(lambda m:m.update(clock_error_ns=None))
        with self.assertRaisesRegex(ValueError,'unknown'): validate_run(self.run)
    def test_mismatched_evidence_provenance_rejected(self):
        self.mutate_meta(lambda m:m.update(evidence='MEASURED'))
        with self.assertRaises(ValueError): validate_run(self.run)
    def test_session_leakage(self):
        r=read_json(self.root/'registry.json'); r['runs'][4]['session_id']=r['runs'][0]['session_id']
        write_json(self.root/'bad_registry.json',r)
        with self.assertRaisesRegex(ValueError,'session leakage'): freeze_split(self.root/'bad_registry.json',self.root/'bad_split.json')
    def test_transfer_leakage(self):
        r=read_json(self.root/'registry.json'); r['runs'][-1]['device_model_unit']=r['runs'][0]['device_model_unit']
        write_json(self.root/'bad_registry.json',r)
        with self.assertRaisesRegex(ValueError,'transfer unit'): freeze_split(self.root/'bad_registry.json',self.root/'bad_split.json')
    def test_fit_does_not_read_confirmation_events(self):
        (self.root/'run_04'/'events.jsonl').write_text('invalid JSON')
        fit_service(self.root,self.root/'frozen_split.json',self.root/'second_fit.json')
    def test_refit_cannot_overwrite_frozen(self):
        with self.assertRaisesRegex(ValueError,'already exists'): fit_service(self.root,self.root/'frozen_split.json',self.root/'frozen_service_model.json')
    def test_binomial_budget(self):
        self.assertEqual(failure_budget(.05,.05)['n_zero_failure_iid_units'],59)
        self.assertEqual(failure_budget(.01,.05)['n_zero_failure_iid_units'],299)
        self.assertEqual(failure_budget(.05,.05,5)['n_zero_failure_iid_units'],90)
    def test_meter_alignment(self):
        spec={'acquisition_id':'a','run_id':'r','clock_id':'h','evidence':'SIMULATED','channel':'gpu_dc','boundary':'all rails',
              'clock_transform_id':'sync','calibration_id':'cal','sync_before_id':'before','sync_after_id':'after',
              'source_clock_id':'sensor','clock_error_ns':1,'slope':1,'offset_ns':100,'time_scale_to_ns':1000,'power_scale_to_W':.001,'baseline_W':1}
        write_json(self.root/'spec.json',spec)
        (self.root/'meter.csv').write_text('sensor_timestamp,arrival_monotonic_ns,power,status\n1,1200,2000,ok\n2,2300,3000,ok\n')
        import_meter(self.root/'meter.csv',self.root/'spec.json',self.root/'mapped.jsonl')
        rows=read_lines(self.root/'mapped.jsonl')
        self.assertEqual(rows[0]['t_ns'],1100); self.assertEqual(rows[0]['power_W'],2)
    def test_dryrun_no_nvml_or_network(self):
        cfg=Path(__file__).parents[1]/'configs'
        with patch('w6kit.acquire.nvml_open',side_effect=AssertionError('GPU forbidden')):
            self.assertEqual(telemetry(cfg/'telemetry.example.json','unused')['GPU_calls'],0)
        with patch('urllib.request.build_opener',side_effect=AssertionError('network forbidden')):
            self.assertEqual(completion_request(cfg/'request.example.json','unused')['network_calls'],0)

    def test_natural_eos_cannot_be_length(self):
        self.mutate_lines('events.jsonl',lambda rows:[r.update(finish_reason='length') for r in rows if r['type']=='eos_visible'])
        with self.assertRaisesRegex(ValueError,'natural EOS'): validate_run(self.run)
    def test_request_identity_rejected(self):
        self.mutate_lines('events.jsonl',lambda rows:[r.update(request_id='wrong') for r in rows if r['type']=='progress'])
        with self.assertRaisesRegex(ValueError,'request identity'): validate_run(self.run)
    def test_too_many_tokens_rejected(self):
        self.mutate_lines('events.jsonl',lambda rows:[r.update(completed_tokens=10000) for r in rows if r['type']=='progress'])
        with self.assertRaisesRegex(ValueError,'useful progress'): validate_run(self.run)
    def test_zero_service_rejected(self):
        self.mutate_lines('events.jsonl',lambda rows:[r.update(true_eos_ns=3_000_000_000) for r in rows if r['type']=='eos_visible'])
        with self.assertRaisesRegex(ValueError,'true EOS order'): validate_run(self.run)
    def test_missing_preregistered_test_run_rejected(self):
        shutil.rmtree(self.root/'run_04')
        with self.assertRaisesRegex(ValueError,'missing preregistered'):
            evaluate_service(self.root,self.root/'frozen_split.json',self.root/'frozen_service_model.json',self.root/'bad_eval.json')
    def test_posthoc_windows_rejected(self):
        self.mutate_meta(lambda m:m.update(service_window_offsets_ns=[[2_000_000_000,3_000_000_000]]))
        with self.assertRaisesRegex(ValueError,'frozen analysis protocol'):
            fit_service(self.root,self.root/'frozen_split.json',self.root/'bad_fit.json')
    def test_consumption_revalidates_split(self):
        split=read_json(self.root/'frozen_split.json'); split['runs'][4]['session_id']=split['runs'][0]['session_id']
        write_json(self.root/'altered_split.json',split)
        with self.assertRaisesRegex(ValueError,'session leakage'):
            fit_service(self.root,self.root/'altered_split.json',self.root/'bad_fit.json')
    def test_incomplete_pcc_metadata_rejected(self):
        self.mutate_meta(lambda m:(m.update(tier='PCC',electrical_topology_id='sim',pcc_nuisance_audit_id='sim',grid_tail_certificate_id='sim'),m['channels'].update(pcc_active={'source':'SIMULATED','boundary':'SIMULATED_PCC'})))
        self.mutate_lines('power.jsonl',lambda rows:rows.extend([{**r,'channel':'pcc_active'} for r in list(rows)]))
        with self.assertRaisesRegex(ValueError,'PCC metadata'): validate_run(self.run,'pcc')
    def test_missing_command_ack_rejected(self):
        (self.run/'commands.jsonl').unlink()
        with self.assertRaisesRegex(ValueError,'command acknowledgment'): validate_run(self.run,'w6-dc')
    @unittest.skipUnless(hasattr(signal, "setitimer"), "Unix absolute timer required")
    def test_slow_drip_total_deadline(self):
        config=read_json(Path(__file__).parents[1]/'configs/request.example.json')
        prompt=self.root/'prompt.txt'; prompt.write_text('SYNTHETIC TEST INPUT')
        config.update(prompt_file=str(prompt),timeout_s=.03)
        write_json(self.root/'request.json',config)
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def readline(self,_limit): time.sleep(.005); return b':keepalive\n'
        class FakeOpener:
            def open(self,*args,**kwargs): return FakeResponse()
        start=time.monotonic()
        with patch('urllib.request.build_opener',return_value=FakeOpener()):
            with self.assertRaises(TimeoutError): completion_request(self.root/'request.json',self.root/'client.jsonl',True)
        self.assertLess(time.monotonic()-start,.5)

    def test_substituted_registered_directory_rejected(self):
        shutil.rmtree(self.root/'run_04'); shutil.copytree(self.root/'run_05',self.root/'run_04')
        with self.assertRaisesRegex(ValueError,'registered directory'):
            evaluate_service(self.root,self.root/'frozen_split.json',self.root/'frozen_service_model.json',self.root/'bad_eval.json')
    def test_frozen_bracket_rule_handles_async_progress(self):
        self.mutate_lines('events.jsonl',lambda rows:[r.update(t_ns=r['t_ns']+1_000_000) for r in rows if r['type']=='progress' and r['t_ns']<7_000_000_000])
        fit_service(self.root,self.root/'frozen_split.json',self.root/'bracket_fit.json')

    def test_host_output_not_physical_service(self):
        self.mutate_lines('events.jsonl',lambda rows:[r.update(timestamp_source='host_engine_output_observation') for r in rows if r['type']=='progress'])
        with self.assertRaisesRegex(ValueError,'host output observation'): validate_run(self.run,'w6-dc')

    def test_measured_rejects_simulated_timestamp_source(self):
        self.mutate_meta(lambda m:m.update(evidence='MEASURED'))
        for name in ['power.jsonl','commands.jsonl','events.jsonl']:
            self.mutate_lines(name,lambda rows:[r.update(evidence='MEASURED') for r in rows])
        self.mutate_lines('events.jsonl',lambda rows:[r.update(work_source='engine_token_ids') for r in rows if r['type']=='progress'])
        self.mutate_lines('events.jsonl',lambda rows:[r.update(true_eos_source='device_completion_instrumented') for r in rows if r['type']=='eos_visible'])
        with self.assertRaisesRegex(ValueError,'simulated timestamp'): validate_run(self.run,'w6-dc')


class FakeNVML:
    NVML_TEMPERATURE_GPU=0
    def __init__(self,fail=False): self.cap=200000; self.sets=[]; self.fail=fail; self.closed=False
    def nvmlDeviceGetUUID(self,h): return 'SIMULATED_UUID'
    def nvmlDeviceGetPowerManagementLimitConstraints(self,h): return 100000,250000
    def nvmlDeviceGetPowerManagementLimit(self,h): return self.cap
    def nvmlDeviceGetEnforcedPowerLimit(self,h): return self.cap
    def nvmlDeviceGetTemperature(self,h,_): return 40
    def nvmlDeviceSetPowerManagementLimit(self,h,v):
        self.cap=v; self.sets.append(v)
        if self.fail and len(self.sets)==1: raise RuntimeError('SIMULATED setter error after change')
    def nvmlShutdown(self): self.closed=True


class CapTests(unittest.TestCase):
    def plan(self):
        return {'evidence':'SIMULATED','acquisition_id':'a','run_id':'r','clock_id':'c','operator_reviewed':True,
                'exclusive_device':True,'no_other_workloads':True,'expected_device_sha256':hashlib.sha256(b'SIMULATED_UUID').hexdigest(),
                'operator_min_W':100,'operator_max_W':150,'max_temperature_C':75,'levels':[{'cap_W':125,'hold_s':.001}]}
    def test_restores_original(self):
        n=FakeNVML()
        with tempfile.TemporaryDirectory() as t: run_cap_session(self.plan(),Path(t)/'cap.jsonl',(n,0))
        self.assertEqual(n.sets,[125000,200000]); self.assertTrue(n.closed)
    def test_restores_after_setter_error(self):
        n=FakeNVML(fail=True)
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(RuntimeError): run_cap_session(self.plan(),Path(t)/'cap.jsonl',(n,0))
        self.assertEqual(n.cap,200000); self.assertTrue(n.closed)
    def test_identity_mismatch_no_write(self):
        n=FakeNVML(); p=self.plan(); p['expected_device_sha256']='0'*64
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(ValueError,'identity'): run_cap_session(p,Path(t)/'cap.jsonl',(n,0))
        self.assertEqual(n.sets,[]); self.assertTrue(n.closed)
    def test_cap_above_original_rejected(self):
        n=FakeNVML(); p=self.plan(); p['operator_max_W']=250; p['levels'][0]['cap_W']=225
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(ValueError,'initial setting'): run_cap_session(p,Path(t)/'cap.jsonl',(n,0))
        self.assertEqual(n.sets,[])

    def test_repeat_signal_during_restore_is_deferred(self):
        class InterruptDuringRestore(FakeNVML):
            def nvmlDeviceSetPowerManagementLimit(self,h,v):
                if self.sets: signal.raise_signal(signal.SIGINT)
                super().nvmlDeviceSetPowerManagementLimit(h,v)
        n=InterruptDuringRestore(); before=signal.getsignal(signal.SIGINT)
        with tempfile.TemporaryDirectory() as t: run_cap_session(self.plan(),Path(t)/'cap.jsonl',(n,0))
        self.assertEqual(n.cap,200000); self.assertEqual(signal.getsignal(signal.SIGINT),before)


if __name__=='__main__': unittest.main()
