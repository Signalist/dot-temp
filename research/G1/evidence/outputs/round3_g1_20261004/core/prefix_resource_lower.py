"""Two information-class outer LP with exact continuum phase envelopes on [0,5].
Continuous-control cell-average relaxation; corrected floating dual, not interval arithmetic.
"""
from research_lp import *
def solve(dt=.002,name=None):
 name=name or f'continuum_prefix_dt{dt:g}';P=.5;n=round(5/dt);t=np.arange(n+1)*dt;bs=4*n+3;EI=2*bs;E0=EI+1;nv=E0+1
 a=np.exp(-dt);Ad=a*np.array([[1+dt,dt],[-dt,1-dt]]);Bd=np.array([1-(1+dt)*a,dt*a]);dy=P*dt*(1+2*np.exp(-2))
 er=[];ec=[];ev=[];eb=[];ir=[];ic=[];iv=[];ib=[];bd=[(None,None)]*nv
 def eq(cols,vals,b=0):
  j=len(eb);er.extend([j]*len(cols));ec.extend(cols);ev.extend(vals);eb.append(b)
 def ine(cols,vals,b=0):
  j=len(ib);ir.extend([j]*len(cols));ic.extend(cols);iv.extend(vals);ib.append(b)
 for j,high in enumerate([True,False]):
  X=j*bs;Y=X+n+1;S=Y+n+1;U=S+n+1;base=(2 if high else 1)*g(t);peak=g(np.minimum(t,1));mn=base-peak if high else base;mx=base if high else base+peak
  for k in range(n+1):bd[Y+k]=(mx[k]-.6-dy,mn[k]+.6+dy);bd[S+k]=(0,None);ine([S+k,EI],[1,-1])
  bd[X]=(0,0);bd[Y]=(0,0);eq([S,E0],[1,-1])
  for k in range(n):
   bd[U+k]=(-P,P);eq([X+k+1,X+k,Y+k,U+k],[1,-Ad[0,0],-Ad[0,1],-Bd[0]]);eq([Y+k+1,X+k,Y+k,U+k],[1,-Ad[1,0],-Ad[1,1],-Bd[1]]);eq([S+k+1,S+k,U+k],[1,-1,dt])
 bd[EI]=(0,None);bd[E0]=(0,None);ine([E0,EI],[1,-1]);c=np.zeros(nv);c[EI]=1
 ae=coo_matrix((ev,(er,ec)),shape=(len(eb),nv)).tocsr();au=coo_matrix((iv,(ir,ic)),shape=(len(ib),nv)).tocsr();eb=np.array(eb);ib=np.array(ib)
 st=time.time();r=linprog(c,A_eq=ae,b_eq=eb,A_ub=au,b_ub=ib,bounds=bd,method='highs');assert r.success,r.message
 lb=np.array([-np.inf if l is None else l for l,u in bd]);ub=np.array([np.inf if u is None else u for l,u in bd]);lam=r.eqlin.marginals;mu=np.minimum(r.ineqlin.marginals,0);ld=np.where(np.isfinite(lb),np.maximum(r.lower.marginals,0),0);ud=np.where(np.isfinite(ub),np.minimum(r.upper.marginals,0),0)
 res=c-ae.T@lam-au.T@mu-ld-ud;box=np.ones(nv)
 for j in range(2):
  X=j*bs;Y=X+n+1;U=X+3*(n+1);box[X:X+n+1]=P;box[Y:Y+n+1]=2*P/np.e;box[U:U+n]=P
 dual=eb@lam+ib@mu+lb[np.isfinite(lb)]@ld[np.isfinite(lb)]+ub[np.isfinite(ub)]@ud[np.isfinite(ub)];corr=abs(res)@box
 out=dict(name=name,P=P,H=5,dt=dt,energy_lower=float(dual-corr),e0=float(r.x[E0]),objective=float(r.fun),correction=float(corr),stationarity_max=float(max(abs(res))),seconds=time.time()-st,phase_envelope='analytic continuum: p0*g(t)+sign*[0,g(min(t,1))]',arithmetic='ordinary floating LP coefficients and corrected dual; not formal interval certificate',terminal='none',applies_to=['initial-class only no subsequent observations','frequency-only bounded noise eta>=1/(2e), even continuous sampling'])
 np.savez_compressed(ROOT/'raw'/f'{name}.npz',solution=r.x,eq_dual=lam,ineq_dual=mu,lower_dual=ld,upper_dual=ud,t=t)
 (ROOT/'raw'/f'{name}.json').write_text(json.dumps(out,indent=2));return out
if __name__=='__main__':
 for d in [.004,.002,.001]:print(json.dumps(solve(d)),flush=True)
