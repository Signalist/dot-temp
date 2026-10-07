# G3 round 3: portable evidence and verified replay

## What this ZIP contains

All 70 frozen files (the 69 files indexed by the original `MANIFEST.json`, plus that manifest) are preserved byte-for-byte. This includes scientific source, copied prior-core modules and theory, proofs, exact payload, results, figures, independent review, failed attempts, requirements and provenance. `portability/` adds clean-unpack replay logs and regenerated JSON records. No `__pycache__`, `.pyc`, virtual environment or compiled executable is included.

**Source/data self-contained; dependencies are not bundled.** Tested with Python 3.12.14 and the six package versions in `requirements.txt`. That file pins top-level packages only, not the complete transitive dependency graph. The replay used an already installed environment; a fresh installation was not tested. No dependency downloads were performed.

The original README phrase “Internet is not needed to reproduce scientific numbers” means that the calculations use local scientific source/data after dependencies are available. It does **not** mean `pip install -r requirements.txt` works offline. Install dependencies through normal package access, or provide your own compatible wheel/cache set. This is not an offline installer or a fully hermetic environment image.

## Verify the downloaded files first

From the extracted `g3_round3_portable_evidence/` directory:

    python portability/verify_integrity.py

This standard-library-only verifier checks the full portable manifest, SHA-256 index, exact file set, and the original 69-file source manifest. Run it before scientific replay: the original scripts deliberately regenerate outputs and runtime fields. After rerunning scripts, those changed outputs no longer match the frozen hashes. Keep one original extraction and replay in a separate copy.

`PORTABLE_MANIFEST.json` indexes every packaged file except itself and `SHA256SUMS`. `SHA256SUMS` indexes those files plus `PORTABLE_MANIFEST.json`; it omits its own self-hash. The ZIP's external SHA-256 and byte count accompany the ZIP.

## Reproduce the frozen-payload check

Use a Python interpreter with the packages in `requirements.txt`. In a disposable copy, run:

    python src/certify_prefix_interval.py
    python src/certify_zoh_inner.py
    python src/certify_matched_baseline.py
    python src/account_and_ablate.py
    python src/check_lag_counterexample.py
    python review/independent_coupled_numeric.py
    python review/check_interval_export.py
    python review/check_zoh_inner.py
    python review/check_exact_zoh_certificate.py
    python review/check_profile_rationals.py
    python src/verify_package.py

These 11 commands were run from a freshly extracted candidate ZIP. A twelfth command, `python src/zoh_inner.py`, was run in a **separate fresh extraction**, so optimization could not replace the input to the frozen-payload check. It reproduced all three recorded hold-grid attempts, with identical scientific JSON fields apart from runtime. The optional local-search script and figure renderer are included but were not rerun in this portability pass. Original figure QA is preserved.

Recorded results: 72 standalone package assertions pass; inner export audit 16 interval pairs and outer audit 12 pairs pass; all 9,603 exact-rational profile comparisons pass; all nine all-time inner constraints are strict. The pointwise same-workload ledger covers five windows. Its matched no-service baseline and continuous-polynomial SOCP comparator reproduce. These counts are checks, not statistical sample sizes.

See `PORTABILITY_VERIFICATION.json`, `portability/REPLAY_ENVIRONMENT.json`, `portability/logs/`, and `portability/replay_outputs/` for exact commands, exit codes, bounds, comparisons and results. Regenerated proof/result records agree with the frozen originals after ignoring only runtime fields. The exact command payload and trace reproduce byte-for-byte.

## Historical verification is separate

The 2,476-file historical source tree is not included. Its hash inventory is preserved as provenance. The isolated replay explicitly reports `historical_preservation.available = false`; it does not claim those files were checked. Scientific computations use the included `prior_core/` modules. Import auditing confirmed these scientific imports resolve within the extraction.

The original `QA.json`, `MANIFEST.json` and `ENVIRONMENT.json` are frozen records of the original build, where historical files existed. They remain unchanged. The portable replay's current result is `portability/replay_outputs/QA.json`. The original `verify_package.py` is a scientific result consistency checker, not a manifest-hash checker; use `portability/verify_integrity.py` for hashes.

## Conservative display correction

Read `DISPLAY_ROUNDING_ERRATA.md` alongside the preserved Chinese source prose. Three displayed lower bounds there rounded upward in their last digits. Use ≥1730.659213 J for lower DC slack, ≥0.449999994 W for command slack, and ≥29.999859 W/s for ramp slack. The authoritative exact interval JSON and the verified command payload are unchanged. The source prose remains byte-identical as a historical record.

## Scientific interpretation is unchanged

Under the fixed ideal averaged contract, 808 kvar is constructively feasible with 25 μs critical / 100 μs later holds and exact return at 0.2 s. The outward prefix certificate excludes 812.5 kvar; the documented monotonic argument extends it above that endpoint. Thus the safe supremum notation is 808 ≤ Qsup ≤ 812.5 kvar, with the endpoint itself excluded from feasibility.

“Exact return” refers to rational base commands plus an analytically defined two-block correction. A small displayed endpoint interval is not a finite-precision command-table or hardware guarantee. The recorded 50 and 100 μs negative-margin constructions remain visible and do not themselves prove universal infeasibility at those hold sizes. The earlier floating reset attempt is retained together with the corrected check. This archive adds no switching, robustness, empirical sample-size, novelty, or hardware claim.
