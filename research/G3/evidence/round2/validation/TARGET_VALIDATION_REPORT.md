# Higher-fidelity target-witness validation

## Decision

The a100 kW / q600 kvar witnesses at n80 and n160 are **finite-horizon safe in this independent switching model**, with **battery inventory recovered**, but **exact electrical/DC recovery fails at both 0.2 s and 0.3 s**. This is partial physical transfer evidence, not validation of the complete ideal-averaged four-contract claim in a switched device. No hardware or real-compute measurements are involved.

The original controller and witnesses were not retuned. No outer voltage regulator, service reduction, hidden charging stage, warmup reset, battery enlargement or load shedding was introduced.

## Exact same-command interface

Each NPZ stores t, p, q, d, the quadratic b coefficients and exact local-polynomial u=b+tau*b'. The simulator reads the latter directly, including jumps at spline knots, and aligns integration steps at every such knot. It does not smooth command discontinuities, reconstruct the control by optimization, or import the analytical plant/solver. The converted input CSV and original NPZ SHA-256 are retained with every case.

Target parameters are 690 V line-line RMS, 50 Hz, L=0.3 mH/phase, R=5 mOhm/phase, C=0.03 F, Vdc0=1200 V, DC limits 1080–1320 V, current-vector amplitude limit 1500 A, B0=50 kJ with 0–100 kJ limits, battery/input limit ±450 kW, tau=5 ms and ramp limit ±30 MW/s. The controller bandwidth remains 2000 rad/s with 10 kHz PWM. Initial electrical/storage/controller states are shared across all comparisons.

The original compute and P/Q waveform runs to 0.2 s. From 0.2–0.3 s the same states continue with baseline import, q=0, d=650 kW and u=0. This finite continuation is a diagnostic, not a claim of indefinite safety.

## Main n160 result at 10 kHz / 1 us

- DC voltage: 1135.98–1255.40 V, including within-cycle ripple
- Instantaneous phase-vector current maximum: 992.00 A, 508.00 A below the specified limit
- PWM duty-span utilization maximum: 0.960702, no clipped cycles
- Battery inventory minimum: 35.421955 kJ; B(0.2)-B0=2.47 microjoules and B(0.3)-B0=3.36 microjoules
- Battery power magnitude maximum: 428.246 kW
- Requested u maximum: 449.999969 kW; maximum actual battery ramp: 29.999998 MW/s
- No u-clamp or rate-clamp alteration was applied at any evaluated integration midpoint
- Over the initial 0.2 s, active/reactive cycle-average tracking RMS errors: 112.08 W / 400.65 var
- W(0.2)-W0=−11.999213 J; W(0.3)-W0=−17.361883 J

The n80 result is similar: current maximum 992.00 A, voltage 1135.69–1255.75 V, W(0.2)-W0=−11.928375 J, W(0.3)-W0=−17.346508 J, and battery inventory restored within 1.8 microjoules.

The electrical/DC return fails already because W does not return. Small sampled dq endpoint differences and nonzero instantaneous switching ripple also remain. Requested P/Q is not tracked exactly; its nonzero error is reported rather than hidden behind the averaged model.

## Numerical tolerance versus genuine model gap

For n160, maximum W trajectory changes on 2→1→0.5 us refinement are 0.010444 J and 0.002751 J. Total-energy residuals decrease from 0.014819 J to 0.003830 J to 0.000972 J. Battery-power discrepancies from the exact commanded witness at 1 us remain below 0.000364 W and inventory discrepancies below 5.2 microjoules.

A deliberately loose 0.01 J DC-energy comparison tolerance exceeds the finest conservation residual and refinement difference, yet the approximately 12 J terminal gap is roughly 1200 times that tolerance. Inventory recovery passes a 0.001 J tolerance. These are numerical comparison tolerances, not newly relaxed service or recovery contracts.

At 20 kHz and 0.5 us, the n160 terminal deficits shrink to 2.952958 J at 0.2 s and 4.329072 J at 0.3 s; active/reactive tracking RMS errors shrink to 44.19 W / 100.78 var. Increasing PWM/controller frequency changes the implemented sampled controller. It is a convergence/sensitivity check, not a replacement of the primary 10 kHz case.

## Exact terminal energy decomposition

Independently integrating the requested piecewise-linear p/q/d polynomials gives ideal grid energy, ideal copper loss, and filter endpoint energy. The signed contributions below sum to actual W minus ideal W to better than 3e−8 J.

For n160 at 0.2 s, 10 kHz, 1 us:

| Signed contribution | J |
|---|---:|
| Actual grid energy minus requested grid energy | −12.143907071 |
| Negative of actual-minus-ideal total copper loss | +0.141796116 |
| Negative of actual-minus-ideal filter endpoint energy | +0.000349850 |
| Actual-minus-ideal battery discharge integral | −0.000002467 |
| Negative load-integration discrepancy | +0.000000010 |
| Numerical total-energy residual | +0.002550221 |
| Total DC-energy discrepancy | −11.999213344 |

The copper term includes switching ripple. Its net sign is not assumed: actual total copper loss is 0.141796 J less than the ideal requested-current loss because tracking changes the mean current. Relative to the matched sampled averaged physical run, PWM increases total copper loss by 0.237490 J. That latter comparison includes any PWM-induced low-frequency controller differences and is not asserted to be a pure isolated ripple-loss calculation.

At 0.3 s, the grid-energy deficit is 17.469469 J, the favorable copper contribution is 0.103892 J, the filter contribution is −0.000132 J, the numerical residual is +0.003830 J, and the total discrepancy is −17.361883 J.

From 0.2 to 0.3 s the capacitor loses another 5.362669 J, an average 53.6267 W decline. The result therefore does **not** demonstrate a recovered ongoing DC orbit. As energy accounting only, an additional approximately 12 J delivered to the capacitor by 0.2 s would offset the observed terminal deficit, and the subsequent baseline needs approximately 54 W over the measured continuation. These figures do not construct an admissible correction, reserve a P/Q budget, or prove an ordinary DC-recovery controller can satisfy the original exact contracts. No such controller was applied.

## Deliverables and reproduction

- `rectifier.cpp`: independently implemented abc circuit, actual PWM, finite-response battery and conservation logging
- `run_target_witness.py`: exact NPZ-to-polynomial-command conversion and six matched physical runs per witness
- `decompose_target_energy.py`: independent exact requested-flow integration and gap attribution
- `witness_a100_q600_n{80,160}_TARGET_RESULTS.json`: full run commands, source hashes, extrema, bounds, terminal states and refinement
- `witness_a100_q600_n{80,160}_ENERGY_DECOMPOSITION.json`: all signed flows at both checkpoints, including the 20 kHz sensitivity
- `target_a100_q600_validation.png`: full pulse and continuing-load trajectories, including visible DC-energy discrepancy
- `target_a100_q600_switching.png`: current envelope, modulation, actual phase-current ripple and binary-leg evidence

Reproduce from the workspace using `python ./validation/run_target_witness.py <witness.npz>`, then `python .../validation/decompose_target_energy.py`. No external paid compute or third-party solver service is used. The physical limitations and primary model references are detailed in `MODEL_AND_REFERENCE_REPORT.md`.
