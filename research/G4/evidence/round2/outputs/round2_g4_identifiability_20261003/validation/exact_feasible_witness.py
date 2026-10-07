#!/usr/bin/env python3
import sys,pathlib,json
from fractions import Fraction as F
R=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'experiments'))
from causal_horizon_design import design
out=design(4,tau=.49,initial_fraction=.5,capacity_value=17.9)
assert out['success']
p=[[F(str(round(z,9))) for z in row] for row in out['p']]
ec=ed=F(19,20);e0=F(9);C=F(18);tau=F(1,2);lo=hi=e0
phi=lambda z:ec*z if z>=0 else z/ed
trace=[];minimum=C;maximum=F(0)
for b,row in enumerate(p):
 inc=[]
 for j in range(6):
  prefix=[F(0)]
  for k,power in enumerate(row):prefix.append(prefix[-1]+phi(power-(18 if j==k else 6)))
  inc.append(prefix)
 mn=min(lo+x for pref in inc for x in pref);mx=max(hi+x for pref in inc for x in pref)
 assert mn>=0 and mx<=C
 minimum=min(minimum,mn);maximum=max(maximum,mx)
 lo+=min(v[-1] for v in inc);hi+=max(v[-1] for v in inc)
 assert lo>=e0-tau and hi<=e0+tau
 assert all(F(6)<=x<=F(18) for x in row)
 trace.append({'block':b+1,'endpoint_low':str(lo),'endpoint_high':str(hi),'state_min':str(mn),'state_max':str(mx)})
cert={'scope':'exact rational feasible common-PCC witness for all6^4 independent high-task positions, eta19/20, capacity18,E0=9,R12,tau1/2; no state reset','PCC_rational':[[str(z) for z in row] for row in p],'PCC_decimal':[[float(z) for z in row] for row in p],'soc_allhistories_min':str(minimum),'soc_allhistories_max':str(maximum),'endpoint_intervals':trace,'valid_exact':True,'direct_current_load_causal':True,'all_tasks_complete_each_6s':True,'scope_extension':'since R=H-L and all worlds allowed per slot, arbitrary within-slot PCC cannot beat the slot-mean capacity exclusion; this feasible witness uses constant per-slot commands'}
(R/'EXACT_FEASIBLE_K4_CERTIFICATE.json').write_text(json.dumps(cert,indent=2));print(json.dumps({k:v for k,v in cert.items() if k not in ['PCC_rational','PCC_decimal','endpoint_intervals']},indent=2))
