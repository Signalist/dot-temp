# Exact ideal-buffer and measurement indistinguishability boundaries

This companion supplies proofs for the original two-world question. The main lossy task-order result is in LOSS_TOLERANCE_TASK_ORDER_THEOREMS.md. All statements are conditional model results; standard rank, interval reachability, set membership, and robust LP methods are not claimed as new.

## 1. Model and three different questions

Slots t=0,...,T-1 have duration δ>0. In world j in {0,1}, strictly positive compute load d^j_t executes the declared work. The common PCC trace is z_t and ideal storage obeys

  e^j_{t+1}=e^j_t+δ(z_t-d^j_t).

Each state must lie in an allowed interval E^j_t=[L^j_t,U^j_t], usually [0,B]. A recovery requirement is represented by narrowing this interval at the specified time. Exact common recovery is E^0_τ=E^1_τ={r_τ}; an interval recovery is an actual interval, not a numerical reset. Charge/discharge bounds are

  -D^j_t <= z_t-d^j_t <= C^j_t.

An optional source interval is z_t in [z^-_t,z^+_t]. Known initial states are x_j=e^j_0.

The following questions are distinct:

1. Is a *particular observed trace z* compatible with both worlds?
2. Does *some common trace z* exist for the two complete trajectories?
3. Is there *one nonanticipative policy* hiding every trajectory in a specified class?

Pairwise feasibility answers question 2, not automatically question 3. Nor does failure to hide an entire class establish that all pairs are identifiable.

Define cumulative energies

  A^j_t=δ sum_{s<t}d^j_s, S_t=δ sum_{s<t}z_s,
  Δ_t=A^1_t-A^0_t, Δ_0=0.

Then

  e^j_t=x_j+S_t-A^j_t,
  e^1_t-e^0_t=(x_1-x_0)-Δ_t.                 (1)

## 2. A fixed observed PCC trace: exact membership test

**Theorem 1.** With known x_j and observed z, both worlds are feasible exactly when, for all t,j,

  L^j_t <= x_j+S_t-A^j_t <= U^j_t,

and all specified per-slot power/source bounds hold. Exact recovery is checked by equality at each recovery time.

**Proof.** Iterating the state equation uniquely determines each displayed state. The inequalities are precisely all the model's constraints, proving both directions. QED.

For one unknown initial state x shared by both counterfactual worlds, in known interval I, this is feasible iff

  I intersect [intersection over j,t of [L^j_t-S_t+A^j_t, U^j_t-S_t+A^j_t]]

is nonempty, together with the rate bounds. If instead each world may have a different unknown initial x_j in I, the corresponding intersection is performed separately for each j. These are different epistemic contracts.

For a single world with capacity [0,B] and unrestricted unknown x in [0,B], writing W_t=S_t-A_t and including W_0=0 gives the familiar criterion

  max_t W_t-min_t W_t <= B.

That single-buffer oscillation criterion must not be confused with the difference criterion for two separately controlled buffers.

## 3. Existence of a common trace: exact scalar corridor

For known initial states define cumulative-source corridors

  a_t=max_j(A^j_t+L^j_t-x_j),
  b_t=min_j(A^j_t+U^j_t-x_j),

and step increments

  ℓ_t=δ max(z^-_t, max_j(d^j_t-D^j_t)),
  u_t=δ min(z^+_t, min_j(d^j_t+C^j_t)).

Omit absent source bounds. First validate each x_j in E^j_0 and set the initial corridor to a_0=b_0=0.

**Theorem 2 (exact corridor reachability).** A common trace exists iff every ℓ_t<=u_t and the recursion

  R_0=[0,0],
  R_{t+1}=([lower(R_t)+ℓ_t, upper(R_t)+u_t]) intersect [a_{t+1},b_{t+1}]

never becomes empty. Equivalently, in addition to a_t<=b_t and ℓ_t<=u_t, every pair 0<=s<t<=T must satisfy

  a_t <= b_s+sum_{k=s}^{t-1}u_k,
  a_s+sum_{k=s}^{t-1}ℓ_k <= b_t.              (2)

**Proof of the recursion.** Given every reachable cumulative source value in interval R_t, its next reachable values with increment in [ℓ_t,u_t] form exactly the Minkowski sum interval. Intersecting with the next state corridor removes exactly inadmissible values. Induction proves exactness. If nonempty at T, a valid complete path can be recovered backwards: for a chosen S_{t+1}, select S_t in R_t intersect [S_{t+1}-u_t,S_{t+1}-ℓ_t]. This intersection is nonempty by the recurrence.

**Proof of (2).** Every admissible path has S_t-S_s between the indicated increment sums, so (2) is necessary. For sufficiency the untruncated lower and upper reachable endpoints at t are

  max_{s<=t}(a_s+sum_{k=s}^{t-1}ℓ_k),
  min_{r<=t}(b_r+sum_{k=r}^{t-1}u_k).

For s<=r, the lower candidate is <=b_r+sum_{r<=k<t}ℓ_k <=b_r+sum_{r<=k<t}u_k by (2). For r<=s, use a_s<=b_r+sum_{r<=k<s}u_k and ℓ<=u. Thus every lower candidate is <=every upper candidate. The recursion is nonempty. QED.

This criterion is sharper than separate pointwise cumulative-difference and instantaneous-rate tests. For example, B=4,x_0=x_1=2,C=2,D=1,δ=1 and

  d^0=(3,6,3), d^1=(6,3,6)

satisfy |Δ_t|<=4 and |d^1_t-d^0_t|<=C+D=3. Yet the rate intersection forces z_t=5. States are (2,4,3,5) and (2,1,3,2), so capacity fails in slot 3. Exact return to 2 after slot 2 also fails. Rates and common-mode energy accumulation matter.

Unknown independent initial states can be treated exactly by selecting offset c=x_1-x_0 and common coordinate W_t=x_0+S_t. Its state corridor is

  [A^0_t+L^0_t,A^0_t+U^0_t]
  intersect [A^1_t+L^1_t-c,A^1_t+U^1_t-c],

with W_0 in I_0 intersect (I_1-c), and the same increment bounds. Existence of an allowed c plus this corridor is the exact criterion. If both worlds must share the same unknown physical initial state, set c=0; do not silently optimize separate states.

## 4. Sharp cumulative-difference special cases

With common known initial state and capacity [0,B], (1) gives the universal necessary condition

  |Δ_t|<=B.                                 (3)

At exact common recovery times Δ_τ=0. At a common recovery interval of width w, |Δ_τ|<=w. For independently unknown initial states, replace Δ_t by Δ_t-c.

Without rate/source restrictions, (3) is also sufficient for existence of some common trace: its cumulative-source corridor is pointwise nonempty, and there is no restriction connecting successive source values. This is not a test of a particular observed trace.

**Theorem 3 (balanced model, exact sharp criterion including rates).** Suppose x_0=x_1=B/2; both buffers have symmetric rate bound |z_t-d^j_t|<=R; no further source restriction excludes the arithmetic mean; and every exact recovery is to B/2. A common trace exists iff

  |Δ_t|<=B for every t,
  |d^1_t-d^0_t|<=2R for every slot,
  Δ_τ=0 at every recovery time.               (4)

**Proof.** Necessity follows from state differences, differences between two bounded storage powers, and common recovery. For sufficiency choose

  z_t=(d^0_t+d^1_t)/2,
  e^0_t=B/2+Δ_t/2,
  e^1_t=B/2-Δ_t/2.

All bounds and recovery equalities follow directly from (4). Since both loads are strictly positive, z is positive as well. QED.

Condition (3) is a bound on absolute displacement from the shared initial state, not range(Δ)<=B. A feasible difference sequence can visit both +B and -B, with range 2B, while both individual buffers remain in [0,B]. Appropriate rates and positive sufficiently large baseline loads realize it.

For initial states independently chosen from the same interval I of width w<=B, with no rate/source restrictions, the exact difference criterion is

  exists c in [-w,w] such that max_t|Δ_t-c|<=B. (5)

Equivalently,

  Δ_max-Δ_min<=2B,
  Δ_max<=B+w, Δ_min>=-B-w.

For I=[0,B], because Δ_0=0, this reduces to range(Δ)<=2B. For a common unknown state (same x in both worlds), c=0 and (3) remains the correct condition. The factor of two reflects nuisance-state freedom, not a larger physical buffer.

## 5. Horizon statements, with the correct quantifiers

Suppose d^1_t-d^0_t>=μ>0 after an exact common state anchor. Then Δ_t>=μδt, so a common trace is impossible by the first sampled state with

  μδt>B,
  t_fail=floor(B/(μδ))+1.                    (6)

This capacity-only bound is sharp over the balanced class: constant load difference μ, arithmetic-mean PCC, midpoint initial energy, and R>=μ/2 attain every prefix with μδt<=B. Recovery constraints or asymmetric/insufficient rates can force earlier failure.

If the independent initial states range over an interval of width w, the corresponding worst-case monotone-drift bound is μδt>B+w. With full initial uncertainty w=B, the horizon doubles; starting the lower-demand world at 0 and the higher-demand world at B, with midpoint PCC, attains 2B/μ when rates permit.

At a repeated exact common recovery deadline, the integrated difference over that recovery block must be zero, regardless of capacity. A strictly positive mean difference cannot cross even the first such exact deadline with a common trace. An interval recovery gives its declared difference budget instead.

These are horizons for the stated *pair* or model class. They do not prove an estimator identifies a source or workload after that time. Conversely, impossibility of one universal trace over a large class does not prove that all pairs can be distinguished.

For a claimed common prefix that must still admit a future individual recovery, include continuation viability. For example, with a future exact target r at time τ and no source restriction, an individual state at t must belong to

  [r-Cδ(τ-t),r+Dδ(τ-t)] intersect [0,B].

Adding these continuation intervals to E^j_t prevents counting a prefix that cannot be extended to the promised recovery. A finite-horizon recursion otherwise certifies only obligations within its horizon.

## 6. Indefinite cyclic ambiguity despite repeated exact recovery

Take m>a>0, δa<=B/2, and a<=R. Let σ_t alternate +1,-1 and define

  d^0_t=m+aσ_t, d^1_t=m-aσ_t, z_t=m,
  e^j_0=B/2.

Every world computes at strictly positive load every slot. The two storage powers are -aσ_t and +aσ_t; states remain between B/2-δa and B/2+δa. After every two slots both return exactly to B/2. The same public PCC trace persists forever. The controller u_t=m-d_t uses only the current load, not future loads.

More generally, any feasible complete block with identical initial/final states in both worlds and equal total task energies can be concatenated indefinitely when its load, rate, and recovery contracts repeat. Zero total difference is necessary at each exact common recovery, but without the within-block corridor/rate check it is not sufficient.

Thus a finite buffer does not force eventual identification for bounded zero-mean cumulative differences. The lossful two-order example in the companion file shows that this is not merely an ideal-efficiency artifact.

## 7. Known linear grid measurements and bounded noise

Stack all measured samples into a vector. Let p be the source PCC history, H the known linear measurement operator (possibly a temporal convolution/block matrix), and

  y=Hp+n, n in N.

For fixed candidate histories p^0,p^1, their observation sets overlap exactly when

  H(p^1-p^0) in N-N.                         (7)

**Proof.** Equality Hp^0+n_0=Hp^1+n_1 is equivalent to H(p^1-p^0)=n_0-n_1. QED.

For a symmetric norm ball N={n:||n||<=ε}, N-N is the radius-2ε ball. Thus overlap is exactly ||H(p^1-p^0)||<=2ε. If the *same known noise realization* must be shared across worlds, the condition instead reduces to H(p^1-p^0)=0. The factor two applies to independently admissible unknown nuisance noise.

For a fixed observed y, exact membership is y-Hp^j in N for both j; the pairwise overlap test only asserts that some ambiguous observation exists.

Let P_θ be the physically admissible PCC histories for parameter/cause label θ, including all buffer, work, and recovery obligations. Then

  Θ(y)={θ: exists p in P_θ, n in N with y=Hp+n}.

Uniform distinguishability of θ_0 and θ_1 is exactly disjointness of HP_{θ_0}+N and HP_{θ_1}+N. For compact candidate sets and norm-ball noise, it is equivalent to

  min_{p0 in Pθ0,p1 in Pθ1} ||H(p1-p0)|| > 2ε. (8)

Compactness/attainment matters at the equality boundary. Formula (8) is a sensor-design or experiment certificate; it is not a new general set-membership method.

**Different targets.**

- PCC waveform: on a known feasible set P, noiseless identifiability is ker(H) intersect (P-P)={0}. Full column rank is sufficient for arbitrary unrestricted histories but not necessary on restricted models
- Source bus: with one active source at bus b, y_t=h_b s_t. For an unknown nonzero real waveform, two buses alias exactly when their columns are nonzero scalar multiples with an admissible waveform rescaling. If waveforms are constrained positive, use positive multiples. Known fixed waveform amplitude changes that condition. Rank deficiency need not prevent single-source bus discrimination
- Internal compute waveform: even exact p does not determine d unless the storage trajectory or its power is known. The relation d_t=p_t-(e_{t+1}-e_t)/δ exposes the remaining degree of freedom
- AI cause: two different software/workload causes that realize the same d, e, and p are indistinguishable to every grid-only H. An AI interpretation needs an independently justified workload model, exclusions, interventions, or internal telemetry; a power label alone does not supply that proof

Unknown measurement mapping adds a nuisance parameter: compare H_0p_0 with H_1p_1 for H_j in the allowed mapping family. When physically admissible, (H,p) and (HQ^{-1},Qp) have the same noiseless observation for invertible Q. Permutation/scaling examples expose source-label or amplitude ambiguity. This gauge argument is only valid for transformations that remain in the physical mapping/model family; arbitrary Q must not be assumed for a constrained network.

Known labeled calibration inputs spanning the relevant source subspace can identify a static mapping: Y=HP with full-row-rank P gives H=YP^T(PP^T)^{-1}. Noise and unmodeled loads require a corresponding calibration-error bound. This is standard linear calibration, not a new identification theorem.

## 8. Informative experiments and internal sensor certificates

At exact common recovery endpoints, conservation removes storage from source energy:

  δ sum_t p_t = δ sum_t d_t + e_T-e_0.

If the known start/end states are equal, integrated PCC energy equals task energy. Candidate workloads with different total energies cannot have identical source traces across such an experiment. Zero-mean alternatives survive this test; a recovery deadline placed where their cumulative energies differ, and individually feasible for both alternatives, can break that particular ambiguity.

For endpoint intervals of widths w_0,w_T, pairwise uncertainty in the boundary correction is at most w_0+w_T. With direct PCC measurement noise bounded by ε per time unit and duration Tδ, an integrated task-energy gap exceeding

  w_0+w_T+2εTδ

cannot be hidden. If the actual initial state is common in the two worlds, omit w_0; if both endpoints are common exact states, both width terms vanish. This is a sufficient robust integrated-energy test, not a claim that every smaller gap is globally indistinguishable.

A colocated storage-power sensor u gives d=p-u directly. With absolute sensor errors ε_p and ε_u, the resulting pointwise error is at most ε_p+ε_u. Alternatively measuring consecutive stored energies gives d_t=p_t-(e_{t+1}-e_t)/δ, with bound ε_p+(ε_{e,t+1}+ε_{e,t})/δ; fast differencing amplifies state-sensor noise. Every significant local storage/generation path must be included. Even perfect electrical accounting does not establish an AI semantic cause.

A network sensor design can maximize the minimum separation in (8) over permitted sensor rows or experiments, then require a positive certified margin over noise/model uncertainty. The certificate must be computed for the stated candidate sets, including buffer freedom, rather than for a classifier's preferred point estimates alone.

## 9. Stable dynamic grid: sufficient DC-energy horizon

Consider a known stable linear model

  xdot=A x+B_u p, y=C_y x+D p+n,

where A is invertible and Hurwitz. Direct integration yields

  integral_0^T y = G integral_0^T p
                  +C_y A^{-1}(x(T)-x(0))+integral_0^T n,
  G=D-C_y A^{-1}B_u.                         (9)

For ideal storage p=d+edot,

  integral y=G integral d+G(e(T)-e(0))
             +C_y A^{-1}(x(T)-x(0))+integral n. (10)

**Proof.** Integrate the state equation to obtain integral x=A^{-1}(x(T)-x(0))-A^{-1}B_u integral p, then substitute into the integrated output equation. QED.

For two worlds with common x(0), choose an output discriminant w. Suppose their mapped task-energy separation is at least γT-K_0, their pairwise storage-boundary contribution has magnitude at most K_e, their pairwise network-transient term at most K_x, and each noise satisfies |w^Tn(t)|<=ε_w. Identical output histories are impossible whenever

  (γ-2ε_w)T > K_0+K_e+K_x.                  (11)

Known common exact recovery removes K_e at those deadlines. With common initial storage and capacities B_i, one may take K_e=sum_i |(w^TG)_i|B_i; independent unknown initial states can double this bound. A uniform K_x requires an explicit state/input bound. For example, ||exp(At)||<=M exp(-λt), ||p^j||<=P, common x(0), gives

  ||x^1(T)-x^0(T)|| <= 2M||B_u||P/λ,

which yields a finite transient bound after multiplication by w^TC_yA^{-1}.

This is a sufficient horizon, not a general “if and only if the DC gap exceeds noise” rule. A zero or small DC gap can still be identifiable through transient or AC signatures. A zero-mean cyclic workload difference is simply not forced to reveal itself by the DC conservation argument.

## 10. Causality and physical transfer checklist

Existence of a complete common trace may use future task information. It does not prove a robust online strategy against all as-yet-unrevealed loads. A common predetermined schedule plus compensation u=p-d is causal only under the declared current-load-before-action interface. If a deterministic actuator has identical information in two worlds at its decision time and must choose u before the first differing load is revealed, its actions agree; the first different load then makes p=d+u different. A hidden low-level compensator must not be smuggled into the model.

Finite slew, actuation delay, switching transients, and source-meter bandwidth can expose onsets even when slot-boundary energy equations are exact. The positive step-task contract is an abstract sampled/held model. A smooth task and converter co-ramp can be considered when the selected task is known before its controlled onset, but that requires fresh integration and a verified timing/slew contract; the discrete numerical capacities do not automatically transfer.

Other required distinctions: known versus unknown initial state; common physical state versus independently chosen nuisance states; exact versus interval recovery; fixed observed trace versus existence of a common trace; universal hidden class versus an indistinguishable pair; fixed versus uncertain H; independent nuisance noise versus shared known noise; deterministic same-trace privacy versus distributional privacy.
