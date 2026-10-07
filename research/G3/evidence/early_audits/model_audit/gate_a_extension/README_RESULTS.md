# Independent abc Gate A extension results

New experiments, 2026-10-02. Authoritative scored results: `authoritative_summary.json`; original raw files remain unchanged in `results/`. Frozen extension SHA256: `a1c399415c6a4b8d17ccf6193963ed73b712fca0890856fbbbf9dcfe1af6bdb8`.

## Findings

| Condition | Internal step | Actual current peak | DC maximum | Outcome |
|---|---:|---:|---:|---|
| Remote source retained 0.85 pu, 150 ms | 10 us | 0.949707634737 pu | 1.012410284156 pu | All specified actual limits passed; electrical/control state recovered at 1.30 s |
| Remote source retained 0.475 pu, 150 ms | 10 us | 0.984102355163 pu | 1.10 pu boundary | DC-boundary stop at 0.606023482181501 s, before clearance |
| Same 0.475 pu case | 5 us | 0.984102355163 pu | 1.10 pu boundary | Same event at 0.606023482181501 s |

All three start from the complete independent abc checkpoint at 0.6 s; the source change starts at 0.60005 s and would clear at 0.75005 s. The 0.85 run actually continues through 2.75005 s, two full seconds after clearance. Its formal electrical/control recovery delay is 0.54995 s. The current-reference limiter is observed to release at 0.7501 s. Other formal limiters never activate. The frozen conditional refinement threshold is not reached for this case, so no extra 5 us run was performed.

The 0.475 test reaches the DC upper boundary only 5.9734821815 ms after onset. Its observed prefix remains within limits up to roundoff at that boundary; this is not a completed safe trajectory. Clearance, limiter release and recovery are unobserved. No state projection, protection reset or continuation past the modeled stop was performed. The preselected necessary energy bound not excluding this point did not guarantee that this particular controller would complete it.

The 0.85 result is **safe electrical/control-state recovery**, not full battery-inventory recovery or uninterrupted P/Q service. During its dip, recorded P ranges approximately 722.9–793.7 kW and Q approximately 630.5–711.3 kvar, versus requests of 800 kW and 700 kvar. The current allocator intentionally clips during the dip. Battery energy is accounted and bounded, not restored to its pre-fault value.

## Two transparent scoring clarifications

1. Original abc JSON reported target-only restoration at 1.20 s. It compared every recent sampled state against the pre-fault normalized state and required three successive passing checks. The stricter joint interpretation also requires three successive 50 ms self-cycle comparisons. Existing raw abc records pass the joint criterion at 1.30 s, matching dq. No new dynamics, extrapolation or dq substitution was used. Both labels and every check are preserved in the authoritative summary.
2. Original raw release-delay fields estimated the next sample as last-active + Ts. That estimate is invalid when a hard stop precedes the next sample. The authoritative summary derives actual active-to-inactive transitions from post-update full-control records. Accordingly, the 0.475 current-reference release is null, not a claimed zero delay. Original JSON/NPZ files remain available and unchanged.

The target/self-cycle errors at 1.10, 1.15 and 1.20 s are respectively (8.48619e-6,5.06028e-5), (3.87283e-6,1.23590e-5) and (1.21655e-6,4.49419e-6). The first three consecutive joint passes are 1.20, 1.25 and 1.30 s.

## Numerical checks

- 0.475 coarse/fine normalized full-control-state difference: 1.279e-12
- 0.475 coarse/fine DC event-time difference: 2.22e-16 s; current-peak difference: 9.62e-14 pu
- Across the three matched abc/dq comparisons, current-peak differences are at most 1.22e-13 pu; DC voltage extrema differ by at most 4.55e-13 pu; DC event times differ by 1.94e-14 s
- abc keeps both sides of the initial checkpoint sample and voltage/sample discontinuities. The dq summaries exclude the initial pre-update checkpoint from their maxima. This explains the small 0.475 P/S maximum difference; the current/DC comparisons agree
- All retained arrays are finite, have explicit matching column schemas, and preserve full 10/5 us physical trajectories plus control pre/post snapshots
- Maximum end-to-end abc AC/DC conservation residual magnitudes are 4.02e-6 J and 1.34e-6 J. Battery stored-energy versus integrated-depletion residual reaches 0.01551 J over the full 2.15 s 0.85 run, with about 1.787 MJ discharged; this includes rounding while accumulating a roughly 3.6 GJ absolute energy state. The integral and endpoint values are both retained
- `signed_rhs_check.json` passes 24 nonintegrating coordinate/energy cases: battery power negative, zero and positive, both current/reactive signs, two coordinate angles. Charge/discharge losses are nonnegative; zero-power continuity and the whole-storage balance pass. Maximum current-derivative coordinate discrepancy is 4.99e-10 A/s and storage-balance discrepancy 1.17e-10 W

The periodic trajectory remains dq-only, as authorized. Algebraic signed checks are not independent periodic trajectory validation. No new external model/package installation was needed. These are balanced switching-cycle-average synthetic-model results, with no hardware/OEM calibration or switching/thermal/protection validation.

## Files and replay

- `run_abc_extension.py`: executed extension wrapper; imports only the unchanged local independent abc source, never parent dq code
- `check_signed_rhs.py`, `signed_rhs_check.json`: nonintegrating signed-energy/coordinate audit
- `audit_results.py`: read-only raw-result schema, release-transition, joint-recovery and abc/dq comparison audit
- `results/`: immutable experiment JSON, full float64 compressed NPZ and stdout log
- `authoritative_summary.json`: scored results and all scoring corrections
- `MANIFEST.json`: hashes of this extension's artifacts and required unchanged inputs

Reproduction commands from the G3 root:

```
python model_audit/gate_a_extension/run_abc_extension.py --case sag0475 --h 0.00001
python model_audit/gate_a_extension/run_abc_extension.py --case sag0475 --h 0.000005
python model_audit/gate_a_extension/run_abc_extension.py --case sag085 --h 0.00001
python model_audit/gate_a_extension/check_signed_rhs.py
python model_audit/gate_a_extension/audit_results.py
```

The existing output paths are not an append-safe rerun interface: future authorized reproductions should copy the wrapper into a new versioned output directory or add an explicitly versioned output argument rather than overwrite the present evidence. No rerun is required for these results.
