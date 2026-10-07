# Independent V2 recovery audit: PASS for the declared finite experiment

Date: 2026-10-03 UTC. Scope: the original alpha100 kW / q600 kvar interior witness in an ideal 10 kHz binary-PWM three-phase model, with positive prescribed compute load. All writes by this auditor remain in recovery_phase2/audit/.

## Decision and provenance

All 34 V2 runs pass the frozen finite contract: one nominal configuration, eight previously seen regression configurations, and eight fresh confirmation configurations, each at 1 us and 0.5 us. These are 17 configurations with numerical refinements, not 34 independent physical samples.

The prior V1A remains failed in two held-out configurations (four numerical rows) because its incremental cP exceeds 5 kW. V2 is a separately numbered, pre-result-frozen revision with tighter 100 J signed/positive/absolute recovery budgets. Its success does not relabel V1A or turn regression cases into held-out ones.

All 437 core SCIENCE_MANIFEST files, all V1A_COMPLETE_FREEZE files, and all frozen V2 source/protocol/driver/evaluator/input hashes were verified unchanged. V2 protocol and ledger addendum were reviewed and saved before any fresh confirmation output existed.

## What the revised controller uses

The source diff from V1A is only (a) measured error (Wset+Bset)-(W+B), replacing Wset-W, and (b) an absolute +/-4.5 kW correction limiter/anti-windup threshold replacing +/-5 kW. Gains and inventory restoration remain fixed. It reads current physical W/B, currents, its own integral state and an authorized known schedule; it never reads the matched healthy trajectory, future actual workload or actual held-out tau/ramp.

W+B is capacitor-plus-inventory energy. It is not all physical stored energy: the filter energy Z remains separate. Exact identities are

    d(W+B)/dt = p_bridge - load = P_grid - copper_loss - load - dZ/dt
    Z = (L/2) sum(i_abc^2)

Only the internal battery transfer b cancels. The filter-energy derivative is a real transient disturbance, not a copper-loss term. The implementation assumes exact, noiseless W/B sensing sampled at 10 kHz without an added measurement filter. Small simulated state differences are numerical diagnostics, not sensor accuracy claims.

## Independent acceptance results

|Group|Configurations × steps|max paired W J|max paired B J|max phase difference A|max absolute recovery J|max incremental cP W|
|---|---:|---:|---:|---:|---:|---:|
|Nominal|1 × 2|0.00006385|0.00000030|0.00000283|0.326630|23.7934|
|Known regression|8 × 2|0.226772|0.225670|0.00029663|0.565316|31.5206|
|Fresh confirmation|8 × 2|0.0762781|0.0758795|0.00010160|0.460614|27.8218|

Frozen thresholds: W/B 2 J, per-phase current 2 A over the final five phase-aligned 20 ms cycles; incremental cP 5000 W; signed magnitude, positive-only and absolute recovery grid increments each 100 J. Net recovery increments range from -0.311569 J to -0.172792 J. Positive/absolute budgets use phase-matched PWM-cycle mean active power; signed energy uses exact accumulated quadrature at milestones.

All 20 ms service-bin errors pass: maximum active error 98.929 W and reactive error 533.871 var, versus 2 kW/10 kvar ceilings. These are approximate measured service tolerances, not exact P/Q delivery.

Both service and healthy hard-bound records pass. Across the service runs: Vdc 1119.680-1262.805 V; current-vector peak 993.426 A; inventory 35.364-50.959 kJ; |b| peak 434.689 kW; requested |u| peak 449.999969 kW; maximum circle utilization 0.974973. Physical slew limits are active and reported. There is no PWM or u clipping, W/B clamp, workload shedding or state reset.

## Complete state, real clocks and pre-onset action

One nominal 2 s V2 warmup checkpoint per dt is reused across every actuator/offset case. All relevant states are cloned: abc currents, W/B/b, both current-PI integrals, capacitor-plus-inventory PI integral, held/current cP, inventory output, gate flag and held duty. Paired snapshots equal the shared checkpoint exactly. Actual grid and carrier phases continue at absolute 2 s; offsets change real onset, not labels. Independent healthy fork equality is bitwise, and all dynamic hold/anti-windup/gate checks pass.

The midpoint current feedforward reads authorized scheduled P/Q values and derivatives. When onset is before the first 50 us midpoint (19 or 37 us), this permits causal anticipatory action before onset; it does not read future actual d. Consequently initial checkpoint states are identical but onset states may differ. Pre-onset grid increments are explicitly recorded (down to -0.0712745 J), and checkpoint-through-observation totals include them.

The whole checkpoint-through-observation paired grid increment is 134.614-134.732 J, including the intended service trajectory, its copper compensation and all later effects. It is not the same quantity as the post-service 100 J engineering recovery budget or the core theorem’s 100 J slack allowance. No exact-contract PWM transfer is inferred.

The healthy physical orbit itself qualifies on PWM-boundary and common 1 us samples. Its phase-resolved W ripple is approximately 10.12 J peak-to-peak, so the paired 2 J return tolerance is phase-aligned and must not be compared to a flat DC setpoint without accounting for the orbit. Physical compute load remains the original positive schedule and then continues at 650 kW through 0.2 s after the deadline.

## Filter-energy bound and separate conservation ledger

If each branch has space-vector current at most Imax=1500 A and every phase difference is at most delta=2 A, then

    |Delta Z| <= (L/2)||i_s+i_h||_2 ||i_s-i_h||_2
    <= L Imax delta sqrt(4.5) = 1.909188309 J

This instantaneous algebraic bound is independent of the chosen controller. The experiment verifies its premises at its evaluation samples, not at all mathematically continuous times. Direct Cauchy bounds were independently checked pointwise against the actual paired traces.

Observed paired filter-energy maxima are 0.01438134 J over recovery PWM-boundary samples, 0.00009468599 J over the final common 1 us grid, and 0.000001546586 J over post-deadline PWM samples. These are sampled maxima on different declared grids. At every sampled state the stored Z equals L*sum(iabc^2)/2 exactly.

FULL_ENERGY_LEDGER.csv contains 204 independently recomputed window rows: pre-onset, service, recovery, post-deadline, onset-through-observation, and checkpoint-through-observation for all 34 runs. Each keeps gross grid energy, copper, load, bridge/battery energy, Delta W, Delta B, Delta Z, grid-after-copper and both baseline and paired increments separate. The largest paired conservation residual is 6.71e-5 J. The maximum post-deadline signed incremental grid magnitude is 0.000236 J, so no material energy debt appears in the declared extra observation window.

## Numerical quality and reproduction

- Maximum single-run case energy residual is 0.010882 J, below the 0.1 J quality target
- On the full shared PWM grid, coarse/fine differences are at most 8.19e-5 J for W, 1.82e-5 J for B and 1.40e-5 A for phase current; deadline and observation-end quality checks pass
- A fresh confirmation run (tau4.5 ms/R27 MW/s/onset19 us, 0.5 us) was independently rerun. Main trace, snapshots, service bins, dense arrays and extrema reproduce exactly
- Pre-run protocols and source hashes are copied into this audit directory; the independent scripts import no primary evaluation code

## Limits that remain

This is finite configuration evidence for one interior alpha100/q600 service witness in the ideal model. It does not certify the near-boundary 808 kvar witness, every tau/ramp in an interval, full fault/noise/PLL/device-loss robustness, or real compute hardware.

Complete controller-state/duty differences are provided as diagnostics but have no frozen pass thresholds; only the declared physical W/B/current finite-window return was accepted. Exact finite-time return, perfect nominal P/Q and indefinite complete-orbit recovery are not established. Numerical hard maxima are midpoint/endpoint sampled extrema, not rigorous continuous-time certificates.

The local unsaturated mean-model explanation is useful, but is not a stability theorem for the sampled, gated, saturated, switched plant. The standard PI coordinate choice and inventory feedback should not be advertised as a new controller invention.

## Per-configuration fine-step state/cost table

|tau ms / R MW/s / onset us|Type|max Delta W J|max Delta B J|max phase Delta i A|absolute recovery J|peak incremental cP W|
|---|---|---:|---:|---:|---:|---:|
|5/30/0|nominal|6.370181e-05|2.961169e-07|2.826728e-06|0.32663|23.79337|
|4/25/37|regression|0.2267723|0.2256695|0.0002965093|0.5653114|29.20957|
|4/25/73|regression|0.2265266|0.2254913|0.0002966308|0.4532611|19.52353|
|4/35/37|regression|0.001449788|0.001493927|3.608678e-06|0.3746752|28.08736|
|4/35/73|regression|0.001445641|0.001490843|3.428394e-06|0.2514593|18.39191|
|6/25/37|regression|0.03251025|0.03229909|4.352183e-05|0.4841932|31.52025|
|6/25/73|regression|0.03247449|0.03227356|4.364577e-05|0.3664435|21.80525|
|6/35/37|regression|0.0001797883|0.0002527132|3.500497e-06|0.4263185|31.03052|
|6/35/73|regression|0.0001804112|0.0002540219|3.293479e-06|0.3026474|21.3143|
|4.5/27/19|fresh|0.07627806|0.07587947|0.0001014892|0.4606115|26.70863|
|4.5/27/61|fresh|0.07619183|0.07580762|0.0001015973|0.3650836|18.0622|
|4.5/33/19|fresh|0.0001152365|5.659459e-05|2.644178e-06|0.3520219|26.08105|
|4.5/33/61|fresh|0.0001168264|5.760739e-05|2.471232e-06|0.2421721|17.43224|
|5.5/27/19|fresh|0.02224754|0.02215098|2.852203e-05|0.409983|27.82153|
|5.5/27/61|fresh|0.02222251|0.02213063|2.863319e-05|0.3040527|19.16525|
|5.5/33/19|fresh|5.618753e-05|0.0001247206|3.129921e-06|0.3781509|27.54582|
|5.5/33/61|fresh|5.641912e-05|0.0001255547|2.946444e-06|0.2681894|18.88881|

## Audit entry points

- audit_recovery_v2.py and INDEPENDENT_RESULTS.json: all independent pass/fail calculations and frozen-hash checks
- FINAL_STATE_COSTS.csv: 34 rows with final-window and endpoint state, pre-onset, recovery and post-deadline costs
- audit_energy_ledgers.py, FULL_ENERGY_LEDGER.csv and FILTER_ENERGY_AUDIT.json: separate physical ledgers and Z bounds
- DYNAMIC_GATE_IDENTITY_CHECK.json: shared state, healthy identity and actual service gate checks
- CONVERGENCE_INDEPENDENT.json and REPRODUCIBILITY_CHECK.json: numerical quality and independent replay

V1A failure report and evidence remain one directory above, unchanged.
