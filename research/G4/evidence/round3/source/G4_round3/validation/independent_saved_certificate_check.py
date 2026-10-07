#!/usr/bin/env python3
"""Validate saved certificates against a new Fraction-only scenario model.
Does not import any producer code or use producer rational_check.
"""
from fractions import Fraction as F
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'experiments/dag_results.json'
boundary_source=ROOT/'experiments/boundary_results.json'
records=json.loads(source.read_text())+json.loads(boundary_source.read_text())['public_pattern_transfer']

def words_and_swaps(labels,edges):
    n=len(labels);pre=[set() for _ in range(n)]
    for x,y in edges:pre[y].add(x)
    words=set();swaps=set();orders=0
    def visit(order,remaining):
        nonlocal orders
        if not remaining:
            orders+=1;words.add(tuple(labels[x] for x in order))
            for t in range(n-1):
                a,b=order[t:t+2]
                # An adjacent topological pair is incomparable iff its reverse
                # also obeys all original precedence edges.
                if labels[a]==labels[b]:continue
                alternate=order[:t]+[b,a]+order[t+2:]
                pos={x:j for j,x in enumerate(alternate)}
                if all(pos[x]<pos[y] for x,y in edges):swaps.add(t)
            return
        done=set(order)
        for v in sorted(remaining):
            if pre[v]<=done:visit(order+[v],remaining-{v})
    visit([],set(range(n)))
    return sorted(words),sorted(swaps),orders

def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))

checks=[]
for record in records:
    labels=record['labels'];edges=record['edges'];eta=F(str(record['eta']));n=len(labels)
    words,swaps,orders=words_and_swaps(labels,edges)
    assert len(words)==record['word_count']
    assert swaps==record['swap_boundaries_zero_based']
    cert=record['exact_certificate'];x=list(map(F,cert['x_fraction']));p=x[:n];z=x[n];B=x[n+1]
    assert len(x)==n+2 and all(6<=q<=18 for q in p) and 0<=z<=B
    ub=[];ubr=[];eq=[];eqr=[];energies=[]
    for w in words:
        energy=z;energies.append(energy);coeff=[F(0)]*n;constant=F(0)
        for j in range(n+1):
            # Direct physical primal evaluation separate from matrix rows.
            assert 0<=energy<=B
            lower=[-q for q in coeff]+[F(-1),F(0)]
            upper=coeff[:]+[F(1),F(-1)]
            ub += [lower,upper];ubr += [constant,-constant]
            if j<n:
                slope=eta if w[j]==0 else 1/eta
                offset=-eta*6 if w[j]==0 else -F(18)/eta
                coeff[j]=slope;constant+=offset
                energy+=slope*p[j]+offset;energies.append(energy)
        assert energy==z
        eq.append(coeff+[F(0),F(0)]);eqr.append(-constant)
    assert all(dot(a,x)<=b for a,b in zip(ub,ubr))
    assert all(dot(a,x)==b for a,b in zip(eq,eqr))
    # Saved sparse dual uses SciPy value sensitivities, i.e. <= rows have y<=0.
    station=[F(0)]*(n+2);objective=F(0)
    for kind,items in cert['dual_nonzero'].items():
        for index,value in items:
            value=F(value)
            if kind in ('ineq','upper'):assert value<=0
            if kind=='lower':assert value>=0
            if kind in ('ineq','eq'):
                rows,rhs=(ub,ubr) if kind=='ineq' else (eq,eqr)
                row=rows[index];objective+=value*rhs[index]
                station=[a+value*b for a,b in zip(station,row)]
            elif kind=='lower':
                station[index]+=value;objective+=value*(6 if index<n else 0)
            elif kind=='upper':
                assert index<n
                station[index]+=value;objective+=value*18
            else:raise AssertionError(kind)
    assert station==[F(0)]*(n+1)+[F(1)]
    assert objective==B==F(cert['capacity_fraction'])==F(cert['dual_fraction'])
    a=[min(sum(w[:j]) for w in words) for j in range(n+1)]
    b=[max(sum(w[:j]) for w in words) for j in range(n+1)]
    assert a==record['prefix_high_min'] and b==record['prefix_high_max']
    checks.append({'name':record['name'],'eta':str(eta),'word_count':len(words),'linear_extension_count':orders,'capacity':str(B),'initial':str(z),'p':list(map(str,p)),'minimum_primal_energy':str(min(energies)),'maximum_primal_energy':str(max(energies)),'primal_exact':True,'dual_exact':True,'zero_gap_exact':True,'slot_graph_independently_rebuilt':True})

result={'source':'experiments/dag_results.json','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'boundary_source':'experiments/boundary_results.json/public_pattern_transfer','boundary_source_sha256':hashlib.sha256(boundary_source.read_bytes()).hexdigest(),'method':'Independent topological-permutation enumeration; Fraction-only physical primal check and scenario dual stationarity/objective; no producer imports','records_checked':len(checks),'all_passed':True,'records':checks}
(ROOT/'validation/independent_saved_certificate_check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
for row in checks:
    if row['eta']=='19/20' and row['name'] in ('antichain_6','connected_restricted_6','barriers_3plus3'):print(json.dumps(row))
