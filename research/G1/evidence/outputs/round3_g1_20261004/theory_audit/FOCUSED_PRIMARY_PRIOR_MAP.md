# Focused primary-source prior map for G1 round 3

Checked 2026-10-04 UTC. This is a small theorem-level check, not exhaustive novelty clearance. PNNL-39459 / DOI 10.2172/3422382 and Wu DOI 10.1109/TPWRS.2023.3285941 remain **unavailable for fulltext comparison after an access denial**. They were not accessed, retried, or sought through alternate fulltext routes in this task.

## Directly verified tools that cannot be claimed as new

### Sampled-data, delayed, uncertain-state CBFs

Singletary, Chen and Ames, *Control Barrier Functions for Sampled-Data Systems with Input Delays* (2020), [primary arXiv full text](https://arxiv.org/html/2005.06418)

- Proposition 1 enforces the barrier over a reachable set spanning each zero-order-hold interval
- Theorem 1 combines sampled-data safety and state uncertainty using incremental stability
- Theorem 2 uses stored input history and forward prediction for a known input delay; Corollary 1 adds bounded prediction uncertainty
- Thus sampled-data robustness, state-error margins, and input-history prediction are occupied methods. Their safety results do not provide the G1 common-SOC capacity calculation or exact finite recovery for an unknown continuing square-wave phase
- The auxiliary input-free CBF witness is weaker on actuation implementation: it permits a continuously evolving internal predictor/control between sensor arrivals. The separate main matched-information predictive filter uses genuine ZOH actuation at .1 and has its own all-phase interval checks. Neither should be advertised as a new sampled-data/robust-controller method

### Measurement-error robustification of a CBF

Dean, Taylor, Cosner, Recht and Ames, *Guaranteeing Safety of Learned Perception Modules via Measurement-Robust Control Barrier Functions* (2020/2021), [primary full text](https://arxiv.org/pdf/2010.16001)

- Theorem 2 uses error bounds and Lipschitz constants of the Lie derivatives/barrier to strengthen the estimated-state CBF constraint and guarantee true-state safety
- Theorem 3 gives a sufficient tolerable-error condition for the robust barrier to exist
- Adding a known barrier-expression error budget M is therefore a classical specialization, not the G1 contribution
- The task-specific calculation is the cooperative order comparison linking that margin to total discharge and power, followed by a common-SOC exact-recovery accounting. No general novelty is asserted for monotone comparison itself

### Robust backup sets and admissible inputs

Cosner, Singletary, Taylor, Molnar, Bouman and Ames, *Measurement-Robust Control Barrier Functions: Certainty in Safety with Uncertainty in State* (2021), [primary full text](https://arxiv.org/pdf/2104.14030)

- Theorem 3 establishes safety of measurement-robust implicit safe sets under a controller satisfying the robust constraints
- Combining a backup invariant set with measurement-error robustness and input admissibility was already treated experimentally as well as theoretically
- G1 should therefore not frame “all-phase safe recovery despite imperfect state estimates” as a new control architecture. Its continuing-load/resource quantifiers and explicit finite terminal moments must carry the argument

## Output-feedback reference/command governors

Angeli, Casavola and Mosca, *On feasible set-membership state estimators in constrained command governor control*, Automatica 37(1),151–156 (2001), DOI 10.1016/S0005-1098(00)00133-3, [publisher primary record and preview](https://www.sciencedirect.com/science/article/abs/pii/S0005109800001333)

- The accessible publisher text describes partial-state command-governor feasibility with the set of states compatible with noisy measurements, and gives measurement-set intersection/prediction recursions
- This directly occupies the idea that a conventional constrained controller can consume a bounded-noise information set
- This task did **not** obtain a complete theorem-by-theorem fulltext audit of that source. It is evidence against broad output-feedback/governor novelty, not a verified inclusion theorem for G1's exact resource/recovery model

## Classical bounded-error information sets

Bertsekas and Rhodes, *Recursive State Estimation for a Set-Membership Description of Uncertainty*, IEEE TAC 16(2),117–128 (1971), [author-hosted full text](https://web.mit.edu/dimitrib/www/RecursiveStateEstimation.pdf)

- The paper characterizes states compatible with bounded disturbances and corrupted observations, with filtering, prediction and smoothing formulations; instantaneous bounds are explicitly distinguished from energy bounds
- Thus “multiple worlds remain consistent with the observation record” is long-established set-membership reasoning
- The G1 shared-prefix construction is a particularly simple additive-LTI intersection argument. Its sharp scalar threshold comes from the range of the first-edge step response. It is not a novel impossibility paradigm or a general data-rate theorem

## Exact increment that remains plausible

A defensible candidate statement is: **for a continuing periodic reconnection model, observation channels with specified noise/delay admit different recoverable-storage resource requirements, with a controller-independent prefix lower bound and a conventional feedback upper witness, under one common initial SOC and one finite recovery contract**.

The large-noise opacity theorem and the small-noise no-power-sensor witness should appear together. Omitting the latter would hide an important limitation on claims about compute-phase telemetry. The opacity threshold is sharp for hiding the full first-prefix phase family, not for optimal capacity, feedback necessity, or hardware sensor economics.

Unresolved direct FFR/RATLLE fulltext comparisons remain a publication-facing gap. They cannot be closed by the sources above, by inference from abstracts, or by asserting that different terminology proves novelty.
