"""Original G6 implementations of classical support and finite-state DP.

No solver novelty claim. Floating numerical experiments, not interval arithmetic.
For unconstrained signs support prefixes are monotone. For run-limited signs
they need not be: retain every startup prefix, never silently replace by RPI.
"""
import numpy as np
from scipy.linalg import eig, solve


def rotation(theta):
    return np.array([[np.cos(theta), -np.sin(theta)],
                     [np.sin(theta), np.cos(theta)]])


def sign_support(weights, max_run=None, keep_prefix=False):
    """weights [..., time]. Joint common sign; language reversible max-run."""
    w = np.asarray(weights)
    if max_run is None:
        pref = np.cumsum(abs(w), axis=-1)
    else:
        shape = w.shape[:-1]
        d = np.full(shape + (2, max_run), -np.inf)
        d[..., 0, 0], d[..., 1, 0] = -w[..., 0], w[..., 0]
        ps = [d.max(axis=(-2, -1))]
        for k in range(1, w.shape[-1]):
            n = np.full_like(d, -np.inf)
            for si, s in enumerate([-1, 1]):
                n[..., si, 0] = d[..., 1-si, :].max(axis=-1) + s*w[..., k]
                if max_run > 1:
                    n[..., si, 1:] = d[..., si, :-1] + s*w[..., k, None]
            d = n
            ps.append(d.max(axis=(-2, -1)))
        pref = np.stack(ps, axis=-1)
    return pref if keep_prefix else pref[..., -1]


def all_startup_support(weights, max_run=None):
    return sign_support(weights, max_run, True).max(axis=-1)


def modal_kernel(A, B, C):
    lam, V = eig(A)
    beta = solve(V, B)
    cv = C @ V
    return lam, beta, cv, np.linalg.cond(V)


def integrate_template(lam, T, qs, tau):
    """Modal state at tau under one piecewise-constant unit block, zero start.
    qs shape (segments,ports); return (modes,ports).
    """
    qs = np.asarray(qs)
    out = np.zeros((len(lam), qs.shape[1]), complex)
    edges = np.linspace(0, T, len(qs)+1)
    for k, q in enumerate(qs):
        l, h = edges[k], min(edges[k+1], tau)
        if h <= l:
            continue
        duration = h-l
        integ = np.where(abs(lam)>1e-13, np.expm1(lam*duration)/lam, duration)
        out += (np.exp(lam*(tau-h))*integ)[:, None] * q
    return out


def lifted_weights(lam, beta, cv, T, qs, phases, N):
    """Return [output,phase,port,current+N past-block coefficients]."""
    block = beta * integrate_template(lam, T, qs, T)
    powers = np.exp(lam[:, None] * T * np.arange(N)[None, :])
    allw = []
    for tau in phases:
        direct = cv @ (beta * integrate_template(lam, T, qs, tau))
        history = np.einsum('om,mi,mn,m->oin', cv, block, powers, np.exp(lam*tau))
        allw.append(np.concatenate([direct.real[..., None], history.real], axis=-1))
    return np.stack(allw, axis=1), block


def modal_tail(lam, block, cv, T, N):
    """Uniform phase tail for stable modes, output x port. Numerical analytic bound."""
    rr = np.exp(lam.real*T)
    if np.any(rr >= 1):
        raise ValueError('Strictly stable observable realization required')
    return abs(cv) @ (abs(block)*(rr**N/(1-rr))[:, None])


def modal_time_lipschitz(lam, beta, cv, block, T, qs):
    """Uniform all-time derivative bound for output, port, strictly proper output.
    Current block derivative includes C B q, which is zero for some outputs.
    Continuous output is Lipschitz across piecewise-constant power switches.
    """
    rr = np.exp(lam.real*T)
    qmax = abs(qs).max(axis=0)
    state_current = abs(beta)*qmax[None, :] * (-np.expm1(lam.real*T)/(-lam.real))[:, None]
    state_history = abs(block)/(1-rr)[:, None]
    direct = abs((cv@beta).real)*qmax[None, :]
    return (abs(cv*lam) @ (state_current+state_history)) + direct


def radial_bounds(weights, tail, lipschitz, phase_step, rays, max_run=None):
    """Continuous-time all-startup safe radial inner/outer (numerical bounds).
    phase_step/2 nearest-node bound; tau endpoints must be included.
    """
    result=[]
    for a in rays:
        w=np.einsum('opit,i->opt',weights,a)
        lower=all_startup_support(w,max_run).max()
        error=(tail@a).max()+phase_step/2*(lipschitz@a).max()
        upper=lower+error
        result.append((1/upper,1/lower,lower,upper,error))
    return np.array(result)
