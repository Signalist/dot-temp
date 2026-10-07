# Fixed Fourier cutoff gives a finite linearized terminal switch bound

2026-10-04 UTC

## Result and scope

For the **linearized terminal functional about an affine nominal clock**, fixed finite Fourier cutoff, fixed nominal speed, fixed horizon and a fixed finite-dimensional LTI kernel yield a uniform finite number of acceleration switches sufficient for exact optimality. This is a corollary of classical L1 duality and exponential-polynomial zero counting. It is not asserted here for the nonlinear phase composition or for a genuinely active speed constraint.

Let eta(0)=eta'(0)=eta(T)=eta'(T)=0, |eta''|<=rho, rho>0, and maximize

    L_q(eta)=integral_0^T q(t)eta(t)dt.

Assume any speed band is redundant for this clamped class, for example it contains [r-rho T/4,r+rho T/4]. Suppose q belongs to a fixed real, conjugation-closed exponential-polynomial space annihilated by a monic constant-coefficient polynomial P(D) of degree D_q. Let

    d = D_q+2,
    Omega = maximum absolute imaginary part of a root of P,
    K = 1,                                  if Omega=0,
        floor(T Omega/pi)+1,                 if Omega>0.

Then an exact optimum exists with at most

    M_star=(d-1)K

interior acceleration switches. If q=0, constant zero acceleration is already optimal; a two-switch bang bridge is an optimal bang representative if one is required. For all q in the stated dictionary, m>=max(2,M_star) makes the restricted linearized optimal-value gap zero. This is an existence result; the formula is conservative and is not a bound on root-isolation or global-search runtime.

## 1 From Fourier workloads to the fixed dictionary

Write a real impulse response as a finite sum

    h_j(s)=sum_l P_jl(s) exp(lambda_jl s)

and a phase-period-one workload as

    e_j(x)=sum_(n=-B)^B c_jn exp(i 2 pi n x).

For the affine nominal phase theta0+rt, the derivative of the fixed-endpoint energy-primitive objective is

    q(t)=sum_j h_j'(T-t)e_j(theta0+rt).

Thus its possible exponents are

    xi_jln = -lambda_jl + i 2 pi n r,

with polynomial degrees no larger than deg(P_jl). Collect repeated exponents, using the maximum necessary polynomial multiplicity nu_xi. One valid annihilator is

    P(D)=product_xi (D-xi)^(nu_xi),
    D_q=sum_xi nu_xi,
    Omega<=max_jl |Im(lambda_jl)|+2 pi B r.

Conjugate eigenvalues and real workloads ensure a real ODE. Missing or cancelling terms only reduce the required dictionary. The multiplicities and frequencies are fixed by the kernel and B, while the workload coefficients may vary arbitrarily within their amplitude/energy restrictions. The constant is consequently uniform over those coefficients.

## 2 Exact affine L1 duality supplies the bang optimizer

Put a=eta''/rho. The endpoint conditions are exactly

    integral a=0,        integral t a=0.

Fubini gives

    L_q(eta)=rho integral K_q(s)a(s)ds,
    K_q(s)=integral_s^T (t-s)q(t)dt,
    K_q''=q.

Minimize the finite-dimensional convex function

    F(lambda0,lambda1)=integral_0^T |K_q(s)-lambda0-lambda1 s|ds.

A minimizer exists because the L1 norm on the two-dimensional affine-polynomial space is coercive in its coefficients. Let S=K_q-lambda0-lambda1 s at a minimizer. If q is not identically zero, S is a nonzero analytic exponential polynomial, so its zero set on [0,T] is finite and has measure zero. Differentiating F with respect to the two coefficients then yields

    integral sign(S)=0,       integral s sign(S)=0.

Therefore a_star=sign(S) satisfies both endpoint moments. For any feasible a,

    integral K_q a = integral S a <= integral |S|
                          = integral K_q a_star.

This proves global optimality, not merely a necessary PMP condition. It also avoids an unverified normality assumption. Zeros of even multiplicity need not cause a switch; counting every zero is a safe upper bound.

If q=0, the objective is constant. This degenerate case must be handled separately rather than applying a nonzero-function zero theorem to S=0.

## 3 The primary zero theorem and the exact substitution

J. M. Aldaz, O. Kounchev and H. Render, *Bernstein operators for exponential polynomials*, Constructive Approximation 29 (2009), 345–367; [DOI](https://doi.org/10.1007/s00365-008-9010-6); [full original preprint](https://arxiv.org/pdf/0805.1618).

Their §1 definition of an extended Chebyshev space counts zeros with multiplicity. Theorem 9, PDF p.7, states that a conjugation-closed exponential-polynomial space with imaginary eigenvalue parts bounded by Omega is extended Chebyshev on any interval of length strictly less than pi/Omega. Repeated eigenvalues are explicitly included in §2 and give polynomial times exponential basis functions.

In the present problem P(D)q=0 and S''=q, hence

    D²P(D)S=0.

This solution space has dimension d=D_q+2 and adds two real zero roots, which do not enlarge Omega. Partition [0,T] into K equal cells. For Omega>0, K>TOmega/pi ensures strict cell length T/K<pi/Omega. Every nonzero S has at most d-1 zeros in each closed cell, so its total number of distinct zeros is at most K(d-1). Counting shared endpoints twice can only enlarge this bound. If Omega=0, all roots are real and the entire interval is an extended Chebyshev interval, giving d-1 directly.

A claim of d-1 zeros on an arbitrary long interval with complex roots would be wrong: a sine already violates it. The horizon-dependent partition is necessary. The theorem is a sufficient local condition, not a claim that pi/Omega is the exact critical length of the dictionary.

## 4 Independent elementary fallback

The finiteness conclusion does not depend on a delicate bibliographic interpretation. Write the annihilating ODE as

    S^(d)+sum_(j=0)^(d-1) c_j S^(j)=0.

Choose delta>0 so sum |c_j|delta^(d-j)<1. If S had d distinct zeros in an interval of length delta, repeated Rolle and integration from a zero of each derivative would give

    ||S^(j)||<=delta^(d-j)||S^(d)||,     0<=j<d.

The ODE would imply ||S^(d)||<||S^(d)|| unless S^(d)=0, in which case d zeros force S=0 there and uniqueness forces S identically zero. Thus a nonzero S has at most d-1 zeros per delta-cell. This supplies a coarser explicit uniform bound. After nondimensionalizing time, delta=min(1,[2(1+sum|c_j|)]^-1) is sufficient. This is a self-contained classical Rolle argument, not a new theorem claimed for publication.

## 5 What the reduction changes and what it does not

1. For this linearized problem, m^-2 worst-case asymptotics cannot persist at fixed B all the way to m→infinity: the gap becomes exactly zero above M_star. Adaptive switch locations can exploit this structure; a uniform fixed time mesh need not hit the same exact optimizer.
2. The pure cosine lower example requires N to grow with m. A fixed cutoff excludes that sequence. The full-peak candidate also uses a flat smooth envelope, which is not itself a finite trigonometric polynomial. A Fourier truncation is a new workload family and needs new estimates.
3. This does not disprove an m^-2 lower for a different nonlinear finite-band family. It only proves the zero-gap result for the declared linearized problem and invalidates transferring the existing unbounded-band sequence unchanged.
4. In the nonlinear endpoint problem the switching curvature contains e_j(theta(t)), evaluated along an unknown non-affine theta. Even a finite Fourier series in theta generally ceases to be a member of a fixed exponential-polynomial space in t. The displayed annihilator is therefore unavailable.
5. With an active speed band, state-constraint multipliers and coast/contact arcs require separate analysis. The unconstrained a_star may violate the band. The zero theorem alone does not provide a global active-band bang/coast count.
6. The statement is for a fixed observation endpoint with fixed service completion data. A peak objective and its moving observation endpoint require explicit treatment of the associated piecewise kernels and boundary terms.
7. The result supplies an exact classical baseline for a manuscript: finite-band linearized switch optimization should be separated from unbounded-band nonlinear representation lower bounds.

## 6 The same classical argument covers linearized finite jerk

For the finite-jerk contract, use eta,eta',eta'' zero at both endpoints and |eta'''|<=J. The three endpoint moments are integral s^r j(s)ds=0 for r=0,1,2. The adjoint kernel is now

    K_q(s)=(1/2) integral_s^T (t-s)²q(t)dt,    K_q'''=-q.

Replace the best affine L1 approximation in Section 2 by a best quadratic approximation. Its three coefficient equations make j_star=J sign(K_q−p2) satisfy all three moments. The annihilator is D³P(D), so d=D_q+3, with exactly the same Omega and short-interval partition. The bound is again (d−1)K switches. Thus the **linearized** finite-jerk problem also has an exact finite-switch representative uniformly over a fixed Fourier dictionary, when all other state envelopes are inactive. This does not turn the nonlinear bounded-slope upper into an exact nonlinear switch theorem.
