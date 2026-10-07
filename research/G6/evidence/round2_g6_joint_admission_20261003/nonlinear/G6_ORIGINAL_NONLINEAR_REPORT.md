# G6 unchanged-workpoint nonlinear stress replays

Status: 20/20 pre-frozen runs exported; complete=True.

## Scope first

Both supplemental constant-P ports have P0=0 at the original qualified operating points. These are signed-injection stress replays. Negative probe power occurs in each nonzero waveform. Native aggregate bus loads remain a separate impedance-load background; their nonnegativity cannot be reinterpreted as a controllable positive-compute load. No throughput calibration, positive compute embedding, full-family nonlinear robustness, infinite-time nonlinear safety, or interval-certified numerical result is claimed.

The official Kundur and WECC source model parameters, original power-flow equilibria, native PQ dynamic conversions, and disabled demonstration events are unchanged. Independently reconstructed x0/y0 match the original stored qualified descriptor x0/y0 exactly. Each run initializes once; electrical state carries across all 65 replayed blocks.

## Frozen design

Equal-split ray (0.5,0.5), T=2s, q1=(1,1,-1,-1), q2=(1,-1,-1,1), quarter-block duration 0.5s. For each network: committed inner 0.98 times conservative numerical LTI capacity lower bound; committed outer 1.02 times LTI capacity outer bound; matching two dynamic-optional cases; erroneous reset-inner 0.98 times reset capacity inner bound, driven by the carried-state committed support-achieving word. All choices are fixed in NONLINEAR_FREEZE.json before any nonlinear results.

Every 257-block full word and its 65-block suffix are preserved. The nonlinear replay starts the retained suffix at t=1s, executes all 65 complete blocks through t=131s, then holds input zero through t=151s. It includes the current block past the support target phase, preserving exact blockwise zero incremental energy. Keeping the last 64 past blocks discards only an LTI modal tail with an upper bound smaller than 5e-9Hz at all preselected amplitudes and aligned observation times. This is an LTI truncation statement only; nonlinear full-history equivalence is not asserted.

Nonlinear maximum steps are 1/64s and 1/128s, with every ZOH jump registered and ±1e-4s event bracketing. The selected support time is an explicit observation event. Same-input LTI output uses analytic modal exponentials with exact ZOH event splitting and no electrical resets, evaluated at the nonlinear solver times. Modal transfer qualification and original descriptor/state independent replay are in ../transfer. Floating exponentials and event-resolved numerical integration are not formal exact-real proofs.

## Refined finite-horizon results

| Network | Frozen case | Total amplitude MW | Same-input LTI peak Hz | Nonlinear peak Hz | Nonlinear margin to 0.05Hz |
|---|---|---:|---:|---:|---:|
| kundur | committed_inner | 32.14922174 | 0.048881787 | 0.049645737 | +0.000354263 |
| kundur | committed_outer | 33.54235592 | 0.050999999 | 0.051828834 | -0.001828834 |
| kundur | dynamic_optional_inner | 29.58288909 | 0.048891223 | 0.049369372 | +0.000630628 |
| kundur | dynamic_optional_outer | 30.85885826 | 0.050999999 | 0.051516438 | -0.001516438 |
| kundur | reset_inner_error | 115.92638283 | 0.176262081 | 0.191099527 | -0.141099527 |
| wecc | committed_inner | 72.60668039 | 0.048809914 | 0.048812369 | +0.001187631 |
| wecc | committed_outer | 75.86451886 | 0.051000000 | 0.050994015 | -0.000994015 |
| wecc | dynamic_optional_inner | 64.33174109 | 0.048831578 | 0.053099550 | -0.003099550 |
| wecc | dynamic_optional_outer | 67.18846461 | 0.051000000 | 0.056249519 | -0.006249519 |
| wecc | reset_inner_error | 98.93569197 | 0.066509619 | 0.066465444 | -0.016465444 |

Positive margin means this finite numerical replay remained inside the chosen research threshold. It is not a safety certificate for all allowed words. Negative margin means an observed finite violating trajectory.

## Boundary conclusions

- kundur committed_inner: this selected nonlinear witness stays inside 0.05Hz, peak 0.049645737Hz at maximum step 0.007812500s
- kundur dynamic_optional_inner: this selected nonlinear witness stays inside 0.05Hz, peak 0.049369372Hz at maximum step 0.007812500s
- wecc committed_inner: this selected nonlinear witness stays inside 0.05Hz, peak 0.048812369Hz at maximum step 0.007812500s
- wecc dynamic_optional_inner: FAILED nonlinear transfer: the LTI-inside witness exceeds 0.05Hz, peak 0.053099550Hz at maximum step 0.007812500s

The cause of any nonlinear mismatch is not assigned to a specific limiter/controller without a separate diagnostic. Step refinement and unchanged source/workpoint/input checks address numerical or input substitutions; they do not remove genuine model nonlinearity.

## Refinement and model mismatch

- kundur_committed_inner: coarse/fine peak change 2.23417574e-05Hz; support-target change 1.76584239e-05Hz; threshold decision unchanged=True; exact schedule identity=True
- kundur_committed_outer: coarse/fine peak change 2.47126087e-05Hz; support-target change 1.88999365e-05Hz; threshold decision unchanged=True; exact schedule identity=True
- kundur_dynamic_optional_inner: coarse/fine peak change 1.62351434e-05Hz; support-target change 1.06623957e-05Hz; threshold decision unchanged=True; exact schedule identity=True
- kundur_dynamic_optional_outer: coarse/fine peak change 1.76875988e-05Hz; support-target change 1.17047893e-05Hz; threshold decision unchanged=True; exact schedule identity=True
- kundur_reset_inner_error: coarse/fine peak change 3.34021543e-05Hz; support-target change 0.000291905071Hz; threshold decision unchanged=True; exact schedule identity=True
- wecc_committed_inner: coarse/fine peak change 1.22836522e-05Hz; support-target change 1.22836522e-05Hz; threshold decision unchanged=True; exact schedule identity=True
- wecc_committed_outer: coarse/fine peak change 1.15944089e-05Hz; support-target change 1.15944089e-05Hz; threshold decision unchanged=True; exact schedule identity=True
- wecc_dynamic_optional_inner: coarse/fine peak change 9.14672801e-06Hz; support-target change 4.09080921e-06Hz; threshold decision unchanged=True; exact schedule identity=True
- wecc_dynamic_optional_outer: coarse/fine peak change 7.49445479e-07Hz; support-target change 5.76614204e-06Hz; threshold decision unchanged=True; exact schedule identity=True
- wecc_reset_inner_error: coarse/fine peak change 1.43253105e-05Hz; support-target change 1.02431442e-06Hz; threshold decision unchanged=True; exact schedule identity=True

Per-run outputs report full-trace maximum/RMS LTI-versus-nonlinear errors, selected support values, terminal-ringdown peaks, generator/time attaining the sampled maximum, and native-plus-probe minimum load. These mismatches must not be hidden by reporting only boundary classifications.

## Evidence files

- NONLINEAR_FREEZE.json: dated pre-outcome choice and source hashes
- *_input.npz: full and trimmed words plus full/actual event arrays
- *_actual_schedule.csv: actual common-sign, optional-amplitude, Q=0 event schedule
- *_dt64.npz and *_dt128.npz: time grid, actual input, nonlinear all-generator frequencies, identical-input exponential LTI traces, bus voltages, native and total aggregate loads
- *_dt64.json and *_dt128.json: solver completion, operating-point metadata, metrics, physical ledgers
- NONLINEAR_AUDIT.json and NONLINEAR_RESULTS.csv: full numerical audit, blockwise-energy checks, input identity and refinement
- ../transfer/: modal qualification, analytic truncation/phase bounds, and original linear state/descriptor checks

Source-integrity check: all monitored original sources unchanged=True.
