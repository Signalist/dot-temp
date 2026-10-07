# G4 bounded-buffer source-identifiability research

Read `report/G4_RESEARCH_REPORT_ZH.md` first. Full mathematical proofs are in `theory/`; exact rational feasibility/infeasibility certificates are in `validation/`; primary-source novelty audit is in `literature/`.

This is mathematical and synthetic model evidence. No real AI-PCC-PMU coupled measurement, no new universal localization algorithm, noAI-label inference, no paid compute is claimed.

## Reproduction

From workspace root with installed NumPy/SciPy/SymPy:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python outputs/round2_g4_identifiability_20261003/experiments/recovery_frontier.py
python outputs/round2_g4_identifiability_20261003/experiments/causal_horizon_design.py
python outputs/round2_g4_identifiability_20261003/experiments/fixed_initial_compare.py
python outputs/round2_g4_identifiability_20261003/experiments/dag_equivalence.py
python outputs/round2_g4_identifiability_20261003/experiments/smooth_dag_pair.py
python outputs/round2_g4_identifiability_20261003/experiments/timing_ablation.py
python outputs/round2_g4_identifiability_20261003/experiments/measurement_ablation.py
python outputs/round2_g4_identifiability_20261003/experiments/heldout_transfer.py
python outputs/round2_g4_identifiability_20261003/experiments/two_site_measurement_design.py
python outputs/round2_g4_identifiability_20261003/experiments/grid_service_decision.py
python outputs/round2_g4_identifiability_20261003/validation/exact_dual_certificate.py
python outputs/round2_g4_identifiability_20261003/validation/exact_feasible_witness.py
python outputs/round2_g4_identifiability_20261003/validation/integrate_smooth_witness.py
python outputs/round2_g4_identifiability_20261003/theory/independent_theory_checks.py
```

Grid-transfer commands and unchanged qualified source paths are specified in `experiments/grid_transfer/REPORT.md`. No import from old grid adapters is needed; the new script reads only locked NPZ inputs. Prior scientific files must remain unchanged.

The older G4 archive is not redistributed in this core package; its original hashes and omission reasons are indexed in the package-root SCIENTIFIC_OMISSIONS.json. The historical summary remains in `recovery/OLD_G4_INDEX_EXTRACT.json`. The initial protocol and prospectively timestamped additions record the narrowing from classical ideal results to the loss–tolerance question. `validation/retained_failures/` preserves the unsegmented ODE check that failed before boundary-resolved integration.

## Scope of the strongest outputs

-4/5block exact separation concerns hiding **all** task orders in one common PCC trace
-2^K residual DAG/pair task histories can still share a fullPCC trace indefinitely
-SOCquery helps that specified task label; it is extra information, no optimizer or cost superiority
-Infinite-horizon bound2Q+W∞ holds in the declared no-leak, no-shunt two-level contract
-Grid single-/two-channel phasor checks are classical measurement geometry, with explicit nuisance/noise and model limits

## Public package navigation

Start at the package-root README_ZH.md or index.html. The current G4 grid-transfer reruns have all 11 locked dependencies bundled at their original relative path; rebuilding the earlier ANDES qualification is outside this package. Nested source manifests describe the original frozen files; use PUBLIC_PACKAGE_MANIFEST.json and SHA256SUMS.txt at the package root to verify the public copies.
