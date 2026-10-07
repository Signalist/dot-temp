# A matching full-future peak representation lower bound

2026-10-03 UTC. This addendum proves a full-peak value gap directly. It does not transfer a terminal gap without controlling earlier and later observations. It uses a fixed synthetic third-order stable two-port output, an actually active speed band, positive per-port energy profiles, a common service deadline, and continuing nominal operation afterward. It is a finite-arc representation theorem, not a computational-runtime lower bound or a novelty claim.

## 1. Fixed model and precise claim

Fix the clock contract, independently of the workload index N:

    T=r=rho=1,
    theta(0)=0, theta(1)=1, v(0)=v(1)=1,
    theta'=v, v'=a, |a|<=1 almost everywhere,
    l=9/10 <= v <= u=11/10 on [0,1].

For all t>=1, continue the same clock as theta(t)=t, v(t)=1, a(t)=0. Neither phase nor speed is reset. The speed band is genuinely active: the unconstrained central phase envelope reaches speed 1+1/4 and is excluded by u=1.1.

Choose two fixed input kernels

    h1(s)=h(s), h2(s)=-h(s),    h(s)=s^2 exp(-s), s>=0.       (1)

The common initial electrical state is zero, for every clock and every N. No unmodeled homogeneous response is omitted. The transfer associated with h is 2/(z+1)^3: this is a stable third-order scalar observation with h(0)=h'(0)=0, not a claim about a raw Kundur generator-frequency transfer. Opposite port signs are a synthetic example until a physical output/port realization is separately justified.

For each integer N>=1 the profiles below obey

    3/4<=e1,N,e2,N<=5/4,
    integral_0^1 e1,N = integral_0^1 e2,N =1,
    p_j(t)=e_j,N(theta(t))v(t)>0.

Both ports therefore consume exactly one unit of energy and complete one unit of common useful progress by t=1, for every permitted clock. They continue positive periodic nominal loading after t=1. Their difference input is generally nonzero after t=1, so the later output is not merely a homogeneous free response.

Define the entire-future absolute peak and its m-jump restriction by

    R_N = sup_{a feasible} sup_{tau>=0}|y_N,a(tau)|,
    R_N,m = sup_{a feasible, piecewise constant with <=m jumps on (0,1)}
                    sup_{tau>=0}|y_N,a(tau)|.                (2)

The restricted controls may use any constant values in [-1,1], including coasting; this is stronger than restricting only bang controls. The prescribed continuation a=0 after 1 is common to both classes.

There are explicit positive constants, independent of N, m, a and tau, such that

    R_N >= c/N^2                         for all sufficiently large N,
    R_N,m <= C*(m+1)/N^3                 for every N>=1 and m>=0.       (3)

Together with the active-band compression upper proved in `../theory_active/ACTIVE_SPEED_BAND_THEOREM.md`, these imply

    sup_{N>=1} [R_N-R_N,m] = Theta(m^-2),       m -> infinity.          (4)

Thus this fixed positive-amplitude/unit-energy workload family requires and admits Theta(epsilon^-1/2) finite acceleration arcs in the worst case for epsilon-accurate **full-future peak value representation**. It says nothing about the runtime of algorithms using symbolic, Fourier, oracle, or other representations.

## 2. Fixed smooth positive profiles

Use the period-one flat bump

    chi(x)=exp(4-1/[x(1-x)]) for 0<x<1,
    chi(0)=chi(1)=0,

extended periodically. On one period put Q(x)=chi(x)exp(1-x), and extend Q periodically as well. All derivatives match at the endpoints because chi is flat. Therefore Q is smooth and periodic, despite the nonperiodic-looking exponential within a single cell.

Use the previously audited analytic derivative bounds

    ||chi||_infinity<=1,  ||chi'||_infinity<=L1=16,
    ||chi''||_infinity<=L2=416.

These imply the N-independent periodic bounds

    Q0=exp(1),    Q1=17 exp(1),    Q2=449 exp(1),
    ||Q^(j)||_infinity<=Qj, j=0,1,2.                       (5)

Fix A=1/100, k=2*pi*N, and set

    D_N(x)=-(A/k)Q(x)sin(kx),
    e1,N(x)=1+D_N'(x)/2,   e2,N(x)=1-D_N'(x)/2.             (6)

Because N is integer these are smooth period-one profiles. Their derivative difference satisfies

    |D_N'| <= A[Q0+Q1/(2*pi)] < 1/2.

For example exp(1)<3 and pi>3 already prove the last inequality with ample margin. Hence the displayed [3/4,5/4] profile bounds hold. Integrating D_N' over one period gives zero, so each port's cycle energy is exactly one. No waveform bandwidth or uniform derivative bound for the e_j,N is imposed; this is the same amplitude-only information class used in the representation upper.

### Sign convention

With the chosen ordering (+h,-h), the aggregate forcing is D_N'(theta)v=d[D_N(theta)]/dt. With the earlier paper's ordering (-h,+h), every y in this addendum changes sign. The absolute-peak conclusions are identical, but the positive sign of the high-switch witness below uses (+h,-h).

## 3. Exact all-time phase formula

Since D_N(0)=0 and h(0)=0, integration by parts in the physical power convolution gives, for every tau>=0,

    y_N,a(tau) = integral_0^tau h'(tau-t)D_N(theta(t))dt
      = -(A/k) integral_0^{theta(tau)} F_tau(x)sin(kx)dx,
    F_tau(x)=h'(tau-t(x))*Q(x)/v(x),                       (7)

where t(x) is the inverse of the entire continuous clock and v(x)=v(t(x)). This integral includes **all** subsequent nominal cycles after t=1. It is not a difference relative to a reference with its periodic baseline discarded.

In particular, D_N is the primitive difference **between the two port profiles**, not the clock-minus-reference Delta E used in the main peak note. D_N(theta(t)) continues oscillating after t=1 and must never be extended by zero.

The inverse exists because v>=l>0 globally (v=1 after 1). Its almost-everywhere derivatives obey

    dt/dx=1/v,     dv/dx=a/v.

At b=theta(tau), F_tau(b)=0 because h'(0)=0; at x=0, F_tau(0)=0 because Q(0)=0. These are the endpoint cancellations responsible for an extra inverse-frequency factor. They are substantive relative-degree/profile assumptions, not properties of every grid output.

## 4. Uniform low-switch upper for every observation time

Write h',h'',h''' at lag tau-t(x), and Q,Q',Q'' at x. On each constant-acceleration arc,

    F_tau'=V-aW,
    V=-h'' Q/v^2+h' Q'/v,
    W=h' Q/v^3.                                            (8)

First integrate (7) against sin. Its endpoint term is zero by Section 3. Then integrate against cos in the bounded-variation sense:

    integral_0^b F_tau sin(kx)dx = (1/k)integral_0^b F_tau' cos(kx)dx,
    |y_N,a(tau)| <= (A/k^3) [ |F_tau'(b-)|
                                 +TV(F_tau';(0,b)) ].      (9)

The upper endpoint generally survives the second integration:

    F_tau'(b-)=-h''(0)Q(b)/v(b)^2=-2Q(b)/v(b)^2.

Thus it is bounded by

    B=2Q0/l^2.                                             (10)

The sine factor at b may vanish at an integer phase but must not be dropped for a general observation. The lower second-integration boundary is zero because sin(0)=0; in fact Q and Q' are both zero there.

### 4.1 Continuous variation and switch atoms

Direct differentiation on a constant-a phase interval yields

    (V-aW)' = h''' Q/v^3 -2h'' Q'/v^2 +3a h'' Q/v^4
                +h' Q''/v -2a h' Q'/v^3 +3a^2 h' Q/v^5.   (11)

Define finite kernel constants

    Hj = integral_0^infinity |h^(j)(s)|ds, j=1,2,3,
    M1 >= sup_{s>=0}|h'(s)|.

Using |a|<=1, v>=l, and dx=v dt, the integral of the absolute continuous part in (11) is at most

    C_cont = (Q0/l^2)H3
              +(2Q1/l+3Q0/l^3)H2
              +(Q2+2Q1/l^2+3Q0/l^4)H1.                    (12)

The crucial point is that every time integral is of a lagged kernel derivative over a subset of [0,infinity), and is therefore at most Hj. The bound is independent of tau, even when theta(tau) crosses arbitrarily many periods of Q.

At an acceleration jump, v,V,W remain continuous and F_tau' has atom -Delta a*W. A clock with m interior jumps before t=1 has total jump magnitudes at most 2m. Extending it by a=0 after 1 adds at most one more unit of variation. Set

    S=M1 Q0/l^3.

Then the total atomic contribution is at most (2m+1)S. In this special flat-periodic construction W vanishes at phase 1, so the return-to-zero atom actually contributes zero; retaining +1 is a harmless conservative allowance. There is no extra contribution from infinitely many nominal periods, because a is identically zero after 1 and Q is smooth at every period boundary.

Combining (9)-(12) proves the all-time upper

    sup_{tau>=0}|y_N,a(tau)|
       <= A/[8*pi^3*N^3] * [2m*S+C0],
    C0=B+C_cont+S.                                         (13)

This proves the restricted-value upper in (3). It applies to arbitrary bounded piecewise-constant accelerations, not just bang or bang/coast controls. It also controls the nominal continuing periodic baseline (take a=0, m=0). No unaccounted post-T peak can defeat the comparison.

### 4.2 Fully explicit conservative constants

For h=s^2 exp(-s),

    h'=(2s-s^2)exp(-s),
    h''=(2-4s+s^2)exp(-s),
    h'''=(-6+6s-s^2)exp(-s).

One can use

    H1=8 exp(-2),    H2<=8,    H3<=14,    M1=1.             (14)

The first equality is the total variation of h, which rises from zero to 4 exp(-2) at s=2 and falls to zero. The next inequalities integrate the absolute polynomial coefficient bounds with integral s^j exp(-s)=j!. For M1, on [0,2], h'<=2s exp(-s)<=2/exp(1)<1; on [2,infinity), |h'|<s^2 exp(-s)<=4/exp(2)<1.

Together with l=.9 and (5), these give approximately

    S=3.7287816577,
    B=6.7118069839,
    C_cont=2416.4133134529,
    C0=2426.8539020944.                                    (15)

The exact definitions, not these rounded decimals, specify the bounds. They are deliberately conservative; a large sufficient index is acceptable for an asymptotic representation theorem and is not evidence of useful engineering margins.

## 5. A feasible high-switch clock has a full-peak lower of order N^-2

On [0,1], choose

    a_N(t)=sign(cos(2*pi*N*t)).

It has 2N interior jumps. Each cell of length 1/N is the clamped +,-,+ acceleration bridge, so both acceleration moments vanish cellwise. Hence it satisfies the exact endpoint phase and speed contract. Its phase perturbation and speed obey

    theta_N(t)=t+eta_N(t),
    eta_N(t)=N^-2 b({Nt}),
    0<=eta_N<=1/(16N^2),       |v_N-1|<=1/(4N),             (16)

where b is the unit clamped phase envelope. Thus it respects the active [.9,1.1] band for every N>=3. Continue theta=t, v=1 after t=1 exactly as required.

At tau=1 define

    w(t)=h'(1-t),
    g(t)=w(t)Q(t)=(1-t^2)chi(t),
    I_g=integral_0^1 g(t)dt>0.                             (17)

The equality uses h'(u)=exp(-u)(2u-u^2). The nominal output driven by the periodic input, including its zero-state startup transient, is not necessarily zero at this time:

    J0=y_N,0(1)=-(A/k) integral_0^1 g(t)sin(kt)dt.

Because g and all its derivatives are flat at both endpoints, two integrations give

    |J0|<= A*(L2+4L1+2)/k^3.                              (18)

The first variation about the nominal phase is

    L_N=integral_0^1 w(t)D_N'(t)eta_N(t)dt
      =-A integral_0^1 g(t)cos(kt)eta_N(t)dt
        -(A/k) integral_0^1 (1-t^2)[chi'(t)-chi(t)]
                                      sin(kt)eta_N(t)dt.   (19)

The exact cell mean is

    integral_0^1 b(s)cos(2*pi*s)ds=-1/(2*pi^3).

It follows by integrating twice and using b''=sign(cos(2*pi*s)), b=b'=0 at the endpoints. Cellwise averaging, with ||g'||<=L1+2 and ||b cos-mean||_L1<=1/8, gives

    |L_N-A I_g/(2*pi^3*N^2)|
      <= A/N^3 * [(L1+2)/8+(L1+1)/(32*pi)].                (20)

The second term uses the explicit bound in (16). All constants are independent of N.

### 5.1 Nonlinear remainder at fixed rho=1

The nonlinearity is not ignored. Since

    ||D_N''|| <= A[kQ0+2Q1+Q2/k],

Taylor's theorem in the exact output integral gives

    |y_N,a_N(1)-J0-L_N|
      <= ||D_N''|| * integral_0^1 |h'(1-t)|dt /(512*N^4).

Here h'>=0 on [0,1] and integral_0^1 h'=h(1)=exp(-1). Combining this with (5) yields

    remainder <= A/[512*N^4]
                       *[2*pi*N+2(L1+1)+(L2+2L1+1)/(2*pi*N)].       (21)

There is no small-rho limit: rho is fixed at one. The small phase excursion arises from the high-frequency feasible clock itself.

Let

    C_star=(L1+2)/8+(L1+1)/(32*pi)
           +(L2+4L1+2)/(8*pi^3)
           +[2*pi+2(L1+1)+(L2+2L1+1)/(2*pi)]/512.           (22)

Equations (18)-(21) prove for all N>=1

    |y_N,a_N(1)-A I_g/(2*pi^3*N^2)|<=A C_star/N^3.         (23)

On [1/3,2/3], chi>=exp(-1/2) and 1-t^2>=5/9. Hence

    I_g>=I0=5 exp(-1/2)/27>0.

Choose

    N0=max(3, ceil(4*pi^3*C_star/I0)).                     (24)

With L1=16,L2=416, C_star is approximately 4.5805065977 and N0=5058 is sufficient. Then

    R_N >= y_N,a_N(1) >= A I0/(4*pi^3*N^2),    N>=N0.      (25)

The lower uses an actual finite-time feasible output, while (13) controls every observation time for every low-jump clock. This is the missing logical step that a terminal-only lower did not supply.

## 6. Actual full-peak optimal-value gap

Define fixed constants

    alpha=I0/(2S),     beta=C0/(2S),
    gamma=A I0/(8*pi^3)>0.

For N>=N0 and m<=alpha*N-beta, (13) and (25) imply

    R_N-R_N,m >= gamma/N^2.                               (26)

Indeed the entire-future restricted peak is then at most half the finite-time feasible lower. The proof does not assume where a low-jump clock peaks and does not discard its nominal post-service forcing.

For each m take

    N_m=max(N0, ceil((m+beta)/alpha)).

Then (26) gives the explicit worst-profile lower

    sup_N[R_N-R_N,m] >= gamma/N_m^2.

Once the N0 branch is inactive, the convenient form is

    sup_N[R_N-R_N,m]
       >= gamma*alpha^2/(m+beta+alpha)^2 = Omega(m^-2).     (27)

Using the conservative constants above, alpha is about .01506129, beta about 325.42183, and gamma about 4.52814e-6. These numbers concern a proof normalization, not actual Hz, MW, or a claimed deployment-scale violation.

### 6.1 Matching active-band upper for the same infinite-horizon peak

The active-band bridge theorem supplies, for any feasible original clock and M service cells, a band-feasible bang/coast replacement with at most 5M-1 acceleration jumps and

    sup_[0,1]|theta_hat-theta|<=1/(8M^2).

Its phase and speed agree at t=1, so both clocks have identical nominal continuation. Apply the energy-primitive identity to their difference, retaining the early h_j(0) term if present and using the common endpoint after t=1. For all tau>=0,

    |y_hat(tau)-y(tau)|
      <= (1/(8M^2))*sum_j e_max,j*(|h_j(0)|+||h_j'||_L1(0,infinity)).

Here h_j(0)=0, e_max,j=5/4, and ||h_j'||_1=8 exp(-2). Thus

    sup_tau |y_hat-y| <= (5/(2 exp(2)))/M^2.               (28)

The supremum norm is 1-Lipschitz, so the same constant bounds the loss of an absolute peak. Apply the construction to an arbitrarily near-optimal original clock; actual attainment of the infinite-horizon supremum is not required. For m>=4, take M=floor((m+1)/5) to obtain

    0<=R_N-R_N,m
      <= [5/(2 exp(2))]/floor((m+1)/5)^2                  (29)

uniformly in N. Combining (27) and (29) proves (4) on the genuinely active fixed band. This use of the bridge theorem is an upper **existence of representation** statement, not an algorithm for finding an unknown optimizer.

## 7. Risk magnitude and scope

For completeness, even without finite variation of a, one phase integration by parts in (7) gives

    sup_tau |y_N,a(tau)|
      <= A/(4*pi^2*N^2)
          *[(Q0/l)H2+(Q1+Q0/l^2)H1].                     (30)

This uses |a|<=1 and dx=v dt, and holds for every admissible measurable control. Together with (25), the true worst peak satisfies R_N=Theta(N^-2). Increasing workload complexity makes this example harder to represent **relatively/exactly** while the absolute risk decreases; it does not produce growing danger.

Important limits:

- The relative-degree-three synthetic output is essential to this particular N^-3 low-jump bound. With h'(0)!=0 the first phase integration can leave an O(N^-2) observation boundary, so the proof cannot be silently transferred to raw generator frequency or a generic second-order output
- The proof uses zero common electrical initial state. A different common homogeneous response could dominate both peak values and destroy the value-gap argument; it needs separate treatment. A continuing nominal periodic input has already been included, not suppressed
- The band is fixed and genuinely active, but the high-switch witness stays in a shrinking interior neighborhood. No lower bound is claimed for every conceivable active contract, such as a singleton-speed band
- Controls are piecewise constant in acceleration with m jumps. The result neither forces every exact active-band optimizer to be bang/coast nor bounds all possible algorithmic descriptions
- Smoothness and positivity are pointwise for each profile. The amplitude-only family has no uniform workload bandwidth or slope restriction
- The mathematical constants are exact expressions; their printed decimal evaluations and numerical checks are not outward-rounded interval certificates
- Perfect-spline/moment replacement, oscillatory integration by parts, bounded variation, and nonlinear-width lower-bound constructions are classical. The candidate full-peak statement must be compared with nearby prior results before any historical novelty claim

The relevant earlier sources and limitations are listed in the main peak theorem and active-band theorem. This addendum closes a specific missing full-peak lower-bound argument for this fixed model; it does not establish a new general robust-control method.

## 8. Reproducible diagnostics and review

`verify_full_peak_lower.py` records seeded-free deterministic checks in `full_peak_lower_diagnostics.json` and `.log`. They use ordinary floating point and do not replace the proofs:

- 72 comparisons of the original power convolution, the first energy/phase identity, and the two-integration BV identity, including active-band five-arc clocks and observations through tau=7.314, agree within 3.62e-15
- The second upper-boundary term is materially nonzero: dropping it changes a tested formula by approximately 1.02727e-4
- The high-switch sequence for N=3,4,8,16,32,64,128 respects the active band; quadrature refinement is stable and N^2*y(1) approaches 4.5236443777e-5 for A=.01
- Independent quadrature gives I_g approximately .2805227384; the proof uses only the conservative analytical I0, not this numerical estimate
- All displayed constant definitions and the sampled inequalities pass the checks

A separate independent mathematical audit checked the full all-time BV argument, high-witness expansion, active-band peak upper and value-gap comparison, and found no material mathematical gap. The audit artifacts are preserved separately in the audit directory. This review is mathematical evidence within the research workflow, not a statement of publication novelty or machine-verified numerical safety.
