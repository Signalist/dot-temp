# Independent skeptical review: full-cycle W6 extension

Reviewed 2026-10-04. This is an independent mathematical audit, not a hardware result, empirical sample, or interval-certified numerical proof. The prior scientific erratum in `outputs/round2_w6_smoothing_errata_20261003/SCIENTIFIC_CLOSURE.json` remains authoritative: the original 384-trajectory blanket pass must not be restored, the 153 frozen originals stay unchanged, and the 33 corrected budget paths remain labelled corrections rather than new experiments.

## 1. Contract and exact reserve identity

Let useful work satisfy `dx/dt=s(p)` while unfinished, with actual dynamic power `p>=0`, `|dp/dt|<=R`, instantaneous EOS, and fastest post-EOS return to zero through an explicit burner. Let `c=idle+lambda>0`, where both idle energy and the time penalty are charged through the entire return-to-zero cycle. Assume `s(0)=0`, continuous at zero, positive and C2 on positive power, `s'>0`, `s''<=0`. Work `W` has essential support supremum `M<infinity`.

Define

- `A(p)=integral_0^p s(q)dq`, `z=A(p)`, `P=A^{-1}`
- `G(z)=(P(z)+c)/s(P(z))`
- `H(z)=[P(z)^2/2+c P(z)]/R`
- `S(x)=Pr(W>x)`

Then `|z'|<=R`, and the exact objective is

`J[z]=integral_0^M S(x)G(z(x))dx + integral_[0,M] H(z(x))mu(dx)`.

Crucially, `H'(z)=G(z)/R`. For any finite-cost path,

`J[z]=H(z0)+integral_0^M S(x)G(z(x))(1+z'(x)/R)dx`.  (1)

This identity accommodates atoms, including at zero and M. One rigorous route is Stieltjes integration by parts first on compact subintervals: finite expected cost and `S>0` before M give local absolute continuity of `H(z(x))`; its weighted variation is bounded by `integral S G`. Bounded H and the survival boundary terms then give (1). Equivalently, use the physical-time reserve `h(p)=(p^2/2+cp)/R`: `d h(p(t))/dt >= -(p(t)+c)`.

The integrand in (1) is nonnegative. Productive maximum-rate decline `z'=-R` has zero incremental full-cycle cost over the already inevitable return reserve. This is an accounting/control identity, not free energy or useful computation after EOS.

## 1A. Optional admissible-class strengthening: pre-EOS withholding

The fully productive model is without loss relative to controls `0<=x_dot<=s(p)` under one additional explicit idealization: the same actual power p can always be redirected from intentional burn/throttling into useful service at exactly s(p), without changing any other state or observation. There must be no thermal, storage, clock-dependent arrival, diagnostic, or information benefit from withholding service.

Fix any independent random seed and simulate the original controller on its no-EOS history, including its ghost progress. The new controller follows the same physical power trajectory while assigning all attainable service to actual useful work. Its actual progress is at least ghost progress, so it reaches every W no later. Until this earlier EOS, ghost progress is below actual progress and hence below W, making the simulated no-EOS history causally consistent. At earlier EOS the new controller switches to fastest return. Both trajectories have the same power and incurred the same full-cycle running cost up to this time. The remaining original waveform, including its eventual return, costs at least the reserve H at that power; the replacement costs exactly that reserve. Thus the improvement is pathwise and remains true after averaging random seeds. Idle waits at zero power can also be removed by time splicing without violating slew, provided there are no exogenous or clock-dependent benefits.

The replacement dominates dynamic energy and cycle duration separately, but it need not preserve an EOS-only burn-power or burn-energy cap: earlier EOS can occur at higher power. Those caps require a separate admissible-class argument. This lemma does not assert that a real GPU can redirect an arbitrary burner draw into useful service at unchanged throughput or instantaneous dynamics. Redirectability belongs to the ideal service/actuator contract and must be stated whenever the larger action class is claimed.

## 2. Exact endpoint-recovery restriction

**Theorem.** If `z0<=RM`, replacing any admissible path by

`z_tilde(x)=min(z(x), R(M-x))`

is no worse for every realization W, hence for every work distribution supported on `[0,M]`. It preserves the initial state and the slew constraint. Consequently there is no loss in imposing `z(M)=0` and `z(x)<=R(M-x)`.

**Proof.** The function `z(x)-R(M-x)` is nondecreasing, since its derivative is `z'+R>=0`. Thus the replacement follows the original path up to its first contact `a` with the recovery cone, then follows maximum decline all the way to M. At contact, remaining maximum work is `M-a=A(p(a))/R`, exactly the work performed by that decline. If EOS occurs earlier, the same physical waveform continues as burn. Its entire subsequent cost is exactly `H(z(a))`. Every alternative waveform starting at the same power and eventually returning to zero costs at least that reserve, by the physical inequality above. Worlds ending before a are unchanged. This proves pathwise dominance.

If `z0>=RM`, maximum productive decline serves every possible W before reaching zero, and its full-cycle cost is `H(z0)` for every W. Equation (1) shows this is the absolute global lower bound. The case `z0>RM` must be handled separately; imposing `z(M)=0` there would violate the initial-state reachability condition.

Recovery clipping separately decreases total dynamic energy and cycle duration pathwise, and lowers EOS power pointwise. It therefore preserves a pre-existing hard cycle deadline and EOS burn-power/energy bounds. This does not rescue critical clipping under a hard deadline.

**Important limitation.** `z(M)=0` alone does not imply `T(M)<infinity` when M has probability zero. The previous endpoint-time erratum still applies. The theorem gives a representative with recovery state zero, not an unconditional hard support-endpoint completion guarantee. A hard deadline is a separate constraint and may invalidate critical clipping.

## 3. Critical restriction and nonzero initial power

Let `N(p)=s(p)-(p+c)s'(p)`. Then `N'=-(p+c)s''>=0`, and `sign G'(z)=sign N`. If there is a first finite root `pcrit`, set `zc=A(pcrit)`.

For nonzero initial state the correct cap is

`b(x)=max(zc,z0-Rx)`, `z_tilde=min(z,b)`.

The minimum is R-Lipschitz and preserves z0. Every changed value lies at or above the critical power, so G cannot increase; H is increasing, so its EOS cost cannot increase. Before `tau=(z0-zc)_+/R`, every feasible path obeys `z>=z0-Rx=b`; the restricted path is therefore forced maximum decline. Thereafter it lies below zc. If tau is beyond M, the effective domain is entirely fixed. If no critical root exists, N remains negative and no critical cap is needed; finite work and initial power already bound the reachable states.

For the *previous* dynamic-energy-plus-task-completion-time objective, with terminal `H0=p^2/(2R)`, this proves the nonzero-initial extension: the fixed high-power prefix is followed by the same convex residual problem, now beginning at the critical state. When `p0<=pcrit`, the original convex argument extends directly with fixed `z(0)=z0`. Resource bounds must still be feasible, and terminal-power restrictions violated even by the mandatory minimum state imply genuine infeasibility.

For the *full-cycle* objective in this review, this argument alone does not give convexity, because H is concave below critical. The additional theorem in section 4 is needed. For `z0<RM` with high initial power, its convex result applies after the fixed prefix, with conditional residual work and support length `M-tau`; the same hazard inequality retains `M-x`. Early EOS worlds contribute only a fixed cost. More precisely, when `tau<M`, `J=H(z0)+S(tau)[J_res-H(zc)]` under the forced prefix and conditioning on `W>tau`.

## 4. Genuine full-cycle convex subclass, including idle power

Assume `s(p)=k p^beta`, `0<beta<=1`. For beta below one, `pcrit=beta c/(1-beta)`; for beta one there is no critical root. Suppose mu is absolutely continuous on `(0,M)`, with possible atoms only at 0 and M. Write its interior density f and hazard `h=f/S` where S is positive.

Define `kappa_beta=(1+2 beta)/(1+beta)`.

**Theorem.** If `h(x)(M-x)<=kappa_beta` almost everywhere, then after the exact critical and recovery restrictions, the full-cycle problem is a strictly convex optimization problem on its effective non-fixed work interval. A minimizer exists and is unique there. The result includes Uniform[0,M], power-tail survival `S=(1-x/M)^alpha` for `alpha<=kappa_beta`, and admissible mixtures with endpoint atoms. It charges both full return time and idle energy, so it removes the old cycle-time limitation for this explicitly delimited subclass.

**Independent algebra.** Let `r=(1-beta)p/(beta c)` when beta<1. On `0<p<pcrit`,

`G''/(-H'') = R [2 beta + 1/(1-r)] / [(1+beta)z] >= R kappa_beta/z`.

The inequality is strict at positive power for beta<1. For beta=1 the ratio is exactly `3R/(2z)`. Since recovery gives `z<=R(M-x)`, the assumed hazard inequality implies

`F_zz = S G'' + f H'' >= 0`, where `F=S G+fH`.

Strict convexity holds on the relevant z interval, even for beta=1 where equality can occur at its upper endpoint. At pcrit, H'' is zero and G'' is positive for beta<1. Endpoint-M atoms contribute the constant zero, and the atom at zero contributes a fixed initial-state constant. Compactness of bounded R-Lipschitz paths and lower semicontinuity give existence; a feasible capped tent has finite time and cost because the power-law time singularity exponent is `beta/(1+beta)<1`. Strict convexity with S positive gives uniqueness of the continuous path on the effective interval.

**Keep these exclusions explicit.** Interior atoms and singular-continuous interior probability measures are not covered. General concave service curves are not automatically covered. A hard deadline is not automatically preserved by critical clipping. No hard guarantee at a zero-probability M follows just from expected-cost existence. Positive c, actual-power slew, known fixed service curve, causal instantaneous EOS, and a real burner remain assumptions.

## 5. Sharp no-go results within the exact feasible domain

### 5.1 Sharp power-tail threshold

For `S=(1-x/M)^alpha` and `alpha>kappa_beta`, choose `gamma` between `kappa_beta/alpha` and one. Near M, take a feasible base path `z=gamma R(M-x)`, below the recovery and critical caps and with strict slope slack. Then `h z/R=alpha gamma>kappa_beta`, while `zG''/(-G')` tends to kappa_beta as p tends to zero. Hence F_zz is negative on an open terminal interval. A sufficiently small compactly supported perturbation there preserves all bounds and yields a positive midpoint gap. Thus the threshold is sharp for convexity of the clipped functional over this power-tail family. This does not prove every super-threshold instance has several local minima or a nonglobal numerical solution.

### 5.2 Interior atoms defeat universal convexity

At any positive-power interior atom, H is strictly concave below critical. Start from a path with local cap and slope slack; add/subtract a narrow triangular perturbation of height d and width epsilon, with d small compared with epsilon. The negative atomic second variation has order d^2, whereas the continuous variation is of order epsilon d^2. For sufficiently narrow support the atomic term wins. This constructs feasible full-functional nonconvexity after both caps, not an unreachable pointwise Hessian witness.

Concrete independently checked example: `beta=.5,k=c=R=M=1`, `mu=.5 delta_.5+.5 delta_1`, base `z=.5 min(x,1-x)`, perturbation `+/- .001 max(0,1-|x-.5|/.004)`. Both paths obey the recovery cap and critical cap, and their largest absolute slope is .75. The midpoint objective exceeds the average by approximately `2.1453260889e-7`.

### 5.3 Uniform is not enough for arbitrary concave service

For a general service curve define, where G'<0,

`q(z)=z G''(z)/(-G'(z)) = 3A(p)s'(p)/s(p)^2 - A(p)(p+c)s''(p)/[( (p+c)s'(p)-s(p) )s(p)]`.

A sufficient generic condition is `h(x)(M-x)<=inf_retained_domain q(z)`. The infimum need not be at least one, or even have a uniform positive lower bound over admissible concave service curves.

Counterexample: `s(p)=.1p+1-exp(-p/.001)`, `c=20,R=M=1`, uniform W. It is smooth, strictly increasing, strictly concave, and has no critical root: `N=1-.1c-[1+(p+c)/.001]exp(-p/.001)<0`. At `p=.2`, `z=A(p)` is essentially .201, safely inside both reachability cones at x=.5. Independent values are `G'' approximately .2717`, `H'' approximately -.9423`, and `F'' approximately -.8065`. Base `z=min(x,A(.2),1-x)` plus/minus `.01 max(0,1-|x-.5|/.1)` gives a genuine feasible midpoint gap approximately `2.6882104878e-6`.

Numerical witnesses and the checking script are `FULL_CYCLE_INDEPENDENT_WITNESSES.json` and `check_full_cycle_witnesses.py` in this directory. They use 80-digit floating arithmetic and 675 curvature-ratio checks. They support the algebra but are not interval certificates or statistical experiments.

## 6. Exact deterministic benchmark and global discrete-EOS algorithm

For deterministic `W=M`, idle initial state, and any admissible service curve, the full-cycle optimum is explicitly

`z*(x)=min(Rx,R(M-x),zc)`,

omitting zc if no finite critical root exists. After recovery clipping the terminal cost is zero, and G is decreasing on the retained domain. This path is the pointwise largest feasible one and therefore globally minimizes the active integral. Its physical power waveform rises at maximum slew, possibly stays at critical power, and declines at maximum slew to zero exactly at EOS; burn is zero. The same proof gives, for nonzero z0<=RM,

`z*(x)=min(z0+Rx, max(zc,z0-Rx), R(M-x))`,

with the obvious no-critical-root version `min(z0+Rx,R(M-x))`. For z0>=RM, the direct maximum decline of section 2 is optimal instead.

For finite atomic work support `0=w0<w1<...<wn=M` (allowing zero mass at w0), the problem admits an exact continuous-state dynamic-programming reduction despite possible nonconvexity. Once endpoint states `a=z(wi)` and `b=z(wi+1)` are fixed, survival is constant on the gap. Its optimal bridge is the pointwise maximal feasible function

`z(x)=min(a+R(x-wi), b+R(wi+1-x), zc)`.

The endpoint constraints `|b-a|<=R Delta`, nonnegativity, critical cap, and reachable/recovery cones imply the bridge satisfies both cones. Let `q=(a+b+R Delta)/2`. The exact unweighted gap cost is

- If `q<=zc`: `K(a,b,Delta)=2H(q)-H(a)-H(b)`
- If `q>zc`: `K=2H(zc)-H(a)-H(b)+G(zc)[Delta-(2zc-a-b)/R]`

The first branch is the entire formula when no critical root exists. The full objective becomes the finite chain

`sum_i S(wi) K(zi,zi+1,wi+1-wi) + sum_i mu({wi})H(zi)`, with `zn=0`.

Bellman recursion over the single continuous state zi gives the global optimum. Finite-state grids provide feasible upper approximations. An exact analytic optimistic cell lower bound is also available. For node cells `[a_lo,a_hi]` and `[b_lo,b_hi]`, an edge exists exactly when `a_lo<=b_hi+R Delta` and `b_lo<=a_hi+R Delta`. The coordinatewise largest jointly feasible endpoint pair is `a*=min(a_hi,b_hi+R Delta)`, `b*=min(b_hi,a_hi+R Delta)`. The bridge cost K decreases in each coordinate: before the plateau `K_a=[G(q)-G(a)]/R<=0`, with the analogous critical-plateau formula. Consequently

`S_i K(a*,b*,Delta) + pi_(i+1) H(b_lo)`

is a valid edge lower bound. Its favorable active and EOS endpoints need not coincide, and adjacent cell-edge choices need not describe the same exact endpoint; both relaxations are deliberately optimistic. Bellman minimization over such cells is therefore a continuous-global lower bound in exact arithmetic. Refining all cell widths to zero makes this lower bound converge: choose approximate endpoint representatives from minimizing cell chains; their edge compatibility violations are O(cell width), compactness yields a feasible limiting chain, and continuity of K and H yields its true objective. Feasible grid upper approximations converge as well; slightly contract a feasible path before rounding to obtain slew slack.

The actual implementation evaluates these analytic bounds in floating arithmetic, rather than outward-rounded interval arithmetic. Its reported numerical gap must retain that qualifier. A plain optimizer success flag or a feasible grid alone is not a global certificate.

## 7. Cycle deadline distinction

Where the physical inverse exists,

`T_cycle(w)=integral_0^w 1/s(P(z(x)))dx+P(z(w))/R`,

and its work derivative is `(1+z'/R)/s(P(z))>=0`. Hence, when M is reached in finite time and z(M)=0, worst-case cycle duration is the endpoint active-time integral. The reciprocal-service term is convex in z for increasing concave s. This gives a convex added constraint on an already justified restricted class, but does not prove that imposing a new hard deadline preserves the critical restriction. Calling this globally equivalent with an arbitrary hard deadline would revive the original counterexample. If the unconstrained optimum independently satisfies the deadline, it remains optimal among deadline-feasible paths.

## Audit verdict

The cycle-time/idle limitation can be materially narrowed through two exact dominance restrictions and a sharp hazard-controlled power-law theorem. It cannot be dropped for arbitrary work laws or arbitrary concave service. The initial-power extension is sound with the fixed high-power prefix, feasibility caveats, and the correct distinction between task-time and full-cycle objectives. These are mathematical model results; all previous hardware, fixed-curve, causal-information, completion, and erratum boundaries remain in force.

## 8. Independent implementation audit and resolved issues

The continuous and atomic production artifacts were independently recomputed without importing their integration/model helpers. `INDEPENDENT_NUMERICAL_AUDIT.json` records 24 primary solves, 108 physical paths with 7,092 segments, eight finite-atom cases, all 12 continuous duals, and the finite-grid Bellman comparators. Uniform objectives were recomputed using 60-digit exact weighted power moments; physical segments were recomputed as linear-power time ramps; dual minima were solved in physical power and integrated adaptively. Maximum primary component disagreement was 1.60e-14, path-cost disagreement 3.11e-15, atomic upper-cost disagreement 4.44e-16, and independent dual disagreement 3.95e-12. The continuous relative numeric primal/dual gaps remain 7.78e-8 through 3.137e-6. Raw physical slew excess reaches 1.883e-9, so these are numerical feasible policies, not an outward-rounded machine safety certificate.

Two pre-release implementation issues were corrected and retained as evidence by the main worker: (1) free-node lower-bound values had incorrectly remained in the linear-constraint offset for nonzero initial states, and (2) clipping only the old policy's sampled nodes did not implement the true off-grid recovery-cone crossing. The repaired solver zeros free entries in the offset, guards nonaligned critical-prefix breakpoints, and the exact recovery transform inserts crossing points. `TRANSFER_REPAIR_INDEPENDENT_AUDIT.json` independently verifies all 12 distribution-transfer cases, six nonzero cases, 12 N256 refinements, six accounting ablations and four nonzero Bellman comparators using physical-power-coordinate quadrature. Their maximum component differences are respectively 3.05e-14, 1.84e-14, 3.24e-14, 2.67e-14 and 2.23e-16. Both prepaid nonzero cases equal H(z0) within 4.45e-16. All tested transfer laws satisfy the stated hazard criterion.

The saved audit JSON files contain the exact source hashes reviewed. After these repairs there is no unresolved material theorem or primary numerical issue in the audited scope. Later exploratory trace and baseline additions are covered in the final sections below. All floating/physical-contract and prior-round erratum limitations above remain required.

## 9. Final baseline correction, matched-time frontier, and trace check

A third pre-release issue affected the constant-target comparator: a generic bounded scalar optimizer could stop inside a flat region of targets above the physically reachable peak. That result was a feasible baseline, not a globally optimized target baseline. The old maximum weighted improvement around 6.85% is withdrawn. The repaired exact uniform baseline uses the unique root `(1-beta)p+(2/R)p^(beta+1)(p+c)=beta c`, capped by `P(R/2)`. Its expected components are evaluated analytically on the actual waveform, with off-grid knees preserved. The derivative is `J'(q)=(1-2q/R)[G/R+G'/2]`, which proves the root characterization. For atomic work laws, enumerate all branch breakpoints `q=Rw_i`, `q=R(1-w_i)` and all admissible stationary roots between them; the derivative's sign is governed by a strictly increasing expression on each such interval. This makes the repaired comparator globally optimal within the explicitly stated constant-target class.

At matched mean cycle time, target energy increases with target power below the reachable peak, whereas target time has a unique minimum at `p^(1+beta)=beta R/2`. Thus the smaller-power solution of a feasible time match minimizes target energy; if the proposed time lies below that global target-class minimum, no matched-energy comparison exists. The six feasible saved cases have dynamic-energy savings approximately 0.455% to 3.866%, and allocated-facility energy savings approximately 0.304% to 3.360% at the stated synthetic idle coefficient 0.1. The other six are honestly classified as target-class time infeasibility; they must not be assigned a fabricated energy-saving ratio. These are mean-cycle comparisons in the ideal model, not a full facility or hardware measurement.

`FINAL_BASELINE_TRACE_AUDIT.json` verifies every repaired uniform baseline component against an independently derived reserve-integral formula to 1.78e-15, and checks all matched-time classifications and energy-minimal branches. The exploratory trace-derived model uses 623 positive empirical generated-length atoms from 19,366 request rows, normalized by 1,000 tokens, with separately assumed synthetic service and slew. Its observed distribution is not a measured EOS-reason trace or a prospective support guarantee. Both complete saved policies were independently reconstructed from 2,402 shared physical bridges, covering 1,246 possible termination paths: maximum path-cost difference is 4.89e-15. Independent n128 interval-box and grid Bellman recomputations match within 4.45e-16. Final trace mean costs are 0.5836288581141714 and 1.4364445298372162; repaired constant-target objective improvements are 3.836834% and 5.344176%. Their numerical continuous-global relative gaps remain approximately 0.0746% and 0.3327%. These are two exploratory model calculations, not 19,366 independent energy experiments.

## 10. Exactly feasible inward policies

The raw solver outputs and all their physical ledgers remain unchanged. An additional family `z_safe=(1-1e-7)z` for the twelve idle-start primary cases is stored separately in `SAFE_PRIMARY_PATHS.json`. Under its explicitly declared contract, each stored IEEE binary64 node is interpreted as its exact rational value; beta, R and c are the exact printed decimal model parameters. The independent `SAFE_INNER_POLICY_AUDIT.json` checks startup, recovery, zero endpoints, positive interior and all slew slopes using exact rational arithmetic. The critical cap is also exact: for rational beta=n/d, compare `[(1+beta)z]^d` with `pcrit^(n+d)`. All checks pass, with minimum exact slew margin 4.811797787995786e-8. These nodal bounds imply the same bounds throughout each linear segment; the positive end segments also give finite completion at M.

The independent 60-digit objective recomputation agrees within 8.89e-15, and endpoint cycle times within 1.34e-15. Reusing the valid continuous duals gives relative numerical gaps 8.7016e-8 through 3.13708e-6. The final matched-time comparison uses these additional safe paths. Exact rational feasibility is a genuine model-trajectory certificate, but the objective, physical-time integrals, and dual integrals remain floating evaluations, not directed-rounding value certificates or measured hardware safety claims.
