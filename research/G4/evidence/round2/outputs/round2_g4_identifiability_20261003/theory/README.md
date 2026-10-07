# Independent theory package

## Read first

- `SERVICE_DECISION_CERTIFICATE_ADDENDUM.md`: fixed-site service decision with identical complete PCC prefixes, opposite physical feasibility, an all-control exclusion, finite-PCS acceptance/recovery construction, and a strictly causal guarded SOC bit
- `SERVICE_DECISION_INDEPENDENT_AUDIT.json`: exact arithmetic and independent ODE validation of the service certificate, including continuous accepted SOC states
- `FIXED_INITIAL_INDEPENDENT_AUDIT.json`: separate direct-physics checks of 42 successful primary half-SOC/fixed-hardware schedule records
- `LOSS_TOLERANCE_TASK_ORDER_THEOREMS.md`: full proofs of lossy task-order rigidity, exact and positive-tolerance boundaries, arbitrary-block uncertainty and common-mode accounting, repeated-block drift, classical rearrangement formula, range-constrained intra-slot extension, persistent pairwise counterexample, and infinite-horizon capacity theorem
- `IDEAL_BUFFER_AND_MEASUREMENT_BOUNDARY.md`: exact two-world corridor criterion, cumulative-difference and horizon special cases, cyclic ambiguity, causal interface, known/unknown linear measurement maps, bounded noise, source/waveform/cause distinctions, sensor/experiment certificates, and sufficient dynamic DC-energy horizon

## Strongest proved statement

For a fixed positive-loss, no-leakage storage model, positive task multiset executed in arbitrary independent permutations every block, and common slot-constant PCC in the task-power range, every infinite universally hidden trajectory class requires

B >= 2Q + W_infinity

Here Q is the positive stored-energy sum at the unique flat exact-reset power, and W_infinity is the total accumulated assignment-residual range across blocks. Flat power attains minimum capacity 2Q when the initial energy is Q. The result allows arbitrary public block schedules and does not require exact recovery or even a recovery band; finite capacity alone suffices. For the two-level task class, range-constrained intra-slot modulation transfers through slot means.

Positive-tolerance finite-horizon recovery is exactly described by |sum midpoint residuals| + half the sum residual ranges <= tolerance, plus all internal state-prefix constraints. No SOC is reset. For one high task, the residual range is delta*(1/eta_d-eta_c)*PCC slot-mean spread.

Failure to hide the entire task class is not identification of every pair: an explicit two-order ambiguity persists forever, including a separately integrated smooth, lossy, finite-PCS example.

## Independent checks

The audit scripts import none of the primary scenario builders or optimizers. They only read the frozen experiment JSON and directly evaluate the piecewise storage physics.

- 78 saved schedules checked directly, with maximum capacity violation 8.96e-10 and maximum recovery violation 8.75e-10
- All histories enumerated for 63 short-horizon cases through K=5 (6^5=7,776 histories); larger cases have explicitly realized extremal physical histories
- 1,000 seeded random scalar corridors agree across interval recursion, all-pairs cumulative inequalities, and an independent full-variable LP; 435 were feasible
- 100 rearrangement tests exhaust 48,395 complete assignments; maximum extremum error 2.13e-14
- Independent full-history LPs, without interval compression, reproduce K=1 and K=2 optima to below 4e-14, and produce additional K=3 checks
- Independent closed-form periodic capacity audit has maximum error 1.91e-10
- Smooth first-order PCS integration: maximum tracking error 6.93e-14, maximum endpoint error 7.96e-13; SOC carried between every integration segment
- All 12 main audit categories and all 6 smooth-physics categories pass

## Reproduce

Run `python theory/independent_theory_checks.py` and `python theory/check_smooth_physical_witness.py` from the package root, or use their full paths. These use ordinary local CPU and write only this theory directory. The former reads the two primary experiment JSON artifacts named below.

## Audited source fingerprints

- `RECOVERY_FRONTIER_RESULTS.json`: `49ee8920f74b890513ff081321cc18d3ebd22b452dc69ba96b3f0f22715db9e4`
- `CAUSAL_HORIZON_RESULTS.json`: `19ae96161abc170d83c588eafa2149195800682ffc8273e78d66719b201e9565`

## Scope and audit caveats

The proof is stronger than numerical evidence within its model, but no hardware measurement, workload semantics, or literature novelty is established by these checks. Current-task-before-actuation timing is explicit. A finite continuous slew cannot realize a literal step; the smooth-DAG pair is a different waveform contract and does not inherit the step-frontier numerical capacities. The known-noise and unknown-noise factor-of-two distinction, uncertain initial states, recovery tolerance, mapping uncertainty, and infinite-versus-finite horizon limits are explicit.

Classical LP, rank, assignment/Monge, interval-hull, and set-membership methods are not presented as new. Novelty assessment is a separate literature task.

## Service-decision and primary fixed-initial additions

The service certificate is a matched-information acceptance/abstention decision at a known site. The two worlds share every PCC sample before commitment, the same completed work and future tasks, and the same actuator state. One lacks the required stored energy under every allowed control; the other has a smooth finite-PCS service and exact recovery witness. A guarded, stale/noisy SOC bit delivered before commitment safely accepts every state that passes its bound. A same-information conventional robust baseline obtains the same answer. No special estimator or sensor-cost advantage is claimed.

- Service audit: all 11 categories pass; independent tracking/PCC errors are below 2.1e-13
- Fixed-initial audit: 42 successful schedule records pass direct nonlinear physics, half-SOC, converter rates, state/recovery bounds, and extremal-history checks; all histories are enumerated where K<=5
- Six failed/infeasible solver rows in the fixed-initial source are explicitly outside that feasibility-only simulation audit. Separate exact infeasibility certificates must support their exclusion
- `check_service_decision.py` and `check_fixed_initial_schedules.py` reproduce these additions
- The external one-bit report and the local exact SOC/model knowledge used for recovery are distinct information interfaces. A local feasibility bit carrying the same certified content is equivalent for the decision; the result does not privilege a particular SOC algorithm
