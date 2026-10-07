> PUBLIC DERIVATIVE NOTICE (2026-10-07): This is a path-sanitized public copy. Start at ../README.md. PACKAGE_SCOPE and PACKAGE_CONTENTS verify this public derivative; historical scientific manifests refer to the earlier freeze. All mathematical quantities, canonical input CSVs and numerical arrays are preserved. This notice supersedes legacy text about exact original bytes or original absolute paths.

# G1 third-round evidence: compact review package

Date: 2026-10-04 UTC. This archive preserves selected bytes from the sealed third-round research and its independent audit. It is a **compact evidence-review package**, not a complete standalone nonlinear simulation distribution.

## Start here

- `outputs/round3_g1_20261004/FINAL_RESULT_INDEX.json`: machine-readable conclusions and evidence paths
- `outputs/round3_g1_20261004/G1_THIRD_ROUND_RESEARCH_DOSSIER_ZH.md`: original research dossier
- `outputs/round3_g1_independent_audit_20261004/INDEPENDENT_G1_THIRD_ROUND_AUDIT_ZH.md`: independent audit
- `PACKAGE_SCOPE.json`: exact inclusion, omission, duplicate-restoration and old-dependency inventory, with source-relative paths, byte sizes and SHA-256 values
- `PACKAGE_CONTENTS.json`: hashes of all delivered archive entries except itself
- `PACKAGE_VALIDATION.json`: actual fresh-copy validation outcome

The original `MANIFEST.json` and `AUDIT_MANIFEST.json` are unchanged historical records. They deliberately describe more evidence than this compact archive contains. Use `PACKAGE_SCOPE.json` to distinguish included files, exactly recoverable duplicate audit snapshots, omitted raw files, and external dependencies. Do not treat an omitted file as zero or as a successful fresh rerun.

## Exact scope

Included:

- All third-round scientific Python source and all text/JSON/CSV result records, including failed and rejected approaches, pre-endpoint-rounding history, interval duals and policy witnesses, figures, freeze guards, immutable provenance snapshots, and analytical arguments
- All independent-audit unique files; 163 byte-identical audit files are represented by an exact-hash restoration map rather than duplicate payloads
- All 24 nonlinear per-case JSON records and all 72 canonical load, actual BESS power, and received-observation CSVs
- Three representative nonlinear observable NPZs: the matched nominal feedback and open-loop low-start cases at phase 2.347, plus the failed +10% amplitude fine-step case at phase 4.927
- Two corresponding same-input linear NPZs for the matched nominal pair
- The qualified old-round `kundur_reduced51.npz`, unmodified adapter/replay code, upstream GPLv3 license, old provenance lock, and old source-manifest records

Omitted from the compact package:

- 21 of 24 nonlinear observable NPZs and 20 of 22 derived same-input linear NPZs, 41 files / 73,989,634 uncompressed bytes total. Every omitted scientific raw file has its exact path, size, SHA-256 and regeneration route in `PACKAGE_SCOPE.json`
- Runtime caches and bytecode already excluded by the original source manifests. Their on-disk inventory is also recorded in `PACKAGE_SCOPE.json`
- The complete round2 evidence tree, generated ANDES cache, simulator environment and installed upstream source/cases. The package inventories each named old-file dependency used by the full source audit/collection routes. The entire installed environment is not enumerated or bundled

The original count remains 22 finite confirmation runs plus two separately frozen, outcome-informed amplitude challenges. Repeats and stresses are not independent statistical trials. The compact package does not change either count.

## Safe, tested review route

Use a Python environment containing NumPy, SciPy and mpmath. The exact locally tested versions are in `requirements-review.txt`; no environment, executable or automatic installer is distributed. ANDES is not needed for the tested route. No new controller synthesis or nonlinear simulation is run.

1. Extract this ZIP to a fresh directory. Keep the extracted package unchanged.
2. From the extracted `G1_evidence_20261004` directory, verify it using only the Python standard library:

   ```sh
   python verify_package.py
   ```

3. Run the packaged validator, choosing a **new, non-existing absolute directory outside the extracted package**. It creates a disposable working copy, restores only exact-hash audit duplicates, and executes the named checks there:

   ```sh
   export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
   python validate_copy.py --work-dir /tmp/g1-review-copy
   ```

   Do not reuse `/tmp/g1-review-copy` if it already exists; choose a new path. The validator refuses to use the extracted package as its working directory.

4. Read `/tmp/g1-review-copy/VALIDATION_RESULT.json` and `validation_logs/`. The validator checks that the extracted package's included source bytes and modification times remain unchanged.

What this route tests:

- Unmodified outward-interval lower-certificate recomputation from the saved dual
- Unmodified continuous phase/time interval validation of all six saved upper-policy witnesses
- All seven original finite feedback implementation tests
- The unmodified 1,444-case exact network observation-boundary audit, using the included old-round model
- Execution of the hardened freeze wrapper and its expected early refusal; all 78 protected inputs/manifests/controller files retain SHA-256, size and modification time
- Read-only hash verification of all 24 canonical CSV sets and independent reintegration of the serialized BESS command/recovery tolerances
- Read-only reconstruction of peaks from the three included nonlinear traces, including the failed amplitude case

The original `core/check_core_evidence.py`, full `independent_checks.py`, `collect_results.py`, and nonlinear replay are **not** part of this portable test route. Their old source/cache dependencies and the omitted raw traces are not fully supplied. The saved 592-check independent audit is retained as evidence; packaging does not claim to have rerun all 592 checks.

## Frozen evidence and path safety

Never run write-capable synthesis, collectors, renderers, sealers, or freeze generators in the original source tree or the extracted evidence package. In particular, do not run `core/seal_evidence.py` or the archival `network_transfer/provenance/freeze_confirmation_at_v1_freeze.py`. That historical snapshot intentionally predates the hardened guard and is provenance, not an executable reproduction entry point.

The supported freeze-refusal test invokes the current hardened wrapper in a disposable copy with the existing freeze intact. Do not delete a freeze just to make a generator run. New scientific freezes require a distinct versioned project and independently validated controller identity.

Some original records and scripts contain absolute paths under `.`. They are deliberately preserved byte-for-byte. The portable reader interprets stored CSV basenames only within the disposable copy's `confirmation/` directory and verifies their hashes; it never modifies the frozen records or follows them back to the old workspace. Other original scripts may still read or write through absolute paths. Do not execute them indiscriminately in a relocated package.

## Recover omitted evidence exactly

Preferred exact recovery is to obtain each omitted file from its original archived source-relative path, then check the byte size and SHA-256 listed under `omitted_scientific_raw`. Restoring an exact file into a **separate rehydrated copy** is distinct from reproducing a numerical result. The source file hash is an identity check; a new NPZ generated in another environment need not have identical bytes even when its arrays agree.

Audit snapshot deduplication is lossless: each `exact_hash_duplicate_restore_map` entry names `restore_from`, the destination path, byte size and SHA-256. `validate_copy.py` restores these only in its new copy. Unique historical snapshots, changed audit outputs and changed source versions have not been merged.

## Full nonlinear regeneration: dependencies and known blockers

Full replay remains outside the tested portability claim. Before attempting it in a distinct, versioned replay workspace:

1. Recreate/provide the qualified round2 ANDES 2.0.0 runtime with all its dependencies, its unchanged official `kundur/kundur_full.xlsx`, and generated cache expected at `outputs/round2_20261003/grid_transfer/home`. The included source uses `andes.get_case` and does not consume a copied arbitrary case workbook. Verify upstream source/case hashes against `network_transfer/EXECUTION_ENVIRONMENT_LOCK.json` and the included old provenance lock. An arbitrary new ANDES installation is not automatically the qualified environment.
2. Restore the external old-round files named in `PACKAGE_SCOPE.json` when running the full old-integrity audit or collection commands. `core/check_core_evidence.py` checks 127 old manuscript sources plus 12 classical-baseline files; `collect_results.py` and the full independent audit check 266 old source/cache/environment files. These whole routes cannot pass from this archive alone.
3. Resolve absolute paths intentionally in the replay workspace, without writing into or disguising the sealed source. Either use a correctly isolated environment with the original expected directory layout or document a replay-only relocation layer. Keep the frozen manifests unchanged; if a separate working manifest is needed, retain its mapping and new hash and do not call it the original freeze. Such full replay relocation has not been implemented or tested by this packaging task.
4. The saved successful per-case JSON causes `replay_pwl_storage.run` to resume-skip even when its NPZ is absent. In the replay copy only, move the case's copied JSON/NPZ output pair into a backup folder before regenerating it. Do not touch frozen source records or canonical input files.
5. For original cases use `run_confirmation.py --start INDEX --stop INDEX_PLUS_ONE`, with the exact case index in the omitted-file inventory. For the amplitude addendum use `run_amplitude_addendum.py` **without `--freeze`**. Read the original `network_transfer/REPRODUCE.md` and `METHOD_AND_LIMITS.md` first. These commands are preparation guidance, not a claim that the compact package can already execute them.
6. After all required nonlinear traces and old locked files are available, `collect_results.py` reconstructs the original cases' linear traces. It writes results and must only run in the replay copy. The original late +10% cases remain a separate addendum.

Running a new synthesis can produce a different degenerate LP optimum under a different solver or environment. Any changed controller must be validated anew and cannot inherit the original frozen confirmation identity. No new scientific experiment was performed while making this archive.

## Scientific claim boundaries

The archive supports the narrow normalized-core resource separation and the finite network evidence exactly as qualified by the source and independent audit. It does not establish a universal nonlinear network theorem, robust operation at +10% amplitude, telemetry necessity against the strong delayed-frequency comparator, hardware savings, or a resolved literature-priority claim. Read the preserved failure records and source-access limitations alongside positive results.
