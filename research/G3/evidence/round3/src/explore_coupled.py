from pathlib import Path
import sys,json
import numpy as np
from scipy.integrate import cumulative_trapezoid,simpson
from scipy.optimize import minimize,brentq,minimize_scalar
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'prior_core'
sys.path.insert(0,str(OLD/'src'))
from model import Params
from envelope import up
p=Params();c=p.losscoef;k=p.L/(3000*p.v**2);Gp=1500*p.v;Kap=np.sqrt(1500*p.Cdc)
P=p.p0-100.;m=1-2*c*P

def values(eps,beta,left,right,angle,N=2001,mode='coupled'):
 t=np.linspace(left,right,N);w=right-left;n=np.array([np.cos(angle),np.sin(angle)])
 h=np.sin(np.pi*(t-left)/w)**2;hp=np.pi/w*np.sin(2*np.pi*(t-left)/w)
 ad=p.L*n[0]*hp-(p.R*n[0]+p.omega*p.L*n[1])*h
 aq=p.L*n[1]*hp-(p.R*n[1]-p.omega*p.L*n[0])*h
 ramp=.005*(-(100+p.Aload)/2+c*p.p0*100-c*(100**2+beta**2)/3)
 slope=-100-p.Aload+2*c*p.p0*100-c*100**2-c*beta**2
 H=p.W0+ramp+(t-.005)*slope-k*(P**2+beta**2-p.p0**2)+up(t,p)[1]
 if H.min()<=0:return dict(margin=-1e6)
 ed=p.v-p.R*P/Gp+p.omega*p.L*beta/Gp;eq=-p.R*beta/Gp-p.omega*p.L*P/Gp
 M=(n[0]*ed+n[1]*eq)*w/2
 rhs=simpson(h*np.sqrt(H)/Kap,x=t)
 z=h/(2*Kap*np.sqrt(H));r=-np.r_[cumulative_trapezoid(z[::-1],t[::-1]),0][::-1] # fix below
 r=np.r_[0,cumulative_trapezoid(z,t)];r=r[-1]-r
 a=ad/Gp+2*k*z*P-r*m
 b=-aq/Gp-2*k*z*beta-r*2*c*beta
 d=k*z+r*c
 if mode=='no_prefix':
  a=ad/Gp+2*k*z*P;b=-aq/Gp-2*k*z*beta;d=k*z
 if mode=='uncoupled':
  a=ad/Gp;b=-aq/Gp;d=np.zeros_like(z)
 def dual(logl):
  lam=np.exp(logl)
  f=(np.maximum(a-lam*m,0)**2+np.maximum(b-lam*2*c*beta,0)**2)/(4*(d+lam*c))
  return lam*eps+simpson(f,x=t)
 opt=minimize_scalar(dual,bounds=(-30,0),method='bounded',options={'xatol':1e-12})
 E=opt.fun if eps>0 else 0.
 return dict(margin=float(M-rhs-E),M=float(M),rhs=float(rhs),E=float(E),lam=float(np.exp(opt.x)),Hmin=float(H.min()),window=[left,right],angle=angle,beta=beta,eps=eps)

if __name__=='__main__':
 rows=[]
 for eps in [0,.001,.01,.1,1.]:
  def obj(v):
   a,b,ang=v
   if not(.005<=a<b<=.035 and b-a>=.002):return 1e3
   try:q=brentq(lambda q:values(eps,q,a,b,ang,N=1001)['margin'],750,1000,xtol=1e-7)
   except:return 1e3
   return q
  opt=minimize(obj,[.009,.027,-.1],method='Nelder-Mead',options={'maxiter':400,'xatol':1e-9,'fatol':1e-7})
  a,b,ang=opt.x;q=brentq(lambda q:values(eps,q,a,b,ang,N=20001)['margin'],750,1000,xtol=1e-9)
  row=values(eps,q+.1,a,b,ang,N=20001);row['root']=q;row['search_success']=bool(opt.success);rows.append(row);print(row,flush=True)
 (ROOT/'results'/'coupled_exploration.json').write_text(json.dumps(rows,indent=2))
