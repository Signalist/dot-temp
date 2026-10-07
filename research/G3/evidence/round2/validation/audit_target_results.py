"""Numerical verification kept separate from physical-contract verdicts."""
from pathlib import Path
import json,hashlib
import numpy as np
R=Path(__file__).resolve().parent
cases=[]
for file in sorted(R.glob('*_TARGET_RESULTS.json')):
    z=json.loads(file.read_text());runs=[];T=z.get('service_horizon_s',.2);endkey=f'state_at_{T:.3f}s';continuekey=f'state_at_{T+.1:.3f}s'
    for r in z['runs']:
        a=np.genfromtxt(R/r['trace'],delimiter=',',names=True);p=z['parameters'];w=np.genfromtxt(R/r['waveform'],delimiter=',',names=True)
        sw=np.c_[w['sa'],w['sb'],w['sc']];ii=np.c_[w['ia'],w['ib'],w['ic']];ee=np.c_[w['ea'],w['eb'],w['ec']]
        checks={
            'all_finite':bool(all(np.all(np.isfinite(a[k])) for k in a.dtype.names)),
            'balanced_currents':bool(np.max(abs(a['ia']+a['ib']+a['ic']))<1e-7),
            'DC_bridge_energy_identity':bool(np.max(abs(a['W']-p['W0']-a['bridge_energy']+a['load_energy']-a['battery_energy']))<1e-5),
            'battery_energy_identity':bool(np.max(abs(a['B']-p['B0']+a['battery_energy']))<1e-5),
            'total_energy_residual_below_0p1J':bool(r['energy_closure_max_J']<.1),
            'instantaneous_bridge_power_identity':bool(np.max(abs(np.sum(ee*ii,axis=1)-w['pdc']))<1e-5),
            'DC_switch_current_identity':bool(np.max(abs(w['pdc']/w['Vdc']-np.sum(sw*ii,axis=1)))<1e-7),
            'positive_continuing_load':bool(np.min(a['dmean'])>0),
            'same_battery_command_not_clamped':bool(r['u_clamp_max_change_W']==0 and r['rate_clamp_max_change_W_per_s']==0),
            'binary_PWM_or_averaged_duties':bool(np.all((sw==0)|(sw==1)) if r['mode']=='pwm' else np.all((sw>=0)&(sw<=1)))}
        verdict={
            'finite_tested_bounds':r['all_tested_hardware_bounds_satisfied'],
            'inventory_recovery_at_service_end_0p001J_tolerance':abs(r[endkey]['B_error_J'])<.001,
            'inventory_recovery_at_continuation_end_0p001J_tolerance':abs(r[continuekey]['B_error_J'])<.001,
            'DC_energy_recovery_at_service_end_0p01J_tolerance':abs(r[endkey]['W_error_J'])<.01,
            'DC_energy_recovery_at_continuation_end_0p01J_tolerance':abs(r[continuekey]['W_error_J'])<.01,
            'exact_PQ_tracking':False,
            'full_four_contract_transfer':False}
        runs.append(dict(trace=r['trace'],verification_checks=checks,all_numerical_verification_checks_pass=all(checks.values()),contract_verdicts=verdict))
    cases.append(dict(case=file.stem,runs=runs))
out={'cases':cases,'all_numerical_verification_checks_pass':all(r['all_numerical_verification_checks_pass'] for c in cases for r in c['runs']),'note':'Passing numerical verification does not mean all physical contracts pass; exact DC recovery and exact P/Q transfer fail.'}
(R/'TARGET_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(R.iterdir()) if p.is_file() and p.name not in ['VALIDATION_SHA256.json','REFERENCE_SHA256.json']}
(R/'VALIDATION_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'all_numerical_verification_checks_pass':out['all_numerical_verification_checks_pass'],'cases':len(cases),'full_four_contract_transfer':False}))
assert out['all_numerical_verification_checks_pass']
