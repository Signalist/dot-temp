"""Independent scalar analytic necessary witness, requiring no optimizer dual.
Every physical b satisfies b<=forward maximum from held-zero initial command;
therefore C(t)<=the closed-form integral below. Test actual prescribed-path
capacitor and modulation floors against this optimistic energy ceiling.
"""
from pathlib import Path
import numpy as np,json
from scipy.optimize import minimize_scalar
from independent_audit import witness_audit
ROOT=Path(__file__).resolve().parents[1]

def maxcharge(t,p):
 z=max(0,t-p['delay']);U=p['umax'];r=p['ramp'];tau=p['tau']
 switch=max(0,U/r-tau)
 if z<=switch:return .5*r*z*z
 # For the frozen b(0)=0, U>tau*r; independent explicit ramp→lag flow.
 if switch==0:return U*z-U*tau*(-np.expm1(-z/tau))
 q=z-switch
 return .5*r*switch*switch+U*q-tau*tau*r*(-np.expm1(-q/tau))

rows=[]
for f in sorted((ROOT/'results').glob('witness*_n160.npz')):
 w,data=witness_audit(f);p,t,P,Q,D,Wpol,U,E=data
 z=np.load(f);bc=np.column_stack((z['b'][:-1],z['a'],z['c']));C=0;minimum={'margin_kJ':1e9}
 W0=500*p['Cdc']*p['vdc0']**2;Wmin=500*p['Cdc']*p['vdcmin']**2
 for k,h in enumerate(np.diff(t)):
  battery=np.array([C,h*bc[k,0],h*bc[k,1]/2,h*bc[k,2]/3]);base=Wpol[k]-battery;C=float(sum(battery))
  for tag in ['DC_lower','modulation']:
   def gap(x):
    ceiling=sum(base[j]*x**j for j in range(4))+maxcharge(t[k]+h*x,p)
    floor=Wmin if tag=='DC_lower' else 1500*p['Cdc']*sum((E[k,0]+x*E[k,1])**2)
    return ceiling-floor
   opt=minimize_scalar(gap,bounds=(0,1),method='bounded',options={'xatol':1e-14})
   candidates=[(0,gap(0)),(1,gap(1)),(opt.x,opt.fun)]
   x,v=min(candidates,key=lambda kv:kv[1])
   if v<minimum['margin_kJ']:minimum={'margin_kJ':float(v),'time_s':float(t[k]+h*x),'segment':k,'side_fraction':float(x),'violated_floor':tag}
 rows.append({'alpha_kW':w['alpha_kW'],'beta_kvar':w['beta_kvar'],**minimum,'analytic_envelope_excludes':bool(minimum['margin_kJ'] < -1e-6)})
res={'method':'Necessary scalar comparison: maximum physically reachable buffer charge under u=umax and slew, starting held at zero. Ignores endpoint recovery and inventory bounds so it is optimistic. Exclusion uses this upper energy ceiling. One explicit violating time suffices; global minimization is not required to validate that witness.','cases':rows}
(ROOT/'audit/ANALYTIC_EXCLUSIONS.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
