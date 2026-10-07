"""Independently recompute metrics of completed signed nonlinear stress replays.
Does not import/run the simulator, certify intersample peaks, or replace pending
finite runs with a robust nonlinear conclusion.
"""
from pathlib import Path
import json,hashlib
import numpy as np
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent/'nonlinear'
conf=json.loads((ROOT/'NONLINEAR_FREEZE.json').read_text());rows=[]
source_integrity={path:hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected
                  for path,expected in conf['source_hashes'].items()}
assert all(source_integrity.values())
def ash(a):return hashlib.sha256(np.asarray(a,dtype=np.float64).tobytes()).hexdigest()
for case in conf['cases']:
    stem=case['network']+'_'+case['label']
    data=np.load(ROOT/(stem+'_input.npz'))
    sc=data['actual_schedule'];word=data['trim_word_current_to_oldest']
    assert len(word)==65 and ash(sc)==case['actual_schedule_sha256']
    block=sc[1:-1,[1,3]].reshape(65,4,2)
    assert abs(block.sum(axis=1)*.5).max()<1e-12
    assert np.max(abs(block-case['total_amplitude_MW']*word[::-1,None,:]*data['q'][None,:,:]))<1e-12
    for dt in conf['dt_s']:
        path=ROOT/(stem+f'_dt{round(1/dt)}.json')
        if not path.exists():continue
        result=json.loads(path.read_text())
        raw=np.load(path.with_suffix('.npz'))
        t=raw['t'];freq=raw['frequency_Hz'];linear=raw['exact_LTI_frequency_Hz']
        peak=float(abs(freq).max());error=float(abs(freq-linear).max());it=int(np.argmin(abs(t-case['target_trim_time_s'])))
        assert abs(peak-result['metrics']['nonlinear_peak_any_generator_Hz'])<1e-13
        assert abs(error-result['metrics']['max_linear_nonlinear_error_Hz'])<1e-13
        assert abs(float(linear[it,case['target_output_zero_based']])-result['metrics']['exact_LTI_target_Hz'])<1e-13
        assert ash(raw['actual_schedule'])==case['actual_schedule_sha256']
        assert result['metadata']['baseline_port_MW']==[0.,0.]
        assert all(not x['positive_compute_probe_contract_embedded'] for x in result['physical_ledger'])
        tail_error=result['metrics']['full_vs_trimmed_LTI_target_error_Hz']
        assert tail_error<=case['LTI_trim_vs_full_tail_upper_Hz']+2e-12
        rows.append({'network':case['network'],'case':case['label'],'dt':dt,
                     'complete':result['complete'],'peak_Hz':peak,'margin_Hz':.05-peak,
                     'max_NL_LTI_difference_Hz':error,'LTI_trim_error_Hz':tail_error,
                     'zero_probe_baseline_confirmed':True,'source_file':path.name})
pairs=[]
for case in conf['cases']:
    rr=sorted([r for r in rows if r['network']==case['network'] and r['case']==case['label']],key=lambda r:r['dt'],reverse=True)
    if len(rr)==2:
        pairs.append({'network':case['network'],'case':case['label'],
                      'coarse_peak_Hz':rr[0]['peak_Hz'],'fine_peak_Hz':rr[1]['peak_Hz'],
                      'peak_difference_Hz':abs(rr[0]['peak_Hz']-rr[1]['peak_Hz']),
                      'fine_margin_Hz':rr[1]['margin_Hz']})
out={'scope':'Raw numerical trajectory/metric and input-contract audit only; no continuous-time interval enclosure or family-wide nonlinear proof. Trimming equivalence bounded only for LTI.',
     'checked_outputs':rows,'refinement_pairs':pairs,
     'frozen_source_integrity':source_integrity,
     'all_current_checks_passed':True,'all_expected_runs_complete':len(rows)==20 and all(x['complete'] for x in rows)}
(OUT/'INDEPENDENT_NONLINEAR_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'checked_outputs':len(rows),'completed_refinement_pairs':len(pairs),
                  'all_expected_runs_complete':out['all_expected_runs_complete'],'all_current_checks_passed':True},indent=2))
