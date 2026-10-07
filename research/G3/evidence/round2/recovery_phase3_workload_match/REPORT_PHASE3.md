# Phase3: time-resolved workload-matched counterfactual

## Result and corrected scope
All 34 retrospective comparator checks pass the newly declared S−L finite-contract tests. These are the 17 already evaluated V2 physical/clock configurations at two integration resolutions. No new blind confirmation is claimed.

The previous V2 no-service branch removed the compute pulses as well as requested grid service. Its correct label is the flat-load baseline F. It remains valid for baseline-orbit recovery: during the recovery interval [0.2,0.7] s, F and S both already consume 650 kW, but their entering physical/controller states contain different service histories. Those old return costs are not isolated whole-service attribution at equal time-resolved workload. All old results and freezes remain intact.

This stage adds L, a feasible load-following no-grid-service comparator that receives exactly the same actual compute input d(t) as S at every time. S−L is the service-strategy increment relative to this explicitly chosen feasible load-following policy under identical time-resolved compute input. It is not the globally optimal no-service opportunity cost, a unique universal causal allocation, or a new proof of uniform uncertainty robustness.

## Exact branch definitions and source locations
- F: existing V2 mode0, Pbaseline=654498.72485653043 W, Q=0, d=650000 W, uFeed=0, with the same service-clock freeze/resume gates
- S: existing V2 mode1, original prescribed P/Q/d/uFeed service schedule and unchanged V2 recovery controller
- L: new mode2, dL(t)=dS(t), Qrequest=0, uFeed=0, and Prequest=(1−sqrt(1−4cd))/(2c), c=R/(1.5VP²), using fixed nominal R=0.005 ohm and VP=563.3826408401309 V. The implementation evaluates the algebraically identical stable form 2d/(1+sqrt(1−4cd)); Pdot=d_dot/sqrt(1−4cd)

In rectifier_load_match.cpp, lines31–32 derive d_dot from the same authorized piecewise-linear workload schedule; lines43–49 define F/S/L, with line46 preserving the original S command path and lines47–48 preserving d in slot2 while changing only L P/Q/uFeed. Lines51–55 consume that same d slot in the physical DC equation. Lines72–74 retain V2 gating and capacitor-plus-inventory PI; lines75–77 retain current control and the authorized midpoint preview. Actual tau/ramp are used only in the physical battery-port equation at line55.

One immutable V2 nominal warmup checkpoint per integration step initializes all corresponding branches. The absolute grid/carrier clock, service onset and sampling are unchanged. Known-schedule half-period P/Q prediction is permitted as before; no future measured workload or matched-health signal is read. Pre-onset differences caused by known preview are included in their own ledger and in checkpoint-to-final totals; onset states are not assumed identical. No workload is curtailed, shifted or reallocated.

## Exact workload and service-window accounting
The input CSV extends to0.3 s; integrating that entire file gives195 kJ. The actual service ends at0.2 s and has130 kJ of compute input, identical in cumulative total to flat650kW over0.2 s. These two intervals must not be confused. S and F differ at intermediate times: their cumulative task-energy difference peaks at10.5 kJ despite returning to zero at the service endpoint. S and L use the identical input function throughout, not merely the same total energy.

Across all runs, maximum numerical S/L cumulative load-energy discrepancy is 3.97674739e-07 J, below the frozen1e−5 J check. This is integration residual from different switching subgrids; exact function equality follows from the common interpolation expression, not a requirement that independently accumulated floating-point integrals be bitwise equal.

Both new-executable nominal S replays reproduce the old S main/snapshot/bin CSV files byte-for-byte, all dense arrays bitwise, and every reported extremum exactly. SERVICE_REPLAY_IDENTITY.json records these checks. All other S/F data are reused read-only.

## Frozen comparison contract
PROTOCOL_PHASE3.json, executable, runner, evaluation script, original input and checkpoint copies were hashed before the first new simulation in EXECUTION_FREEZE_PHASE3.json. Both implementation and independent-audit evaluators were fixed before seeing L results.

- Physical bounds for S and L: voltage1080–1320 V, each phase and space-vector current≤1500 A, B0–100 kJ, |b|/|u|≤450 kW, declared physical slew, PWM and circular utilization≤1
- Service tracking against each branch’s own request: ten matching20ms-window means, P error≤2 kW and Q error≤10 kvar
- Return: in the final five20ms cycles ending atT+0.5 s, common1us samples satisfy |WS−WL|/|BS−BL|≤2 J and each paired phase-current difference≤2 A
- Recovery budget fromT toT+0.5 s: paired cP≤5 kW; absolute net signed, positive-only and absolute-integral grid increments each≤100 J
- Continuing observation extends toT+0.7 s. All six windows retain individual branch energies, paired increments and ΔW/ΔB/ΔZ

These are new comparator-stage tests of the original V2 trajectory against L. They do not retroactively change V2, extend the recovery100J budget to whole-service absolute throughput, or validate the distinct core exact-return100J contract.

## Results
Worst S−L return differences across all34 runs: W=0.226772043 J, B=0.225669519 J, phase current=0.000296728677 A.
Worst S−L recovery costs: |signed|=0.274866326 J, positive-only=0.134570904 J, absolute integral=0.524038042 J, paired cP=27.8222327 W.
L is physically feasible in every check: V=1195.447108–1202.716454 V; peak absolute phase current=1150.088506 A; peak space-vector amplitude=1150.365964 A; maximum circular modulation=0.855852429. The observed L battery state remains at its initial inventory because its port feedforward and inventory error are zero; this does not turn it into a constant-import comparator.

Fine-step matrix:

| Case | S−L max W J | max B J | max phase A | recovery signed J | positive J | absolute J | paired cP W | pass |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| nominal_h05 | 6.08998e-05 | 2.96117e-07 | 2.89997e-06 | -0.215298 | 0.0423529 | 0.300004 | 21.7166 | True |
| tau4_r25_o37_h05 | 0.226772 | 0.22567 | 0.000296339 | -0.249517 | 0.134571 | 0.524038 | 25.5176 | True |
| tau4_r25_o73_h05 | 0.226532 | 0.225491 | 0.000296729 | -0.177808 | 0.127563 | 0.44184 | 18.6696 | True |
| tau4_r35_o37_h05 | 0.00144953 | 0.00149393 | 3.84197e-06 | -0.241867 | 0.0434943 | 0.328973 | 24.3906 | True |
| tau4_r35_o73_h05 | 0.00145065 | 0.00149084 | 3.35407e-06 | -0.173579 | 0.0327095 | 0.239199 | 17.538 | True |
| tau6_r25_o37_h05 | 0.03251 | 0.0322991 | 4.33512e-05 | -0.27485 | 0.0822682 | 0.440907 | 27.8222 | True |
| tau6_r25_o73_h05 | 0.0324795 | 0.0322736 | 4.37436e-05 | -0.205631 | 0.0732033 | 0.354588 | 20.9514 | True |
| tau6_r35_o37_h05 | 0.000179532 | 0.000252713 | 3.76344e-06 | -0.271155 | 0.0546847 | 0.380442 | 27.3325 | True |
| tau6_r35_o73_h05 | 0.000185418 | 0.000254022 | 3.22361e-06 | -0.20301 | 0.043765 | 0.290406 | 20.4605 | True |
| tau4.5_r27_o19_h05 | 0.0762793 | 0.0758795 | 0.000101392 | -0.232695 | 0.0961848 | 0.429227 | 23.8014 | True |
| tau4.5_r27_o61_h05 | 0.0761978 | 0.0758076 | 0.000101743 | -0.174598 | 0.0912476 | 0.359146 | 17.7478 | True |
| tau4.5_r33_o19_h05 | 0.000114007 | 5.65946e-05 | 2.81561e-06 | -0.229855 | 0.0428448 | 0.315598 | 23.1738 | True |
| tau4.5_r33_o61_h05 | 0.00011084 | 5.76074e-05 | 2.32797e-06 | -0.169669 | 0.033249 | 0.23619 | 17.1179 | True |
| tau5.5_r27_o19_h05 | 0.0222488 | 0.022151 | 2.84251e-05 | -0.245949 | 0.0638256 | 0.375012 | 24.9143 | True |
| tau5.5_r27_o61_h05 | 0.0222285 | 0.0221306 | 2.87792e-05 | -0.186463 | 0.0554216 | 0.297995 | 18.8509 | True |
| tau5.5_r33_o19_h05 | 5.74173e-05 | 0.000124721 | 3.30149e-06 | -0.244419 | 0.0486654 | 0.341688 | 24.6385 | True |
| tau5.5_r33_o61_h05 | 6.24053e-05 | 0.000125555 | 2.81935e-06 | -0.184178 | 0.0390544 | 0.262254 | 18.5744 | True |

## Three-branch energy attribution
For every signed window and every additive ledger component, S−F=(S−L)+(L−F). This is an exact algebraic decomposition of specified trajectories. It is not a corresponding identity for positive-only or absolute-integral costs. Those nonlinear costs are recomputed directly from each paired PWM-cycle mean waveform. Signed grid energies use exact integration boundary snapshots.

Maximum computed signed-triangle residual across all34 cases and six windows is 0 J. The complete table has individual F/L/S gross grid, copper, load, bridge and stored-energy ledgers plus all three paired signed/nonlinear costs.

Nominal fine-step signed gross AC decomposition:

| Window | S−F J | S−L J | L−F J |
|---|---:|---:|---:|
| pre_onset | 0.000000000 | 0.000000000 | 0.000000000 |
| service | 134.914959366 | 69.218046705 | 65.696912661 |
| recovery | -0.235908268 | -0.215297809 | -0.020610459 |
| post_deadline | -0.000012788 | -0.000012153 | -0.000000636 |
| declared_onset_total | 134.679038310 | 69.002736744 | 65.676301566 |
| checkpoint_total | 134.679038310 | 69.002736744 | 65.676301566 |

Nominal fine-step recovery costs:

| Pair | signed J | positive-only J | absolute integral J |
|---|---:|---:|---:|
| S-F | -0.235908268 | 0.045360869 | 0.326629987 |
| S-L | -0.215297809 | 0.042352888 | 0.300003522 |
| L-F | -0.020610459 | 0.003140897 | 0.026892296 |

The whole-task positive/absolute integrals are much larger than the return-window metrics because S and L intentionally use different grid-power waveforms during service. For nominal S−L, the full checkpoint-to-final signed AC increment is69.002737 J, while positive-only energy is14248.770799 J and the absolute integral is28428.538862 J. No100J whole-task absolute-throughput claim is made.

The full nominal S−L signed grid increment is almost entirely extra copper loss: grid69.002736744 J versus copper69.002740913 J, leaving net-after-copper≈−4.17e−6 J and effectively equal final stored energy at the numerical resolution. This supplies the requested attribution relative to L without hiding reactive-current or load-shape copper losses. All ΔZ terms remain explicit; the controller still regulates W+B, not W+B+Z.

## Preservation, limitations and files
The preservation check covers 1457 existing files, including all earlier recovery artifacts and both root/public-core copies of FINAL_SCIENTIFIC_STATUS.json and RECOVERY_COMPLETE_MANIFEST.json; none changed.
Physical conclusions remain limited to the declared ideal switching plant, prescribed balanced grid, nominal known R/L/C, ideal sampled measurements, actual tested port tau/ramp, and one workload/service witness. Two integration steps demonstrate numerical consistency, not measurement accuracy. L is a deliberately strong feasible reference, not an optimized universal no-service policy.

- SUMMARY_PHASE3.json: complete branch/pair states, extrema, convergence, acceptance and signed identities
- ACCEPTANCE_PHASE3.csv: all34 row classifications
- ENERGY_ATTRIBUTION_PHASE3.csv: all six windows, F/L/S absolute ledgers and S−L/L−F/S−F paired increments
- SERVICE_REPLAY_IDENTITY.json: old-S exact replay proof
- PROTOCOL_PHASE3.json and EXECUTION_FREEZE_PHASE3.json: pre-result definitions, configuration set and hashes
- audit/: independent source/workload/energy/comparator assessment, without importing the implementation evaluator
- THREE_BRANCH_WORKLOAD_AND_POWER.png and THREE_BRANCH_ENERGY_ATTRIBUTION.png: visual branch comparison

No prior freeze is replaced. A separate PHASE3_INDEX/manifest provides the new stage’s stable entry point.
