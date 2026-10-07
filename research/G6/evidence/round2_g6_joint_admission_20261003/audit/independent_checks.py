"""Original adversarial G6 checks. No imports from the candidate implementation.

Run: python outputs/round2_g6_joint_admission_20261003/audit/independent_checks.py
Analytic arguments are in INDEPENDENT_PROOF_AUDIT.md. These are floating checks,
not outward-rounded certificates or a numerical proof of asymptotic complexity.
"""
from pathlib import Path
import itertools
import json
import math
import platform
import numpy as np
import mpmath as mp

OUT = Path(__file__).resolve().parent

def series(r, theta, a, count=1200):
    k = np.arange(count, dtype=float)
    w = r**k
    return float(np.dot(w, np.abs(a[0]*np.cos(k*theta)-a[1]*np.sin(k*theta))))

def axes(r, theta, count=1200):
    k = np.arange(count, dtype=float)
    return np.array([np.dot(r**k, np.abs(np.cos(k*theta))),
                     np.dot(r**k, np.abs(np.sin(k*theta)))])

def small_angle_limit(r):
    n = int(math.floor(r/(1-r)))
    return n, 2*(n+1)*(1-r)*r**n

results = {'scope': 'Independent original code; ordinary floating checks only',
           'python': platform.python_version(), 'numpy': np.__version__,
           'checks': {}}

# Pointwise dynamic-optional support, including every corner of the amplitude box.
rng = np.random.default_rng(6152026)
errors = []
for _ in range(2000):
    g = rng.normal(size=2)
    a = rng.uniform(0, 3, size=2)
    brute = max(abs(float(g @ np.array(b)))
                for b in itertools.product(*[(0, float(v)) for v in a]))
    identity = (abs(float(g@a)) + float(abs(g)@a))/2
    errors.append(abs(brute-identity))
assert max(errors) < 4e-15
results['checks']['optional_identity_max_abs_error'] = max(errors)

# Fixed adoption and dynamic optional use do NOT commute max and sum.
r, theta, a, N = .82, .71, np.array([.7, 1.1]), 5
k = np.arange(N)
V = r**k[:, None] * np.column_stack([np.cos(k*theta), -np.sin(k*theta)])
corner_values = [float(np.abs(V@np.array(b)).sum())
                 for b in itertools.product(*[(0, float(v)) for v in a])]
fixed = max(corner_values)
choices = [np.array(b)*s for b in itertools.product(*[(0,float(v)) for v in a])
           for s in (-1,1)]
dynamic_brute = max(sum(float(V[j]@word[j]) for j in range(N))
                    for word in itertools.product(choices, repeat=N))
dynamic_identity = float((abs(V@a).sum()+abs(V).sum(axis=0)@a)/2)
assert abs(dynamic_brute-dynamic_identity) < 1e-13
assert dynamic_identity > fixed + 1e-4
results['checks']['quantifier_noncommutation'] = {
    'fixed_box_max': fixed, 'dynamic_exhaustive': dynamic_brute,
    'dynamic_identity': dynamic_identity, 'words_enumerated': len(choices)**N}

# Rational finite formula, independently summed at high precision.
mp.mp.dps = 75
rr = mp.mpf('0.87'); th = mp.pi*3/7
aa = (mp.mpf('0.4'),mp.mpf('0.9'))
sv = mp.fsum(rr**j*abs(aa[0]*mp.cos(j*th)-aa[1]*mp.sin(j*th)) for j in range(1600))
cl = mp.fsum(rr**j*abs(aa[0]*mp.cos(j*th)-aa[1]*mp.sin(j*th)) for j in range(7))/(1-rr**7)
assert abs(sv-cl) < mp.mpf('1e-70')
results['checks']['rational_period7_error'] = str(abs(sv-cl))

# Sharp universal r=1/2 boundary and small-angle limits above/below it.
boundary = []
for rr in (.2, .49, .5, .51, .6, .75, .9, .98):
    for th in (.7, math.pi*(math.sqrt(5)-1)/2, .01, .001):
        cc = axes(rr, th)
        fc = series(rr, th, 1/cc)
        dyn = 1 + fc/2
        n, lim = small_angle_limit(rr)
        lower = 2/cc[0]
        assert fc >= lower-2e-12
        if rr <= .5:
            assert fc > 1
        assert dyn > 1
        boundary.append({'r':rr,'theta':th,'corner_F':fc,
                         'lower_2_over_c1':lower,'corner_Fvar':dyn,
                         'n':n,'small_angle_limit':lim})
results['checks']['rectangle_threshold'] = boundary
limit_errors = []
for rr in (.25,.49,.5,.51,.6,2/3,.75,.9,.98):
    th = 1e-5
    cc = axes(rr,th,3000)
    value = series(rr,th,1/cc,3000)
    n, lim = small_angle_limit(rr)
    assert abs(value-lim) < 2e-7
    limit_errors.append({'r':rr,'n':n,'value':value,'limit':lim,
                         'error':abs(value-lim)})
results['checks']['small_angle_convergence'] = limit_errors

# The folded q-block error bound uses the true theta within the first block.
fold = []
for q,p,delta in [(7,3,1e-3),(7,3,1e-6),(13,5,1e-5),(31,12,1e-5)]:
    rr = .85; th = (p*math.pi+delta)/q
    ts = np.linspace(.2,3,2001)
    k = np.arange(q)
    folded = np.abs(np.cos(k[:,None]*th)-ts[None,:]*np.sin(k[:,None]*th))
    folded = (rr**k @ folded)/(1-rr**q)
    full = np.array([series(rr,th,(1,t)) for t in ts])
    err = float(np.max(abs(full-folded)))
    bound = math.sqrt(10)*abs(delta)*rr**q/((1-rr)*(1-rr**q))
    assert err <= bound+1e-13
    fold.append({'q':q,'p':p,'q_theta_minus_p_pi':delta,
                 'grid_max_error':err,'analytic_uniform_bound':bound,
                 'max_affine_pieces':q+1})
results['checks']['folded_block_error'] = fold

# Early distinct kinks force distinct approximation breakpoints. For any affine
# approximant over a neighborhood, the three-point gap/4 is a necessary error.
rr,th,N,lo,hi = .7, math.pi*(math.sqrt(5)-1)/2, 40, .2, 3.
roots = sorted((math.cos(j*th)/math.sin(j*th),j)
               for j in range(1,N+1)
               if lo < math.cos(j*th)/math.sin(j*th) < hi)
gaps = []
for i,(t,j) in enumerate(roots):
    left = roots[i-1][0] if i else lo
    right = roots[i+1][0] if i+1<len(roots) else hi
    h = min(t-left,right-t)/3
    curvature_gap = series(rr,th,(1,t-h))+series(rr,th,(1,t+h))-2*series(rr,th,(1,t))
    guaranteed = 2*rr**j*abs(math.sin(j*th))*h
    assert curvature_gap >= guaranteed-2e-14
    gaps.append({'index':j,'slope':t,'halfwidth':h,
                 'three_point_gap':curvature_gap,'single_kink_lower':guaranteed,
                 'necessary_error_if_no_breakpoint':guaranteed/4})
results['checks']['local_kink_obstruction'] = gaps

# Initial output safety alone cannot remove the carried hidden-state transient.
rr,th = .85,.7
x0 = np.array([0.,10.]); aa = np.array([0.,0.])
next_y = rr*(math.cos(th)*x0[0]-math.sin(th)*x0[1])+aa[0]
assert abs(x0[0])<=1 and series(rr,th,aa)==0 and abs(next_y)>1
results['checks']['nonzero_initial_state_counterexample'] = {
    'r':rr,'theta':th,'x0':x0.tolist(),'amplitudes':aa.tolist(),
    'initial_output':float(x0[0]),'first_output':next_y,'zero_start_F':0}

# Reciprocal of an affine gauge is not piecewise affine. Here theta=0 makes
# f(t)=1/(1-r) on (1,t) rays, so choose alternative coordinate a=(t,1), whose
# gauge is t/(1-r). Its radial value is (1-r)/t, with nonzero chord error.
rr=.7
errors = []
for segments in (10,20,40,80):
    x=np.linspace(1,2,segments+1);mid=(x[:-1]+x[1:])/2
    err=float(np.max((1-rr)*(1/x[:-1]+1/x[1:])/2-(1-rr)/mid))
    errors.append({'segments':segments,'radial_linear_interpolation_error':err,
                   'segments_squared_times_error':segments**2*err})
results['checks']['radial_PL_class_warning'] = errors
results['all_checks_passed'] = True
(OUT/'INDEPENDENT_CHECK_RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({'all_checks_passed':True,'output':str(OUT/'INDEPENDENT_CHECK_RESULTS.json'),
                  'optional_identity_error':max(errors) if False else results['checks']['optional_identity_max_abs_error'],
                  'tested_kinks':len(gaps)},indent=2))
