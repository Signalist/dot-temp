"""One-shot frozen same-method ablation: no observations after initial p0.
No tuning and no hidden phase revelation. Global a in [0,5] at every update.
"""
from pathlib import Path
import numpy as np,json
from robust_filter import G,env_free,control_response,H,BACKUP
from validate_continuous import validate
OUT=Path(__file__).resolve().parent

def run(p0):
 starts=[0.,.05];us=[0.];z=0.;umax=0.
 for k in range(30):
  t=round(.05+k*.1,10);ss=np.arange(0.,5.005,.01);tt=t+ss
  low,up=env_free(tt,p0,0.,5.);past=control_response(tt,starts,us)
  base=up+past-BACKUP*G(ss-.1);baseL=low+past-BACKUP*G(ss-.1);coef=G(ss)-G(ss-.1)
  lb=0.;ub=BACKUP
  mask=coef>1e-10;lb=max(lb,float(np.max((base[mask]-H+.00005)/coef[mask])));ub=min(ub,float(np.min((baseL[mask]+H-.00005)/coef[mask])))
  mask=coef< -1e-10;ub=min(ub,float(np.min((base[mask]-H+.00005)/coef[mask])));lb=max(lb,float(np.max((baseL[mask]+H-.00005)/coef[mask])))
  mask=np.abs(coef)<=1e-10
  if lb>ub+1e-8 or np.any(base[mask]>H-.00005+1e-8) or np.any(baseL[mask]<-H+.00005-1e-8):return dict(fail=True,k=k,lb=lb,ub=ub,p0=p0,bin=0,phase_edge_interval=[0.,5.])
  u=max(0.,lb);us.append(u);starts.append(round(t+.1,10));z+=u*.1;umax=max(umax,u)
 us.append(0.);starts.append(10.)
 return dict(fail=False,p0=p0,bin=0,z=z,umax=umax,starts=starts,us=us,phase_edge_interval=[0.,5.],information='initial p0 only; no later observations')
if __name__=='__main__':
 rs=[run(p) for p in [1,2]];vs=[validate(r) for r in rs if not r['fail']]
 summary=dict(failed_histories=sum(r['fail'] for r in rs),max_frequency=max(v['max_abs_y'] for v in vs),max_power=max(v['max_abs_u'] for v in vs),common_e0=max(v['zmax'] for v in vs),common_E=max(v['zmax'] for v in vs)-min(v['zmin'] for v in vs),max_terminal_residual=max(v['terminal_residual'] for v in vs),safety_failed_histories=sum(v['max_abs_y']>.6 for v in vs),power_failed_histories=sum(v['max_abs_u']>.5 for v in vs),qualification='One frozen same-method no-feedback ablation; no additional tuning. Analytic continuous-phase/time reduction, double evaluation, phase endpoint pad1e-10.')
 (OUT/'no_feedback_policy.json').write_text(json.dumps(rs,indent=2));(OUT/'no_feedback_validation.json').write_text(json.dumps(vs,indent=2));(OUT/'no_feedback_results.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
