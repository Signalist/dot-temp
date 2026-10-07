# Prospective W6 measurement protocol

Status: **DESIGN ONLY, NEVER EXECUTED.** No hardware access, account access, external contact, paid work or collection is authorized/performed by this artifact. The current corpus fails admission. This protocol is a minimal single-device identification pilot plus a separately powered confirmation stage, not a claim that a fixed small sample proves a device-wide safety guarantee.

## 1. Freeze the claim and boundary first

Start with one identified GPU, one model/revision, one serving-engine revision, one precision, one selected phase/context/batch stratum, and single-task execution with no concurrency. State the scope this excludes. A second context/phase is a deliberate falsification stratum; do not silently pool it into one s(p). Cross-model or cross-hardware generalization needs complete held-out model/device units later.

Define p(t) as the actual measured dynamic power at a named GPU electrical boundary relative to a separately modeled idle baseline P0(t). Specify all rails and sensor topology. Negative measured deviations must remain data with uncertainty, not be silently clamped to make the model true. Power commands u(t), requested/enforced caps, clocks, and p(t) are distinct channels.

The minimum GPU pilot can validate only GPU behavior. A grid-facing claim additionally requires simultaneous metering at the actual declared PCC, a documented electrical topology, nuisance loads and operating modes. Node AC or rack-branch AC is not facility PCC unless that is explicitly the modeled boundary. A utility-scale frequency response cannot be identified by an isolated GPU pilot; use separately validated facility/operator data or retain the grid as a specified simulation model.

## 2. Required synchronized record

Each immutable acquisition has an acquisition_id, session_id, run_id, hardware serial/UUID hash, GPU/CPU/PSU/converter/UPS identities, firmware/driver/engine versions, model/tokenizer revisions, clock source, calibration version, and permitted operating envelope.

1. Commands: control sequence ID; command issue/return/ack times; requested and enforced cap/clock/smoothing settings; observed actuator effect time and error status. No inference from a cap number alone
2. Actual power: all-GPU-rail reference, sensor timestamps, arrival timestamps, unit/gain/offset, physical bandwidth, anti-alias filter/integration window, calibration uncertainty, dropped samples and saturation flags; NVML may be a supplementary channel
3. Service: per-step/token or kernel-completion timestamps; completed work increment; phase; request ID; context length/KV state; batch; queue/concurrency; temperature and clocks. If work is tokens, state context-dependent token cost rather than assuming equal physical work
4. EOS: server/device final useful-work completion; token/output availability; finish_reason; configured maximum; cancellation/error flags; time the controller first learns EOS; associated stop command and physical response. Distinguish natural stop, length cap, cancellation and failure
5. Recovery: continue sampling actual power and thermal/electrical state after EOS until the declared terminal condition holds. Record the entire return/control trajectory and any burn/dummy-load work. If a physical floor/slow down-ramp cannot be realized after useful work ends, reject that model assumption
6. Electrical interface: simultaneous PCC active power P, reactive power Q where relevant, V/I, source frequency estimate, converter/UPS/battery modes/state and other loads. A scalar active-power-only contract must explain exclusions. Record full source-power return plus the separate post-input grid response tail
7. Time: a shared monotonic clock or measured clock transformation with worst-case offset/drift/latency bounds; synchronization events before/after each session. Timestamp precision is not synchronization accuracy

## 3. Smallest informative pilot

This is an identification/falsification pilot, not a population sample-size claim.

- Use at least five feasible control levels spanning the intended region, including the nominal and low-power endpoints. Observe their actual power; some commands may yield indistinguishable power and must not be counted as independent power levels
- For one fixed task stratum, perform one randomized level-order session, one reversed-order session to detect hysteresis, and one independent restarted session. Use at least two independently initialized repeats per level within a session; keep clustering explicit. Three sessions × five levels × two repeats = 30 plateau episodes for a narrow pilot
- In each session, include upward/downward transitions between attainable levels and isolated execution-to-EOS-to-return cycles. The experimenter must arrange physically safe transitions; do not assume a continuous actual-power actuator from discrete cap support
- Add one adjacent context/phase condition as a prespecified falsification check. If s(p) depends materially on context, phase or temperature, use separate conditional envelopes s−(p,z), s+(p,z) or reject the scalar reduction; do not force a concave fit
- Natural-EOS tasks and deliberately fixed-length tasks are separate strata. Randomizing synthetic lengths is useful for control tests but is not natural-EOS evidence
- Include idle before and after the task, and any required cooldown/full-reset interval. Terminal condition must name which state is restored: dynamic p≈0 alone is weaker than matched thermal/clock/queue/storage state

Stop the pilot if clock/measurement coverage fails, the actual control region is unreachable, isolated cycles are unavailable, no useful-progress lower envelope is defensible, full return is not physically reproducible, or PCC is unavailable for a claimed PCC result. A stop is a substantive negative result, not permission to replace missing data with unrelated traces.

## 4. Freeze the split before fitting

No current data are assigned to calibration or confirmatory testing. Current public data are already-exposed schema/measurement diagnostics.

For new acquisition, publish/hash the acquisition manifest and allocate complete session/run groups before viewing outcome curves or fitting. No random row, overlapping-window or token split. A pilot used to choose models/ranges is development data forever. Separate calibration sessions identify sensor/clock and service/actuator envelopes; later untouched sessions validate them. If claiming transfer, reserve complete model families or physical hardware IDs; never split the same run between sides.

Freeze: primary endpoint, comparator, same-information baseline, task/length distribution, initial/terminal state, time/energy horizon, operational thresholds, sensor processing, outlier/missing-data rule, confidence allocation, stopping rule and analysis code hash. Record controller-visible as-of information so benchmark methods cannot use future EOS or actual-power measurements prematurely.

Before large evaluation, send the matched-data sufficiency result and immutable split to the parent for review. An invalid or inconclusive test set cannot be reused for tuning and then reported as confirmatory.

## 5. Measurement and validation budget

Choose tolerance from the engineering claim, not the convenience of available sampling.

Let Δ be maximum physical sample gap, τ the bounded timestamp error, εcal the amplitude/calibration error, εfilter the declared unresolved sensor/filter error, εbase the baseline uncertainty and R a separately justified physical Lipschitz bound. A sample-linear reconstruction has the conditional envelope

εp ≤ εcal + εfilter + εbase + R(Δ/2 + τ).

This is not a way to infer R from sampled slopes. Without an independent R/filter bound, the between-sample deterministic budget is unbounded. Oversampling an internally averaged sensor does not reduce its unknown filtering error. A useful design target is Δ ≤ τmin/10 and τ ≤ Δ/10 for the shortest claimed transition τmin, plus demonstrated passband/gain/phase coverage; these are design heuristics, not safety certificates.

For progress increments with endpoint count error ≤εx and interval clock error ≤2τ, an interval average rate is bounded by

max(0, Δx−2εx)/(Δt+2τ) ≤ s_average ≤ (Δx+2εx)/(Δt−2τ), provided Δt>2τ.

This bounds an interval average, not pointwise s(p). Conditional service envelopes must include p uncertainty, phase/context variation, thermal history, model residual and repeated-run variation. Concavity/monotonicity are falsifiable structural restrictions; a constrained fit is not proof they hold.

For a causal GPU→PCC map, use ΔP = g*p + eP and identify g only from simultaneous excitation/output over execution and return. Let ghat have induced L∞ gain ||ghat||1, kernel uncertainty ||g−ghat||1≤δg, actual |p|≤pcap, and residual baseline/nuisance envelope εres. Then

εP ≤ ||ghat||1 εp + δg pcap + εres.

A scalar multiplier is the special case g=kδ; do not use it when UPS/PSU/thermal dynamics produce lag, sign changes, saturation or mode switches. A low held-out RMS fit error cannot substitute for the stated supremum envelope.

If g includes direct feedthrough, ||g||1 denotes the total variation of its impulse measure (absolute feedthrough gain plus the L1 norm of the dynamic kernel), equivalently the stated induced L∞ bound. It is not an ordinary Lebesgue L1 norm of a Dirac delta. All transfer bounds are restricted to the validated operating region/mode; unmodeled switching requires a separate uncertainty set.

For stable grid impulse response h with estimate hhat, define ||h−hhat||1≤δh, input bound Pbound, initial-state output mismatch B0, and frequency sensing error εf. A conservative full-horizon output uncertainty is

Ef ≤ B0 + ||hhat||1 εP + δh Pbound + εf + εtail.

Accept only when nominal peak + Ef ≤ the facility-specific allowable deviation, including the entire post-recovery zero-input grid decay. The theory worker's 0.05 Hz example is a simulation budget, not a universal grid standard. RoCoF or voltage require separate output models and possible direct-feedthrough terms, not this frequency-only formula.

To stop a finite tail, require a certified stable decay bound, e.g. ||Ce^(At)qT||≤K exp(−λt)||qT||, and select tail length so the remainder is ≤εtail. If a mode/decay bound is missing, report finite-window numerical results only. Neither GPU p returning to zero nor a convenient fixed observation window proves grid recovery.

EOS visibility delay is δEOS=t_controller_knows−t_true_EOS, with timing uncertainty and right censoring retained. Separate software delay, command latency and physical response. Under the theory worker's bounded-power/physical-slew contract, the stated objective penalty bound 2(pcap+c)δEOS uses c in power-equivalent units; it is conditional analysis, not an observed hardware bound. Keep both service completion latency and total regenerative-cycle latency.

## 6. Independent-test sample budget

A deterministic safety claim needs a justified physical envelope; a finite zero-failure test cannot prove it. For one prespecified binary failure endpoint with independent identically distributed (iid) test units, zero failures in n units gives the exact one-sided binomial upper bound qU=1−δ^(1/n). To target failure probability ≤α at confidence 1−δ, n≥ceil(log δ/log(1−α)). For this single endpoint, α=0.05 and δ=0.05 requires 59 iid units; α=0.01 and δ=0.05 requires 299. These are 95% one-sided confidence statements, not simultaneous guarantees for every metric. Five separately prespecified contracts with Bonferroni allocation δ/5=0.01 require 90 and 459 iid units respectively for each endpoint. A single composite failure event is another option, but its components must be fixed before testing.

The unit is the independent acquisition/session appropriate to the claim, not samples/tokens/windows. Repeated cycles within one thermal session may be dependent; do not invoke these n counts without a defensible iid sampling design for that endpoint and target population. Exchangeability alone, uncorrelated samples alone, or an estimated effective sample size does not establish the iid binomial premise. These counts are conditional planning calculations, not automatic numerical acceptance thresholds or invented observations. New hardware, models, contexts or operating modes may change the population and invalidate pooling. Any observed failures use the full prespecified binomial interval or another justified dependence-aware method, not a reset counter. The pilot's 30 clustered episodes do not meet the above confirmation budget.

## 7. Parser admission tests

Reject or retain as explicitly missing: absent IDs, mixed units, decreasing timestamps without an identified reset, duplicate timestamps without a frozen rule, clock-domain mismatch, sensor saturation, incomplete rail coverage, unaudited averaging kernels, absent EOS reason, uncaptured recovery, and uncontrolled overlapping jobs. Join only identical acquisition/run/request identities with a verified clock transform. Never join Azure lengths to NLR/SC24 power as measured pairs. Source-specific hashes, licenses and original immutable files travel with any derived results.

The public-data schema audit has already passed at its limited diagnostic scope. No implementation or data acquisition proposed here has run.
