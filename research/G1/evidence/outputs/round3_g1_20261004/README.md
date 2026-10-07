# G1 round 3 research dossier

Start with `G1_THIRD_ROUND_RESEARCH_DOSSIER_ZH.md`. This is new research, not a replacement of frozen round2 evidence. Main outcome: robust recoverable-storage information contracts, a sharp full-family observation-opacity threshold, and strong ordinary delayed/noisy-frequency comparators that limit telemetry-necessity claims.

## Scientific status

- Controller-independent terminal-free prefix lower: E >= .455615336483606, outward interval audited
- Same conventional predictive filter: delayed noisy P upper E <= .353911; delayed frequency error <= .05 upper E <= .372404; common initial stage provided to both
- Same-filter no-later-observation ablation: E <= .472561, explicitly not the best inherited blind upper
- Sharp whole-family prefix opacity radius: 1/(2e), large relative to the .6 frequency band; not an optimal capacity threshold
- Exact sampled-frequency phase recovery has a sample-aligned-edge exception
- 22 frozen nonlinear Kundur runs passed; separate +10% amplitude coarse/fine challenge failed
- Universal Kundur no-feedback lower is non-separating. The 25.85% result is only within a common conventional controller family
- Literature priority is unresolved because the expressly inaccessible Wu/PNNL fulltexts remain missing

## Safe reproduction after closure

This scientific folder is sealed by MANIFEST.json and SCIENTIFIC_CLOSURE.json. Do not run write-capable synthesis, collectors or renderers in the sealed folder. First copy it to a distinct sibling directory under outputs so the declared round2 dependencies remain at the same relative level; run there and compare scientific values, leaving the original bytes unchanged. Never rerun a freeze generator on frozen inputs; the hardened wrapper refuses before writing, and archival provenance snapshots must not be executed.

## Main reproduction

From the workspace root, use `outputs/round2_20261003/andes_env/bin/python`; packages include NumPy, SciPy, mpmath and matplotlib. This existing environment is not redistributed. Set OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, PYTHONDONTWRITEBYTECODE=1 and MPLCONFIGDIR to a writable temporary path.

1. `feedback_baseline/robust_filter.py` builds the P-only witness
2. `feedback_baseline/validate_continuous.py` verifies it and defines recovery
3. `feedback_baseline/frequency_observer.py` builds all-noise frequency detection-history witnesses
4. `feedback_baseline/nominal_sampled_cbf.py` reproduces the failed direct sampled CBFs
5. `feedback_baseline/no_feedback_ablation.py` reproduces the same-method blind ablation
6. `feedback_baseline/test_feedback.py` runs seven implementation QA tests
7. `core/prefix_resource_lower.py` recomputes the exact-phase-envelope outer LP at three cell widths, with raw duals
8. `core/interval_lower_certificate.py` independently encloses the strongest dual's true coefficients and residual correction
9. `core/interval_validate.py` independently encloses every saved upper witness over continuous phase/time and the exact recovery map
10. `core/check_core_evidence.py` checks common SOC, safe printed rounding, detection bounds, resource separation and 127 final round2 source hashes plus 12 classical-baseline files
11. `theory_audit/compute_theory_constants.py` evaluates the auxiliary no-P analytical CBF resource bounds; its separate falsification experiment supplements its proof
12. `core/make_figures.py` renders the three science figures

Do not execute all `core/*.py` indiscriminately: the pair/fixed-quantizer explorers are retained rejected reconnaissance, and the large scenario-tree LP was interrupted after a simpler validated witness made it unnecessary. `EXPLORATION_AND_CORRECTIONS.md` records exact qualifications.

All computation scripts write only the new round3 folder. Saved final policy decimals define the interval-audited inputs. Rerunning a synthesis with a different solver can produce another policy; validate it anew rather than silently treating it as the frozen witness.

## Network reproduction and raw files

Read `network_transfer/REPRODUCE.md` and `METHOD_AND_LIMITS.md`. Network replay requires the already-qualified round2 `kundur_reduced51.npz`, adapter code, installed ANDES 2.0.0 and its pinned official case. These dependencies are named/hash-locked, not copied from an unverified source. The original source license is retained in round2 `grid_transfer/ANDES_LICENSE_GPL3.txt`.

All 24 nonlinear observable traces, canonical load/BESS inputs, received observation records, freeze manifests, failures and fixed coefficients are retained under `network_transfer/`. There are 22 original runs and two separately frozen follow-on runs; repeats and stresses are not independent statistical N. New caches are isolated and excluded from portable evidence archives.

## Evidence levels

1. Analytical theorem/proof: information indistinguishability, step-response opacity, detector-history coverage, continuous candidate reduction, exact moment recovery, auxiliary CBF comparison
2. Outward interval computation: normalized core lower/upper certificates using mpmath.iv; not a formal proof assistant
3. Ordinary-floating analytic certificate: full-order network phase/time/tail and actuator/SOC inequalities
4. Finite original nonlinear replay: unchanged ANDES, individual-machine frequency endpoint, preserved failures
5. No hardware, GPU trace, field measurement, cost savings or end-to-end nonlinear operational guarantee

`MANIFEST.json` gives final hashes and exclusions. `FINAL_RESULT_INDEX.json` and `SCIENTIFIC_CLOSURE.json` provide concise machine-readable outcomes and review paths.
