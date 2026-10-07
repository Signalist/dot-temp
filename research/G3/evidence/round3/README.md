# G3 third-round reproducible research

Read `G3_THIRD_ROUND_RESEARCH_DOSSIER_ZH.md` first, then `theory/PREFIX_COUPLED_CERTIFICATE.md` and `review/INDEPENDENT_SUPPORT_REVIEW.md`.

## Supported result

Within the unchanged ideal averaged physical contract, 808 kvar is feasible with a 25/100 microsecond zero-order-held battery command and exact0.2s recovery. Every amplitude at or above812.5 kvar is excluded by an outward-checked all-allocation prefix certificate. Safe supremum notation is808<=Qsup<=812.5; the endpoint itself is excluded. This replaces the former834.41453 upper certificate and reduces the bracket width by82.9639%.

The new exclusion needs neither terminal recovery nor a late recharge energy budget. It couples the cumulative loss of grid net delivery to temporary inductive-energy release. It does not claim a new general convex solver, AI-specific mathematics, or a switching/hardware result.

The held-command inner has an exact real-valued definition: decimal rational base commands plus an analytically defined two-block correction. Its near-zero endpoint interval is not a finite-precision hardware guarantee. Known fixed parameters and ideal averaged AC actuation remain assumptions.

## Reproduce in a copy

Python3.12 and `requirements.txt`. Source copies in `prior_core` are exact copies of the old model/tool modules and cited old theory; no old installed environment is needed. Internet is not needed to reproduce scientific numbers.

    python -m venv .venv
    .venv/bin/pip install -r requirements.txt
    .venv/bin/python src/zoh_inner.py
    .venv/bin/python src/certify_zoh_inner.py
    .venv/bin/python src/certify_matched_baseline.py
    .venv/bin/python src/certify_prefix_interval.py
    .venv/bin/python src/account_and_ablate.py
    .venv/bin/python src/check_lag_counterexample.py
    .venv/bin/python review/independent_coupled_numeric.py
    .venv/bin/python review/check_interval_export.py
    .venv/bin/python review/check_zoh_inner.py
    .venv/bin/python review/check_exact_zoh_certificate.py
    .venv/bin/python review/check_profile_rationals.py
    MPLCONFIGDIR=.cache/g3_mpl .venv/bin/python src/make_figures.py
    .venv/bin/python src/verify_package.py

Optional `src/explore_coupled.py` repeats the exploratory local search. This is not required for either frozen certificate; its numerical root is not the certified outer threshold. Solver versions may change an optimizer's chosen held trajectory, but the saved exact payload and interval verification do not depend on reoptimizing.

To check the shipped exact payload rather than regenerate it, use `review/check_exact_zoh_certificate.py` and `review/check_profile_rationals.py`. `certify_zoh_inner.py` deterministically reconstructs the rational base from the shipped LP NPZ and the documented repair, then validates it.

## Artifact semantics

- `PROTOCOL.json` is an exploratory research/verification plan, not a preregistered blind campaign
- `results/outward_prefix_certificates.json`: final literal interval bounds, lambda0
- `results/outward_zoh_inner.json`: repaired all-time interval proof and exact-return definition
- `results/zoh_q808_exact_payload.json`: complete rational command payload and repair rule
- `results/same_workload_energy_ledger.json`: per-window signed, positive, absolute and W/B/Z accounting at identicald(t)
- `results/mature_socp_comparator.json`: reproduced mature continuous-polynomial SOCP baseline
- `results/zoh_inner_results.json`: all three held-grid attempts, including failures
- `results/ablation_results.json`: prefix-coupling mechanism ablations, floating point
- `results/finite_parameter_reset_counterexample.json`: finite parameter corners can reset while an interior lag does not; generic pure-lag illustration
- `literature/ROUND3_PRECISE_COMPARISON.md`: exact prior-art boundaries and newly found September2026 near-neighbor/full-text gap
- `SCIENTIFIC_CLOSURE.json`: completed/open claims and exact evidence map
- `QA.json`, `MANIFEST.json`, `SOURCE_LEDGER.json`: reproducibility and provenance

## Important nonclaims

The outer relaxes away current, inventory, upperDC and recovery constraints; it remains necessary for the more constrained model. The inner retains all of them. Larger late recharge cannot repair the prefix violation, but that does not make808 robust to the declared slower-port box.

The old600kvar34-run finite-tolerance PWM campaign is a different contract and is not rerun or overwritten. This package does not prove an instantaneous finite-switching cap/floor or exact switching-orbit restoration. The no-service comparator is feasible load following, not an optimal no-service counterfactual. All task-energy equality is pointwise workload equality, not merely equal integrals.

Historical second-round hashes are retained in `HISTORICAL_SOURCE_FREEZE.json`; when that sibling tree is available `verify_package.py` checks it read-only. An exported standalone copy reports that optional historical tree as unavailable rather than falsely claiming its verification.
