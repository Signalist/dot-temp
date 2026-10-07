"""Numerical falsification tests of analytical nominal claims; not an all-phase proof."""
from pathlib import Path
import json, numpy as np
from scipy.integrate import solve_ivp
OUT=Path(__file__).resolve().parent
C=json.loads((OUT/'theory_constants.json').read_text())
phases=np.unique(np.r_[np.linspace(0,10,101)[:-1],5-np.array([.1,.15,.2,.21,.22,.25,.3,.35,.4,.5]),np.sqrt(2),5+np.sqrt(3),1e-10,5-1e-10,5+1e-10,10-1e-10])
rows=[]
for hh in [.5988,.6]:
 for theta in phases:
  ee=sorted(set([0.,10.]+[5*k-theta for k in range(5) if 0<5*k-theta<10]));z=np.zeros(3);up=yp=last=0.;ep=0;prev=False
  for a,b in zip(ee[:-1],ee[1:]):
   p=2. if (theta+(a+b)/2)%10<5 else 1.
   def rhs(t,s):
    u=max(0.,2-5*hh-s[0]+3*s[1]);return [s[1],p-2*s[1]-s[0]-u,u]
   sol=solve_ivp(rhs,[a,b],z,rtol=2e-11,atol=2e-13,max_step=.015,dense_output=True)
   tt=np.linspace(a,b,max(2,int((b-a)/.003)+1));ss=sol.sol(tt);uu=np.maximum(0.,2-5*hh-ss[0]+3*ss[1]);up=max(up,float(max(uu)));yp=max(yp,float(max(abs(ss[1]))));active=uu>1e-8
   for t,act in zip(tt,active):
    if act:last=max(last,float(t))
    if act and not prev:ep+=1
    prev=act
   z=sol.y[:,-1]
  rows.append(dict(h=hh,theta=float(theta),power=up,frequency=yp,discharge=float(z[2]),last_active=last,episodes=ep))
for hh,key in [(.5988,'tight_nominal'),(.6,'loose_nominal')]:
 rr=[r for r in rows if r['h']==hh];c=C[key]
 assert max(r['power'] for r in rr)<=c['peak_power']+1e-7
 assert max(r['discharge'] for r in rr)<=c['discharge']+1e-7
 assert max(r['frequency'] for r in rr)<=hh+1e-7
 assert max(r['last_active'] for r in rr)<=c['support_upper']+1e-6
 assert max(r['episodes'] for r in rr)<=1
summary={'tested_phases_per_bound':len(phases),'bounds':[.5988,.6],'runs':len(rows),'all_checks_passed':True,'maxima':{str(hh):{k:max(r[k] for r in rows if r['h']==hh) for k in ['power','frequency','discharge','last_active','episodes']} for hh in [.5988,.6]},'qualification':'Finite numerical falsification tests only. Universal conclusions come from the analytical proof.'}
(OUT/'nominal_falsification_results.json').write_text(json.dumps({'summary':summary,'rows':rows},indent=2));print(json.dumps(summary,indent=2))
