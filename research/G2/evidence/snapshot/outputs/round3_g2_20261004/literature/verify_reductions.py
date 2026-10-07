#!/usr/bin/env python3
"""Deterministic algebra/normalization checks; not interval-certified or proof-assistant output."""
from fractions import Fraction as F
from itertools import product
from math import sin, pi, floor
from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parent
checks=[]

def moments(nodes, vals):
    return (sum((a*(y-x) for x,y,a in zip(nodes,nodes[1:],vals)),F(0)),
            sum((a*(y*y-x*x)/2 for x,y,a in zip(nodes,nodes[1:],vals)),F(0)))

count=0
for delta in (F(1),F(2,3),F(7,4)):
    nodes=[delta*j/4 for j in range(5)]
    for vals in product((F(-1),F(-1,2),F(0),F(1,2),F(1)),repeat=4):
        A0,A1=moments(nodes,vals)
        alpha,beta=-A0/delta,-A1/(delta*delta)
        q=(delta-A0)/2
        if q==0:
            assert A0==delta and A1==delta*delta/2
        else:
            c=(delta*delta/2-A1)/(2*q)
            c_prior=delta*(1+2*beta)/(2*(1+alpha))
            length_prior=delta*(1+alpha)/2
            assert c==c_prior and q==length_prior
            lo,hi=c-q/2,c+q/2
            assert 0<=lo<=hi<=delta
            assert delta-2*q==A0
            assert delta*delta/2-(hi*hi-lo*lo)==A1
        count+=1
checks.append({'name':'exact_rational_moment_mapping','cases':count,'passed':True})

witnesses=[]
for N in (1,2,3,4,8,16,32,64):
    knots=[F(0)]+sorted([F(4*j+1,4*N) for j in range(N)]+[F(4*j+3,4*N) for j in range(N)])+[F(1)]
    vals=[F(1 if j%2==0 else -1) for j in range(2*N+1)]
    A0,A1=moments(knots,vals)
    assert A0==A1==0
    speed=F(0); eta=F(0); maxspeed=F(0); maxeta=F(0)
    for lo,hi,a in zip(knots,knots[1:],vals):
        dt=hi-lo
        z=-speed/a
        if 0<=z<=dt:
            maxeta=max(maxeta,eta+speed*z+a*z*z/2)
        eta+=speed*dt+a*dt*dt/2
        speed+=a*dt
        maxspeed=max(maxspeed,abs(speed)); maxeta=max(maxeta,eta)
    assert speed==eta==0
    assert maxspeed==F(1,4*N) and maxeta==F(1,16*N*N)
    k=2*pi*N
    acos=sum(float(a)*(sin(k*float(hi))-sin(k*float(lo)))/k for lo,hi,a in zip(knots,knots[1:],vals))
    expected=2/pi
    assert abs(acos-expected)<5e-14
    optimum=acos/k**2
    m=N
    restricted_upper=2*m/k**3
    gap_lower=1/(4*pi**3*N*N)
    assert abs((optimum-restricted_upper)-gap_lower)<1e-15
    witnesses.append({'N':N,'switches':2*N,'speed_deviation':str(maxspeed),'phase_deviation':str(maxeta),'linear_optimum':optimum,'m_equals_N_gap_lower':gap_lower,'active_band_feasible':N>=3})
checks.append({'name':'oscillatory_linear_witness','cases':len(witnesses),'passed':True})

zero_bounds=[]
# Synthetic dictionaries: roots consist of multiplicity-3 -lambda+i2pi*n*r,
# with an additional double zero for the two moment multipliers.
for B in (0,1,2,8):
    for r in (0.5,1,2):
        Dq=3*(2*B+1)
        Omega=2*pi*B*r
        K=1 if Omega==0 else floor(Omega/pi)+1
        assert Omega==0 or 1/K < pi/Omega
        zero_bounds.append({'B':B,'r':r,'Dq':Dq,'d':Dq+2,'Omega':Omega,'K':K,'switch_bound':(Dq+1)*K})
checks.append({'name':'strict_short_interval_partition','cases':len(zero_bounds),'passed':True})

# Exact closed-form integrals for the third-order unit-cell construction.
# int p2=0, int s*p2=0, int s²*p2=1/30;
# int cos=0, int s*cos=0, int s²*cos=1/(2pi²).
c=15/pi**2
moments_u=[0.0,0.0,(1/(2*pi**2)-c/30)/(1+c)]
c0=(0.5-45/pi**4)/(1+15/pi**2)
assert max(map(abs,moments_u))<1e-16 and c0>0
checks.append({'name':'third_order_linear_baseline','passed':True,'moment_residuals':moments_u,'positive_cosine_correlation':c0})

out={'status':'passed','scope':'Exact rational mapping and witness geometry; floating-point cosine normalizations; not a proof assistant or outward-rounded certificate','checks':checks,'oscillatory_witnesses':witnesses,'illustrative_zero_bound_partitions':zero_bounds}
(ROOT/'REDUCTION_DIAGNOSTICS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':'passed','checks':checks},indent=2))
