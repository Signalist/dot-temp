"""Round3 G1: exact-ZOH phase resource LP with explicit information constraints.
New directory only. Bound labels separate outer arbitrary controls from inner ZOH.
"""
from pathlib import Path
import json,time, numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
ROOT=Path(__file__).resolve().parents[1]
def g(t):
 t=np.asarray(t); z=np.maximum(t,0); return np.where(t>=0,z*np.exp(-z),0.)
def free(t,r,high,L=5.):
 y=(2 if high else 1)*g(t)
 for k in range(int(max(t)/L)+2):y+=(-1 if high else 1)*(-1)**k*g(t-r-k*L)
 return y
def envelope(t,lo,hi,high,L=5.):
 if hi-lo<1e-14:return free(t,lo,high,L),free(t,hi,high,L)
 # exact analytic phase extrema, including moving discontinuity boundaries
 mn=[];mx=[]
 for tt in t:
  cuts=sorted(set([lo,hi]+[tt-k*L for k in range(int(tt/L)+2) if lo<tt-k*L<hi]));cand=list(cuts)
  for a,b in zip(cuts[:-1],cuts[1:]):
   mid=(a+b)/2;N=int(np.floor((tt-mid)/L))
   if N>=0:
    ks=np.arange(N+1);ws=(-1.)**ks*np.exp(-tt+ks*L);den=ws.sum()
    root=-np.sum(ws*(1-tt+ks*L))/den
    if a<root<b:cand.append(root)
  vals=free(np.full(len(cand),tt),np.array(cand),high,L)
  mn.append(vals.min());mx.append(vals.max())
 return np.array(mn),np.array(mx)
def build_solve(name,phases,branches,dt=.01,H=5.,P=.5,b=.6,inner=False,nonnegative=False,save=True):
 # branches: each (indices,until) set controls identical for k*dt<until.
 n=round(H/dt);t=np.arange(n+1)*dt;ns=len(phases);bs=4*n+3;EI=ns*bs;E0=EI+1;nv=E0+1
 er=[];ec=[];ev=[];eqb=[];ir=[];ic=[];iv=[];ib=[];bounds=[(None,None)]*nv
 def eq(cols,vals,rhs=0.):
  j=len(eqb);er.extend([j]*len(cols));ec.extend(cols);ev.extend(vals);eqb.append(rhs)
 def ine(cols,vals,rhs=0.):
  j=len(ib);ir.extend([j]*len(cols));ic.extend(cols);iv.extend(vals);ib.append(rhs)
 ai=np.exp(-dt);Ad=ai*np.array([[1+dt,dt],[-dt,1-dt]]);Bd=np.array([1-(1+dt)*ai,dt*ai])
 # Inner includes at most one unit derivative jump per dt; outer cell averaging.
 margin=(2+P)*(4+6/np.e)*dt*dt/8+dt/4 if inner else -P*dt*(1+2*np.exp(-2))
 for j,(high,lo,hi) in enumerate(phases):
  X=j*bs;Y=X+n+1;S=Y+n+1;U=S+n+1;mn,mx=envelope(t,lo,hi,high)
  for k in range(n+1):
   bounds[Y+k]=(mx[k]-b+margin,mn[k]+b-margin);bounds[S+k]=(0,None);ine([S+k,EI],[1,-1])
  bounds[X]=(0,0);bounds[Y]=(0,0);eq([S,E0],[1,-1])
  for k in range(n):
   bounds[U+k]=(0 if nonnegative else -P,P)
   eq([X+k+1,X+k,Y+k,U+k],[1,-Ad[0,0],-Ad[0,1],-Bd[0]])
   eq([Y+k+1,X+k,Y+k,U+k],[1,-Ad[1,0],-Ad[1,1],-Bd[1]])
   eq([S+k+1,S+k,U+k],[1,-1,dt])
 for ids,until in branches:
  kmax=min(n,int(np.ceil(until/dt-1e-9)))
  for j in ids[1:]:
   for k in range(kmax):eq([j*bs+3*(n+1)+k,ids[0]*bs+3*(n+1)+k],[1,-1])
 bounds[EI]=(0,None);bounds[E0]=(0,None);ine([E0,EI],[1,-1]);c=np.zeros(nv);c[EI]=1
 ae=coo_matrix((ev,(er,ec)),shape=(len(eqb),nv)).tocsr();au=coo_matrix((iv,(ir,ic)),shape=(len(ib),nv)).tocsr();eqb=np.array(eqb);ib=np.array(ib)
 st=time.time();r=linprog(c,A_eq=ae,b_eq=eqb,A_ub=au,b_ub=ib,bounds=bounds,method='highs',options={'primal_feasibility_tolerance':1e-8,'dual_feasibility_tolerance':1e-8})
 out=dict(name=name,phase_scenarios=ns,dt=dt,H=H,P=P,b=b,inner=inner,margin=margin,nonnegative=nonnegative,seconds=time.time()-st,success=r.success,message=r.message)
 if r.success:
  lb=np.array([-np.inf if lo is None else lo for lo,hi in bounds]);ub=np.array([np.inf if hi is None else hi for lo,hi in bounds]);lam=r.eqlin.marginals;mu=np.minimum(r.ineqlin.marginals,0);ld=np.where(np.isfinite(lb),np.maximum(r.lower.marginals,0),0);ud=np.where(np.isfinite(ub),np.minimum(r.upper.marginals,0),0)
  residual=c-ae.T@lam-au.T@mu-ld-ud;box=np.ones(nv)
  for j in range(ns):
   X=j*bs;Y=X+n+1;U=X+3*(n+1);box[X:X+n+1]=P;box[Y:Y+n+1]=2*P/np.e;box[U:U+n]=P
  dual=eqb@lam+ib@mu+lb[np.isfinite(lb)]@ld[np.isfinite(lb)]+ub[np.isfinite(ub)]@ud[np.isfinite(ub)];corr=abs(residual)@box
  out.update(E=float(r.fun),e0=float(r.x[E0]),dual_lower=float(dual-corr),dual_correction=float(corr),max_stationarity=float(max(abs(residual))),max_eq_residual=float(max(abs(r.eqlin.residual))))
  if save:np.savez_compressed(ROOT/'raw'/f'{name}.npz',t=t,phases=np.array(phases),u=np.array([r.x[j*bs+3*(n+1):j*bs+3*(n+1)+n] for j in range(ns)]),x=np.array([r.x[j*bs:j*bs+n+1] for j in range(ns)]),y_control=np.array([r.x[j*bs+n+1:j*bs+2*(n+1)] for j in range(ns)]),soc=np.array([r.x[j*bs+2*(n+1):j*bs+3*(n+1)] for j in range(ns)]),E=r.fun,e0=r.x[E0],eq_dual=lam,ineq_dual=mu,lower_dual=ld,upper_dual=ud)
 if save:(ROOT/'raw'/f'{name}.json').write_text(json.dumps(out,indent=2))
 return out
if __name__=='__main__':
 import argparse
 pa=argparse.ArgumentParser();pa.add_argument('--mode',default='pair');a=pa.parse_args()
 if a.mode=='pair':
  rs=[.2,.5,1.,2.,5.];results=[]
  for r in rs[:-1]:
   for eta in [.005,.02,.05,.1,.2]:
    tt=np.arange(0,5,.001);gap=abs(free(tt,r,True)-free(tt,5,True));ii=np.flatnonzero(gap>2*eta);until=(tt[ii[0]] if len(ii) else 5)+.05
    name=f'pair_r{r:g}_eta{eta:g}';o=build_solve(name,[(True,r,r),(True,5.,5.)],[([0,1],until)],dt=.01);o.update(eta=eta,shared_until=until,r=r);results.append(o);print(json.dumps(o),flush=True)
  (ROOT/'raw'/'pair_exploration.json').write_text(json.dumps(results,indent=2))
