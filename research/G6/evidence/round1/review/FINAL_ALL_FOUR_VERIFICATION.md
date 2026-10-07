# Final independent verification: all four G6 synthetic models

## Outcome

All four final continuous upper-enclosure artifacts passed complete leaf-by-leaf replay against the unchanged reviewed model source. A successful enclosure audit does not mean the requested precision target was reached.

| Model | Leaves replayed | Evaluated boxes | Maximum support gap | 2% target |
|---|---:|---:|---:|---|
| design4 | 16,527 | 33,053 | 1.9998366% | Met |
| interior4 | 14,740 | 29,479 | 1.9999333% | Met |
| transfer8_cube | 30,001 | 60,001 | 2.9988803% | Not met |
| transfer8_mesh | 30,001 | 60,001 | 2.8135006% | Not met |

Cube and mesh retain valid wider upper enclosures after budget exhaustion. Their unmet precision targets do not establish infeasibility. No additional optimization or integration was run by this reviewer.

## Checks completed

- Every one of 91,269 leaf upper arrays reproduced bit-for-bit
- Exact binary-endpoint partitions had no holes or overlapping interiors
- Every saved global upper equaled the maximum over its leaves
- Saved lower witnesses reproduced and lay inside the nominal decimal parameter domain
- Every certificate array was finite, and the model source stayed unchanged during replay
- All 1,253 closed shared-kappa strips reproduced; each selected leaf contained its whole strip, and the selected frequency projections covered the full frequency interval
- Shared-kappa upper coefficients were no larger than the independent-kappa maxima
- All saved template and phase-free l1 lower-support coefficients reproduced at feasible parameters
- All 974 checked exported safe polygon vertices, axis/balanced endpoints and allocation-ray points were nonnegative and outward-feasible
- All four coarse-trajectory collections had exact case coverage, finite arrays, matching case-file hashes and peak ratios/CSV counts reproduced from saved states
- Final artifact hashes still matched their individual audit records at rollup

The largest checked outward constraint ratio of exported safe amplitudes was 0.9999999999000005. Polygon areas remain numerical geometry estimates, not interval area proofs. The raw trajectory audit checks saved-data consistency; it does not validate nonlinear integration error or continuous-time nonlinear peaks.

## Proof and assumption review

No remaining substantive error was found in the continuous-enclosure proof or the amended assumption ledger. The ledger now correctly states that nonseparable cross-site/time contracts are this project's chosen reopening direction, not a mathematical prerequisite for every possible contribution. It also distinguishes finite observed spectra from an enforced, verified future waveform contract.

The amplitude normalization is internally consistent: for s=sin(theta), the input template is 3s−16s^3/3+16s^5/5. Checking its stationary points s=±1/2, ±sqrt(3)/2 and endpoints ±1 gives maximum absolute value 14/15, so a is fundamental amplitude rather than peak or mean MW.

## Limits that remain

This verifies a conditional synthetic linear steady-state certificate under the stated finite 1/3/5 PCC waveform, frequency range, static shared grid parameter, exact model and trusted NumPy/IEEE754/mpmath.iv assumptions. It is not a formal proof-assistant result, a measured PCC contract, a real-grid validation, an AC/voltage/UPS certificate, or a nonlinear safety theorem.

The classical exact waveform support remains the same-information reference problem. The independently maximized grid parameter is a conservative relaxation; shared-parameter strip bounds are approximations to the stronger reference. Numerical inner-area differences alone do not prove a gain between exact robust regions. The review does not change `paper_ready=false`.

## Records

- `FINAL_ALL_FOUR_VERIFICATION.json`: current per-model outcomes and artifact hashes
- `*_certificate_replay.json`: full leaf replay and precision status
- `*_envelope_artifact_audit.json`: strip, lower-witness and safe-export checks
- `*_trace_artifact_audit.json`: saved coarse-trajectory consistency and chunk hashes
- `implementation_audit.md`: detailed derivations, corrected defects and versioned review history

All production files were left unchanged by this reviewer.
