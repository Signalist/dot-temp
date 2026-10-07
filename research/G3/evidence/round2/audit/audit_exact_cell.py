"""Independent LP/saturated-plant checks of exact_cell oracle.
The oracle is loaded solely as the unit under test. No oracle flow/evaluator is
used by either LP discretization or clipped-actuator ODE integration.
"""
from pathlib import Path
import sys,json
import numpy as np
from scipy.optimize import linprog
from scipy.integrate import solve_ivp
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'theory'))
from exact_cell import Actuator,cell_bounds,lift_value

def reachable_ode(b,h,p,u):
    return float(solve_ivp(lambda t,y:[np.clip((u-y[0])/p.tau,-p.r_down,p.r_up)],(0,h),[b],method='DOP853',rtol=1e-11,atol=1e-11,max_step=h/30).y[0,-1])

def lp_bound(b0,b1,h,p,N,maximize):
    dt=h/N;n=N+1
    # Piecewise linear b; both endpoint command values and exact slope bounded.
    from scipy.sparse import lil_matrix
    A=lil_matrix((6*N,n));B=np.zeros(6*N)
    for k in range(N):
        slope=np.array([-1,1])/dt
        for r,(co,rhs) in enumerate([(slope,p.r_up),(-slope,p.r_down),(p.tau*slope+[1,0],p.upper),(-p.tau*slope-[1,0],-p.lower),(p.tau*slope+[0,1],p.upper),(-p.tau*slope-[0,1],-p.lower)]):
            A[6*k+r,k:k+2]=co;B[6*k+r]=rhs
    weights=np.full(n,dt);weights[[0,-1]]/=2
    bounds=[(p.lower,p.upper)]*n;bounds[0]=(b0,b0);bounds[-1]=(b1,b1)
    res=linprog((-1 if maximize else 1)*weights,A_ub=A.tocsr(),b_ub=B,bounds=bounds,method='highs')
    return None if not res.success else float(weights@res.x)

rng=np.random.default_rng(2026100309);rows=[];max_reach_err=0.;max_outward_lp_error=0.;max_lift_violation=0.;max_lift_charge_error=0.
for j in range(24):
    p=Actuator(-450.,450.,float(rng.uniform(.002,.01)),float(rng.uniform(15000,60000)),float(rng.uniform(15000,60000)))
    h=float(rng.uniform(.0005,.010));b0=float(rng.uniform(-440,440))
    lo=reachable_ode(b0,h,p,p.lower);hi=reachable_ode(b0,h,p,p.upper)
    b1=lo+float(rng.uniform(.1,.9))*(hi-lo)
    bb=cell_bounds(b0,b1,h,p)
    max_reach_err=max(max_reach_err,abs(lo-bb['b1_min']),abs(hi-bb['b1_max']))
    r={'b0':b0,'b1':b1,'h':h,'tau':p.tau,'r_up':p.r_up,'r_down':p.r_down,'oracle_min':bb['Imin'],'oracle_max':bb['Imax'],'lp':[]}
    for N in [64,256,1024]:
        il=lp_bound(b0,b1,h,p,N,False);iu=lp_bound(b0,b1,h,p,N,True)
        r['lp'].append({'N':N,'min':il,'max':iu,'inner_min_gap':None if il is None else il-bb['Imin'],'inner_max_gap':None if iu is None else bb['Imax']-iu})
        if il is not None:max_outward_lp_error=max(max_outward_lp_error,bb['Imin']-il)
        if iu is not None:max_outward_lp_error=max(max_outward_lp_error,iu-bb['Imax'])
    # Actual oracle lift numerically differentiated and checked without internal flows.
    target=(.37*bb['Imin']+.63*bb['Imax']);ts=np.linspace(0,h,20001)
    bs=np.array([lift_value(t,b0,b1,h,target,p,bb) for t in ts]);dt=ts[1]-ts[0];ds=np.diff(bs)/dt;mid=(bs[1:]+bs[:-1])/2;us=mid+p.tau*ds
    violation=max(float(np.max(us-p.upper)),float(np.max(p.lower-us)),float(np.max(ds-p.r_up)),float(np.max(-p.r_down-ds)),0.)
    max_lift_violation=max(max_lift_violation,violation);max_lift_charge_error=max(max_lift_charge_error,abs(np.trapezoid(bs,ts)-target))
    rows.append(r)
    print(j, r['lp'][-1],flush=True)
# Exact boundary anchors and global outer cuts at both command invariant endpoints.
boundary=[];p=Actuator()
for b in [p.lower,p.upper]:
    bb=cell_bounds(b,b,.005,p);boundary.append(bb)
result={'cases':rows,'boundary_cases':boundary,'max_independent_reach_ode_error':max_reach_err,'max_LP_outward_violation':max_outward_lp_error,'max_numeric_lift_differential_violation':max_lift_violation,'max_lift_trapezoid_charge_error':max_lift_charge_error,'note':'LP is an independently constructed sufficient piecewise-linear trajectory family; extrema must lie inside exact oracle bounds and approach them as refined. Floating point tests are not a proof.'}
(ROOT/'audit/EXACT_CELL_AUDIT.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['cases','boundary_cases']}))
