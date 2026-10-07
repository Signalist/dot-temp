"""Diagnostic post-hoc comparator: midpoint state-estimate sampled CBF.
Unconstrained QP commands retained when they exceed P; never silently clipped.
"""
from pathlib import Path
import numpy as np,json
from robust_filter import G,control_response
from validate_continuous import F,validate
OUT=Path(__file__).resolve().parent

def run(p0,b,alpha):
 st=[0.,.05];us=[0.];lo=round(b*.1,10);hi=round((b+1)*.1,10)
 for k in range(100):
  t=round(.05+.1*k,10)
  a=(k*.1+5)/2 if k<b+1 else (lo+hi)/2
  sg=3-2*p0
  x=p0*F(t)+sg*sum((-1)**j*F(t-a-5*j) for j in range(3))
  y=p0*float(G(t))+sg*sum((-1)**j*float(G(t-a-5*j)) for j in range(3))
  for aa,bb,u in zip(st[:-1],st[1:],us):
   x-=u*(F(t-aa)-F(t-bb));y-=u*(float(G(t-aa))-float(G(t-bb)))
  p=p0 if t<a else (3-p0 if int((t-a)//5)%2==0 else p0)
  lower=p-2*y-x-alpha*(.6-y);upper=p-2*y-x+alpha*(.6+y)
  u=lower if lower>0 else (upper if upper<0 else 0.)
  us.append(float(u));st.append(round(t+.1,10))
 return dict(p0=p0,bin=b,starts=st,us=us,alpha=alpha)

if __name__=='__main__':
 summaries=[]
 for alpha in [6.,10.]:
  rs=[];vs=[]
  for p0 in [1,2]:
   for b in range(50):
    r=run(p0,b,alpha);v=validate(r);v['alpha']=alpha;rs.append(r);vs.append(v)
  e0=max(v['zmax'] for v in vs)
  summary=dict(alpha=alpha,max_frequency=max(v['max_abs_y'] for v in vs),max_power=max(v['max_abs_u'] for v in vs),common_e0=e0,common_E=e0-min(v['zmin'] for v in vs),frequency_failed_bins=sum(v['max_abs_y']>.6+1e-9 for v in vs),power_failed_bins=sum(v['max_abs_u']>.5+1e-9 for v in vs),qualification='Unclipped sampled midpoint CBF; failed power rows are infeasible relaxed commands; diagnostic run after predictive design, not pretended chronological development')
  (OUT/f'nominal_cbf_alpha_{alpha:g}_policy.json').write_text(json.dumps(rs));(OUT/f'nominal_cbf_alpha_{alpha:g}_validation.json').write_text(json.dumps(vs,indent=2));summaries.append(summary);print(summary,flush=True)
 (OUT/'nominal_cbf_results.json').write_text(json.dumps(summaries,indent=2))
