# Explicit three-moment bang-jerk compression on one cell

This independent constructive version is optional: the main upper theorem uses the general moment-body proof. It gives a scalar closed-form construction matching jerk moments of degree 0,1,2, with a conservative total 4M-jump bound over M cells.

For |j(s)|<=J on [0,Delta], put b=(1-j/J)/2 in [0,1] and compute

    q=integral b, mu=integral s*b, nu=integral s^2*b.

If q=0 or Delta, b is already constant almost everywhere. Otherwise put c=mu/q. The moment constraints imply

    q^2/2<=mu<=Delta*q-q^2/2.

The minimum possible second moment at fixed q,mu is

    nu_min=mu^2/q+q^3/12,

attained by the interval [c-q/2,c+q/2]. Proof: subtract its indicator from b, multiply by (s-c)^2-q^2/4, and integrate; the product is nonnegative both inside and outside the interval. Constant and linear moment terms cancel.

The maximum is attained by two endpoint intervals [0,x] and [Delta-q+x,Delta], where

    x=(Delta*q-q^2/2-mu)/(Delta-q),  0<=x<=q.

To prove maximality multiply the difference between any b and this endpoint indicator by (s-x)(s-(Delta-q+x)). The product is nonpositive both inside and outside the endpoint intervals; constant and linear moment terms again cancel.

If x=0 or x=q, the first moment is extremal and b is already uniquely an endpoint interval almost everywhere. Otherwise x(q-x)>0. For 0<=g<=Delta-q let

    L=c-q/2-g*(q-x)/q,
    S_g=[L,L+x] union [L+x+g,L+q+g].

The set lies in [0,Delta] and has mass q and first moment mu. Its second moment is

    nu(g)=nu_min+x*(q-x)*g*(1+g/q).

It increases continuously from nu_min to the maximum second moment above. Therefore choose

    g=(q/2)*(sqrt(1+4*(nu-nu_min)/(q*x*(q-x)))-1).

Then b_hat=indicator_(S_g) matches all three moments exactly and j_hat=J*(1-2b_hat) is a bang jerk with at most four cell-interior switches. Across cells, the negative sets form a union of at most 2M intervals, hence at most 4M global jumps; there is no separate boundary surcharge. The general moment-body construction sharpens this to at most 4M-1 but the asymptotic exponent is identical.

The interval formula is exact mathematics. Floating-point implementations must handle q near 0 or Delta, x near 0 or q, stable evaluation of sqrt(1+z)-1, interval ordering, and moment residuals. Unvalidated numerical clamping is not proof of exact feasibility.
