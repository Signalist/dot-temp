"""Exact lag/ramp actuator endpoint-and-charge reachability oracle.

State b in [lower, upper], derivative satisfies
  max(-r_down,(lower-b)/tau) <= b' <= min(r_up,(upper-b)/tau).
This is the feasible-trajectory description of clipped first-order actuation.
Units are arbitrary but consistent; h,tau are time units. No external state.

Bounds and endpoint gradients are analytic except for a scalar Brent root.
Floating point implementation: not an interval-arithmetic certification.
"""
from dataclasses import dataclass
from math import exp, expm1, log, isfinite
from scipy.optimize import brentq

@dataclass(frozen=True)
class Actuator:
    lower: float = -450.0
    upper: float = 450.0
    tau: float = 0.005
    r_up: float = 30000.0
    r_down: float = 30000.0
    def __post_init__(self):
        if not (self.lower < self.upper and self.tau > 0 and self.r_up > 0 and self.r_down > 0):
            raise ValueError('Need lower < upper, tau > 0 and positive ramps.')

# Each flow routine returns (value, integral, derivative_value_wrt_b,
# derivative_integral_wrt_b). The duration is nonnegative.
def _forward_up(b, t, upper, tau, rate):
    g=max(0.0,upper-b)
    if g <= tau*rate:
        ee=exp(-t/tau); one=-expm1(-t/tau)
        return upper-g*ee, upper*t-g*tau*one, ee, tau*one
    ramp_time=g/rate-tau
    if t <= ramp_time:
        return b+rate*t, b*t+0.5*rate*t*t, 1.0, t
    d=t-ramp_time; ee=exp(-d/tau); one=-expm1(-d/tau)
    integral=b*ramp_time+0.5*rate*ramp_time**2+upper*d-tau*tau*rate*one
    return upper-tau*rate*ee, integral, ee, ramp_time+tau*one

def _backward_up(b, t, lower, tau, rate):
    g=max(0.0,b-lower)
    if g >= tau*rate:
        return b+rate*t, b*t+0.5*rate*t*t, 1.0, t
    # At lower, forward time cannot arrive from above in finite time.
    # The reverse flow remains lower, but its one-sided endpoint derivative
    # is exponential; this is finite for the intended cell lengths.
    threshold=float('inf') if g == 0.0 else tau*log(tau*rate/g)
    if t <= threshold:
        ee=exp(t/tau); em1=expm1(t/tau)
        return lower+g*ee, lower*t+g*tau*em1, ee, tau*em1
    d=t-threshold
    integral=lower*threshold+tau*(tau*rate-g)+(lower+tau*rate)*d+0.5*rate*d*d
    deriv=rate*tau/g
    return lower+tau*rate+rate*d, integral, deriv, tau*(tau*rate/g-1.0)+d*deriv

def forward_up(b,t,p): return _forward_up(b,t,p.upper,p.tau,p.r_up)
def forward_down(b,t,p):
    v,I,dv,dI=_forward_up(-b,t,-p.lower,p.tau,p.r_down)
    return -v,-I,dv,dI

def backward_up(b,t,p): return _backward_up(b,t,p.lower,p.tau,p.r_down)
def backward_down(b,t,p):
    v,I,dv,dI=_backward_up(-b,t,-p.upper,p.tau,p.r_up)
    return -v,-I,dv,dI

def reachability(b0,h,p=Actuator()):
    if h <= 0: raise ValueError('h must be positive')
    if not p.lower-1e-10 <= b0 <= p.upper+1e-10:
        raise ValueError('b0 outside command-invariant state interval')
    low=forward_down(b0,h,p); high=forward_up(b0,h,p)
    return {'b1_min':low[0], 'b1_max':high[0],
            'grad_b1_min':low[2], 'grad_b1_max':high[2]}

def cell_bounds(b0,b1,h,p=Actuator(),tol=1e-9,anchor_unreachable=False):
    """Return exact min/max charge and endpoint gradients on reachable pairs.

    If anchor_unreachable=True, clamp b1 to its reachable interval and return
    valid supporting cuts at that clamped anchor. The returned anchor must be
    used in tangent formulas, never the original infeasible b1.
    A tangent at x=(b0,b1) is
       Imax(y) <= Imax(x)+grad_max dot (y-x),
       Imin(y) >= Imin(x)+grad_min dot (y-x).
    Thus both give globally valid *outer* cuts over the reachable domain.
    """
    rr=reachability(b0,h,p)
    if not p.lower-tol <= b1 <= p.upper+tol:
        raise ValueError('b1 outside command-invariant state interval')
    reachable=rr['b1_min']-tol <= b1 <= rr['b1_max']+tol
    out={**rr,'reachable':reachable,'original_b0':b0,'original_b1':b1,'h':h}
    if not reachable and not anchor_unreachable: return out
    b1=min(rr['b1_max'],max(rr['b1_min'],b1))
    out.update(anchor_b0=b0,anchor_b1=b1)
    for label,F,B in [('max',forward_up,backward_up),('min',forward_down,backward_down)]:
        def residual(t): return F(b0,t,p)[0]-B(b1,h-t,p)[0]
        f0=residual(0.0); fh=residual(h)
        scale=max(1.0,abs(b0),abs(b1),p.upper-p.lower)
        tiny=1e-13*scale
        if abs(f0)<=tiny: s=0.0
        elif abs(fh)<=tiny: s=h
        else: s=brentq(residual,0.0,h,xtol=max(1e-15,h*1e-13),rtol=1e-14)
        ff=F(b0,s,p); bb=B(b1,h-s,p)
        out['I'+label]=ff[1]+bb[1]
        out['grad_'+label]=(ff[3],bb[3])
        out['switch_'+label]=s
        out['switch_b_'+label]=0.5*(ff[0]+bb[0])
    return out

def extreme_value(t,b0,b1,h,p,which):
    if which=='max': return min(forward_up(b0,t,p)[0],backward_up(b1,h-t,p)[0])
    if which=='min': return max(forward_down(b0,t,p)[0],backward_down(b1,h-t,p)[0])
    raise ValueError("which must be 'min' or 'max'")

def lift_value(t,b0,b1,h,charge,p=Actuator(),bounds=None):
    """Continuous actual buffer power realizing the specified cell charge."""
    bb=cell_bounds(b0,b1,h,p) if bounds is None else bounds
    if not bb['reachable']: raise ValueError('unreachable endpoint pair')
    lo,hi=bb['Imin'],bb['Imax']
    if not lo-1e-8 <= charge <= hi+1e-8: raise ValueError('unreachable charge')
    weight=0.0 if hi-lo<=1e-13 else min(1.0,max(0.0,(charge-lo)/(hi-lo)))
    return (1-weight)*extreme_value(t,b0,b1,h,p,'min')+weight*extreme_value(t,b0,b1,h,p,'max')

def pure_lag_bounds(b0,b1,h,lower,upper,tau):
    """Uncapped-ramp closed form, valid only for reachable endpoint pairs."""
    E=exp(h/tau); D=upper-lower; db=b1-b0
    kmax=((b1-lower)*E+upper-b0)/D
    kmin=((upper-b1)*E+b0-lower)/D
    imax=lower*h+D*tau*log(kmax)-tau*db
    imin=upper*h-D*tau*log(kmin)-tau*db
    return imin,imax
