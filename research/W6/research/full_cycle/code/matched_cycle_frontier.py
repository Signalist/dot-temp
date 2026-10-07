"""Match mean FULL cycle duration against globally best target policy at that duration.
Target energy increases with p; target cycle time has its unique minimum at p^(1+b)=bR/2.
If the requested duration is smaller, report target-class infeasibility, not a fake saving.
"""
from pathlib import Path
import json
from scipy.optimize import brentq
from cycle_model import Case
ROOT=Path(__file__).resolve().parents[1]
def parts(c,p):
 b=c.beta;R=c.R;K=1+b;a=p**K/(K*R);m=1-2*a
 earlyE=(K*R)**(2/K)*a**(1+2/K)/(R*(1+2/K))
 earlyT=2*(K*R)**(1/K)*a**(1+1/K)/(R*(1+1/K))
 E=earlyE+(1-a)*p*p/R+.5*p**(1-b)*m
 T=earlyT+(1-a)*2*p/R+.5*p**(-b)*m
 return E,T
rows=[]
source=ROOT/'results/SAFE_PRIMARY_PATHS.json'
if not source.exists():source=ROOT/'results/PRIMARY_MESHES.json'
for r in json.load(open(source)):
 if r['N']!=128:continue
 c=Case(**r['case']);ptime=(c.beta*c.R/2)**(1/(1+c.beta));Emin,Tmin=parts(c,ptime);T=r['parts']['cycle_time'];E=r['parts']['dynamic_energy'];P_idle=.1
 row={'policy_source':source.name,'case':r['case'],'facility_idle_per_cycle':P_idle,'lambda_cycle':c.c-P_idle,'proposed_cycle_time':T,'proposed_dynamic_energy':E,'proposed_allocated_facility_energy':E+P_idle*T,'constant_target_min_cycle_time':Tmin,'common_resources':{'R':c.R,'p0':0.,'physical_power_and_burn_cap':float(c.P(c.R)),'burn_energy_cap':float(c.P(c.R))**2/(2*c.R)}}
 if T<Tmin-1e-10:
  row.update({'target_feasible_at_requested_cycle_time':False,'mean_cycle_time_below_best_target_fraction':1-T/Tmin,'energy_saving_at_matched_time':None})
 else:
  p=brentq(lambda p:parts(c,p)[1]-T,ptime*1e-9,ptime,xtol=1e-13);Et,Tt=parts(c,p)
  row.update({'target_feasible_at_requested_cycle_time':True,'matched_target_power':p,'matched_target_cycle_time':Tt,'matched_target_dynamic_energy':Et,'matched_target_allocated_facility_energy':Et+P_idle*Tt,'relative_dynamic_energy_saving':1-E/Et,'relative_allocated_facility_energy_saving':1-(E+P_idle*T)/(Et+P_idle*Tt),'time_match_residual':Tt-T})
 rows.append(row)
(ROOT/'results/MATCHED_CYCLE_FRONTIER.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
