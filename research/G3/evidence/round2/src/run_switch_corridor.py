import json,sys
from pathlib import Path
from dataclasses import replace
import numpy as np
import model
import admission
import exact_outer
from envelope import up
from scipy.optimize import minimize_scalar
root=Path(__file__).resolve().parents[1];outdir=root/'results'/'switch_corridor';outdir.mkdir(exist_ok=True)
knots=np.unique(np.round(np.r_[0,.001,.005,.055,np.linspace(.08,.24,65),.26,.31,.32,.33,.37,.38,.4],12))
loadtimes=np.linspace(.08,.24,65); loadshape=np.sin(2*np.pi*(loadtimes-.08)/.04);loadshape[np.abs(loadshape)<1e-12]=0
model.base_knots=lambda par:knots
model.recovery=lambda t:np.interp(t,[.32,.33,.37,.38],[0,1,1,0],left=0,right=0)
def custom(t,alpha,beta,par=model.Params()):
 t=np.asarray(t);g=np.interp(t,[.005,.055,.26,.31],[0,1,1,0],left=0,right=0);r=model.recovery(t)
 gg=.205+2*.05/3;ra=.05;rr=.04+2*.01/3;c=par.losscoef
 aa=c*rr;bb=-ra*(1-2*c*par.p0);cc=c*beta**2*gg
 gamma=2*cc/(-bb+np.sqrt(bb*bb-4*aa*cc))
 return dict(p=par.p0+gamma*r,q=beta*g,d=par.D0+500*np.interp(t,loadtimes,loadshape,left=0,right=0),gamma=float(gamma))
model.profiles=custom
rows=[]
for ramp in [3000,5000,10000,30000]:
 for q in [900,1000,1050]:
  p=replace(model.Params(),T=.4,ramp=ramp)
  m=model.poly_segments(model.grid(p,160),0,q,p)
  minlo=1e9;minhi=1e9
  for k,h in enumerate(m['h']):
   for typ in ['lower','upper','mod']:
    def f(x):
     A=np.polynomial.polynomial.polyval(x,m['offset'][k]);C=up(m['t'][k]+h*x,p)[1]
     if typ=='upper':return p.Wmax-(p.W0+A-C)
     bound=p.Wmin if typ=='lower' else np.polynomial.polynomial.polyval(x,m['modfloor'][k])
     return p.W0+A+C-bound
    rr=minimize_scalar(f,bounds=(0,1),method='bounded');mm=min(f(0),f(1),rr.fun)
    if typ=='upper':minhi=min(minhi,mm)
    else:minlo=min(minlo,mm)
  inn=admission.solve_inner(0,q,160,p,save=outdir/f'spline_R{ramp}_q{q}.npz')
  ext=exact_outer.solve_exact_outer(0,q,160,p,max_iter=100,save=outdir/f'exact_R{ramp}_q{q}.npz')
  row=dict(ramp=ramp,beta=q,prefix_lower_margin_kJ=minlo,prefix_upper_margin_kJ=minhi,inner=inn,exact_outer=ext,energy_residual=m['energy_residual'])
  rows.append(row);print(ramp,q,minlo,minhi,inn.get('margin_kJ',inn['status']),ext.get('margin_kJ',ext['status']),flush=True)
  (outdir/'RESULTS.json').write_text(json.dumps(rows,indent=2))
