# Gate A V2.1: revalidated short-time DC impossibility certificate

Date: 2026-10-02. This is a new certificate calculation from newly generated dq trajectories and checkpoint records under the recovery project. It is distinct from the historical record and the earlier 0.20005 s diagnostic-state calculation. The original source was reconstructed from prior tool-call text; all state inputs for this calculation came from the new files. No performance search or Gate B experiment is included.

## Result and precise claim

For the declared V2.1 fault-onset state and locked physical series-RL/DC/source model, no policy can simultaneously maintain actual current at or below 1 pu and DC voltage at or below 1.1 pu throughout the 150 ms, 0.4 pu-source sag. A conservative prefix bound already contradicts joint admissibility at **20 ms**:

    unavoidable stored-energy gain >= 4,936.04 J
    available DC-plus-inductor headroom <= 4,344 J
    strict contradiction margin >= 592.04 J.

This conclusion grants every ampere to active export, instantaneous ideal actuation, maximum permitted passive losses, and all allowable inductor headroom. Those relaxations make the hypothetical controller more capable. The proof therefore does not depend on the tested controller's reactive allocation, modulation command or postfault PCC voltage.

Using full-precision declared state values, the first root of the relaxed energy obstruction is 17.0882039325 ms after sag onset; the 20 ms excess is 595.60651056 J. The rounded 20 ms contradiction is the recommended claim. The root is not an exact physically achievable failure-time prediction, and no policy is thereby certified safe before it.

## Fresh evidence and declared initialization

The first checkpoint satisfying the frozen three-successive-check convergence rule was at 0.6 s. The fault begins 50 microseconds later, at 0.60005 s. Checkpoint selection was determined by the new pre-run, not imputed from historical results. The electrical/controller state is approximately periodic under the declared normalization; the battery is discharging under the fixed positive active-power request. This is not an indefinitely sustainable closed battery-energy orbit.

At the 0.6 s convergence checkpoint:

- Wdc = 21,914.743372215053 J
- WL = 277.1038270595847 J
- Pb = 815,639.6755124972 W
- Wdc / nominal 21,600 J = 1.0145714524173635
- WL / rated 397.09750202003335 J = 0.6978231433085292

The certificate uses the subsequent exact recorded fault-boundary state, not the checkpoint state or the original startup state:

- Wdc0 = 21,915.135193267946 J
- WL0 = 276.7121693063766 J
- Pb0 = 815,639.6755381202 W
- id0 = 929.346177558162 A; iq0 = -735.8027745282857 A
- Actual current = 0.8347675377506103 pu
- Vdc = 1.0072683814559669 pu

The stored floating-point boundary time differs from 0.60005 s by less than 3e-16 s. No time interpolation was used. The row is recorded from the healthy side of the ideal source-voltage step; current, capacitor energy and source power are continuous through that step. PCC voltage continuity is neither assumed nor needed.

## Physical scope

The ideal source remains at 0.4 pu for 150 ms. The actual continuous-current limit is 1 pu with no permitted overload. Source power is bidirectional within +/-1 MW but can decrease no faster than 5 MW/s. The positive-power DC/DC efficiency is 0.99. Storage and passive losses are exactly those in the locked model.

The model has no brake/chopper, extra storage, added freewheel/bypass energy-disposal path, instantaneous source disconnect, shutdown/reset, or other unmodeled disposal channel. Ordinary converter commands within the stated equations remain allowed. A command asking the source to charge cannot reverse its actual power instantaneously.

The proof relaxes Q support, modulation, sampling/delay, synchronization, and any additional source-lag restriction beyond the slew floor. It does not imply impossibility for a different plant with extra protection or energy-disposal hardware.

## Energy identity

Let i=id+j iq denote the balanced peak-amplitude current, R=Rf+Rg and L=Lf+Lg. The physical equations give

    Wdc_dot = Pbus - Pinv - Ploss_inv
    WL = (3/4) L |i|^2
    WL_dot = Pinv - Pideal_source - (3/2) R |i|^2.

The rotating-frame cross term has zero real power. Adding these equations eliminates inverter-terminal power:

    (Wdc+WL)_dot = Pbus-Pideal_source-Ploss_inv-Pcopper.             (1)

The complete modeled filter-plus-grid inductor energy is retained. Temporary converter-to-PCC energy transfer cannot evade (1). The source power in (1) is delivered to the ideal Thevenin source; it is not PCC power, and PCC voltage is not set equal to the 0.4 pu source voltage.

## Policy-independent upper bounds

With actual |i|<=Imax=1,419.99405378735 A,

    Pideal_source <= (3/2)(0.4 Vphase,peak,base) Imax = 480,000 W
    Ploss_inv <= 1,200+6,000 = 7,200 W
    Pcopper <= (3/2)(Rf+Rg) Imax^2 = 23,940.44628252 W
    B = maximum total energy exit = 511,140.44628252 W.

Storage bounds are

    Wdc_max = .5 Cdc (1.1 x 1,400 V)^2 = 26,136 J
    WL_max = .75 (Lf+Lg) Imax^2 = 397.0975020200 J.

Granting these separate maxima simultaneously may overestimate the controller's capabilities, which is conservative for this impossibility test. Aggregate headroom from the declared onset state is

    H = Wdc_max+WL_max-Wdc0-WL0 = 4,341.2501394457 J.                (2)

## Source lower bound and prefix contradiction

Every allowed source trajectory satisfies

    Pb(tau) >= max(Pb_min,Pb0-Rdown tau).

The bus transfer map is increasing: h(p)=eta_dc p for p>=0 and p/eta_dc for p<0. The lower envelope remains positive over this 150 ms sag, so (1) implies

    W(tau)-W(0) >= F(tau)
    F(tau)=a tau-.5 b tau^2
    a=eta_dc Pb0-B=296,342.832500219 W
    b=eta_dc Rdown=4,950,000 W/s.                                 (3)

If current and DC limits held throughout a prefix, W(tau)-W(0)<=H. Any F(tau)>H is therefore a contradiction independent of policy.

The smaller root of F=H is

    tau_cross=[a-sqrt(a^2-2bH)]/b=17.0882039325 ms.

At 20 ms, F=4,936.8566500044 J, exceeding H by 595.6065105587 J. F reaches its prefix maximum at 59.8672389 ms, where F=8,870.6135731569 J. At fault clearance, F(150 ms)=-11,236.0751249671 J. The negative clearance bound does not erase the earlier contradiction: safety must hold on every prefix.

### Outward-rounded claim

The following inequalities were checked against the new state and physical constants:

    Pb0>=815,600 W; Wdc0>=21,915 J; WL0>=276 J
    Psource<=480,001 W; Ploss_inv<=7,200 W; Pcopper<=23,941 W
    Wdc_max<=26,137 J; WL_max<=398 J.

Consequently H<=4,344 J and

    F(20 ms) >= [.99 x 815600-(480001+7200+23941)] x .02
                -.5 x .99 x 5000000 x .02^2
              =4,936.04 J >4,344 J.

The 592.04 J margin covers these explicit rounding intervals. This is an analytic statement conditional on the declared state and model. It is not a validated interval enclosure of the preceding numerical warm-up or a hardware state-estimation guarantee.

### Correct sign-changing source extension

When a later case allows the source lower envelope to become negative, it must not be clipped to zero. With Hbus(p)=eta_dc p^2/2 for p>=0 and p^2/(2 eta_dc) for p<0, and t1=min(tau,(Pb0-Pb_min)/Rdown),

    integral Pbus_lower
      =[Hbus(Pb0)-Hbus(Pb0-Rdown t1)]/Rdown
       +(tau-t1) h(Pb_min).

This handles both sign reversal and eventual saturation at -1 MW. The new selfchecks test the piecewise integral against quadrature; the present sag needs only the positive branch.

## Controller observations and startup boundary

The new tested baseline crosses the strict current threshold approximately 0.349696 ms after fault onset and reaches DC overvoltage approximately 5.895970 ms after onset. Its current peak is 1.00007464987 pu. This is controller-specific evidence, separate from the any-current-safe-policy obstruction. Because the baseline violates current first, it is not an example of a current-safe policy surviving until the universal bound.

The original sampled startup retains an apparent-power overshoot of about 1.248563 MVA at 2.9 ms. No claim is made that this whole startup is hard-safe. The frozen checkpoint qualification instead uses its declared 150 ms healthy window before 0.6 s, where the recorded maximum current is about 0.8353591 pu, maximum PCC apparent power about 1.063016 MVA and DC voltage within approximately [1.0072591,1.0072685] pu. These are numerical observations under the qualification rule, not a global safety proof.

The Gate A case audits physical constraints and energy bookkeeping. It is not a test of a proposed continuous-oscillatory-service controller and does not establish a novelty or performance advantage.

## Revalidation and provenance

The calculator read fresh 10 us and 5 us dq trajectories, summaries and complete checkpoint metadata. Protocol hashes in the input reports/checkpoints match the current parameter file. Fault-onset Wdc differs between refinements by about 3e-9 J and Pb by about 8e-8 W. This is numerical consistency, not rigorous integration-error enclosure.

The embedded independent algebra selfcheck reconstructs capacitor/inductor energy, verifies (1) on 25 deterministic test states, compares the piecewise source integral against quadrature, and cross-checks the analytic first root. All new checks passed. Maximum derivative-identity discrepancy was about 2.4e-10 W, integral discrepancy below 4.4e-11 J and root discrepancy below 7.1e-16 s.

Files:

- `DC_BOUND_GATE_A_V2_1_REVALIDATED.json`: fresh state, input hashes, bounds and numeric selfchecks
- `../gate_a/dc_bound_gate_a_v2_1.py`: source-text reconstruction with documented new-evidence guard
- `../gate_a/dc_bound_gate_a_v2_1_revalidation.log`: newly generated calculation output
- `THEORY_CERTIFICATE_RECOVERY_PROVENANCE.md`: reconstruction/edit history
- `DC_CERTIFICATE_HISTORICAL_RECORD.md`: historical values only, not used as state inputs

SHA256:

- Current protocol: `8b2e6dfceffe391dfab7b2ba18fc1f8d3c736c6329a5f7e93175bf7db1e54d57`
- Fresh 10 us NPZ: `232f9c9e77519eb0f9eb91aef3bd09245162459c037d9f57eea135b1fe5f1c4b`
- Fresh 5 us NPZ: `e579459f0a229b57d5ae9761231f09513e000ebf6e96e1a1aff301bf4219662b`
- Active calculator: `0e1bace60a38d1f2385c2caeb4436a0a952350d432160cc9f2bf94bd98a9e8bf`
- Newly calculated certificate JSON: `fd8a03b0c25977d9bef2f2fb84a1474ebe6bc06ec8f4327b05adabc8770d3a0f`

## Independent fresh abc cross-audit

The independently implemented stationary abc model was also rerun. Its fresh 5 us fault-onset data and bound are recorded in [DC_BOUND_ABC_REVALIDATED.json](../model_audit/DC_BOUND_ABC_REVALIDATED.json), SHA256 `c242ab76e1b99f7b23e64f9c6c1292df2e2b7ade090eabcd66ec7d13da940157`. The input is `../model_audit/abc_reference/revalidation_results/preconditioned_v2_1_h5us.npz`, SHA256 `9b19745f35669ae33ba4145c9d8ad38b6772e08ab35808dc54c363299716cd56`.

The abc calculation gives H=4,341.250139483163 J, F(20 ms)=4,936.856650060683 J, excess=595.606510577520 J and first root=17.088203932464 ms. This agrees with the fresh dq calculation well within the outward-rounding margin. The independent model audit also checked the three-phase energy factors, maximum losses, inductor storage and source-ramp/sign-reversal assumptions. This is fresh cross-model numerical evidence and algebraic review; it does not turn numerical warm-up agreement into a formally validated initial-state enclosure.
