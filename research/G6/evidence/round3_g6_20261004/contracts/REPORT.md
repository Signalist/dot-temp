# G6 imperfect-shared-sign contract robustness experiment

## Main result

The perfect shared-sign information benefit degrades materially when a small, explicitly bounded number of mismatches is allowed. At one mismatch in every eight blocks, the positive-load Kundur equal-ray amplitude bracket is **27.396828–27.455076 MW** and the old incremental WECC bracket is **58.550987–58.731042 MW**. These retain bracket-separated gains of at least **12.524%** and **3.477%** over independent signed ports, but lose at least **5.587%** and **20.728%** relative to perfect common signs.

An average-only mismatch-rate bound provides **no all-time peak guarantee benefit** over independent signs if it allows arbitrary finite bursts. This remains true even at zero asymptotic mismatch density. The new evidence therefore identifies a concrete robustness requirement: a local finite-window guarantee matters; a small long-run mismatch percentage alone is insufficient.

This is an input-information contract result, **not a new solver**. Same-information enumeration and a classical totally-unimodular LP reproduce the weighted language DP. These are fluctuation-amplitude thresholds, not extra average hosting, nameplate adoption or measured compute throughput.

## Frozen scope

- L=8 blocks; B=0,1,2,4,8; T=2 s; four half-second segments with q1=(1,1,-1,-1), q2=(1,-1,-1,1)
- Fixed amplitudes and allocation forever; an arbitrary common sign per block; the second port may flip sign in at most B blocks in every L-block window
- Primary ray (0.5,0.5); transfers (0.25,0.75), (0.75,0.25), frozen before new support outcomes
- 256 completed past blocks plus the current block, every generator-frequency output, and a 2048-interval continuous-phase bracket with inherited derivative and modal-tail error bounds
- Every startup prefix is extendible to the padded sliding-window contract; electrical state is carried with no reset
- Positive Kundur uses the previously qualified actual +50 MW compute baseline at each of buses 7 and 8; WECC reuses the old zero-baseline incremental ports and is explicitly nonphysical as compute
- No new nonlinear integration or source-model mutation was performed

The local protocol is in FROZEN_CONTRACT_PROTOCOL.json, written before the new numerical scan. This is a local ordered research record, not an externally preregistered or trusted-timestamped trial. Source SHA-256 hashes are recorded in SOURCE_PROVENANCE.json.

## Primary equal-allocation amplitude brackets

The lower endpoint is an analytic-bound numerical sufficient amplitude for the qualified LTI kernel. Above the upper endpoint, a finite legal word violates 0.05 Hz. Both include continuous phase and every startup history through the proof and inherited error terms; they are not grid-only screens. Evaluation is ordinary floating point, not an interval-certified numerical theorem.

| B per 8 blocks | Positive Kundur (MW) | Incremental WECC (MW) |
|---:|---:|---:|
| 0 | 29.079654–29.145285 | 74.088449–74.376979 |
| 1 | 27.396828–27.455076 | 58.550987–58.731042 |
| 2 | 26.288363–26.341988 | 56.863310–57.033120 |
| 4 | 24.301811–24.347631 | 56.416289–56.583435 |
| 8 | 24.301811–24.347631 | 56.416271–56.583417 |

At B=2 the guaranteed residual gain over independent signs is at least 7.971% for Kundur and 0.495% for WECC. By B=4 no positive equal-ray gain is resolved by these brackets. Kundur's finite-grid maximizing support coincides with unrestricted signs to floating precision; WECC's tiny point difference is far below the phase bracket width. This does not imply equality of the two contract languages or establish exact equality of their infinite supports.

## Transfer allocations

| Source | Ray (a1,a2) | B | Inner (MW) | Outer (MW) |
|---|---|---:|---:|---:|
| positive | (0.25,0.75) | 0 | 22.780212 | 22.829669 |
| positive | (0.25,0.75) | 1 | 22.336659 | 22.384207 |
| positive | (0.25,0.75) | 2 | 21.977730 | 22.023760 |
| positive | (0.25,0.75) | 4 | 21.632662 | 21.677257 |
| positive | (0.25,0.75) | 8 | 21.390354 | 21.433954 |
| positive | (0.75,0.25) | 0 | 35.767555 | 35.852048 |
| positive | (0.75,0.25) | 1 | 31.885757 | 31.952888 |
| positive | (0.75,0.25) | 2 | 29.387098 | 29.444110 |
| positive | (0.75,0.25) | 4 | 26.354736 | 26.400581 |
| positive | (0.75,0.25) | 8 | 26.354736 | 26.400581 |
| wecc | (0.25,0.75) | 0 | 47.398606 | 47.521885 |
| wecc | (0.25,0.75) | 1 | 42.986893 | 43.088267 |
| wecc | (0.25,0.75) | 2 | 42.518987 | 42.618163 |
| wecc | (0.25,0.75) | 4 | 42.395025 | 42.493623 |
| wecc | (0.25,0.75) | 8 | 42.395017 | 42.493615 |
| wecc | (0.75,0.25) | 0 | 70.101444 | 70.431852 |
| wecc | (0.75,0.25) | 1 | 64.222215 | 64.499417 |
| wecc | (0.75,0.25) | 2 | 62.282826 | 62.543504 |
| wecc | (0.75,0.25) | 4 | 60.566671 | 60.813153 |
| wecc | (0.75,0.25) | 8 | 60.438148 | 60.683583 |

The allocation dependence is substantive. It would be misleading to substitute a single scalar 'mismatch penalty' shared by all rays or networks. All 30 brackets and conservative comparison intervals are in contract_amplitude_brackets.csv and comparisons.csv. Negative raw lower comparison endpoints in that CSV mean the numerical brackets overlap; language nesting itself supplies a nonnegative true benefit/degradation. No loss or benefit is asserted from an overlapping pair.

## Continuous-phase convergence

For the primary ray and B=1, reusing the same valid global derivative bound on nested phase grids gives:

| Source | Phase intervals | Inner (MW) | Outer (MW) |
|---|---:|---:|---:|
| positive | 256 | 26.996029 | 27.455196 |
| positive | 512 | 27.223677 | 27.455196 |
| positive | 1024 | 27.338946 | 27.455196 |
| positive | 2048 | 27.396828 | 27.455076 |
| wecc | 256 | 57.321899 | 58.732123 |
| wecc | 512 | 58.018443 | 58.732123 |
| wecc | 1024 | 58.372033 | 58.731042 |
| wecc | 2048 | 58.550987 | 58.731042 |

Across all 30 final brackets the largest support upper-minus-lower gap relative to the finite-grid peak is 0.4713%. All 120 coarse/fine rows are retained in phase_convergence.csv. The inherited fine-grid derivative envelope is used for coarser support grids; no coarser derivative resampling is silently substituted.

The tail bound is independent of mismatch language: truncating a legal word yields a legal finite suffix, and omitted ports are bounded independently. The phase bound is likewise the sum of absolute port derivatives, valid for every admissible word. CONTRACT_THEORY.md gives the DP, prefix monotonicity, tail/phase argument, classical LP equivalence, and average-only obstruction.

## Validation and maximizing finite words

- 25 finite exhaustive-enumeration cases: twenty 12-bit mismatch-word tests and five full two-port 5-block sign tests; maximum DP/LP/enumeration discrepancy 1.78e-15
- 84 same-information LP checks: all 30 source/ray/B maximizing rows and 54 independently selected phase/output rows; largest objective discrepancy 9.84e-13 Hz/MW, far below the retained phase errors
- All LP solutions checked integral to tolerance and their rounded words checked against the original sliding-window language
- 30 maximizing words reconstructed with a separate Python forward-state DP; all reversed chronological words legal, all direct coefficient-weighted sums agree with the compiled support to at most 6.51e-19 Hz/MW
- B=0 and B=8 reproduce the inherited common and independent support endpoints; support nesting is checked at every output and phase
- A separate independent audit passes 351 additional exhaustive startup/end tests (lengths 1–13, every B=0,…,8), verifies all source hashes and schedule/ledger rows, reconstructs inherited modal bound components, and checks the actual nested phase brackets. It independently propagates all 30 primary words with the positive-point 51-state A/B/C matrix exponential or WECC modal-state recurrence: maximum probe discrepancy is 1.513e-15 Hz. These are linear checks, not new nonlinear integrations. See INDEPENDENT_AUDIT.json and independent_audit.py; this audit explicitly excludes the later secondary ablation

The support computation uses classical finite-state optimization. The LP contains the same mismatch windows and fixed amplitudes, so it is a proper same-information baseline. Independent signed ports are a larger-set information relaxation, not a competing solver. These experiments claim neither solver novelty nor a new computational-complexity result.

The supplied compiled implementation uses a 128-entry state buffer and is deliberately bounded to windows no longer than eight blocks (the experiment uses L=8 and the secondary check L=4). The mathematical DP description is general, but the executable is not an arbitrary-L implementation.

The exported chronological word has 257 complete blocks. The probe occurs after 256 completed blocks plus the selected current phase; the final block is completed afterward. The schedule scales each word to 1.02 times its finite-witness outer threshold and its direct finite linear response is 0.051 Hz. This is an algebraic/kernel witness, not a newly integrated descriptor or nonlinear replay. All raw words, schedules, and direct checks are retained.

## Energy, work, physical constraints, and preserved failures

Each full block at each port has exactly zero incremental energy for every allowed common sign and mismatch bit. Under the explicit affine assumption w_i=wbar_i+kappa_i deltaP_i, each 2 s block gives exactly 2 wbar_i work and the entire 514 s word gives 514 wbar_i. Nonnegative work needs wbar_i>=|kappa_i| rho a_i; no empirical conversion from MW to actual completed jobs is claimed.

For positive Kundur each port consumes 100 MW s per block and 25700 MW s = 7.1388888889 MWh over the full word. All 15 exported positive-point words, including their 1.02-outer scaling, keep actual compute demand at least 22.573184 MW. The 50 MW baseline and total-amplitude physical caps are retained explicitly.

For WECC the nominal compute baseline remains zero. Its nonzero symmetric port trajectories contain negative demand and have zero total incremental energy. The stored P columns there are signed incremental quantities, not a physically demonstrated compute load. Nothing here qualifies WECC added demand.

The existing positive Kundur nominal voltages remain **0.945044 pu at bus 7 and 0.948743 pu at bus 8**, below an illustrative 0.95 pu planning floor. This study does not fix that voltage limitation. See ../../round2_g6_joint_admission_20261003/positive_workpoint/POSITIVE_WORKPOINT_REPORT.md.

The existing WECC dynamic-optional old-inner nonlinear witness still reaches **0.05309955034 Hz** at dt=1/128 s (0.05310869707 Hz at dt=1/64 s), against 0.05 Hz, with a coarse/fine difference of approximately 9.15e-6 Hz. That old-inner failure is preserved, not retested, repaired, or absorbed into the new contract claim. See ../../round2_g6_joint_admission_20261003/audit/INDEPENDENT_PROOF_AUDIT.md and ../../round2_g6_joint_admission_20261003/nonlinear/G6_ORIGINAL_NONLINEAR_REPORT.md. The old failing word belongs to a different, dynamic-optional contract; it demonstrates the existing nonlinear-transfer limitation, not a new counterexample for the fixed-amplitude mismatch language.

These are conditional LTI frequency-only bounds evaluated in ordinary floating point. No directed rounding, uniform model-error enclosure, full nonlinear robust certificate, voltage/thermal guarantee, measured throughput, or deployment recommendation is supplied.

## Reproduction and file map

From the workspace root:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 outputs/round2_20261003/andes_env/bin/python outputs/round3_g6_20261004/contracts/run_contracts.py
    outputs/round2_20261003/andes_env/bin/python outputs/round3_g6_20261004/contracts/make_report.py

The first command compiles the accompanying local C++ source with g++, runs all finite support/validation cases, and writes this new experiment directory only. It reads the old coefficients, kernels, bound components and support arrays without modifying them. It does not call ANDES or integrate a nonlinear model.

- FROZEN_CONTRACT_PROTOCOL.json: fixed design, scope and numerical grid
- CONTRACT_THEORY.md: exact contract, DP/LP equivalence, continuous-time bound and asymptotic-average obstruction
- run_contracts.py, window_dp.cpp: numerical experiment and separate witness/baseline checks
- SOURCE_PROVENANCE.json: source paths and hashes
- contract_amplitude_brackets.csv, comparisons.csv, phase_convergence.csv, SUMMARY.json: machine-readable results
- all_phase_support_arrays.npz: complete sampled DP supports for every source/ray/B/output/phase
- maximizing_words.json, maximizing_word_schedules.csv: selected words and complete requested-input schedules
- per_block_energy_work_ledger.csv: all 15420 per-port block energy/work identities
- VALIDATION.json: enumeration, LP, endpoint and word checks
- contract_amplitude_brackets.png/.pdf: scientific figure
- RUN.log: recorded numerical outcomes

## Explicitly post-primary secondary check

After the primary results were available, the parent study requested one additional equal-ray comparison: (L,B)=(4,1) versus the existing (8,2), holding B/L=1/4. This is explicitly exploratory and is not represented as frozen or held-out confirmation. The four-block brackets are 26.980117–27.036605 MW for positive Kundur and 58.541994–58.721993 MW for incremental WECC, giving bracket-separated gains of at least 2.422% and 2.646% over (8,2). Local window shape therefore matters even at the same nominal allowance ratio. See SECONDARY_WINDOW_SHAPE.md/.json and run_secondary_window.py; primary files and scope remain unchanged.
