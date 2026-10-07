"""Independent continuous-time/continuous-phase verifier for fixed history policies.
Uses finite exact candidate reduction for critical damping; no producer imports.
"""
import numpy as np
from scipy.linalg import expm
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
A=np.array([[0.,1.],[-1.,-2.]])
B=np.array([0.,-1.])
def phi(t):return np.exp(-t)*np.array([[1+t,t],[-t,1-t]])
def g(t):return t*np.exp(-t) if t>=0 else 0.
def F(t):return 1-(1+t)*np.exp(-t) if t>=0 else 0.
def H(r):return sum((-1)**j*g(r-5*j) for j in range(5))
def stationary_lags():
 roots=[]
 for j in range(5):
  inds=np.arange(j+1);ws=(-1.)**inds*np.exp(5*inds)
  r=1+5*np.sum(inds*ws)/sum(ws)
  if 5*j<=r<=5*(j+1):roots.append(float(r))
 return sorted(set(roots+[0.,5.,10.,15.,20.]))

def extrema(events,lo,hi,constant=0.):
 events=[(float(a),float(v)) for a,v in events if a<=hi and abs(v)>1e-15]
 cuts=sorted(set([lo,hi]+[a for a,v in events if lo<a<hi]))
 bestp=(-np.inf,None);bestn=(np.inf,None)
 for l,r in zip(cuts[:-1],cuts[1:]):
  # The contribution of an event exactly at l is zero but its derivative is not.
  yy=sum(v*g(l-a) for a,v in events if a<=l+1e-12)
  mm=sum(v*np.exp(-(l-a)) for a,v in events if a<=l+1e-12)
  ts=[0.,r-l]
  if abs(mm)>1e-18:
   q=1-yy/mm
   if 0<q<r-l:ts.append(q)
  for s in ts:
   y=np.exp(-s)*(yy+mm*s)+constant
   if y>bestp[0]:bestp=(float(y),float(l+s))
   if y<bestn[0]:bestn=(float(y),float(l+s))
 return bestn,bestp

def validate(row):
 st=np.array(row['starts']);us=np.array(row['us'])
 # Ignore the zero last interval that straddles time10 in prototype.
 assert not np.any(abs(us[st[:-1]>=9.9])>1e-12)
 mask=st[:-1]<10; st0=list(st[:-1][mask]);uu=list(us[mask]);st0.append(10.)
 z=sum(u*(b-a) for a,b,u in zip(st0[:-1],st0[1:],uu))
 cc=np.array([-sum(u*(F(10-a)-F(10-b)) for a,b,u in zip(st0[:-1],st0[1:],uu)), -sum(u*(g(10-a)-g(10-b)) for a,b,u in zip(st0[:-1],st0[1:],uu))])
 rcuts=[10.,11.,19.,20.]
 C=np.vstack([np.diff(rcuts),np.array([phi(20-b)@np.linalg.solve(A,(phi(b-a)-np.eye(2)))@B for a,b in zip(rcuts[:-1],rcuts[1:])]).T])
 rr=np.linalg.solve(C,np.r_[-z,-phi(10)@cc])
 allst=np.r_[st0,rcuts[1:]];allu=np.r_[uu,rr]
 events=[];last=0
 for a,u in zip(allst[:-1],allu):
  events.append((a,last-u));last=u
 events.append((20.,last))
 allz=np.r_[0.,np.cumsum(allu*np.diff(allst))]
 p0=row['p0'];lo,hi=row.get('phase_edge_interval',[.1*row['bin'],.1*row['bin']+.1]);sg=3-2*p0
 worstp=(-np.inf,None,None);worstn=(np.inf,None,None)
 for a in [lo,hi]:
  ev=events+[(0.,p0)]+[(a+5*j,sg*(-1)**j) for j in range(5)]
  mn,mx=extrema(ev,0,20)
  if mx[0]>worstp[0]:worstp=(*mx,float(a))
  if mn[0]<worstn[0]:worstn=(*mn,float(a))
 for r in stationary_lags():
  l=max(0.,lo+r);h=min(20.,hi+r)
  if h<=l:continue
  mn,mx=extrema(events+[(0.,p0)],l,h,sg*H(r))
  if mx[0]>worstp[0]:worstp=(*mx,float(mx[1]-r))
  if mn[0]<worstn[0]:worstn=(*mn,float(mn[1]-r))
 terminal=C@rr+np.r_[z,phi(10)@cc]
 return dict(p0=p0,bin=row['bin'],phase_edge_interval=[lo,hi],max_y=worstp,min_y=worstn,max_abs_y=max(worstp[0],-worstn[0]),max_abs_u=float(max(abs(allu))),zmax=float(max(allz)),zmin=float(min(allz)),terminal_residual=float(max(abs(terminal))),recovery=rr.tolist(),control_events=events)

if __name__=='__main__':
 rows=json.loads((OUT/'robust_policy.json').read_text()); vals=[validate(r) for r in rows if not r['fail']]
 e0=max(r['zmax'] for r in vals);E=e0-min(r['zmin'] for r in vals)
 result=dict(common_e0=e0,common_E=E,max_frequency=max(r['max_abs_y'] for r in vals),max_power=max(r['max_abs_u'] for r in vals),max_terminal_residual=max(r['terminal_residual'] for r in vals),phase_bins=len(vals),continuous_phase_reduction='Endpoints plus stationary lags of alternating step response, analytic exponential-affine time extrema',arithmetic='double precision evaluation; not outward interval-rounded',tail_bound=1/np.e+20*np.exp(-20))
 (OUT/'continuous_results.json').write_text(json.dumps(dict(summary=result,bins=vals),indent=2));print(json.dumps(result,indent=2));print('worst', {k:v for k,v in max(vals,key=lambda r:r['max_abs_y']).items() if k !='control_events'})
