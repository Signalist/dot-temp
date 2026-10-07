# G4 bounded-storage identifiability: primary-source novelty audit

Audit date: 2026-10-03 UTC. Scope: bounded-energy battery/UPS hiding, exact recovery, continuing known work contracts, sparse electrical observations, and set-valued source identification. This is an adversarial novelty audit, not a claim that every application-specific statement has already appeared. All substantive literature claims below use original papers, author/institutional manuscripts, or publisher records. Search-index dates were not used as publication dates.

## Executive verdict

1. **The broad framework is not new.** Unknown-input indistinguishability, model-set intersection, constrained finite-horizon diagnosis, delay guarantees, and returning candidate sets already have explicit theorems.
2. **There is a remarkably direct battery antecedent.** Arrieta–Esnaola–Effros (2019), Definition 5 and Lemma 1, characterizes exactly when an arbitrary family of demand/initial-state pairs admits a common feasible grid-output sequence, using a cumulative-energy distance. This is stronger and closer than a generic storage-sizing citation.
3. **The ideal permutation-capacity theorem is a specialization.** The proposed maximum prefix-envelope width is obtained by evaluating that cumulative distance on all permutations of a fixed multiset. Public-contract causality and exact reset are useful corollaries; neither turns the underlying capacity criterion into a new observability principle.
4. **The lossy exact-reset rigidity boundary is the best remaining narrow candidate.** I found its combinatorial engine exactly in the classical constant-objective-value property of assignment matrices. I did not find the specific battery consequence, or its singular ideal-efficiency limit, in the primary sources inspected. It may be a useful application-specific proposition, not yet a high-novelty research core.
5. **The original failed initial-energy mechanism remains failed.** Changing the demand order or controller class changes the hypothesis. Permanent hiding by cyclic recharge does not validate permanent source-class separation caused only by hidden initial energy under the old fixed controller.
6. **Sparse-source novelty must face very recent work.** Kai Sun's September 30, 2026 preprint explicitly treats source equivalence classes, exact harmonic identifiability, bounded-error separation, and a set-valued fallback. It excludes nonlinear storage dynamics and finite transients, so the storage-specific question is distinct, but the broad identifiability/abstention language is occupied.

## 1. Primary-source ledger and precise overlap

### P1. Arrieta, Esnaola, Effros (2019): the decisive battery theorem

**Source:** [Universal Mutual Information Privacy Guarantees for Smart Meters](https://arxiv.org/pdf/1905.00111), arXiv:1905.00111v1, §II–III; related conference title *Universal Privacy Guarantees for Smart Meters*, ISIT 2019.

Definition 5 defines distance between two initial-state/demand pairs by the maximum absolute difference of their initial-energy-adjusted cumulative demands. Lemma 1 says that every pair in a set having distance at most battery capacity is equivalent to the entire set sharing one feasible requested-energy sequence. Its proof constructs that output with a cumulative envelope. Theorems 1–2 build covering and distinguishable-sequence bounds; the policy discussion identifies limited lookahead requirements. Model: ideal finite-capacity storage, discrete demand/output alphabets, with output-alphabet qualifications handled separately.

**Overlap:** common-output witnesses, worst-case family guarantees, hidden initial SoC, cumulative drift, demand-family diameter, and exact algebraic impossibility are directly present. **Gap:** not a theorem about lossy exact-reset order contracts, network source labels, or realistic UPS firmware.

**Audit conclusion:** mandatory lead citation. A rank/LP wrapper around this geometry is not a new result. The original text is more exact than a claim that battery-privacy work is only stochastic: its central feasible-set lemma is deterministic.

### P2. Ćustić and Klinz (2014/2016): permutation invariance is assignment COVP

**Source:** [The constant objective value property for combinatorial optimization problems](https://arxiv.org/pdf/1405.6096), arXiv:1405.6096v2, §1, pp. 2–3. Published related article: [The constant objective value property for multidimensional assignment problems](https://doi.org/10.1016/j.disopt.2016.01.004), *Discrete Optimization* 19 (2016), 23–35.

The paper records that a linear-assignment cost matrix has equal total cost under every permutation exactly when it is a sum matrix, C_ij=u_i+v_j. It notes earlier admissible-transformation antecedents and gives the LP-duality interpretation. All 2×2 exchange differences then vanish. The paper's own principal extension is multidimensional assignment.

**Overlap:** if slot/task cost is C_tj=φ(p_t−d_j), terminal-energy independence of task order is precisely this property. The exchange step is therefore established mathematics. **Gap:** this source does not discuss batteries, charge/discharge loss, forced-flat grid profiles, or a discontinuity at unit efficiency.

**Audit conclusion:** cite the assignment property openly. The potentially new part must be the physical consequence under a sharply stated contract, not the exchange proof or the word “nonlinear.”

### P3. Harirchi, Yong, Ozay (2017): constrained finite-time isolation with candidate lists

**Source:** [Guaranteed Fault Detection and Isolation for Switched Affine Models](https://arxiv.org/pdf/1704.05947), arXiv:1704.05947v2 / CDC 2017. [Author PDF](https://web.eecs.umich.edu/~necmiye/pubs/HarirchiYO_cdc17.pdf).

Definition 3 specifies finite-length behaviors with compact state/input/noise sets. Definition 4 calls two models T-distinguishable when those behavior sets are disjoint. Proposition 1 and Theorem 1 supply model-invalidation and pairwise distinguishability feasibility tests. Proposition 2 gives I-isolability of multiple faults; Proposition 3 and Theorem 2 bound delays. Remark 2 explicitly permits returning all compatible faults when separation assumptions fail, or the empty set when no model matches.

**Overlap:** battery states can be constrained states; source locations can index fault models; saturation can be switched affine; unknown-but-bounded noise is already included. Feasibility filtering, a bank of candidate models, abstention, and finite detection/isolation horizons are direct applications. **Gap:** no specialized closed-form task/storage geometry or claimed physical sensor-cost advantage.

**Audit conclusion:** the strongest generic counterexample to claiming “LP + honest uncertainty + finite identification” as a method contribution.

### P4. Pasqualetti, Dörfler, Bullo (2012/2013): indistinguishable input pairs and invariant zeros

**Source:** [Attack Detection and Identification in Cyber-Physical Systems—Part I: Models and Fundamental Limitations](https://arxiv.org/pdf/1202.6144), 2012 preprint. Journal consolidation: [Attack Detection and Identification in Cyber-Physical Systems](https://doi.org/10.1109/TAC.2013.2266831), *IEEE TAC* 58(11), 2715–2729 (2013).

In the inspected Part I version, Theorem 4.5 equates dynamic undetectability to zero-output trajectories and invariant-zero conditions. Theorem 4.6 compares two candidate attack supports through a combined zero-output system and states the associated 2k-support relation. Theorem 4.7 explains why an additive known probing signal does not remove worst-case linear indistinguishability. Numbering is version-specific.

**Overlap:** pairwise world subtraction, source-support ambiguity, hidden initial state, and rank/zero tests. **Gap:** an unconstrained zero trajectory need not respect finite battery energy, power, or recovery requirements. State constraints can exclude a zero-dynamics witness; ordinary rank tests alone cannot settle that constrained question.

**Audit conclusion:** bounded-storage viability can sharpen this framework, but the information-boundary methodology itself is classical.

### P5. Hautus (1983): distinguish observability, input inversion, and asymptotic state estimation

**Source:** [Strong detectability and observers](https://doi.org/10.1016/0024-3795(83)90061-7), *Linear Algebra and its Applications* 50, 353–368.

The paper develops strong observability/detectability for continuous-time systems with only partial input information and algebraic conditions for observers. Its abstract and publisher record were inspected; this audit does not assign an unverified theorem number.

**Overlap:** unknown inputs and unmeasured states are established observer questions. **Gap:** identifying a discrete source class is weaker than reconstructing the full internal state; exact finite-time uniqueness is different from asymptotic estimation. A hidden SoC coordinate can remain unobservable while all source labels of interest are known.

**Audit conclusion:** avoid equating “some internal state hidden” with “source label impossible,” or claiming an unknown-input observer as new.

### P6. Anguluri, Kosut, Sankar (2022/2023): forced inputs with unknown initial states

**Source:** [Localization and Estimation of Unknown Forced Inputs: A Group LASSO Approach](https://arxiv.org/html/2201.07907v1), arXiv:2201.07907. [Journal DOI](https://doi.org/10.1109/TCNS.2023.3258627).

The model expands measurements into an initial-state term plus time-grouped forcing inputs. Theorem 4 supplies probabilistic location-recovery consistency under stated assumptions; Theorem 6 gives estimation bounds; Theorem 7 relates sufficient incoherence conditions to frequency-domain quantities. Input-output delay and invariant-zero issues are treated explicitly, with power-system validation.

**Overlap:** sparse unknown source localization with unknown network initial state is already direct FO prior art. **Gap:** its unknown exogenous forcing is not the same object as an endogenous constrained-storage port response under a continuing job contract; its probabilistic support conditions are not deterministic universal battery-hiding conditions.

**Audit conclusion:** a fair baseline and framing citation, not a theorem that automatically resolves every hybrid storage case.

### P7. Sun (2026): current harmonic-source information limits and fallback sets

**Source:** [Identifiability Limits of Forced Oscillation Sources in Power Systems](https://arxiv.org/html/2610.00356v1), arXiv:2610.00356v1, September 30, 2026. Preprint status; no peer-review claim.

Theorem 1 gives exact single-frequency identifiability from nonzero, pairwise noncollinear complex signatures. Proposition 2 states the descriptor rank version. Equation 20 and Algorithm 1 permit a thresholded candidate set instead of a point answer when margin/validity checks fail. Proposition 4 states that deterministic feature extraction cannot remove overlap already present in raw candidate measurement sets. Section II-C limits the result to a single steady sinusoidal source and explicitly excludes finite transients, nonlinear/hybrid responses, drifting frequency, and simultaneous sources.

**Overlap:** source equivalence, hierarchical source labels, raw-data impossibility, conditioning, measurement augmentation, and abstention. **Gap:** constrained cyclic storage and job-order hiding are outside its model.

**Audit conclusion:** this very recent source must be in the final paper's novelty table, with its scope respected.

### P8. Li, Khisti, Mahajan (2015/2018): optimal finite-battery privacy is not exact identification

**Source:** [Information-Theoretic Privacy for Smart Metering Systems with a Rechargeable Battery](https://arxiv.org/html/1510.07170), arXiv:1510.07170; IEEE TIT publication.

Theorems 1–2 formulate finite/infinite-horizon dynamic programs for ideal charge-conserving storage; Theorem 3 characterizes optimal infinite-horizon mutual-information leakage for i.i.d. demands using a single-letter expression and an invariant policy.

**Overlap:** causal finite-battery load hiding over an ongoing process; statistical information limits and optimal policies. **Gap:** a small or positive average leakage rate does not by itself imply exact identification of every deterministic source, and finite-capacity limitations over unrestricted random demand do not rule out perfect hiding of a restricted periodic contract family.

**Audit conclusion:** do not claim a contradiction with information theory when cyclic contract-conditioned ambiguity lasts forever. Different quantifiers and secret variables matter.

### P9. Arrieta and Esnaola (2017): universal finite-battery privacy and permuting channels

**Source:** [Smart Meter Privacy via the Trapdoor Channel](https://arxiv.org/pdf/1708.04429), SmartGridComm 2017, [DOI](https://doi.org/10.1109/SmartGridComm.2017.8340722).

The paper constructs finite-battery policies with leakage guarantees for general bounded random processes. Theorems 1–2 give capacity-dependent upper/lower guarantees; Theorems 3–4 add average-consumption information. It explicitly relates battery behavior to nonprobabilistic permuting channels while noting that energy outputs need not be literal permutations of input symbols.

**Overlap:** distribution-independent guarantees, finite memory/storage, sequence reordering, and average-energy constraints. **Gap:** not the specific lossy permutation-reset rigidity theorem.

**Audit conclusion:** “universal” and “permutation-based” are not by themselves distinguishing claims.

### P10. Backes and Meiser (2013): recovery leakage already matters

**Source:** [Differentially Private Smart Metering with Battery Recharging](https://eprint.iacr.org/2012/183.pdf), extended manuscript associated with DPM/SETOP 2013, [DOI](https://doi.org/10.1007/978-3-642-54568-9_13).

Section 5 studies information exposed by restoring battery charge; Theorem 2 gives approximate differential-privacy guarantees for possibly infinite streams with capacity/throughput bounds and a specified secondary energy resource. The recovery mechanism is part of the privacy accounting, not silently omitted.

**Overlap:** continuous operation, recharging, and hidden-energy restoration are old privacy concerns. **Gap:** approximate DP under neighboring streams and extra resource assumptions is not exact output equality across all job permutations with loss-only storage and exact block resets.

**Audit conclusion:** cite as an antecedent for the importance of recharge information, while explicitly contrasting the physical-resource and privacy contracts.

### P11. Bovornkeeratiroj et al. (2020): demand-order concealment is already an application

**Source:** [RepEL: A Utility-preserving Privacy System for IoT-based Energy Meters](https://lass.cs.umass.edu/papers/pdf/iotdi20-repel.pdf), IoTDI 2020.

RepEL uses battery discharge to mask actual foreground loads and later charging to replay their patterns in randomized order. It aims to preserve appliance-usage utility while obscuring timing/occupancy, and evaluates a gateway implementation with household traces.

**Overlap:** batteries hide actual load timing while preserving an underlying set of energy-use events. **Gap:** the paper does not establish the proposed exact minimum capacity for a universal fixed-output, all-permutation, exact-reset contract.

**Audit conclusion:** prevents presenting “job order can be hidden using a battery” as the new conceptual discovery. The new candidate must be its exact extremal boundary.

### P12. Le Boudec and Tomozei (2012): causal cumulative-envelope feasibility

**Source:** [A Demand-Response Calculus with Perfect Batteries](https://infoscience.epfl.ch/bitstreams/e96b189e-7314-4494-8a71-77bd1970ec51/download), [DOI](https://doi.org/10.1007/978-3-642-28540-0_23), MMB/DFT 2012, 273–287.

The original abstract and indexed original text state necessary/sufficient feasibility conditions for nonelastic load, imposed supply limits, capacity, and initial charge. They also establish that a feasible causal schedule exists whenever a feasible schedule exists, and give an envelope/service-curve battery-size guarantee. Direct PDF fetch was rate-limited; no theorem number is asserted here.

**Overlap:** cumulative corridors, service contracts, causal storage scheduling, and worst-case feasibility are established. **Gap:** satisfying demand under supply control is different from making one output identical across a secret demand family.

**Audit conclusion:** a corridor implementation is not itself new. Whether a strengthened privacy constraint changes the sharp envelope characterization must be proved.

### P13. Zhang, Kumar, Xie (2025): cumulative excursion already sizes storage

**Source:** [An Average Power-Based Planning Framework of Transmission Expansion: A New Role for Energy Storage](https://doi.org/10.1109/OAJPE.2025.3548911), IEEE OAJPE 12 (2025), 122 onward.

Theorem 1 expresses minimum storage capacity as maximum minus minimum cumulative net-energy mismatch; Equation 14 is the telescoped storage balance. This was verified in indexed publisher full-text excerpts.

**Overlap:** the scalar cumulative-range formula and peak-versus-energy interpretation. **Gap:** not a privacy or source-identification theorem.

**Audit conclusion:** the elementary storage primitive should be treated as background, even if it is usefully combined with source ambiguity.

### P14. John and Katewa (2022): opacity versus attack detection

**Source:** [Opacity and its Trade-offs with Security in Linear Systems](https://cps.iisc.ac.in/faculty/vaibhav/Papers/2022CDCOpacitySecurityTradeoff.pdf), CDC 2022.

The paper characterizes linear-system opacity through the weakly unobservable subspace and connects expanded opaque sets to undetectable attacks under specified conditions.

**Overlap:** private internal trajectories and failure of external identification are two views of output-equivalent behavior. **Gap:** constrained lossy cyclic storage is not directly its unconstrained linear setting.

**Audit conclusion:** reinforces that privacy/identifiability duality is an established perspective, rather than the contribution.

## 2. What the proposed information boundary actually means

This section is our own mathematical audit, not an attribution of these exact statements to a source.

Use ideal storage e_{t+1}=e_t+p_t−d_t, 0≤e_t≤C. Full grid-power observation gives p. Define cumulative demand D_k=Σ_{t<k}d_t, cumulative grid energy Z_k=Σ_{t<k}p_t. Then e_k=e_0+Z_k−D_k.

### 2.1 Two demand hypotheses, one common observed output

For known common initial energy e_0, two hypotheses have identical p only if their cumulative demand difference obeys |D_k^a−D_k^b|≤C at every k. Different unknown initial energies instead give an offset: Δe_k=Δe_0−(D_k^a−D_k^b), with Δe_k∈[−C,C]. The scalar unrestricted-rate pair condition is a bounded-range condition on cumulative difference, including k=0; the exact admissible initial offset must be included. Do not silently replace common known e_0 with separately optimized e_0 for each world.

A sustained nonzero cumulative drift eventually exceeds any finite corridor. If ΔD_k grows at least δk−b with δ>0, a finite-time exclusion bound follows immediately from the appropriate initial-state/capacity budget. This is a conservation corollary, not automatically a new finite-identification theorem.

Conversely, a nonzero periodic difference with zero net sum per period has a bounded primitive. With enough capacity and admissible power rates, repeating a common output can preserve ambiguity forever. Finite capacity limits excursion, not lifetime throughput. However, “zero mean” alone is insufficient: a sequence can have zero asymptotic mean and an unbounded primitive (for example long alternating blocks whose partial sums grow). Use periodic zero-sum or explicitly bounded cumulative discrepancy.

### 2.2 Exact state recovery does not reveal order

If both hypotheses have the same total demand over a block and both return to the same initial energy, their common output only has to share that total energy. Equal endpoints do not determine the within-block demand. A block with a valid common-output schedule can be concatenated indefinitely without any artificial state reset: the physical state returns by its dynamics.

This is a different proposition from the old G4 experiment. There the input and controller were the same and only initial energy changed. Here demand trajectories differ within a public contract. A result in this new hypothesis family cannot be represented as a repair of the old claim about persistent initial-state-specific FO.

### 2.3 Sparse network measurements can erase the very drift being counted

If y_t=H p_t, cumulative demand drift is useful only through measured or otherwise justified combinations. A drift vector in an unobserved network direction is not revealed merely because its norm grows. If y is only an AC phasor or high-pass feature, DC cumulative energy may have been discarded entirely. Any finite-time theorem must specify whether the observer receives full time samples, low-pass energy, absolute power, phasors, or both.

With dynamic network observations, account for transient network initial states and measurement filtering. A static H model is not a universal statement about a dynamical grid. Adding bounded storage gives a constrained viability problem within the established unknown-input framework; it does not authorize ignoring its transfer structure.

### 2.4 “Finite identification” requires all rivals to be excluded

For a finite set of source labels, a singleton candidate set is justified only once every competing label is infeasible. A single pairwise drift bound does not establish uniform identification over an unbounded or continuously parameterized alternative family. Arbitrarily small drift differences can imply arbitrarily large horizons. A positive minimum separation or a fixed finite family must be stated to obtain a uniform finite horizon.

The safe outputs are:
- singleton: all feasible worlds share one target label;
- multiple labels: ambiguity remains;
- empty: the declared model/contract/noise bound failed, rather than evidence for a specific source.

Those decision rules are established set-membership diagnosis. Their value here is truthful reporting and preventing an optimizer from choosing one arbitrary feasible world.

## 3. Ideal permutation contracts: exact but directly inherited

Take a public multiset d_1,…,d_n with all permutations permitted, equal slot duration, common known e_0, ideal storage, and no binding power limits. Define U_k as the sum of the k largest entries and L_k as the sum of the k smallest entries. Every realization satisfies L_k≤D_k≤U_k, with both extremes attainable.

A common p fixes Z_k. At a given k its feasible energy states span U_k−L_k, so C≥C_0:=max_k(U_k−L_k). The public midpoint cumulative output Z_k=(U_k+L_k)/2 with e_0=C_0/2 fits all realizations. It starts at Z_0=0 and ends at Z_n=Σd_i, hence every realization returns physically to e_0. Since the schedule depends only on the public multiset, a controller choosing battery power from current d_t and prescribed p_t is causal; it does not predict the secret order.

This derivation is valuable and elementary. Its common-output existence part is the permutation specialization of P1. Its endpoint and causality observations come from the chosen public schedule. They should be labeled as corollaries/constructive interpretation, not presented as a previously unknown battery-privacy capacity law.

Rate/ramp constraints can destroy feasibility of this midpoint schedule, but “add the inequalities to an LP” is not sufficient novelty. A genuinely useful result would give a new closed-form condition, complexity separation, or tight approximation gap under a realistic contract, with the ordinary constrained model-invalidation baseline retained.

## 4. Strongest remaining candidate and its current status

The separate file `LOSSY_PERMUTATION_BOUNDARY_AUDIT.md` analyzes the proposed lossy exact-reset rigidity result. Its status is:

- **Mathematical claim appears credible under the stated narrow model.** A slot-constant universal output with exact reset for every permutation is forced to be flat when 0<ηcηd<1 and simultaneous charge/discharge is excluded.
- **Proof machinery already exists.** Terminal reset is an assignment constant-value constraint (P2); the storage bound is an extremal partial-sum argument.
- **Exact battery statement was not located in this targeted search.** This is a search result, not proof of novelty.
- **Potential contribution:** a carefully stated physical singularity between ideal and lossy all-permutation exact-repeatability, plus a sharp approximate-reset/measurement-information boundary if developed.
- **Insufficient contribution:** relabeling this as a new general source-localization algorithm, claiming sparse telemetry beats PCC without a same-information budget, or reporting only the simple proof and synthetic orders as a high-novelty method paper.

## 5. Recommended claim discipline and minimum next gate

### Defensible framing

“Using established cumulative-energy privacy geometry and model-invalidation theory, we characterize a particular work-contract family. Exact cycle restoration under asymmetric charge/discharge losses imposes additional output rigidity; this changes the minimum storage needed to keep every admissible job order observationally equivalent.”

This wording still requires proof, model boundaries, and a novelty comparison. It does not claim the entire physical consequence was already published, nor claim the general tools are new.

### Gate before any larger experiment

1. Prove the lossy theorem with all quantifiers: every permutation, one common fixed output, one common initial state, equal-duration slots, exact terminal restoration, positive efficiencies, no simultaneous charge/discharge, no curtailment or external generation.
2. Test degeneracies: constant demand multiset, two-slot block, repeated levels, outputs at extrema, reserve-adjusted capacity, and ηcηd=1.
3. State whether p is slot-constant physically or only its sampled average. Intra-slot modulation can invalidate a theorem based on φ(p−d) if φ is applied after averaging.
4. Establish what happens under an ε terminal tolerance, uncertain efficiency, finite sensor precision, and a continuing stream of arbitrary block orders. A discontinuity confined to exact equality needs an honest robustness interpretation.
5. Distinguish order hiding from source-location hiding. Provide two different physically meaningful labels that really remain feasible; a constant output with zero FO is not an unidentified nonzero FO source.
6. Compare against direct PCC observations with exactly the same public contract, sampling/filtering, noise, and communication budget. If output is truly identical at each PCC, no more accurate PCC meter can reveal the upstream secret; if only remote projected outputs match, a local PCC can.
7. If only standard corollaries remain after these checks, stop at a transparent taxonomy/benchmark/theory note. Do not enlarge the simulator to manufacture methodological novelty.

## 6. Search coverage and limits

Targeted searches covered exact shared-output battery feasibility, universal privacy and permuting channels, finite-battery recharging privacy, causal service-curve storage calculus, constrained fault isolation, strong unknown-input observability, FO source identifiability, and assignment permutation-invariant sums. The decisive hits were full primary manuscripts P1–P4, P6–P11, and P14; P5/P12/P13 have explicitly noted inspection limits.

Downloaded source provenance, sizes, and SHA-256 digests are in `download_provenance.json`. Failed direct fetches are recorded, not silently treated as successful. Local full papers/text are research copies and should not be republished in a user-facing deliverable without checking license terms. The final audit can cite their public URLs.

No claim of exhaustive priority clearance is made. In particular, the lossy rigidity/singular-limit statement should be searched again using its finalized mathematical terminology before a publication claim.
