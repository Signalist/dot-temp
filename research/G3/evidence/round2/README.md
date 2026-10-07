# G3 reproducible research package

This is a new synthetic, import-positive compute-port study. It does not replay historical G3 raw trajectories.

## Read first

1. `reports/G3_RESEARCH_REPORT_ZH.md`: scientific synthesis and all limits
2. `theory/EXACT_PORT_CONTRACT_THEORY.md`: full assumptions, proofs, constructive cell, counterexamples, and free-allocation weak certificates
3. `audit/AUDIT_REPORT.md`: independent audit findings
4. `validation/TARGET_VALIDATION_REPORT.md`, `BOUNDARY_VALIDATION_REPORT.md`, `SHAPE_TRANSFER_VALIDATION_REPORT.md`: independent true-PWM results, including exact recovery failure
5. `literature/PRIMARY_NOVELTY_THREATS.md`, `FIXED_PATH_CERTIFICATE_ADDENDUM.md`: 25 primary-source comparisons

## Main supported result

Under the stated ideal averaged model, fixed continuing compute work, P-import cap/Q-support floor, and full recovery contract, at 100 kW active curtailment and 100 J extra net late-recovery allowance:

808 kvar is constructively feasible, while every support magnitude at or above 834.41453 kvar is excluded by the independently checked weak-modulation bound. This is a conditional all-allocation capacity bracket, not a hardware rating or complete general P/Q controller solution.

The exact lag/ramp charge-cell scheme has a sharp O(h²) **state-tube** bound. An unconditional O(h²) service-capacity or runtime theorem is not claimed. Mathematical ingredients and strong prior art are attributed. High originality remains unestablished.

## Reproduce in a copy

Requires Python 3.12, the packages in `requirements.txt`, and a C++17 compiler for true PWM. The archived Python environment is not included. Exact byte-identical optimizer outputs are not required across platforms; use the recorded physical margins and independent residual checks.

Commands, from the package root:

    python -m venv .venv
    .venv/bin/pip install -r requirements.txt
    .venv/bin/python src/run_campaign.py
    .venv/bin/python src/run_exact_cells.py
    .venv/bin/python src/run_boundary.py
    .venv/bin/python src/run_ablations.py
    .venv/bin/python src/run_switch_corridor.py
    .venv/bin/python theory/test_exact_cell.py
    .venv/bin/python theory/weak_modulation_certificate.py
    .venv/bin/python theory/vector_weak_certificate.py
    .venv/bin/python theory/dc_allocation_certificate.py
    .venv/bin/python audit/independent_audit.py
    .venv/bin/python audit/audit_switch_corridor.py
    .venv/bin/python audit/audit_weak_modulation.py
    .venv/bin/python audit/audit_vector_weak.py
    .venv/bin/python validation/run_reference_tests.py
    .venv/bin/python validation/run_target_witness.py results/witness_a100_q600_n160.npz
    .venv/bin/python validation/run_target_witness.py results/boundary_a100_q808_n320.npz --suite boundary
    .venv/bin/python validation/run_target_witness.py results/switch_corridor/spline_R10000_q1050.npz --suite shape

Run shape, ablation and primary scripts in separate processes: the shape/ablation drivers temporarily replace a local profile function to define their declared counterfactual input. Each script records the resulting explicit input samples.

The boundary driver and all selected witness inputs, command polynomials and full numerical results are included. `src/admission.py` exposes `solve_inner` and `solve_outer` to regenerate any declared pair. Primary 40/80/160 grids and parameter variants are refinements/counterfactuals, not independent empirical samples.

## File / numeric semantics

- Analytical files use kW, kJ, kA, kV, seconds; independent plant uses SI
- Positive grid P is import, positive Q is reactive support injection
- Filenames containing `witness` also retain negative-margin optimization outputs for audit. Only entries marked admitted / positive verified margin are physical witnesses
- `sigma` is a uniform DC/modulation margin objective. A negative inner optimum alone is **not** an impossibility proof
- Saved LP coefficients/duals are floating-point artifacts, supplemented by independent weighted-inequality audits; no interval-arithmetic formal certificate is claimed
- Exact terminal inventory is redundant with exact total energy and DC recovery in the already loss-compensated fixed-path campaign. The uncompensated ablation separates the two stores explicitly
- Buffer commands after the initial hold are continuously varying, not recurring ZOH commands or an unmodeled communication pipeline
- True-PWM tests pass finite-horizon safety and battery inventory recovery, but exact P/Q and DC-orbit recovery fail. No retuning or hidden reset fixes that gap

## Included and excluded

This clean evidence core includes source, input profiles, numerical witnesses, proof, audits, figures and result summaries. It omits large raw PWM/average/recovery traces and execution logs; READ_FIRST_ZH.md and OMITTED_RAW_TRACE_INDEX.csv give the exact scope. No hardware measurements or historical raw replay were used.
