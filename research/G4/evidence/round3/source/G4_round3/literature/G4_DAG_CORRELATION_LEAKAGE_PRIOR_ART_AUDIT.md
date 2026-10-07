# G4: exact prior-art audit for DAG orders, correlated blocks, and self-discharge

Audit date: 2026-10-04 UTC. Scope: primary-source theorem/model comparison, not exhaustive priority clearance. This extends the round-2 audit; it does not replace or retract the independently checked battery propositions there. Here, “self-discharge” means physical state contraction; “information leakage” means disclosure to an observer.

## 1. Decision-level findings

1. **Ideal common-output hiding of a DAG-restricted family is already inside Arrieta–Esnaola–Effros's arbitrary-family lemma.** Restricting permutations to topological orders does not evade that antecedent.
2. **Lossy privacy with self-discharge is explicitly prior art.** Avula–Oechtering–Månsson 2018 has self-dissipation, internal resistance, converter efficiencies, rate/capacity limits, and continued-horizon SOC management. The potentially distinct result is the exact universal task-order boundary, not the physical loss model or battery privacy concept.
3. **The DAG adjacent-swap engine is classical.** Linear extensions form a connected graph under feasible adjacent swaps. Constant terminal cost on that graph is equivalent to zero cost change on its edges. A battery-specific characterization of which slot constraints survive remains an application result.
4. **Correlated uncertainty is also established robust-inventory territory.** What matters for universal hiding is admissible support, not a correlation coefficient. Summing marginal block widths is exact only when the extremizing choices can be concatenated.
5. **Self-discharge invalidates permanent additive-width accumulation.** Discounted reachable-set sums and bounded disturbance invariant sets are classical. A new claim must concern a sharp battery/precedence specialization, not geometric-series boundedness.
6. **Opacity, zero mutual information, and one deterministic common output have different contracts.** The paper must state their quantifiers rather than contrast “deterministic” work with an inaccurately all-stochastic privacy literature.
7. No inspected source states the complete combined lossy, rate-constrained, DAG/common-output, correlated-block capacity result. That is a bounded-search finding, not a novelty certificate.

## 2. Contract that must accompany every comparison

Let Ω be the admissible demand-order histories. A common-output witness fixes one observable PCC waveform p, independent of ω∈Ω, and one initial state e0. Internal battery action may depend on the current task as needed to implement p. Every world must respect capacity, converter rate, the declared within-slot control class, and any recovery requirement. Universal feasibility is:

∃ p,e0 such that ∀ω∈Ω, the induced physical trajectory is feasible.

This is a static robust choice of the observable waveform, with secret-dependent internal compensation. It is not adaptive public dispatch that changes p after learning private demand. Causality of the compensator, initial-state commonality, public inputs, and whether the observer knows p must be explicit. With continuing work, blocks propagate their physical states; no artificial numerical reset is permitted.

## 3. Exact source-to-claim comparisons

### A. Deterministic common-output geometry: direct antecedent

**Arrieta, Esnaola, Effros (2019), _Universal Mutual Information Privacy Guarantees for Smart Meters_**, Definition 5 and Lemma 1, PDF p. 3. [Primary manuscript](https://arxiv.org/pdf/1905.00111)

For ideal additive storage and the paper's alphabet/model qualifications, Lemma 1 equates a capacity-bounded pairwise cumulative distance for an arbitrary family A of initial-state/demand pairs with existence of one feasible requested-energy sequence shared by all A. Its proof constructs that sequence by a cumulative envelope. The surrounding theorems use this deterministic lemma for universal mutual-information bounds.

**Exact consequence:** choosing A to contain DAG-admissible orders, or a finite correlated-history family, is already allowed. The ideal common-output corridor is therefore a specialization. The lemma does not supply a signed-loss, self-discharge, rate-induced affine, or lossy exact-recovery theorem. Never characterize this closest battery antecedent as “only distributional.”

### B. Converter loss and self-discharge: explicit privacy model

**Avula, Oechtering, Månsson (2018), _Privacy-preserving smart meter control strategy including energy storage losses_**, §II-A Eqs. (1)–(2), §II-C Eq. (4), §II-D Eq. (5), PDF p. 2; §III Proposition 2, p. 4. [Primary manuscript](https://arxiv.org/pdf/1803.07864)

The model includes Q_next=(1−γ)Q+βI_bat, a nonlinear resistive-current map, and the two-slope converter map ηcD for D≥0 and D/ηd for D<0. The combined energy-state update retains the contraction (1−γ). Section III optimizes accumulated Bayesian decision risk for a Markov hidden-appliance model through a PO-MDP recursion. Section IV-B discusses end-of-horizon SOC for continued operation.

**Exact distinction:** this is not a universal deterministic same-waveform theorem for every permutation or topological order. Conversely, introducing a scalar retention coefficient is a simplification of an existing privacy battery model. Their γ convention is lost fraction; in e_next=ρe+φ(·), ρ=1−γ, subject also to the update's β/time normalization. Do not identify these coefficients without normalizing units.

### C. DAG order invariance: classical feasible-swap geometry

**Felsner and Reuter, _The Linear-Extension-Diameter of a Poset_**, author manuscript dated 5 June 1997, §1, pp. 1–2; journal paper 1999. [Author PDF](https://page.math.tu-berlin.de/~felsner/Paper/lin-ext-diam.pdf)

The introduction states that any two linear extensions can be connected by adjacent transpositions through valid extensions, with path length equal to their inversion distance. The graph has extensions as vertices. The following battery comparison is our deduction, not a theorem attributed to their paper.

For slot/job costs C_tj, terminal cost T(π)=Σ_t C_t,π(t) is constant over all topological orders iff

C_ti+C_(t+1)j = C_tj+C_(t+1)i

for every adjacent incomparable pair (i,j) that can occur in positions t,t+1 in a valid extension. Necessity is subtraction; sufficiency telescopes along a connecting path. For no self-discharge, C_tj=φ(p_t−d_j); with retention ρ, C_tj=ρ^(n−t)φ(p_t−d_j).

**Boundary:** connectedness of the extension graph does not say that every pair of slots admits a mixed-power swap. Neither arbitrary 2×2 exchange conditions nor globally equal means follow without additional structure. In the unrestricted permutation case the familiar sum-matrix characterization is already assignment COVP; see **Ćustić–Klinz (2014/2016), §1 pp. 2–3**, [primary manuscript](https://arxiv.org/pdf/1405.6096). Neither graph source establishes battery capacity or prefix feasibility. Optimizing over linear extensions should not be advertised as an ordinary unconstrained assignment problem or polynomial-time routine without a separate algorithmic proof.

Additional primary confirmation: **Naatz (2000), _The Graph of Linear Extensions Revisited_**, [publisher record](https://doi.org/10.1137/S0895480199352609), studies the same graph; abstract/record inspected only. The full author manuscript above is the substantive connectivity citation.

### D. Correlated block histories: robust cumulative uncertainty already exists

**Mamani, Nassiri, Wagner (2017), _Closed-Form Solutions for Robust Inventory Management_**, §2.3 Eq. (1), p. 1629; §2.4 Lemma 1, p. 1630; §3.4.1, pp. 1636–1637; Theorem 5, p. 1639. [Author PDF](https://faculty.washington.edu/mrwagner/MNW.pdf)

Their uncertainty set constrains individual demands and partial sums jointly. Lemma 1 computes extrema of cumulative demand over this coupled set. Section 3.4.1 rewrites robust inventory-capacity constraints using lower cumulative-demand extrema. The dynamic result conditions its bounds on observed history. Thus dependent uncertainty, capacity, partial-sum extrema, and history-conditioned robust bounds have precise antecedents.

**Difference:** the inventory balance is ideal/additive, shortage is costed in the economic model, and decisions optimize procurement/holding/shortage cost rather than hide an order through a common PCC waveform. Covariance-inspired uncertainty sets are not exact languages of permissible task orders. A DAG/automaton support can require a different optimizer, but the “optimize cumulative extrema over the joint set” principle is established.

**Bertsimas–Thiele (2006)** remains relevant: §3.1 Eqs. (5)–(6),(13) and §3.2.2 Eqs. (25)–(26) formulate robust cumulative inventory and capacity constraints. [Author PDF](https://web.mit.edu/dbertsim/www/papers/Robust%20Optimization/A%20Robust%20Optimization%20Approach%20to%20Inventory%20Theory.pdf). Mamani's explicit partial-sum coupling is the closer citation for this extension.

### E. Discounted width and bounded continuation: direct reachability specialization

**Girard and Le Guernic (2008), _Efficient Reachability Analysis for Linear Systems using Support Functions_**, Proposition 2, p. 8967; §3 Eqs. (4)–(7), p. 8968. [Proceedings PDF](https://skoge.folk.ntnu.no/prost/proceedings/ifac2008/data/papers/0569.pdf)

The source gives reachable-set recursion Ω_(k+1)=AΩ_k⊕V and support-function rules for Minkowski sums, linear images, and convex hulls. Setting A=ρ^n and V to the block residual hull immediately gives discounted scalar endpoint extrema and width. Using hulls preserves extrema even when the attainable set has gaps; it does not prove every interior point is attainable.

**Kouramas, Raković, Kerrigan, Allwright, Mayne (2005)**, _On the Minimal Robust Positively Invariant Set for Linear Difference Inclusions_, §II Eqs. (9)–(10), §III Theorems 1–2, pp. 2297–2298, establishes convergent reachable-set/invariant-set constructions under stability and bounded disturbance assumptions. [Proceedings PDF](https://skoge.folk.ntnu.no/prost/proceedings/cdc-ecc05/pdffiles/papers/1964.pdf)

**Difference:** endpoint reachability alone omits the battery's within-block SOC/rate requirements, physical loss balance, and common-output synthesis. Those can support a specific new sharp bound. The scalar geometric-series argument alone cannot.

**Zou, Lin, Aliprantis, Chen (2018)**, _Robust Multi-stage Power Grid Operations with Energy Storage_, Theorem 7 and §III-C; technical report §III-D Eqs. (31)–(35), is an important battery-neighbor. It contrasts linear-in-horizon capacity under a class of affine policies with horizon-independent sufficient bounds, exact in a stated ideal infinite-horizon case. Its loss extension is sufficient, explicitly no longer necessary. Dispatch adapts to demand; common-output privacy is absent. [Author technical report](https://staff.ie.cuhk.edu.hk/~xjlin/paper/infocom18-robust-storage-tech.pdf)

### F. Opacity and mutual information: quantifiers, not synonyms

**Yin and Zamani (2019), _On Approximate Opacity of Cyber-Physical Systems_**, Definitions 3.1 and 3.3, PDF pp. 5–6, distinguishes exact output equality from metric-closeness of outputs. [Primary manuscript](https://arxiv.org/pdf/1902.09411)

Standard opacity asks, for each secret execution, for an appropriate nonsecret execution with matching observable behavior. G4's construction instead asks for one prescribed output feasible for every allowed order. Failure of that one-output intersection need not eliminate every ambiguous pair or violate every secret-specific opacity property. A battery terminal-recovery tolerance τ with exactly equal PCC traces is not approximate output opacity δ; they relax different requirements.

For a deterministic output map on a finite order family with a full-support prior, zero mutual information is equivalent to constancy of that map. With randomized mechanisms, zero mutual information refers to identical conditional output laws, not equality under an arbitrarily chosen cross-world coupling. An asymptotically zero normalized information rate can still disclose finite information. These elementary distinctions prevent overclaiming separation from statistical privacy. **Li–Khisti–Mahajan (2015/2018), Theorems 1–3**, studies ideal finite-battery causal information-theoretic control, including an i.i.d. infinite-horizon single-letter result. [Primary manuscript](https://arxiv.org/pdf/1510.07170)

### G. Compute-structure evidence and the limit of the power mapping

**Slaughter et al. (2020), _Task Bench: A Parameterized Benchmark for Evaluating Parallel Runtime Performance_**, §II, PDF pp. 2–3, Figure 1 and Table 2. [Author-hosted primary paper](https://legion.stanford.edu/pdfs/taskbench2020.pdf)

Tasks represent work and dependency edges represent communication/synchronization. Table 2 defines previous-timestep predecessor columns: stencil D(t,i)={i,i−1,i+1}; sweep D(t,i)={i,i−1}. The graph's columns represent parallelism, and kernel duration is separately parameterized. This supports genuine computational precedence structure.

**Permitted use in G4:** reconstruct small graph shapes from those mathematical relations, explicitly state finite boundaries and edge orientation, and call them Task-Bench-inspired precedence microcases. Equal slot durations, positive H/L power marks, serial execution, and conversion to electrical demand are G4's synthetic assumptions. No Task Bench code was run or copied for this audit. These cases are not measured power traces, parallel-runtime simulations, or replications of the paper's performance results. The PCC mapping remains uncalibrated.

**Narayanan et al. (2021), _Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM_**, §2.2, Figure 3, PDF pp. 2–3. [Primary manuscript](https://arxiv.org/pdf/2104.04473)

Figure 3 depicts concurrent device timelines, forward/backward microbatches, and idle pipeline bubbles around flushes. Its backward-pass duration is twice the forward-pass duration **by an illustrative assumption stated in the caption**, not a reported timing measurement. Figure 4 shows alternative interleaved schedules. These are concrete reasons not to identify a positive, equal-slot serial G4 schedule with complete training execution. This source does not calibrate battery parameters or PCC power, and it cannot turn the synthetic DAG examples into an AI-workload attribution result.

## 4. Mathematical guardrails for the extension (our deductions)

### 4.1 Correlation changes a universal result only through the admissible histories

For residuals r_l(ω), the exact K-block endpoint bounds without self-discharge are

E0 + min_(ω∈Ω_K) Σ_l r_l(ω), and E0 + max_(ω∈Ω_K) Σ_l r_l(ω).

The replacement by sums of separate minima/maxima requires simultaneous attainability. Example: r_l∈{−a,+a}, but signs must alternate and either initial phase is allowed. Each marginal width is 2a; cumulative width is zero after even K and 2a after odd K, rather than 2Ka. This is an endpoint example, not a complete battery witness.

A correlated probability law with positive support on every finite order word leaves the worst-case admissible family unchanged. An i.i.d. assumption is unnecessary for the old product-family theorem: set-theoretic concatenation is the actual hypothesis. For a finite automaton, retain its state when propagating endpoint sets; taking independent marginal hulls can add forbidden paths. If public output is allowed to depend on a private automaton state, the common-output requirement must be rechecked.

For time-homogeneous scalar residuals assigned to edges of a finite admissibility graph, nonzero repeatable cycle sums generate drift; zero cycle sums permit removal of repeated cycles and leave bounded simple-path residuals. This is classical weighted-path reasoning. **Karp (1978), Theorem 1 and the final-page recurrence**, provides the minimum-cycle-mean/path-DP antecedent, not a battery theorem. [Publisher record](https://doi.org/10.1016/0012-365X(78)90011-0). Primary scanned PDF was inspected via the web, but its shell download was denied; no bypass was attempted.

### 4.2 Self-discharge discounts uncertainty and changes exact recovery

The following formulas use slot-constant discrete inputs. Under e_t=ρe_(t−1)+φ(p_t−d_π(t)), 0<ρ<1, a block has

e_n=ρ^n e0+R_π, where R_π=Σ_t ρ^(n−t)φ(p_t−d_π(t)).

For independently admissible blocks, endpoint width obeys W_(k+1)=ρ^n W_k+range(R_k). Constant residual width w yields W_K=w(1−ρ^(nK))/(1−ρ^n) from a common initial state. Thus a persistent positive spread need not force unbounded endpoint uncertainty. Common-mode drift and every within-block constraint remain to be checked.

For two task levels and p_t∈[L,H], define κ=1/ηd−ηc>0 and F(p)=H/ηd−ηcL−κp. Adjacent mixed-task swaps impose weighted equalities ρ^(n−t)F(p_t)=ρ^(n−t−1)F(p_(t+1)), not equal means. For unrestricted task positions, a necessary terminal-invariance range condition is ηcηd≤ρ^(n−1), because F([L,H])=[ηc(H−L),(H−L)/ηd]. This condition is not a full reset/capacity theorem. Exact reset additionally requires R_π=(1−ρ^n)e0, with a feasible e0 and feasible prefixes. The round-2 no-self-discharge 2Q+W∞ result must not be carried over unchanged. With continuous self-discharge ė=−λe+φ(p−d), exponentially weighted slot integrals replace ordinary means. Low-task SOC need not stay monotone when p varies within a slot, so the previous endpoint-only SOC check also needs a new proof.

## 5. Defensible positioning

The literature supports describing the work as a sharp physical specialization of shared-output battery feasibility, feasible-swap constraints, and robust reachability. If the independent theory establishes an exact DAG-dependent capacity characterization or sharp changes under admissibility coupling/retention, report those statements and their model assumptions as the candidate contribution. Do not claim that DAG scheduling, correlated robust bounds, self-discharge privacy, opacity, or bounded-disturbance invariance are new.

An honest manuscript sentence is: “Our results characterize exact common-PCC feasibility for a specified lossy task-order contract. They specialize deterministic shared-output battery geometry and classical order/reachability tools, while distinguishing independent admissibility, precedence constraints, inter-block coupling, and physical retention.” Add the exact strongest theorem, not a generic novelty adjective.

Search coverage: primary battery-privacy papers; self-discharge privacy models; assignment COVP; linear-extension/precedence graphs; robust inventory with coupled uncertainty; support-function and invariant-set reachability; weighted graph cycle drift; exact/approximate opacity. Not covered exhaustively: specialist scheduling polytope literature, every recent storage-privacy preprint, or industrial controller contracts. Bibliographic dates are from papers/publisher records, not crawl dates. Source ledger and download provenance accompany this audit.
