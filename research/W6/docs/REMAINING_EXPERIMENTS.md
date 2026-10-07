# Remaining experiments, baselines, stopping rules and permissions

## Priority 1: settle a defensible paper scope

Use `research/novelty/CLAIM_PRIOR_MATRIX.*` and the full-cycle theorem text to build a claim-to-assumption-to-evidence table. Independently review the terminal-recovery reduction and sharp hazard condition together. Cite standard critical-speed, regenerative accounting, Bellman and stochastic-control tools. Keep the earlier hard-deadline failure and round-2 correction prominent. Stop a broad novelty claim if the distinct theorem content is not established; a narrow theory or methods/negative-results paper is still an honest possible outcome.

For numerical claims, replay the exact witness/independent cost checks and mesh refinements. If claiming rigorous cost certificates, implement directed/outward rounding of transcendental weights, quadrature, bounds and objective sums with an independent checker; high precision and exact rational path feasibility alone do not close this requirement.

## Priority 2: close quality before efficiency claims

1. Freeze benchmark, validator, prompts, generation limits, model/tokenizer identity and allowed output formats before model execution. Treat the public heldout examples as seen by anyone who has inspected their answers; create and preregister genuinely unrun families if unseen evaluation is required.
2. Q: run development/calibration once each under the authorized current engine. Keep all 12 scheduled tasks, failures, truncations, unsupported syntax and missing outputs. Do not replace failed tasks or repeatedly change settings until a pass is obtained.
3. Use human judges blind to treatment labels for writing content/genre judgments. Establish how disagreements are adjudicated before the comparison. Preserve complete outputs, token IDs/hashes, termination evidence and the complete scheduled denominator.
4. A strict quality-matched statement needs both arms to satisfy the frozen contract for the entire prespecified task set. If not, report joint quality/cost outcomes and refuse a same-quality efficiency claim. Natural EOS does not imply useful-task completion.

## Priority 3: bounded runtime comparison, separate from physical W6

The latest Q/O/R0/R protocol is in `continuation/comparison/PROTOCOL_ZH.md` and `GATES_AND_DESIGN.json`. These stage names are not the original W6 A–E branch names.

- O: compare COMMON versus MIN observational overhead on 4 fresh engine sessions using calibration tasks and balanced order. Both arms share energy endpoints and validation. Do not subtract a historical overhead percentage from later measurements
- R0: test one eager versus native graph-enabled calibration pairing only if the installed engine supports it. Verify actual graph capture and replay, resolved configuration, model identity, BF16, seed 17, temperature 0, concurrency 1, disabled prefix caching and natural EOS. A flag alone is not treatment compliance
- R: after freezing the candidate and analysis, use 12 paired blocks, 6 per order, each arm a fresh engine episode on the same identified device, each running the fixed 6-task heldout workload H once. Record device reuse and cluster by actual device rather than treating requests/tokens as independent samples
- Count startup, model load, graph capture/compile, warmup, all scheduled requests, failures, recovery, logging and exit. Report request, padded GPU-counter cycle, and episode/job boundaries separately. Uncovered endpoint energy is unknown. No arbitrary idle subtraction or unlimited startup amortization
- Identical complete output token sequences are needed to attribute a difference to equal-computation runtime efficiency. Otherwise describe a whole-configuration quality/cost comparison and retain every mismatched pair
- Report effect sizes and uncertainty with explicit assumptions; 12 blocks do not guarantee precision. No business noninferiority/SLO or significant savings claim without a prespecified target and appropriate evidence

Stop R if graph execution is unavailable/ineffective, quality fails the claimed comparison, source identity drifts, measurement is broken, unaccounted work is present, or safe closure cannot be established. Do not upgrade dependencies, rent another server, lower quality standards or switch to batching to make R succeed. A separate batching/scheduling study requires its own arrivals, queueing, deadlines and batch-cost contract.

## Priority 4: physical W6, only after authorization and instrumentation

The original engineering claim needs:

- Verified actuator scope, privilege and response. Measure cap/clock command issue, acknowledgment and **actual-power** response separately; do not use client sleep/slow reads as GPU control
- Calibrated electrical boundary, units and sampling/response bandwidth, same-acquisition useful-work/power alignment, clock offset/drift/error bounds, missingness and counter-reset policy
- Measured service law and uncertainty at fixed useful work/quality, across context length, cache state, thermals and operating range
- Natural-EOS visibility latency, implementable post-EOS return/burn, all recovery costs and observable initial/final state closure
- Simultaneous facility measurements and validated DC-to-PCC transfer before PCC/grid claims; site-specific limits must come from authorized evidence, not a convenient synthetic threshold

Use the detailed F/I/N/C/A/X/G/O/Z experiment IDs and dependency closure in `execution_plan/experiment_design/EXPERIMENT_MATRIX.*` and `ROUTE_PLAN.json`. Mark unavailable required experiments BLOCKED, never PASS. CPU theory, GPU_ONLY description, GPU_DC control and PCC claims are distinct routes.

## Required baselines and ablations

- Corrected globally optimized constant target plus full return; same-information Bellman; original task-only objective/controller as an explicitly incomplete-accounting ablation
- Matched mean cycle time where feasible, with infeasible cases retained; distinguish dynamic energy from allocated facility and weighted objectives
- Full cycle versus task-only ledger; post-EOS burn/return inclusion; reset-state and EOS-delay assumptions; convex/hazard condition boundary and counterexamples
- Useful-work redirectability/no-exogenous-benefit assumptions; fixed-power versus cap commands; event versus sampled executor and delay; all sampling/logging/compile overhead
- Guarded versus unguarded scalar signed-memory response; amplitude-only, slew-only and LP-support guards; nominal versus stated uncertainty; complete post-return/infinite tails
- Uniform versus knee-aligned meshes as separately labeled numerical resolution studies; preserve the post-confirmation amendment instead of blending it into the original confirmations

## Transfer studies needed for any broader claim

Preregister heldout workload families and service parameters, then freeze models/configurations before testing. Add distinct model/tokenizer families and authorized hardware only if making model/hardware generalization claims; repeated deterministic output is not a new quality case. New distribution families may invalidate the theorem. Queue/concurrency or nonlinear network claims need separate models and fresh validation, not a scalar-model plot. The inherited Kundur transfer is a qualified linear benchmark result; regeneration from upstream ANDES must match the retained release/source-case provenance and is distinct from replay of the included reduced matrix.

## Stop and escalation rules

- No new paid compute, accounts, credential handling, remote access, driver/security changes, power/clock/voltage changes, facility instrumentation or publication is authorized by this bundle
- Confirm operator/device ownership, allowed ranges and restoration plan before any live actuator test; obtain specific permission for the actual target/action
- Preserve negative or inconclusive results, all scheduled attempts, hashes, frozen protocols, failures and changes. Do not sample until significance
- Halt a dependent stage when required identity, calibration, quality, physical boundary, licensing or permission evidence is missing. Deliver the blocker and the highest evidence level actually reached
- Completion means a reviewed claim/evidence table and reproducible package with every selected experiment accounted for. A terminal BLOCKED record closes bookkeeping, not scientific validation
