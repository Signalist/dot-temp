# V2 proposal: regulate total measured storage, not internal transfer

This note records the rationale for the separately numbered recovery V2. It does not change V1A's four failed run classifications. The implementation/protocol and new confirmations are separate artifacts.

## Why the V1A energy throughput was large

In the frozen ideal-buffer physics,

    W' = Pgrid - copper_loss - Z' + b - d,
    B' = -b.

A port timing/rate mismatch can move hundreds of joules between W and B while leaving W+B almost unchanged. A W-only outer PI nevertheless asks the grid to cancel the W deviation while the inventory loop is transferring the same energy internally. That can produce a large positive/negative grid correction even when net missing energy is tiny. The observed V1A absolute recovery increment (~657 J in the worst held-out pair) was reported honestly; signed energy below0.31 J does not hide it.

## V2 measured variable and cancellation

Use E=W+B, measured from the actual plant, against the constant E*=W*+B*. Then

    E' = Pgrid - copper_loss - Z' - d.

The internal b term cancels exactly. An ordinary PI on E need only compensate actual total-energy deficit and sampled tracking/loss bias. Keep the separate measured B feedback to redistribute energy inside the two stores. No matched healthy trajectory or future actual workload enters either feedback.

For constant post-service workload and q=0, the unsaturated averaged linearization is two stable subsystems:

    E-PI: s² + g*kP*s + g*kI,  g=d(P-cP²)/dP>0,
    inventory: tau*s² + s + kB.

They are decoupled in total-energy coordinates; W is recovered by W=E-B. The frozen V2 proposal retains positive PI/inventory gains, causal integral learning, and ordinary saturation/antiwindup. It reduces the absolute correction limit to4.5kW to leave a predeclared margin under the5kW incremental-power contract; this is a new controller setting, not reinterpretation of V1A.

## Boundaries

This simple cancellation uses the declared lossless reversible buffer inventory model. Additional battery/DC-DC losses would enter E' as real losses and must be measured/modelled and paid for. The calculation is a local mean-model rationale, not a full binary-PWM hybrid stability proof.

The strengthened100J V2 recovery budgets remain different from the core theory's100J net cap slack: different observation interface, recovery times, service/state tolerances and allowed timing of grid power. Actual costs below100J do not make the core exact P/Q capacity bracket a switching-system theorem.

New V2 held-out clocks/parameters are confirmation configurations, not proof of the complete continuous uncertainty box. V1A-known corners are labelled regressions. Any V2 failure must remain under V2 and cannot be removed by changing gains, tolerances or budgets after observing it.
