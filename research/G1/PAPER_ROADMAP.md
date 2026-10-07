# G1 research plan and stopping rules

## Priority gate before new computational sweeps

Read accessible full texts of the closest feedback/resource-recovery literature and construct a theorem-by-theorem comparison: information available, noise/delay sampling, common initial state, admissible controllers, actuator limits, prefix versus terminal constraints, and resource metric. The inherited audit flags Wu's minimum-energy FFR work (DOI 10.1109/TPWRS.2023.3285941) and PNNL RATLLE/PNNL-39459 as unresolved full-text gaps. Use an authorized public/library copy; do not bypass access restrictions, infer nonexistence from an inaccessible paper, or contact authors without permission.

Stop the novelty claim if a closest result already contains the same quantifiers, storage/recovery statement, and observation-radius characterization. A useful application or counterexample may remain; relabel it instead of hiding overlap.

## Paper-focused result to pursue

The candidate contribution is a contract-to-resource theorem: indistinguishability under bounded observation error induces a controller-independent prefix resource lower bound; a validated same-information controller supplies a strict feasible upper on a better observation contract. The all-family opacity threshold is distinct from the unknown optimal capacity curve. Present low-noise frequency sufficiency prominently.

## Experiments and ablations

1. Preserve and rerun the fixed normalized lower and six upper witnesses. Verify common initial class/SOC, all noise histories, causal delivery times, real ZOH, and complete recovery accounting
2. Sweep error, sampling and delay under preregistered common constraints. For each cell distinguish feasible upper, necessary lower, unresolved gap, and infeasible contract. Avoid treating upper-vs-upper differences as optimal superiority
3. Compare the same predictive-filter family with P-only, frequency-only, both, and no later observation. Also retain the stronger continuous CBF as a separate, richer-information contract rather than a matched baseline
4. Audit sample-aligned edges, noise extremals, intermediate phase/time maxima, nonanticipativity, recovery windows, initial SOC selection, and actuator/SOC tolerances. Retain rejected controllers and phase scenarios
5. Resolve at least one meaningful interval of the optimal error–capacity tradeoff or prove why the all-family hiding threshold does not locate its transition. A dense grid alone is not a theorem
6. Distinguish imperfect model, imperfect sensor, and imperfect actuator uncertainty. Add interval/robust proofs where claimed; plain float Monte Carlo supports finite evidence only

## Network transfer and deployment

The current Kundur necessary lower is below the feedback upper. Before claiming a network-level information separation, tighten the lower or find a correctly matched stronger upper without changing the contract after results. If the bounds still overlap, publish the non-separation honestly.

Retain the failed +10% amplitude challenge; add preregistered amplitude, damping, phase, ramp, charging-efficiency and PCS-lag challenges with independently refined integration. Hold out topology and operating points. Report minimum voltage as an observed endpoint unless a voltage safety limit was specified in advance. Do not use the two-state theorem as a nonlinear-network guarantee.

An empirical AI interpretation requires synchronized workload phase, actual input electrical power, voltage/frequency at the declared electrical boundary, actual controller outputs, and restoration measurements. GPU software telemetry is not PCC power. Acquisition/switching of real storage or power controls requires separate hardware authority and safety review. Synthetic alternating loads do not establish task-specificity.

## Stop / go

- Go to a narrow theory manuscript only after independent proof review, exact artifact replay, and closest-prior comparison support a distinct claim
- Keep model-only status if realistic observation/actuator contracts are absent
- Stop hardware-savings language until system costs and measured validated effect exist
- Stop broad nonlinear robustness language at the first unqualified counterexample; record and characterize it
- If a baseline given the same information erases the separation, report the boundary and end algorithm-superiority claims
- No declaration of paper readiness follows merely from successful code execution

## Permissions and blocked work

Already packaged: local read/replay, public source references, synthetic data and saved research outputs. Not authorized by this handoff: purchasing compute or data; accepting paywalled legal agreements; using credentials; proprietary-data upload; contacting authors; operating a GPU power-cap/clock/scheduler or physical grid/storage device; external submission/publication beyond the explicitly requested repository; deleting original evidence. Ask the owner for the exact missing permission before those steps.
