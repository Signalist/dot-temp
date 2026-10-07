#!/usr/bin/env python3
"""Original, deterministic exact-arithmetic validation of stochastic admission.
No external packages, downloaded code, simulation, or fitted data are used.
The frozen JSON is read before any results are produced.
"""
from pathlib import Path
from fractions import Fraction
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / 'FROZEN_STOCHASTIC_PROTOCOL.json'
protocol = json.loads(PROTOCOL.read_text())


def integer_probabilities(case):
    from math import lcm
    initial = [Fraction(x) for x in case['initial']]
    transition = [[Fraction(x) for x in row] for row in case['transition']]
    d = lcm(*(x.denominator for x in initial + sum(transition, [])))
    return d, [int(x*d) for x in initial], [[int(x*d) for x in row] for row in transition]


def enumerate_numeric_states(L, nmax, initial, transition):
    """Direct LTI tree enumeration, with a separate pathwise run comparator.
    State y_n=m/2**n obeys m_new=m+s*2**n. Safety uses integer
    cross multiplication of |g_L*y|<=1, never any pattern assumption.
    Integer path weights give independent exact survival numerators.
    """
    survival = [0]*(nmax+1)
    survival[0] = 1
    compared = 0
    boundary = 0
    mismatches = 0
    g_num = 2**(L-1)
    g_den = g_num-1

    def visit(n, m, prev, weight, survived, run, pattern_survived):
        nonlocal compared, boundary, mismatches
        if n == nmax:
            return
        for index, sign in enumerate((-1, 1)):
            m2 = m+sign*2**n
            n2 = n+1
            w2 = weight*(initial[index] if prev is None else transition[prev][index])
            lhs, rhs = abs(m2)*g_num, 2**n2*g_den
            ok = survived and lhs <= rhs
            newrun = run+1 if index == prev else 1
            pok = pattern_survived and newrun < L
            compared += 1
            boundary += (lhs == rhs)
            mismatches += (ok != pok)
            if ok:
                survival[n2] += w2
            visit(n2, m2, index, w2, ok, newrun, pok)
    visit(0, 0, None, 1, True, 0, True)
    return survival, compared, boundary, mismatches


def run_avoidance(L, nmax, initial, transition):
    """Independent finite automaton with states (last sign, run length)."""
    states = {}
    survival = [1]
    for n in range(1, nmax+1):
        nxt = {}
        if n == 1:
            nxt = {(s, 1): initial[s] for s in (0, 1)}
        else:
            for (prev, run), weight in states.items():
                for sign in (0, 1):
                    rr = run+1 if sign == prev else 1
                    if rr < L:
                        key = (sign, rr)
                        nxt[key] = nxt.get(key, 0)+weight*transition[prev][sign]
        states = nxt
        survival.append(sum(states.values()))
    return survival


def bounds(L, initial, transition, d):
    a = [Fraction(x, d) for x in initial]
    P = [[Fraction(x, d) for x in row] for row in transition]
    q0 = sum(a[s]*P[s][s]**(L-1) for s in (0, 1))
    qp = [sum(P[p][s]*P[s][s]**(L-1) for s in (0, 1)) for p in (0, 1)]
    return min([q0]+qp)


def fraction_record(f):
    return {'exact': str(f), 'decimal': float(f)}


def main():
    nmax = max(protocol['mission_lengths_exhaustive'])
    dynamic_max = max(protocol['mission_lengths_dynamic'])
    records, rows = [], []
    total_compared = total_boundary = 0
    for case in protocol['cases']:
        d, alpha, P = integer_probabilities(case)
        for L in protocol['run_lengths_L']:
            direct, count, boundary, mismatches = enumerate_numeric_states(L, nmax, alpha, P)
            automaton = run_avoidance(L, dynamic_max, alpha, P)
            assert not mismatches, (case['name'], L, mismatches)
            assert direct == automaton[:nmax+1], (case['name'], L)
            total_compared += count
            total_boundary += boundary
            q = bounds(L, alpha, P, d)
            entries = []
            for N in sorted(set(protocol['mission_lengths_exhaustive']+protocol['mission_lengths_dynamic'])):
                survival = Fraction(automaton[N], d**N)
                upper = (1-q)**(N//L)
                assert survival <= upper, (case['name'], L, N)
                entries.append({'N': N, 'survival': fraction_record(survival),
                                'disjoint_word_upper': fraction_record(upper),
                                'independently_enumerated': N <= nmax})
                rows.append({'case':case['name'], 'L':L, 'gain':str(Fraction(2**(L-1),2**(L-1)-1)),
                             'N':N, 'survival':float(survival), 'survival_exact':str(survival),
                             'disjoint_word_upper':float(upper), 'independent_enumeration':N<=nmax})
            records.append({'case':case['name'],'L':L,'word_probability_lower':str(q),
                            'path_prefixes_checked':count,'boundary_equalities_checked':boundary,
                            'path_classification_mismatches':mismatches,'missions':entries})
    out = {'protocol_sha256':hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
           'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'method':'exact integer state tree and independent integer weighted run automaton',
           'all_checks_passed':True,'random_draws':0,'total_path_prefixes_checked':total_compared,
           'total_boundary_equalities_checked':total_boundary,'records':records}
    (ROOT/'RESULTS.json').write_text(json.dumps(out, indent=2)+'\n')
    with (ROOT/'FINITE_MISSION_SUMMARY.csv').open('w',newline='') as fh:
        w = csv.DictWriter(fh,fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(json.dumps({k:v for k,v in out.items() if k != 'records'},indent=2))
    for row in rows:
        if row['L']==3 and row['N'] in (3,10,20,50,100,1000):
            print({k:v for k,v in row.items() if k != 'survival_exact'})

if __name__ == '__main__':
    main()
