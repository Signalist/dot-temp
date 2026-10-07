"""Original G6 theory sanity checks. Proofs are in the accompanying markdown.

No downloaded implementation is used. Floating-point checks are not proofs of
irrationality, asymptotic complexity, or continuum-wide physical safety.
"""
from __future__ import annotations

import itertools
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.integrate import quad_vec, solve_ivp

HERE = Path(__file__).resolve().parent


def coefficients(r: float, theta: float, n: int = 800):
    k = np.arange(n)
    return r**k, np.column_stack((np.cos(k * theta), -np.sin(k * theta)))


def gauges(r: float, theta: float, points, n: int = 800):
    points = np.atleast_2d(points)
    w, u = coefficients(r, theta, n)
    f = w @ np.abs(u @ points.T)
    axis = w @ np.abs(u)
    h = (f + points @ axis) / 2
    return f, h, axis


def finite_enumeration():
    r, theta, a, n = 0.7, 1.2, np.array([0.4, 0.65]), 5
    w, u = coefficients(r, theta, n)
    expected_f = float(w @ np.abs(u @ a))
    fixed_outputs = [sum(w[j] * (u[j] @ a) * s[j] for j in range(n))
                     for s in itertools.product((-1, 1), repeat=n)]
    vertices = np.array([a, -a, [a[0], 0], [-a[0], 0],
                         [0, a[1]], [0, -a[1]]])
    var_outputs = [sum(w[j] * (u[j] @ vertices[idx[j]]) for j in range(n))
                   for idx in itertools.product(range(6), repeat=n)]
    expected_h = float(sum(w[j] * np.max(np.abs(vertices @ u[j])) for j in range(n)))
    identity_h = (expected_f + float(a @ (w @ np.abs(u)))) / 2
    assert abs(max(map(abs, fixed_outputs)) - expected_f) < 1e-13
    assert abs(max(map(abs, var_outputs)) - expected_h) < 1e-13
    assert abs(expected_h - identity_h) < 1e-13
    return dict(horizon=n, fixed_bruteforce=max(map(abs, fixed_outputs)),
                fixed_formula=expected_f,
                dynamic_bruteforce=max(map(abs, var_outputs)),
                dynamic_formula=expected_h, hexagon_identity=identity_h)


def rectangle_checks():
    r, theta = 0.9, 0.01
    _, _, c = gauges(r, theta, [[1, 1]])
    q = float(gauges(r, theta, [1 / c])[0][0])
    rq, tq = Fraction(9, 10), Fraction(1, 100)
    c1, c2 = 1 / (1 - rq), rq / (1 - rq)**2
    d1 = tq**2 * rq * (1 + rq) / (2 * (1 - rq)**3)
    d2 = tq**2 * rq * (1 + 4 * rq + rq * rq) / (6 * (1 - rq)**4)
    limit = 2 * 10 * (1 - rq) * rq**9
    bound = limit + 2 * d1 / (c1 - d1) + 2 * d2 / (c2 - d2)
    assert bound < 1 and q < float(bound)
    low_r_checks = []
    for rr in [0.05, 0.25, 0.5]:
        for tt in [0.001, 0.1, 0.7, 1.2, 2.8]:
            _, _, cc = gauges(rr, tt, [[1, 1]])
            qq = float(gauges(rr, tt, [1 / cc])[0][0])
            assert qq > 1 and qq + 1e-12 >= 2 / cc[0]
            low_r_checks.append(dict(r=rr, theta=tt, Q=qq, lower=2 / cc[0]))
    high_r_checks = []
    for rr in [0.51, 0.6, 0.75, 0.9]:
        tt = 1e-4
        _, _, cc = gauges(rr, tt, [[1, 1]], 1500)
        qq = float(gauges(rr, tt, [1 / cc], 1500)[0][0])
        nn = math.floor(rr / (1 - rr) + 1e-12)
        lr = 2 * (nn + 1) * (1 - rr) * rr**nn
        assert qq < 1 and abs(qq - lr) < 1e-5
        high_r_checks.append(dict(r=rr, theta=tt, Q=qq, limit=lr))
    return dict(analytic_case=dict(r=r, theta=theta, c1=c[0], c2=c[1], Q=q,
                                  exact_rational_upper=str(bound), upper=float(bound),
                                  dynamic_corner=1 + q / 2),
                low_memory_grid=low_r_checks, small_angle_grid=high_r_checks)


def approximation_checks():
    points = np.column_stack((np.ones(2001), np.linspace(0.15, 4.0, 2001)))
    results = []
    for r, theta, q in [(0.9, math.pi * (math.sqrt(5) - 1) / 2, 34),
                        (0.9, math.pi / 7 + 1e-8, 7),
                        (0.7, 1.2, 8)]:
        f, h, _ = gauges(r, theta, points)
        w, u = coefficients(r, theta, q)
        fq = (w @ np.abs(u @ points.T)) / (1 - r**q)
        axisq = (w @ np.abs(u)) / (1 - r**q)
        hq = (fq + points @ axisq) / 2
        delta = abs(q * theta - round(q * theta / math.pi) * math.pi)
        tau = delta * r**q / ((1 - r) * (1 - r**q))
        euclidean_bound = np.linalg.norm(points, axis=1) * tau
        assert np.all(np.abs(f - fq) <= euclidean_bound + 1e-12)
        assert np.all(np.abs(h - hq) <= euclidean_bound + 1e-12)
        assert np.all(f <= fq + tau * points.sum(axis=1) + 1e-12)
        assert np.all(h <= hq + tau * points.sum(axis=1) + 1e-12)
        results.append(dict(r=r, theta=theta, q=q, return_angle=delta,
                            max_fixed_error=float(np.max(np.abs(f - fq))),
                            max_dynamic_error=float(np.max(np.abs(h - hq))),
                            max_bound=float(np.max(euclidean_bound))))
    # A kink's second difference cannot be canceled by all other summands.
    r, theta = 0.7, math.pi * (math.sqrt(5) - 1) / 2
    kinks = []
    for k in range(1, 30):
        t = math.cos(k * theta) / math.sin(k * theta)
        if 0.2 < t < 3:
            d = 1e-5
            f, h, _ = gauges(r, theta, [[1, t-d], [1, t], [1, t+d]])
            df, dh = float(f[0] - 2*f[1] + f[2]), float(h[0] - 2*h[1] + h[2])
            selected = 2*r**k*abs(math.sin(k*theta))*d
            assert df + 2e-14 >= selected and dh + 2e-14 >= selected/2
            kinks.append(dict(k=k, slope=t, fixed_second_difference=df,
                              selected_kink_lower=selected,
                              dynamic_second_difference=dh))
    return dict(folding=results, noncancellation=kinks)


def physical_templates(r: float, theta: float):
    lam, omega = -math.log(r), theta
    ac = np.array([[-lam, -omega], [omega, -lam]])

    def impulse(t):
        z = 1-t
        return math.exp(-lam*z)*np.array([math.cos(omega*z), math.sin(omega*z)])

    mean, _ = quad_vec(impulse, 0, 1, epsabs=1e-12, epsrel=1e-12)
    gram, _ = quad_vec(lambda t: np.outer(impulse(t)-mean, impulse(t)-mean),
                       0, 1, epsabs=1e-12, epsrel=1e-12)
    inv = np.linalg.inv(gram)

    def templates(t):
        return (impulse(t)-mean) @ inv

    area, _ = quad_vec(templates, 0, 1, epsabs=1e-10, epsrel=1e-12)
    bmatrix, _ = quad_vec(lambda t: np.outer(impulse(t), templates(t)),
                          0, 1, epsabs=1e-10, epsrel=1e-12)
    assert np.max(np.abs(area)) < 1e-7
    assert np.max(np.abs(bmatrix-np.eye(2))) < 1e-7
    sampled_peaks = np.max(np.abs(np.array([templates(t) for t in np.linspace(0, 1, 20001)])), axis=0)
    # Norm-based analytic upper bound on peaks, independent of time sampling.
    peak_upper = (1 + np.linalg.norm(mean)) * np.linalg.norm(inv, axis=0)
    result = dict(r=r, theta=theta, zero_area_residual=area.tolist(),
                  sampled_B=bmatrix.tolist(), gram_condition=float(np.linalg.cond(gram)),
                  sampled_abs_peaks=sampled_peaks.tolist(),
                  analytic_norm_bound_evaluated_numerically=peak_upper.tolist())
    if theta > 0.1:
        rng = np.random.default_rng(17)
        state = np.zeros(2)
        expected = np.zeros(2)
        ar = r*np.array([[math.cos(theta), -math.sin(theta)],
                         [math.sin(theta), math.cos(theta)]])
        endpoint_errors = []
        for _ in range(25):
            b = rng.uniform(0, 0.2, 2)
            sign = rng.choice([-1, 1])
            # Both scalar physical ports share g=e1; their different templates
            # yield the two distinct sampled columns.
            sol = solve_ivp(lambda t, x: ac@x + np.array([sign*(templates(t)@b), 0]),
                            (0, 1), state, rtol=2e-11, atol=2e-12)
            state = sol.y[:, -1]
            expected = ar@expected + sign*b
            endpoint_errors.append(float(np.max(np.abs(state-expected))))
        assert max(endpoint_errors) < 1e-8
        result['carried_state_blocks'] = 25
        result['max_carried_state_recurrence_error'] = max(endpoint_errors)
    return result


def main():
    results = dict(status='passed', caveat='Finite floating-point sanity tests; proofs are separate.',
                   finite_horizon=finite_enumeration(),
                   rectangle_threshold=rectangle_checks(),
                   approximation=approximation_checks(),
                   physical=[physical_templates(0.7, 1.2), physical_templates(0.9, 0.01)])
    dest = HERE / 'THEORY_CHECK_RESULTS.json'
    dest.write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(dict(status=results['status'], output=str(dest),
                          finite_horizon=results['finite_horizon'],
                          rectangle=results['rectangle_threshold']['analytic_case'],
                          physical=results['physical']), indent=2))


if __name__ == '__main__':
    main()
