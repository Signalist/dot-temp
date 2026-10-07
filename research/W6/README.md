# W6: full-cycle inference power smoothing, with quality gates

**Handoff date: 2026-10-07. Research candidate, not a completed hardware/control paper.**

The question is whether a useful inference job with an uncertain natural end can be scheduled against an actual-power slew limit at lower full-cycle energy/latency cost, including physical recovery and any necessary post-EOS burn. A secondary question is which sufficient grid-memory guards survive that recovery. A cap command, reported GPU power, useful work, output quality, and facility power are separate quantities.

The strongest current contribution is a **narrow mathematical model**: an exact terminal-recovery projection, a sharp power-law tail-hazard convexity condition, finite-atomic EOS bridge/Bellman reductions, and qualified CPU witnesses. The cap-to-actual-power/control mechanism, useful-work quality matching, and DC/PCC measurement chain remain unestablished.

## Latest evidence takes precedence

The 2026-10-07 CPU continuation supersedes earlier optimistic quality assumptions:

- 108 historical requests = 72 MAIN + 36 warmups; MAIN has only **3 distinct quality cases**, each repeated 24 times
- Writing produces 4 sentences where 5 were required; code violates output constraints and its run-partition function drops a final element; arithmetic supports only four final answers, with broader quality unknown
- The 18-task, 9-family synthetic quality pilot and 288 differential code cases test validators; reference fixtures are **not model outputs**
- Writing machine passes stay `MACHINE_GATE_PASS_HUMAN_PENDING`; unsupported code stays unknown; natural EOS is recorded separately from quality
- **New GPU runs in this continuation: 0. `J_W6 = null`. Full original W6: incomplete**

Do not use an earlier report, fixture, repeated output, telemetry counter, synthetic demo, or this successful packaging test to reopen those gates.

## Late graph-aware comparator: plan only

The latest continuation proposes a **conditional native-vLLM graph-enabled versus eager runtime comparison**, with output-quality and identical-token checks. Its Q/O/R0/R phases cover quality calibration, measurement overhead, graph-treatment compatibility and a frozen paired comparison. They are separate from original W6 A–E branches. `continuation/comparison/PROTOCOL_ZH.md`, `GATES_AND_DESIGN.json` and `PAIRED_ORDER.json` contain the design. **There are no new GPU comparator results.** Actual capture/replay must be verified; flags, fixtures and CPU tests do not establish the treatment. Even a future runtime benefit would not validate cap/burn/DC/PCC control or physical W6 novelty.

## Read first

1. [Question, findings and evidence limits](docs/RESULTS_AND_LIMITS.md)
2. [Remaining paper experiments and decision gates](docs/REMAINING_EXPERIMENTS.md)
3. [Data, provenance and license status](docs/DATA_PROVENANCE.md)
4. [Reproduction and environment](docs/REPRODUCE.md)
5. [Agent starting prompt](AGENT_STARTING_PROMPT.md)
6. [Release review and exclusions](docs/RELEASE_REVIEW.md)

## Quick CPU checks

From a published repository checkout:

```sh
cd research/W6
python scripts/verify_manifest.py
python scripts/run_checks.py
```

If this folder itself is the checkout root, omit `cd research/W6`. The base checks need Python 3.10+ and its standard library only; the tested runtime was Python 3.12.14. They compile authored source, run quality-validator and acquisition-kit unit tests, reproduce the compact historical quality diagnostics, exercise the parser gate, export only development prompts, and test manifest/gate invariants. They do not execute generated model programs, start GPU inference, or set power limits.

Optional scientific checks require the versions recorded in `requirements-science.txt` (not a fully resolved environment lock):

```sh
python scripts/run_checks.py --science
python scripts/run_checks.py --full-cycle-replay
```

Checks execute on a temporary copy and write only the new report selected with `--report`. The first scientific option is a small CPU smoke and mathematical-witness check; the second additionally runs the saved full-cycle audit/reoptimization entry point. Neither is a fresh hardware experiment or a strict interval certificate. Full model regeneration is documented separately.

## Payload map

- `research/full_cycle/`: theorem/proof text, solver source, frozen model results, independent audit source, explicit negative/repair ledger, round-2 erratum, Azure length-law evidence and CC BY 4.0 notice
- `research/grid_memory/`: W6 grid-memory theorems, signed-response counterexamples, support LPs, guard/executor model studies, paths and negative transfer summaries; the qualified reduced Kundur input, adapter source and GPL notice are included without the unrelated grid project
- `research/novelty/`: source/claim ledger and conditional novelty disposition; general convexification/control priority is not claimed
- `research/measurement/`: source-coverage audit, data-only parser and minimal physical measurement protocol
- `gpu_handoff/`: offline/demo-first acquisition/analysis source, schemas, placeholder configurations and tests; live hardware operations require a separate authorized operator scope
- `execution_plan/`: detailed prior experiment matrix, contracts and phase prompts, retained as planning artifacts
- `continuation/`: latest fail-closed quality source, frozen synthetic benchmark, historical rescoring results, paired comparison design and bounded review
- `provenance/`: original-to-publication file hashes and dataset provenance
- `verification/`: checks run for this public-payload preparation, distinct from historical scientific reviews

## Preserve the research record

Current model-relative reductions versus the **globally optimized constant-target-plus-return class** are about 0.198%–1.694% in weighted full-cycle objective. At genuinely matched mean cycle time, 6 feasible matches yield about 0.455%–3.866% dynamic-energy reductions; the other 6 target-class matches are infeasible. These are synthetic-model comparisons, not measured inference savings. The old 6.85% target-baseline headline is withdrawn. The original hard-deadline failure and round-2 saved-path erratum remain valid.

## Scope and permissions

This payload is prepared for publication review; no publication, new remote access, paid compute, hardware actuation, or data-sharing permission is granted by a prompt or configuration inside it. Stop at the gates in `docs/REMAINING_EXPERIMENTS.md`. Do not restore excluded inputs from private locations, change driver/security settings, rent GPUs, or open a new service account without the responsible operator's explicit authorization.

No blanket open-source license is asserted for authored project materials. The included Azure data has its own explicit CC BY 4.0 license and attribution. See `docs/DATA_PROVENANCE.md` before redistribution or reuse.
