# Reproduction and environment

All commands below run from `research/G1` after `cd research/G1` from repository root. Python 3.12 was used in the historical review. Exact review dependencies are pinned in `evidence/requirements-review.txt`: NumPy 2.3.5, SciPy 1.17.0, mpmath 1.3.0. Full simulation additionally used ANDES 2.0.0, matplotlib and a separately qualified model/cache; installing a current simulator does not reconstruct the original qualification automatically.

## Safe package check

`python3 evidence/verify_package.py`

This is standard-library-only and verifies the new public package hash scope. It does not certify the science and does not check every historical source manifest.

## Saved-evidence CPU replay

`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python3 evidence/validate_copy.py --work-dir /tmp/g1-review-unique-directory`

The destination must not exist. Never run generators in `evidence/`. The runner copies evidence, restores exact public-hash duplicate snapshots in the copy, and runs:

1. `core/interval_lower_certificate.py`: true coefficient enclosure and residual-repaired lower certificate from saved LP duals
2. `core/interval_validate.py`: six fixed upper policies, continuous phase/time and recovery checks
3. `feedback_baseline/test_feedback.py`: seven finite implementation checks including nonanticipativity, noise-history coverage and numerical cross-checks
4. `network_transfer/audit_exact_boundaries.py`: 1,444 observation-boundary cases
5. Hardened `freeze_confirmation.py`: expected refusal before input generation, preserving 78 protected artifacts
6. Independent integration of the 24 canonical CSV sets and reconstruction of the three included nonlinear trace peaks, including the +10% failure

Each successful result is conditional on its stated model. The saved 592-check audit is preserved, not falsely counted as freshly rerun by the portable path.

## New science is a separate version

Copy `evidence/outputs` into a new research workspace. Do not overwrite current policies, controller freezes, manifests, results, thresholds, or excluded trials. Synthesis scripts may write outputs. Regenerated controller coefficients require a new identity and new validation; a different LP solver can choose a different degenerate optimum.

## Full-network replay dependencies

Read `evidence/README_PORTABLE.md`, `evidence/PACKAGE_SCOPE.json`, and `evidence/outputs/round3_g1_20261004/network_transfer/REPRODUCE.md` before any replay. Exact older-file hashes and simulator/case hashes are in `EXECUTION_ENVIRONMENT_LOCK.json` and the round2 provenance records. The supported compact review does not need ANDES.

Full nonlinear replay needs the official ANDES 2.0.0 `kundur/kundur_full.xlsx`, qualified adapter, generated cache, and omitted old-round source inputs. No arbitrary substitute model qualifies as an exact replay. Forty-one raw arrays (21 nonlinear and 20 same-input linear) were already omitted by the source archive; `PACKAGE_SCOPE.json` records every expected hash and byte size. This is an explicit unavailable-input boundary, not a successful reproduction.

If full dependencies are recovered into a separate copy, restore their hashes before `run_confirmation.py --start INDEX --stop INDEX_PLUS_ONE`. Existing per-case JSON may trigger resume-skip even when its NPZ is absent: back up only the copied output JSON/NPZ pair before rerunning. Do not use `--freeze` on archived inputs. Collectors and sealers are write-capable and require a new versioned workspace. Old complete source-integrity checks require 127+12 or 266 external historical files and cannot pass from this compact handoff alone.

A numeric replay may agree while NPZ bytes differ due to serialization. Report both numeric comparisons/tolerances and byte identity; never conflate them.
