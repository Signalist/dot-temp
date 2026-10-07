"""Quantifier audit, NOT a new robust solver.

One unknown theta is shared across all ports and time. Conservative switched
theta comparison uses only endpoint switches, with an exact finite lattice DP.
The analytic Lipschitz and geometric tail inequalities certify mathematical
bounds; their double-precision evaluation here is not outward-rounded.
"""
from pathlib import Path
import json,time
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments'
r=.85;lo=.55;hi=.85;N=256
rays=np.column_stack([np.linspace(0,1,41),np.linspace(1,0,41)])
ks=np.arange(N);power=r**ks
rows=[]
for ng in [257,1025,4097]:
    theta=np.linspace(lo,hi,ng);ang=theta[:,None]*ks
    co=np.cos(ang)*power;si=-np.sin(ang)*power
    c1=abs(co).sum(axis=1);c2=abs(si).sum(axis=1)
    for j,a in enumerate(rays):
        vals=abs(a[0]*co+a[1]*si).sum(axis=1)
        optional=.5*(vals+c1*a[0]+c2*a[1])
        tail=np.linalg.norm(a)*r**N/(1-r)
        err=(hi-lo)/(ng-1)/2*r/(1-r)**2*np.linalg.norm(a)+tail
        # Optional amplitude changes increase the angular Lipschitz bound.
        errvar=(hi-lo)/(ng-1)/2*r/(1-r)**2*(np.linalg.norm(a)+a.sum())/2 + r**N/(1-r)*(np.linalg.norm(a)+a.sum())/2
        rows.append({'ngrid':ng,'ray':j,'a':a.tolist(),'fixed_theta_lower':float(vals.max()),'fixed_theta_upper':float(vals.max()+err),'argmax_grid_theta':float(theta[vals.argmax()]),'dynamic_optional_lower':float(optional.max()),'dynamic_optional_upper':float(optional.max()+errvar),'port_split_lower':float(a[0]*c1.max()+a[1]*c2.max()),'port_split_upper':float(a[0]*c1.max()+a[1]*c2.max()+(hi-lo)/(ng-1)/2*r/(1-r)**2*a.sum()+r**N/(1-r)*a.sum())})
# Max cumulative reward over all 2^(N-1) endpoint switching patterns is DP on
# cumulative count. Per-path signs are independently optimized by support.
for a in rays:
    d=np.array([abs(a[0])]);dv=d.copy()
    for k in range(1,N):
        aa=k*lo+np.arange(k+1)*(hi-lo)
        p=a[0]*np.cos(aa);q=-a[1]*np.sin(aa)
        reward=r**k*abs(p+q)
        rewardv=r**k*(abs(p+q)+abs(p)+abs(q))/2
        prev=np.maximum(np.r_[d,-np.inf],np.r_[-np.inf,d])
        prevv=np.maximum(np.r_[dv,-np.inf],np.r_[-np.inf,dv])
        d=prev+reward;dv=prevv+rewardv
    row=next(x for x in rows if x['ngrid']==4097 and x['a']==a.tolist())
    row['switched_endpoint_lower']=float(d.max())
    row['switched_endpoint_dynamic_optional_lower']=float(dv.max())
    row['strict_switching_gap_detected_by_float_bounds']=bool(d.max()>row['fixed_theta_upper'])

out={'frozen':{'r':r,'theta_interval':[lo,hi],'N':N,'grid_sizes':[257,1025,4097]},'scope':'Analytic bounds evaluated in ordinary float, no global interval-rounding certificate','rows':rows}
(OUT/'SHARED_PARAMETER_RESULTS.json').write_text(json.dumps(out,indent=2))
fine=[x for x in rows if x['ngrid']==4097]
print(json.dumps({'rays':len(fine),'strict_switching_gaps':sum(x['strict_switching_gap_detected_by_float_bounds'] for x in fine),'equal_ray':fine[20]},indent=2))
