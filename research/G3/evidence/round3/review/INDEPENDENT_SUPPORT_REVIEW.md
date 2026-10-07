# Independent skeptical review of G3 shared-budget weak certificates

Reviewed: historical `EXACT_PORT_CONTRACT_THEORY.md`, historical `vector_weak_certificate.py`, and the proposed quadratic-support and coupled prefix-energy formulas. Historical outputs were not changed. This review is about validity and scope, not a literature-based novelty certification. Numerical checks are floating-point evidence, not interval proofs.

## Final disposition after repair review

The frozen beta=812.5 kvar prefix-only outer exclusion and the beta=808 kvar held-buffer-command inner witness both pass this independent review in their declared averaged-converter model. The raw-LP actuator-tolerance problem in Section 11 was resolved by the rational-base/analytic-repair certificate in Section 12. There is no remaining substantive proof blocker identified for those two frozen results. The review does **not** certify full finite-level PWM implementation, hardware precision robustness, or publication-level novelty.

## Immediate findings

1. **The quadratic energy-budget support formula is correct.** Its improvement over the old max-ratio error is mathematically genuine, because it retains the shared budget, quadratic loss, and optionally active-curtailment cap. It is exact for the declared relaxed measurable-deviation class, not exact for physically achievable allocations.
2. **The coupled tangent/Fubini formula also has the correct signs.** It accounts for both favorable local inductor-energy release and unfavorable prefix energy spending. A strictly positive resulting margin is an all-allocation exclusion for the same averaged model.
3. **Must qualify the small-slack rate.** The active integrated energy-release penalty is O(epsilon), but unrestricted reactive deviations at a zero reactive floor can still cause a Theta(sqrt(epsilon)) weak penalty. An O(epsilon) claim is valid on the positive-Q plateau used in the old search, or under the bounded one-sided price-ratio condition below.
4. **Must state appropriate test-function regularity.** Merely absolutely continuous psi does not ensure a finite quadratic dual integral. H^1_0, or an explicit requirement a_psi in L^2 plus the required integration-by-parts conditions, is sufficient. Sine-squared test windows meet it.
5. **The switching obstruction is a zero-tolerance implementation boundary.** It needs a positive-measure voltage mismatch for every admissible DC voltage, rather than a mismatch at one reference DC voltage or one time. It supplies no positive minimum slack without extra switching-frequency/dwell assumptions and does not exclude the 100 J contract.

## 1. Exact quadratic support

Let x=Pbar-P>=0 and y=Q-Qmin>=0. With c>0, m=1-2c Pbar>0, and Qmin>=0, the exact energy spending is

    g=m x+c x^2+2c Qmin y+c y^2.

The weak-functional reduction is

    Mactual=Mbar-integral(l_d x+l_q y),
    l_d=a_psi,d/Gp,   l_q=-a_psi,q/Gp.

Thus the signs in the proposed objective are correct. On a finite horizon, assume bounded m,Qmin, l_d,l_q in L^2, and epsilon>0. The primal

    sup integral(l_d x+l_q y)
    subject to x,y>=0 and integral g<=epsilon

has the dual

    inf_{lambda>0} lambda epsilon
      +integral[((l_d-lambda m)_+)^2
                +(l_q-2 lambda c Qmin)_+^2]/(4 lambda c).

For fixed lambda, complete the two squares independently. The maximizing deviations are

    x_lambda=(l_d-lambda m)_+/(2 lambda c),
    y_lambda=(l_q-2 lambda c Qmin)_+/(2 lambda c).

Slater holds at x=y=0 because epsilon>0. The quadratic budget controls the L^2 norm; the objective is continuous linear. Standard convex-program duality gives equality. The primal is attained in the L^2 relaxed class; a finite positive dual minimizer exists whenever the usual nontrivial budget-active case applies. A certificate does not need dual attainment or an exact minimizer: **every finite lambda>0 is already a valid upper bound**.

Do not literally substitute lambda=0 into the displayed quotient. Either write inf over lambda>0 or define an extended-value boundary explicitly. Epsilon=0 is best treated directly: g>=0 and m>0 imply x=y=0 a.e. The limiting dual also gives zero, but need not attain it at finite lambda if Qmin=0 and l_q>0.

With the actual cap x<=Pbar, replace the active term by

    z=l_d-lambda m,
    x*=clip(z/(2 lambda c),0,Pbar),
    Phi_d=z x*-lambda c (x*)^2.

Equivalently Phi_d is 0, z^2/(4 lambda c), or z Pbar-lambda c Pbar^2 in its three regimes. Because m+2c Pbar=1, the upper-cap regime begins exactly when l_d>=lambda. This cap is optional for validity and beneficial for tightness. The primal still drops physical dynamics, current limits, endpoint restrictions, and the exact equality of the total budget; accordingly “exact” describes this support relaxation, not the whole admission problem.

## 2. Coupled prefix-energy certificate

Use K_v=sqrt(1500 Cdc) to avoid collision with the historical Lipschitz constant K. Let w=||psi|| and

    H=W0+Abar+U_C,
    G(t)=integral_0^t g(s) ds,
    U=H-G+k(2 Pbar x-x^2-2 Qmin y-y^2).

The exact energy identity plus the buffer upper envelope gives Wactual<=U. Choose an allocation-independent anchor Y(t)>0 with a positive essential lower bound on the support of w, and put

    z=w/(2 K_v sqrt(Y)),
    r(s)=integral_s^T z(t) dt.

The concavity tangent gives

    w sqrt(Wactual)/K_v
      <=w sqrt(Y)/K_v+z(Wactual-Y)
      <=w sqrt(Y)/K_v+z(U-Y).

The second step is valid because z>=0. Fubini gives

    integral z(t)G(t)dt=integral r(s)g(s)ds.

Therefore

    Mactual-integral w sqrt(Wactual)/K_v
      >=base-integral[A_d x+A_q y-b(x^2+y^2)],

where

    base=Mbar-integral w sqrt(Y)/K_v-integral z(H-Y),
    A_d=l_d+2k z Pbar-r m,
    A_q=l_q-2k z Qmin-2r c Qmin,
    b=kz+rc>=0.

All proposed signs check. For every lambda>0,

    integral[A_d x+A_q y-b(x^2+y^2)]
      <=lambda epsilon
        +integral[((A_d-lambda m)_+)^2
                  +(A_q-2lambda c Qmin)_+^2]
                 /[4(b+lambda c)].

A strictly positive base minus this upper bound contradicts the modulation requirement. The same Slater/relaxed-class qualification as above supplies strong duality; it is unnecessary for sufficiency of a fixed-lambda certificate. The x<=Pbar clipping refinement works with denominator 2(b+lambda c), and its upper-cap threshold is now A_d>=lambda+2b Pbar.

Potential pitfalls:

- Y must be chosen independently of the unknown actual allocation. Numerically choosing it from a reference or relaxed optimizer is fine once it is frozen and the final bound is evaluated at that explicit anchor.
- Do not evaluate sqrt(U) for a relaxed allocation with U<0. The proof only needs sqrt(Wactual), which is physical and positive; its supporting tangent remains valid even when the relaxed algebraic U is negative, in which case no actual allocation can realize that bound.
- Keep the fixed-horizon suffix integral r(s), including any zero-weight intervals. Omitting its contribution before a test support does not break sufficiency if deviations there are optimized away, but it loses the exact prefix identity.
- If H or Y changes with beta/epsilon, monotonicity of the final numerical margin does not follow merely from the historical fixed-window argument. Prove it separately before presenting a single root as an upper capacity bound for all larger beta.

## 3. Small-slack rate and a counterexample to an unqualified O(epsilon) claim

If A_d,A_q are bounded and

    R*=ess sup max{(A_d)_+/m,
                   (A_q)_+/(2c Qmin)}<infinity,

with the second ratio interpreted as zero only when its numerator is nonpositive at Qmin=0, then b>=0 implies the relaxed erosion <=R*epsilon. The positive-Q plateau and smooth finite windows satisfy this condition. More generally, the reactive term may be harmless if A_q<=0 wherever Qmin=0.

Without that qualification, take a unit-length interval, Qmin=0, A_q=1, A_d=0, constant b>=0, and cost c y^2. For small epsilon, uniform y=sqrt(epsilon/c) gives exact support

    sqrt(epsilon/c)-b epsilon/c.

Its leading order is sqrt(epsilon), not epsilon. Quadratic costs and the prefix term do not remove that reactive effect.

The active integrated favorable release nevertheless obeys

    integral 2k z Pbar x
      <=2k ||z Pbar||_infinity epsilon/mu,

so a pointwise sqrt(epsilon) energy-release bound is needlessly pessimistic for a bounded weak integral. No current-deviation Lipschitz assumption is required for this integrated active bound. This is a useful conceptual refinement of the historical proof.

## 4. Optional tighter formulations

The physical Wmax cap can be retained by using the concave nondecreasing function

    phi(U)=sqrt(min{Wmax,U}),  U>=0.

Use a supporting slope at Y: the usual 1/(2sqrt(Y)) below Wmax, zero above Wmax, and any slope between these at Wmax. Multiply by w/K_v to obtain z and retain the same algebra. With a zero slope above the cap, no reciprocal sqrt is needed there.

Also U[x,y] is a concave functional of deviations: its local negative quadratics and negative integral of g are concave. Thus maximizing

    integral(l_d x+l_q y)+integral w phi(U)/K_v

under the energy budget, nonnegative deviations, optional x<=Pbar, and U>=0 is a convex-optimization relaxation of the weak obstruction. The proposed anchored certificate is a tractable separable dual upper bound for it. Optimizing anchors may tighten it. Claiming equivalence after optimizing all anchors requires an additional minimax/duality qualification and is not established just by the tangent inequality.

## 5. Historical rho bound

The old rho=k delta_cap(2Pbar-delta_cap), delta_cap=min(Pbar,H_epsilon), is valid under its stated global Lipschitz and endpoint assumptions. Its derivation drops -G and the nonpositive reactive inductor term. The monotonicity of x(2Pbar-x) on [0,Pbar] is the needed fact. The old mu and Lipschitz constant depend on a verified cap maximum and cap slope, including the enlarged late recharge amplitude; do not reuse them beyond the range where gamma<alpha was established.

The old U_C=up(t,p)[1] is a valid favorable buffer envelope even though it drops terminal/inventory requirements. Such omission only weakens an exclusion. The new coupled theorem bypasses the global Lipschitz/rho step, which removes that source of conservatism and its extra regularity burden.

## 6. Exact instantaneous switching obstruction

Under zero total energy slack, the same physical conservation identity and exact instantaneous inequalities force x=y=0 a.e. Continuity gives the prescribed current path everywhere. The converter equation then forces

    e_req=v-R i_ref-L i_ref'-omega L J i_ref

almost everywhere. A finite-level switched implementation can realize it only if e_req(t) belongs to its discrete voltage alphabet S(W(t),t) almost everywhere.

A rigorous obstruction must show nonmembership on a set of positive measure for every admissible W(t). Nonmembership at a single time is insufficient for an a.e. differential equation, and nonmembership at one chosen reference W is insufficient when the buffer can alter actual W. A mismatch of e_req's direction against all permitted switching rays is independent of voltage scaling and avoids the latter problem.

For a conventional ideal finite-level three-phase bridge in the synchronous dq frame, nonzero switching rays rotate with the grid angle. On any nonzero constant-current plateau, e_req is a fixed nonzero dq vector. Equality of its direction to one of finitely many rotating rays occurs only at isolated times when omega!=0. Therefore exact instantaneous tracking fails on that plateau regardless of the DC amplitude or switching frequency. This already applies to the nonzero nominal orbit. It is a generic consequence of a zero-ripple instantaneous contract, rather than a special obstruction created by the service pulse.

This proof does not say that carrier-averaged P/Q contracts fail, nor that 100 J is insufficient. With no finite switching-frequency or minimum-dwell assumption, rapidly switching trajectories can approach the relaxed averaged trajectory; no uniform positive minimum slack follows from finite alphabet alone. An ideal switched model also has instantaneous active-vector magnitudes different from the averaged inscribed-circle voltage constraint. State clearly which model is being compared and which instantaneous contract variables are meant.

## 7. Publication and reporting boundaries

The square-completion dual, convex budget support, concavity tangent, and Fubini exchange are standard operations. Their combination with this exact converter-energy identity is a useful specialization and may materially sharpen bounds; that fact alone does not establish mathematical novelty or publication value. A finite window/angle search is not optimization over all admissible weak tests. Report frozen witness parameters and positive final margins, not only threshold roots. Preserve the same contract/device family and distinguish a changed late-recharge cap from assigning slack to unchanged data. Final numerical signs require independent quadrature and a stated numerical uncertainty policy.

## 8. Stronger prefix-only limit (lambda=0)

The coupled certificate can be valid without any terminal-recovery or total-slack assumption. Drop the budget entirely and maximize the pointwise concave quadratic directly:

    E_prefix=integral[(A_d)_+^2+(A_q)_+^2]/(4b),  where b>0.

On b=0, the support is zero if both coefficients are nonpositive and infinity if either is positive. This is the correct extended-value definition; a small positive numerical lambda is not, by itself, a proof of the budget-free claim.

For a sine-squared window with k>0 and a positive bounded anchor, at the right endpoint z=O(delta^2), r=O(delta^3), b=O(delta^2), and A=O(delta). Therefore the integrand remains bounded near that endpoint. In the proposed negative-angle test, both leading endpoint coefficients are negative, so the support actually vanishes in a terminal neighborhood. Before the window, z=l=0 and r>=0, so the coefficients are nonpositive and the pointwise support is zero. After the window all are zero. This proves why evaluating only the window is sufficient in this case.

The resulting strict inequality is a prefix impossibility for all nonnegative active import below the early cap and all reactive support above the early floor, without relying on later recharge or store return. Increasing beta leaves the active prefix cap unchanged and strengthens the reactive prefix floor; hence all larger beta are excluded by contract nesting. No monotonicity claim for a beta-dependent numerical optimizer is needed.

Independent nested adaptive quadrature at the exploratory fixed window [0.011292608356252797,0.023925376064810815] s and angle -0.10163040739497287 rad gives:

- beta=812.5 kvar, lambda=0: margin +1.8154248764666523e-7 kV s
- beta=813 kvar, lambda=0: margin +5.744150005949744e-7 kV s
- beta=812.5 kvar, lambda=1e-10 and epsilon=.1 kJ: margin +1.8153525596596417e-7 kV s
- beta=812.2689440942253 kvar, lambda=0: residual +1.0478293746789219e-14 kV s

These independently reproduce the exploratory root but are not interval certificates. The independent evaluation derives H from explicit shape integrals and evaluates every suffix integral by nested adaptive quadrature. At beta=812.5 the active positive-coefficient interval is approximately [0.01481439003979,0.01537478981959] s; no positive reactive interval was found. The root is a diagnostic, not a strictly excluded reported witness. Code and full results are `independent_coupled_numeric.py` and `independent_coupled_numeric.json` in this review directory.

## 9. Robust exact pure-lag reset obstruction

The additional robust open-loop proposition is correct with its stated restrictions. Let

    b'=s(u-b),  b(0)=0,  s=1/tau>0,

where one bounded measurable command u on one fixed finite horizon [0,T] must work for every s in a positive interval. Then

    b(T;s)=s integral_0^T exp[-s(T-t)]u(t)dt.

If b(T;s)=0 for all those s, the finite-horizon Laplace transform of v(r)=u(T-r) vanishes on an interval. It is an entire function of complex s because v is integrable and compactly supported. The identity theorem makes it identically zero. Its derivatives at zero give every moment of v equal to zero. Polynomial density, or Laplace uniqueness, then implies v=0 a.e., hence u=0 a.e. Any uncertainty set with an accumulation point in the finite complex domain is enough; a full interval is convenient, not necessary.

This does not rule out feedback, parameter-dependent commands, approximate reset, infinite-horizon reset, or exact reset at finitely many specified time constants. Nontrivial sign-changing commands can meet finitely many linear terminal equations. It also does not automatically cover the historical clipped lag/ramp actuator: the unclipped pure-lag dynamics must hold throughout for every uncertain parameter. If the finite-ramp model is retained, either prove that no ramp clipping occurs under the whole uncertainty set or give a separate argument. This theorem exposes the brittleness of robust exact terminal equalities under a common open-loop waveform; it does not establish robust infeasibility of the physical service under adaptive control.

## 10. Outward interval implementation audit

Inspected `src/certify_prefix_interval.py` and reran its two frozen cases. The mathematical enclosures are valid:

- The rational window [0.0113,0.0239] lies after the 11 ms buffer-envelope transition, so its explicit lag-exponential H expression applies throughout.
- Exact interval integrals of sine-squared are multiplied by an interval range of sqrt(H), giving a valid baseline integral enclosure.
- For each cell, r is enclosed below by the accumulated lower bound on all later cells and above by the accumulated upper bound including the current cell. Nonnegativity of z is essential and holds.
- The positive-part and quadratic/denominator interval operations give outer enclosures. Cells with nonpositive coefficient upper bounds contribute exactly zero.
- In the final one percent of the window, hp/h=2pi cot(pi x)/w decreases. Bounding it at x=.99, using H>=18, and dropping nonpositive -rm and reactive-energy terms proves both coefficients nonpositive. At the endpoint h=hp=r=0, so the defined support is zero. This avoids an artificial zero-denominator interval without dropping a positive contribution.

The unnormalized rational direction (1,-.102) is handled correctly: all voltage functionals scale with that vector and z/baseline use its norm. Normalizing it is unnecessary.

At beta=812.5, N=8192, the certified lower margin is 9.79098694941434407379167402197473e-8 kV s. At beta=813, N=2048, it is 2.601096912431920814734097789766709e-7 kV s. Both are strictly positive prefix-only exclusions.

All 12 exported decimal interval pairs were additionally compared, using exact Python rational arithmetic, against the exact binary mpmath endpoints before serialization. Every lower string is <= the true lower endpoint and every upper string is >= the true upper endpoint. See `check_interval_export.py` and `interval_export_audit.json`.

Recommended defensive assertions for reuse: positive P and m, nonnegative Q and lambda, and the required post-transition plateau window. These are true in the frozen cases but should not be implicit when the function is generalized. This audit checks this mathematical interval construction and its executed arithmetic; it is not a formal verification of the mpmath library itself.

## 11. Held-command inner witness audit

Inspected `src/zoh_inner.py`. Its exponential b recurrence and exact integrated-charge recurrence are correct. For a constant command on a pure-lag cell, |b'| is maximal at the cell start, so |u-b0|<=tau*ramp suffices for the entire cell and ensures no clipping occurs. Command/state bounds and the fixed initial zero-command prefix are correctly imposed. The lower-W, upper-W, modulation, and both buffer-inventory curvature/tube signs are correct. Modulation constraints from both adjacent polynomials are imposed at event boundaries.

Independent propagation from the stored commands, and independent construction of the energy/modulation polynomials from P,Q,d, confirms for the 25 us critical-hold witness at beta=808:

- lower-W continuous tube margin >=1.73066292373817 kJ
- upper-W continuous tube margin >=0.0018566832338018817 kJ
- modulation continuous tube margin >=0.0018566832340217387 kJ
- lower/upper inventory continuous tube margins >=31.28192499248935 / 49.9999624999999 kJ
- terminal b residual about 9.13e-13 kW and terminal charge residual about -9.89e-14 kJ
- current-square margin about 0.9052785327066886 kA^2

**Must fix before calling the stored numerical command an exact admissible witness:** the unrounded, repropagated command sequence violates the nominal ramp bound by approximately 1.4022e-7 kW/s due to LP feasibility tolerances. This is tiny relative to the physical limit and energy margin, but a terminal correction alone does not fix it. Re-solve with strict actuator margins, or explicitly prove a perturbation/projection preserving both ramp bounds and exact b/C return. Numerical p0/gamma values also only satisfy energy balance to floating-point accuracy; an exact-definition/interval treatment of the current path should accompany an exact recovery claim.

The 50 us and 100 us restricted constructions have negative modulation/upper-W tube margins. They do not establish infeasibility of free allocations, of all held-command controllers, or even of all controllers on those grids unless an appropriate outer certificate is supplied. The 25 us witness realizes the **buffer-port** command exactly under the ideal lag/ramp model while retaining the prescribed averaged converter current. It does not prove full finite-level PWM implementation.

See `check_zoh_inner.py` and `zoh_independent_checks.json` for independent reproducible results. This check is floating-point evidence; the outer exclusion above has the separate outward interval certificate.


## 12. Final repaired inner witness: blocker resolved

Reviewed and replayed `src/certify_zoh_inner.py` against `results/zoh_q808_exact_payload.json`. The construction scales the LP command by 1-1e-6, then freezes the resulting 12-decimal rational base commands. The final exact command is this rational base plus two analytically defined constant block corrections on [0.15,0.16] and [0.18,0.19] s.

For each held-command cell let

    w_j=(1-exp(-h_j/tau)) exp(-(T-t_(j+1))/tau).

The terminal quantities are exactly bT=sum(u_j w_j) and CT=sum(h_j u_j)-tau bT. A block correction delta_m contributes B_m delta_m and C_m delta_m, with B_m=sum_block w_j and C_m=block_duration-tau B_m. The displayed inverse of this 2-by-2 system is correct, and its determinant interval is strictly negative, approximately -0.00116729581649738. Consequently the exact corrected command has b(T)=C(T)=0 **by algebra**, independently of floating-point terminal residuals.

The all-time interval replay gives strict lower bounds:

- modulation: 0.00185297320365893701458 kJ
- upper-W: 0.00186121733974712781932 kJ
- lower-W: 1.73065921370781495425 kJ
- command: 0.000449999994840273327768 kW
- power: 0.236346641693594585778 kW
- ramp: 0.0299998598533042688422 kW/s
- current square: 0.905278532706688791287 kA^2
- both inventory constraints: strictly positive with margins over 31 kJ

The exact current profile uses the algebraic nominal-power and recharge roots. Its zero total net-energy identity is analytic; the interval enclosure containing zero is a consistency check, not a substitute for that identity. Combined with the exact repaired b/C return and common endpoint current, this gives exact W/B/current/actuator return in the model.

The replay independently verified all 16 exported decimal interval pairs against exact binary endpoints using rational arithmetic. It also checked every event knot, all 25 us critical holds, all 100 us later holds, strictly increasing times, and exact zero command throughout the initial held-command prefix. The replayed exact payload matches the supplied payload. See `check_exact_zoh_certificate.py` and `exact_zoh_certificate_audit.json`.

As an extra input-arithmetic check, all 9,603 P/Q/d endpoint intervals were compared with an independently constructed 80-digit interval reference using exact rational pulse/event times and coefficients. Every original interval encloses that reference. See `check_profile_rationals.py` and `profile_rational_audit.json`.

The previous raw-LP blocker is therefore resolved. Retain the exact semantic distinction: the payload's rational base plus analytic block repair defines one mathematical held-command waveform. The displayed correction intervals and sampled CSV are enclosures/illustrations of that waveform; independently rounding either correction creates a different waveform for which exact terminal return has not been established. This certifies the buffer actuator with an averaged converter current path, not a digital finite-precision/PWM hardware implementation.
