"""Exact bridge reduction + finite-point upper/interval-box lower Bellman chains.
Bounds are analytic in model; numeric values use floating arithmetic, not outward rounding.
"""
from pathlib import Path
import numpy as np,json,time
from cycle_model import Case,power_int
ROOT=Path(__file__).resolve().parents[1]

def H(c,z):return c.H(np.maximum(z,0.))
def bridge(c,a,b,dx):
 a=np.asarray(a);b=np.asarray(b);cap=float(c.A(c.critical))
 q=np.minimum((a+b+c.R*dx)/2,cap)
 plateau=np.maximum(0.,dx-(2*q-a-b)/c.R)
 return 2*H(c,q)-H(c,a)-H(c,b)+plateau*c.G(cap)

def states(c,x,n,boxes):
 cap=float(min(c.R*x,c.R*(1-x),c.A(c.critical)))
 if cap<=0:return np.array([0.]),np.array([0.])
 v=np.linspace(0,cap,n+1)
 return (v[:-1],v[1:]) if boxes else (v,v)

def dp(c,work,prob,n=256,boxes=False):
 xs=np.r_[0,work];nodes=[states(c,x,n,boxes) for x in xs]
 cost=np.array([0.]);choices=[];S=1.
 for i in range(len(work)):
  al,ah=nodes[i];bl,bh=nodes[i+1];dx=xs[i+1]-xs[i];best=np.full(len(bl),np.inf);arg=np.full(len(bl),-1,dtype=int)
  # Blocks keep memory bounded as interval precision increases.
  for start in range(0,len(bl),128):
   stop=min(len(bl),start+128);alo=al[:,None];ahi=ah[:,None];blo=bl[None,start:stop];bhi=bh[None,start:stop]
   valid=(alo<=bhi+c.R*dx+1e-14)&(blo<=ahi+c.R*dx+1e-14)
   a=np.minimum(ahi,bhi+c.R*dx);b=np.minimum(bhi,ahi+c.R*dx)
   costs=cost[:,None]+S*bridge(c,a,b,dx)+prob[i]*H(c,blo)
   costs=np.where(valid,costs,np.inf);idx=np.argmin(costs,axis=0)
   best[start:stop]=costs[idx,np.arange(stop-start)];arg[start:stop]=idx
  choices.append(arg);cost=best;S-=prob[i]
 inds=[0]
 for arg in choices[::-1]:inds.append(int(arg[inds[-1]]))
 inds=inds[::-1];policy=[float(nodes[i][0][k]) for i,k in enumerate(inds)]
 return float(cost[0]),policy

def segments(c,work,z):
 xs=np.r_[0,work];segs=[];cap=float(c.A(c.critical))
 for i in range(len(work)):
  a,b=z[i],z[i+1];dx=xs[i+1]-xs[i];q=min((a+b+c.R*dx)/2,cap)
  left=(q-a)/c.R;right=(q-b)/c.R;plateau=max(0.,dx-left-right)
  points=[(xs[i],a),(xs[i]+left,q),(xs[i]+left+plateau,q),(xs[i+1],b)]
  for (x0,z0),(x1,z1) in zip(points[:-1],points[1:]):
   if x1-x0>1e-14:segs.append((x0,x1,z0,z1))
 return segs

def physical(c,work,prob,z):
 segs=segments(c,work,z);paths=[];K=1+c.beta
 for W,pr in zip(work,prob):
  task=energy=0.;ledger=[]
  for x0,x1,a,b in segs:
   if x0>=W-1e-14:break
   hi=min(x1,W);end=a+(b-a)*(hi-x0)/(x1-x0)
   dt=K**(-c.beta/K)*power_int(a,end,-c.beta/K,hi-x0)
   E=K**((1-c.beta)/K)*power_int(a,end,(1-c.beta)/K,hi-x0)
   ledger.append({'x0':x0,'x1':hi,'z0':a,'z1':end,'slew':(end-a)/(hi-x0),'time':dt,'energy':E,'power0':float(c.P(a)),'power1':float(c.P(end))})
   task+=dt;energy+=E
  p=float(c.P(z[list(work).index(W)+1]));burn=p*p/(2*c.R);tail=p/c.R
  paths.append({'W':W,'probability':pr,'task_time':task,'cycle_time':task+tail,'dynamic_energy':energy+burn,'burn_energy':burn,'objective':energy+burn+c.c*(task+tail),'segments':ledger})
 return {'paths':paths,'mean_objective':sum(p['probability']*p['objective'] for p in paths),'mean_cycle_time':sum(p['probability']*p['cycle_time'] for p in paths),'mean_dynamic_energy':sum(p['probability']*p['dynamic_energy'] for p in paths)}

def run():
 work=[.1,.3,.6,1.];out=[]
 for beta in (.5,.8):
  for R in (.5,4.):
   for prob in ([.25]*4,[.55,.25,.15,.05]):
    c=Case(beta,R,1.);row={'case':c.__dict__,'work':work,'probabilities':prob,'refinements':[]}
    for n in (128,512,2048):
     t=time.perf_counter();lower,_=dp(c,work,prob,n,True);upper,z=dp(c,work,prob,n,False)
     row['refinements'].append({'intervals_per_node':n,'lower':lower,'upper':upper,'gap':upper-lower,'relative_gap':(upper-lower)/upper,'z_endpoints':z,'seconds':time.perf_counter()-t})
    row['physical']=physical(c,work,prob,z);row['ledger_objective_difference']=abs(row['physical']['mean_objective']-upper)
    out.append(row);(ROOT/'results/ATOMIC_GLOBAL_BOUNDS.json').write_text(json.dumps(out,indent=2))
    print(beta,R,prob,row['refinements'][-1]['relative_gap'],row['ledger_objective_difference'],flush=True)
if __name__=='__main__':run()
