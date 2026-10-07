# G6 round 3: finite information, robust geometry, and enforceable sign contracts

This note separates exact mathematical results from novelty and engineering claims. The support series is classical (Duda, equations 14–15). None of the results below is a new general admission algorithm. All parameters are mathematical contract parameters, not arithmetic classes estimated from floating modal eigenvalues.

## 1. Model and quantifiers

Let 0<r<1, u_k(theta)=(cos(k theta),-sin(k theta)), and

F_theta(a) = sum_{k>=0} r^k |u_k(theta) dot a|.

The scalar output of x_(n+1)=r R_theta x_n+s_n a from x_0=0 has all-time worst magnitude F_theta(a), with independently selectable shared signs s_n∈{−1,1}. a is fixed throughout a trajectory. One unknown theta belongs to a compact interval I and stays fixed across all ports and times. Its exact robust support is Phi_I(a)=sup_(theta∈I) F_theta(a). The maximization is outside the whole support, not inside each lag. Dynamic optional amplitudes use H_theta(a)=[F_theta(a)+F_theta(a1,0)+F_theta(0,a2)]/2 for a≥0; this is a different action contract.

## T1. Finite-angle uncertainty has an explicit, arithmetic-free certificate

For arbitrary theta, eta and a∈R²,

|F_theta(a)−F_eta(a)| ≤ ||a||₂ |theta−eta| r/(1−r)².

For a partition theta_0<...<theta_M of I with maximum gap h and a prefix N, define

Q_N(a)=max_j sum_(k=0)^(N−1) r^k |u_k(theta_j) dot a|,
C_(2,N)=sum_(k=0)^(N−1) k²r^k,
tau_N=r^N/(1−r).

Then

Q_N(a) ≤ Phi_I(a) ≤ Q_N(a)+||a||₂ [C_(2,N) h²/8+tau_N].

The elementary first-order comparator is Q_N(a)+||a||₂ [r h/(2(1−r)²)+tau_N]. The smaller of these two valid errors can be used. A simpler closed bound replaces C_(2,N) by r(1+r)/(1−r)³. These statements hold at every kink, including intervals containing many kinks. They require no rational/irrational classification, curvature fitting, sampling probability, or differentiability assumption on F.

If a≥0, replacing ||a||₂ by a1+a2 gives a direct piecewise-linear sufficient admission condition. Retaining ||a||₂ gives a conic expression. If r is also a fixed unknown in [r_lo,r_hi] independently of theta, monotonicity of each nonnegative summand makes r_hi exact worst-case. This endpoint assertion is specific to the contraction-rotation family and does not hold for arbitrary uncertain state matrices.

**Proof.** The vector u_k has derivative norm k. Absolute value is 1-Lipschitz, so summation gives the first inequality. For the second-order claim, write each term as r^k ||a||₂ |cos(k theta+alpha)|. In distributions its second derivative is −k² times the term plus nonnegative point masses at zeros. Consequently f_N(theta)+(C_(2,N)||a||₂/2)theta² is convex. The defining chord inequality for this convex function yields

f_N(theta) ≤ linear_interpolation(f_N(l),f_N(u)) + C_(2,N)||a||₂ (theta−l)(u−theta)/2
             ≤ max(f_N(l),f_N(u))+C_(2,N)||a||₂ h²/8.

The tail is between zero and tau_N||a||₂, uniformly in theta. Taking the maximum over cells proves the result. This is a standard semiconvex interpolation argument applied to the classical support series. QED.

**Extension to H.** Apply T1 to its three component F functions. Replace ||a||₂ in its error by (||a||₂+a1+a2)/2. The pointwise maximum over theta stays outside the sum defining H. Summing three separately optimized parameter supports would instead be an information relaxation.

**Decision meaning.** At threshold b, Q_N(a)>b is a finite-parameter/finite-word exclusion. Q_N(a)+error≤b is sufficient for the fixed-parameter robust LTI contract. The in-between case is unresolved at that precision. A grid point alone never proves the robust upper claim.

**What finite observations cannot identify.** Every open theta interval contains rational and irrational multiples of pi. Therefore a finite-width parameter report cannot decide exact polygonality or an infinite Diophantine class. T1 bounds the finite-output consequence nonetheless. At an uncertainty width delta, the output-gauge variation is at most 2delta r/(1−r)²||a||₂. This is an upper bound, not a lower bound on any estimator's error and not evidence that every uncertainty interval realizes the bound.

## T2. Arbitrarily small fixed orientation uncertainty can replace the logarithmic arc by a circular arc

Let F be any continuous positive homogeneous gauge on R², positive on nonzero vectors, and let M=max_(||v||₂=1) F(v), attained at angle alpha*. For a fixed orientation interval J=[phi_lo,phi_hi], define

G_J(a)=sup_(phi∈J) F(R_phi a).

Whenever alpha*−arg(a) belongs to J modulo 2pi,

G_J(a)=M||a||₂.

Thus if the alignment direction interval [alpha*−phi_hi,alpha*−phi_lo] has an intersection with the interior capacity cone of positive length, the robust unit boundary has an exact circular arc of radius 1/M. It is enough to choose the center of a nonzero interval so that alpha* aligns with any interior ray. It is false that every arbitrary interval center creates such an arc in every pre-fixed slope range.

**Proof.** Homogeneity bounds every F(R_phi a) by M||a||₂. The alignable maximizing direction attains this bound. QED.

This uncertainty is one fixed common port-mixing or output orientation, e.g. B=R_phi in the same rotating system. It is not uncertainty in theta, not independent per-port orientations, and not a phi that can switch each block. The mathematical construction does not establish that any measured grid has this uncertainty set.

### T2a. Exact finite-resolution piece bounds on the exposed circular sector

Choose any nontrivial closed slope interval [l,u] inside that alignment sector. Here the gauge is f(t)=M sqrt(1+t²). Let D=u−l, kappa=min_[l,u] M/(1+t²)^(3/2)>0, and K=max_[l,u] M/(1+t²)^(3/2). Let N(epsilon) count affine pieces in a continuous piecewise-affine g with uniform gauge error ≤epsilon. Then

N(epsilon) ≥ D sqrt(kappa)/(4 sqrt(epsilon)),
N_safe(epsilon) ≤ max(1,ceil(D sqrt(K/(8epsilon)))),

where the upper construction is convex and g≥f on [l,u]. Consequently both unconstrained and locally safe direct polygon/gauge representation need Theta(epsilon^(−1/2)) pieces on this sector. This is the classical quadratic interpolation/polygon approximation order, not a new complexity exponent. It is not a bound on arbitrary computation or lifted formulations: G=M||a||₂ on this sector has a constant-size SOC description.

**Proof.** An m-piece g has one affine subinterval of length at least D/m. Strong convexity gives f(left)+f(right)−2f(mid)≥kappa (D/m)²/4; approximation at these three points bounds that difference by 4epsilon. This proves the lower bound. Equal-length chord interpolation has error between zero and K(D/m)²/8 by the standard second-derivative remainder, proves the upper bound, and has nondecreasing slopes. QED.

**Crossover and noncommuting limits.** For an orientation width 2delta centered to expose a sector around a fixed interior ray, D is Theta(delta) as delta→0. The circular-sector lower bound has scale delta/sqrt(epsilon), so many pieces are forced on this sector only for epsilon small relative to delta². At delta=0 and an irrational theta of finite exponential type, the historical exact-angle logarithmic theorem remains valid. For every fixed delta>0 exposing a sector, T2a gives a polynomial lower bound as epsilon→0. These statements are compatible; the constants and the accuracy regime depend on delta. No claim that tiny uncertainty causes a large practical error at a coarse tolerance is made.

## 3. Actual workload contracts: imperfect block-sign agreement

For two fixed-amplitude ports, retain the complete templates q_i with zero area in each block. Let port signs be s_k and s_k(−1)^(z_k), z_k∈{0,1}. z_k=1 records a mismatch. Shared s_k remains arbitrary; one mismatch may be selected without changing either port's full-block energy or its affine-law work. Let b_j1,b_j2 be a fixed output/phase's current and past block coefficients, p_j=a1 b_j1, q_j=a2 b_j2. Conditional on a binary mismatch word z, optimization over the shared signs gives exactly

sum_j w_j(z_j), where w_j(0)=|p_j+q_j| and w_j(1)=|p_j−q_j|.

The finite-window (L,B) contract requires no more than B mismatches in any L successive blocks. Short startup windows are bounded by the same B, equivalently pad with zeros. This permits an online scheduler/monitor with L−1 bits of history. It is an explicit coordination guarantee; no cost-free enforcement, real scheduling feasibility, or compute calibration is assumed.

## T3. Finite-window support is ordinary weighted-language optimization

For a finite history N, maximize the displayed sum over all binary words satisfying the (L,B) contract. An exact DP stores the last L−1 bits, appends 0 or 1 when popcount(history)+z≤B, and adds w_j(z). Initialize with all-zero prehistory. The resulting terminal maximum is the exact finite-prefix support.

The language is closed under time reversal and zero padding. Each reward is nonnegative, so extending a maximizing history by zero mismatch cannot decrease its value. The infinite-history support is the monotone limit. A bound on the omitted sum of |p_j|+|q_j| gives a valid tail, and a bound on the independent-port sum of time derivatives gives a valid phase interpolation error for every (L,B).

B=0 recovers committed common signs; B=L recovers independent signs. Nested B gives nested domains. Small finite word enumeration or a binary integer program must equal the DP under identical information. This is a direct specialization of classical support functions and finite automata/weakly-hard scheduling; no new solver is claimed.

**Proof.** For fixed z each shared sign independently maximizes its scalar coefficient. The DP enumerates every admissible binary word exactly through its suffix state. Reversal preserves all window counts. Appending/prepending zero keeps feasibility, and adds a nonnegative optimized reward. Absolute triangle and derivative inequalities give the envelope bounds. QED.

### T3a. A stronger same-information baseline is an ordinary integral LP / interval flow

Put d_j=w_j(1)−w_j(0). For a finite N-word, the mismatch optimization equals the constant sum_j w_j(0) plus

max d^T z subject to 0≤z≤1 and sum_(j in each length-L window) z_j≤B,

including the zero-padded short windows. This LP has an integral optimum: the sliding-window incidence matrix has consecutive ones in each column, is totally unimodular, and adjoining identity rows preserves integrality for integer B. Thus a large suffix-state automaton is not needed for this special cardinal-window problem. Standard LP, not mixed-integer search, suffices.

Equivalently create interval jobs [j,j+L) of value d_j and require at most B overlaps. On time vertices 0,...,N−1+L, use consecutive time arcs of capacity B and zero cost, and job arcs j→j+L of capacity 1 and cost −d_j; send B units from first to last time vertex. Integral min-cost flow picks the compatible mismatch intervals. Negative-value jobs need not be chosen. This is classical weighted interval scheduling with B machines, not a new optimizer.

**Reduction proof.** The active intervals at integer time t are exactly mismatch indices j∈[t−L+1,t], so overlap constraints are the same padded window counts. Feasible flows choose at most B overlapping intervals because every time cut carries only B units. Conversely any set with maximum overlap B can be colored into B nonoverlapping interval chains, by assigning each interval to a free chain in chronological order; these chains give B flow paths. Cost is minus total chosen value. Integral capacities give an integral optimum. This constructive interval argument also supplies an independent reason for the LP integrality. QED.

The current experiments compare DP to this same-information LP on 84 selected independent rows, plus exhaustive small words. The LP therefore receives every correlation/window fact available to the candidate; differences between window sizes are contract comparisons, never algorithm wins.

## T4. An average-only mismatch rate provides no infinite-horizon robust improvement

If the only mismatch restriction is limsup_(n→infinity) (sum_(k<n)z_k)/n≤rho with rho≥0, then the all-time worst output from zero is exactly the independent-sign all-time support. This holds even for rho=0. A weaker long-run expected fraction condition also cannot exclude the deterministic finite-burst counterexample.

**Proof.** The average-only family is a subset of arbitrary independent signs, giving the upper bound. Every finite mismatch word is extendable by all zeros and then has asymptotic rate zero. Every independent-sign finite-horizon maximizing word is therefore feasible in the average-only family. Taking the supremum over finite horizons gives the reverse inequality. QED.

This is about an all-time worst-case guarantee. It does not say mean rate is useless for expected loss, finite-mission probability, stationary assumptions, or a prefix bound sum_(k<n)z_k≤rho n+burst. A token-bucket/prefix burst budget is a stronger contract and can have nontrivial support. Full burst/window restrictions, not an average label alone, carry the safety information.

## 4. Compute-load and scientific scope

These statements concern a port waveform contract. Equal incremental energy only implies equal executed work under the stated affine map work_rate_i=wbar_i+kappa_i deltaP_i with nonnegative rate. A real computational graph must provide permitted phase order, slack/latency, actual PCC power tracking, common-block synchronization and mismatch enforcement. Two arbitrary general loads with the same waveform contract obey every theorem too; nothing in the proof is AI-specific.

The positive Kundur source has actual 50MW compute baselines at each port but nominal voltages about .945044/.948743pu; it is a frequency-only conditional illustration, not voltage-qualified hosting. The WECC transfer source retains zero supplemental compute baselines, and its old dynamic-optional nonlinear inner word exceeds .05Hz at about .05310Hz. No new all-family nonlinear guarantee, device calibration or average-demand hosting gain follows from this round. New numerical amplitudes must retain these caveats.

## T5. Same-job complementary plans realize the templates without an affine power–work law

This is a post-protocol analytical extension, clearly separate from the frozen synthetic uncertainty experiment. At each port, one block releases four labeled nonpreemptive jobs H1,H2,L1,L2. Each needs exactly one slot of length T/4. Each H job has a declared constant PCC demand P0+a and each L job P0−a, where 0≤a≤P0. All four have deadline T. Work units belong to job identities and may be arbitrary positive numbers; they are not calculated from electrical power.

For port 1, choose macroplans [H1,H2,L1,L2] and [L1,L2,H1,H2]. Both obey the two-chain DAG H1→H2 and L1→L2 and produce q1=(1,1,−1,−1) and −q1. For port 2, choose [H1,L1,L2,H2] and [L1,H1,H2,L2]. Both obey the DAG with edges H1→H2, L1→L2, H1→L2 and L1→H2, producing q2=(1,−1,−1,1) and −q2. With common block release/deadline, every allowed sequence of macroplan choices completes exactly the same labeled job set, the same total job work, the same makespan T, and the same electrical energy P0 T at each port. Selecting shared/opposite macroplan signs implements every mismatch word in T3.

**Proof.** Each listed order is topological for its stated DAG. Every order executes all four jobs once in four identical slots. Each uses two H and two L slots; their incremental power integrals cancel. No speed–power substitution or state reset occurs. QED.

**Precise feasibility characterization.** Given any two complete job orders, both are legal for a DAG iff every precedence edge respects both orders. This is simply their intersection partial order. It is a useful validation condition, not a novel scheduling theorem. For instance adding H2→L1 to port 1 keeps its positive plan feasible but excludes its negative plan. Equal work/energy does not repair that exclusion. A scheduler must also preserve any finer individual deadlines or release constraints, which have deliberately not been asserted here.

This construction establishes a nonempty class of explicit job graphs for which the waveform contract is coherent, rather than generic affine work bookkeeping alone. It does not establish that actual GPU jobs have the specified rectangular PCC traces, identical slot lengths, repeatable power, zero switching cost or two admissible macroplans. Changing amplitude a changes the declared job catalog; the amplitude sweep is not a demonstrated scaling of the same real jobs. The graphs contain actual job identities in the model but are synthetic task catalogs, not empirical compute validation.
