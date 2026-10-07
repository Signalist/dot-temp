# G3 reproducibility and evidence scope

## Environment

Frozen third-round environment: CPython 3.12.14, NumPy 2.3.5, SciPy 1.17.0, CVXPY 1.9.3, CLARABEL 0.11.1, mpmath 1.3.0, Matplotlib 3.10.8. The exact saved-payload replay needs NumPy/SciPy/mpmath; the SOCP baseline additionally requires CVXPY/CLARABEL. Use a new virtual environment and the pinned `evidence/round3/requirements.txt`. No installation package, environment binary, GPU or paid simulator is included. See fresh validation for installed versions and never-run stages.

## Commands and outputs

All commands below are from the handoff root after `cd research/G3`. `python3 tools/smoke_test.py` compiles every recovered Python source without bytecode and checks the frozen bound, strict inner margins, complete rational payload and retained failed grids. It is not a dynamic full-source test.

`python3 tools/reproduce.py --mode exact --output ../g3-exact-run` first verifies the public manifest, copies only the third-round tree, reconstructs the rational command plus exact correction from the saved NPZ, checks the rational profile, rechecks outward interval exports, and runs saved scientific assertions. The generated `REPLAY_RESULT.json` reports commands, exit codes, versions and log hashes. The output directory must be new. Reruns should use another directory.

`python3 tools/reproduce.py --mode full --output ../g3-full-run` additionally runs the held LP at all three grids, outward inner/baseline/outer, account-and-ablation/continuous SOCP comparator, lag counterexample, independent numerical/root check, saved payload checks, figures and package assertions. Optimizer-dependent solutions may differ. A failed invariant or endpoint check must be investigated; do not round negative constraints away. Exploratory `src/explore_coupled.py` is separate and its numerical root is not a certificate.

The `exact` mode uses the saved frozen LP NPZ, so no optimizer is called. The wrapper's all_passed means its executed stages exited successfully; it does not mean the complete historical archive was verified. The original `portability/verify_integrity.py`, old nested package manifests and historical full-archive hashes are provenance-only after sanitization; use root `tools/verify_handoff.py` for current bytes. Original 2476-file historical preservation cannot be independently claimed from this subset.

## Historical second-round experiments

Work on a copy of `evidence/round2`, never in the frozen tree. That tree includes `src/model.py`, `admission.py`, exact-cell theory, current-limit/energy/weak-certificate analyses, saved numerical witnesses, C++17 true-PWM source and V1A/V2/Phase3 regeneration scripts. Its README lists full regeneration order. A representative source test is `python3 theory/test_exact_cell.py` from the copied second-round root; it checks exact-cell formulas against numerical quadrature, not hardware. Run shape and ablation drivers as separate processes because they temporarily replace a profile function.

The already omitted large PWM/recovery raw traces are listed in `OMITTED_RAW_TRACE_INDEX.csv`. To recreate them requires a C++17 compiler and the full script chain; the archived public summaries are not replacements for traces. The old 34-run V2 and Phase3 outcomes are finite-tolerance historical checks at 600 kvar, not the new exact-recovery 808 inner. The public helper has historical hashes and should not be invoked as a current package-verifier after sanitized changes.

`evidence/early_audits` supplies the earlier model-sign, allocation and current-guard implementation source and reports. Most optional raw trajectories were already absent from its recovered package. Its report/build/package helper scripts are preserved for lineage; they are not supported blanket replay commands and may reference omitted artifacts. The latest standalone replay is the supported starting point.

## Numerical contracts

Outer: 30-decimal outward interval Riemann envelopes and fixed window/direction. Inner: 40-decimal outward interval evaluation with exact endpoint correction; profile audit uses rational times at greater precision. Finite optimizations and mechanism ablations remain ordinary floating point. Use scientific margin and rational/interval semantics, not byte equality of arbitrary optimizer coordinates or solver status, as the acceptance criterion.
