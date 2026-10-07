"""Deterministic numerical tests of exact-cell formulas and global cuts."""
import json,sys
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from exact_cell import *
rng=np.random.default_rng(20261003)
max_integral_error=max_gradient_error=max_tangent_violation=max_lag_error=0.0
n=600
for j in range(n):
    p=Actuator(lower=-450.,upper=450.,tau=float(rng.uniform(.002,.015)),r_up=float(rng.uniform(10000,90000)),r_down=float(rng.uniform(10000,90000)))
    h=float(rng.uniform(.0002,.015)); b0=float(rng.uniform(-445,445)); r=reachability(b0,h,p)
    # Include endpoint-reachability boundaries as supporting-cut anchors.
    frac=float(rng.uniform(.05,.95)) if j%5 else (j%2)
    b1=r['b1_min']+(r['b1_max']-r['b1_min'])*frac
    out=cell_bounds(b0,b1,h,p)
    for label in ['min','max']:
        s=out['switch_'+label]
        numerical=quad(lambda t:extreme_value(t,b0,b1,h,p,label),0,h,points=[s],epsabs=1e-11,epsrel=1e-11,limit=150)[0]
        max_integral_error=max(max_integral_error,abs(numerical-out['I'+label]))
    # Centered finite differences only when endpoint pairs stay interior.
    if .02<frac<.98:
        step=1e-3
        for axis in [0,1]:
            args=[b0,b1]; args[axis]+=step; pp=cell_bounds(*args,h,p)
            args=[b0,b1]; args[axis]-=step; mm=cell_bounds(*args,h,p)
            if pp['reachable'] and mm['reachable']:
                for label in ['min','max']:
                    fd=(pp['I'+label]-mm['I'+label])/(2*step)
                    max_gradient_error=max(max_gradient_error,abs(fd-out['grad_'+label][axis]))
    # Test global supporting hyperplanes on independent reachable pairs.
    for z in range(20):
        y0=float(rng.uniform(-450,450)); yr=reachability(y0,h,p)
        y1=float(rng.uniform(yr['b1_min'],yr['b1_max'])); yy=cell_bounds(y0,y1,h,p)
        d=np.array([y0-b0,y1-b1])
        max_tangent_violation=max(max_tangent_violation,
            yy['Imax']-out['Imax']-np.dot(out['grad_max'],d),
            out['Imin']+np.dot(out['grad_min'],d)-yy['Imin'],
            yy['b1_max']-out['b1_max']-out['grad_b1_max']*(y0-b0),
            out['b1_min']+out['grad_b1_min']*(y0-b0)-yy['b1_min'])
    # Uncapped-ramp case recovers exact logarithmic formula.
    pl=Actuator(p.lower,p.upper,p.tau,1e12,1e12); rr=reachability(b0,h,pl)
    b1l=float(rng.uniform(rr['b1_min'],rr['b1_max'])); oo=cell_bounds(b0,b1l,h,pl)
    ll,uu=pure_lag_bounds(b0,b1l,h,pl.lower,pl.upper,pl.tau)
    max_lag_error=max(max_lag_error,abs(ll-oo['Imin']),abs(uu-oo['Imax']))
# Simple sharpness witnesses.
p=Actuator(-1,1,1,1,1); exact=cell_bounds(0,0,1,p)
result={
 'seed':20261003,'random_cases':n,'global_tangent_checks':20*n*4,
 'max_integral_absolute_error':max_integral_error,
 'max_gradient_absolute_error':max_gradient_error,
 'max_global_tangent_violation':max_tangent_violation,
 'max_pure_lag_closed_form_error':max_lag_error,
 'cheap_outer_false_positive':{'b0':0,'b1':0,'h':1,'charge':.245,'sharp_ramp_only_upper':.25,'exact_lag_upper':exact['Imax']},
 'sharp_chord_constant':{'h':1,'ramp':1,'C_t':'t*(t-1)/2','node_C':[0,0],'midpoint_C':-.125,'bound':.125},
 'all_checks_pass':bool(max_integral_error<2e-7 and max_gradient_error<2e-7 and max_tangent_violation<2e-8 and max_lag_error<2e-8),
 'warning':'Floating point numerical checks, not interval arithmetic or a proof.'}
Path(__file__).with_name('exact_cell_tests.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
assert result['all_checks_pass']
