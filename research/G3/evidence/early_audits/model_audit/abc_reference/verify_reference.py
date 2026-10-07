"""Algebraic checks and frozen-case summary only; no new dynamic case."""
import hashlib,json,math
from pathlib import Path
import numpy as np
from reference_abc import abc_from_complex,complex_from_abc
root=Path(__file__).parent
checks={}
zs=[1+0j,1j,.6-.8j,-.3+.2j]
checks['transform_max_abs_error']=max(abs(complex_from_abc(abc_from_complex(z))-z) for z in zs)
checks['sum_phase_max_abs']=max(abs(abc_from_complex(z).sum()) for z in zs)
checks['power_max_abs_error']=max(abs(float(abc_from_complex(v)@abc_from_complex(i))-1.5*(v*i.conjugate()).real) for v in zs for i in zs)
checks['reactive_sign_positive_for_negative_iq']=bool((1.5*(complex(1,0)*complex(0,-1).conjugate())).imag>0)
checks['strict_reference_limit_numerical_tolerance_pu']=1e-12
checks['pairs']={}
for case in ['conservation','counterexample']:
 a=json.loads((root/'results'/f'{case}_h10us.json').read_text());b=json.loads((root/'results'/f'{case}_h5us.json').read_text())
 n=np.load(root/'results'/f'{case}_h5us.npz');v=n['trace'];cols={s:i for i,s in enumerate(n['columns'])};t=v[:,cols['t']];I=v[:,cols['Iactual_pu']]
 peak=int(I.argmax())
 # Remove duplicate controller-boundary rows for elapsed-time integration.
 keep=np.r_[True,np.diff(t)>1e-12];tt=t[keep];ii=I[keep]
 # Piecewise-linear threshold crossing times, clearly not exact event roots.
 crosses=[]
 for j in np.flatnonzero((ii[:-1]-1)*(ii[1:]-1)<0):
  crosses.append(float(tt[j]+(1-ii[j])*(tt[j+1]-tt[j])/(ii[j+1]-ii[j])))
 checks['pairs'][case]={'protocol_sha256':b['protocol_sha256'],'same_source':a['source_sha256']==b['source_sha256'],
 'actual_peak_difference_pu':abs(a['actual_current_max_pu']-b['actual_current_max_pu']),
 'reference_peak_difference_pu':abs(a['reference_current_max_pu']-b['reference_current_max_pu']),
 'dc_min_difference_pu':abs(a['dc_voltage_min_pu']-b['dc_voltage_min_pu']),
 'dc_max_difference_pu':abs(a['dc_voltage_max_pu']-b['dc_voltage_max_pu']),
 'stop_time_difference_s':abs(a['last_time_s']-b['last_time_s']),
 'peak_time_s':float(t[peak]),'linear_interpolated_current_1pu_crossings_s':crosses,
 'continuous_violation':bool(I.max()>1),'status':b['status'],
 'reference_bound_with_float_tolerance':b['reference_current_max_pu']<=.95+1e-12,
 'max_battery_power_abs_W':float(np.max(np.abs(v[:,cols['Pbat']]))),
 'max_source_command_abs_W':float(np.max(np.abs(v[:,cols['Pbat_cmd']])))}
checks['algebra_pass']=checks['transform_max_abs_error']<1e-14 and checks['power_max_abs_error']<1e-14 and checks['reactive_sign_positive_for_negative_iq']
(root/'VALIDATION_SUMMARY.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
