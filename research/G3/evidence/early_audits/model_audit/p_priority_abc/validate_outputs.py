"""Integrity and consistency checks of the completed single-condition artifact."""
from pathlib import Path
import hashlib,json
import numpy as np
r=Path(__file__).resolve().parent;root=r.parents[1]
x=json.loads((r/'COMPARISON.json').read_text());audit=json.loads((r/'IMPLEMENTATION_AUDIT.json').read_text())
assert audit['allocation_only_control_text_verified'] and not audit['runtime_DQ_imports']
assert set(audit['only_parameter_changes'])=={'battery_source_tau_s','battery_source_ramp_up_W_per_s','battery_source_ramp_down_W_per_s'}
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in audit['input_sha256'].items())
checks=[]
for h in ['1e-05','5e-06']:
    a=np.load(r/f'fast_p_priority_abc_h{h}.npz');s=json.loads((r/f'fast_p_priority_abc_h{h}.json').read_text())
    for arr,cols in [('trace','trace_columns'),('control','control_columns'),('sample_before','sample_state_columns'),('sample_after','sample_state_columns')]:assert a[arr].shape[1]==len(a[cols])
    assert a['control'].shape==(21,33)
    assert np.max(abs(a['sample_after'][:,:14]-a['sample_before'][:,:14]))==0
    assert np.isfinite(a['control']).all() and np.isfinite(a['sample_before']).all() and np.isfinite(a['sample_after']).all()
    invalid=np.argwhere(~np.isfinite(a['trace']));assert invalid.tolist()==[[0,25]]
    assert s['stop_reason']=='actual_current_numerical_emergency' and .6<s['actual_1pu_crossings_s'][0]<s['stop_s']<.75005
    assert s['Vdc_max_pu']<1.1 and s['iref_max_pu']<=.95+1e-12
    assert x['comparison'][f'h{h}']['pre_sample_normalized_state_max_error']<1e-9
    assert x['comparison'][f'h{h}']['controller_after_normalized_max_error']<1e-9
    assert abs(x['comparison'][f'h{h}']['stop_time_error_s'])<1e-10
    checks.append({'h':h,'trace_rows':len(a['trace']),'sample_updates':len(a['control']),'array_schema_valid':True,'dynamics_alignment_checked':True,'documented_missing_prior_reference_only':True})
result={'passed':True,'checks':checks,'sources_unchanged':True,'no_DQ_runtime_imports':True,'remark':'Output self-consistency checks; thresholds are reporting checks, not a newly frozen physical-performance gate.'}
(r/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
