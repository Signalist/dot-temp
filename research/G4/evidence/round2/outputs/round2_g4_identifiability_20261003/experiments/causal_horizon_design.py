#!/usr/bin/env python3
"""Exact robust envelope LP: independent task order each block, no reset.
Classical reachable-interval formulation compared to fixed periodic schedules.
"""
import pathlib,json
import numpy as np
from scipy import sparse
from scipy.optimize import linprog
from recovery_frontier import paths,solve
R=pathlib.Path(__file__).resolve().parent

def design(K,N=6,L=6,H=18,ec=.95,ed=.95,tau=.5,rate=12,endpoint_mode='every',initial_fraction=None,capacity_limit=None,capacity_value=None,audit=False):
 M,b=paths(N,L,H,ec,ed)
 npow=K*N;ie=npow;ic=ie+1;il=ic+1;ih=il+K+1;nv=ih+K+1
 rows=[];cols=[];vals=[];rhs=[]
 def add(items,rr):
  i=len(rhs)
  for j,v in items.items():
   if v:rows.append(i);cols.append(j);vals.append(v)
  rhs.append(rr)
 for z in range(K):
  for j in range(N):
   # lo_next <= lo + r_j; hi_next >= hi + r_j
   add({il+z+1:1,il+z:-1,**{z*N+k:-M[j,-1,k] for k in range(N)}},b[j,-1])
   add({ih+z:1,ih+z+1:-1,**{z*N+k:M[j,-1,k] for k in range(N)}},-b[j,-1])
   for k in range(N+1):
    add({il+z:-1,**{z*N+t:-M[j,k,t] for t in range(N)}},b[j,k])
    add({ih+z:1,ic:-1,**{z*N+t:M[j,k,t] for t in range(N)}},-b[j,k])
 for z in (range(1,K+1) if endpoint_mode=='every' else [K]):
  add({ie:1,il+z:-1},tau);add({ih+z:1,ie:-1},tau)
 A=sparse.coo_matrix((vals,(rows,cols)),shape=(len(rhs),nv)).tocsr();rhs=np.array(rhs)
 neq=2+(initial_fraction is not None)
 eq=sparse.lil_matrix((neq,nv));eq[0,il]=1;eq[0,ie]=-1;eq[1,ih]=1;eq[1,ie]=-1
 if initial_fraction is not None:eq[2,ie]=1;eq[2,ic]=-initial_fraction
 eq=eq.tocsr()
 obj=np.zeros(nv);obj[ic]=1
 bounds=[(max(L,H-rate),min(H,L+rate))]*npow+[(0,None),((0,capacity_limit) if capacity_value is None else (capacity_value,capacity_value))]+[(None,None)]*(2*(K+1))
 if max(L,H-rate)>min(H,L+rate):return {'success':False,'reason':'empty rate interval'}
 res=linprog(obj,A_ub=A,b_ub=rhs,A_eq=eq,b_eq=np.zeros(neq),bounds=bounds,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
 out={'success':bool(res.success),'K':K,'N':N,'ec':ec,'ed':ed,'tau':tau,'rate':rate,'endpoint_mode':endpoint_mode,'initial_fraction':initial_fraction,'capacity_limit':capacity_limit,'capacity_value':capacity_value}
 if not res.success:return out
 p=res.x[:npow].reshape(K,N);e0=res.x[ie];C=res.x[ic]
 lo=hi=e0;states_lo=[];states_hi=[];deadlines=[];widthincrements=[];prefixes=[]
 for z in range(K):
  v=np.einsum('jkn,n->jk',M,p[z])+b
  states_lo.append(float((lo+v).min()));states_hi.append(float((hi+v).max()))
  lo+=min(v[:,-1]);hi+=max(v[:,-1]);deadlines.append([float(lo),float(hi)])
  widthincrements.append(float(np.ptp(v[:,-1])))
  prefixes.append(v.tolist())
 spread=np.ptp(p,axis=1);a=1/ed-ec
 dual=float(rhs@res.ineqlin.marginals+sum((bb[0] or 0)*yy for bb,yy in zip(bounds,res.lower.marginals))+sum((bb[1] or 0)*yy for bb,yy in zip(bounds,res.upper.marginals)))
 out.update(capacity=float(C),e0=float(e0),p=p.tolist(),block_spreads=spread.tolist(),terminal_intervals=deadlines,width_increments=widthincrements,sum_width=float(sum(widthincrements)),width_formula_residual=float(max(abs(np.array(widthincrements)-a*spread))),soc_min=min(states_lo),soc_max=max(states_hi),max_recovery_error=float(max(max(abs(x-e0) for x in pair) for pair in (deadlines if endpoint_mode=='every' else [deadlines[-1]]))),primal_residual=float(max(0,max(A@res.x-rhs))),primal_dual_gap=float(res.fun-dual),stationarity_residual=float(max(abs(obj-A.T@res.ineqlin.marginals-eq.T@res.eqlin.marginals-res.lower.marginals-res.upper.marginals))))
 if audit:return out,{"A":A,"rhs":rhs,"Aeq":eq,"beq":np.zeros(neq),"bounds":bounds,"objective":obj,"res":res}
 return out

def main():
 out={'scope':'synthetic task-order contract, common predetermined causal PCC, exact robust state intervals, no unphysical SOC resets','arbitrary_public':[],'periodic_comparison':[]}
 for eta in [.999,.99,.95,.8]:
  for K in [1,2,5,10,20,100]:
   r=design(K,ec=eta,ed=eta);out['arbitrary_public'].append(r)
   out['periodic_comparison'].append(solve(K=K,ec=eta,ed=eta,tau=.5,rate=12))
 out['endpoint_ablation']=[design(K,endpoint_mode=mode) for K in [2,5,10,20] for mode in ['every','final']]
 out['rate_ablation']=[design(10,rate=r) for r in [6,8,10,10.21,10.211,11,12]]
 ok=[r for r in out['arbitrary_public']+out['endpoint_ablation']+out['rate_ablation'] if r['success']]
 out['tests']={'all_main_solved':all(r['success'] for r in out['arbitrary_public']), 'state_bounds':all(r['soc_min']>=-1e-7 and r['soc_max']<=r['capacity']+1e-7 for r in ok),'deadlines':all(r['max_recovery_error']<=r['tau']+1e-7 for r in ok),'width_identity':all(r['width_formula_residual']<1e-8 for r in ok),'dual_gap':all(abs(r['primal_dual_gap'])<1e-7 for r in ok),'stationarity':all(r['stationarity_residual']<1e-7 for r in ok),'arbitrary_no_worse_periodic':all(a['capacity']<=b['capacity']+1e-7 for a,b in zip(out['arbitrary_public'],out['periodic_comparison']))}
 (R/'CAUSAL_HORIZON_RESULTS.json').write_text(json.dumps(out,indent=2))
 print(json.dumps({'tests':out['tests'],'eta95':[{k:r[k] for k in ['K','capacity','sum_width','max_recovery_error']} for r in out['arbitrary_public'] if r['ec']==.95],'rate':[{k:r.get(k) for k in ['rate','success','capacity']} for r in out['rate_ablation']]},indent=2))
 assert all(out['tests'].values())
if __name__=='__main__':main()
