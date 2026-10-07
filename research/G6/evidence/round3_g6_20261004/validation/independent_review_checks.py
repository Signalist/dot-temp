"""Independent G6 round-3 falsification checks. No producer top-level script run.
The proofs in INDEPENDENT_PROOF_REVIEW.md carry infinite-horizon claims.
Direct mpmath values below are high-precision diagnostics, not interval proofs.
"""
from pathlib import Path
from fractions import Fraction as Q
import ast, csv, ctypes, hashlib, itertools, json, math, time
import numpy as np
import mpmath as mp
from scipy.optimize import brentq, linprog

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parent / 'round2_g6_joint_admission_20261003'
OUT = Path(__file__).resolve().parent
rng = np.random.default_rng(927640104)
result = {'seed':927640104,'scope':'Original independent tests; no candidate top-level numerical experiment is imported or rerun. Analytic proof review is separate.'}
started=time.time()

def prefix(theta,r,a,n):
    k=np.arange(n)
    return float(np.sum(r**k*np.abs(a[0]*np.cos(k*theta)-a[1]*np.sin(k*theta))))

def finite_max(lo,hi,r,a,n):
    """Enumerate every trig kink, then solve the single possible maximum
    on each smooth component. Each component has f''<=0, so this differs
    materially from a dense phase sample or the candidate grid algorithm.
    """
    k=np.arange(n);w=r**k;alpha=math.atan2(a[1],a[0]);knots=[lo,hi]
    for j in range(1,n):
        for m in range(math.floor((j*lo+alpha-math.pi/2)/math.pi)-1,
                       math.ceil((j*hi+alpha-math.pi/2)/math.pi)+2):
            x=(math.pi/2-alpha+m*math.pi)/j
            if lo<x<hi:knots.append(x)
    knots=np.unique(knots);candidates=list(knots)
    for l,u in zip(knots[:-1],knots[1:]):
        mid=(l+u)/2
        signs=np.sign(a[0]*np.cos(k*mid)-a[1]*np.sin(k*mid))
        def deriv(t):return float(np.sum(w*signs*k*(-a[0]*np.sin(k*t)-a[1]*np.cos(k*t))))
        if deriv(l)>0 and deriv(u)<0:
            candidates.append(brentq(deriv,l,u,xtol=5e-15))
    vals=[prefix(t,r,a,n) for t in candidates]
    j=int(np.argmax(vals))
    return vals[j],candidates[j],len(knots)-2

# T1: wide cells with many kinks, negative a, negative angles, near-unit r.
t1=[]
for case in range(72):
    r=float(rng.choice([.2,.6,.85,.97,.995]));n=int(rng.choice([2,16,47,96]))
    a=rng.normal(size=2);lo=float(rng.uniform(-4,4));h=float(10**rng.uniform(-3,.1));hi=lo+h
    peak,arg,kinks=finite_max(lo,hi,r,a,n)
    endpoints=max(prefix(lo,r,a,n),prefix(hi,r,a,n))
    bound=float(np.linalg.norm(a)*np.sum(np.arange(n)**2*r**np.arange(n))*h*h/8)
    assert peak <= endpoints+bound+2e-12*max(1,peak)
    t1.append({'case':case,'r':r,'N':n,'kinks':kinks,'gap':peak-endpoints,'bound':bound})
# Smooth single-term maximum makes the coefficient 1/8 asymptotically sharp.
sharp=[]
for h in [1e-1,1e-2,1e-3]:
    gap=.7*(1-math.cos(h/2));bound=.7*h*h/8
    sharp.append({'h':h,'gap_bound_ratio':gap/bound})
result['T1']={'finite_cell_cases':len(t1),'maximum_kinks_in_one_cell':max(x['kinks'] for x in t1),'largest_gap_bound_ratio':max(x['gap']/x['bound'] for x in t1),'sharp_constant_diagnostics':sharp,'cases':t1}

# Isolate just producer interval primitives; no side-effecting experiment run.
src=ROOT/'src/run_finite_uncertainty.py'
ns={'Q':Q,'math':math,'S':10**120,'N':512,'r':Q(17,20)}
functions=[node for node in ast.parse(src.read_text()).body if isinstance(node,ast.FunctionDef) and node.name in ['fl','ce','rational_to_iv','add','neg','mul','absiv','trig_iv','exact_prefix','dec']]
exec(compile(ast.Module(body=functions,type_ignores=[]),str(src),'exec'),ns)
S=ns['S']
# Signed rational endpoint witnesses exercise all interval arithmetic quadrants.
for i in range(1500):
    p=sorted(int(x) for x in rng.integers(-200,200,size=2));q=sorted(int(x) for x in rng.integers(-200,200,size=2))
    x=tuple(t*S//73 for t in p);y=tuple(t*S//41 for t in q)
    prod=ns['mul'](x,y)
    exact=[Q(a*b,S*S) for a in x for b in y]
    assert Q(prod[0],S)<=min(exact)<=max(exact)<=Q(prod[1],S)
    absolute=ns['absiv'](x)
    targets=[abs(Q(a,S)) for a in x]+([Q(0)] if x[0]<=0<=x[1] else [])
    assert Q(absolute[0],S)<=min(targets)<=max(targets)<=Q(absolute[1],S)
mp.mp.dps=180
mq=lambda q:mp.mpf(q.numerator)/q.denominator
cert=json.loads((ROOT/'experiments/EXACT_RATIONAL_PARAMETER_CERTIFICATE.json').read_text())
assert cert['source_sha256']==hashlib.sha256(src.read_bytes()).hexdigest()
angles=[Q(11,20)+Q(3,10)*Q(j,128) for j in range(129)]
all_prefix=[];iv=[];mp_r=mp.mpf(17)/20
for angle in angles:
    th=mq(angle)
    # Independent direct sin(k*theta)/cos(k*theta), not trig recurrence.
    val=mp.fsum(mp_r**k*abs((mp.cos(k*th)-mp.sin(k*th))/2) for k in range(512))
    lower,upper=ns['exact_prefix'](angle)
    assert mp.mpf(lower)/S<=val<=mp.mpf(upper)/S
    all_prefix.append(val);iv.append((Q(lower,S),Q(upper,S)))
for row in cert['rows']:
    step=128//row['intervals'];actual=max(all_prefix[::step]);samples=iv[::step]
    assert mp.mpf(row['prefix_lower'])<=actual<=mp.mpf(row['prefix_upper'])
    low=max(t[0] for t in samples);up=max(t[1] for t in samples)
    normhi=Q(math.isqrt(S*S//2)+1,S)
    c2=sum(Q(k*k)*Q(17,20)**k for k in range(512));tail=Q(17,20)**512/Q(3,20)
    error=normhi*(c2*(Q(3,10)/row['intervals'])**2/8+tail)
    assert Q(row['prefix_lower'])<=low and Q(row['prefix_upper'])>=up
    assert Q(row['robust_upper'])>=up+error
    assert Q(row['capacity_at_threshold_1_lower'])<=1/(up+error)
    assert Q(row['capacity_at_threshold_1_upper'])>=1/low
raw=json.loads((ROOT/'experiments/EXACT_RATIONAL_GRID_RAW.json').read_text())
assert int(raw['scale'])==S and raw['N']==512
assert Q(int(raw['c2_numerator']),int(raw['c2_denominator']))==c2
assert Q(int(raw['tail_numerator']),int(raw['tail_denominator']))==tail
for j,row in enumerate(raw['grid']):
    assert Q(row['theta'])==angles[j]
    assert (Q(int(row['prefix_lower_integer']),S),Q(int(row['prefix_upper_integer']),S))==iv[j]
# Float rows are diagnostic and all admit the exact theoretical error formula.
floatrows=json.loads((ROOT/'experiments/FINITE_UNCERTAINTY_FLOAT.json').read_text())['rows']
for row in floatrows:
    r=row['r'];h=2*row['theta_halfwidth']/row['intervals'];norm=math.hypot(row['a1'],row['a2'])
    independent_error=norm*(r*(1+r)/(1-r)**3*h*h/8+r**512/(1-r))
    assert math.isclose(row['second_order_error'],independent_error,rel_tol=1e-12)
    assert row['dense_diagnostic']<=row['second_order_upper']+1e-12
result['rational_certificate']={'arithmetic_endpoint_cases':1500,'direct_high_precision_prefix_checks':129,'precision_digits':180,'all_prefixes_contained':True,'all_5_serialized_brackets_and_reciprocals_round_outward':True,'source_sha256':cert['source_sha256'],'float_diagnostic_rows_checked':len(floatrows),'finest_prefix_max_direct':mp.nstr(max(all_prefix),70),'finest_saved_upper':cert['rows'][-1]['robust_upper'],'note':'High-precision trig checks are diagnostics; the proof of exact enclosure uses Taylor remainder and interval induction, not mpmath.'}

# T2: independent smooth elliptical gauge with explicit maximizing direction.
# Its robustification is an exact circle only where zero angle can align.
M=2.0;delta=.07;arcs=[]
for angle in np.linspace(-delta,delta,31):
    v=np.array([math.cos(angle),math.sin(angle)])
    phi=-angle
    rotated=np.array([[math.cos(phi),-math.sin(phi)],[math.sin(phi),math.cos(phi)]])@v
    attained=math.hypot(2*rotated[0],rotated[1])
    assert abs(attained-M)<2e-15
    arcs.append(attained)
# Miscentered J cannot align a sector around zero.
outside_theta=0.;J=(.5,.6)
miscentered=max(math.sqrt(4*math.cos(phi)**2+math.sin(phi)**2) for phi in np.linspace(*J,5001))
assert miscentered<M-.1
# Chord construction and lower-bound midpoint constants.
piece_tests=[]
for lo,hi in [(.1,.5),(.4,1.2),(2.,4.)]:
    D=hi-lo;kappa=M/(1+hi*hi)**1.5;K=M/(1+lo*lo)**1.5
    for eps in [1e-2,1e-3,1e-4]:
        n=max(1,math.ceil(D*math.sqrt(K/(8*eps))))
        xx=np.linspace(lo,hi,n+1);f=lambda x:M*np.sqrt(1+x*x)
        t=np.linspace(lo,hi,6001);g=np.interp(t,xx,f(xx));err=g-f(t)
        assert err.min()>-1e-14 and err.max()<=eps+1e-13
        l,u=xx[0],xx[1];second=f(l)+f(u)-2*f((l+u)/2)
        assert second+1e-13>=kappa*(u-l)**2/4
        piece_tests.append({'l':lo,'u':hi,'epsilon':eps,'safe_pieces':n,'observed_error':float(err.max()),'lower_piece_bound':D*math.sqrt(kappa)/(4*math.sqrt(eps))})
result['T2']={'aligned_directions_checked':len(arcs),'miscentered_robust_unit_gauge':miscentered,'miscentered_M':M,'chord_and_midpoint_cases':piece_tests}

# An exact finite example detects exchanging parameter maximization and sum.
# r=.7, N=2, a=(.5,.5), theta in [0,pi/2]: max H=.85, but summing
# separately maximized F(a), F(a1,0), F(0,a2), then dividing by two is 1.025.
theta=np.linspace(0,math.pi/2,10001)
F=.5+.35*abs(np.cos(theta)-np.sin(theta))
F1=.5+.35*abs(np.cos(theta));F2=.35*abs(np.sin(theta))
shared=float(np.max((F+F1+F2)/2));relaxed=float((max(F)+max(F1)+max(F2))/2)
assert abs(shared-.85)<1e-14 and abs(relaxed-1.025)<1e-14
result['fixed_parameter_quantifier']={'exact_two_term_shared_H_max':shared,'componentwise_parameter_relaxation':relaxed,'strict_relaxation_gap':relaxed-shared}

# General language enumeration includes startup lengths below L and nonfull tails.
lib=ctypes.CDLL(str(ROOT/'contracts/window_dp.so'))
ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
lib.window_dp.argtypes=[ptr,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ptr]
def cdp(gains,L,B):
    gains=np.ascontiguousarray(gains[None,:],dtype=np.float64);out=np.empty(1)
    lib.window_dp(gains,1,gains.shape[1],L,B,out)
    return float(out[0])
def language(z,L,B):
    # Definition without bit states, convolution, or DP transitions.
    return all(sum(z[i:j])<=B for i in range(len(z)) for j in range(i+1,min(len(z),i+L)+1))
languages=[]
for L in [2,3,5,8]:
    for n in sorted(set([1,L-1,L,L+3])):
        words=list(itertools.product([0,1],repeat=n))
        for B in range(L+1):
            feasible=[z for z in words if language(z,L,B)]
            assert all(language(tuple(reversed(z)),L,B) and language((0,)*L+z+(0,)*L,L,B) for z in feasible)
            gains=rng.normal(size=n)
            best=max(float(gains@z) for z in feasible)
            actual=cdp(gains,L,B)
            assert abs(best-actual)<1e-11
            languages.append({'L':L,'B':B,'n':n,'legal_words':len(feasible),'gap':abs(best-actual)})
result['T3']={'exhaustive_language_cases':len(languages),'maximum_gap':max(x['gap'] for x in languages),'reversal_and_zero_padding_checked_for_every_feasible_test_word':True,'cases':languages}

# T3a: independent integer min-cost residual flow, no LP or suffix states.
def flow_value(gains,L,B):
    n=len(gains);sink=n-1+L;adj=[[] for _ in range(sink+1)]
    def add(u,v,cap,cost):
        adj[u].append([v,len(adj[v]),cap,cost]);adj[v].append([u,len(adj[u])-1,0,-cost])
    for j in range(sink):add(j,j+1,B,0)
    for j,gain in enumerate(gains):add(j,j+L,1,-int(gain))
    total=0
    for _ in range(B):
        dist=[math.inf]*(sink+1);dist[0]=0;previous=[None]*(sink+1)
        # Bellman-Ford also handles negative reverse residual edges exactly.
        for __ in range(sink):
            changed=False
            for u in range(sink+1):
                for e,(v,rev,cap,cost) in enumerate(adj[u]):
                    if cap>0 and dist[v]>dist[u]+cost:
                        dist[v]=dist[u]+cost;previous[v]=(u,e);changed=True
            if not changed:break
        assert previous[sink] is not None
        total+=dist[sink];v=sink
        while v:
            u,e=previous[v];edge=adj[u][e]
            edge[2]-=1;adj[v][edge[1]][2]+=1;v=u
    return -total
flow_cases=[]
for L in [1,2,4,8]:
    for n in sorted(set([1,max(1,L-1),L,L+2])):
        words=list(itertools.product([0,1],repeat=n))
        for B in range(L+1):
            gain=rng.integers(-9,10,size=n)
            best=max(sum(int(g)*z for g,z in zip(gain,word)) for word in words if language(word,L,B))
            actual=flow_value(gain,L,B)
            assert actual==best
            # Fully padded window LP, explicitly including N<L edge cases.
            matrix=np.array([[int(t-L+1<=j<=t) for j in range(n)] for t in range(n+L-1)])
            lp=linprog(-gain,A_ub=matrix,b_ub=np.full(len(matrix),B),bounds=(0,1),method='highs')
            assert lp.success and abs(-lp.fun-best)<1e-8
            flow_cases.append({'L':L,'B':B,'n':n,'integer_optimum':int(best),'flow_optimum':int(actual),'LP_gap':abs(-lp.fun-best)})
result['T3a']={'exact_flow_vs_enumeration_cases':len(flow_cases),'all_padded_LP_values_equal':True,'maximum_LP_gap':max(c['LP_gap'] for c in flow_cases),'cases':flow_cases}

# Independently reload all 30 network witnesses and every power segment.
words=json.loads((ROOT/'contracts/maximizing_words.json').read_text())
arrays=np.load(ROOT/'contracts/all_phase_support_arrays.npz')
saved_rows=list(csv.DictReader((ROOT/'contracts/contract_amplitude_brackets.csv').open()))
checks=[]
for word in words:
    name=word['source'];ri=word['ray_index'];B=word['B'];L=word['L']
    sub='positive_workpoint' if name=='positive' else 'transfer'
    W=np.load(OLD/sub/f'{name}_coefficients.npy',mmap_mode='r')
    o=word['probe_output_index'];t=round(word['probe_phase_seconds']*1024)
    u=np.array(word['unit_total_amplitude_port_values_chronological']);z=tuple(word['mismatch_chronological'])
    assert language(z,L,B) and language(tuple(reversed(z)),L,B)
    assert np.array_equal((u[:,0]*u[:,1]<0).astype(int),z)
    direct=float(np.sum(W[o,t].T*u[::-1]))
    assert abs(direct-word['direct_output_Hz_per_MW'])<1e-13
    profile=arrays[f'{name}_ray{ri}_B{B}']
    assert abs(float(profile.max())-direct)<1e-13
    row=next(row for row in saved_rows if row['source']==name and int(row['ray_index'])==ri and int(row['B'])==B)
    assert abs(float(row['inner_amplitude_MW'])*float(row['peak_upper_Hz_per_MW'])-.05)<1e-15
    assert abs(float(row['outer_amplitude_MW'])*float(row['peak_lower_Hz_per_MW'])-.05)<1e-15
    assert abs(word['finite_linear_probe_output_Hz']-.051)<2e-15
    # An independently assembled window LP at the selected physical coefficients.
    a=np.array([float(row['a1']),float(row['a2'])]);p=W[o,t,0]*a[0];q=W[o,t,1]*a[1]
    base=np.sum(abs(p+q));gain=abs(p-q)-abs(p+q);scale=max(abs(gain)) or 1.
    A=np.zeros((len(gain)-L+1,len(gain)))
    for j in range(len(A)):A[j,j:j+L]=1
    lp=linprog(-gain/scale,A_ub=A,b_ub=np.full(len(A),B),bounds=(0,1),method='highs',options={'primal_feasibility_tolerance':1e-10,'dual_feasibility_tolerance':1e-10})
    assert lp.success
    lp_support=float(base-lp.fun*scale)
    assert abs(lp_support-direct)<1e-12
    checks.append({'id':word['id'],'direct_sum_gap':abs(direct-word['direct_output_Hz_per_MW']),'LP_support_gap':abs(lp_support-direct),'physical_compute':word['actual_compute_nonnegative']})
for name in ['positive','wecc']:
    for ri in range(3):
        for b1,b2 in zip([0,1,2,4],[1,2,4,8]):
            assert np.min(arrays[f'{name}_ray{ri}_B{b2}']-arrays[f'{name}_ray{ri}_B{b1}'])>=-1e-14
# Exact segment energy and chronological sign reconstruction.
segments=list(csv.DictReader((ROOT/'contracts/maximizing_word_schedules.csv').open()))
by_word={w['id']:w for w in words};energy={}
for seg in segments:
    w=by_word[seg['witness_id']];block=int(seg['block']);j=int(seg['segment']);key=(w['id'],block)
    v=np.array(w['unit_total_amplitude_port_values_chronological'][block])*w['exported_schedule_total_amplitude_MW']
    signs=[[1,1],[1,-1],[-1,-1],[-1,1]][j]
    dp=np.array([float(seg['deltaP1_MW']),float(seg['deltaP2_MW'])]);assert np.array_equal(v*signs,dp)
    assert np.allclose(np.array(w['physical_P0_MW'])+dp,[float(seg['P1_MW']),float(seg['P2_MW'])],rtol=0,atol=0)
    energy.setdefault(key,np.zeros(2));energy[key]+=dp*(float(seg['end_seconds'])-float(seg['start_seconds']))
assert all(np.max(abs(e))<1e-13 for e in energy.values())
result['network_contracts']={'witnesses_checked':len(checks),'maximum_independent_LP_gap':max(c['LP_support_gap'] for c in checks),'segments_checked':len(segments),'balanced_two_port_blocks_checked':len(energy),'positive_physical_compute_witnesses':sum(c['physical_compute'] for c in checks),'cases':checks,'scope':'Conditional LTI, frozen modal kernels, floating analytic phase/tail bounds. No new nonlinear result.'}

# T4: an unrestricted finite word followed by zeros has rate zero regardless
# of the finite word. Every selected independent maximizer is such a witness.
independent=[w for w in words if w['B']==8]
result['T4']={'independent_finite_witnesses':len(independent),'finite_mismatch_counts':[sum(w['mismatch_chronological']) for w in independent],'continuation':'All zeros after complete witness; rates are finite_mismatch_count/n -> 0. This is an all-time supremum argument, not a finite-time attainment claim.'}

# T5: independently enumerate all 4! orders, not just the submitted plans.
dagdata=json.loads((ROOT/'experiments/JOB_DAG_REALIZATION.json').read_text())
jobs=('H1','H2','L1','L2');all_orders=list(itertools.permutations(jobs));dag_checks=[]
for port in ['port1','port2']:
    ledgers=[v for v in dagdata['ledgers'] if v['plan'].startswith(port)]
    edges=ledgers[0]['edges']
    legal_orders=[p for p in all_orders if all(p.index(u)<p.index(v) for u,v in edges)]
    assert all(tuple(led['order']) in legal_orders for led in ledgers)
    for led in ledgers:
        assert set(led['order'])==set(jobs) and len(led['order'])==4
        watts=[60 if job.startswith('H') else 40 for job in led['order']]
        assert watts==led['power_MW']
        assert sum(watts)*Q(1,2)==led['energy_MJ']==100
        assert led['completed_work_units']==8 and led['incremental_energy_MJ']==0
    assert np.array_equal(np.array(ledgers[0]['power_MW'])-50,50-np.array(ledgers[1]['power_MW']))
    # Every subset of a common-precedence relation stays acyclic automatically.
    plus,minus=ledgers[0]['order'],ledgers[1]['order']
    common={(u,v) for u in jobs for v in jobs if plus.index(u)<plus.index(v) and minus.index(u)<minus.index(v)}
    expected=2**len(common)
    reported=dagdata['both_feasible_counts'][port]
    assert expected==reported
    dag_checks.append({'port':port,'all_orders_enumerated':24,'topological_orders':len(legal_orders),'common_precedence_pairs':sorted(common),'permitted_forward_edge_subsets':expected})
assert dagdata['counterexample']['plus_feasible'] and not dagdata['counterexample']['minus_feasible']
for row in dagdata['DAG_checks']:
    ports=[x for x in dagdata['ledgers'] if x['plan'].startswith(row['port'])]
    actual=all(all(x['order'].index(u)<x['order'].index(v) for u,v in row['edges']) for x in ports)
    assert actual==row['both_plans_feasible']==row['intersection_test']
orientation=json.loads((ROOT/'experiments/ORIENTATION_CROSSOVER.json').read_text())
for row in orientation['rows']:
    l,u=row['slope_l'],row['slope_u'];K=(1+l*l)**-1.5;kappa=(1+u*u)**-1.5;D=u-l
    n=row['safe_constructed_pieces'];eps=row['gauge_tolerance']
    assert K*(D/n)**2/8<=eps*(1+1e-13)
    assert math.isclose(row['proven_piece_lower_real'],D*math.sqrt(kappa)/(4*math.sqrt(eps)),rel_tol=1e-14)
result['T5']={'job_order_cases':dag_checks,'saved_DAG_rows_checked':len(dagdata['DAG_checks']),'same_jobs_energy_work_and_complementary_powers_verified':True,'orientation_crossover_rows_checked':len(orientation['rows']),'scope':'The declared synthetic fixed-power, fixed-duration job catalog only. No calibrated PCC trace, transition cost, amplitude scaling, or generic GPU realization follows.'}
# Verify every historical file listed in the inherited source provenance.
provenance=json.loads((ROOT/'contracts/SOURCE_PROVENANCE.json').read_text())
for entry in provenance:
    for name,sha in entry['hashes'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha
result['frozen_input_hashes_verified']=sum(len(e['hashes']) for e in provenance)
result['elapsed_seconds']=time.time()-started
result['all_assertions_passed']=True
(OUT/'INDEPENDENT_CHECK_RESULTS.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:result[k] for k in ['all_assertions_passed','elapsed_seconds','frozen_input_hashes_verified']},indent=2))
print('finite-cell tests',len(t1),'maximum kinks',result['T1']['maximum_kinks_in_one_cell'])
print('rational direct checks',len(angles),'language cases',len(languages),'network witnesses',len(checks))
