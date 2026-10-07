# Continuous control and recovery tolerance novelty audit

Date: 2026-10-03 UTC. This focused addendum supplements the earlier audits. It explicitly narrows the blanket slot-constant-control warning in `LOSSY_PERMUTATION_BOUNDARY_AUDIT.md` §6.2; the earlier text is retained as part of the evidence history. This is a primary-source search and mathematical overlap assessment, not an exhaustive priority clearance.

## 1 Main conclusion

The checked two-level, rate-constrained extension is valid. For every task order to share one PCC waveform, a symmetric AC-side converter rating R=H−L forces that waveform into [L,H]. In this interval, low and high tasks remain on their respective charge and discharge efficiency branches. The resulting state increments depend exactly on slot means, even when instantaneous PCC power varies arbitrarily inside slots. Exact recovery therefore forces equal slot means, and the sharp all-orders capacity 2Q remains valid. Pointwise-flat PCC power is not forced.

No inspected primary source states the entire resulting battery-specific loss–spread–recovery-tolerance formula. However, its components are close to established mathematics: the signed efficiency map already occurs in battery-privacy work; the zero-tolerance exchange condition is assignment constant-objective-value theory; multiblock endpoint aggregation is scalar Minkowski/support-function reachability. The plausible remaining contribution is a sharp physical specialization with a carefully specified rate and work contract, rather than a new general observability, opacity, assignment, or robust-control method.

The DAG witness adds a useful logical counterexample: failure to hide every permitted order does not imply that a particular order, workload site, or electrical source becomes uniquely identifiable. The explicit two-order class can remain ambiguous forever while completing positive work and recovering physically each block.

## 2 Checked continuous within-slot extension

Take n−1 tasks at constant power L and one at constant power H>L, equal slot duration δ, and all high-task positions admissible. Let p_t(s) be one publicly prescribed measurable PCC waveform, identical across worlds, with 0≤s≤δ. The current task is revealed to the local compensator before its action; it is not revealed to the remote observer. Converter delay, slew, other state variables, hidden dissipation, and efficiency variation remain outside this model.

The AC-side converter action is p_t(s)−d. Requiring |p_t(s)−d|≤R simultaneously for d=L and d=H gives

  p_t(s) ∈ [H−R,L+R].

At R=H−L this becomes [L,H]. This intersection requires both task possibilities at the slot under consideration. A DAG slot that can contain only L does not itself impose the high-world constraint.

Write m_t=δ⁻¹∫p_t(s)ds. With fixed efficiencies and κ=1/ηd−ηc>0, the exact increments are

  low task:  δ ηc(m_t−L),
  high task: δ(m_t−H)/ηd.

There is no Jensen approximation: the integrand stays on one affine branch in each world. A low-task state is nondecreasing throughout the slot and a high-task state nonincreasing. Thus checking slot boundaries is also sufficient for continuous SOC bounds. Arbitrary modulation within the permitted interval cannot create a hidden intra-slot energy overshoot.

For high task at j, subtracting terminal residuals for positions j and k gives δκ(m_j−m_k). Exact common recovery makes every mean equal to q, where

  q = [H+ηcηd(n−1)L]/[1+ηcηd(n−1)].

Set Q=δ(n−1)ηc(q−L)=δ(H−q)/ηd. Placing the high task first or last attains relative energies −Q and +Q. All other prefixes lie between them. Therefore the necessary and sufficient capacity conditions are E0≥Q and C−E0≥Q, with optimum C=2Q at E0=Q. Any admissible equal-mean waveform attains those same boundary increments; monotonicity supplies the continuous-time sufficiency.

The earlier modulation warning still applies outside this restriction. If p crosses L or H, the order-sensitive component depends on the integral of clipped power rather than its ordinary mean, and additional cycling can change common energy loss. For a general multiset with intermediate task powers, staying between the global extrema need not avoid each intermediate efficiency kink. No unrestricted continuous-control flatness theorem is established here.

## 3 Positive tolerance and independent block choices

For block ℓ, let m_ℓt be its slot means within [L,H]. Let r_ℓj be its net internal-energy change when the high task is in slot j. Direct substitution gives

  r_ℓj = δ[ηc Σ_t(m_ℓt−L) − (H−L)/ηd + κ(m_ℓj−L)].

Define a_ℓ=min_j r_ℓj, b_ℓ=max_j r_ℓj, c_ℓ=(a_ℓ+b_ℓ)/2, and w_ℓ=(b_ℓ−a_ℓ)/2. Then

  b_ℓ−a_ℓ = δκ spread(m_ℓ).

If every block choice is independently admissible in the set-theoretic sense, then all combinations of block choices are possible. No probabilistic independence assumption is needed. The exact endpoint hull after K blocks is

  [E0+Σ_ℓ a_ℓ, E0+Σ_ℓ b_ℓ].

Its endpoints are attained by actual histories; its interior need not be filled. For a recovery target E* with tolerance τ, containment of every endpoint is equivalent to

  |E0+Σ_ℓ c_ℓ−E*| + Σ_ℓ w_ℓ ≤ τ.

In particular, the requested width budget is

  δκ Σ_ℓ spread(m_ℓ) ≤ 2τ.

The width budget alone is necessary, not sufficient. The displayed common-mode term makes endpoint containment exact, and prefix-state/rate constraints must still be verified. If recovery is required at every block boundary, the criterion applies separately to every prefix K; states must propagate between blocks without numerical resets.

This is an exact physical tolerance, not approximate observational opacity: the PCC waveforms remain identical. If the observer instead tolerates different PCC traces, that is a second relaxation with different mathematics.

For unlimited operation under the same finite τ and κ>0, the nonnegative series of spreads must be summable. Hence spread(m_ℓ)→0. This statement does not, by itself, force the common block level to converge to q: the cumulative common-mode energy may oscillate inside the band. A positive spread lower bound s in every block would yield Kδκs≤2τ, but a generic optimizer can reduce its spread, so this is not an unconditional finite identification time. For a periodically repeated block, its actual residual extrema give the sharper full endpoint test, including common drift.

For a general task multiset, min/max assignment totals replace the one-high closed form. Summing their ranges over independently admissible blocks uses the same established reachability operation. It is useful computable structure, not a new LP or assignment method.

## 4 Exact antecedents and remaining gaps

### P15 Signed loss and horizon management already occur in privacy control

Avula, Oechtering, and Månsson, *Privacy-preserving smart meter control strategy including energy storage losses* (2018), [primary manuscript](https://arxiv.org/pdf/1803.07864), DOI [10.1109/ISGTEurope.2018.8571537](https://doi.org/10.1109/ISGTEurope.2018.8571537).

Section II-C, Eq. (4), PDF p. 2, uses exactly the signed converter-efficiency map. Section III, Proposition 2, p. 4, gives a Bayesian-risk control recursion. Section IV-B, p. 5, discusses steering end-of-horizon SOC toward a favorable range for the next horizon. Thus lossy battery privacy and continued-use SOC management are established. The paper's stochastic/adaptive privacy criterion and realistic three-circuit model differ from a common deterministic output for every task permutation. The inspected result does not give the rate-induced affine reduction or the stated spread budget.

### P16 Reachable-set aggregation directly subsumes the multiblock step

Girard and Le Guernic, *Efficient Reachability Analysis for Linear Systems using Support Functions* (IFAC 2008), [primary proceedings PDF](https://skoge.folk.ntnu.no/prost/proceedings/ifac2008/data/papers/0569.pdf), DOI [10.3182/20080706-5-KR-1001.0569](https://doi.org/10.3182/20080706-5-KR-1001.0569).

Section 2, Proposition 2, p. 8967, gives support-function addition under Minkowski sums. Section 3.1, Proposition 3/Eq. (6), p. 8968, accumulates input-set supports along linear dynamics. For scalar identity dynamics, support directions +1 and −1 give the sums of endpoint maxima and minima. Time-varying block sets follow by the same recurrence. Convexifying the finite residual sets leaves extrema and containment in an interval unchanged. This is a direct antecedent for the proposed hull and width addition; the battery-specific coefficient and control-contract interpretation require the preceding reduction.

### P17 Robust inventory provides the same cumulative-deviation primitive

Bertsimas and Thiele, *A Robust Optimization Approach to Inventory Theory*, Operations Research 54(1), 150–168 (2006), [author-hosted primary paper](https://web.mit.edu/dbertsim/www/papers/Robust%20Optimization/A%20Robust%20Optimization%20Approach%20to%20Inventory%20Theory.pdf), DOI [10.1287/opre.1050.0238](https://doi.org/10.1287/opre.1050.0238).

Section 3.1, Eqs. (5)–(6), p. 153, uses additive inventory dynamics; Eq. (13) and its discussion on pp. 153–154 describe opposing cumulative worst-case deviations. Section 3.2.2, Eqs. (25)–(26), p. 156, adds robust inventory capacity. Full-box uncertainty gives additive radii. Their objective and uncertainty construction are not the task-permutation privacy problem, but cumulative uncertainty budgets and capacity feasibility are clearly established.

### P18 Approximate opacity uses a different tolerance

Yin and Zamani, *On Approximate Opacity of Cyber-Physical Systems* (2019 preprint), [primary manuscript](https://arxiv.org/pdf/1902.09411).

Definition 3.3, PDF p. 6, relaxes equality of observed output histories by an output metric. Theorem 5.2, p. 11, transfers opacity bounds through approximate simulation relations. These are relevant if measurement precision is relaxed. They do not directly imply the present SOC-target tolerance while PCC observations stay exactly equal. Avoid describing the proposed τ merely as approximate opacity without explaining this distinction.

### Existing P2 still covers the exchange mechanism

Ćustić and Klinz, [primary manuscript](https://arxiv.org/pdf/1405.6096), §1 p. 3, state the linear-assignment sum-matrix characterization immediately after Theorem 1.1. Theorem 1.1 itself concerns TSP, so the assignment statement should not be mislabeled as that theorem. Their Theorem 2.6 also covers d=2 axial assignment. Zero terminal range over all permutations is exactly this classical condition. The two-level coefficient follows by evaluating the familiar piecewise-affine battery map.

## 5 What the DAG witness adds

The inspected six-job example has powers A=B=D=E=F=6 and H=18, one-second slots, efficiencies ηc=ηd=0.95, capacity 18, known initial energy 9, and AC rate 12. The diamond precedence edges are A→B, A→H, B→D, H→D, D→E, E→F. Its only orders place H in slot 2 or 3. Both perform the same positive work and complete six jobs in six seconds.

The common PCC schedule is 6 outside slots 2 and 3 and

  q_pair=(H+ηcηd L)/(1+ηcηd)≈12.30749014

inside them. Its two nonzero battery increments are ±Q_pair with Q_pair≈5.99211564. Each ordering is feasible and recovers exactly. Every concatenation remains feasible, producing 2^K distinct compatible task-power histories after K blocks. This cardinality is a deterministic ambiguity result; a probabilistic entropy or guessing-rate statement would require a prior.

The checked local files are `experiments/DAG_EQUIVALENCE_RESULTS.json` and `theory/LOSS_TOLERANCE_TASK_ORDER_THEOREMS.md` §§10–11. The independent validation files `validation/EXACT_FEASIBLE_K4_CERTIFICATE.json` and `validation/EXACT_DUAL_K5_CERTIFICATE.json` establish the comparison: with the all-six-position class, the same capacity, E0=9, R=12, and recovery band ±0.5, a common schedule exists through four blocks; the exact rational capacity lower bound at five blocks is 4413038513769794080/239362481131915869≈18.43663423>18. This audit inspected those certificates and their declared scope; it does not replace independent verification of their matrix construction.

Consequently, universal all-orders hiding can fail by K=5 while a 2^K subclass remains exactly hidden at every K. Under the diamond contract that subclass is the whole task-power contract. Precedence information can simplify the admissible family enough to permit indefinite hiding, and it can also remove private alternatives entirely in a fully serial chain. Adding a DAG is not uniformly privacy-helpful or identification-helpful without fixing the compared hypotheses.

### P19 The information distinction is classical opacity

Bryans, Koutny, and Ryan, *Modelling Opacity Using Petri Nets*, ENTCS 121, 101–115 (2005), [university-hosted primary paper](https://pure.coventry.ac.uk/ws/files/11728068/1_s2.0_S1571066105000277_main.pdf), DOI [10.1016/j.entcs.2004.10.010](https://doi.org/10.1016/j.entcs.2004.10.010).

Section 3.2, printed pp. 106–109, defines hidden-state properties through existence of alternative executions with the same observation and gives finite-state language-inclusion verification. The introduction, p. 102, distinguishes hiding a specified fact from suppressing every information flow. Thus the universal-versus-residual ambiguity distinction is established; the physical positive-work battery witness illustrates it. Their theorem does not itself cover this continuous SOC model without a justified encoding or abstraction.

## 6 Appropriate claim and stopping boundary

A defensible provisional description is: a sharp two-level battery specialization in which the converter rate makes arbitrary within-slot control exactly reducible to slot means, yielding explicit loss-dependent recovery-tolerance restrictions and persistent precedence-constrained ambiguity witnesses.

Priority for that precise combined statement remains unverified. The work should credit existing battery privacy, assignment separability, scalar reachable-set aggregation, and opacity. Its strongest use is to clarify which work and recovery contracts permit universal hiding and which smaller classes can remain ambiguous, with checked finite-capacity witnesses.

Do not infer an FO localization rate, a general sensor-placement theorem, AI-workload attribution, or sparse-sensor cost superiority. Identical complete labelled PCC histories already defeat any deterministic processing of those histories. Internal site-labelled SOC can add distinguishing information in the specified witness, but that is a changed measurement channel and requires its own cost, timing, model-error, and practicality comparison.

Search coverage for this update included lossy battery privacy, terminal SOC management, assignment COVP, robust inventory, support-function reachability, approximate opacity, and task/partial-order privacy. No direct complete antecedent was found; absence from this bounded inspection is not evidence of universal absence.

## 7 Further qualification for unlimited operation without recovery checkpoints

Added after the preceding audit, following inspection of the independent theory proof in `theory/LOSS_TOLERANCE_TASK_ORDER_THEOREMS.md` §12. The newly established no-checkpoint bound strengthens the remaining candidate result: exact per-block recovery is no longer needed for the infinite-horizon minimum capacity. The old warning about a finite-horizon exact-equality singularity should not be read as defeating this stronger claim.

Under the same one-high contract, strictly nonunit round-trip efficiency, common prescribed PCC means in [L,H], all block-order combinations admissible indefinitely, and finite capacity B, define

  W∞ = δκ Σ_ℓ spread(m_ℓ).

The checked statement is

  B ≥ 2Q + W∞.

It is a necessary condition for one infinite universally feasible schedule. In particular, minimizing capacity over common initial state and schedule gives exactly 2Q; the constant q schedule at E0=Q attains it and satisfies every recovery tolerance, including zero. At B=2Q, every block must have equal slot means. This condition does not force a pointwise-flat continuous PCC waveform. The inequality alone is not a sufficient test for an arbitrary nonflat schedule, since early prefix placement and common-mode drift can still violate capacity.

### Why the additional 2Q is a substantive step

Scalar support-function accumulation immediately gives W_K≤B, hence W∞≤B and summable spreads. That conclusion alone leaves out the within-block capacity which continuing complete tasks require.

Let μ_ℓ be a block's average of its slot means. Averaging the residual over all n possible high-task positions gives exactly

  r(μ_ℓ)=δ[(n−1)ηc(μ_ℓ−L)−(H−μ_ℓ)/ηd].

This uniform averaging is an algebraic proof device, not an assumption about the actual private scheduler. All histories are feasible, so their averaged endpoint stays bounded. Thus the sum of these residuals stays bounded. Since r is affine with its unique root q, the Cesàro average of μ_ℓ tends to q.

For a flat block at level x, the range over all orders and all prefixes is

  V(x)=δ[(n−1)ηc(x−L)+(H−x)/ηd].

This is affine, and V(q)=2Q. Replacing a nearly flat block by its mean perturbs every prefix by at most nδ spread(m_ℓ)/ηd. Consequently its actual within-block range V_ℓ differs from V(μ_ℓ) by a quantity tending to zero. The preceding endpoint uncertainty has width W_{ℓ−1}; independence of admissible past and current orders gives B≥W_{ℓ−1}+V_ℓ. Cesàro averaging proves B≥W∞+2Q.

This adds a specific unavoidable task-cycle excursion to permanently accumulated order-dependent endpoint uncertainty. Support-function addition supplies the first ingredient, while bounded balance and the affine two-level span supply the additional sharp constant. No inspected primary source directly states the combined bound.

### Additional targeted primary comparisons

**P20 Arrieta 2020 thesis.** [University-hosted thesis](https://etheses.whiterose.ac.uk/id/eprint/26256/1/marrieta_phd_thesis.pdf), *Universal Privacy Gurantees for Smart Meters* (title spelling as deposited). Section 3.1, Eq. (3.2), printed p. 52, uses ideal additive storage; its feasible-policy family is defined immediately thereafter. Chapter 5 develops shared-output geometry. Section 6.2, printed p. 120, identifies more complex battery models and further consumption constraints as future directions. This strengthens attribution for the ideal antecedent P1 but does not supply a lossy infinite-horizon 2Q+W∞ theorem. The thesis's review chapter is not used as proof of another author's theorem.

**P21 Sun, Lampe, and Wong 2017/2018.** *Smart Meter Privacy: Exploiting the Potential of Household Energy Storage Units*, [author-hosted primary paper](https://people.ece.ubc.ca/vincentw/J/SLW-IoT-2017.pdf), DOI [10.1109/JIOT.2017.2771370](https://doi.org/10.1109/JIOT.2017.2771370). Section II-B, Eqs. (4)–(10), includes SOC/rate constraints, an efficiency factor, and required EV departure SOC. Sections III-C and IV formulate expected load-flatness/cost optimization and a deterministic benchmark. These are relevant application antecedents, but the displayed battery update is not the same two-slope signed map, and the inspected results do not optimize one output over all repeated task orders or state the proposed asymptotic bound.

**P22 Zou, Lin, Aliprantis, and Chen 2018.** *Robust Multi-stage Power Grid Operations with Energy Storage*, [author-hosted primary paper](https://www.mhchen.com/papers/robust.grid.operation.with.storage.INFOCOM.18.pdf). Section III-C, PDF p. 7, explicitly shows linear-in-horizon storage growth for a class of affine policies under persistent demand uncertainty without curtailment. Theorem 7 and the same discussion provide horizon-independent capacity conditions, exact in a stated infinite-horizon special case. The end of §III-B discusses efficiency-loss extensions. Their dispatch adapts to demand, the uncertainty family is amplitude/ramp constrained, and privacy/common-output hiding is not required. Thus persistent-uncertainty capacity growth and infinite-horizon sharp storage bounds are established themes; this paper does not directly anticipate the one-high-block 2Q+W∞ formula.

The [P22 technical report](https://staff.ie.cuhk.edu.hk/~xjlin/paper/infocom18-robust-storage-tech.pdf), §III-D, PDF pp. 7–8, Eqs. (31)–(34), explicitly supplies the charging/discharging-loss extension. It notes that the modified conditions are sufficient but no longer necessary. This remains a neighboring robustness result rather than the proposed common-output permutation converse.

### Revised novelty assessment and interpretation

The no-checkpoint result is a stronger, more credible narrowed contribution than the exact-reset rigidity statement alone. It removes one particularly restrictive modeling obligation while preserving a closed-form sharp minimum in the specified universal task-order problem. Its proof is still a short combination of classical tools, and the broader robust-storage literature materially limits novelty language. A suitable provisional claim is a sharp infinite-horizon capacity specialization with an explicit additional capacity requirement for accumulated order-dependent SOC spread. Do not claim priority without further specialist review.

At fixed positive recovery tolerance, the all-orders infinite-horizon optimum remains 2Q. Thus the ideal-versus-strictly-lossy limit can remain singular even when exact reset is relaxed. Finite horizons can still behave continuously as loss vanishes; the order of limits matters. The result does not imply that all finite-horizon reoptimizations constitute one feasible infinite schedule.

The scope still excludes state contraction from self-discharge, degradation or finite cycle life, controllable dissipation, unrestricted out-of-range intra-slot modulation, and restrictions coupling order choices between blocks. Each changes an essential proof step. The DAG's forever-hidden pair remains valid, so neither this asymptotic capacity exclusion nor a finite all-orders infeasibility certificate supplies a universal source-identification horizon.

Final scope check: attainability proves sharpness of the minimum 2Q. It does not establish attainability of equality B=2Q+W∞ for every prescribed positive W∞. No such stronger tradeoff claim is made.
