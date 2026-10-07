# Finite jerk changes the representation exponent; fixed bandwidth changes it again

2026-10-04. New results in this note are mathematical statements about the specified synthetic output and representation class. They are not runtime lower bounds, physical deployment evidence, or historical novelty claims. The earlier frozen round-2 artifacts are not changed.

## Executive result

1. With fixed finite jerk, finite **acceleration-jump** paths are the wrong representation: an absolutely continuous, piecewise constant acceleration must be constant. Replace them with finite **jerk-jump** paths (continuous piecewise affine acceleration).
2. Under one fixed, explicitly inactive acceleration/speed contract, the worst-profile full-future peak representation gap is Theta(m^-3) for at most m jerk jumps. The lower uses positive, unit-energy profiles, each an actual trigonometric polynomial of degree N+2. The bandwidth grows with N. The electrical observation is now fourth order, which makes its physical qualification stricter than the older third-order example.
3. If profile slopes have a common bound, one additional matched jerk moment improves the uniform upper to O(m^-4). Fixed finite Fourier degree K supplies such a bound. Therefore the preceding Theta(m^-3) worst-profile statement does NOT persist at fixed K in this model. This is an approximation-value statement, not an exact finite-switch theorem.
4. Exact pairwise opposite kernels can be replaced by three pairwise non-opposite kernels, but the construction still has an exact aggregate nullspace cancellation. A generic kernel-norm estimate certifies a sufficient perturbation tolerance shrinking as N^-3; structured perturbations may preserve the gap more broadly. Neither is an open-neighborhood physical robustness theorem.

## 1. Fixed contract and admissible representations

Use T=r=1, theta(0)=0, theta(1)=1, v(0)=v(1)=1, a(0)=a(1)=0, and

    theta'=v, v'=a, a'=j, |j|<=J=1/4,
    |a|<=1, 9/10<=v<=11/10.

The acceleration is absolutely continuous; jerk bounds are almost everywhere. After t=1 continue theta=t, v=1, a=j=0, without a reset. The electrical initial state is zero and common. All competing clocks complete identical work and have identical energy at each port.

The acceleration and speed envelopes above are redundant for the ENTIRE jerk-feasible class, not just for the lower witness. Indeed endpoint acceleration zero gives

    |a(t)| <= J min(t,1-t) <= J/2,
    |v(t)-1| <= integral_0^1 |a(t)|dt <= J/4 =1/16<1/10.

This deliberately inactive contract is essential to the upper proof here. No active-band finite-jerk interpolation theorem is asserted.

Let R(e) be the supremum, over all feasible clocks, of sup_(tau>=0)|y(tau)|. Let R_m(e) restrict j to piecewise constant functions with at most m interior jumps on (0,1), with arbitrary values in [-J,J]. The prescribed return j=0 after 1 is not counted. These are finite jerk arcs, not finite constant-acceleration arcs.

## 2. Moment-saturation lemma

Let u in L-infinity[0,Delta], |u|<=J. For every integer n>=1 there is a bang function u_hat taking values +/-J, with at most n switches inside the cell, satisfying

    integral_0^Delta s^k u_hat(s)ds = integral_0^Delta s^k u(s)ds,
    k=0,...,n-1.

Proof. The set of moment vectors (integral s^k u)_(k=0,...,n) is a compact convex subset of R^(n+1), by weak-star compactness and continuity of the moment maps. Among vectors with the first n prescribed coordinates, maximize coordinate n. This vector is on the boundary of the full moment body, since an interior point could be moved upward while fixing the other coordinates. A supporting hyperplane has a nonzero coefficient vector, hence a nonzero polynomial p of degree at most n. If u_star realizes the maximizing vector, its integral against p attains the maximum over |u|<=J. The maximum is J integral |p|, forcing u_star=J sign(p) almost everywhere. A nonzero polynomial of degree at most n has at most n roots, hence at most n switches. This proof also covers prescribed lower moments on the boundary of their moment body; no interiority of the prescribed moments and no Lagrange-multiplier normality assumption is needed. QED.

This is an existence/compression argument. It does not solve the unknown nonlinear optimal-control problem. A separate constructive note gives an explicit two-interval density realization for n=3.

## 3. Uniform O(m^-3) upper, with positive/work/band preservation

Partition [0,1] into M cells of length Delta=1/M and apply the lemma with n=3 to the original jerk on each cell. The first three moments preserve acceleration, speed and phase at each cell endpoint: their increments depend respectively on integral j, integral (Delta-s)j, and (1/2)integral (Delta-s)^2 j. There are at most 3M+(M-1)=4M-1 jerk jumps globally.

For d=theta_hat-theta, each cell has d=d'=d''=0 at BOTH ends and |d'''|<=2J. Integration from the nearer endpoint yields

    |d(s)| <= (J/3) min(s^3,(Delta-s)^3),
    ||d||_infinity <= J Delta^3/24.                         (U1)

The assembled replacement is a globally admissible finite-jerk clock. It obeys the same jerk bound and the same initial/final acceleration, speed and phase. Consequently it satisfies the global redundant envelopes proved in Section 1, including every intermediate time. Positive speed and all per-port completed work/energy are retained exactly.

Let p_j=e_j(theta)v, 0<=e_j<=e_max,j, with primitive E_j. Assume h_j is locally absolutely continuous, h_j and h_j' are integrable on [0,infinity), h_j(0) is finite, and any common deterministic additive output is bounded. These hypotheses make both full-future peak values finite. (The difference estimate itself does not require h_j in L1, but subtracting possibly infinite risk values would be invalid without a bounded-response hypothesis.) Integration by parts in the output difference gives, at any tau>=0,

    Delta y(tau)= sum_j h_j(0) Delta E_j(tau)
                   + integral_0^tau h_j'(tau-t) Delta E_j(t)dt,

where Delta E_j vanishes before time 0 and after time 1. Thus, with

    B=sum_j e_max,j (|h_j(0)|+||h_j'||_L1(0,infinity)),

    sup_tau |Delta y(tau)| <= J B/(24 M^3).                 (U2)

The supremum norm is 1-Lipschitz. Compressing arbitrarily near-optimal clocks proves, for m>=3,

    0<=R(e)-R_m(e) <= [J B/24]/floor((m+1)/4)^3.            (U3)

No e_j' or workload bandwidth bound is used. This upper also holds for non-opposite kernels and any bounded common deterministic initial/idle response, because those cancel in output differences.

## 4. A fixed finite-jerk full-future lower

### 4.1 Fixed output, positive profiles, exact Fourier degree

Fix

    h1(s)=h(s), h2(s)=-h(s), h(s)=s^3 exp(-s), s>=0.

The transfer is 6/(z+1)^4. Its relative degree four is substantive: h(0)=h'(0)=h''(0)=0, h'''(0)=6. This is a stable synthetic filtered observation, not a validated raw generator-frequency transfer.

Put A=1/100, k=2*pi*N, and

    Q(x)=(1-cos(2*pi*x))^2
         =3/2-2cos(2*pi*x)+(1/2)cos(4*pi*x),
    P_N(x)=-(A/k)Q(x)sin(kx),
    e1,N=1+P_N'/2, e2,N=1-P_N'/2.                         (L1)

These are smooth, period-one trigonometric polynomials. Each e_j has exact degree N+2, not just finite effective bandwidth. Set

    Q0=4, Q1=6*pi, Q2=16*pi^2, Q3=48*pi^3.

They bound the corresponding sup derivative norms. Since |P_N'|<=A(Q0+Q1/k)<=7A<1/2,

    3/4<=e1,N,e2,N<=5/4, integral_0^1 e1,N=integral_0^1 e2,N=1.

The load stays positive and continues periodically after the service deadline. No post-deadline forcing is discarded. Q,Q',Q'',Q''' vanish at every integer.

### 4.2 Exact all-time formula and finite-jerk-arc upper

Let t(x) invert the positive clock. For every tau>=0, b=theta(tau),

    y_N,j(tau)=-(A/k) integral_0^b F_tau(x)sin(kx)dx,
    F_tau(x)=h'(tau-t(x))Q(x)/v(x).                        (L2)

This includes the nominal continuing cycles after t=1. Set H_r=h^(r)(tau-t(x)). On a constant-jerk interval,

    F' = -H2 Q/v^2 +H1 Q'/v -a H1 Q/v^3,
    F''= H3 Q/v^3 -2H2 Q'/v^2 +3a H2 Q/v^4
          +H1 Q''/v -2a H1 Q'/v^3 +3a^2 H1 Q/v^5
          -j H1 Q/v^4.                                  (L3)

F(0)=F(b)=0. Also F'(0)=F'(b)=0, since Q,Q' vanish at x=0 and h'(0)=h''(0)=0 at x=b. Three integrations by parts, the last in bounded variation, imply

    |y_N,j(tau)| <= A/k^4 ( |F''(0+)|+|F''(b-)|
                                      +TV(F'';(0,b)) ).    (L4)

The initial term is zero. The final term is bounded by B0=6Q0/l^3, l=9/10, since F''(b-)=6Q(b)/v(b)^3. The nonzero third-integration upper boundary is explicitly retained.

A jump in jerk contributes -Delta j H1 Q/v^4 to F''. Thus m interior jerk jumps contribute at most 2J m S, where

    S=M1 Q0/l^4, M1=3>=sup|h'|.

The prescribed change to zero jerk at t=1 has zero atom because Q(theta(1))=Q(1)=0. No jumps arise at subsequent nominal periods.

For completeness, the continuous-variation constant C_cont is exactly specified by a finite monomial rule, avoiding an omitted differentiation. Represent each of the seven terms of F'' by (c,r,s,p,q,d) for

    c H_r Q^(s) a^p j^q v^-d.

The seven records are

    ( 1,3,0,0,0,3), (-2,2,1,0,0,2), ( 3,2,0,1,0,4),
    ( 1,1,2,0,0,1), (-2,1,1,1,0,3), ( 3,1,0,2,0,5),
    (-1,1,0,0,1,4).

On a constant-jerk interval differentiate every record into

    (-c, r+1,s,p,q,d+1),
    ( c, r,s+1,p,q,d),
    ( cp,r,s,p-1,q+1,d+1) if p>0,
    (-cd,r,s,p+1,q,d+2).

For every resulting record add

    |c| Q_s K_r J^q l^(1-d)

to C_cont, using |a|<=1, dx=v dt, and

    K1=54 exp(-3), K2=24, K3=48, K4=90,
    K_r >= integral_0^infinity |h^(r)(s)|ds.

The first K value is exact total variation of h; the others follow by integrating absolute polynomial-coefficient bounds. Every integral of a lagged kernel derivative is bounded by K_r uniformly in tau. This proves

    R_N,m <= A/[(2*pi)^4 N^4] (2J m S+C0),
    C0=B0+C_cont.                                         (L5)

### 4.3 Explicit smooth feasible witness

Set d0=6(2*pi)^3 and

    theta_N(t)=t+eta_N(t), eta_N(t)=J Q(Nt)/(d0 N^3),
    v_N(t)=1+J Q'(Nt)/(d0 N^2),
    a_N(t)=J Q''(Nt)/(d0 N),
    j_N(t)=J Q'''(Nt)/d0,            0<=t<=1.             (L6)

This clock is smooth and has |j_N|<=J. All six endpoint phase/speed/acceleration constraints hold exactly, since Q,Q',Q'' vanish at integers. The bound from Section 1 guarantees the band for every N. The witness itself need not be a finite-jerk-arc trajectory; it is an admissible member of the unrestricted class.

At tau=1, put

    w(t)=h'(1-t), g(t)=w(t)Q(t), I=integral_0^1 g(t)dt>0.

On [1/3,2/3], Q>=9/4 and w>=8/(27e), so

    I>=I0=2/(9e)>0.                                      (L7)

The mean identity

    integral_0^1 Q(s)cos(2*pi*s)ds=-1

shows that the leading first variation is positive:

    y_N,j_N(1)= A J I/(d0 N^3)+O(N^-4).                  (L8)

Here is a fully specified error bound. Let G1>=||g'||_infinity and G3>=||g'''||_L1[0,1]. The choices

    G1=7Q0+3Q1,
    G3=Q0 K4+3Q1 K3+3Q2 K2+Q3 K1

are valid: sup|h''|<7, sup|h'|<3. Define

    C_R=8/(e*d0^2) [2*pi*Q0+2Q1+Q2/(2*pi)],
    C_star=G3/(2*pi)^4
             +J[5G1/d0+2Q1/(pi*d0*e)] +J^2 C_R.

Then for every N>=1,

    |y_N,j_N(1)-A J I/(d0 N^3)| <= A C_star/N^4.          (L9)

Proof of the three error contributions:

- The nominal zero-state output is -A/k integral g sin(kt). Since g,g',g'' vanish at both endpoints, three integrations give magnitude <=A G3/k^4.
- In the first variation, -A integral g cos(kt) eta_N has the stated mean, with averaging error <=5A J G1/(d0 N^4): the mean-zero periodic factor (Q cos+1)/d0 has L1 norm at most 5/d0. The remaining P_N' term has magnitude <=2A J Q1/(pi*d0*e*N^4), using integral_0^1 w=h(1)=1/e.
- Taylor's theorem bounds the nonlinear remainder by (1/2)||P_N''|| ||eta_N||_infinity^2/e. Here ||P_N''||<=A(kQ0+2Q1+Q2/k), ||eta_N||<=4J/(d0 N^3). It is <=A J^2 C_R/N^5 and therefore <=A J^2 C_R/N^4. No small-jerk limit is taken; J stays fixed.

Consequently, if

    N0=ceil(2*d0*C_star/(J*I0)),

then

    R_N>=A J I0/(2*d0*N^3),                  N>=N0.      (L10)

For arbitrary admissible bounded jerk, F' is absolutely continuous and the formula for F'' in (L3) still holds almost everywhere. Two integrations by parts give |y|<=A*k^-3 integral |F''|. The same seven-record integration bound supplies a constant C2 independent of N, tau and the clock. Thus R_N<=A C2/[(2*pi)^3 N^3]; together with (L10), the actual risk scale is Theta(N^-3), not merely a one-sided decaying witness.

### 4.4 Full-peak gap and matching exponent

Define positive constants

    alpha=pi*I0/(24 S), beta=C0/(2J S),
    gamma=A J I0/(4d0).

For N>=N0 and m<=alpha*N-beta, (L5) and (L10) imply

    R_N-R_N,m >=gamma/N^3.                               (L11)

The comparison is a full-future peak comparison: (L5) bounds EVERY observation of EVERY restricted clock, while (L10) supplies one attained observation of one admissible unrestricted clock. No assumption about the maximizing observation time is made.

Taking N_m=max(N0,ceil((m+beta)/alpha)) yields Omega(m^-3). Combining with (U3), with e_max,j=5/4 and h1=+h,h2=-h, proves

    sup_(N>=1) [R_N-R_N,m]=Theta(m^-3).                    (L12)

Equivalently the worst-profile epsilon-accurate finite-jerk-arc representation count is Theta(epsilon^-1/3). The common upper constant uses B=(5/2)K1=135e^-3. These are representation-of-value facts only. The witness has a short trigonometric formula and does not force computational runtime proportional to its oscillation count.

## 5. Fixed workload slope/bandwidth gives a strictly faster upper

Retain Section 3's integrability and bounded-response assumptions. Assume additionally all e_j are C1 with ||e_j'||<=L_j, h_j are C2 with h_j(0)=0, and M1,j=sup|h_j'|, M2,j=sup|h_j''| finite. Use n=4 moment matching per service cell. This preserves all states at cell endpoints as before, hence exactly the same positive/work/energy/band feasibility. There are at most 5M-1 global jerk jumps. It also gives

    integral_cell (theta_hat-theta)dt=0,                  (S1)

because this integral equals (1/6) integral_cell (Delta-s)^3(j_hat-j)ds.

Continue writing d=theta_hat-theta and E_delta=E(theta_hat)-E(theta). Taylor's theorem gives

    E_delta=e(theta)d+r, |r|<=L_j d^2/2.

For each fixed observation time tau, split [0,min(tau,1)] into whole service cells and at most ONE incomplete cell. The weight f(t)=h_j'(tau-t)e_j(theta(t)) is Lipschitz on this interval with

    Lip(f)<=e_max,j M2,j+L_j u M1,j, u=11/10.

On each whole cell subtract f at the cell's left endpoint and use (S1); on the incomplete cell use |f|<=e_max,j M1,j. With (U1), sum these bounds and bound the quadratic remainder directly. Uniformly for every tau>=0,

    |Delta y(tau)| <= C4 Delta^4+C6 Delta^6,
    C4=(J/24) sum_j [e_max,j M2,j+L_j u M1,j+e_max,j M1,j],
    C6=(J^2/1152) sum_j L_j M1,j.                         (S2)

For general T, the whole-cell and quadratic terms receive a factor T; here T=1. For tau>=1 there is no incomplete-cell term, so its inclusion is conservative. h_j(0)=0 is necessary to this proof of an order-four full-peak bound: a nonzero current-phase boundary otherwise remains order three.

Thus for m>=4,

    0<=R(e)-R_m(e)
       <= C4/floor((m+1)/5)^4+C6/floor((m+1)/5)^6.         (S3)

This is a uniform O(m^-4) upper for a bounded-slope workload class, including fixed-bandwidth trigonometric profiles. No derivative of jerk is assumed. No exact optimizer switch bound follows.

Verified optional constant improvement (the conservative formulas above remain unchanged): define on each cell D(t)=integral_(cell left)^t d(s)ds. The fourth matched moment gives D=0 at both ends; d,d',d'' also vanish there. Hence D and its first three derivatives vanish at both ends and |D''''|<=2J. Integrating from the nearer endpoint yields ||D||<=J*Delta^4/192. Integrating f*d=f*D' by parts cellwise leaves only one possible incomplete-cell boundary and integral f'*D. Therefore C4 in (S2)-(S3) may be replaced by C4/8, with C6 unchanged. This sharper constant is not required for either exponent or the diagnostic conclusions.


For a period-one trigonometric polynomial e of degree at most K, 0<=e<=e_max, its Fourier coefficients satisfy |c_n|<=e_max, and therefore the elementary bound

    ||e'||<=sum_(|n|<=K) 2*pi*|n| |c_n|
            <=2*pi*e_max*K*(K+1)

gives a uniform L_j. This does not need an external Bernstein inequality. Hence for fixed K the constants in (S3) are fixed, and a uniform Omega(m^-3) gap is impossible on this contract.

The lower family has exact degree N+2, so fixing K permits only N<=K-2. Its lower regime m<=alpha*N-beta consequently stops at m<=alpha*(K-2)-beta. This transparent cutoff is stronger than calling each member merely smooth. A uniform C1 bound obtained by scaling A_N=A0/N similarly destroys the fixed-amplitude leading N^-3 scale; the lower would scale N^-4. These observations neither establish a matching fixed-K m^-4 lower nor rule out faster rates or exact finite bounds under further structure.

### 5.1 Matching bounded-slope rate by exact amplitude rescaling

Replace A in (L1) by A/N, while keeping J, the kernels and every clock constraint fixed. The derivative of each profile now satisfies the N-independent bound

    ||e_j,N'|| <= L_star=(A/2)[2*pi*Q0+2Q1+Q2/(2*pi)].

Positivity and unit energy still hold. Because the constant two-port baseline cancels exactly and the common initial state is zero, EVERY output is exactly 1/N times its former value, for EVERY clock and observation. Thus both R_N and R_N,m scale by exactly 1/N, and (L11) becomes

    R_N-R_N,m >=gamma/N^4

under exactly the same condition N>=N0, m<=alpha*N-beta. The constants defining that condition do not depend on A. Choosing N_m as before gives Omega(m^-4). Combining with (S3) proves that over an amplitude-bounded, uniformly L_star-slope-bounded workload class containing this rescaled family,

    sup_e [R(e)-R_m(e)] =Theta(m^-4).

The bandwidth remains N+2 and is unbounded across the class. Therefore this is NOT a matching lower for fixed finite K. Fixed-K sharpness remains open. A common nonzero additive response would also prevent the exact value rescaling unless separately handled; the present zero-state cancellation model has none.

## 6. Non-opposite kernels and perturbation tolerance

### 6.1 Exact three-port realization without pairwise opposite kernels

Let g(s)=s^4 exp(-2s) and choose

    h1=h, h2=-h+g, h3=-g,
    e1=1+P_N'/2, e2=e3=1-P_N'/2.

No pair of kernels is proportional or opposite, and all are fixed stable finite-dimensional kernels. All three profiles are positive and have cycle energy one. Nevertheless

    h1*p1+h2*p2+h3*p3 = h*(p1-p2)

in convolution notation, since p2=p3. The complete earlier output and lower theorem carry over exactly. This removes a literal two-opposite-port presentation, but it DOES NOT remove artificial cancellation: h1+h2+h3=0 is an exact common-mode nullspace, and the correlated second/third profiles are engineered. A network realization and robustness to independent profile changes remain unproved.

### 6.2 Quantified model-error boundary

For perturbed kernels h_j+delta h_j, common initial/idle-output perturbation bounded by delta_init, and unchanged workloads/clocks, powers are bounded by u e_max,j at all times. Thus

    sup_(j feasible,tau>=0)|y_tilde-y|
       <=delta_out=delta_init+u sum_j e_max,j ||delta h_j||_L1.

Both unrestricted and restricted absolute-peak values move by at most delta_out. A gap G_N is therefore retained at least as

    R_tilde_N-R_tilde_N,m >=G_N-2delta_out.

For G_N=gamma/N^3, delta_out<=gamma/(4N^3) retains a gap at least gamma/(2N^3). The tolerance shrinks at exactly the scale of the theorem's certified gap. This is a finite-instance robustness result, NOT a fixed-radius open-neighborhood asymptotic lower.

Subtracting a nominal-clock response does not automatically repair a common-mode perturbation: if h1+h2 is nonzero and e1+e2 is constant, the common-mode input is proportional to v(t), and nominal subtraction leaves a convolution of v(t)-1. It remains clock dependent. An arbitrary common homogeneous response can also dominate the absolute peak. Both must be included unless the output definition explicitly changes to an incremental/differential metric.

## 7. Interpretation limits

- Jerk is uniformly finite and fixed; the hard family still needs unbounded profile bandwidth. Fixed finite bandwidth is addressed by a strictly faster upper, not evaded.
- The jerk upper is positive-speed, exact-work, exact-energy and exact-endpoint preserving for every intermediate time, because the entire jerk class lies strictly inside the other envelopes.
- An active acceleration/speed contract requires a separate interpolation argument; none is hidden in this proof.
- The finite-jerk lower needs a fourth-order output. Physical raw frequency, an arbitrary realistic multi-port grid, and uncertainty at fixed absolute level are not covered.
- The hard output scale goes to zero, and the uncertainty tolerance also goes to zero. Increasing N does not show increasing physical hazard.
- Representation complexity is not solver complexity. Neither the moment lemma nor the existence of a small representation supplies a global optimization oracle.
- The results use classical moment-body, oscillatory-integral and bounded-variation reasoning. Any novelty claim needs a primary-literature comparison.
