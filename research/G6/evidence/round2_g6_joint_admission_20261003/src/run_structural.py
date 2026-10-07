from pathlib import Path
import json, itertools, time
import numpy as np
from block_admission import rotation, sign_support, all_startup_support

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments';OUT.mkdir(exist_ok=True)
cases=[('development',.85,.7),('holdout_low_memory',.6,.7),('holdout_high_memory',.95,.7),('holdout_rational',.85,np.pi/4),('holdout_irrational',.85,np.pi*(np.sqrt(5)-1)/2)]
rays=np.column_stack([np.linspace(0,1,41),np.linspace(1,0,41)])
rows=[];checks=[]
for name,r,theta in cases:
    N=256;k=np.arange(N)
    V=r**k[:,None]*np.column_stack([np.cos(k*theta),-np.sin(k*theta)])
    for ai,a in enumerate(rays):
        w=V@a;tail=np.linalg.norm(a)*r**N/(1-r)
        exact=abs(w).sum()
        vals={}
        for R in [1,2,3,None]:
            p=sign_support(w,R,True)
            vals[str(R)]={'startup_support':float(p.max()),'asymptotic_support_256':float(p[-1]),'max_startup_n':int(np.argmax(p)+1),'capacity_inner':float(1/(p.max()+tail))}
        independent=float(abs(V).sum(axis=0)@a)
        singleton=float(abs(a[0]))
        const=float(abs(np.linalg.solve(np.eye(2)-r*rotation(theta),a)[0]))
        rows.append({'case':name,'r':r,'theta':theta,'ray':ai,'a':a.tolist(),'support':exact,'tail':tail,'independent_port_support':independent,'reset_one_step_support':singleton,'constant_sign_stationary_support':const,'contracts':vals})
    # independent enumeration is a verifier, not the main mature baseline.
    for Nsmall in [4,8,12]:
        w=V[:Nsmall]@np.array([.4,.6])
        for R in [1,2,3,None]:
            vals=[]
            for ss in itertools.product([-1,1],repeat=Nsmall):
                if R is not None and any(len(list(g))>R for _,g in itertools.groupby(ss)):continue
                vals.append(np.dot(w,ss))
            e=max(vals);d=float(sign_support(w,R))
            checks.append({'case':name,'N':Nsmall,'max_run':R,'enumeration':e,'DP':d,'abs_error':abs(e-d)})
    # Both oscillator coordinates protected at block boundaries: omit e1 only trap.
    # Retain primary output exactly as frozen; this is explicitly a scope ablation.
    c=abs(V).sum(axis=0);corner=1/c
    fcorner=float(abs(V@corner).sum());rows.append({'case':name,'partial_use_corner':corner.tolist(),'corner_F':fcorner,'rectangle_float_bound_checked':bool(fcorner+np.linalg.norm(corner)*r**256/(1-r)<=1)})

# Tail series/rational closed form independently checked.
r=.85;theta=np.pi/4;P=4;a=np.array([.4,.6]);k=np.arange(256)
series=float(np.sum(r**k*abs(a[0]*np.cos(k*theta)-a[1]*np.sin(k*theta))))
k=np.arange(P);closed=float(np.sum(r**k*abs(a[0]*np.cos(k*theta)-a[1]*np.sin(k*theta)))/(1-r**P))
checks.append({'rational_identity_error':abs(series-closed)})
# Startup counterexample must not be erased by asymptotic invariant set.
w=.5**np.arange(256);p=sign_support(w,2,True)
checks.append({'startup_caveat_max':float(p.max()),'stationary':float(p[-1]),'n':int(p.argmax()+1)})
(OUT/'STRUCTURAL_RESULTS.json').write_text(json.dumps({'rows':rows,'independent_checks':checks},indent=2))
print(json.dumps({'cases':len(cases),'rays':41,'max_enumeration_error':max(x.get('abs_error',0) for x in checks),'startup_caveat':checks[-1]},indent=2))
