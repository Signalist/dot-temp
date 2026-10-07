# G6 positive compute-load operating-point study

## Fixed nominal point and physical interpretation

The local pre-outcome configuration in POSITIVE_WORKPOINT_FREEZE.json fixes one new Kundur-full workpoint: two genuinely added constant-PQ compute loads, +50 MW at bus 7 and +50 MW at bus 8, each Q=0 Mvar. Positive active power is consumption. The original background loads and generator/controller/network parameters are unchanged; original demonstration events remain disabled. Power flow is recomputed using the original slack, with no favorable redispatch or nominal-point retuning.

The original slack generator's initialized active output moves from 726.802921 to 840.176146 MW. The other three generators remain at 700 MW each. The extra 113.373224 MW covers 100 MW added compute and 13.373224 MW additional network losses. POWER_BALANCE_AND_PHYSICAL_SCOPE.json records initialized active/reactive generation and bus voltages. Static Slack p/q variables are inactive after dynamic replacement; the reported balance uses initialized GENROU p0/Pe, not those inactive entries.

Each compute port obeys P_i(t)=50+deltaP_i(t), Q_i(t)=0. Thus rho on ray a=(a1,a2) must satisfy rho<=min_i(50/a_i). This physical clipping is explicit in positive_physical_rays.csv. None of the 41 proper common/dynamic/independent inner boundaries reaches its physical clipping cap. Even1.02 times every proper outer boundary leaves minimum compute demand at least19.551MW; all117 exported separation decisions leave at least21.256MW (PHYSICAL_AMPLITUDE_AUDIT.json). The reset witness is capped at rho=98 MW total, keeping both compute loads >=1 MW.

## Qualification, including an initially failed probe

- Fresh Newton–Raphson power flow converges in5 iterations to2.84e-14 maximum mismatch, and TDS initialization passes (POWERFLOW_RECHECK.json independently rebuilds identical initial states); initial maximum f/g residuals are 2.22e-16 / 2.8e-14
- A 10-second unforced original nonlinear trace stays stationary: max state drift 1.33e-15; max algebraic drift 2.2e-14; frequency deviation 0 Hz
- A fresh 51-state gauge quotient is exported from the new operating point; max real eigenvalue is -0.141452523 /s. The old A was not reused: max absolute A change is 1.230204
- The largest resolvent relative error is 2.05e-14; eigenvector condition number is 1.27e+04
- Physical-tangent central differences of original DAE residuals, including each active input column, have max relative error 4.69e-09. Small 0.1/0.05 MW pulse errors shrink consistently and are separately stored

The initial arbitrary full-coordinate derivative probe failed at relative error 0.0017417. That result and original script are preserved in QUALIFICATION_initial_sink_probe.json and qualify_positive_initial_sink_probe.py. The entire error was the artificial, unnamed algebraic sink at global index196, introduced by ANDES compaction for partially replaced devices. Its Jacobian row/column have only diagonal1, with zero input and physical coupling; installed ANDES system/facade.py explicitly inserts this numerical identity. Its physical residual stays zero. The correction holds this disconnected sink fixed when differentiating physical directions. It does not change the model, A/B/C, test tolerance, nominal point or dispatch. DERIVATIVE_PROBE_CORRECTION.json and diagnose_derivative.py preserve the diagnosis.

Important voltage limitation: nominal bus7 voltage is 0.945044pu and bus8 is 0.948743pu. The lowest nominal voltage is below an illustrative 0.95pu planning floor. Passing power flow, equilibrium, and frequency-transfer qualification does not establish voltage hosting, VRT, line/thermal limits, or deployability. This study freezes the frequency criterion |Delta f_g|<=0.05Hz only.

## Same-information supports and 41-ray LTI boundary brackets

Use q1=[1,1,-1,-1], q2=[1,-1,-1,1] on four half-second segments of each T=2s block. Every full block has exactly zero incremental energy at each port. The contracts are:

1. Committed common block sign with fixed amplitude allocation
2. Dynamic optional amplitudes in [0,a_i] with one shared sign per block
3. Independent signed ports, explicitly an information relaxation

The original support/Minkowski-sum formulas are reused at the new linearization; no solver novelty is claimed. Dynamic support equals half(common+independent) pointwise and agrees with explicit vertex support to 1.3e-18. Every ray, every generator frequency, all startup histories, and phase within the block are included in the conditional LTI envelope.

Equal-split total-amplitude boundary brackets, MW:

| Contract | Analytic-bound numerical inner | Finite-witness outer |
|---|---:|---:|
| Common committed | 29.079654 | 29.145285 |
| Dynamic optional | 27.557388 | 27.616321 |
| Independent signed | 24.301811 | 24.347631 |

At equal split, the bracket-separated dynamic-vs-independent gain is at least 13.183%; common-vs-independent is 19.435%. Across all41 rays, maximum corresponding lower gains are 25.579% and 35.582%.39 interior rays separate each proper-contract comparison; endpoint rays coincide.

The support uses 256 past blocks and 2048 phase intervals. At equal split the analytic modal tail is 1.05e-37 Hz/MW and the phase interpolation upper error is 3.87192367e-06 Hz/MW. The maximum all-ray relative committed-envelope error is 0.2369%, so the frozen refinement rule did not trigger. Error comes from geometric modal tails plus a Lipschitz phase bound that includes both one-sided derivatives at all segment boundaries. This is floating-point evaluation of proven-formula conditional LTI bounds, without directed-rounding/interval certification. It is not a nonlinear robustness theorem.

## Matched full finite nonlinear replays

Selection was frozen before nonlinear outcomes: equal split .98 times each proper inner and1.02 times each proper outer boundary, plus .98*min(reset inner,100 MW) on the common-contract all-history maximizing word. Every replay executes the complete257-block word with carried electrical state, from the same new positive equilibrium, with1s preroll and20s ringdown. All final blocks remain complete. Primary dt=1/128s; dynamic margin pair and reset witness repeat at1/256s. Event breakpoints are explicitly registered; event epsilon is1e-4s. Input NPZ/CSV files include actual compute power. POSITIVE_NONLINEAR_CASES.json freezes source hashes and selected capacities.

All10 predeclared original nonlinear replays completed to535s, with actual compute power nonnegative at both ports in every sample and schedule segment. Each forcing word retains all257 complete blocks and the same newly balanced positive initial state.

| Case | dt(s) | Total max deviation(MW) | LTI peak(Hz) | Nonlinear sampled peak(Hz) | Min compute(MW/port) | V range(pu) | Frequency result |
|---|---:|---:|---:|---:|---:|---:|---|
| committed_inner_dt128 | 0.00781250 | 28.498061 | 0.04888966 | 0.04977960 | 35.750970 | 0.929753–1.010891 | below0.05Hz |
| committed_outer_dt128 | 0.00781250 | 29.728191 | 0.05100000 | 0.05197414 | 35.135904 | 0.929067–1.011349 | exceeds0.05Hz |
| dynamic_optional_inner_dt128 | 0.00781250 | 27.006240 | 0.04889543 | 0.04973949 | 36.496880 | 0.929031–1.011414 | below0.05Hz |
| dynamic_optional_inner_dt256 | 0.00390625 | 27.006240 | 0.04889543 | 0.04972088 | 36.496880 | 0.929033–1.011413 | below0.05Hz |
| dynamic_optional_outer_dt128 | 0.00781250 | 28.168648 | 0.05100000 | 0.05192293 | 35.915676 | 0.928312–1.011890 | exceeds0.05Hz |
| dynamic_optional_outer_dt256 | 0.00390625 | 28.168648 | 0.05100000 | 0.05190354 | 35.915676 | 0.928314–1.011889 | exceeds0.05Hz |
| independent_ports_inner_dt128 | 0.00781250 | 23.815775 | 0.04890780 | 0.04917310 | 38.092113 | 0.929166–1.011378 | below0.05Hz |
| independent_ports_outer_dt128 | 0.00781250 | 24.834583 | 0.05100002 | 0.05128518 | 37.582708 | 0.928456–1.011850 | exceeds0.05Hz |
| reset_false_admission_dt128 | 0.00781250 | 98.000000 | 0.16812325 | 0.18263230 | 1.000000 | 0.887487–1.034970 | exceeds0.05Hz |
| reset_false_admission_dt256 | 0.00390625 | 98.000000 | 0.16812325 | 0.18255393 | 1.000000 | 0.887488–1.034971 | exceeds0.05Hz |

Fine-step comparison (same inputs and full histories):
- dynamic_optional_inner: coarse/fine sampled peaks 0.049739488/0.049720880Hz; absolute difference 1.86e-05Hz; same finite frequency classification=True
- dynamic_optional_outer: coarse/fine sampled peaks 0.051922926/0.051903535Hz; absolute difference 1.94e-05Hz; same finite frequency classification=True
- reset_false_admission: coarse/fine sampled peaks 0.182632303/0.182553930Hz; absolute difference 7.84e-05Hz; same finite frequency classification=True

At the physically capped98MW reset-error case, the invalid reset screen predicts at most0.04215818Hz, while the carried-state finite nonlinear witness reaches0.18255393Hz at fine step. Actual compute power remains >=1MW each. Thus the false-admission example does not rely on negative compute load. The associated proper common-contract LTI envelope is0.16850269Hz, correctly rejecting this amplitude.

Every case has exactly50MW mean compute demand per port and zero incremental energy per full block. Under the explicit affine law only, each block delivers2*wbar_i work and the complete514s forcing word514*wbar_i. POSITIVE_NONLINEAR_TABLE.csv includes the full requested-input/work/frequency/voltage ledger.

These finite numerical checks support boundary interpretation only for the selected words at this one nominal point. They do not validate every nonlinear word, all physical operating constraints, or actual compute throughput. In particular, observed low voltages rule out interpreting the frequency-only result as full grid hosting certification.

## Finite-work scope

Work preservation is conditional on the explicit affine law w_i(t)=wbar_i+kappa_i*deltaP_i(t), with wbar_i>=|kappa_i|a_i. Then every complete2s block executes exactly2wbar_i work units, independent of common sign and optional amplitude; sum(q_i)=0 gives this identity. The selected waveforms have exact zero block-integral residual in their generation check. No empirical workload calibration, power-to-work conversion, admission latency measurement, queueing guarantee or nonlinear family-wide operational guarantee is claimed.

## Independent checks

The separate audit script `../audit/independent_positive_checks.py` and evidence `../audit/INDEPENDENT_POSITIVE_RESULTS.json` recompute positive-descriptor resolvents at four additional complex frequencies, selected support maxima, full chronological schedules, block energies and nonnegative actual compute powers. The largest independent resolvent relative error is8.08e-12. The application-level audit is tracked in `../audit/INDEPENDENT_PROOF_AUDIT.md`; consult that audit for independent verification of the complete nonlinear package.
