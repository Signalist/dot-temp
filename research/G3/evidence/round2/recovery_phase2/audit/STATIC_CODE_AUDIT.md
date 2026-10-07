# Static code and protocol audit

Reviewed frozen recovery.cpp (SHA-256 62581893afc289718d9ca8f9ec374ceac457dce5510ef1c8a887f2ffeca99ef7) and run_campaign.py. V1 and V1A were reviewed and copied into this audit directory before simulation results. V1A was a pre-execution amendment, not a response to holdout outcomes.

## Causal feedback: PASS

- The executable has inputs for the original authorized schedule, one checkpoint, numerical dt, actual plant tau/ramp, onset offset and service/healthy branch selection. It has no input for the matched healthy output or a future measured signal.
- command() reads the original authorized time schedule only during the service; healthy command is constant. The current loop's midpoint reference is a known scheduled value, not a future measurement.
- DC PI reads current y.W and its own integral; inventory feedback reads current y.B. The actuator's actual tau/ramp occurs in rhs(), not in DC/current control or feedforward generation.
- Original input CSV is byte-preserved; its exact polynomial command model is not recomputed for the altered actuator.
- One 2 s nominal warmup per numerical dt is saved and reused. The run driver does not warm up each holdout. Numerically separate coarse/fine checkpoints are resolution checks, not case-specific calibration.

## State and clock continuity: PASS

- loadcheckpoint() reads all dynamically relevant physical and controller state: iabc, W, B, b, current PI integrals jd/jq, DC integral zw, cp/held/ub, gate flag and held duty. Absolute start time is 2.0 s, at a PWM boundary; actual grid phase uses that same absolute time.
- Modulation/circular-utilization extrema and clip count are diagnostic accumulators rather than dynamics. They restart for separate accounting; this does not reset a physical/controller state.
- Service onset is 2 s plus the declared 37 or 73 us offset. The integrator advances to onset from the common checkpoint under its actual physical dynamics. PWM periods and sinusoidal grid time are not shifted or relabeled.
- The service clock gate is identical for healthy and service branches. Its up-to-one-period early freeze and late release were explicit in the pre-run protocol.
- No W/B/physical-current reset or projection occurs at service end, recovery deadline, or observation end. Milestones only log snapshots.

## Saturation, hard limits and energy: PASS WITH DISCLOSURE

- DC PI conditional anti-windup blocks accumulation farther into its absolute +/-5 kW saturation; the current PI integral is held under duty-span clipping. DC integrator is held through the service by the declared gate.
- uB has an explicit +/-10 kW limit. Physical u is bounded +/-450 kW and bdot obeys the actual plant's slew bound. W and B are never hard-clamped to admissible inventory/voltage limits.
- Actual rate saturation is present in multiple cases, including a small nominal requested-rate alteration. It must be reported, not called absent. Saturation is allowed by the frozen contract and is not by itself a hard-bound failure.
- True binary bridge states are held between exact duty-switch edges; switching edges, source knots, milestone times and the final absolute 1 us sample grid split numerical steps.
- The plant obeys Wdot=p_bridge-load+b, Bdot=-b and abc RL equations. Measured grid energy, copper loss, load, battery and bridge integrals are stored separately. Numerical maxima sample RK midpoints/endpoints; this is not a certified continuous-time extrema proof.

## Contract mismatch identified in results

The controller limiter is |cp_service|<=5000 W, whereas the frozen resource constraint is |cp_service-cp_healthy|<=5000 W. These are different statements. A service value of -5000 W paired with approximately +59.18 W healthy correction yields an approximately 5059.18 W incremental difference. The resulting V1A failure is genuine and must remain failed. A causal future redesign cannot use online healthy-reference subtraction; it would need a separately declared conservative resource design and genuinely new validation.

## Scope

The controller-state/duty differences are reported but have no frozen acceptance thresholds. Passing the W/B/current finite-window tolerances therefore does not prove complete closed-loop-state return. The 8 held-out configurations are finite evidence, not a guarantee over every parameter between the chosen endpoints.

MEAN_RECOVERY_ANALYSIS.md is sound as the stated local, unsaturated continuous mean-model rationale: tau*eB''+eB'+kB*eB=0 has stable roots; the DC characteristic polynomial s^2+g*kW*s+g*ki is Hurwitz when g,kW,ki>0. Its explicit exclusion of sampled/PWM/saturation/gating stability claims is necessary and appropriate.
