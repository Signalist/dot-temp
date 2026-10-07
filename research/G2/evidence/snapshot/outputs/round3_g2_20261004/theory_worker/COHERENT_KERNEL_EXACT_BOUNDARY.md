# A robust non-opposite kernel class has two exact universal candidates

2026-10-04. This is a structural boundary of the hard cancellation examples. It applies to signed terminal and post-service observations, and consequently to the absolute peak over observation times tau>=T. It does not silently include the within-service absolute peak.

## 1. General jerk statement

Use the finite-jerk contract and entirely inactive acceleration/speed envelopes from `FINITE_JERK_AND_BANDWIDTH_THEOREMS.md`, Section 1. For full-future risk statements assume locally absolutely continuous integrable kernels with integrable derivatives and a bounded common additive response, as in its Section 3. Let the profiles be continuous and satisfy 0<e_j<=e_max,j globally (periodic positive profiles are an example). Since speed is globally bounded, h_j in L1 and bounded common additive response then make every full-future peak finite. At any fixed observation tau>=1, the continuation is common, the service endpoint phase is fixed, and integration by parts removes all clock-dependent endpoint terms. The variable output is

    J_tau(j)=constant+sum_j integral_0^1 h_j'(tau-t) E_j(theta(t))dt.

Suppose that

    q_theta(t)=sum_j h_j'(tau-t)e_j(theta(t))

has one strict sign on (0,1) for every feasible theta, or has that sign except for isolated zeros with no zero interval. Then an exact maximum and minimum exist and every optimum has at most THREE jerk switches. The only possible optimal clocks are the two overall signs of the jerk pattern

    j(t)=J*(+1,-1,+1,-1)

with switches

    s1=(2-sqrt(2))/4, s2=1/2, s3=(2+sqrt(2))/4.            (1)

Their phase perturbation is explicitly

    eta_+(t)=J/6*[t^3-2(t-s1)_+^3+2(t-s2)_+^3-2(t-s3)_+^3],
    eta_-(t)=-eta_+(t).                                   (2)

### Proof

The jerk set with its three linear endpoint moments is weak-star compact. Integration three times makes the phase map uniformly compact, and the objective is continuous, so optima exist. At a nonlinear optimum j_star, the first-order necessary inequality over this convex set says that j_star also solves the linear support problem with kernel

    F(s)=(1/2)integral_s^1 q_theta_star(t)(t-s)^2 dt,
    F'''(s)=-q_theta_star(s).

The support dual is the best L1 approximation of F by quadratic polynomials:

    sup_(|j|<=J, integral s^k j=0 for k=0,1,2) integral F j
        =J min_(quadratic p) integral_0^1 |F-p|.

For this case the dual identity follows directly: the finite-dimensional objective is continuous/coercive, so a minimizing p exists; F-p has at most three zeros by three applications of Rolle and the strict sign of F'''. Consequently it vanishes only on a measure-zero set, the derivative of the L1 objective gives the three zero-moment conditions for sign(F-p), and that sign attains equality. The same argument works under the stated isolated-zero condition because F'' is strictly monotone.

Equality forces j_star=J sign(F-p) almost everywhere, with at most three switches. Fewer than three switches cannot satisfy all three zero moments: a polynomial of degree at most two with roots at those switches would have positive integral against the jerk while its moment integral is zero.

For exactly three switches x1<x2<x3, the moment equations are

    x1-x2+x3=1/2,
    x1^2-x2^2+x3^2=1/2,
    x1^3-x2^3+x3^3=1/2.

Writing S=x1+x3=x2+1/2 and P=x1*x3=x2/2-1/8, the cubic equation yields x2=1/2. Hence S=1, P=1/8, proving (1). Both overall signs are feasible, so every extremum belongs to the two explicit clocks. QED.

## 2. Pairwise nonproportional, same-sign kernels

A concrete family is

    h_j(s)=sum_(r=1)^Rj c_jr exp(-lambda_jr s),
    c_jr>0, lambda_jr>0.

Every h_j'(s) is strictly negative at every finite s>=0. The profiles may have arbitrary bandwidth, independent positive shapes, and arbitrary relative phases; their only relevant property here is strict positivity. Distinct rates make kernels nonproportional. Strictly positive coefficients/rates define an open parameter region within this fixed-order family. Thus the property is robust to small parameter changes in that family, with no opposite-port cancellation and no shrinking-with-N uncertainty tolerance.

The same pair of clocks supplies exact extrema for EVERY tau>=1. Therefore

    sup_(feasible clocks) sup_(tau>=1) |y(tau)|
       =max_(sigma=+,-) sup_(tau>=1)|y_sigma(tau)|.          (3)

This is a two-trajectory reduction; it does not claim an easy analytic formula for each remaining one-dimensional time supremum. Common deterministic initial/idle responses may be included because the signed extremum statement holds at each tau and those responses do not affect the optimizing clock.

The robustness claim is parameter-relative. Strict negativity over an infinite horizon is not an open condition under every conceivable unweighted function norm: a tiny, more slowly decaying perturbation can eventually dominate the tail. On a fixed finite observation window, a strictly negative derivative margin is open under sufficiently small C1 perturbations.

## 3. Mixed-sign but common-mode-dominated kernels

Pairwise sign alignment of the h_j' is sufficient, not necessary. For

    h1=h+epsilon*g, h2=-h+epsilon*g,
    e1=1-d(theta)/2, e2=1+d(theta)/2, |d|<=D,

one has

    q_theta(t)=2*epsilon*g'(tau-t)-h'(tau-t)*d(theta(t)).

If

    2*epsilon*g'(s)>D*|h'(s)|

through the relevant lag interval (isolated simultaneous endpoint zeros allowed), then q_theta is strictly positive for every clock and every permitted workload. The exact two-candidate conclusion follows. This yields a finite-instance robust strict inequality in a coefficient parameterization, or in a relative-derivative topology that controls perturbations against the vanishing derivative envelope. It is not necessarily open under arbitrary absolute C1 perturbations: a common derivative zero at an endpoint can leave no positive uniform margin. Equality is the boundary, not a valid strict certificate.

For example on 0<s<=1, h=s^2 exp(-s), g=h+(1/10)s^3 exp(-s) obey g'>=h'>0. Taking epsilon>D/2 suffices for any workload with |d|<=D, at terminal tau=1. This is an open condition on the specified scalar coefficients epsilon and D, with h and g fixed. The kernels are nonproportional, and no workload-frequency restriction is needed. This example is a terminal theorem; g' and h' later change sign, so the same inequality has not been proved for arbitrary observation times.

## 4. Acceleration-only counterpart and the early-observation boundary

Under the earlier acceleration-bounded endpoint contract with entirely inactive speed bounds, exactly the same argument uses an affine dual and the second derivative F''=q_theta. It yields at most two acceleration switches. The two endpoint moments force the universal switch times 1/4 and 3/4. Active-band phase-envelope constructions can cover the sign-coherent terminal case separately, as proved in the earlier frozen clock theorem.

For 0<tau<1, the current phase theta(tau) is not fixed. The exact integration-by-parts identity includes

    sum_j h_j(0)[E_j(theta(tau))-E_j(reference(tau))].

That term must be included in the first variation and can introduce an extra switching-function feature. The post-service theorem does not authorize a whole-time peak reduction when it is nonzero. In particular, the decaying-exponential family has h_j(0)>0, so merely taking a supremum over all tau>=0 in (3) would be an unproved extension.

## 5. What this decides

The cancellation-based hard family is not a generic consequence of synchronization or high workload frequency. A substantial, explicitly non-opposite kernel class has exact fixed-size representations even with arbitrary workload bandwidth and finite jerk. Conversely, this does not prove that real oscillatory multi-port electrical grids belong to the coherent class; their transfer signs/margins have to be checked. The bounded-bandwidth upper and this coherent-kernel boundary establish limitations of the hard construction rather than physical deployment viability.

## 6. Unproved possible extension, not used

A fixed-size full-time representation may also be possible: the retained early-observation boundary adds a squared-hinge term to the jerk support kernel, leaving a sign-controlled third derivative before the observation and a quadratic residual afterward. Singular unused tails could be moment-compressed. This idea is NOT proved, numerically certified, or used in any result here; no whole-time coherent-kernel switch bound is claimed.
