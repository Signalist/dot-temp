import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize_scalar
from pathlib import Path
G=lambda t:np.maximum(t,0)*np.exp(-np.maximum(t,0))*(np.array(t)>=0)
K=lambda t:(1-np.array(t))*np.exp(-np.array(t))
DT=.1; D=.05; P=.5; BACKUP=.5-1e-9; H=.6

def Hresp(r):
 r=np.asarray(r); out=np.zeros_like(r,dtype=float)
 for j in range(7):out+=(-1)**j*G(r-5*j)
 return out

def env_free(t,p0,lo,hi):
 t=np.asarray(t); sg=3-2*p0
 vs=np.stack([p0*G(t)+sg*Hresp(t-lo),p0*G(t)+sg*Hresp(t-hi)])
 vmax=vs.max(axis=0);vmin=vs.min(axis=0)
 for j in range(7):
  jj=np.arange(j+1);w=(-1.)**jj*np.exp(5*jj);r=1+5*np.sum(jj*w)/np.sum(w)
  mask=(t-lo>=r)&(t-hi<=r)&(r>=5*j)&(r<=5*(j+1))
  v=p0*G(t)+sg*Hresp(r)
  vmax=np.where(mask,np.maximum(vmax,v),vmax);vmin=np.where(mask,np.minimum(vmin,v),vmin)
 for r in [0.,5.,10.,15.,20.,25.,30.]:
  mask=(t-lo>=r)&(t-hi<=r)
  v=p0*G(t)+sg*Hresp(r)
  vmax=np.where(mask,np.maximum(vmax,v),vmax);vmin=np.where(mask,np.minimum(vmin,v),vmin)
 return vmin,vmax

def control_response(t,starts,us):
 out=np.zeros_like(np.asarray(t),dtype=float)
 for i,u in enumerate(us):
  if abs(u)>1e-14:out-=u*(G(t-starts[i])-G(t-starts[i+1]))
 return out

def run(p0,binidx,step=.005,margin=.0001,horizon=5,mode='backup'):
 starts=[0.,D]; us=[0.]; z=0; umax=0
 firstsample=binidx+1; lo=round(binidx*.1,10);hi=round((binidx+1)*.1,10)
 for k in range(30):
  t=round(D+k*.1,10)
  if k<firstsample:a,b=round(k*.1,10),5.
  else:a,b=lo,hi
  # Require next control and max-discharge backup after next delivery safe.
  ss=np.arange(0,horizon+step/2,step);tt=t+ss
  low,up=env_free(tt,p0,a,b);past=control_response(tt,starts,us)
  if mode=='backup':
   base=up+past-BACKUP*G(ss-.1);coef=G(ss)-G(ss-.1)
   baseL=low+past-BACKUP*G(ss-.1)
  else:
   base=up+past;coef=G(ss)-G(ss-.1);baseL=low+past
  lb=0.;ub=BACKUP
  mask=coef>1e-10
  lb=max(lb,float(np.max((base[mask]-H+margin)/coef[mask])))
  ub=min(ub,float(np.min((baseL[mask]+H-margin)/coef[mask])))
  mask=coef< -1e-10
  ub=min(ub,float(np.min((base[mask]-H+margin)/coef[mask])))
  lb=max(lb,float(np.max((baseL[mask]+H-margin)/coef[mask])))
  mask=np.abs(coef)<=1e-10
  if lb>ub+1e-8 or np.any(base[mask]>H-margin+1e-8) or np.any(baseL[mask]<-H+margin-1e-8):
   return dict(fail=True,k=k,lb=lb,ub=ub,p0=p0,bin=binidx)
  u=max(0,lb);us.append(u);starts.append(round(t+.1,10));z+=u*.1;umax=max(umax,u)
 us.append(0.);starts.append(10.); return dict(fail=False,p0=p0,bin=binidx,z=z,umax=umax,starts=starts,us=us)
if __name__=='__main__':
 import time,json
 begin=time.time();rs=[]
 for p in [1,2]:
  for b in range(50):
   r=run(p,b,step=.01,margin=.00005);rs.append(r)
   print(p,b,{k:v for k,v in r.items() if k not in ['starts','us']},flush=True)
 Path(__file__).with_name('robust_policy.json').write_text(json.dumps(rs));print('elapsed',time.time()-begin)
