# Prefix coupled modulation exclusion and sampled port recovery

## 1 Model and quantifiers

This note strengthens the previous **all-allocation** result, not merely a fixed P/Q trajectory check. The physical model and kW/kJ/kA/kV units remain those of the frozen second-round model. Put

    Gp = 1500 V, c = R/(1500 V²), k = L/(3000 V²), K_v = sqrt(1500 Cdc)
    P = Gp i_d, Q = Gp i_q, Z = k(P²+Q²)
    e = (V,0) - R i - L i' - omega L J i
    W' = P - c(P²+Q²) - Z' + b - d, B' = -b
    ||e|| <= sqrt(W)/K_v.

The frozen positive workload d(t) is fixed **pointwise**. There is no scheduling, shedding, slowdown, or work-energy substitution. Fix a comparison cap/floor Pbar,Qbar, with 0<=P<=Pbar<1/(2c) and Q>=Qbar>=0. Initial current, W0, B0 and the initial held-zero port command are common. Let U_C(t) be any valid upper bound on integral b; the maximal positive lag/ramp response is one such bound. Define

    Abar(t) = integral_0^t [Pbar-c(Pbar²+Qbar²)-d] - Zbar(t)+Zbar(0)
    H(t) = W0+Abar(t)+U_C(t).

The comparison current need not itself be feasible or recoverable. All feasible currents are absolutely continuous. Test functions are compactly supported H¹ vector functions; the selected sine-squared window is smooth inside and has zero value and derivative at its support endpoints. Bounded measurable coefficients suffice below. No derivative-closeness premise is imposed on actual P/Q.

For deviations x=Pbar-P>=0 and y=Q-Qbar>=0, set

    m=1-2cPbar>0, q=2cQbar>=0
    g=m x+q y+c(x²+y²), G(t)=integral_0^t g.

Conservation, without any recovery assumption, gives the exact identity

    Wactual(t) = W0+Abar(t)+Cactual(t)-G(t)
                 +k[2Pbar(t)x(t)-x(t)²-2Qbar(t)y(t)-y(t)²].       (1)

Thus replacing Cactual by U_C is favorable to feasibility. This is the coupling missing from a bound that separately grants the full favorable inductor release everywhere and charges all curtailment only against a terminal energy allowance.

## 2 Coupled weak certificate

Let psi be a test and

    a_psi = L psi' - (R I+omega L J)^T psi
    Mbar = integral [psi·(V,0)+a_psi·ibar]
    l_d = a_psi,d/Gp, l_q = -a_psi,q/Gp.

Integration by parts and psi=0 at its boundary give

    integral psi·eactual = Mbar - integral(l_d x+l_q y).           (2)

Choose any bounded positive anchor Y with inf Y>0 and put

    z=||psi||/(2 K_v sqrt(Y)), r(s)=integral_s^T z(t)dt
    base=Mbar-integral ||psi||sqrt(Y)/K_v-integral z(H-Y)
    A_d=l_d+2kzPbar-rm
    A_q=l_q-2kzQbar-rq
    D=kz+rc >=0.                                                 (3)

Every physically feasible allocation satisfies integral psi·e <= integral ||psi||sqrt(W)/K_v. By the supporting-line inequality sqrt(W)<=sqrt(Y)+(W-Y)/(2sqrt(Y)), (1), (2), and Fubini,

    0 >= integral psi·e - integral ||psi||sqrt(W)/K_v
      >= base - integral [A_d x+A_q y-D(x²+y²)].                  (4)

The Fubini identity is integral z(t)G(t)dt=integral r(s)g(s)ds. It preserves the cost of earlier lost net delivery. On portions before the test support, z=l=0 and r>=0, so both A coefficients are nonpositive and these deviations cannot improve the relaxed weak inequality.

### Theorem 1 Prefix-only all-allocation exclusion

For D>0 define

    S0(t) = ((A_d)_+²+(A_q)_+²)/(4D).

At D=0 take S0=0 if A_d,A_q<=0, and +infinity otherwise. If S0 is integrable and

    base - integral S0 >0,                                      (5)

then no allocation satisfying the cap/floor and physical prefix exists. There is **no terminal-energy budget or terminal-state premise**.

Proof: pointwise completion of squares shows A_d x+A_q y-D(x²+y²)<=S0 for all x,y>=0. Combine with (4). Dropping x<=Pbar, the current limit, the lower DC bound, the upper DC bound, buffer inventory limits, recovery, and actual-current derivative restrictions only enlarges the competitor class. No optimizer success/infeasibility assertion is used. The displayed pointwise supremum is attained by x=(A_d)_+/(2D),y=(A_q)_+/(2D) where finite, but this relaxed maximizer is not asserted to be a physical trajectory.

### Theorem 2 Shared finite-budget refinement

If full recovery also supplies integral g=epsilon, or the weaker integral g<=epsilon is known, every lambda>0 gives

    S_lambda = ((A_d-lambda m)_+²+(A_q-lambda q)_+²)
               /[4(D+lambda c)]
    base-lambda epsilon-integral S_lambda >0                    (6)

as a sufficient all-allocation exclusion. The proof adds lambda times the budget and again completes squares. Optimization over lambda is optional. At lambda=0 use Theorem1 and its extended-value convention, never silently substitute zero into an undefined fraction. Weak duality suffices for exclusion; no strong-duality claim for the full physical trajectory set is needed.

The supremum with only the convex quadratic energy budget has classical separable convex duality. It is not a new optimization principle. In particular, the version without prefix terms D/r gives the old budget-only support relaxation, sharpened by retaining quadratic costs.

### Corollary on the slack scale

If m is uniformly positive and the positive ratios A_d+/m and A_q+/q are bounded (with a compatible zero convention), selecting lambda above their essential sup makes the integral term zero: erosion is at most O(epsilon). On the positive-Q plateau these conditions hold. Thus integrated active-curtailment/inductor benefit need not inherit the old pointwise O(sqrt(epsilon)) amplitude bound or require a slew bound on P deviations. This does not contradict the sharp pointwise square-root example. If Qbar=0 and A_q>0, the reactive term can still scale as sqrt(epsilon); a universal linear-slack theorem is not asserted.

### Optional tighter anchor

One can replace sqrt(W) by phi(U)=sqrt(min{Wmax,U}), use a supporting slope of this concave function, and repeat the proof. Optimizing anchors or the associated convex relaxation may improve the number but is not required for the certified result. No equality with the complete physical feasible set is claimed.

## 3 Frozen 812.5 kvar certificate and monotonicity

For alpha100 kW the first plateau has Pbar=p0-100 and Qbar=beta. Use

    psi(t)=(1,-.102) sin²(pi(t-.0113)/.0126), .0113<=t<=.0239,
    psi=0 elsewhere, Y=H, lambda=0.

These decimal constants are exact rationals; no unverified optimizer output defines the certificate. On this plateau the port upper charge is

    U_C(t)=450t-4.2+.75 exp(-(t-.011)/.005).

The reference Abar includes the entire initial 5 ms ramp and the same rising compute workload, rather than resetting its energy at the start of the test. At beta812.5, 30-digit outward interval arithmetic gives

    Mbar  in [0.00414234408682699...,0.00414234408682699...]
    RHS   in [0.00414206747082466...,0.00414221639432948...]
    S0int in [2.48999696667e-8,2.97826280109e-8]
    gap   in [9.79098694941e-8,2.51716032655e-7] kV s.

`outward_prefix_certificates.json` retains full outward decimal endpoints. It is an interval-arithmetic numerical certificate with independently checked code/export, not a proof-assistant verification. Ordinary optimizer/adaptive-quadrature roots near812.27 remain exploratory and are not rounded into a claimed certified root.

The upper-bound implication for all larger beta follows from **prefix contract nesting**: early Pbar and workload are unchanged, while increasing beta raises Qbar. Any feasible larger-beta trajectory would be feasible for the certified812.5 prefix. The late compensation cap can grow arbitrarily without changing this prefix. Consequently812.5 and every larger amplitude are excluded under the original100J family and under any late-recharge enlargement. A supremum statement can safely use Qsup<=812.5; strict exclusion of the endpoint alone is not mistaken for a numerical strict supremum inequality.

### Ordered parameter robustness and future transfer

The same exclusion holds for any port whose attainable positive prefix charge is no larger. With b(0)=0, scalar comparison supplies this ordering for upper command<=450kW, upward ramp<=30000kW/s, lag tau>=.005s, and initial held-zero delay>=.001s (positive upper commands, same clipped-lag structure). For example it covers the entire box upper command400–450kW, upward ramp25000–30000kW/s, tau5–6ms, delay1–2ms. This is analytic envelope domination, not a finite sweep or a robust-feasible808 claim. It does not give a grid-voltage, R/L/C, PLL, or measurement-error robustness guarantee.

Arbitrary changes strictly after23.9ms, including more recovery power, a longer recovery deadline, or additional future compute work, cannot repair this prefix violation. They must not change the prefix, initial state, or control permissions. This makes recovery-independent exclusion materially stronger than a tight terminal-energy contradiction.

## 4 Exact held-command inner within the same averaged contract

For a zero-order-held command u_j on [t_j,t_j+h_j], with tau fixed and initial b_j,

    b_{j+1}=E_j b_j+(1-E_j)u_j, E_j=exp(-h_j/tau)
    C_{j+1}=C_j+tau(1-E_j)b_j+[h_j-tau(1-E_j)]u_j.               (7)

If |u_j-b_j|<=tau r, no clipping occurs and the derivative magnitude decreases within the cell. The command/power limits and (7) form linear constraints. The same Abar and one-sided modulation polynomials are used. On each cell the exact exponential port lift has b' in[-r,r]; requiring nodal physical slack >=M_j h_j²/8 using the previously proved curvature bounds certifies all intermediate times. This is a standard sparse LP, solved with HiGHS, not a new solver. It changes the control representation from continuously varying commands to implementable held battery-port commands.

At beta808, use25us cells through40ms and100us cells thereafter, with all original events included. The initial1ms is exactly held zero. The LP returned1.856683J uniform inward margin. Its raw floating command exceeded one ramp bound by1.40e-7kW/s and had tiny terminal residuals; those values are not silently relabeled exact. The final witness scales commands by1−1e−6, rounds the base payload to12 decimal places, and makes an analytically exact two-block repair on[.15,.16] and[.18,.19].

For each command cell let w_j=(1-E_j)exp(-(T-t_{j+1})/tau). The uncorrected endpoint satisfies bT=sum u_j w_j and CT=sum h_j u_j-tau bT. A constant correction delta_m over a block has endpoint coefficients B_m=sum_block w_j and C_m=block_duration-tau B_m. Solve the nonsingular2x2 system

    [B1 B2; C1 C2] delta = -[bT,CT].                             (8)

This defines an exact real command. The payload is rational plus (8), not a claim that independently rounding the corrected commands preserves exact zero. The corrections are approximately+6.78473e-12 and−5.15973e-12kW, far smaller than the created actuator slack.

A40-digit outward interval pass on every cell verifies: modulation margin>=1.85297320365J; upper-DC margin>=1.86121733974J; lower-DC margin>=1730.6592137J; command margin>=.4499999948W; ramp margin>=29.99985985W/s; current squared margin>=.9052785327kA². Algebra gives b(T)=C(T)=0; interval evaluation encloses these zeros within1.02e−35kW and5.98e−36kJ. The original analytic gamma root gives total net input minus compute exactly zero, hence W(T)=W0 and B(T)=B0. Common current recovery gives Z(T)=Z0. Zero command and continuing nominal load extend the exact averaged orbit indefinitely.

This is a same-contract battery-port implementation bridge only. AC current/voltage actuation remains the ideal averaged model with known waveform and parameters. The command rate is40kHz in the critical prefix; no claim is made that the earlier10kHz sampled bridge realizes it. h50us and h100us attempts yielded negative inner margins and are retained. They are not all-allocation impossibility results.

## 5 Two implementation obstructions that block overclaims

### Exact instantaneous PWM tracking

For an ordinary finite-level two-level bridge, available voltage directions in the synchronous dq frame are zero and finitely many rotating rays. Exact nonzero constant-dq current on a positive-length interval requires a fixed nonzero e_ref=(V,0)-Ri-omegaLJi. Varying DC voltage only scales the rays and does not change their directions. Equality to that fixed nonzero vector holds only at isolated times. Thus exact constant-dq tracking on such an interval is impossible for the unaveraged finite-switch converter, even though it can be feasible in the averaged convex-voltage model.

The old zero-energy-slack cap/floor conservation rigidity forces the reference P/Q path; on its plateau this obstruction applies. It also explains why literally exact nominal dq orbit recovery cannot be silently equated to return to a periodic switching orbit. This is a standard averaging-versus-switching issue, not an AI-specific theorem. It does **not** prove the100J free-allocation contract impossible, give a positive minimum switching slack, or exclude feedback/tolerance contracts. A proof for finite frequency would need explicitly stated instantaneous or filtered service and periodic-orbit recovery tolerances.

### Unknown lag and exact open-loop reset

Let b'=s(u-b), b(0)=0, with one predetermined bounded u and common finite T. If b(T;s)=0 for every s in a nontrivial positive interval, then

    0=b(T;s)/s=integral_0^T exp(-s(T-t))u(t)dt.

The right side is an entire finite-horizon Laplace transform. Vanishing on an interval forces it to vanish identically; transform uniqueness (or all moments plus polynomial density) implies u=0 almost everywhere. Therefore a nontrivial common open-loop command cannot have exact terminal port reset for a continuum of unknown pure-lag parameters. The result is a classical analytic/ensemble-control specialization, not a new general robust-control theorem. It excludes neither known-parameter feedforward, feedback/adaptation, finitely many parameter tests, nor approximate/asymptotic reset. Ramp-saturated models are not automatically covered by this pure-lag proof.

## 6 Scientific scope

The contribution strengthened here is the physical **prefix delivery versus inductive release coupling** in an all-allocation weak exclusion, plus a sampled-port inner under the exact same averaged service and recovery contract. Supporting tangents, Fubini, scalar comparison, quadratic conjugates, exact ZOH discretization, LP/SOCP and Laplace uniqueness are classical. These are generic converter/actuator facts; persistent computation provides the fixed task context, not a mathematical dependence on artificial intelligence. The exact finite-PWM, unknown-parameter, and actual-device capability gap is explicitly open.

### Exact finite-parameter diagnostic

For four equal5ms holds, let a=exp(−.005/.004), b=exp(−.005/.006), A=−100/(1+a+b), and define commands A(1,−(1+a+b),a+b+ab,−ab). Their cubic p(z)=A(z−1)(z−a)(z−b) gives b(T;tau)=(1−z)p(z), z=exp(−.005/tau), and integral u=.005p(1)=0. Thus both b and C reset exactly at tau4ms and6ms, but at5ms b(T)≈−.126046295110468kW and C(T)≈.00063023147555234kJ. This is an exact-function construction; saved decimals approximate it. It demonstrates why successful parameter corners cannot certify a continuum exact-reset claim.
