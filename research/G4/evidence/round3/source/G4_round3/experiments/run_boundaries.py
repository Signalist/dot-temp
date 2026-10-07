#!/usr/bin/env python3
import json
from fractions import Fraction as F
import numpy as np
from run_workload_study import *

def more():
 transfer=[]
 # Table-2-inspired structural patterns; no Task Bench software or power traces used.
 for pattern in ['stencil','sweep']:
  for layers,width in [(3,3),(3,4),(4,3)]:
   edges=[]
   for t in range(1,layers):
    for j in range(width):
     preds=[j,j-1,j+1] if pattern=='stencil' else [j,j-1]
     edges += [((t-1)*width+i,t*width+j) for i in preds if 0<=i<width]
   for marking in ['periodic','seeded']:
    labels=([int((i+t)%3==0) for t in range(layers) for i in range(width)] if marking=='periodic' else np.random.default_rng(442+layers*100+width).integers(0,2,layers*width).tolist())
    rr,pats,r=record(f'task_shape_{pattern}_{layers}x{width}_{marking}',labels,edges,split='public_pattern_synthetic_power');transfer.append(rr)
 # Lossless baseline uses all endpoint equations; lossy graph equalities must not be imposed.
 ideal=[]
 for row in json.loads((OUT/'dag_results.json').read_text()):
  if row['split']=='worked' and row['eta']==.95:
   pats,*_=dag_data(row['labels'],row['edges']);m=matrices(pats,eta=1.0);r=solve_model(m)
   ideal.append({'name':row['name'],'scenario_B':float(r.fun),'prefix_formula_B':row['ideal_B'],'exact_certificate':rational_check(m,r)})
 # Cyclic discrete PCC-step limits. These are not converter continuous slew constraints.
 src=next(row for row in json.loads((OUT/'dag_results.json').read_text()) if row['name']=='heterogeneous_barriers' and row['eta']==.95)
 pats,*_=dag_data(src['labels'],src['edges']);ramps=[];n=len(pats[0])
 for R in [0.,1.,3.,6.,12.]:
  m=list(matrices(pats));c,a,b,ae,be,bounds=m
  extra=[]
  for t in range(n):
   v=np.zeros(n+2);v[t]=1;v[(t+1)%n]=-1;extra.extend([v,-v])
  m[1]=np.vstack([a,*extra]);m[2]=np.r_[b,[R]*len(extra)];r=solve_model(m)
  ramps.append({'cyclic_PCC_step_limit':R,'capacity':float(r.fun),'output':r.x[:n].tolist(),'exact_certificate':rational_check(m,r)})
 # Paired-order support: AB or BA every two blocks, independently chosen at each pair.
 eta=F(19,20);kap=1/eta-eta;lo,hi=F(6),F(18);p1,p3=F(7),F(13)
 p2=(2*(hi-lo)/eta-kap*(p1+p3-2*lo))/(2*eta)+3*lo-p1-p3
 p=[p1,p2,p3];A=[hi,lo,lo];B=[lo,lo,hi]
 phi=lambda x:eta*x if x>=0 else x/eta
 def path(word,pp):
  states=[F(0)]
  for d,q in zip(word,pp):states.append(states[-1]+phi(q-d))
  return states
 ra=path(A,p)[-1];rb=path(B,p)[-1];ab=path(A+B,p+p);ba=path(B+A,p+p);vmin=min(ab+ba);vmax=max(ab+ba)
 paired={'A':list(map(str,A)),'B':list(map(str,B)),'public_period3':list(map(str,p)),'rA':str(ra),'rB':str(rb),'sum_zero':ra+rb==0,'capacity':str(vmax-vmin),'initial':str(-vmin),'AB_relative_states':list(map(str,ab)),'BA_relative_states':list(map(str,ba)),'old_independent_width_after_K_blocks':'2*K*abs(rA)','paired_endpoint_width_even_blocks':'0','paired_endpoint_width_odd_blocks':str(2*abs(ra)),'support_warning':'every two-block word is AB or BA; AA and BB removed, not merely made unlikely'}
 # Exact weighted-invariance threshold under retention.
 thresholds=[]
 for rho in [F(999,1000),F(99,100),F(9,10)]:
  alpha=eta*eta;thresholds.append({'rho':str(rho),'N':6,'alpha':str(alpha),'rho_power_Nminus1':str(rho**5),'zero_endpoint_width_possible':alpha<=rho**5})
 result={'public_pattern_transfer':transfer,'ideal_comparison':ideal,'PCC_step_ablation':ramps,'correlated_exact_counterexample':paired,'leakage_threshold':thresholds,'disposal_counterexample':{'trace':'p_t=H=18','AC_ballast_rating':12,'buffer_capacity':0,'extra_grid_energy_per6slot_2high_block':48,'assumption_change':'instantaneous controllable AC ballast load H-d, no thermal or disposal budget'}}
 (OUT/'boundary_results.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':more()
