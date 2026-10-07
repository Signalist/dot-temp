"""Terminal-free cell-moment relaxation of arbitrary measurable OL injection.
Cell positive/negative moments preserve exact lossy energy and include every
bounded physical waveform. Simultaneous auxiliaries are allowed ONLY as a
relaxation for a lower bound. Frequency moment error gets analytic quadrature
remainder, not an assumption that the unknown waveform was ZOH.
"""
from design_controller import *
from scipy.sparse import hstack,eye

def lower(h=.02,T=10.,high=False):
 N=round(T/h);times=np.arange(.1,T+.00001,.1);index=np.rint(times/h).astype(int);lo=np.arange(N)*h
 step=response(np.r_[lo,T]);W=np.diff(step,axis=0)/h
 nsub=12;x=lo[:,None]+h*(np.arange(nsub)+.5)[None,:]/nsub
 coef=CV*bm
 g=(np.exp(x.ravel()[:,None]*lam)@coef.T).real.reshape(N,nsub,4)
 gm=(np.exp((lo+h/2)[:,None]*lam)@(coef*lam).T).real
 g2env=np.exp(lo[:,None]*lam.real)@abs(coef*lam**2).T
 L=abs(gm)+h/2*g2env
 err=h/nsub*np.sum(abs(g-W[:,None,:]),axis=1)+L*h*h/(4*nsub)
 cumulative=np.vstack([np.zeros(4),np.cumsum(err,axis=0)])*POWER
 K=np.zeros((len(times),4,N))
 for i,m in enumerate(index):K[i,:,:m]=W[:m][::-1].T
 K=K.reshape(-1,N);eps=cumulative[index].ravel()
 phase=np.r_[.0001,np.arange(.25,5.00001,.25)]
 # x=[cell discharge integral,cell charge magnitude,E], units MWs.
 rows=[];rhs=[]
 for r in phase:
  y=loadtrace(times,r,high).ravel()
  F=csr_matrix(np.c_[-K,K,np.zeros(len(K))]);rows.extend([F,-F]);rhs.extend([.1+eps-y,.1+eps+y])
 cum=csr_matrix(np.tril(np.ones((N,N))));D=hstack([cum/ETA,-ETA*cum,csr_matrix(-np.ones((N,1)))],format='csr')
 rows.append(D);rhs.append(np.zeros(N));Dlo=hstack([-cum/ETA,ETA*cum,csr_matrix((N,1))],format='csr');rows.append(Dlo);rhs.append(np.zeros(N))
 cap=hstack([eye(N),eye(N),csr_matrix((N,1))],format='csr');rows.append(cap);rhs.append(np.full(N,POWER*h))
 mat=vstack(rows,format='csr');b=np.concatenate(rhs);cost=np.r_[np.zeros(2*N),1.]
 sol=linprog(cost,A_ub=mat,b_ub=b,bounds=[(0,None)]*(2*N+1),method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
 out={'h_s':h,'prefix_s':T,'initial_high':high,'phases_r_s':phase.tolist(),'P_MW':POWER,'eta':ETA,'band_Hz':.1,'success':bool(sol.success),'status':sol.message,'max_frequency_moment_remainder_Hz':float(max(eps)),'initial_SOC':'full E','terminal_conditions':'none','scope':'51-state exact LTI, arbitrary measurable bounded active injection, no subsequent observations; float analytic error bound and LP dual, not nonlinear impossibility'}
 if sol.success:
  dual=sol.ineqlin.marginals;stat=mat.T@dual;dualobj=b@dual;lowerdual=cost-stat
  # Negative reduced costs can be repaired with known finite cell bounds;
  # E coefficient has positive slack and needs no finite upper bound.
  repair=POWER*h*np.maximum(-lowerdual[:2*N],0).sum()
  out.update(E_lower_MWs=float(dualobj-repair),primal_E_MWs=float(sol.fun),duality_gap=float(sol.fun-dualobj),dual_positive_violation=float(max(0,np.max(dual))),stationarity_min=float(min(lowerdual)),E_reduced_cost=float(lowerdual[-1]),dual_repair_MWs=float(repair),max_primal_violation=float(max(0,np.max(mat@sol.x-b))))
  np.savez_compressed(OUT/f'openloop_lower_h{h:g}_T{T:g}_{"high" if high else "low"}.npz',x=sol.x,dual=dual,b=b,c=cost,kernel_moment=W,kernel_remainder=err,frequency_remainder=eps)
 return out

if __name__=='__main__':
 import argparse
 pa=argparse.ArgumentParser();pa.add_argument('--h',type=float,default=.02);pa.add_argument('--T',type=float,default=10.);a=pa.parse_args();z=lower(a.h,a.T,False);(OUT/f'OPENLOOP_CONTINUOUS_LOWER_h{a.h:g}_T{a.T:g}.json').write_text(json.dumps(z,indent=2));print(json.dumps(z,indent=2))
