# Final narrow scope addendum

## Ordered actuator-parameter robustness: passes

The new ordered-parameter robustness paragraph in `theory/PREFIX_COUPLED_CERTIFICATE.md` is valid for the stated fixed-zero initial power and held-zero delay, positive upper command, and clipped-lag structure.

For upper command U>0 and upward ramp r>0, the pointwise largest power after enabling satisfies

    b_max'=min{r,(U-b_max)/tau}, b_max(0)=0,

and lies in [0,U]. Before enabling it is zero. Any admissible command is <=U, so scalar comparison bounds its trajectory above by b_max, even if that command first drives power negative. Its cumulative charge is consequently bounded above by the integral of b_max.

Compare a weaker device (U1,r1,tau1) to the certified device (U0,r0,tau0) with

    U1<=U0, r1<=r0, tau1>=tau0.

For b in [0,U1], both U1-b and U0-b are nonnegative, and

    min{r1,(U1-b)/tau1}<=min{r0,(U0-b)/tau0}.

Scalar comparison gives b_max,1<=b_max,0. A later held-zero release only reduces the weaker response further, since the maximal response is nonnegative and nondecreasing. Integrating preserves the ordering. Thus the entire box U=400–450 kW, upward ramp=25000–30000 kW/s, tau=5–6 ms, and delay=1–2 ms shares the certified favorable charge upper bound, and the 812.5 kvar prefix exclusion transfers.

No lower-command or downward-ramp change can improve this upper positive response. Additional physical restrictions can only reduce attainable charge. This establishes envelope domination sufficient for the exclusion; it does not assert that every weaker-device trajectory belongs to the stronger device's exact trajectory set. “Analytic envelope domination” is a clearer phrase than an unqualified “class inclusion.”

There is no robust-feasible 808 kvar consequence, no guarantee for changes to the electrical/grid parameters, and no need for terminal recovery. Those limits are correctly stated in the theory note.

## Supremum wording: passes

The proof excludes beta=812.5 and all beta>=812.5 by prefix contract nesting. The safe reported numerical bound is Qsup<=812.5. Exclusion of an endpoint by itself does not imply a strict inequality on a supremum; the text correctly avoids that inference. The strictly positive certificate may be continuously extendable below this value, but no additional numerical threshold is claimed or needed here.

## Finite-parameter reset diagnostic

The floating-point nullspace illustration is correct as a diagnostic. The command table, interpreted as exact exported decimal numbers, has small nonzero endpoint residuals. A 65-digit replay gives approximately

- tau=4 ms: bT=-7.0040426943e-15 kW
- tau=5 ms: bT=-0.1260462951104680361 kW
- tau=6 ms: bT=-4.6321315180e-15 kW
- integral u=1.7e-17 kJ

Therefore the existing decimal table alone should not be labeled a mathematically exact-reset waveform. There is an immediate exact version. Let

    h=.005, a=exp(-h/.004), b=exp(-h/.006), A=-100/(1+a+b),
    (u0,u1,u2,u3)=A(1,-(1+a+b),a+b+ab,-ab).

Its command polynomial is

    p(z)=u0 z^3+u1 z^2+u2 z+u3=A(z-1)(z-a)(z-b).

For four equal held-command cells, with e=exp(-h/tau),

    bT(tau)=(1-e)p(e), integral u=h p(1)=0,
    CT(tau)=integral u-tau bT(tau).

Thus exact b/C reset holds at tau=4 and 6 ms, while at tau=5 ms e differs from all three roots and bT is nonzero. The exported command numbers approximate this analytically defined waveform. This is a classical polynomial/nullspace illustration of why finitely many parameter tests do not imply continuum robust reset; no novel or robust physical-service claim follows.
