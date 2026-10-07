"""Independent outward interval evaluation of continuum-phase extrema.
MPMath interval arithmetic (50 decimal digits), not a proof assistant.
Policy prefix decimals treated as exact rationals; recovery defined by exact 3x3 solve.
Separate implementation of analytic exponential-polynomial candidates.
"""
from pathlib import Path
import json,math,time
import mpmath as mp
mp.mp.dps=65;mp.iv.dps=50
I=mp.iv.mpf;OUT=Path(__file__).resolve().parents[1];FB=OUT/'feedback_baseline'
def ii(x):return I(str(x))
def low(x):return mp.mpf(x._mpi_[0])
def high(x):return mp.mpf(x._mpi_[1])
def pt(x):return I([str(x),str(x)])
def gg(t):return t*mp.iv.exp(-t)
def ff(t):return 1-(1+t)*mp.iv.exp(-t)
def inv3(a):
 cof=[[((-1)**(i+j))*(a[(i+1)%3][(j+1)%3]*a[(i+2)%3][(j+2)%3]-a[(i+1)%3][(j+2)%3]*a[(i+2)%3][(j+1)%3]) for j in range(3)] for i in range(3)]
 # Use explicit minors, avoiding cyclic cofactor sign pitfalls.
 cof=[]
 for i in range(3):
  row=[]
  for j in range(3):
   rr=[k for k in range(3) if k!=i];cc=[k for k in range(3) if k!=j]
   row.append(((-1)**(i+j))*(a[rr[0]][cc[0]]*a[rr[1]][cc[1]]-a[rr[0]][cc[1]]*a[rr[1]][cc[0]]))
  cof.append(row)
 det=sum(a[0][j]*cof[0][j] for j in range(3));assert not low(det)<=0<=high(det)
 return [[cof[j][i]/det for j in range(3)] for i in range(3)]
CUTS=[10,11,19,20]
C=[[ii(CUTS[j+1]-CUTS[j]) for j in range(3)],[-(ff(ii(20-CUTS[j]))-ff(ii(20-CUTS[j+1]))) for j in range(3)],[-(gg(ii(20-CUTS[j]))-gg(ii(20-CUTS[j+1]))) for j in range(3)]]
CI=inv3(C)
def prefix_recovery(row):
 st=list(row['starts']);us=list(row['us']);segments=[]
 for a,b,u in zip(st[:-1],st[1:],us):
  if a>=10:break
  b=min(b,10.)
  if b>a:segments.append((str(a),str(b),ii(u)))
 zz=sum((u*(ii(b)-ii(a)) for a,b,u in segments),ii(0))
 xx=-sum((u*(ff(ii(20)-ii(a))-ff(ii(20)-ii(b))) for a,b,u in segments),ii(0))
 yy=-sum((u*(gg(ii(20)-ii(a))-gg(ii(20)-ii(b))) for a,b,u in segments),ii(0))
 rhs=[-zz,-xx,-yy];rec=[sum(CI[i][j]*rhs[j] for j in range(3)) for i in range(3)]
 segments+= [(str(a),str(b),u) for a,b,u in zip(CUTS[:-1],CUTS[1:],rec)]
 events=[];zs=[ii(0)]
 for a,b,u in segments:
  events.extend([(mp.mpf(a),-u),(mp.mpf(b),u)]);zs.append(zs[-1]+u*(ii(b)-ii(a)))
 # Merge time-coincident control events, but do not discard tiny terms.
 ev={}
 for t,v in events:ev[t]=ev.get(t,ii(0))+v
 ev=[(t,v) for t,v in sorted(ev.items()) if low(v)!=0 or high(v)!=0]
 return ev,zs,rec

def extrema(events,lo,hi,const=None):
 if const is None:const=ii(0)
 lo=mp.mpf(lo);hi=mp.mpf(hi)
 if hi<lo:return (mp.inf,-mp.inf,mp.mpf(0))
 cuts=sorted(set([lo,hi]+[t for t,v in events if lo<t<hi]));mini=mp.inf;maxi=-mp.inf;width=mp.mpf(0)
 for l,r in zip(cuts[:-1],cuts[1:]):
  active=[(t,v) for t,v in events if t<=l]
  A=sum((v*mp.iv.exp(pt(t)) for t,v in active),ii(0));B=-sum((v*pt(t)*mp.iv.exp(pt(t)) for t,v in active),ii(0))
  cand=[pt(l),pt(r)]
  if not low(A)<=0<=high(A):
   root=1-B/A
   if high(root)>=l and low(root)<=r:cand.append(I([str(max(l,low(root))),str(min(r,high(root)))]))
  else:
   # Degenerate uncertain A: bound the whole cell, conservative but safe.
   cand.append(I([str(l),str(r)]))
  for tt in cand:
   val=mp.iv.exp(-tt)*(A*tt+B)+const;mini=min(mini,low(val));maxi=max(maxi,high(val));width=max(width,high(val)-low(val))
 return mini,maxi,width

def validate(row):
 events,zs,rec=prefix_recovery(row);p0=row['p0'];sg=3-2*p0
 if 'phase_edge_interval' in row:lo,hi=map(lambda x:mp.mpf(str(x)),row['phase_edge_interval'])
 else:lo=mp.mpf(row['bin'])/10;hi=lo+mp.mpf('.1')
 lo=max(mp.mpf(0),lo-mp.mpf('1e-10'));hi=min(mp.mpf(5),hi+mp.mpf('1e-10'))
 mn=mp.inf;mx=-mp.inf;ww=mp.mpf(0)
 for r in [lo,hi]:
  ev=events+[(mp.mpf(0),ii(p0))]+[(r+5*j,ii(sg*((-1)**j))) for j in range(5) if r+5*j<=20]
  a,b,w=extrema(ev,0,20);mn=min(mn,a);mx=max(mx,b);ww=max(ww,w)
 # All phase stationary curves plus all load-edge kink curves.
 lags=[ii(5*j) for j in range(5)]
 for j in range(4):
  weights=[ii((-1)**k)*mp.iv.exp(ii(5*k)) for k in range(j+1)]
  lag=1+5*sum(ii(k)*weights[k] for k in range(j+1))/sum(weights)
  if high(lag)>=5*j and low(lag)<=5*(j+1):lags.append(lag)
 for lag in lags:
  a=max(mp.mpf(0),lo+low(lag));b=min(mp.mpf(20),hi+high(lag))
  if b<=a:continue
  # On fixed lag t-r, phase part is constant. Evaluate H on each branch.
  c=ii(0)
  for j in range(5):
   d=lag-ii(5*j)
   if high(d)<0:continue
   if low(d)<0:d=I(['0',str(high(d))])
   c+=ii(sg*((-1)**j))*gg(d)
  m,M,w=extrema(events+[(mp.mpf(0),ii(p0))],a,b,c);mn=min(mn,m);mx=max(mx,M);ww=max(ww,w)
 pu=max([abs(mp.mpf(str(u))) for u in row['us']]+[max(abs(low(u)),abs(high(u))) for u in rec]);zmin=min(low(z) for z in zs);zmax=max(high(z) for z in zs)
 return dict(p0=p0,history=int(row.get('detection',row['bin'])),phase_interval=[str(lo),str(hi)],frequency_abs_upper=str(max(mx,-mn)),power_abs_upper=str(pu),zmin_lower=str(zmin),zmax_upper=str(zmax),max_interval_width=str(ww),soc_final_interval=[str(low(zs[-1])),str(high(zs[-1]))])

def main():
 files=['robust_policy.json']+[f'frequency_policy_eta_{e}.json' for e in ['0.005','0.01','0.02','0.05']]+['no_feedback_policy.json'];out=[]
 for fname in files:
  st=time.time();rows=json.loads((FB/fname).read_text());vs=[validate(r) for r in rows if not r['fail']]
  e0=max(mp.mpf(v['zmax_upper']) for v in vs);E=e0-min(mp.mpf(v['zmin_lower']) for v in vs)
  summary=dict(policy=fname,histories=len(vs),all_histories_feasible=len(vs)==len(rows),frequency_upper=str(max(mp.mpf(v['frequency_abs_upper']) for v in vs)),power_upper=str(max(mp.mpf(v['power_abs_upper']) for v in vs)),common_e0_upper=str(e0),common_capacity_upper=str(E),max_interval_width=str(max(mp.mpf(v['max_interval_width']) for v in vs)),seconds=time.time()-st,arithmetic='mpmath.iv 50 dps directed interval operations; exact decimal prefix policy; recovery defined by real 3x3 solve; finite analytic extrema including phase kinks; every phase interval widened 1e-10 and clipped[0,5]; not a proof assistant')
  (OUT/'raw'/f'interval_{fname}').write_text(json.dumps(dict(summary=summary,histories=vs),indent=2));out.append(summary);print(json.dumps(summary),flush=True)
 (OUT/'raw'/'interval_summary.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':main()
