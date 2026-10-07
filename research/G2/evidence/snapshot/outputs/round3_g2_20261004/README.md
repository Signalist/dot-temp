> Historical scientific document. Use the handoff root README.md and REPRODUCE.md for current execution commands and dependency limits. Historical hashes/complete-workspace statements are not current handoff verification.

# G2 round 3: response-value representation boundaries

Start with `report/G2_ROUND3_RESEARCH_DOSSIER_ZH.md`.

## What changed scientifically

- Exact prior-art reduction removes the old moment/spline count and constant from the novelty list
- A finite-jerk, positive equal-energy shared-clock full-future gap is proved for finite jerk arcs: Theta(m^-3), on an explicitly inactive-band synthetic fourth-order model
- Uniform workload slope gives Theta(m^-4) over a still unbounded-bandwidth family; fixed Fourier cutoff sharpness for the full nonlinear problem remains open
- Coherent non-opposite kernels yield two universal jerk-clock candidates for post-service peak optimization, showing the hard cancellation family is not generic
- Matched classical free-knot support baselines, endpoint-information ablations, jerk-preserving compression and an actual Kundur transfer-structure check are executed

## Essential scope

All power models are p_j=e_j(theta)*theta_dot, fixed completed shared work and per-port energy, and common continuing nominal tail. Finite acceleration jumps and finite jerk jumps are different admissible classes. Synthetic full-peak theorems, linearized endpoint baselines, nonlinear witnesses and actual network structure tests are separately labeled. No runtime lower bound, new general optimizer, hardware validation or confirmed historical priority is claimed.

The theorem's sufficient asymptotic constants are extremely conservative: N0=1,734,133, and the certified m=100 gap requires N=6,358,421 and is about 1.34e-28 in normalized output units. This is mathematical asymptotic evidence, not an engineering margin.

## Reproduce

Run from `scratch/727bd5f4248b`. The already provisioned interpreter is:

`outputs/round2_20261003/andes_env/bin/python`

Run these scripts with that interpreter:

1. `outputs/round3_g2_20261004/literature/verify_reductions.py`
2. `outputs/round3_g2_20261004/experiments/matched_support_baselines.py`
3. `outputs/round3_g2_20261004/experiments/matched_arc_budget.py`
4. `outputs/round3_g2_20261004/audit/verify_matched_support.py`
5. `outputs/round3_g2_20261004/experiments/jerk_compression.py`
6. `outputs/round3_g2_20261004/theory_worker/verify_theory.py`
7. `outputs/round3_g2_20261004/audit/verify_jerk_audit.py`
8. `outputs/round3_g2_20261004/experiments/network_structure_transfer.py`
9. `outputs/round3_g2_20261004/audit/final_verification.py`

No script installs software or edits the round-2 inputs. Runtime versions are recorded in `protocol/RUNTIME.json`. Ordinary floating point is used; no outward-rounded matrix/root certification is claimed. The formal statements rely on the included proofs, not fitted log-log slopes.

## Key evidence files

- `theory_worker/FINITE_JERK_AND_BANDWIDTH_THEOREMS.md`: complete upper/lower and regularity proofs
- `theory_worker/COHERENT_KERNEL_EXACT_BOUNDARY.md`: exact non-opposite post-service boundary
- `theory/NONCANCELLING_KERNEL_BOUNDARY.md`: separate bounded-acceleration endpoint ablation
- `literature/`: exact theorem/equation reductions, primary-source excerpts, fixed-band linearized switch bound
- `protocol/`: pre-execution confirmations, source hashes, deviations and post-hoc same-arc-budget design
- `experiments/`: scripts, numerical results, logs and network kernel traces
- `audit/`: independent physical-convolution checks and skeptical mathematical review
- `report/CLAIM_LEDGER.json`: supported claims, exclusions and remaining questions

The package preserves failures and conservative bounds rather than overwriting them with favorable interpretations. All 896 inherited G2 files are checked against their initial SHA-256 digests in final verification.
