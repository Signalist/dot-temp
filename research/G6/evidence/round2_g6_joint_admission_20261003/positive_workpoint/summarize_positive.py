"""Produce explicit physical amplitude caps and final finite-replay report."""
from pathlib import Path
import json,csv,hashlib,time
import numpy as np
P=Path(__file__).resolve().parent
q=json.loads((P/'QUALIFICATION.json').read_text());s=json.loads((P/'positive_summary.json').read_text());rows=list(csv.DictReader((P/'positive_rays.csv').open()));physical=[]
for row in rows:
 r={k:float(v) for k,v in row.items()};a=np.array([r['a1_share'],r['a2_share']]);cap=min(50/a[a>0]);r['positive_compute_amplitude_cap_total_MW']=cap
 for c in ['committed','dynamic_optional','independent_ports','reset']:
  for bound in ['lower','upper']:
   raw=r[f'{c}_capacity_{bound}_MW'];r[f'{c}_physical_capacity_{bound}_MW']=min(cap,raw)
  r[f'{c}_physical_inner_min_compute_MW']=float(np.min(50-a*r[f'{c}_physical_capacity_lower_MW']))
 physical.append(r)
with (P/'positive_physical_rays.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(physical[0]));w.writeheader();w.writerows(physical)
old=q['old_zero_compute_workpoint']['GENROU'];new=q['positive_compute_workpoint']['GENROU'];power={'base_MVA':100.,'nominal_extra_compute_P_MW':[50.,50.],'nominal_extra_compute_Q_Mvar':[0.,0.],'demand_sign':'positive is consumption; actual computeP_i(t)=50+deltaP_i(t), computeQ_i(t)=0','original_generator_P_MW':(100*np.array(old['p0'])).tolist(),'positive_workpoint_generator_P_MW':(100*np.array(new['p0'])).tolist(),'generation_P_change_MW':(100*(np.array(new['p0'])-old['p0'])).tolist(),'original_generator_Q_Mvar':(100*np.array(old['q0'])).tolist(),'positive_workpoint_generator_Q_Mvar':(100*np.array(new['q0'])).tolist(),'old_network_loss_MW':100*sum(old['p0'])-2734,'new_network_loss_MW':100*sum(new['p0'])-2834,'additional_loss_MW':100*(sum(new['p0'])-sum(old['p0']))-100,'base_bus_voltage_pu':q['positive_compute_workpoint']['Bus']['v'],'base_bus_ids':q['positive_compute_workpoint']['Bus']['idx'],'stationary_min_voltage_pu':q['stationarity']['bus_voltage_range_pu'][0],'planning_voltage_caveat':'Stationary minimum0.945044pu is below an illustrative0.95pu planning floor. This study froze only generator-frequency deviation±0.05Hz and does not qualify voltage/VRT/thermal deployment.'}
(P/'POWER_BALANCE_AND_PHYSICAL_SCOPE.json').write_text(json.dumps(power,indent=2))
results=[]
for f in sorted(P.glob('*_dt*.json')):
 d=json.loads(f.read_text())
 if 'case' in d and 'complete' in d:results.append(d)
if results:
 summary={'results':[{'label':d['label'],'complete':d['complete'],'dt_s':d['dt_s'],'total_amplitude_MW':d['case']['total_amplitude_MW'],'min_compute_MW':d['actual_compute_min_MW'],'metrics':d['metrics']} for d in results],'all_complete':all(d['complete'] for d in results),'all_compute_nonnegative':all(d['actual_compute_nonnegative'] for d in results),'count':len(results),'refinements':[]}
 for lab in ['dynamic_optional_inner','dynamic_optional_outer','reset_false_admission']:
  by={d['dt_s']:d for d in results if d['case']['label']==lab}
  if len(by)==2:
   coarse=by[1/128];fine=by[1/256];summary['refinements'].append({'label':lab,'coarse_peak_Hz':coarse['metrics']['nonlinear_peak_Hz'],'fine_peak_Hz':fine['metrics']['nonlinear_peak_Hz'],'absolute_peak_change_Hz':abs(coarse['metrics']['nonlinear_peak_Hz']-fine['metrics']['nonlinear_peak_Hz']),'classifications_same':(coarse['metrics']['nonlinear_peak_Hz']>.05)==(fine['metrics']['nonlinear_peak_Hz']>.05)})
 (P/'POSITIVE_NONLINEAR_SUMMARY.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({'power_balance':power,'completed_nonlinear_cases':len(results),'physical_caps_active_for_proper_inner_rays':{c:int(sum(r[f'{c}_capacity_lower_MW']>r['positive_compute_amplitude_cap_total_MW'] for r in physical)) for c in ['committed','dynamic_optional','independent_ports']}},indent=2))
