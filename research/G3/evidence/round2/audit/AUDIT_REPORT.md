# Independent physical/admission audit

Audit date: 2026-10-03 UTC. Scope: declared synthetic averaged import-side converter and finite-lag/slew buffer, prescribed P/Q trajectories, exact store/current recovery. This is not hardware validation or a historical replay audit. No existing model, solver, protocol, or theory file was modified by the auditor; new files are confined to `audit/`.

## Bottom line

The frozen primary physical model and the 21 admitted spline witnesses pass independent reconstruction and actual clipped SI abc plant integration. All 13 rejected profiles among the 20 unique primary contracts have an independently understandable necessary obstruction: three static current violations and ten optimistic maximum-charge energy/modulation failures. Classification is consistent on all three grids.

The original conic outer objective is not by itself a rigorous numerical exclusion certificate: one reported outer margin is 2.4136e-5 kJ below an explicitly feasible inner margin. This numerical ordering defect does not change the primary classifications because independent analytic necessary bounds exclude every rejected profile by a substantial gap.

The exact lag/ramp/charge cell formulas, convexity, endpoint gradients, and O(h²) continuous-state-tube argument pass this audit, with the qualifications below. Those results are not evidence of algorithmic novelty. The primary grid is easy for an elementary scalar maximum-charge screen, so it does not demonstrate an algorithmic advantage for exact-cell optimization.

## Independent witness and plant checks

`independent_audit.py` imports neither `src/model.py` nor `src/admission.py` nor the reference simulator. It independently:

- Recomputes the prescribed profiles; solves the loss-compensation root by numerical quadrature and root finding
- Reconstructs W, B, u and all polynomial constraints from saved b coefficients, with analytic stationary-point extrema on every cell
- Checks node and integral continuity, initial held-command prefix, horizon timestamps, and exact recovery residuals
- Computes physical abc current, converter voltage, power and energy derivatives directly
- Replays all claimed admitted witnesses through an SI abc ODE with converter modulation clipping, input-command clipping and actual lag/slew clipping in the right-hand side, aligning integration boundaries to every profile/command knot

All 51 saved spline witnesses were checked. There were 21 claimed admissions and 21 independent admissions, with no disagreements. The remaining nine campaign rows had current infeasibility and no witness file.

Maxima across all saved spline witnesses:

- Profile reconstruction disagreement: 6.83e-13 kW/kvar
- W/B coefficient disagreement: 1.31e-11 kJ
- Direct abc power/energy identity residual: 2.14e-12 kW
- Initial held-prefix coefficient magnitude: 2.00e-14 kW
- b continuity residual: 1.14e-13 kW
- C continuity/recovery residual: 1.31e-11 kJ

Maxima across the 21 independent SI abc replays:

- abc current tracking error: 3.36e-8 A
- active-power error: 2.46e-5 W
- reactive-power error: 1.51e-5 var
- capacitor-energy discrepancy: 3.34e-6 J
- total-energy closure residual: 3.26e-7 J
- command clipping, ramp clipping and modulation clipping: zero

The smallest true all-time modulation energy slack among admitted witnesses is 0.3153599 kJ. Other tight actuator bounds remain positive at the independently calculated polynomial extrema, including approximately 2.45e-6 kW command slack and 2.21e-4 kW/s ramp slack. These are numerical, not interval-arithmetic, verifications.

Full results: `INDEPENDENT_AUDIT.json` and `INDEPENDENT_AUDIT.log`.

## Units, signs, and continuation

For the stored kW/kJ/kA/kV units, the factors are correct:

- P=1500 V id, Q_injected=1500 V iq
- Copper loss=1500 R ||i||²
- Magnetic energy=750 L ||i||²
- Capacitor energy=500 Cdc Vdc²
- W'=P-loss-Z'+b-d, B'=-b

With the import-positive Park transform, positive iq gives negative imported reactive power, hence positive reactive injection support as intended. The dq norm is a phase-peak amplitude envelope: balanced actual phase currents have squared sum 3||i||²/2, and every phase magnitude is bounded by ||i||. This differs from phase RMS.

The voltage bound ||e||<=Vdc/sqrt(3) is the inscribed linear SVPWM/min-max-zero-sequence circle. Zero-sequence-free sinusoidal PWM has the smaller Vdc/2 amplitude limit. The model must say which bound it uses; the reference uses min/max common-mode injection.

The protocol models one initial 1 ms held-zero command. The admitted controls thereafter vary continuously within each polynomial segment and can jump at event boundaries. It does not certify recurring sample-and-hold commands or a persistent transport-delay queue. At the terminal time, a command jump to zero is permissible because no command-slew constraint is imposed. Together with b(T)=0 and restored stores/current, this gives the declared continued baseline orbit.

The modulation voltage can jump at prescribed-current slope changes. Both one-sided floors are necessary and are checked. There is no converter-voltage-command lag in the ideal averaged proof; switching/controller tracking belongs to the separate validation layer.

## Analytic independent rejection witnesses

Any admissible actual buffer power is bounded by the maximal-command trajectory. For the frozen parameters and z=max(t-0.001,0), its ramp phase lasts tr=0.010 s. The maximum cumulative charge is

- Cmax=0.5 r z² for z<=tr
- Cmax=0.5 r tr²+umax(z-tr)-tau² r[1-exp(-(z-tr)/tau)] for z>tr

Thus W(t)<=W0+A(t)+Cmax(t), even when all inventory/recovery/upper-voltage constraints are generously ignored. A single point where this ceiling falls below Wmin or the prescribed modulation floor excludes every battery controller for that prescribed path.

All ten non-current rejected profiles have such a point. Examples:

- alpha=200 kW, beta=0: DC-energy deficit at least 0.4623248 kJ at t=0.03561074 s
- alpha=100 kW, beta=900 kvar: modulation-energy deficit at least 0.6725527 kJ at t=0.01727480 s
- alpha=300 kW, beta=1200 kvar: modulation-energy deficit at least 8.9182153 kJ at the appropriate one-sided t=0.035 s voltage

The location search is only a way to find a violating time. Its global optimality is unnecessary for validating the necessary exclusion at that time. Results and explicit times for every case: `ANALYTIC_EXCLUSIONS.json`; script: `analytic_exclusions.py`.

## Exact-cell oracle and theorem audit

The flow formulas correctly implement forward maximum/minimum lag/slew trajectories and reverse endpoint envelopes. Integrating the upper/lower envelopes gives the exact charge interval; convex mixing preserves the affine command/ramp strips and realizes intermediate charges. Boundary-crossing cancellation yields the stated endpoint gradients, and their supporting-cut orientation is correct.

Independent tests:

- 24 random asymmetric actuator cases compared with a separately constructed piecewise-linear trajectory LP at 64, 256 and 1024 cells. All LP bounds lie inside the exact oracle interval, with zero outward violations
- Reachable endpoint comparison with an independent actual clipped-actuator ODE: discrepancy <=1.13e-8 kW
- Dense lift charge check: <=1.01e-9 kJ
- Dense finite-difference actuator-strip discrepancy: <=2.90e-6 in corresponding units, attributable to finite differences at piecewise switch locations; this test is not an exact extrema certificate
- 112 endpoint-domain anchors (command corners, forward-reachability boundaries and ramp/lag transitions), 22,400 global supporting-cut comparisons: zero tangent violations

See `EXACT_CELL_AUDIT.json`, `EXACT_CELL_BOUNDARY_AUDIT.json` and their scripts.

The O(h²) theorem is a continuous state-slack tube, not an unconditional admission/objective-gap rate. The chord-lemma sign and physical slack-curvature bounds are correct. Both one-sided modulation constraints must be imposed at derivative events. For exact fixed boundary states with zero slack, symmetric Mh²/8 endpoint tightening can make every finite-grid inner problem infeasible despite a feasible continuous path. The theory has been updated to distinguish outer subsequential compactness from inner density and to require endpoint compatibility/strict margin for stronger convergence claims.

The cubic-Hermite interpolation constants stated in the theory are consistent. The cubic interval-positivity representation is the classical exact Markov–Lukacs result; the 2x2 PSD encoding in the spline code expands correctly and is SOC-representable.

## Exact-cell implementation residuals

The 36 saved exact-cell campaign witnesses were checked for nonlinear reachability/moment residuals:

- Maximum endpoint reachability violation: 1.00e-10 kW
- Maximum charge violation against a clamped reachable pair: 1.00e-9 kJ
- No cell is unreachable at the 1e-9 kW audit threshold
- All saved endpoint b(T), C(T) values are exactly zero in stored floating point

Full data: `EXACT_WITNESS_RESIDUALS.json`.

The code's stopping tolerances allow small nonzero nonlinear violations; label the computation numerical. A mathematical constructive certificate needs either exact feasibility or a rigorously bounded repair/margin argument. At audit time, the saved exact-cell NPZ included inequality duals but omitted lower/upper-bound multipliers and primary primal variables, while the saved primal was the secondary tie-break solution. A complete standalone dual audit requires all of those objects plus objective/bounds. This does not invalidate the tangent mathematics.

## Energy-tight inequality bridge

Under the explicitly stated contract 0<=P<=Pbar<P_vertex, Q>=Qmin>=0, R>0, fixed workload and exact initial/final total electrical+storage energy, the identity

  epsilon=integral[(Pbar-P)(1-c(Pbar+P))+c(Q²-Qmin²)]

is correct. At zero epsilon, both nonnegative terms vanish, forcing the reference allocation. Thus fixed-path exclusions extend to all allocations for this energy-tight inequality contract, not for arbitrary slack or freely optimized P/Q.

For positive slack, the active-power deficit has an L1 bound; current-derivative limits give its Lipschitz bound and O(sqrt(epsilon)) peak bound. Since Q>=Qmin only decreases the corresponding inductive-release upper bound, no pointwise Q estimate is required for the stated capacitor-energy ceiling. If a separate pointwise Q-closeness claim were made, Qmin=0 generally yields only an O(epsilon^(1/3)) bound from Lipschitz+L2² control, not O(sqrt(epsilon)).

The small-slack result does not transfer pointwise modulation infeasibility because small waveform errors do not control derivative error. Any weak/integrated modulation extension needs a separate audit. For numerical use with the frozen units, c=R/(1500 V²) and k=L/(3000 V²); using the unconverted SI coefficients would produce a factor-of-1000 error.

The key assumptions cannot be dropped: R=0 leaves Q unconstrained by energy; Qmin<0 destroys monotonicity of Q²; above the net-delivery vertex, active-power uniqueness fails; exact common terminal inductor energy and unchanged workload energy are necessary.

## Reporting cautions

1. With loss compensation and exact DC/current recovery, terminal inventory recovery is redundant. Removing only that equality is a no-op, not evidence of benefit. The no-compensation terminal ablation deliberately changes the contract and should be identified as such.
2. The protocol includes predeclared parameter/model references and its file timestamp precedes primary solves, but a local mtime is not an independently signed preregistration. The audit records input SHA256 values rather than claiming a stronger provenance guarantee.
3. The ablation at beta=810 kvar is outside the 20-profile primary grid and should be described as an exploratory near-boundary diagnostic.
4. The primary results support correctness under the stated model. They do not establish generic controller dominance, generic algorithmic novelty, measured GPU/facility performance, switching-hardware exact tracking, or historical experimental replay.

## Final audited additions (09:14 UTC)

### Positive-slack weak-modulation exclusion

The one-sided vector integration-by-parts formula is correct. With D=RI+omega L J and a_psi=L psi'-D^T psi, actual current deviations are (-deltaP,+deltaQ)/Gp. The adverse weak-voltage terms are therefore a_d,+ deltaP and a_q,- deltaQ. The originally audited d-axis test has a_q>=0, so reactive excess cannot help it.

The independent script `audit_weak_modulation.py` imports no target model/theory modules. It derives the first ramp and plateau energy offset directly, obtains the recharge root independently, maximizes the trigonometric coefficient numerically, and repeats the integral quadrature. At 100 J extra total net-energy slack, the d-axis test's positive exclusion margin is 5.21713799542e-5 kV*s. Its sufficient slack threshold is independently 1.173669666465 kJ. The largest reproduced term discrepancy is 1.71e-16 kV*s. These are sufficient exclusions, not feasibility thresholds.

It also independently verifies an all-late-recharge prefix obstruction for alpha=200 kW and Qfloor=0. At t=0.03561073948 s, even granting release of all instantaneous magnetic energy, W is at most 17.10594116 kJ, below Wmin=17.496 kJ. No amount of later recharge can change that earlier contradiction; this argument does not need terminal recovery. The theory separately optimizes the witness time and obtains a slightly stronger gap, consistent with this independent fixed-time witness.

### Final all-allocation capacity bracket

On a positive-Q plateau, the same total energy budget pays for both active and reactive deviations:

  energy_gap >= mu_local deltaP + 2c beta deltaQ.

Thus the vector-test adverse error is bounded by

  epsilon/Gp * max{sup(a_d,+)/mu_local, sup(a_q,-)/(2c beta)}.

This shared-budget maximum, rather than a sum of separate full-budget penalties, is valid. The trigonometric coefficient formulas and their signs were independently checked by direct numerical maximization. The selected sine-bump test has window [0.009,0.027] s and direction (cos(-0.1),sin(-0.1)). At epsilon=0.1 kJ and beta=834.414530875619 kvar, the independent strict exclusion margin is 1.12339823763e-8 kV*s. Across all five supplied selected-test cases, independent terms agree within 8.68e-19 kV*s; this audit verifies the selected certificates, not optimality of the finite search family.

An isolated rejected beta would not be an upper-capacity bound because the recharge cap itself rises with beta. The needed monotonicity was checked explicitly: through the free-allocation reactive-current ceiling 1267.61094189 kvar, the 100 J recharge amplitude stays below 100 kW (15.0875188 kW at the ceiling). Hence global mu, K and rho remain fixed. For the chosen test, Mbar increases, the joint error max(const,const/beta) does not increase, and the optimistic capacitor ceiling decreases with beta squared. Higher beta therefore remains excluded; beyond the current ceiling Qfloor alone is impossible.

The beta=808 kvar lower witness was independently reconstructed, checked for true all-time polynomial extrema, and replayed through the clipped SI abc plant. It passes with zero clipping and full recovery. Its actual zero-slack tail amplitude 5.30763054 kW is below the 100 J inequality contract's allowed tail 7.56112502 kW. Thus the exhibited lower and strict excluded upper bracket the supremal attainable beta under this particular free-allocation contract family:

  808 kvar <= supremal beta < 834.41453088 kvar.

The bracket width is 3.269125% of the exhibited 808 kvar lower value. The upper value is a numerical evaluation of an analytic sufficient exclusion, not a directed-interval proof. The 808 replay has maximum W discrepancy 8.01e-11 J, current discrepancy 3.56e-11 A, and no actuator or modulation clipping. Full results: `VECTOR_WEAK_AUDIT.json`; script: `audit_vector_weak.py`.

### Exploratory multi-cycle corridor family

All 12 custom profiles were independently reconstructed, including the exactly defined piecewise-linear sampled sine workload, positive continuing load, slow Q ramp and compensation root. Eight admitted splines and four rejections agree with the reported classifications. All eight admitted splines were independently replayed through the clipped SI abc plant, with zero clipping, maximum W discrepancy 3.02e-8 J and current discrepancy 2.27e-10 A. The smallest admitted actual upper-W/modulation slack is approximately 0.0240047 kJ. See `SWITCH_CORRIDOR_AUDIT.json` and `audit_switch_corridor.py`.

Saved supporting-cut LP inequalities were independently combined with nonnegative weights. Their sigma coefficient is positive; auxiliary coefficients are nonnegative (in these results exactly zero); any remaining b/C coefficients are bounded using their explicit finite boxes. This produces an independent objective upper bound without trusting the primal objective, an optimality label, or exact dual stationarity. High-precision recombination was performed on stored binary64 constants. All 48 available exact LPs admit such a weighted bound; 22 bounds are negative. See `WEIGHTED_LP_BOUNDS.json` and `audit_weighted_lp_exclusions.py`. The remaining caveat is floating-point evaluation of the analytically valid nonlinear tangent formulas, not LP optimality.

The four rejected multi-cycle cases have these independently recombined upper margins:

- ramp=3000 kW/s, beta=1000 kvar: -0.18058929864136 kJ
- ramp=3000 kW/s, beta=1050 kvar: -0.35072698903590 kJ
- ramp=5000 kW/s, beta=1000 kvar: -0.07050950635429 kJ
- ramp=5000 kW/s, beta=1050 kvar: -0.24064719674883 kJ

A separate audit checked every ordered triple of recorded grid nodes, not merely symmetric triples, against the necessary second-derivative chord condition using the two-sided physical corridor and fixed C endpoints. The ramp=5000, beta=1000 case still evades this screen; its strongest tested violation score is negative (-0.14434493 kJ), while the full-horizon weighted LP bound is strictly negative. See `THREE_POINT_SCREEN.json` and `audit_three_point_screen.py`. This is a concrete incremental decision beyond the stated weak screens, not a claim of superiority to mature optimal-control algorithms or all possible analytic screens.

### Closed audit issues

The theory now explicitly identifies SVPWM, converts both c and k, distinguishes outer compactness from tightened-inner density, and states the non-nested-family monotonicity needed for the capacity upper bound. Complete dual data were subsequently added to the target NPZ files by the model author; the independent weighted-bound audit does not depend on those additions. The independent numerical audit finds no remaining sign, unit, quantifier, or implementation issue affecting the reported claims within their stated scope.
