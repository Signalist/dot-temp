# Loss, positive recovery tolerance, and hidden task order

Status: proved in the declared discrete-time model. These are identifiability and robust storage-feasibility statements, not an estimator, source-localization rate claim, or empirical novelty claim. Standard assignment-swap, robust-envelope, interval-hull, and LP machinery is used openly. Literature novelty requires a separate review.

## 1. Contract, timing, and meanings

A block has N >= 2 equal-duration slots of length δ > 0. A known multiset of strictly positive task powers d_1,...,d_N is executed completely, exactly once per block, in an arbitrary permutation π. Tasks are nonconstant: a = min d_i < b = max d_i. Each block's permutation may be chosen independently, including adversarially. Thus every world performs positive compute in every slot and completes the same declared multiset and work/energy contract. “Meaningful compute” beyond this electrical/work declaration, and the semantic label “AI,” require additional evidence; they do not follow from power alone.

The common public PCC trace p_{ℓ,t} is fixed independently of the hidden permutations. It may depend on public block and slot indices and a publicly chosen horizon, but not on private task order or SOC in a way that changes the observed trace. Deterministic, exact same-trace hiding is the privacy notion. Equality only in distribution is a different problem.

Storage has no leakage, auxiliary dissipation, simultaneous charge/discharge, or other energy channel. Its state is

  e_{next} = e + δ φ(p-d),
  φ(u) = η_c u for u >= 0, and u/η_d for u < 0,
  0 < η_c,η_d <= 1.

The stored-energy capacity is B, with 0 <= e <= B. Let α=η_cη_d and κ=1/η_d-η_c. Strict round-trip loss means α<1, equivalently κ>0. PCC-side charging/discharging power and stored-energy rate are different quantities.

The starting energy E0 is common and known. A recovery obligation of tolerance τ is |e_{ℓ,N}-E0|<=τ at every declared checkpoint; it is not a reset operation. States propagate continuously from one block to the next. Recovery to E0 is exact when τ=0.

Implementation interface: the current slot's task power is measured or announced before the compensating action and is held during that slot. The converter applies u=p-d. The PCC schedule is predetermined and the compensation is causal, memoryless in the current load. If the actuator must choose u before learning d, or finite delays/ramp/transients are visible to the observer, this implementation and its same-trace assertion need a new model. No claim about an actual converter's bandwidth is made.

## 2. Exact-recovery rigidity for a single block

**Theorem 1 (lossy permutation rigidity).** Suppose α<1. A single deterministic slot-constant PCC trace p_1,...,p_N achieves e_N=E0 for every permutation of a nonconstant task multiset if and only if

  p_1=...=p_N=q,
  sum_i φ(q-d_i)=0.

The root q is unique, lies strictly between a and b, and is strictly above the arithmetic mean of the task powers. This theorem concerns endpoint recovery; capacity/rates must additionally be checked.

**Proof.** Exact recovery is sum_t φ(p_t-d_{π(t)})=0 for all π. Pick any two different slots s,t and put a designated minimum task a and maximum task b there. Complete the remaining assignment arbitrarily. Swapping only those two tasks gives

  F(p_s)=F(p_t), where F(x)=φ(x-a)-φ(x-b).

For x<=a, F(x)=(b-a)/η_d. For a<x<b,

  F(x)=(b-a)/η_d - κ(x-a),

and for x>=b, F(x)=η_c(b-a). Hence F is constant on each exterior half-line and strictly decreasing on (a,b). Equivalently,

  F(x)=(b-a)/η_d - κ(clip(x,a,b)-a).

Equality for every pair s,t implies precisely one of: all p_t<=a; all p_t>=b; or every p_t equals one common q in (a,b). The first case makes every increment nonpositive, with at least one strictly negative increment in every complete block because a task b>a occurs. The second makes every increment nonnegative with at least one strictly positive. Neither can recover exactly. Thus all p_t=q in the interior.

Conversely, a constant q makes the endpoint sum independent of order. The function sum_i φ(q-d_i) is continuous and strictly increasing; it is negative at a and positive at b, so it has a unique root in (a,b). Write P=sum_i(q-d_i)_+ and M=sum_i(d_i-q)_+. Recovery gives αP=M. Since the multiset is nonconstant and q is interior, P>0. Therefore Nq-sum_i d_i=P-M=(1-α)P>0. QED.

**Scope that matters.** Equal slot durations are essential to the pair-swap equality as written. With unequal durations, it becomes δ_s F(p_s)=δ_t F(p_t), allowing other structures. Leakage introduces time weights. Controllable dissipation or simultaneous charging/discharging changes φ. Approximate recovery changes zero equalities into inequalities. All are genuine model changes, not technicalities.

**Theorem 2 (sharp exact-reset capacity and rates).** For the constant q above, put

  Q = δ sum_i [φ(q-d_i)]_+
    = -δ sum_i [φ(q-d_i)]_-.

Every permutation fits a buffer of capacity B from common initial E0 if and only if E0>=Q and B-E0>=Q. Thus the minimum capacity over the initial state is B*=2Q, attained at E0=Q.

The exact PCC-side rate requirements are charging limit >=q-a and discharging limit >=b-q. For stored-energy rates they are >=η_c(q-a) and >=(b-q)/η_d respectively. A symmetric PCC-side converter needs max(q-a,b-q). Common PCC ramp inside the block is zero. A discrete slot-to-slot bound on |u_{t+1}-u_t| must additionally admit b-a; this is a power jump, not a derivative bound. Literal step-task trajectories require instantaneous actuation at slot boundaries. No finite continuous-time slew can realize an instantaneous jump; smooth ramps require a separate timing and waveform contract. Start/end transitions are separate constraints.

**Proof.** Each permutation orders the same set of increments g_i=δφ(q-d_i), whose sum is zero. Every partial sum lies in [-Q,Q]. Ordering all positive increments first attains +Q; ordering all negative increments first attains -Q. Both orders are allowed. Thus E0-Q>=0 and E0+Q<=B are necessary and sufficient. The rate statements follow by evaluating the extreme tasks. QED.

## 3. Ideal-storage comparison, without a novelty claim

For η_c=η_d=1 let sorted powers be a_1<=...<=a_N. Define cumulative task-energy envelopes

  L_k=δ sum_{i=1}^k a_i,
  U_k=δ sum_{i=N-k+1}^N a_i,
  L_0=U_0=0.

**Proposition 3 (classical cumulative-envelope specialization).** With free nonnegative PCC power and no rate/ramp limit, the minimum buffer capacity hiding all permutations and recovering exactly is

  B_ideal = max_{0<=k<=N}(U_k-L_k).

One attaining public schedule is E0=B_ideal/2,

  Z_k=δ sum_{t=1}^k p_t=(U_k+L_k)/2,
  p_k=(a_k+a_{N-k+1})/2.

**Proof.** At prefix k the possible cumulative task energies include L_k and U_k. A fixed Z_k translates their energy-state range without changing its width U_k-L_k, proving the capacity lower bound. The proposed midpoint schedule centers every possible state at E0 with half-width at most B_ideal/2. Its increments are positive because the tasks are positive. At N, U_N=L_N equals total task energy, so all worlds recover exactly. QED.

This is a direct finite task-contract use of standard battery-privacy/cumulative-envelope reasoning and should not be advertised as a new general algorithm. Rate constraints require p_t in [max_i d_i-D, min_i d_i+C]; the displayed envelope solution need not obey them. PCC ramp constraints and converter slew constraints also need explicit checks or an augmented feasibility program.

**Example and singular exact-reset limit.** For N-1 tasks of power L and one task H>L:

  B_ideal=δ(H-L),
  ideal p=[(H+L)/2,L,...,L,(H+L)/2].

For any strictly lossy battery, Theorem 1 forces constant

  q=[H+α(N-1)L]/[1+α(N-1)],
  B_loss=2δ(N-1)η_c(q-L).

As η_c,η_d -> 1 from strictly lossy values,

  B_loss -> 2δ(H-L)(N-1)/N.

For N=6,L=6,H=18,δ=1 these limits are 12 and 20, respectively. The ratio is 2(N-1)/N, approaching 2 with N. This is an exact-constraint singularity. It is not a statement that more loss always increases capacity: the stored-energy unit and increased grid energy both matter, and sufficiently low charging efficiency can decrease required stored capacity while wasting energy.

At fixed positive finite-block tolerance τ, the ideal schedule's endpoint residuals tend continuously to zero as efficiencies tend to one. Therefore the exact-equality discontinuity alone is not a robust finite-tolerance performance claim. The next sections give the positive-tolerance, no-reset boundary.

## 4. Approximate endpoint recovery: exact and sharp nonflatness bounds

For a block and permutation π, write

  r_π = δ sum_t φ(p_t-d_{π(t)}).

If |r_π|<=τ for every permutation, comparing two orders differing only by swapping tasks a and b at slots s,t gives

  δ |F(p_s)-F(p_t)| <= 2τ.

Therefore

  spread(clip(p,a,b)) <= 2τ/(δκ).                 (1)

If every p_t is in [a,b], the clip may be removed. The raw spread bound is not valid without that restriction. This pairwise condition alone is not generally sufficient: common-mode endpoint drift and internal capacity/rates still matter.

For the one-high-slot multiset (N-1 copies of L and one H), let j denote the high task's slot. For arbitrary real p, define c_t=clip(p_t,L,H)-L and S=δ sum_t φ(p_t-L). Direct subtraction gives

  r_j = S - δ(H-L)/η_d + δκ c_j.               (2)

Consequently

  r_max-r_min = δκ spread(clip(p,L,H)).         (3)

When p_t in [L,H], (2) is equivalently

  r_j = δ[η_c sum_t(p_t-L)+κ p_j-H/η_d+η_c L]. (4)

Thus the exact one-block endpoint condition is

  |m|+w <= τ,
  m=(r_max+r_min)/2,  w=(δκ/2)spread(p).         (5)

The spread bound is sharp. Let q be the exact constant root and choose zero-sum perturbations ε_t with symmetric extrema ±s and q+ε_t in [L,H]. Then p_t=q+ε_t gives r_j=δκ ε_j, so m=0 and w=δκ s. Equality in (1) holds when s=τ/(δκ), whenever the power interval admits that perturbation. N=2 with perturbations (+s,-s) is the simplest witness. With larger horizons the budget can instead be distributed across blocks.

## 5. Arbitrary public blocks: the exact no-reset boundary

The schedule may differ publicly between blocks. Define, for block ℓ,

  g_{ℓ,π,k}=δ sum_{t=1}^k φ(p_{ℓ,t}-d_{π(t)}),
  r_{ℓ,π}=g_{ℓ,π,N},
  a_ℓ=min_π r_{ℓ,π},  b_ℓ=max_π r_{ℓ,π},
  m_ℓ=(a_ℓ+b_ℓ)/2,  w_ℓ=(b_ℓ-a_ℓ)/2.

Let g^-_{ℓ,k}=min_π g_{ℓ,π,k} and g^+_{ℓ,k}=max_π g_{ℓ,π,k}.

**Theorem 4 (exact reachable hull and recovery contract).** From common starting E0, after K complete blocks the smallest interval containing all reachable energies is exactly

  [E0+sum_{ℓ=1}^K a_ℓ, E0+sum_{ℓ=1}^K b_ℓ].  (6)

Both endpoints are attained by actual histories of complete task orders. Intermediate values need not all be reachable; “interval” here means exact interval hull, sufficient for interval state and recovery constraints.

At every prefix k of block ℓ the exact state hull is

  [E0+sum_{h<ℓ}a_h+g^-_{ℓ,k},
   E0+sum_{h<ℓ}b_h+g^+_{ℓ,k}].               (7)

All histories obey 0<=e<=B if and only if the lower endpoints in (7) are >=0 and upper endpoints are <=B. They obey |e_{K,N}-E0|<=τ at a given checkpoint K if and only if

  |sum_{ℓ=1}^K m_ℓ| + sum_{ℓ=1}^K w_ℓ <= τ. (8)

For recovery at every block, (8) must hold at every prefix K.

**Proof.** Energy increments are independent of the current energy in the declared model. A history has endpoint E0+sum r_{ℓ,πℓ}. Because each block's permutation can be chosen independently, the minimum sum is the sum of minima and the maximum is the sum of maxima; each is achieved by choosing its minimizing/maximizing order in each block. The same argument applies before a current prefix, proving (7). A closed interval [M-W,M+W] lies within [-τ,τ] exactly when |M|+W<=τ, proving (8). No state is reset anywhere. QED.

For a given public schedule, define L_* and U_* as the minimum and maximum relative-state endpoints in (7), including initial relative state 0. Its exact minimum capacity over freely selected E0 is

  B_schedule=U_*-L_*,  E0=-L_*.

Recovery error relative to E0 does not change under this shift. This is an exact deterministic optimization target; finding an optimal schedule remains a classical robust feasibility/optimization problem.

**Corollary 4a (cumulative hidden-order budget).** For one-high-slot tasks with PCC in [L,H], (3), (6), and (8) give

  δκ sum_{ℓ=1}^K spread(p_ℓ) <= 2τ.          (9)

The finite buffer independently gives the same left side <=B at checkpoints. Therefore it is bounded by min(B,2τ), though this simpler bound does not replace the exact common-mode condition (8) or the internal-prefix conditions (7).

For general task multisets, pair swaps give

  b_ℓ-a_ℓ >= δκ spread(clip(p_ℓ,a,b)),

so the corresponding clipped-spread sum bound remains necessary. For the one-high class, equality (3) remains valid even outside [L,H].

**Sharpness of the budget, including common mode.** For each block choose p_{ℓ,t}=q+ε_{ℓ,t}, with zero-sum perturbations, symmetric extrema ±s_ℓ, and values in [L,H]. Then a_ℓ=-δκs_ℓ, b_ℓ=δκs_ℓ, and m_ℓ=0. Hence all checkpoint conditions hold exactly when δκ sum_{h<=ℓ}s_h<=τ. Choosing the total sum equal to τ/(δκ) saturates (9), and actual histories choosing a maximizing or minimizing high-task slot attain the two recovery-band edges. A sufficiently large finite B contains all internal prefixes, as (7) gives directly. Thus no smaller universal constant than 2 in (9) is possible. This sharpness does not assert that the simultaneously minimum-capacity schedule attains the same witness.

**Common-mode drift cannot be omitted.** A sequence of flat blocks has zero spread and spends none of budget (9), yet can exhaust the buffer if every flat level is above q or below q. Conversely, public flat levels may alternate so that their order-independent residuals remain bounded. Thus summable within-block nonflatness does not force the block level to converge to q.

**Infinite horizon.** For fixed positive loss and a fixed finite recovery band, universal hiding of arbitrary independent block orders implies summability of the nonnegative clipped-spread sequence. In particular its terms tend to zero. For the one-high class inside [L,H], sum spread(p_ℓ)<=2τ/(δκ). Infinitely many nonflat blocks are possible with summable deviations; immediate exact flatness is not forced by positive tolerance. The common-mode sums and all within-block hulls must also remain bounded.

## 6. Fixed periodic public output: stronger rigidity and exact drift horizon

**Theorem 5.** Repeat the same public PCC block indefinitely. A finite buffer can hide every infinite sequence of independently chosen task permutations only if r_π=0 for every permutation. If all one-block paths fit, that condition is also sufficient. Under strict loss and nonconstant tasks, Theorem 1 therefore forces p_t=q. Replacing exact recovery by any fixed finite checkpoint band does not weaken this infinite-horizon conclusion.

**Proof.** If some r_π is nonzero, repeatedly execute that same complete order. The energy at block K is E0+K r_π and leaves every finite interval. Conversely zero residual for every order returns each block to E0 and makes concatenation of individually feasible paths valid. QED.

For a repeated order with residual r!=0, the first checkpoint violating |e-E0|<=τ is

  K_fail=floor(τ/|r|)+1,

subject to ordinary care when floating-point values are used near equality. For capacity alone, a positive r violates at the first K with Kr>B-E0, and a negative r at the first K with K|r|>E0. Internal prefixes can fail earlier.

An exact within-block horizon follows from G_min=min_k g_{π,k} and G_max=max_k g_{π,k}, including k=0,N. For r>0 and a feasible first block, K complete copies fit iff

  E0+G_min>=0 and E0+(K-1)r+G_max<=B.

For r<0 they fit iff

  E0+G_max<=B and E0+(K-1)r+G_min>=0.

For a fixed block hiding *all* histories through K, let a=min r, b=max r, G_min=min_{π,k}g, G_max=max_{π,k}g. The exact relative-state extrema are

  L_*=G_min+(K-1)min(0,a),
  U_*=G_max+(K-1)max(0,b).                    (10)

All checkpoint recoveries hold iff max(|a|,|b|)<=τ/K. Equations (10) explain why repeating one extremal past order suffices to certify the full-history extrema in a fixed-periodic LP; no SOC reset is being approximated.

## 7. One-high-slot algebra for an independent certificate

Assume p_t in [L,H], δ=1 for compact notation (multiply all increments by δ otherwise). Set

  v_t=η_c(p_t-L), V=(H-L)/η_d, λ=1/(η_cη_d)-1,
  A=sum_t v_t.

For high slot j, its endpoint residual is r_j=A-V+λv_j. Its prefix after the high task is sum_{t<=k}v_t-V+λv_j; before the high task it is sum_{t<=k}v_t. Thus, over all orders and all prefixes,

  G_max=A-v_N,
  G_min=min_j[sum_{t<j}v_t+(1+λ)v_j]-V.       (11)

The latter is <=0, and G_max>=0. To see the maximum formula, a still-unexecuted high task gives the largest prefix sum; among such prefixes the largest is immediately before a high task in the last slot. An endpoint cannot exceed this value because v_N+λmax v<=V. For the minimum, after a particular high task all subsequent increments are nonnegative, so its smallest prefix is immediately after that task. Formula (11), combined with (10), supplies a direct nonlinear-physics audit of a periodic LP without using its scenario matrices.

## 8. Boundary claims this analysis does not establish

- Universal same-PCC hiding is conditional on the declared task class, storage model, observation model, control timing, rate limits, and recovery contract
- The ideal envelope capacity, lossy flat capacity, and finite-tolerance minimax capacity are privacy/feasibility quantities, not source-identification rates or classifier accuracy
- Equality at one PCC does not alone hide which network bus the source occupies; that depends on the grid measurement map
- A recovered PCC waveform, or even an exact compute-power waveform, does not by itself prove an AI workload cause
- Ideal efficiency is a different rank of endpoint constraint; a numerical tolerance must not silently replace exact recovery
- Repeated approximate recovery is a physical obligation, not permission to numerically reset SOC at each block
- No claim of new generic rank, LP, set-membership, assignment, or interval-reachability methodology is made

## 9. General task multiset: classical assignment/rearrangement formula

For a block define the assignment costs C_{t,i}=δφ(p_t-d_i). Endpoint residual extrema are the minimum and maximum complete assignment sums. Because φ is concave, for x<=x' and a<=b,

  φ(x-a)+φ(x'-b) >= φ(x-b)+φ(x'-a).           (12)

One proof subtracts the two sides and uses that φ(x-a)-φ(x-b) is nonincreasing in x. Thus the cost is supermodular (the opposite sign of one common “Monge array” convention; the inequality, not the label, is decisive).

Let p_(1)<=...<=p_(N) and d_(1)<=...<=d_(N). Removing inversions by (12) proves

  b=max_π r_π=δ sum_i φ(p_(i)-d_(i)),
  a=min_π r_π=δ sum_i φ(p_(i)-d_(N+1-i)).      (13)

For the maximum, an inverted assignment is weakly improved by aligning its two rows; repeated swaps reach the aligned ordering. For the minimum, the same inequality weakly decreases the objective when an aligned pair is reversed; repeated swaps reach the reversed ordering. Ties do not affect the argument.

Consequently, for arbitrary independent public blocks the exact cumulative endpoint width is the sum of the nonnegative assignment ranges in (13). The recovery condition remains precisely (8). This generalizes the one-high closed form; it is a specialization of classical assignment/rearrangement reasoning, not a new assignment algorithm. Prefix extrema can likewise be obtained by assigning the current prefix rows and padding unexecuted rows with zero costs; a generic assignment formulation is safe when no simpler formula is proved.

## 10. Continuous within-slot output: a range-constrained extension

Consider the one-high task contract and allow a publicly prescribed measurable PCC waveform p_t(s) within slot t, 0<=s<=δ. Tasks still have constant powers L or H throughout each slot. Suppose p_t(s) is in [L,H] almost everywhere. Let its slot mean be pbar_t=δ^{-1} integral p_t(s) ds.

For a low task, φ(p-L)=η_c(p-L) throughout the slot. For a high task, φ(p-H)=(p-H)/η_d throughout the slot. Therefore every slot-boundary energy increment is exactly the increment in the discrete model with p_t replaced by pbar_t. In particular:

- Exact common endpoint recovery forces all slot means to the same q in Section 3, though the instantaneous waveform need not be flat
- Endpoint residual range is exactly δκ spread(pbar); the arbitrary-block sum budget is δκ sum_ℓ spread(pbar_ℓ)<=2τ
- With exact reset, all low-task boundary increments are δ η_c(q-L)>0 and the high-task increment is their negative sum. Ordering the high task first or last attains relative boundary energies -Q and +Q. Thus B>=2Q and E0 in [Q,B-Q] remain necessary
- The energy path within a low-task slot is nondecreasing, and within a high-task slot it is nonincreasing. It lies between its slot endpoints. Hence equal-mean waveforms introduce no additional SOC excursion; B=2Q,E0=Q is sufficient

This range need not be an arbitrary waveform restriction. If a symmetric PCC-side converter rate is R=H-L and the same p(t) must be feasible for either current task, then

  p(t) in [H-R,L+R]=[L,H]

almost everywhere. The rate contract itself supplies the needed range. A larger rate can permit excursions outside it.

Outside [L,H], exact slot-boundary equalities involve integrals of clip(p_t(s),L,H)-L, not slot means. Sequential charge/discharge modulation can alter common-mode energy and efficiency losses. The flat-mean/capacity theorem above therefore must not be generalized to unrestricted intra-slot modulation. Merely banning simultaneous charging and discharging does not ban sequential modulation. For general multisets with intermediate power levels, range-constrained modulation can cross their efficiency kink; the single-high/two-level argument should not be silently reused for that case.

## 11. Failure of universal hiding does not imply identification

A positive-loss/tolerance/capacity horizon for hiding every permutation is not a horizon after which any two task orders become identifiable. Pairwise ambiguity can remain forever.

For an explicit example, take N=6, low task L=6, high task H=18, η_c=η_d=0.95, capacity B=18, initial E0=9, and symmetric PCC-side rate R=12. Compare just two worlds: the high task occurs in slot 2 in world A and slot 3 in world B; all other tasks have power 6. Set public PCC power to 6 outside slots 2 and 3 and to

  q_pair=(H+η_cη_d L)/(1+η_cη_d)

in those two slots. The two nonzero storage increments have magnitudes

  Q_pair=δ η_c(q_pair-L)
        =δ(H-q_pair)/η_d.

One world encounters -Q_pair then +Q_pair; the other encounters +Q_pair then -Q_pair. Thus they have exactly the same public trace, perform all positive tasks, and both recover to E0 every block. With δ=1, q_pair is approximately 12.30749 and Q_pair approximately 5.99212, below both the 9-unit initial energy and headroom. The converter rate is also below 12. Concatenating either world, or arbitrary block choices between these two orders, remains feasible indefinitely.

Thus even if a separate optimization proves that B=18 cannot hide *all six* high-task positions through a declared horizon and recovery band, these two positions remain observationally indistinguishable forever. Universal privacy feasibility, pairwise identifiability, source localization, and AI-cause attribution are distinct questions.

## 12. Infinite-horizon minimax capacity with positive tolerance

The next result permits arbitrary public time-varying schedules and does not assume the same PCC block repeats. It is stronger than the exact-reset single-block argument.

**Theorem 6 (long-run capacity and permanent uncertainty cost).** Consider one-high-slot blocks, fixed η_cη_d<1, independent arbitrary task orders in every block, and common PCC slot means in [L,H]. Suppose one public infinite schedule keeps every possible history in a finite capacity B. There need not be any recovery constraint. Define the accumulated endpoint uncertainty

  W_∞=sum_{ℓ>=1}(b_ℓ-a_ℓ)
     =δκ sum_{ℓ>=1}spread(p_ℓ).

Then

  B >= 2Q+W_∞,                               (14)

where q and Q are the exact flat-reset quantities in Section 3. In particular the minimum capacity for infinite universal same-trace hiding is exactly 2Q, attained by p=q and E0=Q. A fixed positive recovery tolerance does not lower this infinite-horizon minimum. If B=2Q, every block must have zero order-dependent endpoint range. The statement concerns one infinite feasible schedule; a sequence of separately reoptimized finite-horizon schedules is not itself such a schedule.

**Proof.** Let s_ℓ=spread(p_ℓ), and q_ℓ=N^{-1}sum_t p_{ℓ,t}. Equation (6) and finite capacity give W_K=sum_{ℓ<=K}(b_ℓ-a_ℓ)<=B. These widths are nonnegative, so W_K converges to W_∞<=B, sum s_ℓ is finite, and s_ℓ->0.

For a flat block at level x in [L,H], put

  c(x)=δ η_c(x-L), h(x)=δ(H-x)/η_d,
  r(x)=(N-1)c(x)-h(x),
  V(x)=(N-1)c(x)+h(x).

The first is a low-task increment, -h is the high-task increment, r is the block residual, and V is the range of relative energies over every order and every prefix: its extrema are -(h) (high first) and (N-1)c (high last).

Average over all N choices of the high task independently in each block. The expected block residual for arbitrary p_ℓ is exactly r(q_ℓ), by formula (4). Since every history has its endpoint in [0,B], its expectation does too; hence sum_{ℓ<=K}r(q_ℓ) stays bounded. The affine function r has its unique zero at q and positive slope δ[(N-1)η_c+1/η_d]. Therefore the Cesàro average K^{-1}sum q_ℓ tends to q. This does not require q_ℓ itself to converge.

Let V_ℓ be the relative-state range over all prefixes and orders within actual block ℓ. Replacing all its powers by q_ℓ changes each slot increment by at most δs_ℓ/η_d, because φ is 1/η_d-Lipschitz. Every prefix changes by at most Nδs_ℓ/η_d, so

  |V_ℓ-V(q_ℓ)| <= 2Nδs_ℓ/η_d -> 0.

At the start of block ℓ, the endpoint hull already has width W_{ℓ-1}. Independent choices of prior and current orders make the range over all current states exactly W_{ℓ-1}+V_ℓ. Consequently B>=W_{ℓ-1}+V_ℓ for every ℓ. Average this inequality over ℓ=1,...,K. The average W_{ℓ-1} tends to W_∞. Since V is affine and the average q_ℓ tends to q, the average V(q_ℓ) tends to V(q)=2Q. The vanishing perturbation has zero Cesàro mean. Taking the limit proves (14).

The constant schedule q has zero uncertainty range and requires exactly 2Q by Theorem 2, proving attainability and the minimum. If B=2Q then W_∞=0; every nonnegative range is zero, and for the one-high class with p in [L,H] equation (3) forces each block's slot means to agree. QED.

**Consequences and limits.**

- Order-dependent uncertainty cannot be undone by future common open-loop output in this no-leakage, state-independent increment model. It consumes permanent headroom, quantified by W_∞
- Positive recovery bands constrain W_∞ further by W_∞<=2τ and the exact common-mode condition (8)
- Block levels need not converge to q; only their Cesàro mean is forced. The theorem does not contradict bounded common-mode oscillations
- As η_c,η_d approach one while remaining strictly lossy, the infinite-horizon minimum tends to 2δ(H-L)(N-1)/N, whereas the exactly ideal infinite-horizon envelope schedule uses δ(H-L). Thus the singularity persists at fixed positive tolerance on the infinite universal horizon
- At any fixed finite horizon, small-loss schedules can behave continuously with loss. The limits of infinite horizon and zero loss need not commute
- This is a universal same-trace capacity result. The persistent two-world counterexample in Section 11 remains valid and prohibits turning (14) into a universal identification horizon
- The range-constrained intra-slot extension in Section 10 applies using slot means. Unrestricted modulation, leakage, adaptive output that reveals state/order, or a restricted set of admissible block histories changes the argument

## 13. Fixed k high tasks: direct two-level extension

Let 1<=k<=N-1 tasks have power H and the remaining N-k have power L. A permutation is equivalently a k-element subset S of high-task slots. With p in [L,H],

  r_S=δ[η_c sum_t(p_t-L)+κ sum_{t in S}p_t
         +kη_c L-kH/η_d].

Therefore the exact endpoint range is

  b-a=δκ[sum of k largest p_t - sum of k smallest p_t]. (15)

The two subset sums attain the extrema because the only order-dependent term is the positive coefficient κ times their sum. Their difference is unchanged on replacing k by N-k, and is at least max p-min p: after separating the extreme pair, the remaining sorted high-low differences are nonnegative. Thus a finite cumulative assignment-range budget implies summable within-block spread here too.

The exact constant-reset level and half-capacity are

  q=[kH+α(N-k)L]/[k+α(N-k)],
  Q=δ(N-k)η_c(q-L)=δk(H-q)/η_d.

For a flat level x, block drift is (N-k)c(x)-k h(x), and within-block range is (N-k)c(x)+k h(x). Both are affine. The proof of Theorem 6 applies verbatim with these coefficients, giving B>=2Q+W_∞. The exact positive-tolerance condition still consists of the common-mode term plus half the cumulative range (15), as in (8).

The ideal universal envelope capacity is

  B_ideal=δ(H-L)min(k,N-k),

because at a prefix the possible numbers of completed high tasks range from max(0,t-(N-k)) to min(t,k). The strictly lossy infinite-horizon capacity tends as efficiencies approach one to

  2δ(H-L)k(N-k)/N.

The ratio to the ideal optimum is 2max(k,N-k)/N. It equals one in the balanced case k=N/2, so the capacity jump is not universal across all two-level task contracts even though loss still changes the admissible exact-reset policy structure.

The range-constrained continuous within-slot extension also holds for this two-level class: every low and high slot stays on one linear efficiency branch, so slot means give exact boundary increments and each within-slot SOC path is monotone.

## 14. General task multiset: range-constrained infinite-horizon theorem

**Theorem 7.** In the slot-constant model, let any nonconstant finite positive task multiset execute in arbitrary independent order in every block. Assume p_{ℓ,t} in [a,b]=[min_i d_i,max_i d_i], strict loss, and finite capacity B for every history. Let a_ℓ,b_ℓ be the exact assignment residual extrema in (13) and W_∞=sum(b_ℓ-a_ℓ). Let q be the unique zero of

  f(x)=δ sum_i φ(x-d_i),

and Q=δ sum_i[φ(q-d_i)]_+. Then B>=2Q+W_∞, and the minimum infinite universal hiding capacity is 2Q, attained by constant q and E0=Q.

**Proof.** The pair-swap bound gives b_ℓ-a_ℓ>=δκspread(p_ℓ), so finite capacity and the exact endpoint hull imply summable spread s_ℓ. Let q_ℓ be the mean of the slot powers. Averaging the residual uniformly over all permutations gives

  rbar_ℓ=(1/N)sum_t f(p_{ℓ,t}).

The function f is strictly increasing and Nδ/η_d-Lipschitz. Hence |rbar_ℓ-f(q_ℓ)|<=Nδs_ℓ/η_d and the error sequence is absolutely summable. Expected endpoint SOC remains in [0,B], so sum_{ℓ<=K}rbar_ℓ is bounded. It follows that the partial sums of f(q_ℓ) are bounded.

For a flat block x, its relative-state range is

  V(x)=δ sum_i |φ(x-d_i)|,

because positive increments first attain their sum and negative increments first attain their sum. Each summand is a convex V-shaped piecewise-linear function of x, so V is convex. The actual block range V_ℓ differs from V(q_ℓ) by at most 2Nδs_ℓ/η_d. The global capacity condition gives B>=W_{ℓ-1}+V_ℓ. Therefore limsup_ℓ V(q_ℓ)<=B-W_∞.

Suppose B-W_∞<V(q). Choose c strictly between those two numbers. Eventually every q_ℓ lies in the compact convex sublevel set {x in [a,b]:V(x)<=c}. This interval excludes q because V(q)>c, so it lies strictly on one side of q. Since f is continuous, strictly increasing, and zero at q, f(q_ℓ) then has one fixed sign with magnitude bounded away from zero. Its partial sums cannot remain bounded, a contradiction. Thus B-W_∞>=V(q)=2Q. The constant-q construction attains the lower bound when W_∞=0. QED.

Unlike the two-level case, this argument does not assert that the Cesàro mean of q_ℓ equals q; f is generally nonlinear. It uses bounded cumulative drift and convex state-range sublevels instead. The theorem is limited to slot-constant output (or a separately justified equivalent model). Arbitrary within-slot modulation can cross intermediate task-power efficiency kinks and is not covered merely by bounding p in [a,b].
