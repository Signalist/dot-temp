# Independent G6 round-3 skeptical proof and implementation review

Date: 2026-10-04. Scope: `theory/THEOREMS.md`, rational fixed-angle certificate, bounded-mismatch experiments, and the post-protocol same-job DAG extension. This review does not establish novelty or a new nonlinear-network safety result.

## Decision

**Accept T1–T5 with the hypotheses and narrow scopes currently stated. No mathematical blocker found.** The significant contribution of the round is a clearer information/implementation boundary, not a superior general admission solver. T3a is important: this cardinal sliding-window problem already has an ordinary integral LP and standard interval-flow solution.

The exact rational support bracket is a genuine enclosure for the explicitly declared contraction–rotation family. The network brackets remain ordinary floating evaluations of conditional modal-LTI bounds. These are different evidence levels and must remain separate.

## T1: one-sided quadratic parameter-grid error

### Independent proof check

Put A=||a||₂ and f_N(theta)=Σ_(k<N) r^k A|cos(k theta+alpha)|. Away from its zeros, each term has second derivative −k² times itself, hence is bounded below by −A k²r^k. At a zero, its first derivative jumps upward by 2Akr^k. Therefore the distributional second derivative satisfies

f_N'' ≥ −A C_(2,N), where C_(2,N)=Σ_(k<N) k²r^k.

Thus f_N(theta)+A C_(2,N)theta²/2 is convex. Applying its chord inequality on [l,u] and subtracting the quadratic term gives

f_N(theta) ≤ chord(f_N)(theta)+A C_(2,N)(theta−l)(u−theta)/2.

The product is at most (u−l)²/4, proving the coefficient 1/8. No upper bound on the number of kinks is needed. Dense positive curvature atoms cannot invalidate this one-sided inequality. The argument would not justify a two-sided smooth interpolation error across the same kinks; the statement correctly does not claim one.

The omitted terms satisfy 0≤F−f_N≤A r^N/(1−r), uniformly in theta. The lower endpoint is the maximum of finite supports at actual grid parameters. Adding the uniform tail and interpolation allowance supplies the upper endpoint. The first-order comparator follows separately from Σ kr^k=r/(1−r)². Taking the smaller valid bound is legitimate.

A smooth N=2 example shows 1/8 is asymptotically sharp in this general form: take a=(1,0), a cell of width h centered at theta=pi, and gap r(1−cos(h/2)). Dividing by r h²/8 tends to one.

### Quantifiers

One theta must be fixed throughout the trajectory, with its supremum outside the complete support. The draft maintains this. The dynamic-optional H extension uses the same theta in all three F components; its error coefficient is their half-sum, but their maxima must not be added independently.

An exact finite counterexample makes the distinction visible. For r=.7, N=2, a=(.5,.5), theta∈[0,pi/2], the shared-theta maximum of H is .85, while half the sum of the three separately maximized F functions is 1.025. The latter is only an information relaxation.

The r_hi endpoint assertion is correct for an independently uncertain fixed scalar r in this family, because every summand is nonnegative and increases with r. It is not a general uncertain-matrix result. Neither rational/irrational classification nor an infinite Diophantine invariant is identified from finite observations.

### Independent checks

The original validation script partitions each tested cell at **every finite-prefix trigonometric zero**. Within each resulting smooth component f_N''≤0, so it tests endpoints and the unique possible derivative zero. This is a different maximization procedure from the producer’s parameter grid. All 72 cases passed, including negative angles, mixed-sign a, r=.995, and one cell containing 352 kinks. The separate smooth example gives gap/bound ratios approaching .99999998.

These finite floating checks corroborate the implementation; the distributional argument proves the arbitrary-kink and infinite-tail statement.

## Exact rational enclosure: accepted as implemented

The certificate specifies r=17/20, theta∈[11/20,17/20], a=(1/2,1/2), N=512, and scale S=10^120.

1. For either trig function, the degree-160 Taylor polynomial has remainder bounded by |theta|^161/161!, since every derivative of sine/cosine has magnitude at most one. The sine polynomial happens to have no degree-160 term; this does not invalidate the degree-160 Taylor remainder.
2. Every coefficient, grid angle, Taylor term and remainder is evaluated with exact Python integers/Fractions. Floor of the lower scaled endpoint and ceiling of the upper scaled endpoint round outward, including negative values.
3. Multiplication uses the minimum/maximum of all four endpoint products, then floor/ceiling after division by S. Absolute value correctly returns zero as its lower endpoint when the interval contains zero. These operations are inclusion-preserving.
4. The paired sine/cosine update evaluates both right-hand sides from the old pair. Induction therefore encloses cos(k theta), sin(k theta), r^k, every absolute projected term, and their sum. Dependency may widen the interval but cannot defeat containment.
5. isqrt(S²//2)+1 is a valid upper integer enclosure of S/√2. The exact finite C_(2,N) and tail are then multiplied by this norm upper bound. Thus the total upper bound is not obtained by naively adding the error to a lower grid estimate.
6. The maximum of grid interval lower endpoints is below the actual grid maximum; the maximum of their upper endpoints is above it. Decimal strings round lower bounds downward and upper bounds upward. Reciprocal capacity endpoints reverse the support endpoints correctly.

The independent script exercises 1,500 signed rational interval cases; checks all 129 prefix supports by **direct** sin(k theta)/cos(k theta) at 180-digit precision, without the producer’s trig recurrence; checks all raw serialized rational grid intervals, C₂ and tail; and verifies all five support and reciprocal bracket serializations using exact rational comparisons. The source hash matches the saved certificate. All passed.

The direct mpmath calculations are diagnostics, not the source of rigorous rounding guarantees. The Taylor/interval induction above is what makes the certificate exact.

Finest saved robust support enclosure:

[2.8623636724591267663858792605385748155190,
 2.8625898942636140397383614235755641321063].

The first-/second-order error ratio about 138.378 is a comparison of conservative analytic grid-error budgets for this setup. It is not an observed speedup, not a ratio of actual approximation errors, and not evidence of a network-model certificate.

## T2 and T2a: exact circular sector and direct-piece complexity

For any nonzero a, positive homogeneity yields F(R_phi a)≤M||a||₂. If a maximizing angular direction alpha* is alignable through the allowed **single fixed common** orientation interval, equality is attained. Therefore the indicated robust unit boundary is exactly circular on the aligned sector.

The cone-intersection condition is essential and is now stated correctly. A nonzero uncertainty width with an arbitrary center need not align a maximizing direction in a preselected capacity cone. No switching orientation, independent port uncertainty, or uncertainty in theta is substituted for the stated model.

On a closed slope interval within that sector, f(t)=M√(1+t²) has f''(t)=M/(1+t²)^(3/2). For an affine piece of length d, strong convexity implies

f(left)+f(right)−2f(mid)≥kappa d²/4.

Three uniform approximation errors bound the same centered difference by 4epsilon. Hence d≤4√(epsilon/kappa), and at least D√kappa/(4√epsilon) pieces are necessary. Equal-spaced chord interpolation is convex, lies above f, and has error ≤K(D/m)²/8; the stated sufficient count follows. The lower bound applies even to nonconvex continuous piecewise-affine approximants; the upper construction supplies a safe gauge on this sector.

The claim is local **direct gauge/polygon representation** complexity. An SOC representation remains constant-size; the result is not a general computational lower bound. If a radial metric is later added, the historical reciprocal-gauge approximation-class restriction must remain in force.

For a sector centered at a fixed finite interior slope, tan is smooth with positive derivative, so D=Theta(delta). The lower-bound scale delta/√epsilon and crossover epsilon≪delta² are correct. Constants/domain widths depend on delta. The delta=0 historical exact-angle logarithmic theorem and the fixed positive-delta circular-sector asymptotics are compatible. This does not show an engineering-significant effect at a prescribed coarse tolerance.

Independent tests confirm an explicit elliptical gauge aligns to a circle where allowed and fails to do so for a miscentered interval; nine chord/midpoint cases and all 12 saved crossover rows pass. These are diagnostic checks of the constants, not an empirical grid-orientation uncertainty model.

## T3: startup, time reversal and tails

After a mismatch word z is fixed, each common sign independently maximizes its scalar coefficient, yielding |p_j+q_j| or |p_j−q_j|. This elimination is exact because common signs have no additional inter-block restrictions.

The finite language must include short startup windows, equivalently zero-pad before and after the word. In particular, when N<L the whole N-word is constrained by B; a vacuous “only full windows” implementation would be wrong. The current mathematical statement and implementation avoid that error.

Reversing a word preserves its contiguous-window counts. This justifies optimizing coefficients ordered current-to-past and exporting a chronological reversed witness. Extending a prefix by zero mismatch adds the nonnegative reward |p_j+q_j|. The monotonically increasing finite support converges to infinite-history support when the absolute coefficient envelope is summable. The tail Σ(|p_j|+|q_j|) safely dominates any constrained mismatch continuation.

Likewise, each fixed admissible word’s support has phase Lipschitz constant bounded by the independent-port coefficient derivative envelope. Supremizing over a phase-independent word language preserves that common bound. No maximizing word must remain fixed as phase changes for the upper envelope argument.

All 85 independent exhaustive language cases pass, including N<L, B=0, B=L, reversal and both-side zero padding. The tests also exercise the compiled DP directly, not a rerun of its producer script. The C++ storage has capacity for L≤8; the experiment fixes L=8 and makes no general-purpose arbitrary-L implementation claim.

## T3a: integral LP and interval flow

**Accepted; this is the appropriate stronger baseline.** In chronological row order, each mismatch variable occurs in a consecutive interval of padded-window rows. The window matrix is totally unimodular; adding box-constraint identity rows preserves integrality, and B is integral. For N≥L, the ordinary full windows already dominate every partial edge window because z≥0. For N<L, the sum of the entire word must explicitly be bounded, or the padded rows retained.

Interval j occupies [j,j+L). Its overlap at integer cut t is precisely Σ_(j∈[t−L+1,t])z_j, giving the padded-window constraint. A forward unit-capacity job arc and consecutive capacity-B time arcs form the standard B-machine interval-selection flow network. Every selected interval set of overlap at most B can be greedily colored into B nonoverlapping chains; those chains are flow paths. Conversely every B-unit integral flow gives such chains. Sending B units is harmless even if fewer jobs are chosen because zero-cost time paths remain. Negative-value jobs can be omitted. B=0 is correctly trivial.

An independent integer-cost residual-flow implementation is tested against exhaustive words and a separately assembled fully padded LP in 69 cases, including L=1 and N<L. Every exact flow optimum and LP optimum agrees with enumeration. No suffix-state DP or producer LP function is used in these tests.

## T4: asymptotic zero rate still gives independent all-time support

The proof has the correct order of quantifiers. Every finite independently signed maximizing word determines a finite mismatch word. Completing the current block and then using zero mismatches forever gives a deterministic admissible sequence with asymptotic rate zero. Thus every independent finite-horizon optimum remains available. Taking the supremum over finite horizons recovers the independent all-time support.

There need not be one finite horizon attaining an infinite sum, and a single infinite maximizing trajectory need not have zero rate. Neither is required for the robust all-time supremum. Expected-rate versions also admit the same deterministic finite-burst sequence. Finite mission risk, stationarity and a uniform prefix/token-bucket restriction are different assumptions, as the draft correctly says.

The six B=8 exported maximizing words supply concrete finite counterexample prefixes. Their zero-mismatch continuations have finite total mismatch counts and rate tending to zero.

## Contract data: independent checks and inherited limitations

All 30 saved maximizing words were checked directly against the frozen source coefficient files; reversal, mismatch bits, all-phase maximum, threshold-to-amplitude arithmetic, and the .051-Hz finite linear probe at 1.02 times the outer amplitude were independently recomputed. Thirty separately assembled selected-row LPs agree within numerical tolerance. Every pointwise nesting relation across B was checked. All 30,840 schedule segments match their raw word signs and template levels; all 7,710 two-port blocks have zero incremental energy. Fifteen positive-baseline witnesses are physically nonnegative; the 15 WECC signed-injection witnesses are not physical compute-load realizations. Eight inherited coefficient/kernel/support/bound file hashes match provenance.

The reusable phase/tail bounds are the independent-port envelopes accepted in the prior G6 audit and remain conditional on the frozen modal kernels. This round does not re-establish a uniform original-descriptor-to-modal error enclosure and does not upgrade doubles to directed interval arithmetic. The 1.02 scaling gives .051 Hz by linearity and is a finite **linear** witness calculation, not a new nonlinear trajectory.

Preserved failures and scope gates:

- Positive Kundur baselines are 50 MW each, but nominal voltages about .945044/.948743 pu are not voltage-qualified hosting
- WECC supplemental compute baseline remains zero
- The prior WECC dynamic-optional inner nonlinear witness remains about .05310 Hz against .05 Hz; no failure is erased or overturned
- No family-wide nonlinear safety, real scheduler enforcement cost, extra mean-load hosting, or measured throughput gain follows

## T5: same-job realization

All four macroplans are valid topological orders of the specified DAGs. Independent enumeration finds six total topological orders for the first DAG and four for the second; both advertised complementary plans are among them. Each runs the same four labeled jobs once in the same four slots, uses two H and two L power levels, and hence preserves job-completion work, makespan and electrical energy without assuming an affine power-to-work conversion.

The common-order relation has two precedence pairs for port 1 and four for port 2. Consequently 4 and 16 subsets of the six possible plus-compatible edges preserve both orders, matching the saved 128-case sweep. The additional edge H2→L1 genuinely excludes port 1’s negative macroplan while preserving its positive one. Equal work/energy does not make that missing control action legal.

The result is an existence construction for a declared synthetic per-job service/power model. It removes the affine-work assumption **only for this explicit class**. It does not demonstrate that actual GPU job power is rectangular, duration independent of operating conditions, synchronization free, or switching cost zero. Separate blocks must be fresh job instances without unmodeled inter-block dependencies or tighter release/deadline constraints. Changing amplitude changes the declared job catalog; the numerical amplitude sweep is not a demonstrated scaling of the same measured workload.

This extension was added after the primary protocol and is correctly labeled as such. Its local check is not empirical compute validation or a new scheduling theorem.

## Reproduction and evidence level

Run from the workspace:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python outputs/round3_g6_20261004/validation/independent_review_checks.py

Outputs: `INDEPENDENT_CHECK_RESULTS.json` and the redirected run log. The test script imports no producer top-level experiment. It isolates only the candidate rational interval primitives for primitive-level algebra checks and independently evaluates their outputs. The network LPs and residual-flow solver are separately written.

All current assertions pass. The proof review, exact interval argument, high-precision diagnostics, floating network tests and historical nonlinear evidence are explicitly different forms of support. Publication novelty remains a separate literature question.
