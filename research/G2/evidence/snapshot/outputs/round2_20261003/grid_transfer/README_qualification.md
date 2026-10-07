# Independent multi-machine grid transfer qualification

## Status and permitted interpretation

This package independently reproduces public ANDES 2.0.0 benchmark models. It is not a physical-grid measurement and does not validate the origin of any compute workload. All compute traces used downstream remain explicitly synthetic. Successful local tests are empirical qualifications, not a uniform nonlinear error certificate or an operational safety guarantee.

Two complete dynamic cases are qualified for the described interfaces:

- Modified Kundur full: 10 buses, 4 GENROU machines, TGOV1 governors and EXDC2 exciters; 52 differential states. The only reduction in `kundur_reduced51.npz` removes the uniform rotor-angle gauge. No machine/controller is truncated.
- WECC full: 179 buses, 29 GENROU machines, IEEEG1 governors, ESDC2A/EXST1/ESST3A exciters, IEEEST/ST2CUT stabilizers. Original nonlinear equations and parameters are unchanged. The verified analysis interface is the complete descriptor pencil; do not use the installed ANDES EIG.As for this case.

NPCC140 remains a documented negative qualification at this particular distribution version and working point. Its +0.01122858/s real mode is reproduced by an independent full generalized pencil and a nonlinear directional perturbation: after 20s a 1e-5 modal displacement becomes 1.251717e-5, versus 1.251786e-5 predicted. This does not invalidate other published NPCC operating points, versions, or validation studies. It excludes this working point from a stable infinite-tail certificate.

## Source lock and baseline changes

`PROVENANCE_LOCK.json` records original workbook SHA-256 hashes, sheet-level canonical data hashes, base MVA/frequency, active-model counts/configuration, solver settings and installed source hashes. All original workbooks remain untouched in the pinned installed distribution. `ANDES_LICENSE_GPL3.txt` preserves the upstream GPL-3.0-or-later notice. Do not redistribute the virtual environment as a deliverable.

Original source SHA-256:

- Kundur: f725e03ba12d8207616f68acdd606bbd35e7c4a68f13e66d7db43925adac2ed8
- NPCC: f85a46d5f4b4910b09c7b141b85504fc060b812f5f940f266db8c9784f755b21
- WECC: 038cf6732389f7d691232b7548cfa3dea2dc6a01304cc5918ad63ad55fdf23ec

The explicitly named runtime variant disables the supplied demonstration line-toggle events, then adds separate supplemental constant-power ZIP ports. Original background PQ loads keep ANDES's default constant-impedance dynamic conversion. They are not globally replaced by constant-power loads. Original machines, control parameters, limiters, network branches and operating-point load/generation values are not tuned to obtain desired results.

All cases converge in power flow and initialize with residuals below approximately 1e-12. An undisturbed equilibrium staying exactly still is not accepted by itself as stability evidence. The qualification additionally checks eigenvalues, independent descriptor structure, actual nonlinear perturbations, input amplitude scaling and timestep refinement.

## Reproducible injection interface

`grid_adapter.py` exports:

- `build(slug, buses=[...], dt=1/128, tf=..., baseline_MW=[...], baseline_Mvar=[...])`
- `install_schedule(system, rows)` with rows `[time_s,P0_MW,Q0_Mvar,P1_MW,Q1_Mvar,...]`
- `extract(system)` for individual generator frequency deviations in Hz, COI frequency, rotor angles, all bus voltage magnitudes, from-end branch P/Q, full state deviations and identifiers
- `descriptor(system)` for the original generated analysis Jacobian, retained for diagnostics
- `descriptor_verified(system)` for the independent ESST3A chain-rule-completed analysis Jacobian

Positive P/Q means added consumption. Both cases use 100 MVA and 60 Hz. For zero-baseline ports the first row is `[0,0,...,0]`. Later values are zero-order held, and their timestamps are registered as exact integration breakpoints. Nonzero steady added loads must be passed through `baseline_MW`/`baseline_Mvar` before power flow; schedules then specify increments above that baseline. Reconnection/isolation is an exogenous change in this extra port; the model does not implement a physical UPS converter, breaker protection, protection coordination, battery energy accounting or real IT hardware dynamics.

Typical qualified ports are Kundur buses 7/8, original active loads 1159/1575MW, and WECC buses 1/4, original active loads 1750/2350MW. Q probes are scaled to these active-load numerical reference magnitudes and must not be mislabelled as a percentage of original Q, which may be negative.

Native excitation/governor limits remain present. Reported frequency bands are research thresholds, not regulatory limits and not actual protection trips. Any later finite-amplitude waveform must be replayed in the nonlinear model rather than declared safe from micro-perturbation accuracy alone.

## Descriptor and linearization audit

The complete local DAE is `M dz/dt = K z + G u`, where `z=[delta_x;delta_y]`, `M=diag(Tf,0)`, and `K=[[fx,fy],[gx,gy]]`. Load columns in G enter the corresponding bus active/reactive balance with coefficient 1/baseMVA. Algebraic equations, including zero-Tf state rows, are retained. `linear_trace` uses the same differential trapezoidal versus instantaneous algebraic residual convention as ANDES and the actual nonlinear sample timestamps.

WECC's installed EIG routine returns 569 finite modes, including a spurious +1.00494/s mode. The independent complete generalized pencil has 565 finite modes. A nonlinear perturbation in the reported spurious direction decays rather than exhibiting its predicted exponential growth. Consequently, `wecc_baseline.npz`'s EIG As and `wecc_qz_finite565_candidate.npz` are DIAGNOSTIC/REJECTED AS ORDINARY INPUT STATE-SPACE MODELS. The latter also fails the input-derivative-free reduction check. No Lyapunov certificate may be built from either file.

A second, distinct audit found missing ESST3A.VE VarService chain-rule contributions in the generated Jacobian. Let

`Z = KPC (vd + j vq) + j (KI + KPC XL) (Id + j Iq)`, `VE=abs(Z)`.

For real `a`, `dVE/da = Re(conj(Z) dZ/da)/abs(Z)`. The four `dZ/da` values for `(vd,vq,Id,Iq)` are `(KPC,j KPC,j(KI+KPC XL),-(KI+KPC XL))`.

The `VB_x` equation receives `FEX_y*dVE/da`; the `IN` equation receives `-ue*IN*dVE/da`. Four ESST3A devices times two equations times four inputs give the 32 entries listed in `ESST3A_chainrule_32_entries.csv`. This completion changes the analysis matrix only. It does not patch the ANDES installation or the nonlinear model. Source location: installed `andes/models/exciter/esst3a.py`, VE declaration and IN/VB equations; exact source hash and upstream-version URL are in the lock file.

Three independent central-difference step sizes confirm the corrected submatrix (relative Frobenius errors 1.69e-11, 2.81e-10, 1.80e-9). Before correction, the directional derivative error persists when displacement is reduced by 100x. After correction the actual nonlinear/linear frequency error scales down approximately 10x with 10x input reduction.

`chainrule_audit.json` records the corrected generalized spectrum: 565 finite roots at absolute beta thresholds 1e-8, 1e-10 and 1e-12; one uniform-angle zero root; all remaining real parts negative, rightmost -0.0333333/s. The earlier complete-pencil audit reports a normalized finite-eigenpair residual <=4.14e-16 but also a large shifted-pencil condition estimate (~2.49e9). Good root residuals alone cannot validate that a Jacobian differentiates the nonlinear model, hence the separate chain-rule and trajectory audits.

## Probe results and numerical limitations

`port_qualification.json` retains all exploratory 0.1%, 1%, 5% local-load P/Q pulses on both nodes, including failed Boolean statuses. Some WECC dt=.01 runs reached 8s minus ~1e-13 and then failed on a vanishing final step; these are not silently promoted to success. `timestep_refinement.json` reruns both P/Q ports with dt=1/128 and 1/256; all finish successfully exactly at 8s. Binary-valued timesteps are recommended for these experiments.

Kundur P/Q micro-probes agree with its ordinary analysis model, with errors growing with input amplitude. WECC's verified descriptor nonlinear/linear frequency relative L2 errors at 0.1% local P are:

- bus1 P: 0.03994%; bus1 Q: 0.03522%
- bus4 P: 0.14100%; bus4 Q: 0.11844%

At 0.01% local P the respective errors are 0.003982%, 0.003535%, 0.014122%, 0.011837%. These establish local consistency for these probes; they are not a global eta bound.

Kundur's full A has a neutral rotational gauge. `kundur_reduced51.npz` saves R/V, full_A/full_B, and the 51-state stable quotient. Its input order is `[P7_MW,Q7_Mvar,P8_MW,Q8_Mvar]`. `C_frequency_Hz` produces the four individual machine frequency deviations. For inertia-weighted risk use `sum_i w_i*df_i^2`, not `(sum_i w_i*df_i)^2`. The latter is a different COI metric that can cancel opposing machine motions.

## Phase and scheduling experiments

`nonlinear_replay/` holds the actual nonlinear frozen-waveform replays, separate from baseline qualification. `replay_kundur_nonlinear.py` records every case, including non-separating controls, and skips already successful saved cases on resumption. `run_focused_replays.py` prioritizes the fixed-pair timestep check and a scheduler zero-delay/oracle replay.

The fixed phase pair uses bus8, period10s, low/high50/100MW, 50% duty, and observation t=1..101s. The first high phase has 5s remaining; the second has .1s remaining. Both reconnect at 100MW. Their periodic waveform, mean75MW, amplitude and 100s total energy match. The grid starts at the same recovered original equilibrium. Compute-phase continuity through an ideal UPS island is an imposed scenario assumption; no compute workload measurement is claimed.

Reference sources: [official test cases](https://docs.andes.app/en/v1.6.2/getting_started/testcases/), [official verification](https://docs.andes.app/en/v1.10.1/verification/), [pinned software release](https://pypi.org/project/andes/2.0.0/), [versioned case source](https://github.com/CURENT/andes/tree/v2.0.0/andes/cases), [license](https://github.com/CURENT/andes/blob/v2.0.0/LICENSE). Published verification motivates using these benchmarks; the local numerical audit above is still required.

## Frozen nonlinear results now available

All numbers below are the maximum absolute frequency deviation across individual machines during 100s after reconnection. For the same-P phase pair, both reconnection powers are 100MW and the low/high levels are 50/100MW. The original research-band test is 0.1Hz; 0.2/0.3Hz results are also retained. No parameters or bands were changed to force an outcome.

| Network / port / period | High-start peak Hz | High-end peak Hz | Mean75MW peak Hz | 0.1Hz result |
|---|---:|---:|---:|---|
| Kundur bus8 T2 | 0.10359777 | 0.10314332 | 0.09534850 | Both phases exceed |
| Kundur bus8 T5 | 0.12319990 | 0.10280708 | 0.09534850 | Both phases exceed |
| Kundur bus8 T10 | 0.12704506 | 0.08750588 | 0.09534850 | Fixed pair separates |
| Kundur bus8 T20 | 0.12704506 | 0.09109669 | 0.09534850 | Fixed pair separates |
| Kundur bus7 T10 | 0.14958083 | 0.10661224 | 0.11244708 | Both phases and mean exceed |
| WECC bus1 T10 | 0.03830663 | 0.02876124 | 0.02868504 | All below |
| WECC bus4 T10 | 0.04314911 | 0.02452531 | 0.03243589 | All below |

Kundur table rows and the WECC constant-mean references use maximum step1/64s. The final WECC phase-pair columns use step1/128s and explicit integration points 1e-4s before/after each ZOH jump. All complete with a true solver return. In WECC the 0.1s initial high-tail segment exposed half-step event errors in ordinary coarse stepping; all original numerical variants are retained. With event resolution the maximum coarse/fine peak difference is1.27e-5Hz, and final phase spreads are9.5454mHz at bus1 and18.6238mHz at bus4 (`wecc_eventresolved_convergence.json`). For the main Kundur bus8/T10 pair, step1/128s gives 0.12703354 and 0.08753166Hz; the fixed-band conclusion is unchanged. Its already-running periodic reference has a late100s peak of 0.08574202Hz. WECC demonstrates a continuous same-instantaneous-P phase effect on an independent complete network, but it does not reproduce the Kundur threshold crossing under the frozen absolute input. WECC has an original baseline bus voltage as high as approximately1.16705pu, so the frequency statement is not a claim that every generic voltage criterion is met.

The actual legal scheduler trace for synthetic seed701, Kundur bus7, P-only peak1.159MW (0.1% of local baseline P) is independently replayed without changing its timestamps or shapes, except an irrelevant common1s start shift. Nonlinear frequency-energy integrals through104.3s (including100s after input ends) are 4.1612716797e-6 Hz²s for zero delay and 3.8617209421e-6 for the exact discrete oracle: 7.19854% reduction. This is the weighted sum of separate machine-frequency squares, not squared COI frequency. The corresponding exact linear infinite-tail risks are4.1605516751e-6 and3.8609243070e-6; differences are0.01730% and0.02063%. Terminal nonlinear maximum machine frequency deviations are5.80e-12 and7.35e-11Hz. The small observed terminal residual is disclosed rather than promoted to a proved nonlinear infinite-tail bound.

### Storage-controller development failures retained

The original ideal P25MW storage design has a linear continuous-time upper bound below0.1Hz, but its actual nonlinear replay peaks at0.100821586Hz. Halving the step to1/256s gives0.100816022Hz, so this failed band test is not explained by the integration timestep. Its COI peak is only0.0986Hz; substituting COI would change the predeclared endpoint and is not allowed. Replaying the identical canonical input through the linear descriptor gives a sampled peak0.099534741Hz and a candidate-specific full-trace maximum discrepancy0.011428696Hz. This discrepancy is evidence of finite-amplitude mismatch, not a uniform robustness bound.

The original P50MW ideal-controller trajectory also fails in the nonlinear grid: peak0.113133618Hz, COI0.102821686Hz, minimum bus voltage0.925448pu. These two different control trajectories do not establish a monotonic capacity comparison. They show that increasing an ideal linear-design power budget alone does not establish the nonlinear claim.

`replay_pwl_storage.py` supports later finite-PCS candidates without editing the grid engine: IT is an explicitly separate ZOH signal and realized BESS power is PWL, evaluated exactly by interpolation at integration timestamps with every knot registered. Positive BESS means grid injection; net supplemental consumption is IT minus BESS. Its producing controller must independently establish command/slew feasibility, charge/discharge efficiency and energy constraints. A grid replay does not prove those properties by itself. Input file hashes and distinct labels prevent silently reusing results for a changed candidate.

### Prospectively frozen finite-PCS confirmation

`storage_service/CONFIRMATION_FREEZE_V1.json` independently specifies26 input/candidate/timestep combinations before their new nonlinear evaluations. The complete result set is `nonlinear_replay/storage_v1_confirmation_results.json`; `storage_confirmation_summary.csv` combines its metrics with the producer's declared power/energy/PCS assumptions. This is a prospectively frozen numerical confirmation on the same benchmark operating point, not a statistically independent grid holdout or a uniform robustness theorem.

All26 simulations complete successfully. Six optimized nominal candidates, at P25/P50MW and known tau20/50/100ms, stay below the0.1Hz research band. The P25/P50 tau50ms nominal301s peaks are0.094886275 and0.094676223Hz; their step1/256s101s checks give0.094884639 and0.094732367Hz. A P25tau100ms candidate had a pre-freeze fallback design target0.0975Hz after the stronger0.095 family proved infeasible; the acceptance band remained0.1Hz and its actual nonlinear peak is0.098190799Hz.

Each fixed P25/P50 tau50ms actual-power trajectory is replayed under eight predeclared IT period, phase, amplitude and reactive-power changes. Six of eight stay below the research band for each controller. Both fail at+5% real-load amplitude (peaks0.101205972/0.100820840Hz) and at PF0.98 leading reactive input (0.116059063/0.115725050Hz). No control is reoptimized in these transfer tests. The result is a localized admissibility region with explicit failures, not blanket robustness.

The initially specified conventional P25 slow-ramp baseline peaks at0.100447443Hz, while its P50 counterpart peaks at0.097379699Hz. The separately frozen stronger P25 conventional baseline succeeds: coarse/fine peaks0.095892101/0.095877174Hz. Its usable SOC excursion is0.0354532MWh versus0.0270377MWh for the optimized P25 candidate, a23.7368% reduction within the compared control family; neither a global optimum nor unique feasibility is claimed. The conventional baseline actually has a slightly smaller frequency-squared integral (0.255857 versus about0.259739Hz²s). All28 frozen evaluations complete, with23 below-band and5 above-band outcomes; these counts include three timestep repeats and are not independent statistical trials. The complete predeclared set, including every failure, is retained.

P means effective active-power service headroom. E is usable SOC excursion under the declared efficiency and recovery assumptions, not battery nameplate energy or capital cost. For example, nominal P25 has E≈0.02704MWh; this does not imply a27kWh physical battery can furnish25MW. Cell C-rate, thermal constraints, minimum nameplate energy and technology choice are outside this model. The declared first-order PCS/command feasibility and loss-aware energy checks are supplied separately by the controller producer, while this package verifies the unchanged grid response to realized power.


### Additional numerical diagnostics, excluded from frozen-sample counts

The closest-margin P50 fixed-control period10.5s case remains below-band at step1/256s, peak0.099878948Hz, versus0.099816977Hz at step1/128s. The121microHz residual margin is small relative to the62microHz step-refinement change; this is reported as a close numerical pass, not a rigorously certified continuous nonlinear margin.

The original ideal P50 failure is independently refined and compared against exact ZOH linear propagation. Its nonlinear peak changes only from0.113133618 to0.113097739Hz when the step halves to1/256s. The exact matrix-exponential linear model driven by identical canonical input has a sampled peak0.099541618Hz, and the full-trace discrepancy is0.021086609Hz. The nonlinear negative-frequency peak occurs at34.578125s on the fourth machine, when net supplemental consumption is150MW because charging coincides with high IT power. The substantial failure is not attributable primarily to the tested timestep. This is a candidate-specific diagnosis and does not supply a transferable nonlinear error bound.

### Reactive periodic-tail diagnostic

The fixed P25 controller with PF0.98 leading IT load was extended to301s at step1/256s, without redesign. Its first100s peak is0.116014194Hz. The peaks on281–291s and291–301s are0.100708110210297 and0.100708110210357Hz, with maximum corresponding machine-frequency trace difference1.53e-13Hz. BESS power is zero after its finite40s service, yet the numerically converged forced periodic orbit remains above the0.1Hz band. This is nonlinear numerical evidence for this operating point and original constant-impedance background-load model. The separate stable-LTI periodic-tail theorem can establish an all-future obstruction in its stated linear model; a single nonlinear trajectory is not a global impossibility proof over arbitrary nonlinear controls or basins.

### Narrow version2 confirmation after preserving version1 failures

After the version1 failures, a new common P50MW/tau50ms/eta0.95 trajectory was designed for the explicitly bounded scale range1..1.05, fixed period10s, phase0 and Q0. This is a targeted conventional robust-LP design; the new freeze and all old failures are preserved separately. `storage_service/CONFIRMATION_FREEZE_V2.json` specifies six evaluations: two design-endpoint checks, three previously unevaluated joint-input points, and one numerical repeat.

All six finish successfully below the0.1Hz research band:

- Design scale1:0.088653321Hz
- Design scale1.05:0.094742129Hz through301s; step1/256s check:0.094794632Hz
- New scale1.025, phase0:0.091675042Hz
- New scale1.025, phase0.15s:0.091675042Hz
- New scale1.025, phase1.25s:0.091561737Hz

The identical maxima at the first two new phase settings do not imply identical trajectories: an earlier common portion can dominate their maxima, while their complete traces/integrals differ. The two endpoints and timestep repeat are not independent input holdouts. The two shifted-phase points are outside the robust-LP design set and provide finite-point numerical evidence only. These results do not establish arbitrary-phase, Q, actuator-parameter or nonlinear-global robustness. `storage_v2_summary.csv` preserves the distinct purposes.

## Final integrity and compact redistribution

`ORIGINAL_SOURCE_INTEGRITY_CHECK.json` confirms all three source workbook hashes and every tracked installed model/solver source hash still match the pre-experiment lock. `implementation_sha256.txt` identifies the study adapters and retained matrix exports. Original input workbooks and the simulator installation are unchanged.

For a compact artifact, retain all study code/JSON/CSV/Markdown/text, the GPL notice, the environment freeze and especially `kundur_reduced51.npz`, which is the shared calculation input for the phase, legal scheduler and storage studies. Retaining the sparse descriptor matrices and their small auxiliary/eigenvalue files permits independent local inspection. Large remaining NPZ files are raw trajectories or derived diagnostics and may be distributed separately with hashes and regeneration commands. `home/` is a regenerable ANDES code-generation cache; the full `andes_env` is not a publication artifact. Do not treat rejected WECC EIG/QZ candidates as trusted input models.
