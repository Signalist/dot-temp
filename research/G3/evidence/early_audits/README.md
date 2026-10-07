# G3 Gate A reconstruction and revalidation

Start with `GATE_A_REVALIDATED_REPORT_ZH.md` and `RECOVERY_TIMELINE.md`. Status: reconstructed_then_rerun; original filesystem results were lost. No Gate B search or new controller performance claim. `paper_ready=false`.

## Evidence entry points

- `recovery/PARAMETER_TEXT_RECONSTRUCTION.json`: exact historic protocol hash matches
- `recovery/UNITS_REVALIDATED.json`: new coordinate, power and energy algebra tests
- `gate_a/dq_results/`: new500kW/150kvar dq nominal trajectories,10/5us
- `model_audit/abc_reference/revalidation_results/`: independently rerun abc nominal/fault trajectories
- `gate_a/preconditioned_dq/`: newV2.1dq traces and complete first-qualified checkpoints
- `gate_a/INDEPENDENT_COMPARISON_REVALIDATED.json`: matched100us control-clock comparison
- `recovery/TRAJECTORY_REPRODUCTION_HASH_AUDIT.json`: allfourV2.1NPZ hashes reproduce pre-reset reported hashes
- `protocol/DC_BOUND_GATE_A_V2_1_REVALIDATED.md/.json`: current necessary-bound proof and fresh-data calculations
- `model_audit/DC_BOUND_REVALIDATION_ADDENDUM.md`: independent freshabc audit
- `model_audit/DEPENDENCY_PROVENANCE.json`: public reference package identity; no vendor binary bundled

Any HISTORICAL file is explicitly historical-only. Do not substitute its oldstate or old17.035ms value for the newly qualified-state certificate.

## Core model

PositiveP/Q are PCC exports. Peak-amplitude dq uses S=1.5v*conj(i), while perunit p/q omit1.5 after base conversion. The dynamic series filter+grid branch uses Ldi/dt=u−e−Ri−jω0Li. ActualPCC voltage includes the gridLdi/dt term and is computed from the dynamic circuit, not set equal to the remote source voltage.

DC energy obeys Wdc_dot=Pbus−Pinv−inverter_loss. Battery power is bidirectional, with bounded firstorder/rate dynamics and sign-correct conversion and energy efficiency. Controller is sampledSRF-PLL, P/Q-to-current Q-priority, currentPI, radial DC-dependent voltage saturation and antiwindup. A normalized stationary modulation command is delayed one sample and held; actual converter voltage scales with instantaneousVdc. Current is never numerically projected. See lockedJSON controller contracts and code for every value.

## Reproduction (from the extracted G3 root)

Python3.12, NumPy2.3.5, SciPy1.17.0 were used. Core experiments require onlyNumPy/SciPy. Set OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1. Create a localvirtualenv if needed; do not edit an unrelated environment.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
PY=python
$PY recovery/test_units_reconstructed.py
$PY gate_a/dq_bench.py --case conservation_nominal --max-step 1e-5
$PY gate_a/dq_bench.py --case conservation_nominal --max-step 5e-6
$PY gate_a/dq_preconditioned.py --h 1e-5
$PY gate_a/dq_preconditioned.py --h 5e-6
for pair in '1e-5 10us' '5e-6 5us'; do
  set -- $pair
  $PY model_audit/abc_reference/reference_abc.py --protocol protocol/GATE_A_LOCKED_V1_1.json --case conservation_nominal --h "$1" --out "model_audit/abc_reference/revalidation_results/conservation_h$2"
  $PY model_audit/abc_reference/preconditioned_abc.py --protocol protocol/GATE_A_LOCKED_V2_1.json --h "$1" --out "model_audit/abc_reference/revalidation_results/preconditioned_v2_1_h$2"
done
$PY gate_a/compare_independent.py
$PY gate_a/dc_bound_gate_a_v2_1.py --new-evidence
```

The optional public component check uses motulator0.7.8, with officialwheel identity in the dependency record. Only its grid/capacitive converter path was used. The full package's unrelatedTorch stack was not required; it is not bundled here. The directRHS comparison is algebraic and is not a switching simulation.

## Scope and caveats

This is a transparent synthetic balanced average-value model. No OEM calibration, hardware protection, PWM validation, successful fault recovery, sustained oscillation service, network damping result or strongbaseline comparison is claimed. The800kW/700kvar continuous equilibrium has an unsafe sampled-startupS overshoot; it remains in the record. The fixedpre-run selects the first full-state converged safe window, without choosing a favorable laterpoint. Allstate and event failure data remain inspectable.
