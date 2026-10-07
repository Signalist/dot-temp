# Independent G6 adversarial proof and application audit (final)

Completed: 2026-10-03 13:06 UTC. Scope: sampled carried-state rotation model, three distinct amplitude contracts, representation complexity, and numerical evidence wording. This review independently derived the key inequalities before inspecting `theory_review/G6_STRUCTURAL_AND_COMPLEXITY_PROOFS.md` in full. It did not import the candidate numerical kernels.

## Decision

**Accept the mathematical claims with the explicitly stated hypotheses and metric. No mathematical blocker found in the final draft inspected.** The support series and rational formula are old; the arithmetic classification and sharp static-optional masking threshold are independently valid narrower results. This audit does **not** establish publication novelty or a practical grid-controller advance.

Mandatory communication boundaries:

1. The logarithmic result concerns the convex gauge on a fixed, nonzero-width interior slope interval. Its radial version counts polyhedral approximants whose radial function is the reciprocal of a piecewise-affine gauge. It does not count ordinary piecewise-affine interpolation of the radial function itself.
2. Infinite exponential approximation type provides sublogarithmic **subsequences**, equivalently a zero liminf ratio. A full little-o statement at every sufficiently small accuracy is unsupported.
3. The r=1/2 threshold belongs to one optional cohort held fixed forever, with B=I and C=(1,0). It must not be extended to independently varying amplitudes or arbitrary port coordinates.
4. The proofs start from zero deviation state and protect sampled outputs. Intersample output constraints and nonzero initial state are additional problems.
5. Numerical evaluations use ordinary floating point. Analytically justified tail formulas do not make their floating evaluations outward-rounded certificates.

## Claim-by-claim review

### A. Exact carried-state support and the older formulas: ACCEPT; no novelty

For x_0=0 and arbitrary common signs, the finite-horizon maximum is

    F_N(a)=sum_{k=0}^{N-1} r^k |a_1 cos(k theta)-a_2 sin(k theta)|.

The partial sums increase, so all finite times are safe exactly when F(a)<=1. The maximizing sign sequence may depend on the horizon; the universal safety quantifier makes this harmless. No stationary-state assumption is required.

Duda explicitly gives the exponentially weighted absolute-cosine sum in Eq. (14), its rational-angle geometric-series reduction in Eq. (15), and the support self-similarity framework in Eqs. (11)–(12). His contraction is written as the reciprocal of a radius greater than one. Write a=||a||(cos phi,sin phi) and shift his angle by phi-theta to obtain the present series up to a constant factor. The exact series, finite rational formula, and broad rational/irrational geometry are therefore not a defensible new contribution here.

Primary source inspected: Jarek Duda, *Analysis of the convex hull of the attractor of an IFS*, arXiv:0710.3863v2, pp. 6–8, https://arxiv.org/pdf/0710.3863v2 ; bibliographic record https://arxiv.org/abs/0710.3863v2 . This source is credited, rather than copied into the deliverable.

### B. Dense kinks and nonpolyhedrality: ACCEPT

For irrational theta/pi the positive roots t_k=cot(k theta) are distinct and dense on every nontrivial positive slope interval. At such a root the jump in the derivative of f(t)=F(1,t) is exactly 2r^k|sin(k theta)|. Differentiability of the other terms follows by dominated convergence using their summable Lipschitz constants. Dense nearby kinks do not cancel the selected jump.

There is also a direct strict-triangle-inequality proof: any two nonparallel vectors have opposite projection signs on an open set of directions, and the irrational orbit visits that open set. Thus the corresponding unit ball is strictly convex. The positive-quadrant gauge is nevertheless nonsmooth on a countable dense set, which is consistent with strict convexity.

For rational theta/pi=p/q in lowest terms, exactly floor((q-1)/2) cancellation rays lie strictly inside the positive quadrant, hence ceil(q/2) affine regions. The q=1 case is an unbounded strip, and requires separate treatment from a two-axis bounded admission set.

### C. Finite exponential type lower bound: ACCEPT

The correct invariant is

    beta(alpha)=limsup_{q->infinity} log(1/||q alpha||_Z)/q,
    alpha=theta/pi irrational.

This is not the ordinary polynomial irrationality exponent. Fix J=[l,u] with 0<l<u<infinity, and choose a strictly interior subinterval J_0. For each B>beta(alpha), B>0, there is c>0 such that ||q alpha||>=c exp(-Bq) for all q>=1. Among the first K orbit points, a positive fraction have roots in J_0, by ordinary equidistribution. Their pairwise root separation is at least pi c exp(-BK), since their folded angular differences lie within one positive quadrant and |cot'|>=1.

Place disjoint neighborhoods of common radius delta_K>=c_0 exp(-BK) around those roots. At each selected root k<=K the kink weight is at least r^K/sqrt(1+u_0^2). Convexity of every remaining term makes its centered second difference nonnegative. Therefore any approximant affine on that neighborhood has uniform error at least

    r^K delta_K / (2 sqrt(1+u_0^2)).

An m-piece function has only m-1 breakpoints. Choosing K proportional to m supplies more disjoint neighborhoods than breakpoints, so some neighborhood is affine. Consequently its error is at least C exp(-C' m), establishing m=Omega(log(1/epsilon)). Geometric-tail truncation gives the matching O(log(1/epsilon)). The lower proof does not assume convexity of the approximant; the upper proof supplies convex homogeneous safe gauges.

For H=(F+L)/2 the local jump is halved and the same proof applies with changed constants. Neither a quantitative equidistribution rate nor an unproved spacing heuristic is needed.

### D. Infinite exponential type necessity: ACCEPT, with subsequence language

For any integer q define the folded true-angle gauge

    G_q(a)=(1-r^q)^(-1) sum_{j<q}r^j |u_j dot a|,
    Delta_q=dist(q theta,pi Z).

For k=j+lq, the projection differs from its j-th folded value by at most ||a|| l Delta_q. Summing both geometric series gives

    |F(a)-G_q(a)| <= ||a|| Delta_q r^q / ((1-r)(1-r^q)).

This remains valid for large l Delta_q. The same estimate holds for the hexagon support H because the support of the one-block uncertainty set is ||a||-Lipschitz in the projection direction. A linear safety correction proportional to a_1+a_2 yields a true upper gauge with at most q+1 regions.

If beta=+infinity, choose q_j with log(1/||q_j alpha||)/q_j tending to infinity. For the displayed analytic error scales epsilon_j, (q_j+1)/log(1/epsilon_j) tends to zero. Hence no eventual logarithmic lower bound holds. Together with C, this proves the stated iff classification. It proves liminf N_J(epsilon)/log(1/epsilon)=0, not a full limit of zero.

A single very small rational residual in a finite experiment cannot establish beta=+infinity. The near-rational numerical case is properly only a mechanism diagnostic.

### E. Gauge, halfspace and inverse-radial metrics: ACCEPT with approximation-class condition

For origin-containing polyhedral admission approximants with m upper halfspaces, the gauge on J is the maximum of at most m affine functions. Thus the general piece lower bound applies. The safe constructions in C and D have O(K) actual angular regions, not 2^K effective regions.

If 0<m_0<=f<=M_0 on J, and |g-f|<=delta<m_0/2, then

    |1/g-1/f| <= 2delta/m_0^2.

Conversely, sufficiently small reciprocal error epsilon gives |g-f|<=2M_0^2 epsilon. The target here has m_0>=1. Multiplication by sqrt(1+t^2) converts slope-radial displacement into Euclidean radial displacement, with fixed constants on J.

This transfers complexity for a polyhedron's radial boundary 1/g. It does not transfer the *piecewise-affine approximation class* through inversion. Even a single nonconstant affine gauge has a curved reciprocal; ordinary PL interpolation of its reciprocal has error of order m^-2. The independent script includes this simple diagnostic.

### F. Optional fixed-cohort box formula: ACCEPT

Convex vertex testing gives

    sup_{0<=b<=a}F(b)=max(c_1a_1,c_2a_2,F(a)).

Therefore its domain is the full axis-intercept rectangle iff Q=F(1/c_1,1/c_2)<=1. If Q>1, the F=1 boundary passes strictly inside that rectangle and contributes an open, genuinely nonpolygonal arc for irrational theta/pi. Merely seeing dense kinks in F would not suffice if they were all masked by the axis constraints; the corner test correctly resolves that point.

### G. Sharp r=1/2 threshold and small-angle formula: ACCEPT

At the normalized corner, set alpha_k=r^k cos(k theta)/c_1 and gamma_k=r^k sin(k theta)/c_2. Their l1 norms are one; alpha_0=1/c_1 and gamma_0=0. The tail reverse triangle inequality proves Q>=2/c_1. If sin(theta)!=0, c_1<1/(1-r), so Q>2(1-r)>=1 for r<=1/2. Strictness is valid at r=1/2 and is not a numerical edge-case inference.

As theta decreases to zero, dominated convergence gives

    Q -> 2(n+1)(1-r)r^n,
    n=floor(r/(1-r)).

This is twice the positive-part difference between a geometric probability mass and its size-biased derivative mass. On each interval n/(n+1)<=r<(n+1)/(n+2), differentiating gives sign n-(n+1)r. The neighboring formulas agree. Thus the limit is below one for every r>1/2, establishing an open small-angle rectangle regime. Integer values of r/(1-r) cause no discontinuity; the zero term at k=n contributes nothing.

The draft's explicit r=9/10, theta=1/100 example is stronger than a plot: the stated Taylor error bounds rigorously bound the l1 distances of normalized signed cosine/sine sequences from their limits. The resulting rational upper bound on Q is below one. The fact that theta/pi is irrational follows from irrationality of pi, rather than finite floating-point digits.

### H. Dynamic optional-amplitude identity and no rectangle: ACCEPT

For each lag and every real p,q,

    max(|p|,|q|,|p+q|)=(|p|+|q|+|p+q|)/2.

The independent per-block choices permit these maxima before summation, giving H=(F+L)/2. Holding one b forever instead requires a maximum after summation; these operations do not commute. The independent code exhaustively verifies a five-block case over 32,768 vertex/sign words and records a strict discrepancy.

At the axial top corner, H=1+Q/2>1. Dynamic optional admission is therefore never that rectangle when both intercepts are finite. In the irrational case, its interior kinks and strict triangle inequality remain, so it is nonpolyhedral. This conclusion holds for all 0<r<1 and does not inherit the static-only masking threshold.

### I. Nonzero initial states, sampled safety, physical realization: ACCEPT as scoped; block overgeneralization

For a fixed initial state x_0, the exact finite-horizon worst absolute output is

    |C A^N x_0|+F_N(a),

not simply F(a). With an initial uncertainty set, the corresponding translated support must be maximized explicitly. The script supplies x_0=(0,10), r=.85, theta=.7, a=0: the initial output is safe and F=0, but the first output violates the limit. An output-safe initial strip is insufficient.

The zero-area template Gramian construction is algebraically sound. For nonzero rotation frequency, differentiating a hypothetically constant projection shows orthogonality to both A_c g and A_c^2 g, independent vectors, so the centered Gramian is positive definite. Centering ensures zero block area and inversion assigns the desired sampled input column. Fixed baselines can ensure nonnegative bounded power over bounded capacity boxes. This is not a claim about practical peak/ramp limits or about equal task work without the explicit constant-energy-per-work model.

The intersample formula is also correct: the present block has coefficient C D(t), past blocks have C exp(A_ct) A^j, and their independent signs can be optimized. Endpoint equality to F does not eliminate the phase supremum. No sampled-state representation theorem has yet been transferred to the full phase-supremum admission set.

## Numerical code review

Reviewed candidate files `src/run_structural.py`, `run_dynamic_optional.py`, `run_shared_parameter.py`, `run_face_budget.py`, and the corresponding mathematical kernels.

- The common-sign finite-state recurrence preserves startup prefixes; it does not silently replace their maximum by the final stationary-like term.
- Dynamic optional support and its independent-port comparison use the correct quantifiers.
- Shared-theta grid uncertainty uses the valid Lipschitz constant ||a|| r/(1-r)^2 and half-grid spacing. The endpoint-switching DP is valid because planar rotations commute: lag k depends only on k and the count of high-angle transitions. This special argument is not a theorem for arbitrary noncommuting uncertain matrices.
- The adaptive chord comparator majorizes the finite convex series, and its largest chord gap occurs at a series kink. Adding the reference tail to the reported gap is conservative for absolute gauge error. The exact-knot comparator can outperform truncation; no new-solver benefit is established.
- The Euclidean per-term dynamic optional tail bound is valid, since every vertex of the amplitude box has norm at most ||a||.
- Ordinary trigonometric evaluation and root deduplication are not exact symbolic arithmetic. The rational pi/4 folded residual prints zero by floating cancellation; that case must either be labeled symbolically exact or treated as a numerical residual, not a rounding certificate.
- Suggested terminology corrections sent to the parent: replace `Certified-formula` in the face-budget docstring and `rectangle_certified_by_tail` / `strict_switching_gap_proven_by_numeric_bounds` flags with explicit float-bound check language. The formulas may be rigorous; the stored doubles are not validated enclosures.

## Independently reproducible checks

Run:

    python outputs/round2_g6_joint_admission_20261003/audit/independent_checks.py

The script is original and imports no candidate kernel. It writes `INDEPENDENT_CHECK_RESULTS.json` and checks:

- 2,000 randomized one-block support identities; maximum observed error 8.89e-16
- All 32,768 amplitude-corner/sign words for a five-block dynamic example
- A period-seven rational identity at 75-digit working precision
- 32 threshold/corner cases across r=.2 to .98, including r=.5
- Nine small-angle limits, including integer mean boundaries
- Four true-angle folded approximants against analytic uniform error bounds
- Thirteen separated early-kink three-point obstructions
- A concrete nonzero-initial-state counterexample and the reciprocal-PL class warning

All implemented assertions passed. These tests corroborate implementations and detect quantifier errors; the analytic arguments above carry the theorem claims. Finite runs cannot demonstrate asymptotic necessity, actual irrationality of machine numbers, or research novelty.

## Frozen network-transfer follow-on audit

The transfer study's original-source qualifications and implementations were subsequently inspected in `transfer/run_transfer.py`, `validate_transfer.py`, `verify_wecc_descriptor_time.py`, and their recorded results. The phase-mesh bound is mathematically valid for the selected stable modal kernel: it uses the minimum of a global first-derivative envelope and a sampled derivative envelope enlarged by the exact modal derivative tail plus a half-cell second-derivative bound. Every forcing-switch phase is a mesh endpoint, and both one-sided derivatives are considered. The same independent-port envelope safely dominates the common-sign, fixed-optional, dynamic-optional, reset and single-sign contracts. The current-block and past-block coefficient indexing is consistent.

An additional original script, `independent_transfer_checks.py`, imports none of the candidate code. It reloads the original frozen source matrices, evaluates four previously unused resolvent points (including a purely imaginary point), checks original Kundur matrix-exponential impulse responses at five times, recomputes full-grid support maxima for five rays, and verifies all 123 finite maximizing witnesses and their permitted one-block amplitude/sign sets in each network. All assertions passed. Maximum new resolvent relative discrepancies were 2.84e-14 for Kundur and 1.15e-10 for WECC; witness projection discrepancies were zero in the stored double data. Results are in `INDEPENDENT_TRANSFER_RESULTS.json`.

The qualification still has an important limit: the WECC construction clusters nearly repeated eigenvalues and performs ill-conditioned block residue recovery (reported maximum Gram condition about 3.39e12). Excellent finite resolvent tests and finite-time descriptor replays are numerical evidence, not a uniform enclosure of the discrepancy between the descriptor and modal model. Thus the infinite-tail and continuous-phase analytic bounds apply to the qualified modal kernel. They must not be called a validated all-time certificate for the full original descriptor or nonlinear network without a separate uniform model-error bound.

The original frozen ports have baseline incremental active powers [0,0] in both networks. Large background constant-impedance loads at the selected buses are not automatically controllable compute baselines. Therefore the original network results describe **signed incremental active-power injections**. The abstract positive-baseline equal-work realization does not make those original perturbation ports physically nonnegative compute loads. A separately reinitialized positive-load workpoint was subsequently evaluated and independently audited below; it does not retroactively change the original signed-injection results.

The WECC original-descriptor witness replay subsequently reported three equal-split 256-past-block witnesses at dt=1/64, 1/128 and 1/256, with approximately second-order refinement and final maximum relative discrepancy 4.032e-5. This is additional finite-time linear qualification and does not remove the preceding all-time model-error caveat.

## Audit repairs and local-freeze timing

The parent confirmed that the ambiguous numerical certification/proof labels identified above were replaced by explicit float-bound-check wording, and that the rational pi/4 fold is now identified as symbolically exact. Those terminology issues are resolved.

The face-budget script initially wrote a local pre-loop configuration record, then accidentally regenerated its timestamp during a later wording-only rerun. The recorded cases, interval, tolerances and comparators were unchanged, and the current script now preserves the existing record. The saved timestamp is therefore regeneration time, not independent evidence of a fresh blinded experiment. `protocol/FREEZE_TIMING_AUDIT.md` transparently documents this limitation. All such files are local computational freezes, not third-party preregistrations. This audit did not independently witness their earlier timestamps and does not make an external preregistration claim.

The proof author incorporated the explicit origin-containing polyhedron requirement and inverse-radial approximation-class distinction requested by this audit. The added finite-phase realization argument is also valid: the response curve has full affine span; three sufficiently small intervals around affinely independent response values give an invertible area-plus-endpoint matrix. Solving its three constraints produces bounded piecewise-constant zero-area forcing with the desired column. It does not enforce finite slew rates.

## Open gates and stopping scope

No outstanding mathematical blocker in the narrowly stated theorem draft. Outstanding external gates are novelty review, source-complete comparison against specialized approximation literature, and application-specific physical constraints. The positive-load workpoint and all30 preselected nonlinear replay outputs have now been independently audited; their qualified conclusions and failed transfer case are retained below. The present evidence supports a precise elementary representation theorem and workload-contract distinction, not a claim that a new robust-control solver beats the same-information classical baseline.

## Positive-load workpoint: independently accepted linear qualification

The separate Kundur workpoint actually adds 50 MW, Q=0, at each selected compute port, re-solves power flow, reinitializes the original nonlinear model and exports a fresh Jacobian/gauge quotient. The new matrix differs from the old one; the older zero-baseline transfer kernel is not reused. Initialized slack generation rises by 113.373224 MW, covering 100 MW added demand and 13.373224 MW additional losses, while the other three generators retain 700 MW active output. This is a genuine changed-workpoint experiment, kept separate from the original-source stress tests.

An initial qualification failure was correctly preserved: the random full-coordinate central-difference test gave relative error 0.0017417. The entire error was at unnamed global coordinate196. This audit independently loaded the saved 197-by-197 descriptor and confirmed that this coordinate has exactly one unit diagonal entry, no other row/column coupling and a zero input row. Its original random-direction value, 0.1525543225868725, equals the complete maximum derivative mismatch. The coordinate is a disconnected numerical sink, not a physical degree of freedom. Restricting the probe to zero in that coordinate is a justified physical-tangent correction; it changes neither model matrices, operating point nor tolerance. The corrected maximum derivative discrepancy is 4.69e-9. Both the original failed result and correction record remain present.

`independent_positive_checks.py` independently verifies the sink diagnosis, fresh modal kernel against the full original positive-workpoint descriptor at four new complex frequencies (maximum relative discrepancy 8.08e-12), and equal-ray full-grid support maxima. It also verifies all seven selected nonlinear input schedules: complete257-block chronology, permitted amplitudes, nonnegative actual compute power, zero incremental energy and exactly100 MWs per port per two-second block. The physically clipped reset example reaches a minimum1 MW per port. This precise energy/work statement relies on the explicitly assumed affine work law; an empirical compute-throughput claim is not supported.

The equal-split LTI numerical amplitude brackets are common [29.079654,29.145285] MW, dynamic optional [27.557388,27.616321] MW, and independent signed [24.301811,24.347631] MW. These are modulation-amplitude budgets around the fixed100 MW compute baseline, not incremental admitted task throughput. The nominal minimum voltage is already0.945044pu (bus8 is0.948743pu). Thus passing the frozen frequency criterion does not establish voltage hosting, general operational safety, line limits or deployability. The positive-workpoint report explicitly retains that limitation. The same-information support baseline remains identical.

The positive report's ambiguous certification wording and external-preregistration implication were repaired following this audit. Its configuration record is a local pre-outcome freeze. All ten preselected full finite nonlinear runs, seven primary and three refinements, have completed and passed the independent raw-data/input-integrity audit. They do not establish family-wide nonlinear safety.

## Nonlinear-transfer gate: material counterexample confirmed by refinement

The original-source nonlinear tests are correctly labeled signed-injection stress replays, with zero probe baselines. Their65-block trimmed words are not claimed equivalent to the full257-block history in a nonlinear plant: the supplied tail bound controls only the LTI difference. This is explicitly recorded in the protocol. All five Kundur cases at both dt=1/64 and1/128 have completed; independent raw-data checks find the committed and dynamic inner/outer selected words straddling the limit as predicted, while the invalid-reset word reaches approximately0.191100 Hz at the fine step.

A material failure occurs for the original WECC dynamic-optional inner case at dt=1/64 and persists at dt=1/128. The preselected amplitude is0.98 times the LTI inner bound, yet the raw nonlinear trace reaches0.05310869707 Hz against the0.05 Hz limit, while its LTI target is approximately0.048831578 Hz. This audit recomputed the raw peak and violation0.00310869707 Hz independently. At dt=1/128 the independently recomputed peak is0.05309955034 Hz, a violation of0.00309955034 Hz. The coarse/fine peak difference is only9.15e-6 Hz. The same frozen input is used. This refinement confirms a finite nonlinear counterexample to blanket transfer of the LTI inner bound. It is not a validated continuous-time enclosure, but the observed violation is far larger than the tested refinement difference. The mathematical sampled LTI theorems remain unaffected by this application failure. All twenty original-source replay outputs and ten refinement pairs have now been independently checked, with frozen source hashes unchanged. The WECC optional-outer fine peak is0.05624951853 Hz. Input, execution and metric audits pass, while the scientific proposition that every refined inner witness stays below the nonlinear threshold is false.


## Final positive-workpoint nonlinear audit and disposition

`independent_positive_checks.py` was rerun against all ten completed535-second raw outputs. It independently recomputed every reported nonlinear peak and physical power minimum, confirmed identical initial-state hashes across all ten runs, and verified that frozen support-source hashes remain unchanged. The selected proper pairs have nonlinear sampled peaks:

- Committed: inner0.049779604 Hz, outer0.051974137 Hz at dt=1/128
- Dynamic optional: inner0.049720880 Hz, outer0.051903535 Hz at refined dt=1/256
- Independent signed: inner0.049173098 Hz, outer0.051285181 Hz at dt=1/128

The selected inner and outer words straddle0.05 Hz in each case. Only the dynamic pair and reset case were preselected for refinement; no unperformed refinement is inferred. Dynamic peak changes are1.86e-5 and1.94e-5 Hz. The physically nonnegative98 MW reset-error example reaches0.182632303/0.182553930 Hz at coarse/fine steps, while its invalid reset screen predicts at most0.042158175 Hz. Its actual compute loads remain between1 and99 MW per port. This confirms that the finite carried-state counterexample does not require negative compute load. The minimum voltage in that stress example is about0.887488pu; even the proper frequency-margin cases reach roughly0.929pu. These results are not full operating-envelope or voltage-hosting approval.

The final auditable disposition is:

1. **Mathematical core accepted:** exact workload quantifiers, finite-exponential-type iff complexity, small-angle static threshold, dynamic nonpolyhedrality, and scoped zero-area realization
2. **Numerical implementation accepted within scope:** independent original formula tests, new-source resolvents, full-grid selected supports, finite witness admissibility, all physical schedules and all30 finite nonlinear output ledgers
3. **Strong generalizations blocked:** new-solver superiority over the same-information support baseline; whole-family nonlinear safety; LTI-to-nonlinear safety transfer across both networks; overall grid hosting; or empirically validated compute throughput/work capacity
4. **Unresolved research gate:** matching specialized prior-art theorem search and publication novelty, which numerical success or a lack of search hits cannot establish

No preselected computation remains pending in this audit. Core audit artifacts are four original independent implementation scripts, their four results files, the separate final-main-report verifier and hash check, this report and `AUDIT_MANIFEST.json`. The report retains the initially failed numerical probe, its justified correction, the original zero-baseline limitation, the timestamp-regeneration caveat and the refined WECC negative result.


## Final assembled main-report check

The final Chinese report was reviewed separately after assembly. All20 table rows were independently checked against raw trajectory NPZ files and audited support summaries, including total amplitude kappa, both per-port amplitudes, LTI and nonlinear peaks, voltage extrema, actual compute-power minima and refinement differences. Displayed four-decimal LTI lower endpoints round down and upper endpoints round up from their stored numerical values; this avoids display-level narrowing but does not add validated floating-point error control. The report explicitly states0<r<1, compact interior J, nearest-integer distance in beta and strictly positive probabilities for every sign-to-sign Markov transition. Its confirmed WECC inner failure, positive baseline voltage limitation, finite-trajectory scope and absence of solver/throughput novelty are visible in the main text. The synthetic shared-parameter circular-domain counterexample was also hand checked.

No remaining blocker in the final assembled claims or numerical tables. Final main-report SHA256: 5751a29cfe2b7027ee113f01d6c8b2cddf4a8826a3e3ba10e0a035e6e5061594. The automated reproduction is `verify_final_report.py`; its recorded result is `FINAL_MAIN_REPORT_CHECK.json`.
