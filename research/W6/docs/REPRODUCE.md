# Environment and reproduction

Commands assume `cd research/W6` from the repository root, or this handoff root as working directory. Check the root manifest before direct scripts write any outputs.

## Base checks: standard library only

```sh
python scripts/verify_manifest.py
python scripts/run_checks.py --report verification/RECHECK_BASE.json
```

Python 3.10+ is sufficient; tested runtime 3.12.14. The wrapper copies this payload to a temporary directory, compiles authored source, runs 12 quality-validator methods, deduplicated historical rescoring, acquisition-kit tests, parser/gate checks, development-prompt export and payload invariants. No GPU, inference, network, power control or generated-Python execution occurs. The compact rescore reproduces the 108 request-level **derived diagnostics** from four distinct safe output texts and allowlisted stop metadata; it does not reconstruct or independently authenticate original complete host telemetry.

## Scientific environment and small checks

Use an existing environment with `requirements-science.txt`. No installation was performed in this handoff. For a separately authorized fresh environment:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-science.txt
python scripts/run_checks.py --science --report verification/RECHECK_SCIENCE.json
```

Requirements record versions, not complete transitive hashes or a cross-platform lock. Scientific smoke adds full-cycle physical witnesses, signed scalar-swing checks and a 32-mesh guard optimization. The wrapper sets single-thread BLAS and writable temporary caches; changes stay away from frozen evidence.

## Saved full-cycle and network replay

```sh
python scripts/run_checks.py --full-cycle-replay --network-replay --report verification/RECHECK_REPLAY.json
```

The full-cycle replay independently audits saved paths and reoptimizes selected 64-grid convex, 128-box atomic and complete 623-atom empirical-law examples. It is not all-configuration regeneration. Network replay verifies the qualified reduced matrix and four saved linear-transfer kernels, including the high-gain negative baseline. It does not install ANDES or repeat nonlinear/source-model qualification. A numerical replay is not a new independent experimental sample or an interval certificate.

For full regeneration, copy `research/full_cycle` to scratch and run `python code/reproduce.py --full` within the copy. This can take minutes and overwrites that copy's outputs. Compare numeric tolerances, not timestamps; preserve original evidence. Copy `research/grid_memory` before invoking its full study scripts, as they also write outputs.

## Grid-memory component checks

Within a copied `research/grid_memory` directory:

```sh
python review/verify_swing_exact.py
python review/verify_slew_support.py
python review/verify_slew_support_repair.py
python code/slew_support.py
python guard_eval/code/portable_smoke.py
python review/verify_network_transfer.py
```

Complete frozen design/confirmation/executor commands and the separately amended knee-aligned run are in `guard_eval/reports/GRID_GUARD_STUDY.md`. Do not merge the post-confirmation amendment into the original table. `code/kundur_transfer.py` regenerates cached W6 network kernels/results from the retained reduced matrix. Upstream ANDES regeneration requires the separately qualified release, adapter and source-case hash in `docs/DATA_PROVENANCE.md`.

## Quality interfaces

```sh
python continuation/quality/prepare_requests.py --split development --out scratch/development_requests.jsonl
python continuation/quality/validate_outputs.py --help
python continuation/quality/rescore_compact.py
```

The exporter submits nothing and rejects heldout use outside a declared frozen paired phase. The complete benchmark includes answers/tests and must not be sent wholesale to inference. Writing needs blinded human review. Per-record diagnostics cannot establish complete experimental denominators, provenance or treatment compliance. Optional full original-telemetry rescore requires rights-cleared inputs and the import recipe in `docs/DATA_PROVENANCE.md`; it is not necessary for the compact quality-failure reproduction.

## GPU tooling

`gpu_handoff` tests and demo are CPU-only. Optional NVIDIA bindings in its requirements file do not provide drivers, serving engines, weights or physical meter drivers. Configurations are placeholders with operator declarations false. Example wattages are not device recommendations. Live flags, power control and requests need separately verified operator scope; none is run by this check suite.
