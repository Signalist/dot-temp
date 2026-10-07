# G2 Reproduction

Commands are relative to the handoff root, deployed as research/G2. Python 3.12.14 on Linux was used; reference pins are in requirements.txt. No ANDES installation or network request is needed to run from the included reduced matrix.

```sh
cd research/G2
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python verify.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python replay.py --mode diagnostics --work-dir ../../g2_diagnostics_new
OPENBLAS_NUM_THREADS=1 .venv/bin/python replay.py --mode full --work-dir ../../g2_full_new
```

Installation commands are recipes, not an assertion that a fresh package-index install was tested here. Each work directory must not exist. Use a different name for each retry. The scripts write only the copied evidence; the root source and results remain unchanged.

Full stages: literature/verify_reductions.py; experiments/matched_support_baselines.py; experiments/matched_arc_budget.py; audit/verify_matched_support.py; experiments/jerk_compression.py; theory_worker/verify_theory.py; audit/verify_jerk_audit.py; experiments/network_structure_transfer.py. Diagnostics mode selects five diagnostic stages but does not rerun baseline optimizations/compression. All stage paths begin with outputs/round3_g2_20261004 inside the fresh copy.

The wrapper checks original scientific assertions and compares generated JSON with archived results at rtol=1e-7, atol=1e-12 (wall-time fields ignored), and compares the generated kernel arrays. Those tolerances do not certify the sign of tiny gaps. The analytical lower bound, not floating regression tolerance, supports the asymptotic claim.

Results and logs go to the selected work directory. Handoff-time testing is in validation/HANDOFF_QA.json. No fresh simulator run, independent benchmark matrix qualification, nonlinear network integration, real hardware measurement, cross-platform test or full 896-file historical audit is claimed. The two source lineage scripts grid_adapter.py/qualify_ports.py are references to the upstream qualification workflow, not part of the default replay. Their fuller historical dependencies are not all included.
