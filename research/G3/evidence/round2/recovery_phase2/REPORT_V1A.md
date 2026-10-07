# G3 phase2: causal recovery, frozen V1A

## Result
All 18 runs (nominal and eight held-out physical/clock cases, each at two numerical resolutions) satisfy the measured physical hard bounds, service tracking tolerances, and finite-window W/B/current return tolerances. Four runs fail the full frozen contract: actual tau=4 ms and slew=25 MW/s at both onset offsets and both integration steps exceed the 5 kW incremental cP budget. V1A is therefore a qualified physical-recovery result, not an all-pass contract validation. No controller tuning followed those failures.

## Scope and contract separation
- The original core theory, admission witness and old sampled-current-PI/PWM failure results are unchanged. The 457-file before/after hash check reports no changes.
- The original core epsilon=100 J is a NET allowance in its prescribed late active-power cap over 0–0.2 s, with exact averaged P/Q and exact return. This phase instead allows finite tracking error and approximate W/B/current return by T+0.5 s, adds a matched-health recovery energy budget, and observes another 0.2 s of continuing operation. These are different contracts even when an observed recovery cost is below 100 J.
- The preconditioned controller adds a learned nominal DC bias during service and causal W/B restoration afterward. It is standard control, with no novelty claim. This does not retroactively turn the old exact-command switching experiment into a recovered trajectory.
- Only the primary a100/q600/n160 positive continuing-compute witness was used. The offered large-margin multi-cycle witness was not needed or run.

## Frozen controller and matched health
PROTOCOL_V1.json was preserved. The pre-result authoritative amendment PROTOCOL_V1A.json has SHA256 e781acb04587aac37eb5f8c3ba40980d17dc392beceb1a9c2d1e8b41ace5f2fc. Source, executable and campaign were frozen in EXECUTION_FREEZE.json before the first simulation.

At 10 kHz, cP=clip(100(21600−W)+2500 zW,±5000 W), with conditional-integrator antiwindup, and uB=clip(20(B−50000),±10000 W). One fixed 2 s nominal healthy warmup per numerical step produces the complete current/energy/battery/controller/PWM checkpoint. All actual tau/ramp holdouts start from that same nominal checkpoint at their resolution. No held-out bias calibration occurs.

During the service gate cP and zW are held, uB=0, and the original polynomial port feedforward is unchanged. Recovery resumes the same controller against constant setpoints; d=650 kW continues and no state reset occurs. Service and no-service comparator use identical gate, grid and carrier clocks; the healthy fork has only nominal P/Q/d/u feedforward. The comparator is an offline evaluator, never an online controller input. Actual tau/ramp enter only the plant. Offset37/73us is an actual onset on a continuously advancing absolute clock, not a relabelled or rotated state.

Inherited current-loop feedforward evaluates the known authorized schedule at the PWM midpoint. At the 37 us onset, this can affect the short checkpoint-to-onset interval. Its energy is separately reported and included in checkpoint-to-final totals. It is not future measured-workload feedback.

## Health qualification and baseline costs
Independent identical no-service processes are bitwise equal. At both steps, last-five-cycle nominal warmup changes are <1.5e−9 J in W and <1.3e−9 A in phase currents, with B unchanged, against frozen 0.1 J/0.2 A qualification thresholds. Final matched healthy cycles also qualify.
- h1: healthy average cP=52.408896 W; held pre-service cP=45.125219 W; actual healthy mean grid power above model baseline=1.134258 W; one-time 2 s warmup AC increment vs model baseline=2.325550 J
- h05: healthy average cP=52.418233 W; held pre-service cP=45.134431 W; actual healthy mean grid power above model baseline=1.144732 W; one-time 2 s warmup AC increment vs model baseline=2.346502 J

The approximately 52 W command correction compensates sampled-loop tracking bias; it is not 52 W of extra physical load. The actual ongoing grid increment is approximately 1.14 W. The PWM-boundary healthy W ripple is about0.166 J; dense1us healthy W ripple is about10.12 J, with sampled mean W offset about0.055 J. Both are reported rather than conflating stroboscopic and switching ripple.

## Frozen tolerances and tested coverage
- Hardware: V1080–1320 V, each phase and space-vector current≤1500 A, B0–100 kJ, |b|/|u|≤450 kW, and actual declared physical slew; modulation utilization reported
- Service: actual and authorized nominal P/Q averaged over the same ten20ms bins; max errors≤2 kW and≤10 kvar
- Return: throughout final five20ms cycles ending at T+0.5 s, dense common-clock |ΔW|/|ΔB|≤2 J and each |Δi_phase|≤2 A
- Budget during T toT+0.5 s: max |service cP−healthy cP|≤5 kW; |signed|, positive-only and absolute-integral incremental grid energies each≤1 kJ
- Nominal actualtau5ms/slew30MW/s/onset0, then previously unrun factorial actualtau4/6ms × slew25/35MW/s × onset37/73us, each integrationstep1/0.5us. Nominal command model remains5ms/30MW/s
- Signed energies use physical midpoint quadrature and boundary snapshots. Positive-only and absolute-integral metrics use matched PWM-cycle mean active power; they are not instantaneous switching-power absolute integrals

## Fine-step acceptance table

| Case | physical/tracking/return | max ΔW J | max ΔB J | max Δi A | max incremental cP W | recovery signed J | positive J | absolute J | full contract |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| nominal_h05 | pass | 6.39954e-05 | 2.96248e-07 | 2.82628e-06 | 23.793 | -0.235908 | 0.045 | 0.327 | PASS |
| tau4_r25_o37_h05 | pass | 0.14239 | 0.22567 | 0.00238954 | 5059.153 | -0.246987 | 328.299 | 656.850 | FAIL cP |
| tau4_r25_o73_h05 | pass | 0.142226 | 0.225491 | 0.00238957 | 5059.183 | -0.147062 | 328.343 | 656.842 | FAIL cP |
| tau4_r35_o37_h05 | pass | 0.000910343 | 0.00149393 | 1.62754e-05 | 2241.522 | -0.278332 | 9.736 | 19.751 | PASS |
| tau4_r35_o73_h05 | pass | 0.000907438 | 0.00149084 | 1.6268e-05 | 2262.505 | -0.181817 | 9.838 | 19.858 | PASS |
| tau6_r25_o37_h05 | pass | 0.02564 | 0.0322991 | 0.000227648 | 4945.592 | -0.299578 | 157.191 | 314.682 | PASS |
| tau6_r25_o73_h05 | pass | 0.0256103 | 0.0322736 | 0.000227674 | 4945.592 | -0.202133 | 157.258 | 314.722 | PASS |
| tau6_r35_o37_h05 | pass | 0.000123529 | 0.000252713 | 4.43614e-06 | 1455.915 | -0.307802 | 5.710 | 11.728 | PASS |
| tau6_r35_o73_h05 | pass | 0.00012387 | 0.000254022 | 4.2743e-06 | 1454.973 | -0.211433 | 5.793 | 11.798 | PASS |

All coarse-step classifications match fine-step classifications. The failed corners have service cP=−5000 W while healthy cP≈+59.18 W; the absolute controller clip therefore does not enforce the stricter paired incremental bound. These four failures are retained.

Across all18runs, voltage extrema are1119.680–1262.805 V; peak absolute phase current971.585 A and space-vector amplitude992.968 A. Maximum grid-cycle P error98.929 W and Q error533.870 var are well within the predeclared tolerances. Actual command and ramp saturations, instantaneous P/Q extrema, all integrator/duty states, and endpoint differences are retained in SUMMARY_V1A.json. Physical return does not assert exact equality of the complete controller state.

## Energy accounting
ENERGY_COST_TABLE_V1A.csv contains every case and window, gross AC energy, copper losses, signed/positive/absolute incremental costs, net-after-copper increments against both matched health and the theoretical model baseline, and stored-energy/load/loss residuals. Windows include checkpoint→onset, service, recovery, post-deadline, declared-onset→final and checkpoint→final. The model baseline is P=654498.72485653043 W with copper loss4498.72485653043 W and net650000 W.

Nominal fine-step example:

| Window | gross AC Δ vs health J | net-after-copper Δ vs health J | gross AC Δ vs model J | net-after-copper Δ vs model J | positive vs health J | absolute vs health J |
|---|---:|---:|---:|---:|---:|---:|
| service_cost | 134.914959364 | 0.232671703 | 133.679392849 | -1.208380728 | 3635.887945 | 7136.860931 |
| recovery_cost | -0.235907953 | -0.232663883 | 1.787012055 | 1.206247512 | 0.045358 | 0.326624 |
| post_deadline_cost | -0.000012780 | -0.000012606 | 0.224908105 | -0.000658696 | 0.000000 | 0.000013 |
| checkpoint_total_cost | 134.679038631 | -0.000004786 | 135.691313008 | -0.002791912 | 3635.933303 | 7137.187568 |

Recovery net energy magnitude is below100 J in every tested case, indeed below0.31 J, but absolute throughput reaches656.85 J. Reporting only signed energy would hide substantial return-control cycling in the constrained4ms/25MW/s corners. Whole-service gross increments include reactive-current copper losses and need not be below100 J. None of these observations is a same-core-contract validation.

The physical identity used is Δ(W+B+L|i|²/2)=∫(Pgrid−R|i|²−d)dt. Pair subtraction preserves the same identity. Maximum full-trajectory numerical identity error is0.010868 J at1us and lower at0.5us. Maximum coarse/fine PWM-boundary W discrepancy is0.000622 J, B discrepancy<0.000019 J and phase-current discrepancy<0.000081 A; these comfortably pass the frozen numerical-quality checks. Nominal battery/ramp limiter contact is reported and is allowed by the contract; “all limiters off” is not the health criterion.

## Reproduction and evidence
1. Compile recovery.cpp using the compiler command in the execution record or g++ -O3 -std=c++17 recovery.cpp -o recovery
2. Run python run_campaign.py warmup, then nominal, then holdout with the bundled virtual environment
3. Run python summarize.py and python make_report.py
4. Inspect EXECUTION_FREEZE.json, COMMON_CLOCK_IDENTITY.json, checkpoint_h1.csv/checkpoint_h05.csv, SUMMARY_V1A.json, *_snapshots.npz, *_dense.npz, *_bins.npz, ENERGY_COST_TABLE_V1A.csv, ACCEPTANCE_TABLE_V1A.csv and the independent audit/ files

No parameter, workload, initial condition, threshold or gain was repaired after observing holdouts. Any repair requires a separately numbered protocol and must retain V1A as failed on the four incremental-power cells.
