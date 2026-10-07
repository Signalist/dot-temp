# Additional multi-cycle compute shape-transfer validation

## Scope and decision

This is a separate **six-run validation layer added after the original 41 runs**. Three admitted witnesses were selected before their PWM results to cover a slow port, a small nominal safety margin, and a fast port:

- `spline_R5000_q900.npz`: 5 MW/s battery ramp limit, 900 kvar support, ideal uniform margin 262.0765 J
- `spline_R10000_q1050.npz`: 10 MW/s ramp, 1050 kvar support, ideal margin 24.0046 J
- `spline_R30000_q1000.npz`: 30 MW/s ramp, 1000 kvar support, ideal margin 1228.6309 J

All three pass the tested finite-horizon bounds at both 1 and 0.5 us integration steps with the unchanged 10 kHz PWM controller. All restore battery inventory numerically. **Exact electrical/DC-energy recovery and exact P/Q transfer still fail.** No new controller, retuning, grid-power correction, battery enlargement, state reset or compute-task alteration was introduced.

The physical C++ source SHA-256 is identical to the original reference validation layer. Only the existing input runner, reporting and checkpoint handling were extended to the new 0.4 s service horizon and 0.5 s continuation. The supplied ramp limit is read independently for each case.

## Input preservation and initial conditions

The actual NPZ p/q/d nodes and exact u polynomials are applied directly. The continuing workload is the supplied four-cycle waveform, piecewise-linear at 2.5 ms sampling, spanning 150–1150 kW on the active interval, with 650 kW before and afterward. The actual d nodes are authoritative; the legacy `Aload` value in the parameter metadata is not used to rebuild or rescale this different workload.

For every case:

- Integral of d from 0 to 0.4 s: 260000.000000 J
- Equal-duration 650 kW baseline work: 260000 J
- Extra work integral: approximately 2.7e−12 J, numerical zero
- Initial grid current: id=774.48691459 A, iq=0
- Initial W=21600 J, B=50000 J, b=0, current-PI integral states zero
- L=0.3 mH/phase, R=5 mOhm/phase, C=0.03 F, Vdc0=1200 V, 690 V line-line RMS and 50 Hz remain unchanged

At 0.4 s the simulation continues without resetting any state, holding baseline import, q=0, d=650 kW, and u=0 through 0.5 s. This is a finite continuation test, not evidence of indefinite DC-orbit restoration.

## Complete primary results: 10 kHz, 1 us

| Ramp / support | Vdc range (V) | Current peak (A) | Circular utilization | PWM duty-span utilization | Clipped cycles |
|---|---:|---:|---:|---:|---:|
| 5 MW/s / 900 kvar | 1157.85–1313.37 | 1345.28 | 0.99373394 | 0.99283964 | 0 |
| 10 MW/s / 1050 kvar | 1179.79–1319.64 | 1493.94 | 0.99968502 | 0.99921181 | 0 |
| 30 MW/s / 1000 kvar | 1199.11–1288.85 | 1443.57 | 0.97162564 | 0.97148865 | 0 |

The 10 MW/s / 1050 kvar case is particularly close to physical limits:

- Current headroom: 6.06217 A below the 1500 A instantaneous phase-vector limit
- DC upper-voltage headroom: 0.358904 V below 1320 V
- Circular modulation headroom: 0.000314983, about 0.0315%
- Actual PWM duty-span headroom: 0.000788189, about 0.0788%

Its ideal requested-current maximum is 1464.11178 A, whereas switched current reaches 1493.93783 A. Thus this case retains only about 6 A after switching ripple consumes most of the approximately 36 A ideal-current margin. The result is numerically resolved, but it is not a robust hardware certificate.

Circular utilization is the **pre-limiter average voltage command** sqrt(3)|e_cmd|/Vdc, matching the analytical isotropic envelope; PWM duty span is the phase-sensitive bridge condition. Neither is a constraint on the instantaneous binary voltage-state vector. Both are logged separately, before any clipping. There is zero bridge clipping, zero input-u clamping, and zero battery-rate clamping in all six runs.

## Service and recovery errors

| Ramp / support | Active RMS error (W) | Reactive RMS error (var) | W(.4)-W0 (J) | W(.5)-W0 (J) | Maximum terminal inventory error (microJ) |
|---|---:|---:|---:|---:|---:|
| 5 MW/s / 900 kvar | 210.30 | 446.84 | −21.53372 | −26.96298 | 0.754 |
| 10 MW/s / 1050 kvar | 197.45 | 455.73 | −21.29314 | −26.78151 | 1.519 |
| 30 MW/s / 1000 kvar | 142.77 | 451.22 | −21.37321 | −26.84643 | 1.765 |

RMS errors are evaluated over the actual 0–0.4 s service horizon. Maximum active/reactive errors, respectively, are 587.30 W / 616.87 var, 559.31 W / 627.34 var, and 415.43 W / 590.30 var.

At a 0.001 J numerical inventory tolerance every case passes recovery. At a 0.01 J DC-energy comparison tolerance every case fails by more than three orders of magnitude. These tolerances separate numerical integration accuracy from the model/controller gap; they do not relax the requested exact recovery contract.

The continuing baseline loses a further approximately 5.43–5.49 J over 0.4–0.5 s, corresponding to about 54–55 W. The same ongoing sampled-current tracking bias seen in the earlier layer remains. No DC-recovery action is hidden in the continuation.

## Step refinement and conservation

Halving the integration step from 1 to 0.5 us changes W trajectories by at most:

- 0.004589 J for 5 MW/s / 900 kvar
- 0.004603 J for 10 MW/s / 1050 kvar
- 0.004611 J for 30 MW/s / 1000 kvar

Current-envelope differences are below 0.0000041 A. The tight case's Vmax changes from 1319.641096 V to 1319.641076 V and its circular utilization from 0.999685017 to 0.999685065. All finite-bound and failed-recovery verdicts are unchanged.

Maximum total-energy conservation residuals are approximately 0.0063 J at 1 us and 0.0016 J at 0.5 us. These millijoule errors cannot explain the approximately 21 J service-end DC deficit.

## Exact flow attribution

The existing independently integrated requested-flow decomposition was extended to checkpoints 0.4 and 0.5 s. For the 10 MW/s / 1050 kvar case at 0.4 s, signed contributions are:

| Contribution to actual-minus-ideal W | J |
|---|---:|
| Grid-power tracking integral | −23.79722615 |
| Negative actual-minus-ideal copper loss | +2.49724881 |
| Negative filter endpoint difference | +0.00182065 |
| Battery-discharge difference | +0.00000152 |
| Negative load-integration difference | +0.00000004 |
| Numerical total-energy residual | +0.00501448 |
| Total | −21.29314065 |

The copper contribution includes the actual switched-current waveform; its sign is measured, not presumed. The entire discrepancy is retained, with no adjustment to the witness. The corresponding decompositions for the other two cases and both step sizes are included in their `*_ENERGY_DECOMPOSITION.json` files.

## Excluded and untested cases

No negative-margin NPZ was simulated as an admitted witness. In particular, the analytically excluded 5 MW/s / 1000 kvar path was not simulated. The independent exact-cell exclusion and the comparison against static/global-energy screens belong to the associated analytical evidence; this physical layer neither replaces that argument nor asserts switching-model impossibility for an untested case. The three selected cases were declared before their PWM results, and all three results are reported.

## Artifacts

- `SHAPE_TRANSFER_VALIDATION_PROTOCOL.json`: pre-result three-case selection, frozen controller and step sizes
- `SHAPE_TRANSFER_VALIDATION_SUMMARY.json`: unchanged physical-code hash, workload/initial-state checks, source hashes, all outcomes and refinement
- `spline_R*_q*_TARGET_RESULTS.json`: exact run commands, extrema, requested/actual power errors, clamp logs and checkpoint states
- `spline_R*_q*_ENERGY_DECOMPOSITION.json`: independent flow attribution
- `shape_transfer_validation.png`: the entire selected family, including load, support, voltage/current/modulation and failed DC recovery
- `TARGET_AUDIT.json`: numerical-verification checks kept separate from physical-contract verdicts

Primary physical equations, signs, integration method and limitations remain those in `MODEL_AND_REFERENCE_REPORT.md`. This is idealized synthetic software evidence only. The new narrow margins particularly preclude extrapolation to unmodeled losses, dead time, noise, tolerances, arbitrary initial phase or real hardware.
