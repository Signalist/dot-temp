# Actual-power recovery projections in grids with memory

## 1. Scope and physical contract

This extends the W6 single-task model, not a GPU measurement claim. Work W is fixed
before execution, is independent of the control, and has known support [0,M]. Until
EOS, progress obeys ẋ=s(p), with p actual dynamic power, s increasing, s(0)=0,
and |ṗ|≤R. EOS is observed immediately in the ideal theorem. Following EOS, a
physically available dissipative return follows ṗ=−R until p=0. Every path's dynamic
energy and power-return time are charged: J=E[∫(p+c)dt] through that return. The
complete waveform is then extended by zero. No subsequent job starts automatically.

The separate grid interface is ΔP_PCC=g p+e_P about a fixed baseline. Neither g nor
e_P has been measured for a GPU/facility in this study. For a linear model,
q̇=Aq+BΔP_PCC, y=Cq+DΔP_PCC, with a common initial grid state and common exogenous
future, all grid constraints are evaluated on the same absolute clock and through
the full zero-input decay tail. A p=0 endpoint does not reset q. The cost above
does not charge additional grid-settling idle time and does not establish a
grid-reset regenerative deployment model. If settling occupancy is charged, or
the next task arrives during decay, that is a different optimization problem.

The simulation uses the stable small-signal swing mode

δ̇=2πf, M_H ḟ=−D_m f−Kδ−g p,
M_H=2H S_base/f_0, K=M_H ω_n²/(2π), D_m=2ζω_n M_H.

It is a modal surrogate with memory, not an identified network or validated PCC
transfer. H=4 s, S_base=1000 MW, f_0=60 Hz and g=20 MW per model power unit are
declared modeling parameters. Frequencies in the 0.25–0.7 Hz range are motivated
by inter-area electromechanical modes, not calibrated from this facility. The
0.05 Hz budget is a study/planning allocation, not a cited regulatory threshold,
equipment ride-through limit, or verified load-specific allowance.

## 2. Physical-time strengthening of terminal recovery

Let A_s(p)=∫₀ᵖs(r)dr, z=A_s(p), and C_R z(x)=min{z(x),R(M−x)} with
z(0)≤RM. Assume physically realizable finite-completion paths for the EOS values
under discussion. A finite expected objective alone guarantees this only almost
surely; a zero-probability endpoint must be checked separately.

**Theorem 1 (pathwise physical-time domination).** For every such EOS w,

p_(C_R z,w)(t) ≤ p_(z,w)(t) for every t≥0,

where both powers include the real post-EOS return and are extended by zero.

**Proof.** z(x)−R(M−x) is nondecreasing because its derivative is z′+R≥0 a.e.
Thus the projection can change only a terminal suffix. Prior to first contact
x=a, the physical paths coincide. If w≤a, the paths and their returns coincide.
Otherwise both reach p_a at the same time t_a. From that moment the projected
path is the single physical waveform [p_a−R(t−t_a)]_+, whether EOS occurs during
it or at its endpoint. Every nonnegative R-slew original continuation, including
its own possibly earlier EOS and subsequent return, lies above that lower
envelope. This proves the assertion without comparing the two EOS times. ∎

This also proves E_C(w)≤E(w) and T_powercycle,C(w)≤T_powercycle(w), not merely a
weighted-cost inequality. It uses real burn availability. It does not authorize
omitting recovery energy or starting another load on the shortened cycle.

**Corollary 1 (positive-memory preservation).** Any causal order-preserving map
from the full power waveform to stress, with the same initial state/exogenous
path, preserves the projection for upper stress bounds and nondecreasing stress
costs. In particular, y=y_free+D p+h*p with D≥0 and h≥0 a.e. obeys y_C≤y.
The statement includes the entire tail and time-varying upper thresholds.
It does not cover two-sided bounds, lower bounds, oscillation amplitudes, or
frequency outputs whose kernels change sign.

**Theorem 2 (universal LTI boundary).** For a scalar causal LTI output with locally
integrable h and scalar feedthrough D, universal same-clock pointwise order
preservation under every W6 recovery projection holds iff D≥0 and h≥0 a.e.
The necessity refers to the full admissible profile class, not a restricted
parameterized family. Its exact restricted-class criterion is
(D I+h*)d≥0 for each attainable loss waveform d=p−p_C.

**Necessity sketch.** Start with a fixed idle-to-idle recovery triangle. On its
final descent, at p=ε, replace the remaining useful descent by a hold at ε lasting
L_ε=A_s(ε)/(R s(ε)), then observe deterministic EOS and return. It completes the
same work; C_R recovers the original triangle. The removed power is a nonnegative
shrinking trapezoid of area εL_ε. Since 0<L_ε≤ε/R, its normalized shape converges
to a point mass at the reference return endpoint. At a Lebesgue point where
h(τ)<0, its filtered effect is negative for sufficiently small ε. If D<0, use
the shrinking waveform at a point of positive height; the direct term dominates
the vanishing local convolution. Sufficiency is Corollary 1. Details and the
exact signed-kernel witness are independently reviewed in ../review/.

This is an order-compatibility result, not a new general theory of positive
systems. Its useful increment is the physical-time strengthening that allows
the existing W6 projection to be carried through a memory operator.

## 3. Why the old convexity does not transfer automatically

The W6 hazard theorem makes the reduced energy/time functional convex in z.
It says nothing about an additional constraint on y at physical time, where
t(x)=∫₀ˣ1/s(P(z(u)))du. The memory-state work dynamics are

dq/dx = [Aq+B g P(z)]/s(P(z)),

which are generally nonlinear in (q,z). Even positive-memory projection
preservation alone does not imply a convex work-domain feasible set. The
critical-power cap has a different physical-time effect (it can prolong work),
and is not covered by Theorem 1. Fixed-clock grid commitments can invalidate it.

### A stable zero-state counterexample with an analytic proof

Set s(p)=p, R=.01, a=4π/3, M=Ra² and p(0)=0. The original actual-power path rises
at R to Ra over [0,a], holds until EOS at 1.5a, then returns at −R until 2.5a.
Its recovery projection rises identically and then returns immediately to zero
at 2a, reaching EOS at that endpoint. Both complete exactly M work, and p_C≤p.
For the common zero-state oscillator δ̈+.02δ̇+1.0001δ=−p and y=−δ̇, the original
all-time absolute peak is 0.01968875539, whereas the projected peak is
0.03541856137. Thus the common two-sided budget |y|≤.025 is destroyed by the
otherwise beneficial projection. These normalized units demonstrate a structural
failure, not a calibrated facility frequency prediction.

This violation has a numerical-search-independent proof. With damping α=0,
the response to a unit ramp is F₀(t)=1−cos t. The original maximum is at most 2R
and its postreturn tail vanishes because 1.5a=2π. The projected response at
T=2.5a is 3R. For α=.01 and stiffness 1+α², the ramp response is
Fα(t)=[1−e^(−αt)(cos t+α sin t)]/(1+α²), and on [0,T],
|Fα−F₀|≤α(T+1)+2α²=:B<.115. Each waveform is a signed sum of ramp responses
with coefficient absolute sum 4R. The original pre-T peak is at most
2R+4RB<.0246 and projected y(T)≥3R−4RB>.0254. For the original after T,
its complex coefficient factors as
(1−e^((α−i)a))(1−e^((α−i)1.5a)); using 1.5a=2π bounds the entire tail below
.0015. Hence both feasibility and failure are analytic all-time statements.

### Direct work-domain nonconvexity

The independent post-reset witness uses β=.5, c=1, R=1, M=2, the swing mode
ω_n=2π*.4, ζ=.08, M_H=400/3 and gain36.8. Two exact three-decimal z-node arrays
at Δx=.125 respect the initial/recovery cones, the critical cap and slew exactly.
With zero initial grid state and deterministic endpoint EOS, their global
absolute peaks are .04987635051 and .04688435190; the exact midpoint peaks at
.05024113362. Thus both satisfy |f|≤.05 while their midpoint fails. Every maximum
occurs after the physical power return. Exact node arrays, stationary-point
enumeration and independent 60/100-digit evaluations are in
../review/CONVEXITY_INDEPENDENT_VERIFIED.json. The decimal evaluations are not
outward-rounded interval certificates; unlike the first counterexample this
one is a high-precision evaluated witness rather than a separate symbolic bound.

## 4. Conservative grid-safe alternative that preserves the convex core

Let a stable impulse response h include the PCC gain, let input p be nonnegative
and bounded by P, and define

G_+(h)=∫₀∞max(h,0), G_−(h)=∫₀∞max(−h,0), G=max(G_+,G_−).

**Proposition 3 (nonnegative-input guard).** For zero input history,
|h*p|(t)≤P G at every time, including after p returns to zero. Thus P≤F/G
is a sufficient scalar actual-power cap for the frequency allocation F.
It is the exact induced norm for arbitrary bounded nonnegative inputs without
the slew constraint; it is generally conservative for the W6 workload class.

Proof: positive and negative parts bound the convolution above by P G_+ and
below by −P G_−. Sharpness without slew follows by selecting input P on the
favorable-sign lags over increasingly long finite histories. This classical
bound is not claimed as a novel control algorithm.

For the swing mode, a=ζω_n, b=ω_n sqrt(1−ζ²), and κ=g/M_H,

h(t)=−κ e^(−at)[cos(bt)−(a/b)sin(bt)],
G_+=G_−= κ/ω_n * exp[−ζ acos(ζ)/sqrt(1−ζ²)]
                    / {1−exp[−πζ/sqrt(1−ζ²)]}.

The equality of sign areas follows from ∫h=0. G increases with κ, decreases as
1/ω_n, and decreases with ζ in 0<ζ<1. A box with gain≤1.1g, mode frequency≥0.9ω_n,
and damping ratio≥0.8ζ has its largest G at that corner. This is a model-parameter
box, not an experimentally inferred uncertainty set.

For completeness, with k=ζ/sqrt(1−ζ²) and θ=acos ζ,
d log G/dζ=[−θ+ζsqrt(1−ζ²)−π/(exp(πk)−1)]/(1−ζ²)^(3/2)<0,
because θ−sinθ cosθ>0 for θ∈(0,π/2). The uncertainty-corner argument is
therefore analytic rather than an inference from finitely many corner replays.

The constant cap z≤A_s(P) is convex. It is preserved by both original W6
projections when the initial state respects it. Therefore the old sharp hazard
condition h_W(x)(M−x)≤(1+2β)/(1+β) still gives a convex energy/time problem
within this sufficient grid-safe cap class. It does not solve the larger exact
grid-constrained problem. A global Bellman reference must share the same cap
before its objective is compared with the convex solver.

### Actual-power errors and nonzero grid state

For ΔP=g p+e_P, let h_1 be the unit-PCC impulse response, h=g h_1, and suppose
||e_P||∞≤ε_P. If B_0 bounds the common initial-state/exogenous output for all time,

P G(h)+||h_1||₁ ε_P+B_0 ≤ F

is sufficient. For uncertain models use the suprema of the relevant gains over
the specified set. This is valid only if those sets/bounds are valid; none was
identified from hardware here. If the right-side reserve is nonpositive, the
guard cannot admit positive service. Measurement filtering is part of the
identified transfer, not an excuse to hide faster violations.

## 5. Slew-aware all-history support bounds

Since H(t)=∫₀ᵗh(r)dr is the swing step response, an idle-start continuous input
with zero past (p(0)=0, no initial step) obeys h*p=H*ṗ. Thus

|f|≤R||H||₁,
||H||₁=κ/ω_n² coth[πζ/(2sqrt(1−ζ²))].

For a convolution starting at zero with p(0)=p0>0, the identity instead is
h*p=p0 H+H*ṗ, so add p0||H||∞ to the slew bound, or explicitly include the
feasible prior ramp/history. The amplitude guard PG is unaffected. The minimum
of the appropriately qualified slew bound and P G is a valid simple bound. A joint amplitude/slew
bound can be considerably less conservative and can be computed by an ordinary
linear program with explicit approximation remainders.

Fix lag horizon L and spacing Δ. Optimize ±∫₀ᴸh(t)v_Δ(t)dt over nodal linear
v_Δ with 0≤v≤P and |v_(i+1)−v_i|≤RΔ. Endpoint values are free. Hat-weight
integrals are analytic for the swing kernel. Let V_Δ be the larger support value,
ε_tail=P∫ᴸ∞|h| and ε_int=(RΔ/2)∫₀ᴸ|h|. Then the exact all-history nonnegative
amplitude/slew induced support V satisfies

max(0,V_Δ−ε_tail) ≤ V ≤ min(PG,R||H||₁,V_Δ+ε_tail+ε_int).

Proof: interpolate any feasible continuous lag input. It remains amplitude/slew
feasible, and its interpolation error is at most RΔ/2. The omitted tail has the
stated bound. Conversely extend an optimal lag profile in the remote past to
zero by a feasible ramp, whose omitted contribution is at worst −ε_tail. Extend
the current endpoint into the future by a return; causality leaves its current
output unchanged. Δ→0 and L→∞ close the analytic bounds. The provided
implementation uses ordinary floating LP/complex exponential arithmetic, not
outward rounding; analytic error budgets do not certify floating solver error.
The final code does not equate a solver's objective with a certified LP upper
bound: it evaluates the weak dual expression λᵀb+P∑[w−Aᵀλ]₊ for λ≥0, including
the box residual explicitly. Lower witnesses are inward-scaled by a 10⁻⁹
relative reserve and their serialized power/time amplitude and slew constraints
are checked with exact rational arithmetic. Pre-repair LP paths with tiny
floating slew excesses remain archived. These path checks still do not enclose
the analytic kernel weights, costs or upper-bound evaluations outwardly.

A cap selected from a valid upper support bound is still a constant cap and so
retains the original convex core. This replaces an unjustified exact-grid
convexity claim with a convergent conservative guard. The LP is classical.

## 6. EOS latency and model execution

Suppose delayed EOS reporting follows the same pre-EOS physical trajectory for
at most d extra seconds and then returns at −R, with 0≤p≤P and |ṗ|≤R. The cap
guarantee remains valid irrespective of the delay. Relative to immediate return
from the same true-EOS state, the added energy/time objective is bounded by

0≤ΔJ≤2(P+c)d, and T_delayed−T_immediate≤2d.

Indeed the extra pre-return integral is at most (P+c)d; the return-value change
is at most (P+c)/R times the possible power increase R d. Nonnegativity follows
from fastest return being the minimum possible continuation cost. This compares
the same pre-EOS trajectory only. Sampling, service-model errors, thermal state,
or cap-command tracking errors require separate accounting; the bound does not
turn a requested cap into measured actual power.

An event-driven ideal executor uses u=z′(observed work), changing slope at a work
node or EOS. A sampled ideal executor uses observed progress, a slew-limited
actual-power state and a hard actual cap. Simulating these executors tests code
and model consistency. It does not identify a realizable GPU interface.

## 7. Claims and exclusions

Supported: physical-time recovery domination; exact universal order-preservation
boundary; explicit signed-grid failure; sufficient robust all-tail guards that
retain a conditional convex optimization problem; model-only executor tests.

Not supported: new generic DP/LP/MPC; exact convexity of the signed-grid problem;
beating a same-information global optimum; real GPU energy/frequency improvement;
site compliance; concurrency; hard deadlines recovered from the earlier failed
candidate; exact grid-state reset at p=0; hardware-calibrated model uncertainty.

Physical context sources: NERC's 2026 large-load action plan and 2025/2026
large-load modeling/guidance work emphasize load dynamics and validation;
PNNL-35221 describes inter-area-mode sensitivity in the 0.15–1 Hz band. These
motivate the question, not the chosen parameters or a universal 0.05 Hz limit.
https://www.nerc.com/initiatives/large-loads-action-plan
https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-35221.pdf
