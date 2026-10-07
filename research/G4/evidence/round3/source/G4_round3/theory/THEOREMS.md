# Workload-conditioned lossy hiding: theory under review

## Contract
A block has N equal slots δ, positive task powers L<H, and a finite nonempty set S of admissible binary words with the same number k of high tasks. A DAG's linear extensions induce S, but S may also be a more general specified within-block contract. Successive words are independently selectable from S. The public trace p_{b,t} is fixed independently of private order and constrained to a fixed compact polytope P subset [L,H]^N (e.g. slot/ramp restrictions). Compensation knows the current task before acting. Stored energy evolves e'=e+δφ(p-d), φ(u)=η_c u for u≥0 and u/η_d for u<0; 0<η_c,η_d≤1, strict loss η_cη_d<1. No self-discharge, disposal, simultaneous cycling, hidden generation, or forced state reset. Initial e0 is common and free within [0,B]. All boundaries must remain in [0,B]. Slot-constant implementation is primary; two-level in-slot means apply only when p(t) stays inside [L,H], and extra waveform limits are checked separately.

For σ∈S define affine prefix functions g_{σ,j}(p)=δ∑_{t≤j}φ(p_t-d_{σ_t}) including j=0, and residual r_σ=g_{σ,N}. Affinity holds because all low tasks charge and all high tasks discharge on the given p domain. Define B_S* as the minimum B of the finite LP over p∈P,z,B:

r_σ(p)=0 for all σ; 0≤z+g_{σ,j}(p)≤B for all σ,j.

If infeasible set B_S*=∞. This is a standard robust scenario LP, not a new optimization algorithm.

## T1. Exact infinite-horizon reduction for every admissible word family
Suppose one infinite common schedule p_b∈P and common e0 works for every independent history. Put a_b=minσ r_σ(p_b), b_b=maxσ r_σ(p_b), W_m=∑_{b≤m}(b_b-a_b), W∞=lim W_m. Then

B ≥ B_S* + W∞.

Consequently the minimum capacity over all (even nonperiodic) infinite common schedules equals B_S*, attained by repeating an optimal exact-reset block. This is sharp for the optimum W∞=0; equality for each prescribed positive W∞ is not claimed.

Proof. At the start of block b, the exact reachable energy hull is [l_b,u_b]=[e0+∑_{h<b}a_h,e0+∑_{h<b}b_h]. Endpoints are achievable because block choices are independent. Thus u_b-l_b=W_{b-1}, 0≤l_b≤u_b≤B, and for all σ,j,
0≤l_b+g_{σ,j}(p_b)≤B-W_{b-1}.
For the upper inequality the actual upper endpoint u_b and the same current word can be combined. Average these inequalities through b=1,...,M. Affinity gives
0≤lbar_M+g_{σ,j}(pbar_M)≤B-(1/M)∑_{b≤M}W_{b-1}.
Compactness gives a subsequence (pbar_M,lbar_M)→(p*,z*)∈P×[0,B]. W is increasing and bounded by B, so its Cesàro mean tends to W∞. For any fixed σ, the history that executes this σ in every block is allowed, and e0+∑_{b≤M}r_σ(p_b) stays in [0,B]. Therefore r_σ(pbar_M)=M^{-1}∑r_σ(p_b)→0, hence r_σ(p*)=0. The limit is a feasible one-block LP point of capacity B-W∞. The lower bound follows. Conversely any finite-LP solution repeats with exact physical recovery, so is feasible indefinitely. Compactness of feasible sublevel sets ensures an optimum whenever finite. QED.

This proof does not need full permutations, connected swaps, stationarity, or per-block recovery imposed on the original schedule. It does need independent block choices, affine two-level increments, bounded/common initial state, and a fixed convex public action set. The theorem extends to a compact convex P, but the finite problem is then a convex program rather than necessarily an LP. It is not asserted for multilevel kink-crossing output averages or state-dependent efficiency.

## T2. DAG slot-swap graph and exact endpoint-invariance
Let tasks have labels H/L and precedence DAG D. Make a graph on slot positions 1,...,N, with an edge (t,t+1) iff some labeled linear extension has incomparable opposite-label tasks in those positions. For p∈[L,H]^N and strict loss, endpoint residual r_σ(p) is equal for every linear extension iff p_t=p_{t+1} on every edge. Thus p is constant on connected components of this path subgraph; one additional residual-zero equality gives exact recovery.

Proof. Swapping adjacent incomparable high/low tasks changes the endpoint by ±δκ(p_t-p_{t+1}), κ=1/η_d−η_c>0. Necessity follows. Any two linear extensions can be joined by adjacent swaps of incomparable tasks (classical linear-extension graph connectivity, elementary induction by moving a selected maximal task to the end). Same-label swaps never change costs; opposite-label swaps are exactly graph edges. Edge equalities therefore make every residual equal. QED.

Do not confuse connectivity of the graph of labeled linear extensions (always true) with connectivity of this slot-position graph (may fail).

## T3. Connected slot graph gives an explicit sharp DAG capacity
If T2's slot graph is connected and P contains constant q, all exact-reset public outputs are p_t=q, where
q=[kH+η_cη_d(N−k)L]/[k+η_cη_d(N−k)].
Let c=δη_c(q−L), h=δ(H−q)/η_d. For prefix length t let a_t and b_t be respectively the minimum and maximum number of high tasks in any feasible DAG prefix (a_0=b_0=0). Then
B_D* = max_t[c t−(c+h)a_t] − min_t[c t−(c+h)b_t].
The common optimum e0 is minus the latter minimum. By T1 this is also the optimum among all infinite nonperiodic schedules. Full permutations allow all low tasks first and all high tasks first, reducing this to 2Q. Restricted precedence can lower it strictly even when the slot graph remains connected. This is task-prefix geometry, not an inference classifier.

## T4. Correlated history boundary through finite automata
Fix a public repeated block p. A finite strongly connected directed graph has a known starting node s0; each edge e carries a complete task word σ(e). Private workload histories are every directed path from s0. Put r_e=r_{σ(e)}(p). A finite buffer exists for all infinite histories iff every directed cycle has total residual zero. Equivalently there is a node potential v with r_e=v(target)−v(source). For a given p satisfying this condition, the exact minimum capacity is
max_{e,j}[v(source(e))+g_{σ(e),j}(p)] − min_{e,j}[v(source(e))+g_{σ(e),j}(p)],
including the initial node value. The initial energy shifts the minimum to zero.

Proof. A nonzero cycle is reachable and repeatable and drives state unbounded. If all directed cycles sum to zero, two directed paths from s0 to any node have equal residual because a return path to s0 exists; concatenate each with that same return path and compare closed-walk sums. Their common value defines v relative to v(s0)=0. Edge increments telescope. Every edge is reachable, so the displayed extrema are attained; selecting initial state minus their minimum proves sufficiency. QED.

This is a classical weighted-graph conservation/coboundary fact applied to workload energy, not a new graph theorem. It invalidates independent width accumulation for correlated histories; nonzero edge residuals can cancel on every admissible cycle. Multiple hidden initial nodes require a separate initial-state-set treatment and are not covered by the formula as stated.

## T5. Self-discharge changes the accumulation law
For e_{t+1}=ρe_t+δφ(p_t−d_t), 0<ρ<1, fixed public repeated p, and independent words σ, write a=ρ^N and g^ρ_{σ,j}=δ∑_{t≤j}ρ^{j−t}φ(p_t−d_{σ_t}). At block endpoints rσ=g^ρ_{σ,N} and
l_{b+1}=a l_b+minσ rσ, u_{b+1}=a u_b+maxσ rσ,
W_{b+1}=aW_b+range(rσ).
Thus W∞=range(rσ)/(1−a), rather than a sum that must vanish. The stationary endpoint hull is [l*,u*]=[min r/(1−a), max r/(1−a)]. A feasible common initial state exists for all time iff
0≤ρ^j l*+minσ g^ρ_{σ,j} and ρ^j u*+maxσ g^ρ_{σ,j}≤B for all j=0,...,N.
Necessity follows by limits from any finite initial state; sufficiency follows by choosing e0∈[l*,u*]. This is classical scalar invariant-set reachability. On the two-level p domain, its capacity optimum is the exact LP using variables l,u,p,B with l≤u, ρ^N l+rσ≥l, ρ^N u+rσ≤u and all prefix box inequalities. These inequalities admit the exact stationary hull, so minimizing over invariant intervals is not conservative here.

A self-discharge scalar model is not a validated battery model and does not imply a beneficial net energy trade-off. Energy lost to leakage must be supplied at the PCC.

## T6. A sharp leakage threshold for all-permutation endpoint invariance
For 1≤k≤N−1 high tasks, full permutations, equal slots, strict converter loss, and discrete retention ρ∈(0,1), order-independent endpoint increments occur exactly when
ρ^(N−t) F(p_t)=C for every t,
where F(x)=φ(x−L)−φ(x−H)=H/η_d−η_c L−κx on [L,H]. Such an output in [L,H]^N exists iff
η_cη_d ≤ ρ^(N−1).

Proof. For any two positions a swap of one high and one low is allowed. Comparing weighted endpoint sums forces equality of the displayed weighted F values; conversely that equality makes the sum independent of the high-position subset. Since F maps [L,H] bijectively onto [η_c(H−L),(H−L)/η_d], the possible common C values are the intersection of intervals [ρ^(N−t)η_c(H−L),ρ^(N−t)(H−L)/η_d]. This intersection is [η_c(H−L),ρ^(N−1)(H−L)/η_d], nonempty precisely at the stated threshold. QED.

This is only endpoint-invariance feasibility, not sufficient battery capacity, nonnegative periodic e0, rate feasibility, or recovery to a prescribed initial state. It explains the geometric nonflat outputs in the leaky LP: p_t=[H/η_d−η_c L−Cρ^(t−N)]/κ. If the inequality fails, positive endpoint width is unavoidable, but stable contraction can still permit bounded universal hiding. This threshold is a scalar weighted-swap corollary, not a new self-discharge model.

## Continuous-time and measurement boundary
T5–T6 use discrete retained-state dynamics with a net slot increment deposited at the boundary. They do not claim a continuous physical path certificate. For ė=−λe+φ(p(t)−d), the exact increment is an exponentially weighted integral; ordinary means are insufficient, and low-demand-slot SOC need not be monotone under variable p. Subslot extrema need independent validation. At ρ=1 with two-level tasks and p(t)∈[L,H], the earlier monotone slot-mean reduction is valid.

All primary theorems concern equality of the entire ideal PCC trace. Passing an identical p through the same workload-independent deterministic or stochastic observation channel preserves indistinguishability. With bounded additive error ε, two distinct sampled PCC traces can have overlapping observation sets only when their coordinatewise differences are ≤2ε; this is a specified-pair consistency fact, not an accuracy guarantee or universal source-identification horizon. Hiding task labels is distinct from hiding a nonzero forcing at the PCC. An exactly flat common PCC removes the task-induced forcing there.

## T1a. Finite horizons converge to the same static capacity
Let B_K be the minimum capacity for K independently selectable blocks, allowing a different public p_b∈P in every block and imposing no terminal recovery. Then B_K is nondecreasing, B_K≤B_S*, and B_K→B_S* (including divergence when B_S*=∞).

Proof. Truncation proves monotonicity; repetition of a static exact-reset solution proves the upper bound. If a bounded subsequence of finite-horizon feasible designs has capacities tending to b<B_S*, use the same averaged start-hull and averaged p construction as T1. For each word σ, its repeated K-block history gives |rσ(pbar_K)|≤B_K/K. Discard the nonnegative mean width in the prefix capacity inequalities. Compactness then gives a one-block exact-reset point of capacity at most b, a contradiction. QED.

No finite-K rate follows from this compactness proof. The saved 1–64-block optimizations illustrate this limit and do not replace the proof or prove a universal exponential convergence rate.

## T5a. The leaky invariant LP also covers all nonstationary common outputs
Under the same finite two-level independent word family, fixed compact polytope P⊂[L,H]^N, and fixed 0<ρ<1, the minimum capacity among all infinite common schedules p_b∈P equals the stationary invariant-interval LP of T5 (with p∈P). Thus restricting to one repeated public block loses no design-capacity optimality in this specific affine robust contract.

Proof. Let [l_b,u_b] be the exact reachable endpoint hull before block b, a=ρ^N, and rσ(p)=g^ρ_{σ,N}(p). An arbitrary feasible infinite schedule satisfies
l_(b+1)≤a l_b+rσ(p_b), u_(b+1)≥a u_b+rσ(p_b)
for every σ; all prefixes satisfy 0≤ρ^j l_b+g^ρ_{σ,j}(p_b) and ρ^j u_b+g^ρ_{σ,j}(p_b)≤B. Average through b=1,...,M. Since all l_b,u_b are in [0,B], telescoping differences divided by M tend to zero. A compact subsequence of (pbar,lbar,ubar) converges to (p*,l*,u*)∈P×[0,B]^2 with l*≤u*. Affinity then gives (1−a)l*≤rσ(p*) and (1−a)u*≥rσ(p*), along with every prefix inequality. This is a stationary robust invariant interval at capacity B. Conversely, one common initial state in any feasible interval and repeated p* remains feasible under all independent words. QED.

The chosen initial state may differ between designs; a prescribed initial state or additional initial-entry transient can invalidate the equality without an entry argument. The result is classical occupation/averaging reasoning specialized to an affine privacy contract, not a new generic invariant-set method.
