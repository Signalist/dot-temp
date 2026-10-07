#!/usr/bin/env python3
"""Independent small-instance checks; numeric LP evidence is not a proof."""
from itertools import combinations, permutations, product
from fractions import Fraction as F
from pathlib import Path
import json, math
import numpy as np
from scipy.optimize import linprog

OUT=Path(__file__).parent
L,H,EC,ED,DT=1.,3.,.5,.5,1.

def prefixes(word,rho=1.):
    n=len(word); A=np.zeros((n+1,n)); c=np.zeros(n+1)
    for j,label in enumerate(word,1):
        A[j]=rho*A[j-1]; c[j]=rho*c[j-1]
        A[j,j-1]=EC if label==0 else 1/ED
        c[j]-=EC*L if label==0 else H/ED
    return A,c

def stationary_lp(words,pbounds=None):
    n=len(words[0]); A=[]; b=[]; E=[]; f=[]
    for w in words:
        g,c=prefixes(w)
        for j in range(n+1):
            row=np.zeros(n+2); row[:n]=g[j]; row[n]=1; row[n+1]=-1
            A.append(row); b.append(-c[j])
            row=np.zeros(n+2); row[:n]=-g[j]; row[n]=-1
            A.append(row); b.append(c[j])
        row=np.zeros(n+2); row[:n]=g[-1]; E.append(row); f.append(-c[-1])
    obj=np.zeros(n+2);obj[-1]=1
    return linprog(obj,A_ub=A,b_ub=b,A_eq=E,b_eq=f,bounds=(pbounds or [(L,H)]*n)+[(0,None)]*2,method='highs')

def horizon_lp(words,m,pbounds=None):
    n=len(words[0]); l0=m*n; u0=l0+m+1; bi=u0+m+1; nv=bi+1
    A=[]; b=[]; E=[]; f=[]
    row=np.zeros(nv);row[l0]=1;row[u0]=-1;E.append(row);f.append(0.)
    for block in range(m):
        sl=slice(block*n,(block+1)*n)
        for w in words:
            g,c=prefixes(w)
            for j in range(n+1):
                row=np.zeros(nv);row[sl]=-g[j];row[l0+block]=-1;A.append(row);b.append(c[j])
                row=np.zeros(nv);row[sl]=g[j];row[u0+block]=1;row[bi]=-1;A.append(row);b.append(-c[j])
            row=np.zeros(nv);row[l0+block+1]=1;row[l0+block]=-1;row[sl]=-g[-1];A.append(row);b.append(c[-1])
            row=np.zeros(nv);row[u0+block+1]=-1;row[u0+block]=1;row[sl]=g[-1];A.append(row);b.append(-c[-1])
    for block in range(m+1):
        row=np.zeros(nv);row[l0+block]=1;row[u0+block]=-1;A.append(row);b.append(0.)
        row=np.zeros(nv);row[u0+block]=1;row[bi]=-1;A.append(row);b.append(0.)
    bounds=(pbounds or [(L,H)]*n)*m+[(0,None)]*(nv-m*n)
    obj=np.zeros(nv);obj[bi]=1
    return linprog(obj,A_ub=A,b_ub=b,A_eq=E,b_eq=f,bounds=bounds,method='highs')

def rank_exact(A):
    if not A:return 0
    a=[[F(x) for x in row] for row in A];r=0
    for c in range(len(a[0])):
        q=next((q for q in range(r,len(a)) if a[q][c]),None)
        if q is None:continue
        a[r],a[q]=a[q],a[r];v=a[r][c];a[r]=[x/v for x in a[r]]
        for q in range(r+1,len(a)):
            v=a[q][c]
            if v:a[q]=[x-v*y for x,y in zip(a[q],a[r])]
        r+=1
    return r

results={'parameters':{'L':L,'H':H,'eta_c':EC,'eta_d':ED,'delta':DT},'scope':'independent exact rational identities, exhaustive tiny DAGs, numerical LP cross-checks'}

# T1: all nonempty fixed-count binary-word families for N<=3.
family_cases=[]
for n in range(1,4):
    for k in range(n+1):
        allwords=[w for w in product((0,1),repeat=n) if sum(w)==k]
        for mask in range(1,1<<len(allwords)):
            words=[w for j,w in enumerate(allwords) if mask>>j&1]
            ss=stationary_lp(words);assert ss.success
            vals=[]
            for m in (1,2,4,8):
                h=horizon_lp(words,m);assert h.success
                vals.append(h.fun)
                assert h.fun<=ss.fun+1e-7
            assert all(x<=y+1e-7 for x,y in zip(vals,vals[1:]))
            family_cases.append({'words':[''.join(map(str,w)) for w in words],'B_star':float(ss.fun),'horizon_1_2_4_8':vals})
results['T1_tiny_family_count']=len(family_cases)
results['T1_tiny_families']=family_cases

# A rational infinite schedule realizes the strengthened lower bound with W>0.
# First p=(14/5,12/5); subsequent p=(13/5,13/5); e0=11/10.
q=F(13,5);e0=F(11,10);B=F(11,5)
words=[(0,1),(1,0)]
def fg(word,p,rho=F(1)):
    g=[F(0)]
    for d,x in zip(word,p):g.append(rho*g[-1]+((x-1)/2 if d==0 else 2*(x-3)))
    return g
trans=[fg(w,[F(14,5),F(12,5)]) for w in words]
rs=[g[-1] for g in trans];lo=e0+min(rs);hi=e0+max(rs)
assert rs==[F(-3,10),F(3,10)]
assert all(0<=e0+g<=B for gs in trans for g in gs)
repeated=[fg(w,[q,q]) for w in words]
assert all(gs[-1]==0 for gs in repeated)
assert min(lo+g for gs in repeated for g in gs)==0
assert max(hi+g for gs in repeated for g in gs)==B
results['T1_positive_width_equality']={'first_p':['14/5','12/5'],'later_p':['13/5','13/5'],'initial':'11/10','B_star':'8/5','W_infinity':'3/5','B':'11/5','verified':True}
# Infeasible reset restriction forces horizon capacity growth.
bad=[]
assert not stationary_lp(words,[(1,1),(3,3)]).success
for m in (1,2,4,8):
    h=horizon_lp(words,m,[(1,1),(3,3)]);assert h.success and abs(h.fun-(3*m+1))<1e-8;bad.append(h.fun)
results['T1_infeasible_reset_example']={'p':[1,3],'horizons':[1,2,4,8],'capacities':bad,'exact_formula':'3 M + 1'}

# T2: all DAGs with natural-order edges N<=4, and all mixed binary task labels.
dag_count=0;labelled_count=0;connected_count=0;t3_count=0;strict_example=None
for n in range(2,5):
    possible=list(combinations(range(n),2));perms=list(permutations(range(n)))
    for mask in range(1<<len(possible)):
        edges=[edge for i,edge in enumerate(possible) if mask>>i&1]
        exts=[]
        for order in perms:
            positions={x:i for i,x in enumerate(order)}
            if all(positions[a]<positions[b] for a,b in edges):exts.append(order)
        extset=set(exts);dag_count+=1
        for labels in product((0,1),repeat=n):
            k=sum(labels)
            if k in (0,n):continue
            labelled_count+=1
            S=sorted(set(tuple(labels[x] for x in e) for e in exts))
            slots=set()
            for e in exts:
                for t in range(n-1):
                    if labels[e[t]]==labels[e[t+1]]:continue
                    swapped=e[:t]+(e[t+1],e[t])+e[t+2:]
                    if swapped in extset:slots.add(t)
            diff=[[w[t]-S[0][t] for t in range(n)] for w in S[1:]]
            assert rank_exact(diff)==len(slots)
            components=[];start=0
            for t in range(n-1):
                if t not in slots:components.append(range(start,t+1));start=t+1
            components.append(range(start,n))
            assert all(sum(row[t] for t in component)==0 for row in diff for component in components)
            if len(slots)==n-1:
                connected_count+=1
                q=(k*H+EC*ED*(n-k)*L)/(k+EC*ED*(n-k))
                c=EC*(q-L);h=(H-q)/ED
                prefix_values=[c*t-(c+h)*sum(w[:t]) for w in S for t in range(n+1)]
                formula=max(prefix_values)-min(prefix_values)
                lp=stationary_lp(S);assert lp.success and abs(lp.fun-formula)<1e-7;t3_count+=1
                if strict_example is None and formula<2*(n-k)*c-1e-7:
                    strict_example={'N':n,'edges':edges,'task_labels':labels,'words':S,'B':formula,'full_permutations_B':2*(n-k)*c,'slot_edges':sorted(slots)}
results['T2_exhaustive']={'natural_order_DAGs':dag_count,'DAG_label_cases':labelled_count,'connected_cases':connected_count,'all_exact_rank_and_component_assertions_passed':True}
results['T3_formula_LP_checks']=t3_count
results['T3_first_strict_restriction_example']=strict_example

# T4: rational alternating automaton; verify potentials and extrema directly.
p=[F(14,5),F(12,5)];v={'A':F(0),'B':F(-3,10)}
edges=[('A','B',(0,1)),('B','A',(1,0))];values=[v['A']]
for a,b,w in edges:
    g=fg(w,p);assert g[-1]==v[b]-v[a];values += [v[a]+x for x in g]
assert max(values)-min(values)==F(8,5)
results['T4_correlated_nonzero_residual_example']={'edge_A_B_word':'LH','edge_B_A_word':'HL','p':['14/5','12/5'],'edge_residuals':['-3/10','3/10'],'potential_A':'0','potential_B':'-3/10','B':'8/5','initial_energy':'7/10','verified':True}

# T5: rational self-discharge hull and all prefixes, plus numerical LP cross-check.
rho=F(9,10);p=[F(27,10)]*2;gs=[fg(w,p,rho) for w in words];a=rho**2
r=[g[-1] for g in gs];lo=min(r)/(1-a);hi=max(r)/(1-a)
mins=[rho**j*lo+min(g[j] for g in gs) for j in range(3)]
maxs=[rho**j*hi+max(g[j] for g in gs) for j in range(3)]
assert lo==F(33,38) and hi==F(31,19) and min(mins)>=0 and max(maxs)==F(881,380)
for init in (lo,(lo+hi)/2,hi):
    l=u=init
    for _ in range(100):
        assert min(rho**j*l+min(g[j] for g in gs) for j in range(3))>=0
        assert max(rho**j*u+max(g[j] for g in gs) for j in range(3))<=F(881,380)
        l=a*l+min(r);u=a*u+max(r)
results['T5_rational_example']={'rho':'9/10','p':['27/10','27/10'],'residual_LH':'33/200','residual_HL':'31/100','stationary_l':'33/38','stationary_u':'31/19','W_infinity':'29/38','B':'881/380','100_block_exact_checks_for_three_initial_states':True}

# T5: independently formulate invariant interval LP and compare to exact hull.
def leaky_lp(words,rho,pbounds=None):
    n=len(words[0]);a=rho**n;nv=n+3;li=n;ui=n+1;bi=n+2
    A=[];b=[]
    row=np.zeros(nv);row[li]=1;row[ui]=-1;A.append(row);b.append(0.)
    for w in words:
        g,c=prefixes(w,rho)
        for j in range(n+1):
            row=np.zeros(nv);row[:n]=-g[j];row[li]=-rho**j;A.append(row);b.append(c[j])
            row=np.zeros(nv);row[:n]=g[j];row[ui]=rho**j;row[bi]=-1;A.append(row);b.append(-c[j])
        row=np.zeros(nv);row[:n]=-g[-1];row[li]=1-a;A.append(row);b.append(c[-1])
        row=np.zeros(nv);row[:n]=g[-1];row[ui]=-(1-a);A.append(row);b.append(-c[-1])
    objective=np.zeros(nv);objective[bi]=1
    return linprog(objective,A_ub=A,b_ub=b,bounds=(pbounds or [(L,H)]*n)+[(0,None)]*3,method='highs')
fixed_lp=leaky_lp(words,.9,[(2.7,2.7)]*2)
assert fixed_lp.success and abs(fixed_lp.fun-float(F(881,380)))<1e-8
opt_lp=leaky_lp(words,.9);assert opt_lp.success
results['T5_invariant_interval_LP']={'fixed_p_capacity':float(fixed_lp.fun),'unrestricted_p_optimum':float(opt_lp.fun),'optimal_p':opt_lp.x[:2].tolist(),'optimal_interval':opt_lp.x[2:4].tolist()}
# Grid-check LP feasibility and optimum against the independently computed hull.
feasible_grid=0;infeasible_grid=0
for p in product(np.linspace(1.,3.,13),repeat=2):
    dat=[prefixes(w,.9) for w in words]
    rr=[g[-1]@p+c[-1] for g,c in dat]
    lower=min(rr)/.19;upper=max(rr)/.19
    lowest=min(.9**j*lower+min(g[j]@p+c[j] for g,c in dat) for j in range(3))
    highest=max(.9**j*upper+max(g[j]@p+c[j] for g,c in dat) for j in range(3))
    lp=leaky_lp(words,.9,[(x,x) for x in p])
    if lowest>=-1e-8:
        feasible_grid+=1;assert lp.success and abs(lp.fun-highest)<1e-7
    else:
        infeasible_grid+=1;assert not lp.success
results['T5_grid_hull_vs_LP']={'feasible':feasible_grid,'infeasible':infeasible_grid,'all_match':True}

# Exact assumption-failure examples. These are outside the stated contract.
# Nonconvex P: alternate constant p=5/2 and constant p=27/10.
ps=[[F(5,2)]*2,[F(27,10)]*2];e0=F(1);B=F(7,4)
current=[e0]
for p in ps:
    nextstates=[]
    for e in current:
        for w in words:
            g=fg(w,p);assert all(0<=e+x<=B for x in g);nextstates.append(e+g[-1])
    current=sorted(set(nextstates))
assert current==[e0]
assert all(fg(w,ps[0])[-1]==F(-1,4) and fg(w,ps[1])[-1]==F(1,4) for w in words)
results['outside_contract_nonconvex_P']={'P':['(5/2,5/2)','(27/10,27/10)'],'B_star':'infinity','alternating_schedule_B':'7/4','common_e0':'1','verified':True}
# Private-history-dependent initial state beats the stronger T1 bound.
# First p=(12/5,14/5), then q; initial state is 3/5 for LH, 6/5 for HL.
p=[F(12,5),F(14,5)];B=F(17,10);center=F(9,10)
for w,e in zip(words,(F(3,5),F(6,5))):
    g=fg(w,p);assert all(0<=e+x<=B for x in g);assert e+g[-1]==center
for w in words:assert all(0<=center+x<=B for x in fg(w,[F(13,5)]*2))
assert B<F(8,5)+F(3,5)
results['outside_contract_private_initial_state']={'first_p':['12/5','14/5'],'later_p':['13/5','13/5'],'e0_LH':'3/5','e0_HL':'6/5','B':'17/10','B_star_plus_W':'11/5','verified':True}
results['all_checks_passed']=True
(OUT/'independent_theory_checks.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({k:v for k,v in results.items() if k!='T1_tiny_families'},indent=2))
