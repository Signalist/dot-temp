# G4 reproducibility and evidence scope

## Environment and tiers

Frozen environment: CPython 3.12.14, NumPy 2.3.5, SciPy 1.17.0, SymPy 1.14.0, Matplotlib 3.10.8. Requirements are `evidence/round3/requirements-replay.txt`. Exact verification can run with `python3 -S` using only the standard library. No Task Bench executable, real power trace, third-party paper, installed environment or commercial solver is needed for the main theory.

From the handoff root after `cd research/G4`:

1. `python3 tools/verify_handoff.py` checks public distribution hashes
2. `python3 tools/smoke_test.py` compiles all Python sources without bytecode and checks key saved exact results
3. `python3 -S evidence/round3/tools/replay.py --mode exact --output ../g4-exact-run` independently reconstructs all 89 rational finite LP models and verifies primal/dual feasibility and equal objective without importing producer code
4. `python3 evidence/round3/tools/replay.py --mode checks --output ../g4-checks-run` adds the independent small-theory and T6 threshold suites
5. `python3 evidence/round3/tools/replay.py --mode full --output ../g4-full-run` adds the two producer scripts, regenerated result comparisons, fresh exact checks of rebuilt 89 certificates and all original-work figures

Use a new output directory outside the handoff every time. The wrapper verifies its sanitized EVIDENCE_INDEX before/after, copies its source into the output, and compares scientific JSON after removing only `seconds`, `python`, `numpy` and `scipy` metadata keys. A scientific mismatch is a failure. PDF timestamp differences do not establish scientific changes. Source timing/LP comparisons are not exact just because a separate certificate layer is exact.

## Coverage boundaries

The independent checker covers 77 primary + 12 synthetic-power graph transfers, not the additional 5 ideal and 5 PCC-step producer cases. Independent 948 DAG/label and related LP tests are finite mathematical checks; theorem proofs remain separate. No real-world sample size is implied.

Original science manifests and the optional `--historical-round2` mode concern unchanged historical bytes. The sanitized second-round distribution does not satisfy that old 114-file contract. Do not use it to claim a fresh historical all-file verification. The replay remains self-contained for exact/checks/full third-round modes.

## Historical inputs and withheld grid matrices

Earlier non-grid identifiability and smooth-workload scripts are retained under `evidence/round2/outputs/round2_g4_identifiability_20261003`. Execute selected scripts only in a copied tree; see its scientific README for the older model. The earlier `reproduce.py` is retained source but its original package-hash guard is provenance-only after this distribution's exclusions.

Optional historical grid-transfer regeneration is blocked because five protocol-locked ANDES-derived matrix NPZ files are withheld pending redistribution/source-scope review. `provenance/EXCLUDED_FILES.json` and `evidence/round2/EXTERNAL_GRID_INPUTS.json` retain their hashes. Upstream input version is ANDES 2.0.0; case URLs and original hashes are in `provenance/GRID_INPUT_RECIPE.json`. The upstream software is GPL-3.0-or-later; its license notice is retained. No raw case workbook or installed ANDES source is bundled.

The retained `grid_adapter.py` and `README_qualification.md` describe model variant, disabled demo events, descriptor ports, chain-rule corrections and exclusions. They are not a complete standalone regeneration recipe for every omitted derived matrix; the earlier full qualification driver is absent. Obtain the exact qualified artifacts from an authorized source or recover/rebuild the complete qualifier and verify the locked hashes. Do not substitute an unqualified case, call an eigenproblem matrix a physical descriptor, or present a different-model run as a reproduction.

Historical frozen outputs remain readable but were not rerun by the third-round checks. They do not establish actual PCC-PMU task attribution or calibrated grid benefit.
