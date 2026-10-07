# Reproduction and array schema

This directory contains one physical condition at two numerical step sizes. All parent sources, protocols, baseline data and checkpoints are read-only inputs.

Run from any working directory, with Python, NumPy, SciPy and Matplotlib available:

1. `PYTHONDONTWRITEBYTECODE=1 python run_abc.py --h 1e-5`
2. `PYTHONDONTWRITEBYTECODE=1 python run_abc.py --h 5e-6`
3. `PYTHONDONTWRITEBYTECODE=1 python compare_and_report.py`
4. `PYTHONDONTWRITEBYTECODE=1 python plot_window.py`
5. `PYTHONDONTWRITEBYTECODE=1 python validate_outputs.py`
6. `PYTHONDONTWRITEBYTECODE=1 python compare_and_report.py` to include all generated files in the final manifest

Use the full path to each script if outside this directory. The saved execution logs are `run_10us.log` and `run_5us.log`. No step invokes a DQ runtime controller, allocator or integrator.

## Raw arrays

Each abc NPZ has named column arrays for `trace`, `control`, `sample_before` and `sample_after`. The physical state is ia/ib/ic, Wdc, Pbat and Ebat, followed by seven non-feedback energy-integral diagnostics. All scalar/complex-part held controller values are saved without normalization in the sample arrays and every trace row.

`trace.phase` codes:
- 0: immediately before the control update, measuring the old applied command
- 1: immediately after the control update and queued-command promotion
- 2: start of a fixed-source integration segment, including the right-hand side of a source discontinuity
- 3: completed RK4 substep or located terminal event

Duplicate timestamps intentionally retain different sides of a sample or disturbance. Do not deduplicate them without considering `phase` and `source_pu`. The only NaN is the last reference at the first pre-update row: it was absent from the source checkpoint, has no feedback role, and becomes known at the immediately following sample.

`normalized_before/after` are [time, id/Ipeak, iq/Ipeak, Wdc/Wref, Pbat/1MW, thetaPLL−omega0*t, zPLL/omega0, zi_d/Vpeak, zi_q/Vpeak, applied_d, applied_q, queued_d, queued_q, omegaPLL/omega0, source_command/1MW], with modulation rotated into the nominal source frame. Ebat and diagnostic integrals are deliberately excluded from this periodic-orbit normalization, but are included in the raw arrays and independently preserved/checked.

`control` saves the measured pre-update quantities, raw/limited allocation, PLL error/raw/new frequency, current error, uu/us, Ki terms and current-voltage antiwindup terms. `same_window_control_snapshots.csv` is the complete 21-sample export, not a subsampled curve. Key sample excerpts appear in COMPARISON.json.

`dq_saved_state_diagnostics.npz` is a read-only reconstruction from the original saved DQ arrays. It contains no new DQ integration. Reconstructed post-update values use the next endpoint's held state with its angle advanced back to the sample time; identities verify queue promotion and PI/PLL updates.

`diagnostic_window.png` displays the observed window. `REPORT_ZH.md` explains the conclusion and limits. `VALIDATION.json` records schema and consistency checks. `MANIFEST.json` binds all delivered file bytes and source-input hashes.
