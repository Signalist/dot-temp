import hashlib,json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Payload(unittest.TestCase):
    def test_latest_quality_is_fail_closed(self):
        r=json.loads((ROOT/'continuation/quality/LEGACY_RESCORE.json').read_text())
        self.assertEqual((r['requests'],r['main_requests'],r['warmups'],r['distinct_main_quality_cases']),(108,72,36,3))
        self.assertEqual(r['quality_matching_eligible_existing_tasks'],0)
        self.assertFalse(r['task_details']['writing_short_v2c']['full_quality_pass'])
        self.assertFalse(r['task_details']['code_short']['full_quality_pass'])
        self.assertIsNone(r['task_details']['reasoning_medium']['full_quality_pass'])
    def test_frozen_validator_and_references(self):
        q=ROOT/'continuation/quality';v=json.loads((q/'VALIDATOR_FREEZE.json').read_text());b=json.loads((q/'BENCHMARK_FREEZE.json').read_text())
        for path,digest in [(q/'validator.py',v['validator_sha256']),(q/'test_validators.py',v['test_source_sha256']),(q/'benchmark.json',b['benchmark_sha256']),(q/'reference_fixtures.json',b['reference_fixtures_sha256'])]:
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),digest)
    def test_request_export_has_no_answers(self):
        p=ROOT/'continuation/quality/development_export_test.jsonl'
        if not p.exists():self.skipTest('Run through scripts/run_checks.py to test fresh exporter output')
        rows=[json.loads(x) for x in p.read_text().splitlines()];self.assertEqual(len(rows),6)
        for r in rows:
            self.assertEqual(r['split_role'],'development');self.assertFalse(r['new_gpu_run'])
            self.assertTrue({'cases','expected','reference','answer','reference_fixtures'}.isdisjoint(r))
    def test_only_three_main_quality_hashes(self):
        p=ROOT/'continuation/quality/legacy_compact';rows=json.loads((p/'REQUEST_INDEX.json').read_text())['rows']
        self.assertEqual(len(rows),108);main=[r for r in rows if r['phase']=='MAIN'];self.assertEqual(len(main),72)
        hashes={r['output_text_sha256'] for r in main};self.assertEqual(len(hashes),3)
        for h in hashes:self.assertEqual(sum(r['output_text_sha256']==h for r in main),24)
        for row in rows:self.assertEqual(hashlib.sha256((p/(row['output_text_sha256']+'.txt')).read_bytes()).hexdigest(),row['output_text_sha256'])
    def test_licensed_input_hashes(self):
        checks={'research/full_cycle/literature/data_candidate/AzureLLMInferenceTrace_conv.csv':'2f1e5b666d4e3055fdbba98598ce2ec307767b9064e03e2fa46676dbcc7d0bf8','research/grid_memory/inputs/kundur_reduced51.npz':'31e798abc23bdcb6c3b46aeb488caf96636127390935eac4d9f0e2fdd5601828'}
        for rel,h in checks.items():self.assertEqual(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),h)
    def test_measured_configs_not_authorized(self):
        cap=json.loads((ROOT/'gpu_handoff/configs/cap_session.example.json').read_text())
        self.assertFalse(cap['operator_reviewed']);self.assertFalse(cap['exclusive_device']);self.assertFalse(cap['no_other_workloads'])
if __name__=='__main__':unittest.main()
