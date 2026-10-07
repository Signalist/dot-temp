# Continuously clocked, energy-matched drift: exact and asymptotic results

Prepared 2026-10-03. These are mathematical results under an explicit model, not a claim of historical novelty or validation of a real compute installation. The older fixed-period reconnection manuscript is not modified.

## 1. Physical and information contract

Let unwrapped job phase be theta, with theta'=v>0. One period corresponds to a specified amount of completed useful work; for example W(theta+L)-W(theta)=W_cycle, with W strictly increasing when endpoint work is used to identify phase. A common clock represents synchronized stages. Model electrical power as

    p(t) = p_idle + e(theta(t)) v(t),     E'(theta)=e(theta),

where e is nonnegative periodic energy per unit progress and p_idle is constant. Then

    integral_0^T p(t) dt = p_idle T + E(theta(T))-E(theta(0)).

Thus a common initial/terminal phase fixes completed work AND electrical energy. It does not fix the time profile. This contract is appropriate only when timing elasticity has approximately speed-independent energy per unit useful progress over the specified speed band. DVFS-dependent energy, stall power, phase-dependent idle power, and thermal effects are not silently included. Their errors need measurement/model bounds. A fixed stage-power model p=P(theta) is a different contract: dwelling longer generally consumes more energy.

Use a continuously running clock, never a reset. The principal endpoint contract is

    theta(0)=theta0, v(0)=r,
    theta(T)=theta0+rT, v(T)=r,
    |v'| <= rho,    omega_min <= v <= omega_max.

Write theta(t)=phi(t)+rho eta(t), phi(t)=theta0+rt, and a=eta''. The normalized feasible class is

    C={a in L_infinity: |a|<=1,
       integral_0^T a(s) ds=0,
       integral_0^T s a(s) ds=0},
    eta(t)=integral_0^t (t-s)a(s) ds.

The two moments are exactly terminal speed and terminal work/progress. They are substantive promises, not harmless normalization. Remove either promise and the uncertainty class changes. Regularity is v in W^(1,infinity), theta in W^(2,infinity), with acceleration bounds almost everywhere. If continuous acceleration is required, bang paths need smoothing and exact attainment needs reconsideration; the bang bounds remain sharp limits.

For a finite-dimensional strictly proper LTI grid, let h(t)=C exp(At) B be the scalar impulse response of the output of interest. Stable A matters for long-horizon interpretation, but the finite-horizon identities below do not require stability. Direct feedthrough needs separate endpoint-power terms. Initial-state and idle-power responses are deterministic additions.

## 2. Sharp, simultaneous phase and speed envelopes

Define

    b(t)= t^2/2                                  0<=t<=T/4
          -t^2/2+Tt/2-T^2/16                     T/4<=t<=3T/4
          (T-t)^2/2                              3T/4<=t<=T.

For every a in C,

    -b(t) <= eta(t) <= b(t),   |eta'(t)| <= T/4.

Both phase bounds are attained simultaneously for every t by the two accelerations +/-a_b, where a_b is +1, -1, +1 on the three intervals split at T/4 and 3T/4. In particular max b=T^2/16. Consequently

    rho*T/4 <= min(r-omega_min, omega_max-r)                 (inactive-band condition)

makes the speed constraints redundant for the ENTIRE normalized feasible class C.

Proof of phase bound: eta(t)=integral k_t(s)a(s) ds, k_t(s)=(t-s)_+. For t in [T/4,3T/4], subtract the affine line through (T/4,k_t(T/4)) and (3T/4,k_t(3T/4)); its integral against a vanishes. The residual has signs +,-,+ on the three intervals. Therefore its integral against a is at most its absolute integral, attained by a_b. For t<=T/4 the elementary eta(t)<=t^2/2 is attained by a_b. Use the terminal conditions for the time-reversed bound after 3T/4. Negate a for the lower bound.

Proof of speed bound: v=eta' has v(0)=v(T)=0 and zero mean. Its periodic extension is 1-Lipschitz for circular distance d_T(s,t)=min(|s-t|,T-|s-t|). Hence |v(s)| <= T^{-1} integral_0^T d_T(s,t)dt=T/4. The extremal above attains equality.

### 2.1 Exact envelopes with active speed limits or noncentral endpoints

There is a stronger constructive result for any feasible total displacement D, endpoint speeds v0,vT, duration T, speed band [l,u], and acceleration rho>0. Define

    U0(t)=min(u,v0+rho*t),
    LT(t)=max(l,vT-rho*(T-t)),
    v_c(t)=max(LT(t), min(U0(t), c-rho*t)).

Choose c in [v0,vT+rho*T] to satisfy integral v_c=D. Existence follows from continuity/monotonicity: the two endpoint choices reproduce the pointwise lower and upper velocity bridges. Then theta_max(t)=theta0+integral_0^t v_c is the largest feasible phase simultaneously at EVERY t. Obtain theta_min by reversing time, exchanging v0 and vT, applying the same construction, and reversing back.

Proof: feasibility implies LT<=U0. The construction consists of an initial U0 arc, a middle slope -rho arc, and a terminal LT arc, with possible speed plateaus. For any other feasible v, v-v_c is nonpositive on the initial arc, nondecreasing on the middle arc, and nonnegative on the terminal arc. It therefore has at most one negative-to-positive sign crossing. Equal total integrals imply integral_0^t(v-v_c)<=0 for every t. This proof requires no grid model. The scalar c need not be unique if clipping creates a flat parametrization, but the resulting extremal trajectory is sufficient.

For completeness, feasible total displacement is exactly [A_minus,A_plus] where, provided l<=v0,vT<=u and |vT-v0|<=rho*T,

    A_plus = (v0+vT)T/2 + rho*T^2/4 - (vT-v0)^2/(4rho)
             - positive_part(v0+vT+rho*T-2u)^2/(4rho),
    A_minus= (v0+vT)T/2 - rho*T^2/4 + (vT-v0)^2/(4rho)
             + positive_part(2l-v0-vT+rho*T)^2/(4rho).

They are the integrals of min(u,v0+rho*t,vT+rho*(T-t)) and max(l,v0-rho*t,vT-rho*(T-t)). Any intermediate displacement is attained by a convex combination of those velocity bridges.

## 3. Exact convolution identity

For a common initial phase, integration by parts gives the clock-dependent output difference at final time T:

    Delta y(T) = h(0) Delta E(T)
                 + integral_0^T h'(T-t) Delta E(t) dt,
    Delta E(t)=E(theta(t))-E(phi(t)).

Under the endpoint-progress contract, Delta E(T)=0 exactly, leaving

    Delta y(T)=integral_0^T h'(T-t)[E(phi(t)+rho*eta(t))-E(phi(t))] dt.       (1)

This identity removes explicit speed from the nonlinear convolution and exposes the effect of service information. It is exact, not a small-drift expansion.

If h' has one sign on [0,T], e>=0 makes E monotone, so the two universal phase trajectories are exact global output extrema. If h'<=0, theta_min maximizes y(T) and theta_max minimizes it; reverse the assignment if h'>=0. Section 2.1 permits active speed bands. No HJB or optimal-control discretization is needed for this special class. A positive decaying exponential impulse response is an example. Oscillatory electromechanical impulse responses generally do not satisfy this sign condition.

## 4. Sharp first-order support and a uniform second-order remainder

Assume e is continuously differentiable, with Lipschitz constant L_e over the reachable phase range. Define

    F(s)=integral_s^T h'(T-t)e(phi(t))(t-s) dt,
    S(F)=sup_{a in C} integral_0^T F(s)a(s) ds.

Then

    Delta y(T)=rho*integral F a + R(a),
    |R(a)| <= Rbar = (rho^2 L_e/2) integral_0^T |h'(T-t)| b(t)^2 dt.        (2)

Use local valid bounds on |e'| to tighten the integrand if desired. The b^2 bound respects both endpoint moments and is substantially tighter than t^4/4 near the end of the horizon.

The support is EXACTLY

    S(F)=min_{alpha,beta} integral_0^T |F(s)-alpha-beta*s| ds.              (3)

Equivalently use the affine basis 1,T-s. The dimension of this convex minimization is two, independent of the grid state dimension and of a time discretization.

Proof: subtracting an affine function preserves integral F a. The triangle inequality gives weak duality. The affine L1 objective is coercive and continuous, so it has a minimizer. If the residual has a measure-zero zero set, its two derivative conditions state that sign(F-alpha-beta*s) has zero zeroth and first moments. This feasible acceleration attains the dual bound. More generally an appropriate value in [-1,1] on the residual zero set supplies the subgradient and proves equality.

Under the inactive-band condition, (2)-(3) yield

    y0+rho*S-Rbar <= sup y(T) <= y0+rho*S+Rbar,
    y0-rho*S-Rbar <= inf y(T) <= y0-rho*S+Rbar.

Consequently the worst absolute terminal output differs from |y0|+rho*S by at most Rbar. A dual upper by itself is a safe upper, not proof of an attained exact nonlinear risk. A feasible realizer and the remainder provide the matching lower.

### 4.1 Information value

With neither terminal promise the support is integral |F|, with the appropriate endpoint boundary term retained. With only terminal speed, it is the L1 distance to constants (a median problem). With only terminal progress, it is a weighted one-parameter L1 fit against T-s. With both, it is the affine L1 fit above. Additional phase/work checkpoints impose additional linear acceleration moments (t_j-s)_+ and enlarge the dual fitting span. These comparisons must use the same physical power contract and correctly retained boundary terms.

For synchronized energy profiles e=sum_j e_j, F=sum_j F_j and

    S(sum_j F_j) <= sum_j S(F_j).

The latter is the relaxation that gives stages/harmonics independent clocks. Equality is not guaranteed; strict inequality is possible when the individual maximizing accelerations conflict. It is inappropriate to model synchronized harmonics as independently drifting uncertainties without labeling that relaxation.

## 5. Exact finite-rho finite-switch theorem

Assume the endpoint contract of section 1, the inactive-band condition, rho>0, e continuous and strictly positive on the reachable phase range, and h' continuous with K DISTINCT zeros in (0,T) and no zero interval. Analytic nonzero finite-dimensional LTI h' has finitely many zeros on a compact interval. Then an exact global maximum and minimum of y(T) exist, and EVERY maximizer/minimizer is bang acceleration almost everywhere with at most K+2 switching times.

Proof, avoiding any abnormal-PMP issue:

1. C is weak-star compact. Weak-star convergence of a implies pointwise convergence of eta(t); bounded second derivatives give equicontinuity, hence uniform convergence of eta. The nonlinear objective (1) is continuous, so extrema exist.
2. At any global maximizer a_star, differentiability and convexity of C imply DJ(a_star)[a-a_star]<=0 for every a in C. Thus a_star solves a LINEAR support problem whose kernel is

       F_star(s)=integral_s^T h'(T-t)e(theta_star(t))(t-s)dt.

3. Apply (3) to F_star. For a minimizing affine function ell, q=F_star-ell satisfies

       q''(s)=h'(T-s)e(theta_star(s)).

   Strictly positive e makes the zero set of q'' exactly that of h'(T-s). Repeated Rolle gives at most K+2 distinct zeros of q. Thus q is nonzero almost everywhere.
4. Equality in the support dual forces a_star=sign(q) almost everywhere. Therefore a_star switches at most K+2 times. Minima follow by negating the objective.

This is an exact structural result; it does not mean every bang trajectory is optimal, that there is a unique optimum, or that a local switch-time solver certifies the global optimum. The exact problem reduces to a finite UNION over initial signs and switch counts m<=K+2 of compact switch-time domains with two moment equalities. The objective is a low-dimensional nonlinear integral. A global branch-and-bound/interval bound is still needed for a numerical certificate in general. In the special case K=0, two moments force the two switches to T/4 and 3T/4, recovering the exact universal-envelope solution.

The theorem can fail as stated when speed bands are active (boundary arcs appear), e vanishes on intervals (singular intervals become possible), h' has a zero interval, or initial/final progress is not fixed. These are limitations of the theorem, not evidence that the real model becomes unsafe.

### 5.2 Multiple electrical ports

If all ports have p_j=alpha_j e(theta)v with the SAME waveform, combine their transfer kernels into h_eff=sum_j alpha_j h_j. Apply the theorem to h_eff. With different positive waveforms e_j sharing a clock, the switching-function curvature instead is sum_j h_j'(T-t)e_j(theta(t)). Its zero count can depend on the waveform and trajectory; sharing a clock alone does NOT make the switch bound independent of stage complexity. A sign-coherent kernel partition can preserve a finite sign-variation bound, but the direct Rolle statement above counts actual zeros, not merely sign changes. Mixed-sign multi-port kernels require a separate zero-count argument or a conservative general reachability treatment.

Explicit mixed-port example: h1(u)=-exp(-u), h2(u)=exp(-u), e1(theta)=1+epsilon*sin(N*theta), e2(theta)=1-epsilon*sin(N*theta), 0<epsilon<1. Each stable port derivative has zero sign changes, but their common-clock switching curvature is 2*epsilon*exp(-(T-t))*sin(N*theta(t)); its zero count grows with synchronized stage frequency N. Thus the scalar factorization cannot be invoked merely because the ports share a clock. This example establishes failure of that zero-count argument, without claiming an exact global switching-count lower bound for every nonlinear parameter choice.

A refined version is valid if the curvature is strictly positive or strictly negative on each member of a partition into K+1 consecutive intervals, allowing isolated zero points: q' is strictly monotone on each interval, so it has at most K+1 distinct zeros, and q has at most K+2. This permits a bound in terms of sign-change count rather than all distinct zeros, provided the stated strict-monotonicity/nonzero-interval condition is established. Multiplicities do not enter the simpler distinct-zero Rolle bound.

### 5.1 Exact switch constraints

For m ordered switches 0<t1<...<tm<T, initial sign sigma, and alternating signs thereafter,

    integral a = sigma[(-1)^m T + 2 sum_j (-1)^(j-1)t_j],
    integral s a = sigma[(-1)^m T^2/2 + sum_j (-1)^(j-1)t_j^2].

Set both to zero. Thus at most K free continuous dimensions remain after the two moments. Coincident switches describe lower-switch strata and should not be accidentally excluded by a search implementation. For m=2, the only solution is (T/4,3T/4). For m=3, one free switch parameter remains.

Two adjacent switches can correct tiny moment residuals algebraically. Let their coefficients in the sums be c and -c (c=+/-1), and let R1,R2 be the required remaining linear and square sums after all other switches are subtracted. Then

    t_i - t_j = c*R1,   t_i+t_j=R2/R1,
    t_i=(R2/R1+c*R1)/2, t_j=(R2/R1-c*R1)/2,

provided R1 is nonzero. Recheck ordering, bounds, and the exact moments afterward.

### 5.3 Fully explicit K=1 family and its global interpolation bound

When h' has at most one zero, every exact optimizer belongs to the two signed copies of one family. Let

    x in [0,T/4],
    z(x)=T*(3T/4-x)/(T-2x),
    y(x)=x+z(x)-T/2.

Use initial sign + and switches x,y,z, or negate the acceleration. The endpoints x=0 and x=T/4 give the two-switch limits. The corresponding phase perturbation is

    eta_x(t)=t^2/2-(t-x)_+^2+(t-y)_+^2-(t-z)_+^2.

Here the subscript x labels the family; in the following bounds partial_x denotes differentiation with respect to the parameter. Put d=z'(x)=T^2/[2(T-2x)^2], so 1/2<=d<=2, y'=1+d, and z''=y''=2T^2/(T-2x)^3. Then

    partial_x eta = 0                         t<x,
                    2(t-x)                    x<t<y,
                    2(t-x)-2(1+d)(t-y)        y<t<z,
                    0                         t>z.

The derivative is a nonnegative triangular function of t, with peak 2(y-x)=2z-T<=T. The second parameter derivative is -2 on (x,y), is

    -2+2(1+d)^2-2z''(t-y)

on (y,z), and is zero elsewhere. On (y,z) it decreases from 4d+2d^2<=16 to 2d^2. Thus the sharp convenient uniform bounds are

    |partial_x eta|<=T,       |partial_xx eta|<=16 a.e.

For J(x)=integral h'(T-t)E(phi(t)+rho*eta_x(t))dt, and |e'|<=L_e, e<=e_max,

    |J''(x)| <= M = integral_0^T |h'(T-t)| [L_e*rho^2*T^2+16*e_max*rho]dt.

Consequently a piecewise-linear interpolation of J on x-grid width Delta has uniform error <=M*Delta^2/8. This supplies an exact finite-dimensional GLOBAL upper when nodal objective enclosures are validated, and a matching feasible lower from the evaluated clocks. Include both initial signs. Ordinary time quadrature at the nodes is not a formal enclosure unless its error is bounded.

The dependence on x is C1 with a Lipschitz derivative; discontinuities of second derivatives along t=x,y,z do not invalidate this interpolation bound. Neither uniqueness nor unimodality of J is asserted.

## 6. Computable support certificates

### 6.1 Rigorous upper without finding roots

For ANY affine ell, take nodes s_j and certified enclosures F(s_j)=Fhat_j +/- eps_j. Let q_PL be the piecewise-linear interpolant of Fhat_j-ell(s_j). The integral J_PL=integral |q_PL| is elementary, including panels with a sign crossing. If M_j bounds |h'(T-s)e(phi(s))| on a panel of width Delta_j, then

    S(F) <= J_PL
            + sum_j M_j Delta_j^3/12
            + sum_j Delta_j(eps_j+eps_{j+1})/2.                         (4)

Proof: the interpolation error satisfies |q-q_PL_exact| <= M_j(s-s_j)(s_{j+1}-s)/2; integrate it and then use ||q|-|q_PL||<=|q-q_PL|. No unresolved zero crossing can invalidate this bound.

For endpoint values q0,q1, the integral of the absolute linear interpolant is

    Delta*(|q0|+|q1|)/2                            if q0*q1>=0,
    Delta*(q0^2+q1^2)/(2*(|q0|+|q1|))             otherwise.

Certified node errors matter. Double-precision quadrature with a reported tolerance is not automatically a mathematical enclosure. Use interval arithmetic, analytic formulas with validated evaluation, or derivative-based quadrature bounds. A good floating-point optimization may supply ell; ANY exactly represented chosen ell is permitted in the upper bound, so optimizer optimality need not be certified.

### 6.2 Feasible lower despite inaccurate root finding

Let x=s/T and a0(x) be any implementable function in [-1,1], such as the sign of a computed dual residual. Compute its moments m0=integral_0^1 a0 dx and m1=integral_0^1 x*a0 dx. Set

    c0=-4m0+6m1,  c1=6m0-12m1,
    R=max(|c0|,|c0+c1|),
    a(x)=(a0(x)+c0+c1*x)/(1+R).

This a has both moments exactly zero and |a|<=1. It is therefore a valid continuously clocked witness, even if the root locations were approximate. Compute its linear objective for a support lower or its exact nonlinear output for a physical lower. Exact arithmetic or validated moment enclosures are required when claiming exact numerical feasibility. This procedure is a practical alternative to solving both switch equations to machine tolerance and calling them exact.

### 6.3 Closed-form Fourier/LTI kernel evaluation

If e(theta)=sum_k c_k exp(i*k*theta), with conjugate symmetry, put L=T-s, nu=k*r and

    Psi2(M,L)=integral_0^L (L-u)exp(Mu)du.

Then

    F(s)=sum_k c_k exp(i*k*(theta0+r*T)) C A Psi2(A-i*nu*I,L) B.

When M is nonsingular, Psi2=M^{-2}(exp(M L)-I-M L); a block exponential or phi-function evaluation avoids singular/inaccurately conditioned inverses. Real conjugate pairing gives real F. This formula offers exact analytical evaluation and removes nested quadrature; finite-precision matrix exponentials still require error control for a formal enclosure.

## 7. Earlier observation times and peak risk

When the work/frequency promise is at T but the observation time is tau<T, do NOT silently impose terminal progress at tau. The correct first-order kernel, defined on the FULL [0,T], is

    F_tau(s)=h(0)e(phi(tau))(tau-s)
             + integral_s^tau h'(tau-t)e(phi(t))(t-s)dt     if s<=tau,
             0                                             if s>tau.

Its support is still the affine L1 distance over [0,T]. A valid remainder is

    Rbar_tau=(rho^2 L_e/2)[|h(0)|b(tau)^2
                    + integral_0^tau |h'(tau-t)|b(t)^2dt].

Consequently sup_tau(|y0(tau)|+rho*S(F_tau)+Rbar_tau) is a robust peak upper. A finite time grid additionally needs a time-interpolation/output-derivative bound; dense sampling alone is not continuous certification.

The clean exact K+2 switch theorem is a final-time theorem. For tau<T, the switching function has a kink at tau and an affine tail. A zero tail can yield unconstrained continuation arcs, so the same switch count must not be asserted without an extension proof. Feasible tail accelerations with prescribed two moments can be represented by a bang acceleration with at most two tail switches, providing a route to a separate finite-dimensional peak theorem.

## 8. Alternative exact reduction for flat stage POWER

If the independent physical contract is p(t)=P_j while phase traverses stage j, terminal LTI output depends only on the stage crossing times. Continuous bounded-acceleration realizability is exactly described by crossing speeds v_j and stage durations tau_j: each stage phase length d_j must lie in [A_minus(tau_j,v_j,v_{j+1}),A_plus(...)]. The endpoint speed compatibility conditions also apply. The bridge construction proves necessity and sufficiency, and any intermediate phase length is realized by convexly mixing its lower/upper velocity bridges. Concatenation preserves a continuous clock and Lipschitz velocity.

For step response H(t)=integral_0^t h(u)du, stage j contributes

    P_j[H(T-t_j)-H(T-t_{j+1})].

An explicit total energy budget is linear: sum P_j*tau_j. Fixed progress alone does NOT fix it. This gives an exact finite-dimensional nonconvex optimization without grid-state decision variables, but it is a DIFFERENT physical contract from energy-per-progress.

Crossing times and crossing speeds are NOT sufficient statistics for p=e(theta)v. Counterexample: T=1, theta(0)=0, theta(1)=1, v(0)=v(1)=1, e=1, v_plus/minus(t)=1 +/- epsilon*sin(2*pi*t). Both clocks have identical crossing times, speeds, progress, and energy, and satisfy the acceleration bound if 2*pi*epsilon<=rho. For h(u)=exp(-a*u), their terminal response differences from constant speed are

    +/- epsilon * [-2*pi*(1-exp(-a))/(a^2+4*pi^2)],

which are nonzero. A stage-time certificate for energy-per-progress must retain additional within-stage information.

## 9. What can and cannot be claimed

- The nontrivial mathematical object is a common-clock, endpoint-service-preserving risk envelope. It quantifies how much trajectory information and synchronization restrict drift risk.
- Exact monotone-kernel extrema, an exact finite-switch theorem for oscillatory kernels, and a two-variable sharp-support certificate give structure that a generic HJB statement does not expose.
- These results do not establish historical novelty. Bang-bang principles, moment-constrained L-infinity support duality, L1 approximation, bounded-acceleration reachability, and optimal-control sensitivity are classical. Frequency-drift IQC and reachability literature must be compared directly before a novelty claim.
- The benchmark is not required to outperform optimal control. Exact/global optimal control is a truth model/comparator; the claim is model-specific reduction, certificate cost, information value, and physically fair energy/work matching.
- The finite-switch theorem remains nonconvex and does not certify a local solver. The first-order certificate is quantitatively meaningful only when its explicit remainder is small relative to the decision margin.
- A continuously varying workload phase, oscillatory grid kernel, and finite rho can matter; an ordinary Lipschitz triangle bound is not the proposed main result.
- If real compute energy depends materially on clock speed or idle dwell, the energy-per-progress model is unvalidated and its engineering interpretation must be limited accordingly.
- No artificial waiting reset, reconnection scheduling, BESS recovery service, or fixed-period assumption is used. This is distinct from the frozen earlier manuscript.
