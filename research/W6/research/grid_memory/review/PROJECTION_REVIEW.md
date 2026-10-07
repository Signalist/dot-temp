# Independent review: recovery projection and grid memory

## Bottom line

The proposed pathwise real-time power domination is correct for the stated isolated-cycle W6 contract. It is stronger than energy/cycle-time domination, needs no EOS density or objective convexity, and yields exact preservation for any common-clock, output-order-monotone upper constraint/cost of a positive input-output system. It does **not** establish positivity for swing-frequency outputs, preservation of two-sided frequency budgets, or convexity in work coordinates.

The following are essential qualifications: same physical initial power; a well-defined physical no-EOS trajectory; the same absolute clock, grid initial state and exogenous path; actual burn counted in the power input; power zero-extended after return; and a constraint/cost that is monotone in the relevant oriented output trajectory. A different next-job start time is not the same exogenous input.

## 1. Power domination theorem and proof

Let R>0, s(0)=0 and s(p)>0 for p>0. Let A(p)=integral_0^p s(q)dq, P=A^{-1}, z=A(p). Take a physically realizable productive-until-EOS profile z with |z'|<=R and z(0)=z0<=RM. After EOS, actual power returns at slope -R and remains zero. Define Cz(x)=min(z(x),R(M-x)). Then, for every EOS w in [0,M] and every common physical time t>=0,

p_{Cz,w}(t) <= p_{z,w}(t).

Proof. d(x)=z(x)+Rx-RM is nondecreasing because d'=z'+R>=0 a.e. Therefore the recovery cap can only replace a suffix. If there is a first contact a<M, z(a)=R(M-a), let t_a be its physical arrival time and p_a=P(z(a)). Up to that time both productive histories coincide. If w<a, EOS and all later burn coincide as well. If w>=a, after contact the capped profile is productive maximum descent, whose physical waveform is

q(t)=[p_a-R(t-t_a)]_+.

While productive, its work is x(t)=M-A(q(t))/R. Hence it reaches EOS w during that same descent and then continues exactly the same waveform as burn. Thus its entire postcontact power, independently of w>=a, is q. Any original full-cycle continuation from the common power p_a satisfies p(t)>=p_a-R(t-t_a) by its lower slew bound, and p(t)>=0. This gives the result, including the interval after the projected cycle has finished. If no contact is reached, the physical histories are identical. Contact only at a=M causes no nontrivial replacement. QED.

Concavity, the value of c and the EOS law are not used in this argument. If z0>=RM, the physically admissible global fastest return from p0 has the analogous pointwise domination and completes every w<=M before zero, but min(z,R(M-x)) is not an initial-state-preserving projection when z0>RM.

### Completion subtlety

Finite expected cost ensures almost-sure completion only. It does not justify a finite physical map for every zero-probability EOS endpoint. State the theorem for all physically defined EOS trajectories; require finite completion for every w if the claim explicitly quantifies over every completed cycle. Alternatively, an unattainable contact leaves both policies physically identical forever. Do not silently infer hard endpoint completion from finite expectation.

## 2. Exact preservation statement

For a scalar draw and possibly vector output, write

y_p(t)=y_free(t)+D p(t)+integral_0^t h(t-u)p(u)du.

Here y_free includes the common initial-state response and the same exogenous input, not an assumption that the grid starts at rest. The following sufficient conditions are exact for input-output order preservation:

- D is componentwise nonnegative
- h(t) is componentwise nonnegative almost everywhere

Then y_C(t)<=y_z(t) componentwise for every t>=0. Internal-state positivity is unnecessary: input-output positivity of the constrained channels suffices. A Metzler state matrix with nonnegative input/output/direct matrices is only a convenient sufficient realization condition.

Any downward-closed feasible output set is preserved. Examples include y_j(t)<=b_j(t) for all calendar times, nonnegative weighted positive-part exceedance integrals, and coordinatewise nondecreasing functionals of the entire output trajectory. Monotone chance/risk constraints inherit the result under the same samplewise coupling. Stability is useful for tail decay and finiteness, but not needed for finite-time order.

An absolute-value or squared-frequency cost is not generally coordinatewise monotone. Neither is a lower output bound. The constraint must be oriented first: a lower bound on a physical frequency is an upper bound on its frequency-deficit output, and the kernel for that oriented channel is what must be checked. Two-sided frequency bounds do not follow merely from a positive load-to-one-sided-output kernel.

For a fixed restricted profile class, let D_C be its attainable nonnegative power differences p_z-p_C, with their EOS choices. The **exact restricted test** is

D d(t)+(h*d)(t)>=0 for every d in D_C and all t.

Positivity of the whole kernel is sufficient, but can be stronger than necessary for a highly restricted D_C. It is incorrect to call a signed kernel universally safe merely because it passes finitely many sampled waveforms.

### Necessity over the full W6 class

For a continuous scalar kernel (and, with the usual approximate-identity interpretation, a locally integrable kernel), nonnegativity is also necessary for universal pointwise preservation even within a fixed deterministic EOS W=M, idle-start W6 class. Start with an ordinary recovery triangle and terminal return time T. Follow it until its descending power is epsilon. Instead of continuing descent, hold epsilon until EOS, for

L_epsilon=A(epsilon)/(R s(epsilon)),

then return at -R. For increasing s, 0<L_epsilon<=epsilon/R. Its recovery projection is the original triangle. The removed draw d_epsilon is a nonnegative trapezoid on [T-epsilon/R,T+L_epsilon] with area epsilon L_epsilon. Normalized by that area, it tends to a unit mass at T. If h(tau)<0, then (h*d_epsilon)(T+tau)<0 for sufficiently small epsilon. Thus projection increases that output. A negative direct feedthrough is detected near the start of a sufficiently short such pulse, where convolution is of smaller order than Dd.

This proves the useful universal iff characterization D>=0, h>=0 a.e.; it does not claim a signed kernel must fail for every policy, every fixed budget, or every constrained subclass.

## 3. Stable swing-frequency counterexample, with an exact all-time constraint

Take s(p)=p, R=0.1, M=0.025, and p0=0. The original full-cycle power is

p_z(t)=0.1t,                          0<=t<=0.5
       0.05,                         0.5<=t<=0.75
       0.1(1.25-t),                  0.75<=t<=1.25
       0,                            t>=1.25.

EOS occurs at 0.75, since productive work is 0.0125+0.0125=M. In work coordinates, z=x until x=M/2 and z=M/2 thereafter. Its recovery projection replaces the hold/burn suffix by the triangular waveform

p_C(t)=0.1t,                         0<=t<=0.5
       0.1(1-t),                     0.5<=t<=1
       0,                            t>=1.

The projected EOS W=M is at t=1, with zero burn. Both satisfy the physical slew and have p_C<=p_z everywhere.

Consider a stable single-mode swing model with load input p, angle delta, and frequency deficit y=-delta_dot:

delta_ddot+0.2 delta_dot+1.01 delta = -p.

The poles are -0.1 +/- i. Its load-to-deficit impulse response is

h(t)=exp(-0.1t)(cos t-0.1 sin t),

which changes sign. This is the ordinary small-signal damped swing oscillator with inertia 1, damping 0.2 and synchronizing stiffness 1.01, in normalized units.

Set T=1.25 and choose the common initial state exactly as

delta0 = -integral_0^T exp(0.1u) sin(u) p_z(u)du,
omega0 =  integral_0^T exp(0.1u)(cos u+0.1 sin u) p_z(u)du.

Numerically (delta0,omega0)=(-0.02279665,0.03342640). This is a small-angle, nonzero initial grid mode, not an altered grid state between policies. There is no exogenous forcing. By construction the original state is exactly zero at T, and for 0<=t<=T its deficit is

y_z(t)=-integral_t^T exp(0.1(u-t))[cos(u-t)+0.1 sin(u-t)]p_z(u)du <=0.

The inequality is exact because T=1.25<pi/2+atan(0.1), the first positive zero of the bracket. For t>=T, y_z=0. Thus the original respects any nonnegative all-time upper deficit limit.

The nonnegative removed draw d=p_z-p_C has support [0.5,1.25], area 0.0125, and trapezoid segments

0.1(t-0.5) on [0.5,0.75],
0.025 on [0.75,1],
0.1(1.25-t) on [1,1.25].

At t=3 all lags 3-u lie in [1.75,2.5], strictly inside a negative lobe of h. Hence

y_C(3)=-integral h(3-u)d(u)du >0.

The minimum of -h on this interval is -h(1.75)>0.232, giving y_C(3)>0.0029. Consequently the uniform all-time underfrequency constraint y<=0.002 is satisfied by the original and violated by its recovery projection. Direct evaluation gives y_C(3)=0.0060783095 and projected positive maximum approximately 0.009191962 near t=3.82. The stricter analytic lower-bound argument, rather than an intersample maximum, suffices to prove violation.

This is a one-sided underfrequency counterexample with a common nonzero initial state. It does not by itself establish an increased zero-initial-state two-sided peak. Its initial state was deliberately chosen to make the proof transparent; that is legitimate against a theorem quantified over common initial states, but should be stated plainly.

## 4. Scope boundaries that should be explicit in the paper

1. Full return and entire grid tail are included. Checking only until EOS or task/cycle completion discards physical grid memory.
2. Compare outputs at the same absolute time. The theorem alone is not a comparison of states evaluated at each policy's different cycle-completion time.
3. Fixed exogenous demand/generation is coupled identically. A scheduler that launches another job as soon as the earlier projected cycle ends changes future input and needs a separate argument.
4. The critical cap is a work-coordinate cost reduction, not a proved real-time power ordering. Its slower service can shift draw later. Positive-grid constraint preservation does not automatically transfer to that cap.
5. Convexity of the old objective on a convex work-profile cone is not convexity of new grid-memory constraints. The z-to-real-time-waveform map includes a nonlinear time change.
6. An EOS-state-only constraint is not automatically an isotone common-clock output functional, because EOS times differ.
7. Added grid penalties can preserve recovery dominance if they are monotone, but can still invalidate a prior critical-cap argument or a prior randomization/convexity statement.

## Source for physical model interpretation

The normalized oscillator is derived explicitly above. A primary-source description of generalized inertia, damping and synchronization constants for a single-unit/infinite-bus swing model is Chatterjee et al., *Small-Signal Stability of a Unified Single-Unit Infinite-Bus Swing-Equation Model for Generators and Inverters*, National Laboratory of the Rockies publication record: https://research-hub.nlr.gov/en/publications/small-signal-stability-of-a-unified-single-unit-infinite-bus-swin/ . The counterexample itself is a new construction here, not a reported result from that source.

## 5. Stronger analytic counterexample: stable, zero initial state, two-sided budget

The engineered initial state is unnecessary. The following independent construction has zero initial grid state, no exogenous forcing, a stable swing oscillator, and a strict violation of an all-time symmetric frequency budget.

Set a=4*pi/3, R=0.01, s(p)=p, M=R*a^2, and p0=0. The original rises at R for a seconds, holds power Ra for a/2 seconds until EOS, then descends at -R for a seconds. Its return time is T=5a/2. The recovery projection is the triangle that rises for a seconds and immediately descends for a seconds. These are the same admissible W6 shape as Section 3, with another time scale. In work coordinates, z=Rx up to M/2 and z=RM/2 thereafter; recovery replaces the constant suffix by R(M-x).

Take delta_ddot+2*alpha*delta_dot+(1+alpha^2)*delta=-p with alpha=0.01, output y=-delta_dot and grid initial state zero. Its poles are -0.01 +/- i. For a unit ramp input define

F_alpha(t) = [1-exp(-alpha*t)(cos t+alpha*sin t)]/(1+alpha^2),  t>=0,
F_alpha(t) = 0,  t<0.

The entire responses, including tails, are exactly

y_z(t)=R[F_alpha(t)-F_alpha(t-a)-F_alpha(t-3a/2)+F_alpha(t-5a/2)],
y_C(t)=R[F_alpha(t)-2F_alpha(t-a)+F_alpha(t-2a)].

### Analytic separation, independent of numerical maximization

At alpha=0, the original satisfies |y_z,0(t)|<=2R for every t:

- before a, y/R=1-cos t
- from a to 3a/2=2pi, y/R=cos(t-a)-cos t, with magnitude at most sqrt(3)
- during the return, y/R=-1+cos(t-a)
- after T, y=0 exactly

Meanwhile y_C,0(T)=3R. For every 0<=t<=T,

|F_alpha(t)-F_0(t)| <= alpha*(T+1)+2*alpha^2 =: E.

For alpha=.01 and T=10pi/3, 4E<.46. Both response coefficient vectors have l1 norm 4R. Thus throughout [0,T],

|y_z,alpha(t)| <= (2+4E)R <2.46R,
y_C,alpha(T) >= (3-4E)R >2.54R.

The original tail cannot hide a larger peak. For t>=T, its magnitude is bounded by

R/sqrt(1+alpha^2) * exp(-alpha*t)
 * |1-exp((alpha-i)*a)| * |1-exp((alpha-i)*3a/2)|.

Since 3a/2=2pi, the last factor is exp(2pi*alpha)-1. At alpha=.01 the whole bound is less than .15R, even if the exp(-alpha*t) factor is replaced by 1. Therefore the uniform symmetric budget |y(t)|<=2.5R=.025 holds for the original at all times and fails for its recovery projection. This is an analytic counterexample; no sampled peak search is needed for the separation.

The output here is angular-frequency deficit if delta is electrical angle. Divide both y and its budget by 2pi to express a Hz deficit. The example is a normalized, small-signal modal construction, not a fitted facility model.

### Independent high-precision exact-extrema values

`verify_swing_exact.py` evaluates the closed-form ramp responses at every inter-knot stationary point and includes the complete tail. It gives

- original all-time absolute peak: 0.01968875538750935546 at t=pi
- projected all-time absolute peak: 0.03541856137428691928 at t=7.00718019989798146
- projected value at original return T: 0.02817164842321510225
- M=0.17545963379714415322

The stationary-point equation on each piece is a single sine with a phase shift. After the final knot, successive absolute stationary values have ratio exp(-alpha*pi/beta), so only the first two tail stationary points can be candidates for the infinite-horizon absolute maximum. The script does not discretize time to locate maxima. Results were repeated at 60 and 100 decimal digits with all 40 printed digits unchanged. They are high-precision evaluations of analytic expressions, not an outward-rounded interval certificate. The analytic inequalities above separately certify the projection violation.

## 6. Independent verification of the work-coordinate nonconvexity witness

A parent-supplied witness was independently mapped from piecewise-linear work profiles to exact piecewise-affine physical power and propagated through the oscillator. For s(p)=sqrt(p), A(p)=(2/3)p^(3/2), hence at a node p=(3z/2)^(2/3), and a segment of work slope u has physical slope p_dot=u. Its exact duration is (p_next-p)/u, or delta_x/sqrt(p) if u=0.

Use x=0,.125,...,2, R=1, M=2, c=1. Both profiles below are exact three-decimal rationals:

z1=[0,.125,.210,.085,.210,.335,.306,.181,.306,.431,.500,.375,.250,.375,.250,.125,0]
z2=[0,.093,.218,.154,.103,.228,.353,.478,.449,.324,.199,.324,.449,.342,.217,.125,0]

They and their work-coordinate midpoint satisfy both Lipschitz slew inequalities, the initial reach cap z<=x, terminal recovery cap z<=2-x, and critical cap z<=2/3. Their piecewise-linear interpolation is feasible because all these constraints are affine/convex in work coordinates.

Use the zero-state grid

delta_dot=2pi*f,
f_dot= -omega_n^2*delta/(2pi)-2*zeta*omega_n*f-(g/(400/3))*p,
omega_n=2pi*.4, zeta=.08, g=36.8.

The exact-extrema high-precision global absolute peaks, including the complete post-return tail, are

z1:       .04987635051167888784, at t=3.26443371845965673
z2:       .04688435190489452814, at t=3.26420305040502164
midpoint: .05024113362147024627, at t=3.22270741982003181

All three maxima occur in the post-return tail. Thus both endpoints satisfy a symmetric .05 Hz study budget and their midpoint violates it. This independently verifies a strict nonconvexity witness for the exact grid-feasible work-profile set. It is a different claim from projection failure.

Important corrections found during review:

- The original long-decimal arrays have 1e-16-scale slew violations if those printed decimal strings are treated literally; do not call them exact feasible rationals without repair
- Rounding to three decimals fixes slew exactly, but gain 36.9 gives z1 peak .05001188407, slightly over .05; use gain 36.8 with those rounded nodes
- All-time checks matter: the witness is a tail violation, not an active-task peak
- Saved evaluation was independently repeated at 60 and 100 decimal digits, agreeing in all 40 printed digits; it uses mpmath arithmetic and closed-form root enumeration, not directed-rounding interval certification

See `CONVEXITY_INDEPENDENT_VERIFIED.json` for all stationary candidates, physical time knots, cone slacks, and both the exploratory and repaired variants.

## 7. Review of the parent theory's guard, support LP and latency propositions

The formulas and bounds in `theory/GRID_MEMORY_THEOREMS.md` were independently checked on 2026-10-04 after the environment reset:

- Positive/negative impulse areas correctly give the exact arbitrary-nonnegative-input L-infinity support PG, and the swing expression is consistent with summing the step-response extrema
- The swing step-response norm is kappa/omega_n^2*coth(pi*zeta/[2sqrt(1-zeta^2)])
- The R*||H||_1 derivative bound needs a zero-past, continuous/slew-feasible input (no initial step); the text's zero-past assumption supplies this for idle-start profiles
- The LP nodal interpolation remains feasible, its pointwise approximation error is at most R*Delta/2, and the stated integral/tail error bounds and remote-past extension lower bound are sound
- Endpoint values being free is correct for an all-history support envelope; that envelope is generally larger than the single-job W6 class
- The EOS-latency bound Delta J<=2(P+c)d and added return time<=2d are correct for the same true-EOS state and the same pre-EOS trajectory; the fastest-return lower bound makes the objective difference nonnegative
- These are analytic approximation bounds; LP floating feasibility/objective error still needs its own treatment before calling the implementation an interval certificate

No new substantive proof flaw was found in those propositions. Keep the specified common-clock, no-automatic-next-job and zero-past qualifications visible.

## Recovery/provenance note

The execution transport disconnected around 14:16 UTC and previously visible Oct4 artifacts disappeared. This review file and the verification code/results were freshly recreated/rerun after the parent's resume authorization. Pre-reset raw outputs were not recovered or relabeled as verified artifacts. The exact formulas were retained in conversation context; the independent midpoint arrays were resent by the parent. All numeric statements in Sections 5-6 are from the new exact-response rerun.

### Nonzero initial-power addendum

If the task begins at p0>0 while the convolution is defined with zero history, integration by parts gives h*p=p0 H+H*p_dot, so R||H||_1 alone is not a valid slew guard. Either restrict that guard/support-LP interpretation to an idle start or a genuinely continuous zero-past history, or add p0||H||_infinity to the derivative bound. The amplitude-only PG guard and recovery theorem are unaffected. This distinction was sent to the parent explicitly.
