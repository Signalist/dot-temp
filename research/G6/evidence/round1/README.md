> Historical scientific document. Use the handoff root README.md and REPRODUCE.md for current execution commands and dependency limits. Historical hashes/complete-workspace statements are not current handoff verification.

# G6 Continuous Joint Amplitude Envelope Audit

This is a reproducible research audit, not a paper-ready method or a verified grid-interconnection study. All four networks and PCC waveforms are synthetic. No IEEE benchmark, real joint data-center trace library, DML execution, full AC/PQ dynamics, or proprietary user model is claimed.

## Read first
- `reports/G6_FULL_REPORT_ZH.md`: final report when all frozen gates finish
- `reports/CONTINUOUS_ENCLOSURE_PROOF_ZH.md`: exact model, units, quantifiers and certificate proof
- `reports/NEXT_GATE_AND_STOP_ZH.md`: bounded stopping decision and falsifiable next gate
- `stage0/FROZEN_PROTOCOL_ZH.md` plus numbered amendments: complete preregistration and correction history
- `review/G6_independent_novelty_audit.md`: close literature, strongest same-information baseline, precise source dates

## What the certificate covers
Constant-frequency steady-state outputs under an exact three-odd-harmonic actual-PCC template, with independent site phases/frequencies and continuous shared grid-strength uncertainty. Certified outputs are frequency and line active-power deviations in normalized limit units. Capacity variables are fundamental oscillation amplitudes in MW, not rated or mean data-center MW.

A shared-grid-uncertainty classical support baseline weakly dominates the deliberately separable per-site-grid-max candidate. Any harmonic-l1 comparison changes the waveform uncertainty information. Small differences between certified inner approximations are not exact optimal-domain gains. The full angle system has a common-angle gauge mode; stability pertains to observable frequency/flow transfer after quotienting it out.

## Run
Python 3.12, NumPy 2.3.5, SciPy 1.17.0, pandas 2.2.3, mpmath 1.3.0. Matplotlib is used only for figures. No external executable was downloaded or run.

From this directory:

    OPENBLAS_NUM_THREADS=1 python src/test_g6.py
    OPENBLAS_NUM_THREADS=1 python src/run_certificates.py
    OPENBLAS_NUM_THREADS=1 python src/analyze_envelopes.py
    OPENBLAS_NUM_THREADS=1 python src/run_challenges.py
    OPENBLAS_NUM_THREADS=1 python src/verify_raw.py
    MPLCONFIGDIR=/tmp/g6-mpl XDG_CACHE_HOME=/tmp/g6-cache python src/make_figures.py

An individual model name can follow each numerical script: design4, interior4, transfer8_cube, transfer8_mesh. Running overwrites that model's generated files, so retain the delivered hashes/backups before reproducing. The preserved earlier rectangle-only implementation writes into a separate `rerun_rectangle_v1` directory; it is diagnostic history, not the accepted refined result.

## Raw data schema
- `*_certificate.npz`: all covering leaf rectangles, their support upper bounds, global lower/upper bounds and feasible witness parameters. Method index 0 = locked template; 1 = phase-free harmonic l1; last index=site. Outputs are dimensionless limit ratios per unit fundamental MW
- `*_envelope_coefficients.npz`: sharedκ upper coefficients and cuts, validated lower-support samples and frequencies, explicit search seeds, and all compared halfspace coefficients
- `*_challenge_cases.json`: complete realized test parameters and method allocations, saved before simulation
- `*_traces_*.npz`: every 0.02 s solver state over 90 s for the indexed cases, float64. State order is θ[0:n] radians then Δf[0:n] Hz. `pcc_P_MW` contains actual generated PCC active-power increments for both sites; Q and voltage are not represented
- `*_dt_half_traces.npz`: 0.01 s check for the worst overall and worst fixed-template shared-baseline traces
- `*_challenge_trials.csv`: peaks and conditions; 40 paired base scenarios become 160 method runs, with 36 separate contract-break variants. They are not 196 independent observations

All nonlinear traces use sin(angle difference) physics and thus lie outside the LTI theorem. The boolean `waveform_or_initial_contract_breach` distinguishes additional waveform/startup differences; `nonlinear_model_extension` is true for all. Zero sampled violations do not extend the certificate or establish real-world failure rates.

## Verification and corrections
The initial point-transcendental zero bug and negative-subnormal square-root bug were fixed before any accepted certificate. The first valid rectangle-only bound was too conservative. One bounded resolvent refinement was then frozen and run. Later corrections involved feasible lower-witness endpoints, witness metadata, and outward checking of exported capacities; the underlying physical scenarios and scientific thresholds were not tuned to the nonlinear results.

`review/` contains independent code, high-precision, full-cover and artifact audits. Final raw replay checks reconstruct PCC power and nonlinear peaks from stored states. The final manifest lists SHA256 hashes for all delivered files. Public source PDFs are not bundled without confirmed redistribution rights; official links, minimal source-date records and local-source hashes are provided instead.

Raw transport fragments, if present, are reconstructed losslessly with `python src/reassemble_raw.py` after extracting all packages together. The final manifest also lists the three previously delivered design4 raw archives needed for the complete trace collection.
