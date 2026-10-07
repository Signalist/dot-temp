import json,sys,time
from pathlib import Path
from admission import *
root=Path(__file__).resolve().parents[1]; rows=[]
for n in [40,80,160]:
 for alpha in [0,100,200,300]:
  for beta in [0,300,600,900,1200]:
   inn=solve_inner(alpha,beta,n,save=root/'results'/f'witness_a{alpha}_q{beta}_n{n}.npz')
   out=solve_outer(alpha,beta,n)
   row=dict(alpha=alpha,beta=beta,n=n,inner=inn,outer=out); rows.append(row)
   print(alpha,beta,n,inn.get('margin_kJ',inn['status']),out.get('outer_margin_kJ',out['status']),flush=True)
   (root/'results'/'PRIMARY_CAMPAIGN.json').write_text(json.dumps(rows,indent=2))
print('DONE',len(rows))
