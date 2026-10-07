# Preregistered near-boundary PWM batch

## Outcome

All four admitted q790/q800/q805/q808 kvar cases, each with active service alpha=100 kW and n320 analytical control, satisfy the tested finite-horizon physical bounds in the unchanged 10 kHz PWM model. None clips the PWM bridge, battery command or battery ramp. All four recover battery inventory numerically but **fail exact DC-energy recovery**, consistent with the earlier q600 case. No survivor-only selection or controller retuning was used.

The batch was defined in the frozen `BOUNDARY_PROTOCOL.json` before these PWM results. That protocol also includes q810, which is analytically excluded with prefix-envelope margin −6.362611 J. Its negative-margin NPZ is not a feasible witness, and the protocol explicitly required no q810 simulation. This report does not claim switching-model impossibility for an unsimulated case.

## All admitted cases, 10 kHz and 1 us

| q support (kvar) | Ideal uniform margin (J) | Max circular utilization | Max PWM duty span | Clipped cycles | Current peak (A) | W(.2)-W0 (J) |
|---:|---:|---:|---:|---:|---:|---:|
| 790 | 138.286 | 0.99635601 | 0.99610962 | 0 | 1169.77 | −11.91632 |
| 800 | 65.509 | 0.99825084 | 0.99801118 | 0 | 1179.58 | −11.91346 |
| 805 | 29.043 | 0.99919957 | 0.99896329 | 0 | 1184.50 | −11.91251 |
| 808 | 7.138 | 0.99976924 | 0.99953493 | 0 | 1187.46 | −11.90778 |

Both modulation measures are retained. Circular utilization is sqrt(3)*|e_cmd|/Vdc, matching the analytical isotropic voltage envelope. PWM duty span is (max e_phase-min e_phase)/Vdc, the actual common-mode-injected bridge limit. Reporting only the latter could accidentally take advantage of the phase-sensitive hexagonal region outside the analytical circle. Here even the stricter circular envelope passes in all four cases.

The smallest circular headroom is only 0.00023076, or about 0.0231%, for q808. The smallest duty-span headroom is 0.00046507, or about 0.0465%. These are fragile synthetic-model margins, not robust device certificates. No tolerance on semiconductor losses, dead time, parameter error, grid disturbances, current measurements, PLL error or initial grid phase was established.

The q808 circle maximum occurs at the cycle ending 17.2 ms. Its contemporaneous DC-energy difference from ideal is approximately +0.136 J, even though its later terminal deficit is approximately −11.91 J. Therefore comparing the global terminal deficit directly with the 7.14 J ideal active modulation margin would ignore timing and would not correctly predict a violation.

## Tracking, voltage, inventory and continuation

| q (kvar) | Voltage range (V) | Active RMS error (W) | Reactive RMS error (var) | Max active error (W) | Max reactive error (var) | W(.3)-W0 (J) |
|---:|---:|---:|---:|---:|---:|---:|
| 790 | 1132.48–1272.83 | 116.94 | 404.61 | 334.32 | 561.33 | −17.32563 |
| 800 | 1132.27–1273.53 | 117.21 | 404.82 | 334.13 | 563.27 | −17.32403 |
| 805 | 1132.16–1273.89 | 117.36 | 404.93 | 334.08 | 564.25 | −17.32333 |
| 808 | 1132.09–1274.34 | 117.43 | 405.00 | 333.51 | 564.84 | −17.32201 |

RMS tracking uses the 0–0.2 s service horizon. Maximum errors are retained over the full 0–0.3 s trajectory. The continuing 0.2–0.3 s baseline uses unchanged 650 kW load, baseline import, q=0 and u=0, with no state reset. It does not produce exact DC recovery and is not an indefinite-orbit test.

The exact battery-polynomial command remains applied with no clamping. Actual B differs from the ideal analytical inventory by less than 9 microjoules over the initial horizon in each primary 1 us run, so the inventory conclusion is not hiding a different battery use.

## Refinement and matched average

Every admitted case was rerun with 0.5 us maximum integration steps, keeping PWM at 10 kHz. Maximum W-trajectory changes are approximately 0.00275 J, and current-envelope changes are below 0.000003 A. Clipping, finite-bound and recovery verdicts are unchanged.

The preregistered matched averaged run for q800 also has no clipping. Its duty-span maximum is 0.99800722, compared with 0.99801118 for PWM; its current maximum is 1151.94 A versus 1179.58 A for PWM. Its W(.2)-W0 is −12.09122 J versus −11.91346 J for PWM. This confirms the dominant exact-recovery failure also exists with the frozen sampled current controller before explicit switching ripple is added.

No additional 20 kHz near-boundary cases were needed to interpret this outcome; the earlier q600 frequency study already separated finite sampling bias from time-integration error. This choice was made after reporting the entire admitted batch, not to remove failing cases.

## Reproducibility and scope

`BOUNDARY_VALIDATION_SUMMARY.json` retains protocol and NPZ hashes, all admitted outcomes, source paths, and the explicit q810 omission reason. Each `boundary_a100_q*_n320_TARGET_RESULTS.json` contains exact commands, run traces, comparison arrays and convergence. `boundary_validation_batch.png` shows every admitted case together. `TARGET_AUDIT.json` separates numerical-verification success from failed physical recovery contracts.

The modeling assumptions and primary physical references are in `MODEL_AND_REFERENCE_REPORT.md`; the exact terminal-flow decomposition method and baseline results are in `TARGET_VALIDATION_REPORT.md`. All artifacts remain simulations of an idealized synthetic converter. The correct final statement is finite-horizon constraint support plus inventory recovery, with exact P/Q/DC-recovery transfer not established.
