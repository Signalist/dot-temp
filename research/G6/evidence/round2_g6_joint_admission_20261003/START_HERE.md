> Historical scientific document. Use the handoff root README.md and REPRODUCE.md for current execution commands and dependency limits. Historical hashes/complete-workspace statements are not current handoff verification.

# G6 mobile core evidence / G6 轻量科学证据包

## Start here / 阅读顺序

1. `reports/READINESS_SUMMARY_ZH.md` and `reports/G6_FULL_REPORT_ZH.md`: conclusions and limits
2. `theory_review/G6_STRUCTURAL_AND_COMPLEXITY_PROOFS.md`: theorem statements and proofs
3. `audit/INDEPENDENT_PROOF_AUDIT.md`: separately implemented internal audit; not external peer review
4. `reports/ASSUMPTION_AND_HYPOTHESIS_LEDGER_ZH.md`: quantifiers, assumptions, and scope
5. `literature/PRIMARY_SOURCES.json`: primary-reference metadata and verification depth
6. `positive_workpoint/POSITIVE_WORKPOINT_REPORT.md` and `nonlinear/G6_ORIGINAL_NONLINEAR_REPORT.md`: finite nonlinear outcomes, including the failures

This is a cleaned, portable **core evidence subset**, not the full raw dataset, a self-contained ANDES installation, or a publication-readiness certificate. No real measured compute-to-grid calibration was added. Mathematical proofs, ordinary-floating LTI calculations, and finite nonlinear trajectory checks have different evidential strength. A passing finite replay never establishes whole-family nonlinear safety.

本包包括数学、代码、小型数值结果、冻结协议、逐例JSON/CSV、见证输入、核/支撑数组、审查、图和文献元数据。完整系数张量和30条非线性原始轨迹不在本包；精确文件名、字节数及SHA256见省略清单。不要把轻量复核、线性重建、全网络非线性重放混为一谈。

## Package provenance

- `PUBLIC_MANIFEST.json`: SHA256 of every other packaged file; verify this before running
- `SOURCE_TO_PUBLIC_SHA256.json`: original relative paths and original SHA256 → public copy path and SHA256, with every transformation identified
- `OMITTED_SCIENTIFIC_FILES.json`: large original arrays/traces and redundant replay-validation copies omitted from the core
- `EXTERNAL_DEPENDENCIES.json`: legacy source/data requirements, official ANDES source/case identities and hashes; full installed ANDES file index; runtime dependencies
- `PACKAGE_QA.json`: exactly which package checks were run, and which were not
- `FINAL_SOURCE_FREEZE.json` and other final scientific manifests, when present: source-side scientific freeze; their embedded hashes refer to the original scientific files

The original scientific files were not edited. Cleaning strips the original workspace prefix from documentary paths, omits nonscientific operational/coordination wording, clarifies full-source versus subset availability, and localizes generic figure-cache paths in two copied plotting scripts. Original hashes embedded inside scientific records remain untouched and refer to original scientific bytes, not sanitized public copies. Use the original→public mapping to interpret this deliberately preserved distinction. In particular, do not treat a recorded source-integrity Boolean as a fresh check of the cleaned bundle. Public paths beginning `outputs/` are logical original-layout paths, not a disclosure of an execution host.

Logs, execution caches, in-progress drafts and unrelated private material are excluded. Final source manifests may name excluded files: naming/hash metadata is not inclusion. Primary-reference PDFs and the ANDES installation are not bundled. The dossier DOCX/PDF is delivered separately, if supplied.

## Level 0: verify package bytes

From the extracted `g6_core` directory:

```sh
python portable_recheck.py verify
```

Uses the Python standard library. This checks bytes, not scientific correctness.

## Level 1: lightweight mathematics and numerics

Requires Python 3.12 plus NumPy, SciPy and mpmath. The tested versions are recorded in `PACKAGE_QA.json`; matplotlib is needed only to regenerate figures. No network download or ANDES model is needed for these seven scripts.

```sh
python portable_recheck.py light --workdir ../g6_light_recheck
```

Choose a new empty directory outside the extracted package. The wrapper copies the evidence to a disposable original-layout workspace, verifies the package, and runs structural, dynamic-optional, shared-parameter, face-budget, theory, independent-mathematics and exact finite-state stochastic checks. Some scripts rewrite results and a protocol timestamp **only inside that working copy**. `RECHECK_RESULT.json` there records exit status and runtime. Inspect its full outputs; command success is not a formal proof.

## Level 2: rebuild linear public-model evidence from included fixtures

```sh
python portable_recheck.py linear --networks kundur wecc --workdir ../g6_linear_recheck
```

Uses the included qualified numerical fixtures and original support implementation. It does not reload or requalify an original ANDES network. It reconstructs omitted coefficient arrays and writes fresh linear results inside the new workspace; allow several hundred MB of disk and memory. The wrapper compares regenerated numerical arrays and coefficient hashes with the frozen originals. Cross-platform floating arithmetic can differ; the package QA only describes the observed environment, not universal bit identity.

To rebuild the positive-workpoint support tensor, use another copy in the same original layout and run `positive_workpoint/run_positive_support.py`. Its qualified positive kernel, witnesses and supporting qualification data are included. This command does not perform a fresh nonlinear workpoint qualification. The packaging test also rebuilt this positive-workpoint support tensor; see `PACKAGE_QA.json` for the observed comparisons.

## Level 3: full network qualification and nonlinear replay (dependency-gated)

This core does **not** claim standalone full replay. Required external dependencies and exact recorded hashes are in `EXTERNAL_DEPENDENCIES.json`: ANDES 2.0.0, the exact Kundur/WECC official case spreadsheets, compatible numerical runtime, and generated ANDES model code. The legacy adapter, provenance lock, chain-rule audit and upstream license text are included under `dependencies/legacy_grid_transfer/`; numerical legacy fixtures are under `inputs/`. The old runtime and generated caches are excluded; reconstructing them was not tested as part of packaging. Obtain upstream software from its official sources and preserve applicable notices; no automatic installation is performed by this bundle.

For a full replay, create an isolated original-layout workspace (`outputs/round2_g6_joint_admission_20261003` alongside `outputs/round2_20261003/grid_transfer`). Populate legacy fixture and adapter files from this package and configure the external ANDES environment/caches. Follow `README_REPRODUCE.md` and `positive_workpoint/REPRODUCE.md`, treating the historical interpreter path as a logical layout example. Check case SHA256 before simulation.

**Cache caveat:** original replay scripts skip a case when its per-case JSON says `complete`. For a genuinely fresh replay, in the disposable copy move the 20 `nonlinear/*_dt*.json` and 10 `positive_workpoint/*_dt*.json` result files aside before executing, while retaining frozen protocols, case selections and `_input.npz` files. Otherwise the command can merely reuse recorded outcomes. Keep new results separate from the original records. Sanitized documentary-path/summary hashes require comparing via the supplied original→public mapping rather than blindly rerunning original source-integrity checks. Recreating exact historical source-integrity manifests is not supported from cleaned copies alone.

The old workpoint replay runs 65 blocks with an explicitly LTI-only truncation bound; the positive Kundur replay runs all 257 blocks plus ringdown. Do not substitute nominal grids for actual solver/event times. To audit already-recorded nonlinear metrics directly, obtain the omitted traces by exact hash and restore them in a disposable copy; the core summaries alone cannot repeat raw-trace audits.

## Scientific stopping point

The bounded route and targeted internal audits can be complete while paper readiness and standalone high innovation remain unestablished. Keep all negative outcomes and scope restrictions when reusing these materials. The source freeze is a local research-process freeze, not a third-party preregistration; targeted reference checking is not exhaustive novelty certification.
