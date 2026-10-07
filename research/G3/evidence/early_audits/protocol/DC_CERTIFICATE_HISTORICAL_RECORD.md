# Historical DC-certificate record: not revalidated

Written 2026-10-02 from this worker's visible prior tool results. No original NPZ, checkpoint JSON, selfcheck log, certificate JSON or independent-audit artifact was recovered. This document is not a replacement for that evidence and is not a new certificate. Every scalar below is historical and unverified in the current recovery workspace.

## What previously existed

The original THEORY_REVIEW.md, legacy DC_BOUND_GATE_A.md/.json, legacy calculation script/log, and V2.1 DC_BOUND_GATE_A_V2_1.json plus calculation script/log had been saved before interruption. The separate V2.1 Markdown certificate had **not** yet been written. The parent had reported independent abc agreement and asked for that citation, but it had not been incorporated into a completed V2.1 Markdown artifact.

All those original files were under . No backup outside . was made by this worker. That root disappeared. Read-only searches of /workspace and /tmp found no surviving copies of the G3 artifacts.

## Physical argument retained as mathematics

For the locked three-phase series-RL/DC model,

    (Wdc+WL)_dot = Pbus-Pideal_source-Ploss_inv-Pcopper,
    WL=(3/4)(Lf+Lg)|i|^2.

At actual |i|<=Imax, grant maximal ideal-source active export, inverter/copper loss, and inductor energy. This deliberately optimistic outer relaxation gives

    Pideal_source <= (3/2) Vs_phase_peak Imax,
    Ploss_inv <= loss_constant+loss_I2_at_1pu,
    Pcopper <= (3/2)(Rf+Rg)Imax^2,
    Wdc <= .5 Cdc Vdc_max^2,
    WL <= .75(Lf+Lg)Imax^2.

The source cannot instantaneously reverse: Pb(t)>=max(Pb,min,Pb0-Rdown t). Its increasing bus map is eta_dc p for p>=0 and p/eta_dc for p<0. While the lower envelope is positive, accumulated energy is bounded below by

    F(t)=(eta_dc Pb0-Pexit_max)t-.5 eta_dc Rdown t^2.

If F(t)>H, where H=Wdc_max+WL_max-Wdc0-WL0, current and DC limits cannot both hold through that prefix. Checking only fault clearance can miss an earlier forced violation. Postfault candidate PCC voltage is never used as a universal bound.

The modeled scope excludes brake/chopper, added storage, extra freewheel/bypass dissipation, instantaneous source disconnect or shutdown/reset. Bidirectional source operation remains allowed subject to its continuous slew limit. Q obligations and modulation constraints are relaxed, making the impossibility argument more permissive. The root is an outer-relaxation obstruction, not an exact failure-time prediction or proof of safety before it.

## Latest V2.1 historical result, distinct from legacy

Historical protocol hash: 8b2e6dfceffe391dfab7b2ba18fc1f8d3c736c6329a5f7e93175bf7db1e54d57. This hash is a conversation record, not verification of a currently recovered original file.

First preregistered electrical/controller convergence checkpoint: 0.6 s. Fault onset: 0.60005 s. The fixed positive-P warm-up was finite battery discharge, not a sustainable closed battery-energy orbit.

Historical warm-up checkpoint values:
- Wdc: 21,914.743372215053 J
- WL: 277.1038270595847 J
- Pb: 815,639.6755124972 W
- Wdc / nominal 21,600 J: 1.0145714524173635
- WL / rated 397.09750202003335 J: 0.6978231433085292

Historical exact fault-onset values from the 10 us trace:
- Wdc: 21,915.135193267946 J
- WL: 276.7121693063766 J
- Pb: 815,639.6755381202 W
- id: 929.3461775581621 A; iq: -735.8027745282857 A
- Current: 0.8347675377506103 pu; Vdc: 1.0072683814559669 pu

Historical certificate outputs:
- Aggregate headroom H: 4,341.250139445723 J
- First-root obstruction: 17.088203932514614 ms after fault onset
- F(20 ms): 4,936.85665000438 J
- Excess F(20 ms)-H: 595.6065105586567 J
- Maximum-prefix time: 59.86723888893313 ms
- Maximum-prefix energy gain: 8,870.613573156854 J
- F(150 ms): -11,236.075124967138 J; clearance alone did not prove failure

Historical outward-rounded thresholds, which the recovered calculator must check against NEW inputs rather than assume:
- Pb0>=815,600 W; Wdc0>=21,915 J; WL0>=276 J
- Source export<=480,001 W; inverter loss<=7,200 W; copper loss<=23,941 W
- Wdc_max<=26,137 J; WL_max<=398 J
- Headroom upper bound: 4,344 J
- 20 ms accumulated-energy lower bound: 4,936.04 J
- Strict contradiction margin: 592.04 J

The earlier diagnostic state at 0.20005 s gave a different first root, 17.0350722465 ms. That number is not the V2.1 result and must not be substituted for it.

Historical observations, not current evidence: baseline DC stop 5.89596979813 ms after the V2.1 fault; strict current peak 1.0000746498725568 pu; startup PCC apparent-power overshoot about 1.248563 MVA. The healthy convergence window and fault-onset state must be audited separately from unsafe sampled startup. The observed controller violated current before DC failure and was not an example of a current-safe policy surviving to the universal root.

The prior 10 us/5 us calculations reportedly agreed to roughly 1.5e-9 J in the 20 ms margin. The parent reported independent abc agreement in files named DC_BOUND_INDEPENDENT_REVIEW.md and DC_BOUND_ABC_NUMERIC_CHECK.json. Neither those files nor old raw outputs have been recovered by this worker; no new cross-audit claim is made here.
