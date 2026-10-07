# Standard causal recovery outer loop: limited mean-model rationale

This is an explanation of the pre-result frozen V1A controller, not a new controller contribution or a switching-system stability proof. The frozen code and actual held-out validation remain authoritative.

## Signals and scope

During recovery only, the outer loops read present DC energy W and buffer inventory B, constant setpoints W*=21600 J/B*=50000 J, and the authorized service clock. They do not read the matched healthy trajectory. The latter is an offline evaluation comparator.

The physical workload continues at650kW after the service; it is not shed or rescheduled. Original planned P/Q and buffer feedforward apply during service. A held nominal learned DC correction is explicitly additional to the ideal averaged-model command and must be charged to the new measured service/cost contract, not hidden inside the frozen exact-theory result.

## Inventory feedback

Let eB=B−B*. Near the nominal post-service equilibrium with the recovery command u=kB eB and inactive power/ramp clipping,

    eB' = −b,
    tau b' = kB eB−b,
    tau eB'' + eB' + kB eB = 0.

For any tau>0 and kB>0 both roots have negative real part. The frozen kB=20 s^-1 is overdamped for tau in{4,5,6}ms. This is a local mean-model statement; it does not assert that arbitrary saturation or unmodeled state-estimation errors preserve the same response.

## DC PI

For q=0 and fixed grid V, net active delivery is F(P)=P−cP². On the physical current range its derivative g=1−2cP is positive. Let an approximately constant measured-tracking/loss disturbance be absorbed by the PI equilibrium correction cP*. Linearize around that equilibrium, with eW=W−W*, correction cP=−kW eW+z and z'=−ki eW:

    [eW', z']^T = [[−g*kW, g], [−ki,0]] [eW,z−z*]^T + [b,0]^T.

The characteristic polynomial is s²+g*kW*s+g*ki, hence Hurwitz for g,kW,ki>0. With kW=100 s^-1, ki=2500 s^-2, and the stated low-loss import point, this is a roughly critically damped tens-of-milliseconds outer response. The stable inventory subsystem drives it as a vanishing disturbance, so the unsaturated continuous mean cascade is locally asymptotically stable.

No equilibrium bias is supplied by a counterfactual health trajectory: the integral state learns it from the actual DC error during the fixed nominal warm-up. The one nominal complete checkpoint per numerical resolution is shared across held-out parameter/clock cases. There is no held-out fitting.

## What this does not prove

The actual converter includes100us sampling, binary switching, current PI, initial command hold, mode gating, physical lag/ramp/power saturation and conditional integration. The simple Hurwitz calculation is not a theorem about that full hybrid plant, not a proof of every future PWM orbit, and not an exact finite-time recovery guarantee.

V1A therefore validates a separately declared finite-window physical recovery contract, continued-load observation and explicit resource budgets. Complete controller-state differences are reported as diagnostics, and exact-theory P/Q or DC-return claims remain confined to the original averaged-model theorem. Any failed held-out case must stay failed under V1A; a changed controller/protocol requires a separately numbered stage.
