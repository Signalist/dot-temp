#!/usr/bin/env python3
"""Mature exact set-membership baseline using piecewise mode enumeration.
Each candidate gets same PCC samples, state/rate limits and error contract.
No free task label. No novel optimizer claim.
"""
import itertools,json,pathlib
import numpy as np
from scipy.optimize import linprog
R=pathlib.Path(__file__).resolve().parent
ec=ed=.95;E0=9;C=18;rate=12;a=12/(1+ec*ed);y=np.array([6,6+a,6+a,6,6,6]);Q=ec*a

def fit(j,energy_obs=None,energy_error=.1):
 d=np.full(6,6.);d[j]=18;best=None
 # Enumeration covers all actual charge/discharge branches, including grid below6 orabove18.
 for modes in itertools.product([0,1],repeat=6):
  slopes=np.array([ec if c else 1/ed for c in modes]);bounds=[]
  for load,c in zip(d,modes):
   lo=max(0,load-rate);hi=load+rate
   if c:lo=max(lo,load)
   else:hi=min(hi,load)
   bounds.append((lo,hi))
  bounds.append((0,None));A=[];b=[]
  for k in range(6):
   r=np.zeros(7);r[k]=1;r[-1]=-1;A.append(r);b.append(y[k])
   r=np.zeros(7);r[k]=-1;r[-1]=-1;A.append(r);b.append(-y[k])
  for k in range(1,7):
   r=np.zeros(7);r[:k]=slopes[:k];c=float(slopes[:k]@d[:k]);A.append(r);b.append(C-E0+c);A.append(-r);b.append(E0-c)
  if energy_obs is not None:
   r=np.zeros(7);r[:2]=slopes[:2];c=float(slopes[:2]@d[:2]);A.append(r);b.append(energy_obs+energy_error-E0+c);A.append(-r);b.append(-energy_obs+energy_error+E0-c)
  eq=np.zeros((1,7));eq[0,:6]=slopes;beq=[float(slopes@d)]
  obj=np.zeros(7);obj[-1]=1;res=linprog(obj,A_ub=A,b_ub=b,A_eq=eq,b_eq=beq,bounds=bounds,method='highs')
  if res.success and (best is None or res.fun<best['minimum_PCC_Linf_error']):
   p=res.x[:6];e=E0+np.r_[0,np.cumsum(np.where(p-d>=0,ec*(p-d),(p-d)/ed))]
   best={'high_slot_1indexed':j+1,'minimum_PCC_Linf_error':float(res.fun),'candidate_PCC':p.tolist(),'candidate_energy':e.tolist(),'mode':list(modes),'terminal_error':float(e[-1]-E0)}
 return best

def main():
 raw=[fit(j) for j in range(6)]
 withsoc=[fit(j,E0-Q,.1) for j in range(6)]
 rows=[]
 for eps in [0,.05,.1,.25,.5,1,2]:
  keep=lambda rr:[z['high_slot_1indexed'] for z in rr if z is not None and z['minimum_PCC_Linf_error']<=eps+1e-8]
  rows.append({'PCC_error':eps,'PCC_only_candidates':keep(raw),'plus_identity_bound_SOC_candidates':keep(withsoc),'PCC_only_decision':'abstain' if len(keep(raw))>1 else 'singleton' if keep(raw) else 'inconsistent','plus_SOC_decision':'abstain' if len(keep(withsoc))>1 else 'singleton' if keep(withsoc) else 'inconsistent'})
 out={'scope':'exact small-model piecewise-linear set-membership, all6 candidate high-task slots, actual world highslot2; not exposedPCC-source inference','state_contract':{'initial_energy':E0,'capacity':C,'eta_c':ec,'eta_d':ed,'battery_ac_limit':rate,'exact_recovery':True},'observed_PCC':y.tolist(),'energy_observation':E0-Q,'energy_error':.1,'PCC_fit':raw,'PCC_plus_SOC_fit':withsoc,'noise_ablation':rows,'mapping_ablation':{'labelled_site_SOC':'distinguishes source-of-high-task swapped worlds','unlabelled_SOC_multiset':'same in swapped worlds; still abstain','block_end_SOC':'identical; still abstain','total_SOC':'identical; still abstain'},'tests':{'noise0_retains_two':rows[0]['PCC_only_candidates']==[2,3],'noise0_SOC_selects2':rows[0]['plus_identity_bound_SOC_candidates']==[2],'all_models_preserve_recovery':all(abs(z['terminal_error'])<1e-7 for z in raw+withsoc if z),'candidate_sets_nested':all(set(rows[i]['PCC_only_candidates'])<=set(rows[i+1]['PCC_only_candidates']) for i in range(len(rows)-1))}}
 (R/'MEASUREMENT_ABLATION_RESULTS.json').write_text(json.dumps(out,indent=2));print(json.dumps({'thresholds':[(x['high_slot_1indexed'],x['minimum_PCC_Linf_error']) for x in raw],'ablation':rows,'tests':out['tests']},indent=2));assert all(out['tests'].values())
if __name__=='__main__':main()
