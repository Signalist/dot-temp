# G6 Reproduction

All commands start at the handoff root (research/G6 after publication). Tested reference: Linux, CPython 3.12.14, NumPy 2.3.5, SciPy 1.17.0, mpmath 1.3.0, pandas 2.2.3, Matplotlib 3.10.8. g++ with C++17 and OpenMP is required for the actual network DP backend. The handoff contains source, not a precompiled binary.

```sh
cd research/G6
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python verify.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python replay.py --mode quick --work-dir ../../g6_quick_new
OPENBLAS_NUM_THREADS=1 .venv/bin/python replay.py --mode synthetic --work-dir ../../g6_synthetic_new
OPENBLAS_NUM_THREADS=1 .venv/bin/python replay.py --mode network --work-dir ../../g6_network_new
OPENBLAS_NUM_THREADS=1 .venv/bin/python replay.py --mode round2 --work-dir ../../g6_round2_new
```

Dependency installation is a recipe, not a newly tested isolated install. Every work directory must be nonexistent and outside the handoff. Default execution makes no external request. Each mode writes logs and REPLAY_RESULT.json in its work directory. Read explicit tested/not-tested flags in validation/HANDOFF_QA.json.

- verify checks current public bytes only
- quick compiles the actual window_dp.cpp and checks 33 deterministic small reward rows against exhaustive legal words; runs the earlier synthetic model unit tests, second-round theory checks, and third-round orientation/DAG source
- synthetic regenerates the 135 floating cases, exact rational parameter enclosure/raw integer grid, 12 orientation cases and 128 DAG checks
- network reconstructs compact modal kernels into approximately 278MB coefficient arrays, runs the original 30-row DP/LP producer, and compares four primary numeric columns to archived values at absolute error below 1e-9
- round2 executes seven selected mathematics/structure/audit/stochastic scripts, without a simulator. It is separate from network reconstruction

Original round3 `src/reproduce_network_contracts.py` refuses existing scratch and compiles `contracts/window_dp.cpp` with `-O3 -std=c++17 -fopenmp -shared -fPIC`. The small backend test uses -O2 and the same C++17/OpenMP source. Keep generated .so files, pycache and scratch outside publication. Mac/Windows/OpenMP toolchains are not tested.

## Larger historical workflows are reference-only

The original producer/audit scripts needing the full prior directory, omitted ~267MiB tensors, original simulator code generation or omitted raw nonlinear traces are not certified standalone entry points. The supported network wrapper reconstructs only its necessary coefficient tensors from included compact frozen kernels. Original round1 raw archive transport/reassembly and packaging tools are excluded; raw nonlinear states from that generation are not present. Second-round input schedules and result JSON preserve the negative outcomes, but absent full raw trajectories cannot be re-audited as if present.

Full ANDES reproduction requires the pinned official andes==2.0.0 distribution and its original case workbooks, compatible generated model code and qualification sequence. Use provenance/fetch_upstream_cases.py only to retrieve and checksum original public workbooks; downloading is not qualification. The old nonlinear runners expect a qualified grid-transfer layout and an ANDES generated-code directory. Those dependencies are not silently substituted or claimed available. Existing `complete` JSON can cause a historical runner to skip an old case; such a skip is not a new nonlinear integration.

No new nonlinear network integration, independent source-DAE qualification, real compute-power calibration, fresh dependency installation, full family-wide nonlinear certificate or physical-grid test was performed for this handoff.

Scientific reference checker `evidence/round2_g6_joint_admission_20261003/audit/verify_final_report.py` is retained unchanged. It independently checks the main report tables, LTI bounds, nonlinear peaks and voltages against complete raw trajectory arrays. Those raw trajectories are not all in this compact handoff, so this checker was not rerun and must not be described as passing here. Obtain and verify its stated inputs before use; do not replace missing arrays with summaries.
