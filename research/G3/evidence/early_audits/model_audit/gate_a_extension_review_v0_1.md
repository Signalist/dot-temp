# Gate A extension: independent pre-freeze model audit

Date: 2026-10-02 UTC. Status: review only; no new simulation executed. This document does not approve or perform Gate B or controller-performance search. All numerical thresholds below that are not already in V2.1 are recommendations to be explicitly accepted in the new frozen JSON.

## Decision

The twelve-condition extension is suitable for bounded model checks: four signed steady points, four same-quadrant outward steps, three analytically preselected balanced source-voltage dips, and one signed periodic forcing with a deterministic loss-compensation calibration. Keep the original physical resources, limits, controller equations, sample order, and delay unchanged. Separate numerical agreement, constraint compliance, limiter release, tracking, and recovery results. A test can pass an implementation/conservation check while failing physical constraints.

The causal bias calibration is acceptable as an instrumented model-bench procedure. Only a successful fixed-b verification can support an **observed approximate periodic regime**. Neither finite simulation nor the bias iteration proves mathematical existence, hardware implementation, robust feasibility, or a deployable energy-management policy.

## Inputs inspected

- `protocol/GATE_A_LOCKED_V2_1.json`
- `model_audit/abc_reference/reference_abc.py`
- `model_audit/abc_reference/preconditioned_abc.py`
- `protocol/gate_a_extension_boundary_selection.json`

The independent abc implementation integrates physical current and stored energy without current-state projection. Its bidirectional DC conversion and stored-battery-energy equations already distinguish charge and discharge correctly. No general anti-windup correction is demonstrated necessary by this review. Original archived sources must remain untouched.

## 1. Fixed condition definitions

1. Steady points: every Cartesian sign combination P = +/-300 kW, Q = +/-200 kvar. Solve the continuous electrical/DC equilibrium for each signed point; retain the known sampled startup transient and then apply the complete V2.1 first-converged-checkpoint rule. Never call the continuous initial condition a discrete steady orbit.
2. Four outward steps: (P,Q) = (sP*300 kW,sQ*200 kvar) to (sP*350 kW,sQ*225 kvar), sP,sQ in {-1,+1}. Preserve the corresponding complete checkpoint and clock. Specify the first sample that observes the command change; if the external change occurs 50 us after the checkpoint, it is observed at the next 100 us controller boundary, not immediately by an unsampled reference generator.
3. Source dips: retained voltages 0.85, 0.75, and 0.475 pu, each 150 ms; use the preserved V2.1 checkpoint at 0.6 s and begin at 0.60005 s. Restore every plant/controller/held/queued state, including absolute source and PLL phase. The 0.475 point follows the analytical ceil-to-0.001 rule, not observed controller performance. Its relaxed necessary-bound headroom margin is only 40.506248111 J; it is not an established feasible point. Label 0.85 a recovery-observation representative until its trajectory is known.
4. Signed cycle: P_req(t)=300000*sin(2*pi*1*(t-t0))+b W, Q_req=0. Define t0, phase, sample-and-hold reference evaluation and cycle endpoint ordering. Recommended: start from the first converged b=0,Q=0 checkpoint, with the sine phase zero at a control boundary. This avoids a command discontinuity at onset, although its derivative changes. Keep the global electrical clock running.

The four step trajectories can reuse the matching preserved steady checkpoints; they are distinct registered conditions, not eight independently tuned initializations. A failure to find a checkpoint is a failure, not permission to select a later point or alter tolerances.

## 2. Recovery definition

### Preserve distinct claims

- **Continuous screening:** actual averaged-current amplitude <=1.0 pu, apparent PCC power <=1.2 MVA, DC voltage within [0.8,1.1] pu, terminal battery power within +/-1 MW, SoC within [0.2,0.8]. The emergency current stop at 1.1 pu does not authorize the interval between 1.0 and 1.1 pu.
- **Emergency stop:** retain the existing hard-event integration and stop behavior. If stopping precedes voltage restoration, fault clearance/recovery is unobserved. Do not reset the state and continue as if recovery occurred.
- **Numerical conservation:** report AC, DC and battery energy residuals separately from all safety/service assertions.
- **Limiter release:** measure the release of each modeled limiter; do not infer it from a small P/Q error.
- **Full recovery:** requires the frozen state-convergence and safe-window tests plus a separately frozen tracking criterion. A final point inside limits is insufficient.

### Recommended post-event rule

Use the first global controller-clock/50 ms check boundary after clearance at which:

1. Three consecutive complete-state 50 ms comparisons pass tolerance 1e-5, with pre-update snapshots and right-closed windows exactly as V2.1. All comparison windows used to declare recovery must be after the external event ends. For a permanent P/Q step, compare the new-command orbit, not the old-command checkpoint.
2. The preceding full 150 ms is safe under all continuous screens and PLL held frequency is within 1 mHz of 60 Hz. Include both sides of sample/actuator and source-voltage discontinuities. Earlier violations remain in the record even if a later safe window exists.
3. Over that same 150 ms, current-reference projection, voltage modulation clipping, battery-command clipping, battery slew clipping, PLL frequency clipping and low-voltage PLL freeze are inactive. Record which limiter never activated, first activation, first release and first sustained release. Freeze a numerical *activity* tolerance separately; it must not relax a physical limit.
4. Recommended service check: over every complete 50 ms subwindow of the trailing 150 ms, mean actual PCC P and Q are each within 1% of Sbase (12 kW and 12 kvar) of their fixed requests. Record peak and RMS tracking errors as diagnostics. This 1% recommendation is synthetic and must be accepted explicitly, not introduced after results. State convergence alone does not prove correct P/Q tracking.

Recommend a maximum post-clearance/post-step recovery horizon of 5 s. Failure to satisfy the rule by then is `not_recovered_within_registered_horizon`. Distinguish `recovered_after_prior_violation` from `safe_and_recovered`. Do not present the former as continuous service/constraint success.

Release requires actual raw-versus-limited values. The old trace stores reference magnitude and modulation magnitude but not enough to reconstruct every limiter flag. A new version may add logging of unclipped reference components, raw and clipped voltage, source command before/after clipping, unslewed source derivative, PLL raw/bounded frequency and low-voltage freeze. Log current/PLL integrators, applied/queued complex modulation and held commands. These are instrumentation additions, not controller changes.

## 3. Signed periodic bias calibration

### Correct energy variable and sign

Let ΔE_b,n = E_b(t_{n+1}) - E_b(t_n), positive when the battery gains stored energy. The locked model has

- P_deplete = P_b / eta_discharge when P_b >= 0
- P_deplete = eta_charge * P_b when P_b < 0
- ΔE_b,n = - integral(P_deplete dt) over the cycle

Then the proposed unit-gain update is sign-correct:

`b[n+1] = clip(b[n] + ΔE_b,n / T, -50000 W, 0 W)`

Here T=1 s, P>0 means export/discharge, and the update uses the old completed cycle. Losses at b=0 normally make ΔE_b negative and hence move b negative. If code instead stores a positive depletion integral D, use `b_next = clip(b - D/T, ...)`.

Zero mean P at the PCC or zero mean battery terminal power is not stored-energy neutrality because DC/DC and battery efficiencies are directional. Evaluate the integral as the primary scalar, with stored-energy endpoint subtraction as a numerical cross-check. Do not subtract large energy states as the sole objective. This update has the units and local sign of a root iteration; global convergence is not guaranteed.

### Accept the single causal sequence with explicit qualifications

- Begin b0=0 and retain every plant/controller/energy state between cycles. No resetting DC voltage, SoC, PLL, integrators, applied/queued modulation, or cumulative energy.
- Evaluate the completed cycle on a consistently left/right-closed interval before assigning the next bias. Keep the last bias in the state record. The update is a model-bench loss-compensation operation with exact integrated energy information; real BMS precision is not established.
- At most 12 calibration cycles. Stop calibration early only at the first boundary with three consecutive cycles each satisfying |ΔE_b|<=1 J and complete one-second orbit difference <=1e-5. Add held b/1 MW to the comparison vector during calibration. Include the forcing phase modulo 2*pi or record the identical phase endpoints explicitly.
- Compare full **one-second** sampled trajectories to the preceding full one-second trajectory. The V2.1 50 ms steady-window comparison is inappropriate for a 1 Hz service cycle. At 60 Hz and Ts=100 us, one service period is exactly 60 electrical periods and 10000 samples.
- At the freeze boundary retain the bias actually used by the just-completed qualifying cycle; do not perform one more unverified bias update. Store the complete pre/post-update state and the exact ordering.
- Then run with b fixed and no calibration updates for at least three additional complete cycles, permitting at most eight. Require three consecutive fixed-b cycles each meeting both the full orbit test and |ΔE_b|<=1 J. Include DC and inductor energies in state periodicity; save battery energy but exclude its huge absolute magnitude from the generic state norm, testing its drift directly in joules.
- Apply continuous constraint screens throughout calibration and validation. Keep any earlier violation visible. A stop or failure to converge is a registered failure; do not widen the bias bracket, retune gains, extend the cycle budget, or choose a favorable earlier interval afterward.

The stated 1 J tolerance is a numerical test target, not a metering specification. It bounds drift per verified cycle, not unlimited-horizon SoC behavior. Separate requested mean PCC power b, actual mean PCC power, mean terminal battery power and stored-energy change in the report. These are generally different quantities.

A trace from the calibration phase is not a fixed-b periodic orbit. The final claim must rest on the additional frozen-b cycles. Fine-step validation must replay the same frozen bias without recalibrating it to the fine solver.

## 4. Minimal independent abc audit

Accept the proposed small **fault** reference set, selected before execution:

- 0.85 pu retained voltage: abc and dq at 10 us, including clearance and the complete recovery window unless stopped.
- 0.475 pu retained voltage: abc and dq at both 10 and 5 us.
- Apply the registered additional 5 us rerun to 0.85 if its normalized current or DC-voltage hard-boundary margin is below 1e-3. Define the normalized margins explicitly; never compare joules or amperes directly with this dimensionless threshold. Numerical disagreement or opposite event ordering also requires reporting an inconclusive result, not silent threshold changes.

This covers recovery and the analytically selected near-necessary-boundary behavior but does **not** independently validate every quadrant or the periodic trajectory. Lowest-cost supplementary signed check: deterministic algebraic public-component/abc/dq RHS comparisons covering P_b<0,=0,>0 and both signs of Q; verify sign continuity at P_b=0, P_bus and depletion identities, loss nonnegativity and conservation. No trajectory integration is needed for that check.

If an independently cross-checked periodic-regime claim is required, add a separately approved abc replay of the final three fixed-b cycles from the recorded freeze checkpoint, using the exact same b, event/sample clock and controls, with no additional bias calibration. Explicitly map physical state and controllers between coordinates. If this is not authorized/performed, label signed periodic trajectory evidence as dq-only. Independent initialization from the same physical checkpoint does not remove a shared-controller specification error, so retain component RHS tests as complementary evidence.

## 5. Storage and reproducibility

Create only new extension files/directories. Recommended root: `model_audit/gate_a_extension/`; do not alter original abc files, prior raw traces, protocols, or ZIP archives.

Store:

1. Frozen JSON and hash, code/dependency hashes, exact condition registry and ordering, mathematical point-selection input/hash, and every predeclared stopping/tolerance rule.
2. Per-condition immutable JSON summary and compressed float64 NPZ, with explicit column names, units, sample-side/event-side labels, coordinates and schema version. Preserve exact timestamps, source and command levels, all physical/control/held/queued states and separate cumulative energy integrals. Retain each complete checkpoint in JSON with full numeric precision.
3. Separate warmup, event, recovery and periodic calibration/verification phases. Preserve startup violations and preconditioning check history. Do not hide initialization failures by writing only post-checkpoint data.
4. Every calibration cycle: b used, ΔE_b from integral and endpoints, complete-state orbit error, safe/limiter flags, next b and whether the clamp was active. Retain all cycles, including failed ones. For storage economy, candidate/calibration control-cadence traces may be retained with all-step online extrema/event states and integrals, but label this decimation; do not call them full internal-step raw traces.
5. For final abc/dq representatives retain full internal-step physical traces and exact event brackets, plus control pre/post snapshots. Chunk long traces by phase or cycle without changing float precision. A reduced plot file may supplement, never replace, numerical evidence.
6. Pairwise numerical comparison JSON: checkpoint norms, current/DC extrema, event times/order, released-limiter times, recovery declaration time, energy residuals and periodic per-cycle drift. Missing/unobserved quantities should be null with a reason, not zero.
7. A final SHA256 manifest excluding private virtual environments/caches. Hash new results after all writes; preserve previous manifests rather than rewriting them.

## 6. Version discipline and limitations

Do not change initialization or anti-windup to improve the outcome of these preselected conditions. If an algebraic/sign/unit or general initialization error is established independently, document the defect and introduce a separately frozen model version before reruns; compare the version on baseline conservation and fixed cases. Do not transplant old bounds/checkpoints to changed dynamics without recomputing and labeling them.

All results remain balanced, switching-cycle-average, synthetic/non-OEM model evidence. No semiconductor ripple or thermal overload rating, BMS fidelity, DC chopper, external protection sequence, unbalanced fault, harmonic validation or hardware verification is established. Resource and control parameters remain exactly those of the locked reference unless explicitly versioned and approved.
