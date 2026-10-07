"""Exact-event diagnostic for the Gate C scalar storage audit; no Euler resets."""
import cmath
import json
import math
from pathlib import Path

ETA_C = ETA_D = 0.95
U_H, U_L, TAU_H, TAU_L = 12.0, 8.0, 5.0, 5.0
T = TAU_H + TAU_L
R = (TAU_H * U_H + ETA_C * ETA_D * TAU_L * U_L) / (
    TAU_H + ETA_C * ETA_D * TAU_L
)
D, C = U_H - R, R - U_L
A, B_RATE = D / ETA_D, ETA_C * C
S = A * TAU_H


def cycle(e, cap, reference=R):
    """Return end energy and exact constant-power segments; units MW, s, MJ."""
    d, c = min(3.0, U_H - reference), min(3.0, reference - U_L)
    a, b = d / ETA_D, ETA_C * c
    initial = e
    th = min(TAU_H, e / a) if a else TAU_H
    e -= a * th
    e = max(0.0, e)
    tl = min(TAU_L, (cap - e) / b) if b else TAU_L
    segments = [(0.0, th, U_H - d, U_H, 0.0, d),
                (th, TAU_H, U_H, U_H, 0.0, 0.0),
                (TAU_H, TAU_H + tl, U_L + c, U_L, c, 0.0),
                (TAU_H + tl, T, U_L, U_L, 0.0, 0.0)]
    e += b * tl
    pcc_energy = sum((v-u)*p for u,v,p,_,_,_ in segments)
    load_energy = sum((v-u)*p for u,v,_,p,_,_ in segments)
    loss = sum((v-u)*((1-ETA_C)*c_ + (1/ETA_D-1)*d_)
               for u,v,_,_,c_,d_ in segments)
    residual = pcc_energy - load_energy - (e-initial) - loss
    assert abs(residual) < 1e-11, residual
    assert -1e-12 <= e <= cap + 1e-12
    return e, segments, residual


def harmonic(segments):
    w = 2*math.pi/T
    return abs(sum(2/T*p*(cmath.exp(-1j*w*v)-cmath.exp(-1j*w*u))/(-1j*w)
                   for u,v,p,_,_,_ in segments))


def value(segments, t):
    for u,v,p,_,_,_ in segments:
        if u <= t < v:
            return p
    raise ValueError(t)


def F(x, capacity, h, ell):
    return min(capacity, max(0.0, x-h)+ell)


def soft_bound_checks():
    from scipy.integrate import quad
    from scipy.optimize import brentq
    eta = 0.95
    u = lambda s: 10+2*math.tanh(3*math.cos(2*math.pi*s))

    def integrals(pref):
        z = math.acos(math.atanh((pref-10)/2)/3)/(2*math.pi)
        ip = 2*quad(lambda s: u(s)-pref, 0, z, epsabs=1e-12)[0]
        im = quad(lambda s: pref-u(s), z, 1-z, epsabs=1e-12)[0]
        return ip, im

    pref = brentq(lambda p: integrals(p)[0]/eta-eta*integrals(p)[1],
                  10,10.2,xtol=1e-13)
    ip, im = integrals(pref)
    u0 = u(0)
    cmd = u0-pref
    low = u0-cmd*0.01/(0.01+0.05)
    high = u0-cmd*0.5/(0.5+0.05)
    result = dict(
        Pref_MW=pref,
        u0_MW=u0,
        maximum_abs_command_MW=max(u0-pref,pref-(20-u0)),
        ideal_R_MJ_by_frequency={str(f):ip/(eta*f) for f in [0.25,0.5,0.75]},
        pcc_low_initial_MW=low,
        pcc_high_initial_MW=high,
        PCC_bit_threshold_MW=pref+0.5,
        PCC_bit_minimum_margin_MW=min(low-pref-0.5,pref+0.5-high),
        energy_bit_initial_values=[True,False],
        PCC_bit_initial_values=[low>pref+0.5,high>pref+0.5],
        PCC_bit_equivalent_energy_fraction=0.05*(cmd-0.5)/0.5,
        exactly_matched_PCC_threshold_for_E_point1C_MW=u0-cmd*0.1/0.15,
        contraction_bounds=[],
    )
    for ratio in [0.5,2,20]:
        k = 0.1/(1.05**2*ratio)
        result['contraction_bounds'].append(dict(C_over_R=ratio,K=k,
                                                q_bound=math.exp(-k),
                                                q_power_200=math.exp(-200*k)))
    Path(__file__).with_name('SOFT_BUFFER_BOUND_CHECKS.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


def soft_first_cycle_check(bounds):
    import numpy as np
    from scipy.integrate import solve_ivp
    pref, period, eta = bounds['Pref_MW'], 2.0, 0.95
    demand = bounds['ideal_R_MJ_by_frequency']['0.5']
    result = []
    for ratio in [0.5,2,20]:
        capacity = ratio*demand
        es = 0.05*capacity

        def rhs(t,z):
            u = 10+2*np.tanh(3*np.cos(2*np.pi*t/period))
            cc, dc = max(pref-u,0), max(u-pref,0)
            e = z[:2]  # Deliberately do not clip the energy state in this independent check.
            c, d = cc*(capacity-e)/(capacity-e+es), dc*e/(e+es)
            p = u+c-d
            return np.r_[eta*c-d/eta, 2/period*p*np.cos(2*np.pi*t/period),
                         -2/period*p*np.sin(2*np.pi*t/period)]

        sol = solve_ivp(rhs,[0,period],[0.01*capacity,0.5*capacity,0,0,0,0],
                        method='DOP853',rtol=1e-11,atol=1e-12,max_step=period/200)
        assert sol.success
        assert sol.y[:2].min() >= 0 and sol.y[:2].max() <= capacity
        z = sol.y[:,-1]
        coeff = z[2:4]+1j*z[4:6]
        amp = np.abs(coeff)
        gap_initial = 0.49*capacity
        gap_final = z[1]-z[0]
        fourier_difference = float(abs(coeff[0]-coeff[1]))
        energy_budget_bound = 2*(gap_initial-gap_final)/(eta*period)
        assert fourier_difference <= energy_budget_bound + 1e-10
        result.append(dict(C_over_R=ratio,first_cycle_amplitude_MW=amp.tolist(),
                           support_world_A=np.flatnonzero(amp>0.5).tolist(),
                           end_E_MJ=z[:2].tolist(),solver_success=sol.success,
                           complex_Fourier_difference_MW=fourier_difference,
                           Fourier_difference_energy_budget_bound_MW=energy_budget_bound,
                           unclipped_energy_range_MJ=[float(sol.y[:2].min()),float(sol.y[:2].max())]))
    Path(__file__).with_name('SOFT_BUFFER_FIRST_CYCLE_AUDIT.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


def main():
    cap = 2*S
    alpha, beta = 0.2*S, 1.5*S
    ea, eb = alpha, beta
    rows = []
    for k in range(5):
        ea, sa, ra = cycle(ea, cap)
        eb, sb, rb = cycle(eb, cap)
        rows.append(dict(cycle=k+1, low_end_MJ=ea, high_end_MJ=eb,
                         low_harmonic_MW=harmonic(sa), high_harmonic_MW=harmonic(sb)))
        for j in range(1001):
            t = (j+0.25)/1001*T
            # Swapping entire continuous trajectories preserves aggregate PCC.
            assert value(sa,t)+value(sb,t) == value(sb,t)+value(sa,t)
        if k:
            assert harmonic(sa) < 1e-12 and harmonic(sb) < 1e-12
    formula = 2*D/math.pi*math.sin(math.pi*4/T)
    assert abs(rows[0]['low_harmonic_MW'] - formula) < 1e-12
    rho = 0.5
    ecrit = A*(TAU_H - T/math.pi*math.asin(math.pi*rho/(2*D)))
    _, sa, _ = cycle(0.2*S, cap)
    _, sb, _ = cycle(0.95*S, cap)
    assert harmonic(sa) > rho > harmonic(sb)
    assert abs(cycle(0.2*S,cap)[0]-cycle(0.95*S,cap)[0]) < 1e-12

    small_cap = 0.5*S
    e1, e2 = 0.1*small_cap, 0.9*small_cap
    e1, _, _ = cycle(e1,small_cap)
    e2, _, _ = cycle(e2,small_cap)
    assert abs(e1-e2) < 1e-12
    _, steady_small, _ = cycle(e1,small_cap)
    small_amp_formula = 2*(D+C)/math.pi*math.sin(math.pi/4)
    assert abs(harmonic(steady_small)-small_amp_formula) < 1e-12

    # Deterministic sweep verifies the stated finite-time map bound, not hardware.
    map_cases = 0
    for capacity in [0.1,0.5,1,2,5,10]:
        for h in [0,0.2,1,2,4]:
            for ell in [0,0.2,1,2,4]:
                for frac in [0,0.01,0.2,0.5,0.9,1]:
                    x = capacity*frac
                    if ell > h:
                        bound = 1+math.ceil(max(0,capacity-ell)/(ell-h))
                        target = capacity
                    elif ell < h:
                        bound = 1+math.ceil(max(0,capacity-h)/(h-ell))
                        target = min(capacity,ell)
                    else:
                        bound = 1
                        target = min(capacity,max(x,h))
                    for _ in range(bound):
                        x = F(x,capacity,h,ell)
                    assert abs(x-target) < 1e-10, (capacity,h,ell,frac,bound,x,target)
                    map_cases += 1

    h0 = (U_H-10)/ETA_D*TAU_H
    l0 = ETA_C*(10-U_L)*TAU_L
    kbound = 1+math.ceil(max(0,cap-h0)/(h0-l0))
    e = cap
    unbalanced = []
    for k in range(kbound+1):
        old = e
        e, ss, _ = cycle(e,cap,reference=10)
        unbalanced.append(dict(cycle=k+1,start_MJ=old,end_MJ=e,harmonic_MW=harmonic(ss)))
    assert abs(e-l0) < 1e-12

    result = dict(
        units='MW, seconds, MJ; a1=(2/T) integral p(t) exp(-i omega t) dt',
        loss_compensated_reference_MW=R, charge_MW=C, discharge_MW=D,
        stored_rate_MW=A, required_energy_MJ=S, required_energy_kWh=S/3.6,
        sufficient_capacity_MJ=cap, initial_energy_pair_MJ=[alpha,beta],
        first_saturation_time_s=alpha/A, balanced_pair_cycles=rows,
        threshold_MW=rho, threshold_initial_energy_MJ=ecrit,
        threshold_time_s=ecrit/A,
        late_energy_alias_pair=dict(initial_MJ=[0.2*S,0.95*S],
                                   first_cycle_harmonic_MW=[harmonic(sa),harmonic(sb)],
                                   shared_end_MJ=S),
        insufficient_capacity_MJ=small_cap,
        insufficient_capacity_steady_harmonic_MW=harmonic(steady_small),
        phase_map_cases_passed=map_cases,
        uncompensated_reference_MW=10,
        uncompensated_H_MJ=h0, uncompensated_L_MJ=l0,
        uncompensated_worst_case_state_washout_cycles=kbound,
        uncompensated_cycles=unbalanced,
        evidence_status='synthetic exact-event model diagnostic; not field validation',
    )
    path=Path(__file__).with_name('BUFFER_MODEL_AUDIT_CHECKS.json')
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    bounds = soft_bound_checks()
    print(json.dumps(bounds,ensure_ascii=False,indent=2))
    print(json.dumps(soft_first_cycle_check(bounds),ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
