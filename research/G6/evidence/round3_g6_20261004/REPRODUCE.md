> Historical scientific document. Use the handoff root README.md and REPRODUCE.md for current execution commands and dependency limits. Historical hashes/complete-workspace statements are not current handoff verification.

# G6 round-3 reproducibility

## Scope and files

- `report/G6_ROUND3_DOSSIER_ZH.md`: main scientific decision and interpretation
- `theory/THEOREMS.md`: complete T1–T5 proofs, including T2a and T3a
- `literature/`: theorem-level prior reductions and exact reading-status ledger
- `experiments/`: ordinary sensitivity data, exact rational enclosure and all raw grid integer intervals, synthetic orientation/DAG data
- `contracts/`: full primary/secondary network contract data, maximizers, schedules, energy ledger, source code and independent audit
- `validation/`: independent skeptical theorem/implementation review and independent tests
- `inputs/`: small frozen qualified modal kernels and existing derivative/tail support fixtures; original source hashes retained

No original round-2 file is modified. No new nonlinear integration is performed. A numerical modal kernel is a conditional model, not an exact original-network interval enclosure.

## Environment

Development used the already available Python at `outputs/round2_20261003/andes_env/bin/python`, with numpy, scipy, mpmath and matplotlib. The primary contract producer compiles its included original C++ source using `g++ -O3 -std=c++17 -fopenmp`; it requires no downloaded software. Do not install anything merely to execute these commands; use a suitable existing environment.

## Standalone synthetic results

From this directory:

    OPENBLAS_NUM_THREADS=1 python src/run_finite_uncertainty.py
    python src/run_orientation_and_jobs.py
    MPLCONFIGDIR=/tmp/g6_matplotlib python src/make_figures.py

The first script independently creates the exact rational parameter certificate. It uses only Python exact integers/Fractions for that enclosure; the broad sensitivity sweep uses ordinary double precision. The optional 180-digit validation uses mpmath as a diagnostic, not as the basis of the exact enclosure.

## Portable network-contract replay from compact fixtures

The archived `inputs` contain about 550KB of frozen kernels and analytic error components. The original coefficient tensors are about 267MiB and are intentionally regenerated rather than shipped. Run:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 python src/reproduce_network_contracts.py --scratch /tmp/a_new_g6_replay_directory

The named scratch directory must not exist. The replay creates the expected sibling folder layout, reconstructs every 2049-phase/257-lag two-port tensor from the compact kernels, executes the unchanged primary DP/LP/enumeration producer, and checks all 30 primary support/amplitude rows against archived references. Allow about 300MB scratch plus working memory. It writes `REPLAY_RESULT.json` in the scratch directory. The validated original portable replay result is retained under `experiments`.

This portable route replays the conditional-kernel results without the original simulator or the hundreds of megabytes of historical raw coefficient files. It does not independently requalify the original DAE-to-modal mapping or reproduce old nonlinear runs. That broader historical evidence remains in the preserved round-2 archive.

## Full original-workspace audits

When the old source directory is still available at its original sibling location:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 python contracts/run_contracts.py
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python validation/independent_review_checks.py
    OPENBLAS_NUM_THREADS=1 python contracts/independent_audit.py

These original audits intentionally compare the independent source models, stored source tensors, raw word schedules, and original provenance hashes. Do not substitute the portable generated tensors and call that a fresh source-model qualification.

## Evidence accounting

135 synthetic grid rows, 129 exact grid nodes, 30 primary network configurations, 2 post-primary window-shape configurations, and the many audit checks are different numerical objects. They are not independent physical experiment samples. The new nonlinear run count is zero.

Kundur retains 50MW positive compute baseline per port but nominal voltages near .945/.949pu. WECC supplemental compute baselines remain zero and its old nonlinear inner witness about .05310Hz still fails the .05Hz threshold. Every new network capacity number is total zero-mean fluctuation amplitude, not average hosting.
