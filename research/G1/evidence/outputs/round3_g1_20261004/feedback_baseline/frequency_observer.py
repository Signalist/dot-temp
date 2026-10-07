"""Finite first-detection frequency observer with the same predictive filter.
All-noise guarantee is conditional on the documented residual-detection proof.
"""
from pathlib import Path
import numpy as np,json,time,math
import mpmath as mp
from scipy.optimize import brentq
from robust_filter import G,env_free,control_response,H,BACKUP
from validate_continuous import validate
OUT=Path(__file__).resolve().parent

def run(p0,j,tau,step=.01,margin=.00005):
 starts=[0.,.05];us=[0.];z=0.;umax=0.
 lo=max(0.,round((j-1)*.1-tau,10));hi=min(5.,round(j*.1,10))
 for k in range(30):
  t=round(.05+k*.1,10)
  if k<j:a,b=max(0.,round(k*.1-tau,10)),5.
  else:a,b=lo,hi
  ss=np.arange(0.,5.+step/2,step);tt=t+ss
  low,up=env_free(tt,p0,a,b);past=control_response(tt,starts,us)
  base=up+past-BACKUP*G(ss-.1);baseL=low+past-BACKUP*G(ss-.1);coef=G(ss)-G(ss-.1)
  lb=0.;ub=BACKUP
  mask=coef>1e-10;lb=max(lb,float(np.max((base[mask]-H+margin)/coef[mask])));ub=min(ub,float(np.min((baseL[mask]+H-margin)/coef[mask])))
  mask=coef< -1e-10;ub=min(ub,float(np.min((base[mask]-H+margin)/coef[mask])));lb=max(lb,float(np.max((baseL[mask]+H-margin)/coef[mask])))
  mask=np.abs(coef)<=1e-10
  if lb>ub+1e-8 or np.any(base[mask]>H-margin+1e-8) or np.any(baseL[mask]<-H+margin-1e-8):return dict(fail=True,k=k,lb=lb,ub=ub,p0=p0,detection=j,phase_edge_interval=[lo,hi])
  u=max(0.,lb);us.append(u);starts.append(round(t+.1,10));z+=u*.1;umax=max(umax,u)
 us.append(0.);starts.append(10.)
 return dict(fail=False,p0=p0,bin=j,detection=j,z=z,umax=umax,starts=starts,us=us,phase_edge_interval=[lo,hi])

if __name__=='__main__':
 out=[];start=time.time()
 for eta in [.005,.01,.02,.05]:
  tau=math.ceil(brentq(lambda t:t*np.exp(-t)-2*eta,0.,1.,xtol=5e-15)*1e10)/1e10;assert tau+.1<1
  mp.mp.dps=60; mt=mp.mpf(str(tau));assert mt*mp.exp(-mt)>=2*mp.mpf(str(eta))
  n=int(np.ceil((5+tau)/.1));rs=[];vs=[]
  for p0 in [1,2]:
   for j in range(1,n+1):
    r=run(p0,j,tau);rs.append(r)
    if not r['fail']:vs.append(validate(r))
  summary=dict(eta_y=eta,tau=tau,history_count=len(rs),failed_history_count=sum(r['fail'] for r in rs),max_frequency=max(v['max_abs_y'] for v in vs),max_power=max(v['max_abs_u'] for v in vs),common_e0=max(v['zmax'] for v in vs),common_E=max(v['zmax'] for v in vs)-min(v['zmin'] for v in vs),max_terminal_residual=max(v['terminal_residual'] for v in vs),interpretation='continuous time and phase for every overapproximating detection-history interval; all-noise if observer proof applies')
  (OUT/f'frequency_policy_eta_{eta:g}.json').write_text(json.dumps(rs,indent=2));(OUT/f'frequency_validation_eta_{eta:g}.json').write_text(json.dumps(vs,indent=2));out.append(summary);print(summary,flush=True)
 (OUT/'frequency_results.json').write_text(json.dumps(out,indent=2));print('elapsed',time.time()-start)
