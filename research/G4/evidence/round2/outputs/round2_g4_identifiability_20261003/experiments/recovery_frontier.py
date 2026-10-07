#!/usr/bin/env python3
"""Frozen synthetic task-contract LP. Classical robust LP, not new estimator.
Energy is propagated, never numerically reset. All writes local G4 output only.
"""
import json,itertools,math,pathlib
import numpy as np
from scipy.optimize import linprog, brentq
R=pathlib.Path(__file__).resolve().parent

def paths(N,L,H,ec,ed):
    # e_k-e0 = M_jk @ p + b_jk; one high task at slot j.
    M=np.zeros((N,N+1,N)); b=np.zeros((N,N+1))
    for j in range(N):
        a=np.full(N,ec); a[j]=1/ed
        c=np.full(N,-ec*L); c[j]=-H/ed
        for k in range(1,N+1):
            M[j,k,:k]=a[:k]; b[j,k]=sum(c[:k])
    return M,b

def solve(N=6,L=6,H=18,ec=1,ed=1,tau=0,K=1,rate=None,cap=None):
    M,b=paths(N,L,H,ec,ed); nv=N+2; ie=N; iC=N+1
    A=[];rhs=[]
    # All past block choices have extrema achieved by repeating one order.
    # Considering m=0 and m=K-1 suffices because each expression affine in m.
    for m in sorted(set([0,K-1])):
      for jp in range(N):
       for j in range(N):
        for k in range(N+1):
         row=np.zeros(nv);row[:N]=m*M[jp,-1]+M[j,k];row[ie]=1
         cons=m*b[jp,-1]+b[j,k]
         A.append(-row);rhs.append(cons)
         row2=row.copy();row2[iC]-=1;A.append(row2);rhs.append(-cons)
    # |SOC_deadline-E0|<=tau for every of K deadlines and every history.
    for j in range(N):
      row=np.zeros(nv);row[:N]=K*M[j,-1]
      A.append(row);rhs.append(tau-K*b[j,-1])
      A.append(-row);rhs.append(tau+K*b[j,-1])
    obj=np.zeros(nv);obj[iC]=1
    low,high=L,H
    if rate is not None: low=max(low,H-rate);high=min(high,L+rate)
    if low>high:return {'success':False,'status':'rate_interval_empty'}
    bounds=[(low,high)]*N+[(0,None),(0,cap)]
    A=np.array(A);rhs=np.array(rhs)
    res=linprog(obj,A_ub=A,b_ub=rhs,bounds=bounds,method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
    out={'success':bool(res.success),'solver_status':int(res.status),'tau':tau,'blocks':K,'eta_c':ec,'eta_d':ed,'rate':rate,'capacity_limit':cap}
    if not res.success:return out
    p=res.x[:N];e0=res.x[ie];C=res.x[iC]
    v=np.einsum('jkn,n->jk',M,p)+b
    out.update(capacity=float(C),e0=float(e0),p=p.tolist(),p_spread=float(np.ptp(p)),terminal_errors=v[:,-1].tolist(),one_block_relative_paths=v.tolist(),worst_primal_violation=float(max(0,np.max(A@res.x-rhs))),dual_objective=float(rhs@res.ineqlin.marginals+sum((bb[0] or 0)*yy for bb,yy in zip(bounds,res.lower.marginals))+sum((bb[1] or 0)*yy for bb,yy in zip(bounds,res.upper.marginals))),objective=float(res.fun))
    out['primal_dual_gap']=out['objective']-out['dual_objective']
    # Independently recompute all adversarial worst-prefix energy values.
    vals=[]
    for m in range(K):
      for jp in range(N):
       for j in range(N): vals.extend((e0+m*v[jp,-1]+v[j]).tolist())
    out['independent_state_min']=min(vals);out['independent_state_max']=max(vals)
    out['max_all_deadline_error']=float(K*max(abs(v[:,-1])))
    return out

def flat(N,L,H,ec,ed):
    rho=ec*ed;q=(H+(N-1)*rho*L)/(1+(N-1)*rho)
    Q=(N-1)*ec*(q-L)
    return {'q':q,'capacity':2*Q,'e0':Q,'total_task_energy':(N-1)*L+H,'grid_energy':N*q,'loss_energy':N*q-((N-1)*L+H)}

def universal_envelope(d):
    ds=np.sort(d); lo=np.r_[0,np.cumsum(ds)];up=np.r_[0,np.cumsum(ds[::-1])]
    C=max(up-lo);z=(up+lo)/2;p=np.diff(z);E0=C/2
    per=list(set(itertools.permutations(d)));states=np.array([E0+z-np.r_[0,np.cumsum(x)] for x in per])
    mean=np.mean(d);dev=np.array([np.r_[0,np.cumsum(mean-np.array(x))] for x in per]);flatC=float(dev.max()-dev.min())
    return {'task_powers':list(d),'unique_orders':len(per),'capacity':float(C),'e0':float(E0),'p':p.tolist(),'state_min':float(states.min()),'state_max':float(states.max()),'terminal_residual':float(max(abs(states[:,-1]-E0))),'flat_capacity':flatC,'capacity_reduction_fraction':float(1-C/flatC)}

def main():
    etas=[(1,1),(.999,.999),(.99,.99),(.95,.95),(.9,.95),(.8,.8)]
    taus=[0,.01,.05,.1,.25,.5,1,2]
    rows=[]
    for ec,ed in etas:
      for tau in taus:rows.append(solve(ec=ec,ed=ed,tau=tau))
    multi=[solve(ec=.95,ed=.95,tau=.5,K=K) for K in [1,2,5,10,20,100]]
    rate=[solve(ec=.95,ed=.95,rate=r) for r in [5,6,8,10,10.21,10.211,11,12]]
    env=[universal_envelope(d) for d in [[6,6,6,10,10,10],[6,7,7,8,12,14],[6,6,6,6,6,18],[6,7,8,9,10,11,12,13]]]
    exact=[dict(eta_c=ec,eta_d=ed,**flat(6,6,18,ec,ed)) for ec,ed in etas]
    ideal_p=np.array([12,6,6,6,6,12]);M,b=paths(6,6,18,.95,.95);v=np.einsum('jkn,n->jk',M,ideal_p)+b
    # Show physical failure under repeated orders; no state reset.
    repeats=[]
    for j in range(6):
      tr=np.concatenate([6+m*v[j,-1]+v[j,:-1] for m in range(100)]+[[6+100*v[j,-1]]])
      bad=np.flatnonzero((tr < -1e-9)|(tr>12+1e-9));repeats.append({'high_task_slot':j,'terminal_drift_per_block':float(v[j,-1]),'first_capacity_violation_sample':int(bad[0]) if len(bad) else None,'after_100_blocks':float(tr[-1])})
    out={'scope':'synthetic universal deterministic task-order hiding, declared affine-region model; exact LP baseline','frontier':rows,'multiblock':multi,'rate':rate,'ideal_envelope':env,'flat_formula':exact,'unrecovered_ideal_schedule_in_lossy_storage':repeats,'tests':{}}
    checks={
      'all_48_frontier_LPs_solved':all(r['success'] for r in rows),
      'all_primal_feasible':all(r['worst_primal_violation']<1e-7 for r in rows+multi),
      'all_dual_gaps_small':all(abs(r['primal_dual_gap'])<1e-7 for r in rows+multi),
      'lossy_exact_flat_formula':all(abs(next(r for r in rows if r['eta_c']==ec and r['eta_d']==ed and r['tau']==0)['capacity']-flat(6,6,18,ec,ed)['capacity'])<1e-7 for ec,ed in etas[1:]),
      'lossy_exact_spread_zero':all(r['p_spread']<1e-7 for r in rows if r['tau']==0 and r['eta_c']*r['eta_d']<1),
      'ideal_envelope_sharp_example':abs(rows[0]['capacity']-12)<1e-7,
      'independent_states_feasible':all(r['independent_state_min']>-1e-7 and r['independent_state_max']<r['capacity']+1e-7 for r in rows+multi),
      'multiblock_tolerance_valid':all(r['max_all_deadline_error']<=.5+1e-7 for r in multi),
      'envelopes_complete_task_and_recover':all(r['terminal_residual']<1e-9 and r['state_min']>=-1e-9 and r['state_max']<=r['capacity']+1e-9 for r in env)
    }
    out['tests']=checks
    (R/'RECOVERY_FRONTIER_RESULTS.json').write_text(json.dumps(out,indent=2))
    print(json.dumps({'tests':checks,'exact':[(r['eta_c'],r['eta_d'],r['capacity'],r['p_spread']) for r in rows if r['tau']==0],'multi':[(r['blocks'],r['capacity'],r['p_spread']) for r in multi]},indent=2))
    assert all(checks.values())
if __name__=='__main__':main()
