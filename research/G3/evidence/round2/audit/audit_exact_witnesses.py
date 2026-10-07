from pathlib import Path
import sys,json,numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'theory'))
from exact_cell import Actuator,cell_bounds,reachability
rows=[]
for f in sorted((ROOT/'results').glob('exact_a*.npz')):
 z=np.load(f);p=json.loads(str(z['par_json']));a=Actuator(-p['umax'],p['umax'],p['tau'],p['ramp'],p['ramp']);t=z['t'];b=z['b'];C=z['charge'];reacherr=0.;areaerr=0.;strict_unreachable=[]
 for k,h in enumerate(np.diff(t)):
  rr=reachability(float(b[k]),float(h),a);err=max(rr['b1_min']-b[k+1],b[k+1]-rr['b1_max'],0);reacherr=max(reacherr,float(err))
  if err>1e-9:strict_unreachable.append(k)
  r=cell_bounds(float(b[k]),float(b[k+1]),float(h),a,anchor_unreachable=True);dc=C[k+1]-C[k]
  areaerr=max(areaerr,float(max(r['Imin']-dc,dc-r['Imax'],0)))
 rows.append({'file':f.name,'tightened':bool(z['tightened']),'max_reachability_violation_kW':reacherr,'max_charge_violation_against_clamped_reachable_pair_kJ':areaerr,'unreachable_cells_at_1e-9_kW':strict_unreachable,'terminal_b_kW':float(b[-1]),'terminal_C_kJ':float(C[-1]),'saved_lp_max_violation':float(max(0,np.max(z['lp_A']@z['lp_x']-z['lp_rhs']))),'saved_margin_kJ':float(z['lp_x'][2*len(t)]),'dual_rows_match':len(z['lp_duals'])==len(z['lp_rhs'])})
res={'rows':rows,'max_reach_violation_kW':max(r['max_reachability_violation_kW'] for r in rows),'max_clamped_charge_violation_kJ':max(r['max_charge_violation_against_clamped_reachable_pair_kJ'] for r in rows),'files_with_unreachable_cells_at_1e-9_kW':[r['file'] for r in rows if r['unreachable_cells_at_1e-9_kW']]}
(ROOT/'audit/EXACT_WITNESS_RESIDUALS.json').write_text(json.dumps(res,indent=2));print(json.dumps({k:v for k,v in res.items() if k!='rows'},indent=2))
