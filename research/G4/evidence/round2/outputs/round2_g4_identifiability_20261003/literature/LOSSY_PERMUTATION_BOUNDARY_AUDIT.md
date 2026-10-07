# Narrowed lossy task-permutation boundary: novelty and scope audit

Date: 2026-10-03 UTC. This addendum evaluates the proposed theorem; it does not claim publication priority. It uses the source labels and verified source descriptions in `PRIMARY_NOVELTY_AUDIT.md`.

## 1. Bottom line

The proposed rigidity statement has a credible, short proof. Its exact battery consequence was not found in the inspected literature. The central “all permutations have the same sum iff all swap differences vanish” argument is the established assignment constant-objective-value property, not new combinatorics. The result could support a useful sharply limited physical boundary note, especially with a robust continuation theorem. It does not by itself establish a new sparse-source-localization method or an advantage over equally informed PCC measurements.

## 2. Exact claim and assumptions

Use n≥2 equal-duration slots, normalized to duration one. Public demand multiset d=(d_1,…,d_n) has a=min d_j < b=max d_j. Every permutation is admissible, and the order is private. One common initial battery energy e_0 is fixed independently of that order. Capacity C is usable internal energy after subtracting any backup reserve.

A single real-valued public grid-power vector p=(p_1,…,p_n), fixed independently of the private order, must be feasible for every permutation. Grid power and demand are physically constant inside each slot. There is no simultaneous charging/discharging, load shedding, hidden generation, intentional waste, or state reset. Charge/discharge efficiencies are constants satisfying 0<ηc≤1, 0<ηd≤1, ηcηd<1. No state-dependent efficiency, self-discharge, degradation, or other storage state is included.

Define the internal-energy increment function

φ(z)=ηc z for z≥0; φ(z)=z/ηd for z<0.

For permutation π,

e_t^π=e_{t−1}^π+φ(p_t−d_{π(t)}), t=1,…,n.

Require 0≤e_t^π≤C at every boundary and e_n^π=e_0 for every π. Power/ramp limits, if imposed, must also hold and can only further restrict this class.

## 3. Proof map and exact prior-art overlap

The terminal condition is Σ_t A_{t,π(t)}=0 for every π, where A_tj=φ(p_t−d_j). Thus A has the linear-assignment constant-objective-value property. P2's sum-matrix characterization applies directly. Independently, comparing two permutations that only swap tasks i,j between slots r,s gives

A_ri+A_sj=A_rj+A_si.

Choose the minimum and maximum tasks a,b. Then F(p_r)=F(p_s), where

F(p)=φ(p−a)−φ(p−b).

Its pieces are

- p≤a: F(p)=(b−a)/ηd
- a<p<b: F(p)=b/ηd−ηc a+(ηc−1/ηd)p
- p≥b: F(p)=ηc(b−a)

Since ηc−1/ηd<0, F is strictly decreasing inside (a,b), with different outer plateau values. Equal F values force either all p_t≤a, all p_t≥b, or every p_t equal to the same q∈(a,b). The first class has strictly negative total battery increment because at least one task exceeds a; the second has strictly positive total increment because at least one task is below b. Neither can reset. Consequently p_t=q for all t.

The unique q solves

ηc Σ_j(q−d_j)^+ = (1/ηd) Σ_j(d_j−q)^+.

The left-minus-right expression is continuous and strictly increasing, negative at a and positive at b, so the root exists uniquely inside the task range. This is the battery-specific scalar consequence of the established exchange constraint. Do not attribute the physical conclusion itself to P2; that paper does not state it.

## 4. Sharp capacity once the output is forced flat

Let v_j=φ(q−d_j) and Q=Σ_j v_j^+=−Σ_j v_j^−. Every permutation has total zero. The partial sum of any permutation is between −Q and Q. Both extremes are attainable: schedule all negative increments first to reach −Q, or all positive increments first to reach Q.

One common e_0 must therefore satisfy e_0≥Q and C−e_0≥Q. Necessarily C≥2Q. Taking e_0=Q makes every prefix feasible, so C*=2Q is exact within the stated model. Every block then returns physically to Q; arbitrary block-order sequences can continue without artificial resets.

This capacity argument is elementary robust partial-sum geometry. The nontrivial interpretation is that losses plus universal exact reset remove the nonflat output choices available in the ideal case. If e_0 were secretly chosen separately for each complete order, or if the controller knew the future order and selected a different observable p, the statement would be a different problem.

Rate checks do not follow from the capacity proof. For a flat q, the minimum charge/discharge ratings must cover max_j(q−d_j)^+ and max_j(d_j−q)^+. A battery-power ramp limit must accommodate the largest allowed adjacent job-power jump. If all permutations are admissible and slots have instantaneous boundaries, a continuous-time finite-ramp requirement needs a separate transition model.

## 5. Singular ideal-efficiency limit

At ηc=ηd=1, φ is linear, every assignment matrix A_tj=p_t−d_j is automatically a sum matrix, and exact reset requires only Σp_t=Σd_j. Nonflat common schedules can therefore exploit the ideal prefix envelope from the main audit.

For one high-demand slot D>0 and n−1 zero-demand slots:

- ideal envelope capacity: C0=D
- for symmetric efficiency ηc=ηd=η<1, the forced flat grid draw is q=D/[1+(n−1)η²]
- Q=(n−1)ηq, hence Cη=2(n−1)ηD/[1+(n−1)η²]
- as η approaches 1 from below, Cη approaches 2(n−1)D/n

For n=3 this limit is 4D/3; as n grows, the ratio to C0 approaches 2. With D=2 and n=3, ideal capacity is 2 while the lossy-side limit is 8/3. This is a discontinuity in the exact all-order feasibility problem at the ideal model, not a claim that real battery size varies discontinuously under an engineering tolerance.

The gap should be described with internal-energy units held consistent. For some small contracts and efficiency parameters Cη can be less than a corresponding ideal internal capacity even while grid energy increases; do not claim monotonic capacity growth with loss without proving it.

## 6. Four restrictions that determine whether this is a meaningful physical result

### 6.1 Exact reset is a strong equality contract

For a nonflat public p, reset discrepancies tend continuously to zero as efficiencies tend to one. Allowing a fixed nonzero terminal tolerance can restore schedules excluded by the exact theorem. Over repeated arbitrary orders, those small discrepancies may accumulate; a finite battery cannot support persistent one-sided drift. A rigorous many-block bound would be more practically meaningful than emphasizing a formal singularity alone.

A useful next result would relate efficiency deficit, within-block waveform nonflatness, allowed terminal error, number of blocks, and remaining capacity. It should compare minimum and maximum assignment totals rather than only checking equality. That is a standard assignment optimization primitive, so novelty must lie in the sharp resulting physical bound or its information consequence.

### 6.2 Slot-constant power is essential

If p_t(τ) can vary within a slot, the terminal increment becomes A_tj=∫φ(p_t(τ)−d_j)dτ. Distinct waveforms having the same within-slot amplitude distribution produce equal rows of A and satisfy the order-invariance constraint. A nonconstant periodic public waveform can therefore replace the flat scalar output while preserving permutation-independent terminal increments.

Moreover, sequential intra-slot charging and discharging can create controllable dissipation without simultaneous charge/discharge. Thus “no simultaneous charge/discharge” by itself does not justify applying φ to an averaged p−d. A theorem about slot-averaged measurements is not automatically a theorem about physical slot-constant control. This is the strongest scope caveat found in this audit.

### 6.3 Complete permutation freedom may not model real jobs

Real tasks can have precedence, arrival, deadline, minimum dwell-time, or coupled-device constraints. Then not every 2×2 swap is realizable; the full sum-matrix condition may no longer be necessary. Conversely, an explicitly public fixed multiset can be much stronger information than realistic task telemetry. Both are legitimate mathematical contracts, but their relevance must be established rather than presumed.

### 6.4 The hidden target is order, not automatically a nonzero FO source

A perfectly flat PCC has no forced component from these tasks at that port. It demonstrates nonidentification of upstream work order. Calling it an unidentified persistent nonzero electrical oscillation source would change the target incorrectly. For location, construct different site-labelled internal task worlds with the same electrical data and show that the chosen label is physically meaningful in both worlds.

## 7. Novelty grade and recommended next step

- **Generic hidden-source/abstention framework:** established
- **Ideal common-output permutation capacity:** direct specialization of P1
- **All-permutation exchange / additive separability:** established P2
- **Lossy exact-reset forcing a flat slot-constant PCC:** exact application statement not located; plausible narrow new corollary
- **Singular exact-feasibility capacity gap:** exact statement not located; potentially useful consequence, with severe tolerance/control-class caveats
- **Sparse sensor advantage or realistic UPS applicability:** not established by these propositions

Recommended scope is a rigorously bounded theorem note, not a method paper claim. Before expanding experiments, either derive a sharp robust continuation result or show that a real documented control/telemetry contract makes the exact restriction operationally relevant. If those checks fail, retain the result as an instructive boundary/counterexample with full antecedent attribution.


## 8 Explicit update on 2026 10 03

The warning in section 6.2 was written for unrestricted intra-slot modulation. A checked two-level rate-constrained extension now removes the need for physically slot-constant PCC power in that specific model. For task powers L or H, all positions possible, and symmetric AC converter rate R=H-L, common feasibility forces p(t) into [L,H]. SOC increments then depend exactly on slot means, with monotone within-slot energy paths. Exact recovery forces equal slot means, not pointwise-flat power, and the sharp capacity 2Q remains valid. The earlier warning remains applicable outside this rate/two-level restriction.

See `CONTINUOUS_TOLERANCE_DAG_ADDENDUM.md` for this explicit scope correction, the positive-tolerance formula, the persistent DAG ambiguity comparison, and five additional primary sources. The multiblock endpoint-hull argument is directly subsumed by classical support-function reachability; novelty, if any, is the battery-specific physical specialization. The original sections above have been preserved byte for byte.

A further qualification is recorded in section 7 of the same addendum: for the rate-constrained one-high class over one infinite universally feasible schedule, finite capacity alone implies B >= 2Q + W_infinity, where W_infinity is the accumulated order-dependent endpoint width. No recovery checkpoint is needed. Therefore the long-run minimum 2Q is not merely an artifact of exact terminal equality. This stronger application theorem was not located in the inspected primary sources; its generic reachability and bounded-drift ingredients remain classical.
