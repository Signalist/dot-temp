#!/usr/bin/env python3
"""Independent physical/combinatorial checks. Reads primary experiment artifacts, never rewrites them.
No source import, no use of the primary scenario matrix builder or optimization code.
"""
from pathlib import Path
import itertools, json, math, hashlib
import numpy as np
from scipy.optimize import linprog, brentq
from scipy import sparse

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
rng=np.random.default_rng(20261003)

def phi(u,ec,ed):
    u=np.asarray(u,dtype=float)
    return np.where(u>=0,ec*u,u/ed)

def physical_paths(p,N,L,H,ec,ed):
    p=np.asarray(p)
    ds=np.full((N,N),L,dtype=float)
    np.fill_diagonal(ds,H)
    inc=phi(p[None,:]-ds,ec,ed)
    return np.column_stack([np.zeros(N),np.cumsum(inc,axis=1)])

def corridor_recur(a,b,l,u):
    if np.any(a>b) or np.any(l>u): return False
    lo,hi=a[0],b[0]
    for t in range(len(l)):
        lo=max(a[t+1],lo+l[t]);hi=min(b[t+1],hi+u[t])
        if lo>hi+1e-10:return False
    return True

def corridor_pairs(a,b,l,u):
    if np.any(a>b) or np.any(l>u):return False
    for s in range(len(a)):
        for t in range(s+1,len(a)):
            if a[t]>b[s]+sum(u[s:t])+1e-10:return False
            if a[s]+sum(l[s:t])>b[t]+1e-10:return False
    return True

def corridor_lp(a,b,l,u):
    n=len(a);A=[];rhs=[]
    if np.any(a>b) or np.any(l>u):return False
    for t in range(n-1):
        r=np.zeros(n);r[t+1]=1;r[t]=-1
        A.extend([r,-r]);rhs.extend([u[t],-l[t]])
    ans=linprog(np.zeros(n),A_ub=np.array(A),b_ub=np.array(rhs),bounds=list(zip(a,b)),method='highs-ds')
    return ans.success

def check_corridors():
    cases=[];yes=0
    for z in range(1000):
        T=int(rng.integers(1,13))
        center=rng.uniform(-5,5,T+1);half=rng.uniform(0,4,T+1)
        a=center-half;b=center+half;a[0]=b[0]=0
        lc=rng.uniform(-2,2,T);lh=rng.uniform(0,3,T)
        l=lc-lh;u=lc+lh
        # Include many feasible cases and exact singleton recovery corridors.
        if z%3==0:
            path=np.r_[0,np.cumsum(rng.uniform(-1,1,T))]
            a=np.minimum(a,path);b=np.maximum(b,path)
            l=np.minimum(l,np.diff(path));u=np.maximum(u,np.diff(path))
        if z%7==0:
            k=int(rng.integers(1,T+1));a[k]=b[k]=(a[k]+b[k])/2
        rr=corridor_recur(a,b,l,u);pp=corridor_pairs(a,b,l,u);ll=corridor_lp(a,b,l,u)
        if not rr==pp==ll:
            cases.append(dict(case=z,recur=rr,pairs=pp,lp=ll,a=a.tolist(),b=b.tolist(),l=l.tolist(),u=u.tolist()))
        yes+=rr
    return dict(cases=1000,feasible=yes,mismatches=cases)

def audit_schedule(p,e0,C,ec,ed,tau,N=6,L=6,H=18,enumerate_histories=False):
    p=np.asarray(p,float);K=len(p)
    lo=hi=e0;globalmin=globalmax=e0;maxerr=0.;sumwidth=0.;minrecord=None;maxrecord=None
    min_orders=[];max_orders=[];allstates=np.array([e0]);enum_min=enum_max=e0;enum_err=0.
    for ell in range(K):
        g=physical_paths(p[ell],N,L,H,ec,ed);r=g[:,-1]
        imin=np.unravel_index(np.argmin(g),g.shape);imax=np.unravel_index(np.argmax(g),g.shape)
        mn=lo+g[imin];mx=hi+g[imax]
        if mn<globalmin:
            globalmin=float(mn);minrecord=(min_orders.copy()+[int(imin[0])],int(imin[1]),float(mn))
        if mx>globalmax:
            globalmax=float(mx);maxrecord=(max_orders.copy()+[int(imax[0])],int(imax[1]),float(mx))
        lo+=min(r);hi+=max(r);maxerr=max(maxerr,abs(lo-e0),abs(hi-e0));sumwidth+=np.ptp(r)
        min_orders.append(int(np.argmin(r)));max_orders.append(int(np.argmax(r)))
        if enumerate_histories:
            expanded=allstates[:,None,None]+g[None,:,:]
            enum_min=min(enum_min,float(expanded.min()));enum_max=max(enum_max,float(expanded.max()))
            allstates=expanded[:,:,-1].reshape(-1)
            enum_err=max(enum_err,float(np.max(np.abs(allstates-e0))))
    # Realize both purported extremal histories by actual sequential state updates.
    witness_errors=[]
    for rec in [minrecord,maxrecord]:
        if rec is None:continue
        orders,k,target=rec;e=e0
        for ell,j in enumerate(orders):
            d=np.full(N,L,dtype=float);d[j]=H
            upto=k if ell==len(orders)-1 else N
            for t in range(upto):e+=float(phi(p[ell,t]-d[t],ec,ed))
        witness_errors.append(abs(e-target))
    out=dict(K=K,state_min=globalmin,state_max=globalmax,max_checkpoint_error=maxerr,sum_endpoint_width=sumwidth,
             max_witness_error=max(witness_errors,default=0),capacity_violation=max(0,-globalmin,globalmax-C),
             recovery_violation=max(0,maxerr-tau),width_vs_spread_error=abs(sumwidth-(1/ed-ec)*np.ptp(p,axis=1).sum()))
    if enumerate_histories:
        out.update(enumerated_histories=int(N**K),enumeration_error=max(abs(globalmin-enum_min),abs(globalmax-enum_max),abs(maxerr-enum_err)))
    return out

def full_history_lp(K,ec=.95,ed=.95,tau=.5,N=6,L=6,H=18,periodic=False):
    """No envelope variables: enumerate complete order histories and every prefix."""
    npow=N if periodic else K*N;ie=npow;ic=ie+1;nv=ic+1
    rows=[];cols=[];vals=[];rhs=[]
    def add(coef,b):
        ii=len(rhs)
        for j,v in coef.items():
            if v:rows.append(ii);cols.append(j);vals.append(v)
        rhs.append(b)
    for orders in itertools.product(range(N),repeat=K):
        coeff={};constant=0.
        add({ie:-1},0);add({ie:1,ic:-1},0)
        for ell,j in enumerate(orders):
            for t in range(N):
                idx=t if periodic else ell*N+t
                slope=1/ed if t==j else ec
                d=H if t==j else L
                coeff[idx]=coeff.get(idx,0)+slope;constant-=slope*d
                add({**{i:-v for i,v in coeff.items()},ie:-1},constant)
                add({**coeff,ie:1,ic:-1},-constant)
            add(coeff.copy(),tau-constant)
            add({i:-v for i,v in coeff.items()},tau+constant)
    A=sparse.coo_matrix((vals,(rows,cols)),shape=(len(rhs),nv)).tocsr()
    obj=np.zeros(nv);obj[ic]=1
    ans=linprog(obj,A_ub=A,b_ub=rhs,bounds=[(L,H)]*npow+[(0,None),(0,None)],method='highs-ds',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
    return dict(K=K,periodic=periodic,complete_histories=N**K,inequalities=len(rhs),success=bool(ans.success),capacity=float(ans.fun) if ans.success else None)

def check_rearrangement():
    worst=0.;totalper=0
    for k in range(100):
        N=int(rng.integers(2,8));d=rng.integers(1,15,N).astype(float);p=rng.uniform(-3,18,N)
        ec=float(rng.uniform(.5,1));ed=float(rng.uniform(.5,1))
        perm=list(set(itertools.permutations(d)));v=np.array([phi(p-np.array(x),ec,ed).sum() for x in perm]);totalper+=len(perm)
        ps=np.sort(p);ds=np.sort(d)
        high=phi(ps-ds,ec,ed).sum();low=phi(ps-ds[::-1],ec,ed).sum()
        worst=max(worst,abs(max(v)-high),abs(min(v)-low))
    return dict(cases=100,total_assignments=totalper,max_error=worst)

def check_exact_capacity():
    records=[]
    for d in [[6,6,6,6,6,18],[1,2],[2,3,4,8],[1,1,2,2,6],[3,4,7,8,9,11]]:
        ec=.95;ed=.9;q=brentq(lambda q:phi(q-np.array(d),ec,ed).sum(),min(d),max(d),xtol=1e-13)
        g=phi(q-np.array(d),ec,ed);Q=float(np.maximum(g,0).sum());ps=list(set(itertools.permutations(d)))
        traces=np.array([np.r_[0,np.cumsum(phi(q-np.array(x),ec,ed))] for x in ps])
        records.append(dict(d=d,q=q,Q=Q,range=float(np.ptp(traces)),capacity_error=abs(np.ptp(traces)-2*Q),endpoint_error=float(np.max(np.abs(traces[:,-1])))))
    return records

def periodic_algebra(p,ec,ed,K):
    p=np.asarray(p);v=ec*(p-6);V=12/ed;lam=1/(ec*ed)-1;A=v.sum();r=A-V+lam*v
    Gmax=A-v[-1];Gmin=min(np.r_[0,np.cumsum(v)[:-1]]+(1+lam)*v)-V
    low=Gmin+(K-1)*min(0,min(r));high=Gmax+(K-1)*max(0,max(r))
    return high-low

def main():
    out={'seed':20261003,'scope':'independent theory audit; no primary scenario-builder imports or rewrites'}
    out['source_sha256']={name:hashlib.sha256((ROOT/'experiments'/name).read_bytes()).hexdigest() for name in ['RECOVERY_FRONTIER_RESULTS.json','CAUSAL_HORIZON_RESULTS.json']}
    out['corridors']=check_corridors();out['rearrangement']=check_rearrangement();out['exact_capacity']=check_exact_capacity()
    fixed=json.loads((ROOT/'experiments/RECOVERY_FRONTIER_RESULTS.json').read_text())
    horizon=json.loads((ROOT/'experiments/CAUSAL_HORIZON_RESULTS.json').read_text())
    audits=[];algebra=[]
    for cat in ['frontier','multiblock']:
        for r in fixed[cat]:
            if not r['success']:continue
            K=r['blocks'];p=np.tile(r['p'],(K,1))
            a=audit_schedule(p,r['e0'],r['capacity'],r['eta_c'],r['eta_d'],r['tau'],enumerate_histories=K<=5)
            a.update(category=cat,ec=r['eta_c'],ed=r['eta_d'],reported_capacity=r['capacity']);audits.append(a)
            algebra.append(abs(periodic_algebra(r['p'],r['eta_c'],r['eta_d'],K)-r['capacity']))
    for r in horizon['arbitrary_public']:
        a=audit_schedule(r['p'],r['e0'],r['capacity'],r['ec'],r['ed'],r['tau'],enumerate_histories=r['K']<=5)
        a.update(category='arbitrary_public',ec=r['ec'],ed=r['ed'],reported_capacity=r['capacity']);audits.append(a)
    out['physical_audits']=audits;out['max_periodic_closed_form_capacity_error']=max(algebra)
    comparisons=[]
    for K in [1,2,3]:
        for periodic in [False,True]:
            r=full_history_lp(K,periodic=periodic)
            # K=3 is an independent additional point; source files contain K=1,2.
            source=(fixed['multiblock'] if periodic else horizon['arbitrary_public'])
            matches=[s for s in source if s.get('blocks',s.get('K'))==K and s.get('eta_c',s.get('ec'))==.95 and s.get('eta_d',s.get('ed'))==.95]
            if matches:r['reported_capacity_error']=abs(r['capacity']-matches[0]['capacity'])
            comparisons.append(r)
    out['full_history_optimization']=comparisons
    # Sharp budget witness and continuous within-slot range-constrained witness.
    ec=ed=.95;N=6;L=6;H=18;tau=.5;K=5;kappa=1/ed-ec
    q=(H+ec*ed*(N-1)*L)/(1+ec*ed*(N-1));s=tau/(K*kappa)
    p=np.tile([q+s,q-s,q,q,q,q],(K,1));w=audit_schedule(p,50,100,ec,ed,tau,enumerate_histories=True)
    out['sharp_budget_witness']=dict(q=q,s=s,spread_sum=float(np.ptp(p,axis=1).sum()),bound=2*tau/kappa,**w)
    qpair=(H+ec*ed*L)/(1+ec*ed);pairp=np.array([L,qpair,qpair,L,L,L]);pp=physical_paths(pairp,N,L,H,ec,ed)[[1,2]]
    out['persistent_pairwise_witness']=dict(q_pair=qpair,Q_pair=ec*(qpair-L),state_min=float(9+pp.min()),state_max=float(9+pp.max()),endpoint_error=float(np.max(np.abs(pp[:,-1]))),peak_converter_power=float(max(qpair-L,H-qpair)))
    intra=[]
    for high in range(N):
        energy=0.;trace=[0.]
        for t in range(N):
            d=H if t==high else L
            for power in [q+.5,q-.5,q+.25,q-.25]:
                energy+=.25*float(phi(power-d,ec,ed));trace.append(energy)
        intra.append(trace)
    Q=(N-1)*ec*(q-L);arr=np.array(intra)
    out['intraslot_witness']=dict(Q=Q,relative_min=float(arr.min()),relative_max=float(arr.max()),capacity_excess=max(0,float(np.max(np.abs(arr)))-Q),endpoint_error=float(np.max(np.abs(arr[:,-1]))))
    out['tests']={
        'corridor_1000_exact_agreements':not out['corridors']['mismatches'],
        'rearrangement_100_exhaustive_cases':out['rearrangement']['max_error']<1e-9,
        'sharp_exact_capacity':all(r['capacity_error']<1e-9 and r['endpoint_error']<1e-9 for r in out['exact_capacity']),
        'all_saved_schedules_direct_physics_feasible':all(r['capacity_violation']<1e-7 and r['recovery_violation']<1e-7 for r in audits),
        'all_extreme_histories_physically_realized':all(r['max_witness_error']<1e-8 for r in audits),
        'all_short_horizons_fully_enumerated':all(r.get('enumeration_error',0)<1e-8 for r in audits),
        'one_high_width_identity':all(r['width_vs_spread_error']<1e-8 for r in audits),
        'periodic_independent_closed_form':max(algebra)<1e-7,
        'full_history_LP_matches_compressed':all(r['success'] and r.get('reported_capacity_error',0)<1e-7 for r in comparisons),
        'sharp_positive_tolerance_budget':abs(w['sum_endpoint_width']-2*tau)<1e-8 and abs(w['max_checkpoint_error']-tau)<1e-8,
        'persistent_pairwise_counterexample':out['persistent_pairwise_witness']['state_min']>0 and out['persistent_pairwise_witness']['state_max']<18 and out['persistent_pairwise_witness']['endpoint_error']<1e-9,
        'intraslot_extension':out['intraslot_witness']['capacity_excess']<1e-9 and out['intraslot_witness']['endpoint_error']<1e-9,
    }
    (HERE/'INDEPENDENT_THEORY_CHECKS.json').write_text(json.dumps(out,indent=2,default=lambda x:x.item()))
    print(json.dumps({'tests':out['tests'],'full_history_optimization':comparisons,'corridors':out['corridors'],'rearrangement':out['rearrangement'],'max_periodic_algebra_error':max(algebra),'pairwise':out['persistent_pairwise_witness']},indent=2,default=lambda x:x.item()))
    assert all(out['tests'].values())
if __name__=='__main__':main()
