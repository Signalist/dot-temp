> Historical scientific document. Use the handoff root README.md and REPRODUCE.md for current execution commands and dependency limits. Historical hashes/complete-workspace statements are not current handoff verification.

# G2 round-3 finite-jerk, bandwidth and kernel boundaries

## Results to use

- `FINITE_JERK_AND_BANDWIDTH_THEOREMS.md`: fixed-jerk, entire-future peak representation gap Theta(m^-3) for amplitude-only profiles; Theta(m^-4) for uniformly slope-bounded profiles with growing bandwidth; O(m^-4) at fixed finite bandwidth, with fixed-bandwidth sharpness left open. Positive speed, work, energy and jerk are all preserved by the upper construction. Acceleration/speed bands are inactive for the entire feasible class.
- `COHERENT_KERNEL_EXACT_BOUNDARY.md`: a nonproportional positive-exponential-mixture kernel family has exact terminal/post-service extrema among two fixed three-switch jerk clocks. Also gives a mixed-sign common-mode dominance condition. The within-service peak is expressly excluded from this two-clock result.
- `CONSTRUCTIVE_THREE_MOMENT_LEMMA.md`: closed-form two-interval construction matching three jerk moments, complementary to the general moment-body proof.

The upper moment machinery is classical; the exponents and application-specific lower construction must be compared with literature before any novelty claim. The fourth-order filtered output and aggregate cancellation are synthetic restrictions, not a physical validation advance. General non-opposite three-port algebra still has exact nullspace cancellation. Certified kernel-error tolerance shrinks with the output gap.

## Diagnostic findings

The protocol was frozen before execution in `DIAGNOSTIC_PROTOCOL.json`. The 45 power/primitive/BV identity probes agree within 2.24e-18, and quadrature-order refinement changes values by at most 1.98e-17. Nonzero upper boundary and jerk-atom terms are exercised. The witness scaling N^3*y(1) approaches 9.4404711e-7; N=128 is within 0.0566% of that asymptotic constant.

The analytic constants are deliberately conservative: the sufficient index is N0=1,734,133. Diagnostics at N<=128 are NOT tests inside the theorem's certified positive-lower regime. At N=4 and N=8 the complete zero-state startup contribution makes the displayed signed witness output negative. This does not contradict the asymptotic theorem, and must not be hidden by subtracting the nominal response.

Ordinary floating point and symbolic algebra complement the analytic proofs; they are not outward-rounded numerical certificates. The diagnostic script does not test the moment-compression upper construction, which is being checked independently in the parent research task.

## Reproduce

From the shared workspace:

    python outputs/round3_g2_20261004/theory_worker/verify_theory.py

The script overwrites only `THEORY_DIAGNOSTICS.json`, with a structured report. The captured run output is `THEORY_DIAGNOSTICS.log`. It uses Python, NumPy and SymPy, records exact symbolic identities, and makes no network requests. `REPAIR_LEDGER.json` records the serialization-only first-run failure and the independently identified integrability hypothesis repair.

## Scope not established

- An active-band finite-jerk moment-replacement theorem
- A matching fixed finite-bandwidth lower, or a fixed-bandwidth exact switch bound
- A lower bound on every optimization/certification algorithm
- A robust fixed-radius kernel-neighborhood lower as N tends to infinity
- Physical grid/load-model validity, useful deployment-scale risk, or general historical novelty
