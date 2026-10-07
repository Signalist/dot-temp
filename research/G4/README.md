# G4 handoff: task order and lossy common-output capacity

Status on 2026-10-07: **conditional narrow-theory candidate; not paper-ready**. The current evidence contains **89 independently checked exact rational primal–dual zero-gap certificates** (77 primary configurations and 12 graph-shape transfer configurations). It establishes no advantage over the same-information all-scenario LP.

## Exact research question

For a finite family S of equal-slot, serial, two-level workload words, common public grid output inside [L,H], lossy storage, a common freely selected initial state and independently allowed block histories, does arbitrary infinite, potentially nonperiodic public scheduling reduce the minimum capacity below a one-block exact-reset design? How does restricting executable task order through a DAG change that capacity, and where do cross-block support, leakage, nonconvex actions and disposal break the result?

Within the principal contract the optimum is exactly the one-block all-word LP value B*_S. Every infinite public schedule satisfies B ≥ B*_S + W∞, where W∞ is its limiting accumulated endpoint width. Legal mixed-label adjacent swaps induce a slot-position graph; endpoint invariance requires output equality on each component, with a sharp prefix-count formula when connected. The separate discrete affine-leakage model has an invariant-interval LP optimum even among nonstationary common outputs. Full-permutation endpoint invariance within the output cube exists iff ηcηd ≤ ρ^(N−1). Read the exact hypotheses and proofs in `evidence/round3/source/G4_round3/theory/THEOREMS.md`.

## Current findings and negative limits

- Same six labeled tasks, two high tasks, L=6, H=18, ηc=ηd=19/20, unit slot length: common output 1922/187; full-order capacity 6080/187 ≈ 32.5134, connected-DAG 3800/187 ≈ 20.3209, barrier-DAG 3040/187 ≈ 16.2567
- These are values of different allowed task-order languages, not optimization-algorithm savings. The matched all-scenario LP has the same optima
- 89 exact finite rational certificates are independent of producer code. There are also 948 tiny DAG/label row-space checks, 168 connected-formula LP comparisons, 169 leakage-grid checks and 90 threshold checks. Counts are configurations, not physical sample size
- The 5 ideal-efficiency and 5 PCC-step examples are outside the independent 89-record checker's declared coverage. They have separate producer certificates. Finite-horizon/leakage LP comparisons are floating-point unless expressly labeled exact
- Statistical correlation cannot help if the admissible history support is unchanged. Restricted support can prevent drift accumulation. Private precharge, nonconvex actions, disposal or changed energy budgets violate principal assumptions; exact counterexamples are included
- PCC step bounds are not continuous converter slew. Discrete retention is not a certified continuous leakage/within-slot model
- DAG dependencies are genuine task semantics, but equal-duration serial H/L power and PCC mapping are synthetic. No GPU throughput, measured workload-power calibration, UPS/PCS validation, or real-grid source-attribution benefit is established
- Averaging, LP duality, exchange graphs, cycle potentials and robust reachability have classical predecessors. Combined theorem priority and high originality remain open

## Read in order

1. `docs/RESEARCH_ROADMAP.md` and `docs/STOPPING_AND_PERMISSIONS.md`
2. `evidence/round3/source/G4_round3/report/G4_ROUND3_DOSSIER_ZH.md`
3. `evidence/round3/source/G4_round3/theory/THEOREMS.md`
4. `evidence/round3/source/G4_round3/validation/INDEPENDENT_THEORY_REVIEW.md`
5. `evidence/round3/source/G4_round3/FINAL_SCIENTIFIC_STATUS.json`
6. `evidence/round3/source/G4_round3/literature/SOURCE_LEDGER.json`

`evidence/round2` retains the earlier identifiability, fixed-initial-state, causal-horizon, smooth-workload and grid-transfer source/evidence. `evidence/early_audits/GateC` retains the initial hidden-state construction and failures. These earlier models must not be merged silently with the third-round common-output theorem.

## Portable reproduction

From the repository root:

```sh
cd research/G4
python3 tools/verify_handoff.py
python3 tools/smoke_test.py
python3 -S evidence/round3/tools/replay.py --mode exact --output ../g4-exact-run
python3 -m venv .venv
.venv/bin/python -m pip install -r evidence/round3/requirements-replay.txt
.venv/bin/python evidence/round3/tools/replay.py --mode checks --output ../g4-checks-run
.venv/bin/python evidence/round3/tools/replay.py --mode full --output ../g4-full-run
```

Exact mode is standard-library-only. Checks mode needs NumPy/SciPy; full mode also needs SymPy/Matplotlib. Every output path must be new and outside the handoff. Scientific scripts run in a disposable copy; the wrapper compares results and rejects differences other than declared environment/timing fields. An absent dependency, missing input or mismatch is a failure/blocker, never evidence of successful reproduction.

`validation/HANDOFF_VALIDATION.json` distinguishes fresh checks from historical records. `PUBLIC_MANIFEST.json` is this handoff's distribution manifest; original science/package manifests remain provenance only. The third-round wrapper's EVIDENCE_INDEX was rebuilt for this sanitized tree. Optional original 114-file historical hash verification is not valid against a sanitized/missing-input copy.

Five historical ANDES-derived grid matrices are withheld pending redistribution/source-scope review; their exact hashes, upstream input provenance and acquisition limits are retained. Thus the optional historical grid-transfer regeneration is blocked, while the principal G4 theory and 89-certificate replay need no grid data. See `provenance/PUBLIC_SOURCES.md`, `docs/REPRODUCIBILITY.md` and `AGENT_START.md`.
