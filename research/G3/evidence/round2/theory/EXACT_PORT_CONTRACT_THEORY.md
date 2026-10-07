# Exact prescribed-port admission and energy-tight inequality contracts

Status: conditional mathematical result for the declared averaged converter model. This document does not claim that energy coordinates, convexity, Markov–Lukács representations, Hermite interpolation, or forward/backward reachability are new. See the separate primary-literature audit. Numerical oracle checks are not interval-arithmetic proofs.

## 1. Physical model, units, and scope

Use peak dq variables with nu = 3/2, grid voltage v=(V,0), and import-positive current i=(id,iq). Define grid active import P=nu V id and positive reactive injection support Q=nu V iq. With J=[[0,-1],[1,0]],

    e = v - R i - L i' - omega L J i
    Z = nu L ||i||² / 2
    W' = P - nu R ||i||² - Z' + b - d
    B' = -b

W is DC-capacitor energy, B is buffer inventory, and d(t)>0 is the continuing compute demand. Task timing d(t) is fixed, not optimized or shed. The converter constraints are

    ||i|| <= Imax,
    ||e||² <= kappa² W,
    Wmin <= W <= Wmax.

For the frozen implementation, P,d,b,u are kW; W,B,Z are kJ; i is kA; V,e,Vdc are kV; R is ohms; L is H; time is seconds. Consequently P=1500 V id, loss=1500 R||i||², Z=750 L||i||², W=500 Cdc Vdc², and the inscribed linear SVPWM/min-max-zero-sequence circle ||e||<=Vdc/sqrt(3) gives W >= 1500 Cdc ||e||². Ordinary zero-sequence-free sinusoidal PWM would instead have the stricter ||e||<=Vdc/2 limit. These are exactly the factors in src/model.py, not a change of physical parameters.

The buffer actuator has lower/upper commands l<u, lag tau>0, and asymmetric ramp rates rd,ru>0. If b starts in [l,u], the feasible trajectories of

    b' = clip((command-b)/tau, -rd, ru), command in [l,u]

are exactly the absolutely continuous trajectories obeying

    -rd <= b' <= ru,
    l <= b+tau b' <= u.

Proof: an original command implies these inequalities on the invariant state interval [l,u]; conversely command*=b+tau b' realizes the trajectory, including points on a ramp limit. The invariant-domain assumption matters. If physical power bounds are narrower than [l,u], impose them separately; the oracle below currently assumes they coincide.

A known initial queue command on [0,delay] is a fixed prefix, not a decision. In the frozen model command=b=0 on this prefix, so C=0 exactly. Include its endpoint as a grid event. After T, b(T)=0 and a command continuation of zero keep the buffer on the continuing nominal orbit. If a genuine command pipeline is modeled, its queued post-T commands must also be set to zero before T; the simple initial-held-command model does not silently certify a more elaborate delay state.

## 2. Exact charge-corridor reduction

For a prescribed admissible current path i(t), set

    A(t) = integral_0^t [P(s)-nu R||i(s)||²-d(s)] ds - Z(t)+Z(0)
    C(t) = integral_0^t b(s) ds.

Then W=W0+A+C and B=B0-C exactly. Define the modulation floor M(t)=||e(t)||²/kappa². All electrical/inventory constraints are equivalent to

    max{Wmin-W0-A(t), M(t)-W0-A(t), B0-Bmax}
       <= C(t) <=
    min{Wmax-W0-A(t), B0-Bmin}.

Keep the separate polynomial inequalities rather than differentiating a max/min at a switching event. This avoids introducing artificial nonsmoothness into curvature estimates.

For exact return to common initial DC energy and buffer inventory, C(T)=0 and A(T)=0 are necessary. Also require i(T)=i(0)=i_nominal and b(T)=b(0)=0. These endpoint conditions give continued nominal operation when the prescribed workload and grid port return to their nominal values. The bridge is an equivalence for the ideal averaged model, not a switching-converter tracking claim.

### Recovery-energy obstruction

With constant nominal id0, a zero-integral active-current deviation delta_id and a reactive pulse iq both returning to zero give

    integral [P-loss-d] = -nu R integral [(delta_id)²+iq²] < 0

whenever the deviation is nonzero, nominal d is balanced, and the workload perturbation has zero integral. Hence a nonzero zero-net-grid-energy P/Q service cannot restore both stores: even pure reactive support needs positive loss-compensation import. Buffer capacity cannot cure this energy deficit.

For the declared disjoint service/recharge shapes P=P0+alpha*s+gamma*r, Q=beta*g with integral s=0, write Ss=integral s², Sg=integral g², R1=integral r, R2=integral r², and c=R/(nu V²). Recovery requires

    gamma R1(1-2cP0) - c R2 gamma²
       = c(alpha² Ss + beta² Sg).

The smaller nonnegative quadratic root is the stated loss-compensation tail. A negative discriminant or a current-limited recharge maximum below this requirement is an allocation-independent recovery exclusion.

## 3. Exact actuator endpoint-and-charge cell

Fix a cell of duration h, initial power b0 and terminal power b1 in [l,u]. Define

    a(b)=max(-rd,(l-b)/tau),
    c(b)=min(ru,(u-b)/tau).

Let Fminus(t;b0), Fplus(t;b0) be the forward flows of b'=a(b), b'=c(b). Let Gplus(t;b1) be the reverse-time flow b'=-a(b), and Gminus(t;b1) the reverse-time flow b'=-c(b). The endpoint pair is reachable exactly when

    Fminus(h;b0) <= b1 <= Fplus(h;b0).

For a reachable pair, the pointwise maximal and minimal feasible trajectories are

    b_upper(t)=min{Fplus(t;b0), Gplus(h-t;b1)},
    b_lower(t)=max{Fminus(t;b0), Gminus(h-t;b1)}.

Each pair of envelopes has one crossing, with endpoint crossings allowed. The upper path uses the largest derivative then the smallest; the lower reverses that order. Each segment is ramp-linear or lag-exponential. The min/max paths obey the differential inclusion almost everywhere and have the prescribed endpoints. Every other feasible path is bounded between them by scalar comparison.

Therefore the EXACT one-cell charge set is

    Imin(b0,b1,h) <= DeltaC <= Imax(b0,b1,h),
    Imin=integral b_lower, Imax=integral b_upper.

Sufficiency is constructive: if theta=(DeltaC-Imin)/(Imax-Imin), use b=(1-theta)b_lower+theta*b_upper. The affine ramp and command-strip constraints are convex, so this is a genuine actuator trajectory with exactly the desired charge and endpoints. Handle the degenerate Imin=Imax by taking that unique charge. Concatenating cells preserves b and C and needs no endpoint repair.

The reachable endpoint domain is convex. Imax is concave and Imin convex in (b0,b1), by mixing feasible trajectories. Forward endpoint upper/lower maps are respectively concave/convex. Thus global tangent cuts give valid controller-independent outer approximations. A finite cutting-plane iteration is not an exact-cell solution until all nonlinear reachability and moment residuals have been checked; every valid intermediate tangent relaxation remains an outer bound.

### Pure-lag closed form

If the separate ramp bounds never bind, let D=u-l, E=exp(h/tau), db=b1-b0. On the reachable endpoint domain,

    Imax = l h + D tau log(((b1-l)E+u-b0)/D) - tau db,
    Imin = u h - D tau log(((u-b1)E+b0-l)/D) - tau db.

Together with the linear fixed-h lag endpoint inequalities these are exact exponential-cone constraints. They are not generally SOCP constraints. With finite ramps, the implementation evaluates analytic flow integrals and locates only a scalar crossing by Brent's method.

### Endpoint gradients and valid cuts

If the upper crossing is s, write Imax=integral_0^s Fplus + integral_0^(h-s) Gplus. On differentiating, the crossing-time terms cancel because the two values agree at the crossing. Hence

    d Imax/d b0 = integral_0^s d Fplus/d b0,
    d Imax/d b1 = integral_0^(h-s) d Gplus/d b1.

The analogous formulas hold for Imin. These analytic derivatives, including one-sided boundary super/subgradients, are in exact_cell.py. For an unreachable queried pair, use its returned reachable anchor when constructing a tangent, not the original infeasible endpoints. A tangent taken outside the domain is not justified.

### Cheaper necessary cell bound

Under ramp constraints alone, with Delta=b1-b0 and eta=DeltaC-h(b0+b1)/2,

    |eta| <= ((ru h-Delta)(rd h+Delta))/(2(ru+rd)),
    -rd h <= Delta <= ru h.

This bound is sharp and SOC-representable; it follows by integrating the ramp tent/valley envelopes. Also

    l h <= tau Delta + DeltaC <= u h

is necessary by integrating the command strip. Their conjunction is not sufficient for lag/ramp reachability. For l=-1,u=1,tau=1,rd=ru=1,h=1,b0=b1=0, it permits DeltaC=0.245 (ramp upper bound 0.25), while the exact maximum is 0.22796904633820209. Thus a cheap SOCP outer must not be relabeled exact-cell.

## 4. Paired exact-cell certificates and a sharp O(h²) state tube

Assume all current/workload/voltage formula changes are grid events. On cell k write every physical constraint as a nonnegative scalar slack f_j(t), for example

    W-Wmin, Wmax-W, W-M(t), B-Bmin, Bmax-B.

Each exact-cell lift satisfies b' in [-rd,ru]. For constant V and piecewise-affine i,d, A is cubic and M quadratic, so explicit upper bounds f_j''<=M_jk are available without choosing a controller:

    lower DC:       M_jk=max(0, sup A'' + ru)
    upper DC:       M_jk=max(0, -inf A'' + rd)
    modulation:     M_jk=max(0, sup(A''-M'') + ru)
    lower B:        M_jk=rd
    upper B:        M_jk=ru.

The supremum/infimum on a cell is exact for the known low-degree polynomials. At current-slope jumps, impose both one-sided modulation constraints, and do not apply a smooth-cell curvature bound across the jump.

Chord lemma: if f''<=M in the weak/a.e. sense, then for x=(t-tk)/h,

    f(t) >= (1-x)f(tk)+x f(tk+1) - (M h²/2)x(1-x)
         >= min{f(tk),f(tk+1)} - M h²/8.

Proof: subtract the chord and add (M/2)(t-tk)(tk+1-t); the resulting function is concave and zero at both endpoints.

Consequently:

1. OUTER: exact endpoint-and-charge cells, exact initial queue and terminal recovery, and untightened nodal physical constraints contain every continuously feasible contract. Every feasible outer point has an actual actuator realization whose violation of each continuous constraint is at most M_jk h²/8.
2. INNER: impose the SAME cell sets and endpoint conditions, but require each relevant endpoint slack on each cell to be at least M_jk h²/8. Any envelope-mixture lift is continuously safe under the SAME physical parameters. This inner construction needs no differentiability of the chosen actuator beyond absolute continuity, and preserves recovery exactly.

The gap is an explicit energy/state-tube gap, not automatically an objective/admission gap. The factor 1/8 is sharp: f(t)=M t(t-h)/2 has zero endpoint slacks and midpoint violation -M h²/8. It is realizable by b(t)=M(t-h/2), constant corridor, and b'=M with sufficiently broad command bounds. Since this saturates the ramp endpoint displacement, no different actuator lift can remove the intersample dip in this example.

Under an appropriate local error bound/transversality condition, state-tube accuracy implies O(h²) admission-value accuracy. Without it, only the state-tube result and (under standard compactness) outer subsequential convergence are justified: tangency, nonunique frontier branches, or degenerate active constraints can amplify small state errors. No universal admission-value rate is claimed.

Important endpoint caveat: symmetric tightening can exclude every finite-grid inner witness if a required endpoint has exactly zero physical slack and M_jk>0, even when the physical trajectory is feasible. Consequently no unconditional density of this tightened inner is asserted. An improved convex local condition is to require the entire known chord lower bound

    (1-x)f(tk)+x f(tk+1)-(M_jk h²/2)x(1-x) >= 0 on [0,1].

This is an exact quadratic nonnegativity SOC condition and permits f(tk)=0 when f(tk+1)>=M_jk h²/2. It still needs suitable endpoint compatibility when both endpoints are active. Strict-margin/slater-type assumptions or a more local derivative-aware construction are needed for inner density.

## 5. An independent exact continuous-time SOCP inner

On each cell let b(x) be a quadratic polynomial. C is then cubic, as are W and B; the modulation floor is quadratic. All actuator and physical constraints are polynomial inequalities of degree at most three. A cubic p(x)>=0 on [0,1] has the exact classical representation

    p(x)=x [1,x] Q [1,x]^T +(1-x)[1,x] S [1,x]^T,
    Q,S positive semidefinite 2-by-2 matrices.

This exact cubic-to-SOCP specialization is established explicitly by [Xia and Alizadeh, Sections 2 and 4](https://optimization-online.org/wp-content/uploads/2015/06/4966.pdf). Each 2-by-2 PSD constraint is a Lorentz-cone constraint. Therefore quadratic-buffer-power spline feasibility, continuity, fixed prefix, and exact terminal b/C return form an exact continuous-time SOCP inner. Solver residuals must still be independently checked.

The spline density argument is classical cubic Hermite interpolation of C; see [Van Loan, Cornell numerical-computing text, Section 3.2](https://www.cs.cornell.edu/courses/cs4210/2014fa/CVLBook/CVL3.PDF) for the cubic Hermite construction and h^4/384 error bound, and [NIST DLMF §3.3(vi)](https://dlmf.nist.gov/3.3.vi) for established references. The derivative constant used below follows from the ordinary Hermite Peano kernel and was independently checked in the audit. On an event-aligned cell, take the unique quadratic b_h matching b at both endpoints and its cell integral. This preserves C at every node and terminal recovery exactly. If ||b'''||<=M on that cell, then the Hermite error hierarchy gives

    ||C-C_h|| <= M h^4/384,
    ||b'-b_h'|| <= M h^2/12,
    ||b-b_h|| <= M h^3/24  (a simple conservative bound).

The last bound follows by integrating the derivative-error bound from the closer endpoint. Thus sufficient inherited margins are M h²/12 for the ramps, M h³/24+tau M h²/12 for the command strip, and M h⁴/384 for each energy constraint. The regularity assumption is essential and may fail at an unaligned optimal-control switch. These familiar interpolation bounds are not claimed as new methodology.

## 6. Exact bridge from inequality contracts to all allocations

This section addresses a broader allocation class than fixed P/Q. Let V be constant, R>0, and

    c=R/(nu V²),  k=L/(2 nu V²),
    net(P,Q)=P-c(P²+Q²),   Z=k(P²+Q²).

These displayed coefficients are in consistent SI units. In the frozen kW/kJ/kV/kA convention they are explicitly c=R/(1500 V²) [1/kW] and k=L/(3000 V²) [kJ/kW²]. Convert both coefficients, not only the P/current scaling.

Assume the contract permits ANY absolutely continuous P,Q with

    0 <= P(t) <= Pbar(t) <= Pmax < 1/(2c),
    Q(t) >= Qmin(t) >= 0,

subject to the same converter, buffer, initial queue, fixed workload d(t), and full initial/final W,B,current recovery. The cap/reference paths themselves share the common initial and terminal current. Define the total energy slack

    epsilon = integral_0^T [net(Pbar,Qmin)-d] dt.

Conservation for every recoverable actual allocation gives EXACTLY

    epsilon = integral_0^T {deltaP[1-c(Pbar+P)]
                            +c(Q²-Qmin²)} dt,
    deltaP=Pbar-P >=0.

Both terms are nonnegative. Therefore:

- epsilon<0: no allowed allocation can satisfy full recovery.
- epsilon=0: every allowed allocation must equal P=Pbar, Q=Qmin almost everywhere. With continuity, equality holds everywhere. The fixed-path corridor theorem is then genuinely controller-independent over all allocations allowed by this precisely stated energy-tight inequality contract.
- epsilon>0: allocations need not equal the reference. A fixed-path infeasibility result alone does not exclude them.

This is a monotonicity/conservation saturation argument, not a general solution to freely optimized P/Q or task scheduling. The exact assumptions are part of the result, not optional implementation details.

### Sharp small-slack energy benefit

Let mu=1-2cPmax>0. Then integral deltaP <= epsilon/mu. If deltaP is K-Lipschitz and deltaP(0)=deltaP(T)=0, its triangular lower envelope around a maximum H gives

    integral deltaP >= H²/K,
    ||deltaP||inf <= sqrt(K epsilon/mu).

The one-dimensional interpolation/tent ingredient is classical; compare [Sz.-Nagy, original integral-inequalities paper](https://acta.bibl.u-szeged.hu/13524/1/math_010_064-074.pdf), with the journal/repository dating distinction documented in the literature audit. A stronger combined inequality retains the copper-loss quadratic:

    epsilon >= mu H²/K + 2c H³/(3K).

Its unique nonnegative cubic root is a sharper amplitude bound H_epsilon. The square-root expression is asymptotically sharp as epsilon tends to zero; positive c prevents exact equality with that simpler expression at positive epsilon.

A controller-independent finite K follows from the physical converter bounds:

    ||i'|| <= [V+(R+|omega|L)Imax+kappa sqrt(Wmax)]/L,
    Lip(deltaP) <= Lip(Pbar) + nu V [V+(R+|omega|L)Imax+kappa sqrt(Wmax)]/L.

This bound can be conservative; an explicit valid service-slew bound can sharpen it. In the frozen kW/kA units replace nu V by 1500 V and kappa sqrt(Wmax) by Vdcmax/sqrt(3).

Let G(t)=integral_0^t [net(Pbar,Qmin)-net(P,Q)] ds. Then 0<=G(t)<=epsilon and the actual/reference unbuffered energy offsets obey

    Aactual(t)-Abar(t)
      = -G(t)+k[Pbar²-P²+Qmin²-Q²]
      <= 2k Pmax sqrt(K epsilon/mu).

Let U_C(t) be ANY valid upper envelope for cumulative buffer charge under the same actuator, inventory and recovery constraints. It need not impose the DC/modulation constraints. Every allowed allocation consequently obeys

    Wactual(t) <= W0+Abar(t)+U_C(t)
                   +2k Pmax sqrt(K epsilon/mu).

If this upper bound is below Wmin at some t, all allowed allocations are infeasible. This is a robust DC-underenergy obstruction, not a complete robust viability certificate.

A materially sharper pointwise favorable inductive-release bound is

    rho(t)=k delta_cap(t)[2Pbar(t)-delta_cap(t)],
    delta_cap(t)=min{Pbar(t),H_epsilon}.

It follows because deltaP(2Pbar-deltaP) increases on [0,Pbar]. Independently of epsilon, rho(t)<=kPbar(t)². Therefore the early DC upper bound H(t)+kPbar(t)², with H=W0+Abar+U_C, needs no eventual-recovery or late-recharge allowance: monotone prefix net delivery and nonnegative active-current energy suffice.

The square-root exponent is sharp in this model. On a region with constant Pbar=P*>0 and Qmin=0, take a triangular curtailment deltaP of height H and slopes +/-K, zero elsewhere. Then

    epsilon=(1-2cP*)H²/K + 2cH³/(3K).

At its peak, G=epsilon/2 and

    Aactual-Abar=2kP*H-kH²-epsilon/2,

which is asymptotically proportional to sqrt(epsilon). The following construction makes this a physical-model family, rather than merely an interpolation example. Start with a constant-load nominal equilibrium P*, Q=0, b=0, inventory strictly between its bounds, current strictly inside Imax, and DC energy W0 strictly between its bounds with strict modulation margin m=kappa sqrt(W0)-||e_nominal||>0. Choose a fixed K>0 with L K/(nu V)<m/4. Place the triangular curtailment in one interior interval. In a disjoint later interval use a fixed smooth nonnegative recharge shape r with positive integral and reference Pbar=P*+gamma r. The smaller solution of integral[net(Pbar,0)-d]=epsilon exists with gamma=O(epsilon). Both actual and reference currents return to nominal at the endpoints; actual P=Pbar-deltaP has exact total energy recovery. Take b identically zero, so buffer inventory and actuator/queue states are unchanged. Current-amplitude perturbations are O(H), recharge slopes are O(H²), and capacitor-energy deviations are uniformly O(H). Therefore for all sufficiently small H every current and DC bound remains strictly satisfied. The triangle's derivative contribution to converter voltage is at most L K/(nu V)<m/4, while the remaining voltage and DC-voltage changes vanish with H, so modulation also remains satisfied. Continuing d stays fixed and positive. This is a full family within the averaged physical model; it does not claim attainment in the frozen device campaign.

Thus inductive-energy release can improve instantaneous capacitor headroom by order sqrt(epsilon) even though total grid-energy slack is only epsilon. An O(epsilon) replacement is false in general when L>0.

### Essential limitations and sharp boundaries

1. Pointwise modulation floors depend on P',Q'. Small amplitude or L1 deviations do not force small derivative deviations. Therefore the square-root energy bound does NOT transfer a fixed-path pointwise modulation-infeasibility witness to all allocations. A weak/integrated modulation witness or extra derivative regularity is needed.
2. If Pmax=1/(2c), zero-slack uniqueness still holds, but uniform mu is lost. Since epsilon>=c integral deltaP² and a K-Lipschitz zero-endpoint tent gives integral deltaP²>=2H³/(3K), the general amplitude bound becomes H<=(3K epsilon/(2c))^(1/3). Above the vertex, the strict-monotonicity argument fails algebraically: P=1/c-Pbar<Pbar has the same net active delivery when both are nonnegative. This pointwise identity alone is not asserted to be a full trajectory counterexample with common initial/terminal current; transitions and their energy must also be supplied. The vertex regimes are mathematical sharpness boundaries far outside this device's nominal operating range; they are not claimed observed operating modes.
3. With R=0, zero slack forces active P but does not force Q. With Qmin<0, Q>=Qmin does not make Q²>=Qmin².
4. Common terminal current is essential because inductor energy is part of total recovery. Fixed workload timing is essential for the corridor, even though only workload energy appears in the total conservation identity.
5. The reference path at epsilon>0 is a comparison path with excess energy; it need not itself satisfy terminal W return. Do not call it a recoverable fixed-path solution.

### Weak-form modulation exclusion for genuinely free allocations

Pointwise derivative closeness is unnecessary if modulation is tested in weak form. Let psi(t) be an absolutely continuous compactly supported vector test function, D=R I+omega L J, and

    a_psi=L psi'-D^T psi,
    Mbar(psi)=integral [psi dot v + a_psi dot ibar].

Integration by parts gives the same functional for the actual current; there is no boundary term. With Gp=nu V in SI (1500 V in the frozen units), the deficit identity implies

    Mactual >= Mbar - Epsi,
    Epsi = (epsilon/mu) ||(a_psi,d)_+||inf / Gp
             + sqrt(epsilon/c) ||(a_psi,q)_-||_2 / Gp.

Here the signs use P-Pbar=-deltaP<=0 and Q-Qmin>=0. The reactive estimate follows from integral(Q-Qmin)² <= integral(Q²-Qmin²) <= epsilon/c; no false pointwise square-root Q bound is used.

Meanwhile actual modulation necessarily gives

    Mactual <= kappa integral ||psi|| sqrt(Wactual)
            <= kappa integral ||psi|| sqrt(min{Wmax,H(t)+rho(t)}),

where H=W0+Abar+U_C and rho is any of the justified inductive-release bounds above. If the proposed upper energy is below Wmin at any point, the DC exclusion already applies. Thus a strict reverse inequality

    Mbar-Epsi > kappa integral ||psi|| sqrt(min{Wmax,H+rho})

excludes every allowed time-varying allocation. It does not assume the actual current derivatives are close to the reference derivatives. With a positive energy floor, the robust erosion is O(sqrt(epsilon)); the interpolation exponents themselves are classical, not claimed new.

For the frozen model choose psi=(h,0), omega>0 and h>=0. Then a_psi,q=omega L h>=0, so higher reactive support cannot reduce the weak voltage functional: the reactive error term vanishes entirely. With h=sin²(pi(t-a)/(b-a)) supported on [a,b],

    ||(a_psi,d)_+||inf
      = sqrt((L pi/(b-a))²+(R/2)²)-R/2.

This is the exact coefficient used by the reproducible numerical certificate, not a fitted robustness factor.

A sharper vector test uses the same energy budget jointly. If the support of psi lies where Qmin>=q*>0 and m(t)=1-2cPbar(t)>0, then the pointwise gap pays at least m(t) deltaP+2cQmin(t) deltaQ. Consequently one may replace the separated error above by

    Epsi_joint = epsilon/Gp * max{
        ess_sup (a_psi,d)_+ / m(t),
        ess_sup (a_psi,q)_- / (2cQmin(t)) }.

This is a weighted one-sided support-function inequality, not an assumption that the active and reactive error budgets are separately available. Where the positive reactive floor assumption fails, this joint linear-price formula is not applicable without handling zero denominators or reverting to the L2 estimate.

For psi=n sin²(pi(t-a)/w), ||n||=1 and w=b-a, write dd=R nd+omega L nq and dq=R nq-omega L nd. The exact scalar extrema are

    sup(a_psi,d)_+ = -dd/2 + sqrt((L pi nd/w)²+(dd/2)²),
    sup(a_psi,q)_- =  dq/2 + sqrt((L pi nq/w)²+(dq/2)²).

On the first constant-current plateau m(t) and Qmin are constants, making this joint error directly computable.

### Same-device positive-slack and unrestricted-late-recharge witnesses

Only the late recovery-cap amplitude gamma is expanded, so the net-energy slack equals epsilon exactly. Device parameters, workload timing, early active cap, reactive floor, initial state and initial held command all remain the same. This is a distinct, explicitly declared inequality-contract family, not a nonzero slack assigned to unchanged energy-tight data.

- alpha=100 kW, beta=900 kvar: the fixed weak test psi=(sin²(pi(t-0.008)/0.022),0) on [0.008,0.030] s excludes all allowed allocations at epsilon=0,1,5,10,50,100 J. At 100 J, gamma=8.80077283088 kW and the weak inequality margin is 5.2171379954e-5 kV*s. The sufficient certificate changes sign near epsilon=1.17366966646 kJ; failure of this sufficient test above that value is not feasibility.
- alpha=200 kW, beta=0: even granting complete release of the reference active-current inductor energy, the favorable prefix DC upper bound is 0.390788736632 kJ below Wmin at t=0.0354898100273 s. This excludes every allowed early allocation regardless of later recharge capacity, and does not require terminal recovery for the prefix impossibility.

An explicitly finite secondary search used 295 sine-window supports (left endpoints 5:1:20 ms, right endpoints 11:1:35 ms, width at least 5 ms) and 19 vector angles from -0.18 to 0 radians in steps of 0.01. This does not claim optimality over all test functions. The selected vector direction is angle -0.1 rad in the reported cases. Independently re-evaluated sufficient upper beta thresholds at alpha=100 kW are 809.70072 kvar (0 J), 813.31787 kvar (1 J), 821.01968 kvar (10 J), 834.40453 kvar (100 J), and 860.20949 kvar (1 kJ). Each root is supplemented by a strictly excluded value 0.01 kvar higher; for 100 J, the selected support is [9,27] ms and beta=834.41453 kvar gives margin 1.12339824e-8 kV*s.

These are actual capacity upper bounds within the stated family, not merely isolated infeasible points. For beta up to the absolute physical current ceiling 1500 V Imax=1267.61094 kvar and epsilon<=1 kJ, gamma<=35.37680 kW<alpha, so Pmax and the cap-Lipschitz bound stay fixed. For any chosen fixed negative-angle test, its Mbar increases linearly in beta, reference H decreases quadratically, and the joint error is nonincreasing (maximum of a constant and a positive constant/beta). Thus its margin is increasing; all larger beta are also excluded. Above the absolute current ceiling, the current limit alone excludes.

Scripts and floating-point evidence: weak_modulation_certificate.py, weak_modulation_results.json, dc_allocation_certificate.py, dc_allocation_results.json, vector_weak_certificate.py, vector_weak_results.json. The optional d-axis-only support search is separately recorded in optimize_weak_window.py and optimized_weak_windows.json. These analytically valid inequalities are evaluated numerically; no interval-arithmetic certification, measured-device result, or PWM transfer theorem is claimed.

## 7. Failure of an unqualified energy-coordinate SOCP exactness claim

Set E=W+Z. Then

    E'=P-loss+b-d,
    ||e||²+kappa² Z <= kappa² E,
    E>=Wmin+Z,
    E<=Wmax+Z.

The modulation/lower constraints are convex in the appropriate variables, but the upper bound is reverse-convex and the concave-dynamics equality cannot simply be replaced by an inequality. A relaxation E'<=P-loss+b-d allows artificial dissipation.

Counterexample: prescribe a constant import current with positive DC input 2, constant continuing load d=1, b=0, and start W at its upper bound. Set relaxed E constant by silently discarding 1 unit of power. It satisfies the relaxed differential inequality and can claim exact endpoint recovery. The actual system gains energy at rate 1, violates the upper bound immediately, and cannot restore both stores; allowing arbitrary buffer action with B(T)=B(0) does not remove the total surplus. Import-only demand and monotonicity alone do not fix this defect.

## 8. Reproducibility and novelty boundary

- exact_cell.py: analytic asymmetric lag/ramp flow, moment bounds, gradients, and constructive lift.
- test_exact_cell.py: seeded checks against quadrature, finite differences, global supporting inequalities and pure-lag formula.
- exact_cell_tests.json: frozen numerical results and the cheap-outer false-positive witness.
- literature/FIXED_PATH_CERTIFICATE_ADDENDUM.md: external novelty threats. In particular, cubic interval SOCP, cubic Hermite interpolation, generic O(h²) intersample bounds, and acceleration-constrained corridor reachability predate this work.

The candidate contribution is a carefully delimited synthesis/specialization: exact lag/ramp/charge cells, physical converter modulation/inductor-energy corridor, continuing-workload full recovery, and the energy-tight inequality-contract bridge with a sharp small-slack inductive-energy sensitivity. Whether that synthesis is publication-level novelty requires the separate prior-art and empirical judgments; the component mathematics alone is not evidence of novelty.
