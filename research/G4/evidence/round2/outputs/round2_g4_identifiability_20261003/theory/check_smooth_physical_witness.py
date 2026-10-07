#!/usr/bin/env python3
"""Independent ODE/quadrature check of the smooth pair; no imports of its generator."""
from pathlib import Path
import json,math
import numpy as np
from scipy.integrate import quad, solve_ivp
HERE=Path(__file__).resolve().parent
r=.2;ec=ed=.95;L=6.;D=12.;a=D/(1+ec*ed);Q=ec*a;time_constant=.01

def pulse(s):
    if s<=0 or s>=1:return 0.,0.
    if s<r:
        return (1-math.cos(math.pi*s/r))/(2*(1-r)),math.pi*math.sin(math.pi*s/r)/(2*r*(1-r))
    if s<=1-r:return 1/(1-r),0.
    x=1-s
    return (1-math.cos(math.pi*x/r))/(2*(1-r)),-math.pi*math.sin(math.pi*x/r)/(2*r*(1-r))

def signals(t,high):
    if t>=6:return L,L,0.,0.
    slot=int(math.floor(t));h,dh=pulse(t-slot)
    active=slot in [1,2];is_high=slot==high
    load=L+(D*h if is_high else 0)
    target=L+(a*h if active else 0)
    bstar=(D if is_high else 0)*h-(a if active else 0)*h
    dbstar=(D if is_high else 0)*dh-(a if active else 0)*dh
    command=bstar+time_constant*dbstar
    return load,target,command,bstar

def main():
    area,err=quad(lambda x:pulse(x)[0],0,1,points=[r,1-r],epsabs=1e-13)
    rows=[]
    for high in [1,2]:
        def rhs(t,y):
            load,target,cmd,b=signals(t,high)
            actual=y[0]
            return [(cmd-actual)/time_constant,-actual/ed if actual>=0 else -ec*actual]
        ts=np.linspace(0,6,60001)
        breaks=sorted(set([float(k+x) for k in range(6) for x in [0,r,1-r,1]]))
        ys=np.zeros((2,len(ts)));carry=np.array([0.,9.]);success=True
        for left,right in zip(breaks[:-1],breaks[1:]):
            segment=solve_ivp(rhs,[left,right],carry,method='DOP853',rtol=2e-13,atol=1e-14,max_step=.0005,dense_output=True)
            ix=np.flatnonzero((ts>=left-1e-14)&(ts<=right+1e-14))
            ys[:,ix]=segment.sol(ts[ix]);carry=segment.y[:,-1];success=success and segment.success
        from types import SimpleNamespace
        sol=SimpleNamespace(y=ys,success=success)
        vals=np.array([signals(float(t),high) for t in ts]);pcc=vals[:,0]-sol.y[0]
        rows.append(dict(high_slot=high+1,success=sol.success,max_tracking_error=float(np.max(np.abs(sol.y[0]-vals[:,3]))),max_PCC_error=float(np.max(np.abs(pcc-vals[:,1]))),min_energy=float(sol.y[1].min()),max_energy=float(sol.y[1].max()),endpoint_error=float(abs(sol.y[1,-1]-9)),max_actual_power=float(np.max(np.abs(sol.y[0]))),max_command_sampled=float(np.max(np.abs(vals[:,2])))))
    bounds=dict(command_bound=max(a,D-a)*(1/(1-r)+time_constant*math.pi/(2*r*(1-r))),actual_power_bound=max(a,D-a)/(1-r),actual_slew_bound=max(a,D-a)*math.pi/(2*r*(1-r)),state_min=9-Q,state_max=9+Q,work_energy=6*L+D*area,pcc_energy=6*L+2*a*area,loss_energy=2*a-D)
    out=dict(scope='independent quadrature plus numerical integration of first-order PCS and lossy SOC; smooth contract is distinct from step-task capacity frontier',pulse_area=area,quadrature_error=err,bounds=bounds,worlds=rows,causal_requirement='The current task selection and its smooth shape/phase must be available locally before ramp execution; feedforward uses this current task and public PCC target. No future task order is required. This does not certify delayed/uncertain derivative sensing or a real hardware converter.',tests=dict(area_one=abs(area-1)<1e-12,command_bound=bounds['command_bound']<12,actual_slew_bound=bounds['actual_slew_bound']<75,state_bounds=bounds['state_min']>0 and bounds['state_max']<18,ode_tracking=all(x['max_tracking_error']<1e-7 for x in rows),endpoint=all(x['endpoint_error']<1e-7 for x in rows)))
    (HERE/'SMOOTH_PHYSICAL_WITNESS_AUDIT.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2));assert all(out['tests'].values())
if __name__=='__main__':main()
