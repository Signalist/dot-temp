# Independent V1A audit: fail the full declared contract; physical recovery passes

Audit completed for the nominal case and eight predeclared held-out configurations, each at 1 us and 0.5 us. This is nine configurations and 18 numerical runs, not 18 independent physical samples.

## Decision

- Nominal and six of eight held-out configurations pass the entire frozen V1A contract
- The two tau=4 ms/ramp=25 MW/s configurations (37 and 73 us offsets) fail the incremental correction-power budget at both resolutions
- Every run passes the frozen approximate W/B/current return, healthy periodicity, hard bounds, service tracking, and signed/positive/absolute recovery-energy budgets
- The controller is causal and uses only present measurements, its own past state, constant setpoints and the authorized schedule; the healthy branch is an offline comparator
- Original exact-command PWM DC recovery remains failed. This is a different, approximate-service contract with warmup and explicit correction resources

## Final-window return and recovery cost

Fine-step rows below; the independent CSV contains both resolutions, deadline state and post-deadline cost. The return values are maxima over the final 100 ms, not only a favorable endpoint. Positive/absolute energies use phase-matched PWM-cycle means. Net energy uses exact stored quadrature at the declared milestones.

|Configuration (tau ms/R MW/s/offset us)|max ΔW J|max ΔB J|max phase Δi A|net grid J|positive J|absolute J|peak incremental cP W|Full result|
|---|---:|---:|---:|---:|---:|---:|---:|---|
|5/30/0|6.39954e-05|2.96248e-07|2.82628e-06|-0.235908|0.0453578|0.326624|23.792924|PASS|
|4/25/37|0.14239|0.22567|0.00238954|-0.246987|328.299|656.85|5059.153143|FAIL: cP budget|
|4/25/73|0.142226|0.225491|0.00238957|-0.147062|328.343|656.842|5059.182620|FAIL: cP budget|
|4/35/37|0.000910343|0.00149393|1.62754e-05|-0.278332|9.73608|19.7506|2241.522464|PASS|
|4/35/73|0.000907438|0.00149084|1.6268e-05|-0.181817|9.8379|19.8578|2262.505108|PASS|
|6/25/37|0.02564|0.0322991|0.000227648|-0.299578|157.191|314.682|4945.591750|PASS|
|6/25/73|0.0256103|0.0322736|0.000227674|-0.202133|157.258|314.722|4945.591752|PASS|
|6/35/37|0.000123529|0.000252713|4.43614e-06|-0.307802|5.70993|11.7276|1455.914692|PASS|
|6/35/73|0.00012387|0.000254022|4.2743e-06|-0.211433|5.79331|11.7979|1454.972921|PASS|

The resource failure is not an integration-error ambiguity: the largest incremental correction is 5059.182620 W, while the frozen ceiling is 5000 W. The absolute service correction clips at -5000 W when the healthy correction is approximately +59.18 W. Replacing the paired incremental constraint by an absolute control bound would change the protocol after seeing results. V1A remains failed.

## Initial state, preview and causality

All paired branches load an identical complete nominal warmup checkpoint for their numerical resolution. The same checkpoint is reused across all actual actuator/offset cases, and all input command/model hashes are unchanged. Current-PI and DC-PI integrals, held outputs, gate flag, duty and actual physical states were checked against the checkpoint. Absolute grid and carrier clocks continue from 2 s. Two separately executed healthy forks are bitwise identical.

The known P/Q schedule is evaluated at the next PWM half-period. At a 37 us onset, the first half-period is 13 us into the schedule, so action starts before the stated onset. It previews scheduled P=Pbase-260 W, Q=1560 var and their derivatives (-20 MW/s, 120 Mvar/s). It does not preview actual load measurements or read the healthy trajectory. At onset the fine-step paired difference is ΔW=+0.852031 J, Δfilter=-0.922327 J, Δgrid=-0.0712745 J and max phase Δi=2.69546 A. At 73 us, the first midpoint precedes onset and onset states match. Thus checkpoint states match; onset states need not. PREONSET_PREVIEW_AUDIT.json supplies the separate ledger. V1A costs were frozen as onset-to-observation; adding the omitted pre-onset grid term changes the whole-observation increment by -0.0712745 J for 37 us cases. It does not rescue or cause the cP budget failure.

## Warmup, phase alignment and continuing work

One fixed 2 s causal nominal warmup is used per dt; there is no held-out fitting. At 0.5 us the one-time warmup consumes 1,308,999.796215 J grid energy and 1,300,000 J compute energy, including 8,999.706716 J copper loss. Its grid energy above the model baseline is 2.346502 J. Learned pre-service cP is about 45.1344 W and is held throughout service. It is not a free hidden controller bias.

The warmup cycle differences are below 1.5e-9 J and 1.3e-9 A at matched PWM boundaries. Dense 1 us physical samples also qualify final healthy periodicity. The true healthy DC-energy ripple is about 10.1199 J peak-to-peak, with mean about 0.0553 J above Wset; therefore a meaningful return comparison must align phase. A 2 J paired return tolerance is not a claim that instantaneous healthy W is always within 2 J of a flat Wset.

Compute follows the identical authorized positive 350-950 kW schedule, then 650 kW continuously through the 0.2 s observation after the recovery deadline. No workload clipping, shedding, rescheduling, reset or retrospective compression occurs.

## Numerical and physical checks

- All 437 frozen SCIENCE_MANIFEST files are unchanged; protocol, controller executable/source, driver and original schedule hashes also remain unchanged
- Every hard-bound audit includes healthy and service branches, phase and vector current, voltage, inventory, b/u/ramp, duty span and circular modulation. No PWM or u command clipping occurs. Physical slew limiting does occur and is fully exposed, including a small nominal requested-rate alteration
- Maximum case energy-closure residual is 0.010868 J at the coarse step; the largest checked coarse/fine deadline W/B/current difference is 5.026e-6 in the corresponding units, comfortably below the 0.1 quality thresholds
- Signed grid/loss/load/stored-energy identities were independently recomputed at service end, deadline and observation end. Positive/absolute budget values were independently reconstructed from cycle means with clipped boundary durations
- The worst failed fine-step run was rerun into the audit directory and reproduced extrema, full PWM trace, all snapshots, bins and dense arrays exactly
- Full numerical extrema include RK midpoints/endpoints; these are not rigorous interstep extrema proofs. No exact finite-time return or indefinite orbit theorem follows

## Interpretation limits

The new recovery budget and horizon do not coincide with the core averaged-model 100 J slack contract. Even a post-service net increment below 100 J does not establish transfer of that exact core contract to PWM. The positive/absolute throughput is materially larger than the small signed net in several cases.

The eight held-out configurations give finite evidence, not a uniform robustness guarantee over every tau/ramp value in a box. Complete controller-state differences are diagnostics without frozen tolerances; only physical W/B/current finite-window recovery was accepted. The limited mean-model Hurwitz argument is valid within its stated continuous, local, unsaturated assumptions and is not a hybrid-PWM stability proof.

## Audit artifacts

- INDEPENDENT_RESULTS.json: all 18 independent decisions and ledgers
- FINAL_STATE_COSTS.csv: both-resolution final-state/cost table
- STATIC_CODE_AUDIT.md: control, state, clock and saturation inspection
- PHYSICAL_WAVEFORM_DIAGNOSTICS.json: true phase-aligned dense health checks
- PREONSET_PREVIEW_AUDIT.json: pre-onset state and energy accounting
- REPRODUCIBILITY_CHECK.json: independent deterministic replay
- PROTOCOL_*_REVIEW*.json: pre-result protocol review and exact saved bytes
- audit_recovery.py: independent, read-only parsing and recalculation entry point
