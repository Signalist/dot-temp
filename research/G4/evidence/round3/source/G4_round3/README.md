# G4 round 3: workload-constrained lossy common-output capacity

## Start here

- `report/G4_ROUND3_DOSSIER_ZH.md`: complete Chinese scientific dossier and publication-level verdict
- `theory/THEOREMS.md`: full mathematical contracts and proofs T1–T6, T1a and T5a
- `validation/INDEPENDENT_THEORY_REVIEW.md`: adversarial independent review, exact positive-width equality witness, assumption failures
- `literature/G4_DAG_CORRELATION_LEAKAGE_PRIOR_ART_AUDIT.md`: precise primary-source comparison
- `FINAL_SCIENTIFIC_STATUS.json`: machine-readable closure

## Strongest result

For a finite family of two-level task words, independently admissible across blocks, fixed compact polyhedral common-output constraints inside the task power range, a common freely selected initial state, and no state leakage/disposal, the minimum capacity over every infinite (possibly nonperiodic) public output schedule is exactly the one-block all-word exact-reset LP optimum B_S*. Any accumulated endpoint width costs additional capacity: B≥B_S*+W∞. DAG slot-swap geometry makes this optimum explicit in the connected case. The leaky discrete analogue is a stationary invariant-interval LP, also exact among arbitrary nonstationary common schedules under the same affine assumptions.

This is a workload-dependent specialization using standard LP, graph and robust-reachability tools. It is not a new source locator or a claim of performance superiority over matched-information LPs.

## Reproduce

From the handoff root, use the isolated wrapper described in the root README:

```sh
python3 evidence/round3/tools/replay.py --mode exact --output ../g4-exact-run
python3 evidence/round3/tools/replay.py --mode full --output ../g4-full-run
```

These publication-safe commands supersede the original private-environment commands. The root manifest tracks sanitized files; original manifests remain provenance.

The first two scripts optimize finite synthetic models and reconstruct exact rational certificates. The saved-certificate checks do not optimize. The independent certificate checker imports no producer code. `check_saved_certificates.py` also checks all 114 entries in the existing round-2 source manifest; it requires that historical directory. No historical source is rewritten.

Python environment: 3.12.14; NumPy 2.3.5; SciPy 1.17.0; SymPy and Matplotlib required. Seeds and every DAG, label, efficiency, LP solution, exact primal/dual witness, and outcome are saved in JSON. Fraction certificates are exact for the declared rational models. Finite-horizon and retained-state LP results are floating-point and labeled accordingly. No simulator, live hardware, proprietary workload, external account, or paid service is needed.

## Files and evidence levels

- 77 primary DAG/loss configurations: `experiments/dag_results.json`, `.csv`
- 12 public graph-shape/synthetic-power transfer configurations: `experiments/boundary_results.json`
- 21 finite-horizon problems (three families, K=1,...,64): `experiments/finite_horizons.json`
- 9 discrete-retention configurations: `experiments/leakage_results.json`
- 5 exact ideal-efficiency comparisons, 5 exact cyclic PCC-step ablations, exact correlated-history witness and disposal counterexample: `experiments/boundary_results.json`
- 89 exact producer primal/dual certificates independently checked
- Independent tiny-model suite: 948 DAG/label row-space checks, 168 connected-case LP checks, 23 small word families at four horizons, 169 leaky fixed-output checks, 90 weighted-invariance threshold checks

These counts are model configurations and algebraic checks, not independent physical samples. Some differently labeled graph constructions project to identical power languages. Public-pattern transfer reconstructs only Task Bench mathematical predecessor relations; no Task Bench runtime/code or measured power is used.

## Source and historical integrity

`literature/SOURCE_LEDGER.json` identifies source URLs, exact sections and access limits; its own `MANIFEST.json` hashes readable local source snapshots. Full downloaded source papers and extracted text remain local research inputs. The user-facing core evidence ZIP excludes them and supplies official/author links instead.

`SCIENCE_MANIFEST.json` hashes new scientific deliverables. The old round-2 114-file manifest was checked without mismatch. A core evidence archive contains the reports, theory, code, exact certificates, source ledger, original-work figures and checks. It excludes caches and full third-party texts. All downloaded-source limitations remain in the ledger rather than being concealed.

## Scope stopping condition

The specified-model theorem, matched-information baseline, task-structure transfer, leakage/correlation/disposal boundaries, independent review and source-integrity closure are complete. No empirical AI power attribution, actual converter bandwidth, continuous leakage certification, measured scheduler cost, or real grid deployment claim has been established. High originality/priority remains unproved.
