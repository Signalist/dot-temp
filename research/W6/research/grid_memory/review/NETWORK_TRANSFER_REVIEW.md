# Independent exploratory network-transfer and support-LP review

Scope: review of `code/kundur_transfer.py`, its fresh `network_transfer/RESULTS.json`, recovered 51-state NPZ, and a lightweight check of `code/slew_support.py`. The full optimization/transfer study was not rerun. All checks here were newly run after the reset.

## Verdict

No substantive analytic or propagation error was found. The methods produce mathematically valid truncation/interpolation budgets for the stated stable, diagonalizable linear model in exact arithmetic. The implementation is ordinary floating point, has no outward-rounding enclosure of its eigensolve/LP, and must not be called a machine-verified interval certificate or hardware guarantee.

The recovered input mapping is correct: column 0 is `P_MW@bus7`; column 2 is `P_MW@bus8`. The frequency output has four generator channels. The model's largest pole real part is about -0.13953445, and modal eigenvector condition number is about 12124.66. No new model identification, nonlinear validation, concurrency test, real-GPU mapping or hardware measurement was performed.

## Independent numerical checks

`verify_network_transfer.py` checks both active-power input ports at gain 200 against direct 51-by-51 matrix exponentials at t=0,.01,.5,1,5,20,60,140. It also compares five continuous piecewise-affine forcing segments per port with separate augmented-matrix exponential propagation.

Observed discrepancies:

- Maximum modal versus direct kernel error: 6.95e-15
- Maximum forced-response frequency-output error: 4.10e-16
- Maximum forced-response state error: 2.31e-15
- Minimum reported segment upper bound minus an independent 10,001-point segment sample maximum: 2.06e-4
- Maximum independently quadrature-recomputed objective error: 1.34e-15

These spot checks support implementation consistency; they are not an enclosure of every possible floating-point error. `NETWORK_TRANSFER_REVIEW.json` records times, ports, outputs and the underlying source checksum.

## Area and tail remainder proofs

For each scalar output, h(t)=Re sum_j r_j exp(lambda_j t), with Re(lambda_j)<0. On an interval [t_i,t_i+dt], linear-interpolation pointwise error is bounded by dt^2/8 times sup|h''|. Its integrated error is consequently bounded by dt^3/8 times that supremum. This constant is conservative; a sharper integrated bound is possible but unnecessary.

The maps x to max(x,0) and max(-x,0) are 1-Lipschitz, so the same integrated error bounds both positive and negative areas. On each interval,

sup |h''| <= sum_j |r_j lambda_j^2| exp(Re(lambda_j)*t_i).

The code sums these intervalwise bounds as a geometric series. Its expm1 formulation avoids needless loss of precision for small modal exponents. The exact areas of each linearly interpolated sign-crossing segment are computed correctly. Independent integration of the saved kernel samples reproduced both area arrays and their error budgets.

The tail-area formula is also correct:

integral_T^infinity |h(t)| dt <= sum_j |r_j| exp(Re(lambda_j)T)/[-Re(lambda_j)].

Thus max(interpolated positive area, interpolated negative area) minus the interpolation remainder is a lower bound for the infinite-horizon nonnegative-input support, and adding the interpolation and tail remainders is an upper bound. This relies on all poles being strictly stable, as they are in this recovered case. A production implementation should explicitly reject unstable/zero-real-part poles rather than silently applying these formulas.

## Segment and full-future peak bounds

The normalized modal coordinate obeys q_j'=lambda_j q_j+p. The affine-forcing propagation formula in the code is exact. For nonnegative affine p on a sample interval of length step, stability gives

|q_j(t)| <= |q_j(t_i)| + p_max*step.

Therefore its sampled maximum plus p_max*step bounds the entire segment. This establishes the code's output derivative budget

L <= sum_j |r_j| (|lambda_j|*qmax_j+p_max).

Every time is within step/2 of a sample, so sampled_absolute_peak+L*step/2 is a valid intersample upper bound. The independent denser spot checks remain below that bound, but the analytic argument, not the denser samples, is what supplies the time-continuum justification.

The 60-second post-return segment is explicitly propagated. For every later time, the omitted homogeneous response is bounded by

sum_j |r_j*q_return,j| exp(Re(lambda_j)*60).

Taking the maximum of that envelope and previous upper bounds covers all future time. It remains valid even if the 60-second envelope is not below the observed peak; the comment about being settled is not a required hidden assumption.

## Same-cap comparisons and honest interpretation

The solver and global target baseline use the same physical cap min(1,guard_cap), service law sqrt(p), physical slew R=1, work M=2, uniform EOS law, initial idle state and full-cycle objective. The solver's nested `case.R=2` is a normalized-work-coordinate value R*M; physical slew is 1. Its cost is rescaled by M consistently. Independent physical-coordinate quadrature reproduces the stored objective to about 1e-15.

At gain 20, both bus cases have cap 1 and identical workload policies/objectives. The relative weighted-objective improvement versus the target class is approximately 1.1961654%. These are different transfer ports of the same model, not independent workload optimization replications.

At gain 200, the caps bind. The finite-mesh solver is slightly worse than the exact target:

- bus 7: relative gain -0.0000173303, or -0.00173303%
- bus 8: relative gain -0.00000849267, or -0.000849267%

Retain these negative results. They are consistent with a restricted finite mesh failing to represent exact target knees and do not show a benefit. Neither comparison is a matched-cycle-time energy comparison, nor evidence of beating a same-information global optimum.

For gain 200, the calculated all-work/all-time guard meets the study allocation at .05 Hz in the model; the five stored EOS replays have lower upper bounds. Those five EOS values alone are not an all-work certificate. The amplitude-kernel bound supplies the all-work claim, subject to the stated mathematical model and ordinary-float limitations. At gain 20, the corresponding model amplitude bounds are about .0413961 and .0412751 Hz.

## Lightweight slew-support implementation check

`verify_slew_support.py` independently generates nodal hat weights using 12-node Gauss-Legendre integration on every interval, checks all 12 archived optimizer paths, and solves one of the LPs using those independently generated weights.

- Maximum analytic-versus-quadrature hat-weight difference: 2.06e-14
- Maximum selected-path objective difference: 2.78e-16
- One independently weighted LP optimum difference: 4.17e-17
- Maximum archived path slew excess from floating arithmetic: 4.89e-13
- Maximum cap excess: zero

The indefinite integrals in `Swing.hats` are correct, including their first moments and the assembly of left/right nodal hat weights. The remainder `R*step*area()` equals (R*step/2)*||h||_1 because this swing-frequency kernel has equal positive and negative areas; using the full L1 norm rather than its truncated value is conservative.

The LP has free endpoints because it bounds the all-history amplitude/slew class. A feasible remote-past ramp extends its last lag value to zero; its additional contribution is bounded by the stated tail remainder. Consequently LP_support-tail is a lower bound and LP_support+tail+interpolation is an upper bound, intersected with the amplitude and slew norm guards. This interpretation needs the continuous zero-past/all-history condition already identified in the main review. It is not automatically the support of the smaller W6 single-job class.

The 4.89e-13 floating slew excess and ordinary HiGHS/eigensolve arithmetic are further reasons to retain the explicit non-interval-certified label. They do not materially affect these exploratory comparisons, but a rigorously machine-certified lower feasible witness would require inward correction/verified arithmetic and a corresponding objective adjustment.

## Support-witness repair review, 2026-10-04 14:35 UTC

The prior tiny-slew-excess finding is resolved in the newly saved witness paths, while all 12 original paths are retained under `results/pre_inward_repair/`. The repaired path is inward-scaled, and independent `Fraction` checks on the serialized node powers and node times pass for all 12 files. The checks pass both with IEEE-exact R/P values and with their intended decimal values. The earlier review evidence remains in `SLEW_SUPPORT_REVIEW.json`; the new evidence is appended in its `repair_reviews` field.

The upper LP support now uses nonnegative inequality multipliers and an explicit box residual. For any y>=0 and feasible Av<=b, 0<=v<=P,

c^T v <= y^T b + P sum_i max(c_i-(A^T y)_i,0).

This weak upper bound is valid without exact dual stationarity and without assuming that a reported primal LP optimum is an upper bound. Evaluate both objective signs and take the maximum. One case was rerun independently; its computed weak bounds reproduce exactly. Independent rational evaluation for the represented nodal weights and exact grid constraints differs from the floating upper sums only at roughly 1e-17, with both signs of rounding discrepancy. Accordingly the ordinary-float/non-interval label remains necessary. Exact witness feasibility does not by itself enclose transcendental kernel weights or cost arithmetic.

Reproducible check: `verify_slew_support_repair.py`. It appends rather than erases historical review findings.

## Bundled-input portability note

`verify_network_transfer.py` imports `SOURCE` from `kundur_transfer.py`; after the parent changed that source definition to `ROOT/'inputs/kundur_reduced51.npz'`, the verifier uses the bundled file automatically. The bundled receipt records SHA-256 `31e798abc23bdcb6c3b46aeb488caf96636127390935eac4d9f0e2fdd5601828`, matching the source checked in this review. This is a path-only portability change, not fresh physical model validation.

The default `verify_slew_support.py` was subsequently updated and executed again. It now recomputes the current lower from the repaired witness and the upper from `LP_dual_weak_upper`, preserves the original audit under `historical_reviews`, preserves appended `repair_reviews`, and automatically invokes `verify_slew_support_repair.py`. A standalone reproduction therefore checks the repaired final method rather than restoring the superseded primal-objective upper formula. The network verification script also preserves its analytic-review annotations while refreshing numerical results and bundled-input provenance.
