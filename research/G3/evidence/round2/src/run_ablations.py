import json,sys
from pathlib import Path
from dataclasses import replace
import numpy as np
import admission as adm
import model
root=Path(__file__).resolve().parents[1];(root/'results'/'ablations').mkdir(exist_ok=True)
original=adm.poly_segments; original_profiles=model.profiles
rows=[]
for a,q in [(100,600),(100,900),(200,0),(100,810)]:
 for var in ['full','omit_inductive_energy_only','zero_delay','zero_lag','ramp100x','omit_modulation']:
  p=model.Params(); mod=True
  if var=='zero_delay':p=replace(p,delay=0.)
  if var=='zero_lag':p=replace(p,tau=0.)
  if var=='ramp100x':p=replace(p,ramp=p.ramp*100)
  if var=='omit_modulation':mod=False
  if var=='omit_inductive_energy_only':
   def noenergy(*args,**kw):
    z=original(*args,**kw); zz=z['z'].copy(); zz[:,0]-=z['z'][0,0]; z['offset']+=zz; z['final_A']=float(z['offset'][-1].sum());return z
   adm.poly_segments=noenergy
  else:adm.poly_segments=original
  r=adm.solve_inner(a,q,160,p,modulation=mod);rows.append(dict(alpha=a,beta=q,variant=var,result=r));print(a,q,var,r.get('margin_kJ',r['status']),flush=True)
adm.poly_segments=original
for b0 in [10,15,50]:
 for relaxed in [False,True]:
  p=replace(model.Params(),B0=b0,Bmin=-1000 if relaxed else 0,Bmax=1000 if relaxed else 2*b0)
  r=adm.solve_inner(100,600,160,p);rows.append(dict(family='inventory_bounds',B0=b0,relaxed=relaxed,result=r));print('inventory',b0,relaxed,r.get('margin_kJ',r['status']),flush=True)
def no_comp(t,alpha,beta,par=model.Params()):
 v=original_profiles(t,alpha,beta,par);v['p']=v['p']-v['gamma']*model.recovery(t);v['gamma']=0.;return v
model.profiles=no_comp
for orbit,inv in [(True,True),(True,False),(False,True),(False,False)]:
 fn=root/'results'/'ablations'/f'no_comp_orbit{int(orbit)}_inventory{int(inv)}.npz'
 r=adm.solve_inner(100,600,160,inventory=inv,restore_orbit=orbit,save=fn)
 if fn.exists():
  z=np.load(fn);r['final_W_minus_W0_kJ']=float(z['Wpoly'][-1].sum()-model.Params().W0);r['final_B_minus_B0_kJ']=float(z['Bpoly'][-1].sum()-model.Params().B0)
 rows.append(dict(family='no_comp_terminal_contract',orbit=orbit,inventory=inv,result=r));print('terminal',orbit,inv,r,flush=True)
model.profiles=original_profiles
(root/'results'/'ABLATION_RESULTS.json').write_text(json.dumps(rows,indent=2))
