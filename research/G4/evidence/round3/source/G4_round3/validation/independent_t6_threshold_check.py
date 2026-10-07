#!/usr/bin/env python3
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
from scipy.optimize import linprog
import numpy as np,json
checks=[]
for n in range(2,7):
 for k in range(1,n):
  words=[tuple(int(j in s) for j in range(n)) for s in combinations(range(n),k)]
  for eta in (F(1,2),F(19,20)):
   for rho in (F(1,2),F(9,10),F(99,100)):
    rows=[];rhs=[]
    for w in words:
     row=[rho**(n-j-1)*(1/eta if bit else eta) for j,bit in enumerate(w)]
     offset=sum(rho**(n-j-1)*(-F(3)/eta if bit else -eta) for j,bit in enumerate(w))
     rows.append(row);rhs.append(-offset)
    differences=[[float(a-b) for a,b in zip(row,rows[0])] for row in rows[1:]]
    drhs=[float(x-rhs[0]) for x in rhs[1:]]
    result=linprog(np.zeros(n),A_eq=differences,b_eq=drhs,bounds=[(1,3)]*n,method='highs')
    threshold=(eta**2<=rho**(n-1))
    assert bool(result.success)==threshold
    witness=None
    if threshold:
     low=eta*2;high=rho**(n-1)*2/eta;C=(low+high)/2;kappa=1/eta-eta
     p=[(F(3)/eta-eta-C/rho**(n-j-1))/kappa for j in range(n)]
     assert all(1<=x<=3 for x in p)
     residuals=[sum(a*b for a,b in zip(row,p))-rr for row,rr in zip(rows,rhs)]
     assert len(set(residuals))==1
     witness=list(map(str,p))
    checks.append({'N':n,'k':k,'eta':str(eta),'rho':str(rho),'threshold_feasible':threshold,'scenario_LP_matches':True,'exact_constructive_witness':witness})
out={'cases':len(checks),'all_passed':True,'notes':'Exact rational feasible witnesses and independent scenario LP feasibility comparison; endpoint invariance only','results':checks}
(Path(__file__).parent/'independent_t6_threshold_check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2))
