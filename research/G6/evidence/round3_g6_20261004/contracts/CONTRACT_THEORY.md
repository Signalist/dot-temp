# Imperfect common signs: exact finite-window support and the average-only obstruction

## Contract and startup convention

Freeze two templates q1=(1,1,-1,-1) and q2=(1,-1,-1,1), each constant on four half-second segments of a T=2 s block. The fixed allocation ray a=(a1,a2), with a1+a2=1, and radial amplitude rho are chosen once. For each block k,

    deltaP1 = rho a1 s_k q1,
    deltaP2 = rho a2 s_k (-1)^z_k q2,
    s_k in {-1,+1}, z_k in {0,1}.

Only the mismatch sequence z is constrained. The language K(L,B) consists of finite words whose every contiguous subword of length at most L has at most B ones. Equivalently pad the finite word by zeros on both sides and require every L-block window to have at most B mismatches. This includes precisely the startup prefixes extendible to the same infinite sliding-window contract. It does not give an unconstrained first seven blocks. If one instead constrains only completed L-windows during startup, shorter prefixes would require separate treatment and can be much worse; that is a different contract.

This definition is prefix-closed, suffix-closed, reversal-invariant, and closed under zero extension. It allows arbitrary common signs and carries electrical state across all block boundaries. No storage, reset, or optional per-block amplitude is introduced. B=0 is perfect common signs; B=L gives unrestricted relative signs and therefore independent signed ports. Intermediate languages are nested strictly as combinatorial sets, even if a particular model's worst-case support happens to coincide.

## Sign elimination and exact finite DP

For a selected frequency output and within-block phase, let g_j1,g_j2 be the two inherited lifted coefficients, j=0 for the current partial block and j=1,...,N for completed blocks, newest to oldest. Put p_j=a1 g_j1 and q_j=a2 g_j2. After choosing z_j, the common sign maximizing the positive output is independent at every lag:

    r_j(0) = |p_j+q_j|,   r_j(1) = |p_j-q_j|,
    s_j = sign(p_j + (-1)^z_j q_j).

Global reversal of all common signs proves that the positive support also equals the absolute-output support. Both rewards are nonnegative. Hence the exact finite support is

    H_N = sum_j r_j(0) + max_{z in K(L,B)} sum_j d_j z_j,
    d_j = r_j(1)-r_j(0).

Keep the most recent L-1 mismatch bits as a state m. Append z only if popcount(m)+z <= B, replace m by ((m<<1)|z) mod 2^(L-1), and add d_j z. Start at the zero state; maximize over all terminal states. This is a classical max-plus finite-state dynamic program, not a novel solver. The implementation scans lag order (current to oldest); reversal invariance makes the recovered chronological word equally admissible. Zero-state initialization of this automaton represents the startup/end padding of mismatch bits, not an electrical-state reset.

For L=8, at most 128 states are needed. Reachable state counts for B=0,1,2,4,8 are 1,8,29,99,128. The C++ implementation uses destination predecessors; the Python witness implementation independently uses forward transitions and backpointers. At B=8 a direct positive-part sum is equivalent.

## Every startup prefix and all time

Appending one more older block with z=0 preserves legality. Choose its common sign to attain r_j(0)>=0. Thus H_N is nondecreasing with retained history, even though rewards differ by lag; every shorter zero-state startup support is bounded by a longer support using the same phase. This monotonicity needs zero extension and nonnegative optimized block rewards; it must not be asserted for arbitrary finite-state languages.

For any infinite legal word, its truncated N+1 suffix is legal. The omitted older contribution in absolute value is bounded by the inherited port-independent modal tail. Conversely every finite maximizing word is a realizable zero-incremental-state startup history and can be completed and extended with zero mismatches. Its current partial block is completed in the exported schedule. The electrical state is carried continuously through all 257 blocks. Taking the supremum over N, outputs and phase therefore covers all startup times and all legal infinite histories, subject to the same stable LTI kernel assumptions.

## Continuous phase and tail enclosure

For any word and any phase interval between template switches,

    |dy/dtau| <= sum_j sum_i a_i |g'_ji(tau)|.

This bound does not depend on the mismatch language or common signs. A maximum over admissible words has the same Lipschitz bound. The inherited derivative bound L_a includes both one-sided switch derivatives and is the smaller of a global analytic first-derivative bound and the sampled sum-absolute derivative maximum plus its modal tail plus (h_old/2) times an analytic second-derivative bound. It was evaluated at the inherited 2048-interval grid; that computation remains a valid global derivative bound when evaluating support on any coarser nested grid.

With h=2/M, all segment switches included, the exact conditional-model support satisfies

    max_grid H_N <= H_infinity <= max_grid H_N + (h/2)L_a + tail_a.

The lower endpoint is attained by a finite legal word, so no subtraction of the tail is required. On the 0.05 Hz criterion, rho_inner=0.05/(max_grid H_N+error) is sufficient and every rho>rho_outer=0.05/max_grid H_N has a finite witness. Equality at the outer endpoint saturates rather than strictly violates the limit. The exported witnesses use 1.02 rho_outer and reach 0.051 Hz in the conditional finite linear sum.

These are analytic-formula, ordinary-floating-point numerical brackets. They do not enclose eigensystem, descriptor approximation, or model error uniformly; no directed rounding or interval proof is claimed. 'All phase' distinguishes the quantifiers from a grid-only screen and does not upgrade the numeric/model qualification.

## A strongest same-information classical baseline

After sign elimination the finite objective is linear in z. Solve

    max d^T z
    subject to 0 <= z_j <= 1,
               sum_{j=k}^{k+L-1} z_j <= B for every complete window.

For n<L use the one inequality sum_j z_j<=B. For n>=L every shorter boundary subword is contained in a full window, so these constraints describe the same padded finite language on binary points. The window-incidence matrix has consecutive ones in each column and is totally unimodular; adding unit bounds preserves total unimodularity. With integer B its LP vertices are integral. Thus the LP equals binary enumeration, the DP, and the ordinary support calculation using exactly the same information. The experiment checks all 30 maximizing rows plus 54 independently selected rows with SciPy/HiGHS LP, and small words by exhaustive enumeration. This is baseline equivalence, not algorithmic advantage. Numerical LP objective tolerances are recorded rather than hidden.

## Why asymptotic mismatch rate is insufficient

Consider any constraint of the form

    limsup_{n->infinity} (sum_{k=0}^{n-1} z_k)/n <= alpha,

where alpha>=0. An arbitrary finite mismatch word followed by zeros has limiting density zero and is allowed even when alpha=0. Therefore, at any finite observation horizon, every independent-sign word is allowed by this average-only constraint. All finite independent supports are attainable, and their supremum is the stable all-time independent-sign support. The reverse inequality follows because average-constrained inputs are a subset of independent-sign inputs. Hence the all-time robust supports are exactly equal.

This result also applies to any looser average-only semantics explicitly allowing every finite burst. It does not apply to a finite-horizon cumulative budget, a token bucket with a bounded burst parameter, or a uniform finite-window constraint. Those impose extra local restrictions. Small average mismatch rate alone gives no all-time peak-frequency benefit. A meaningful imperfect-synchrony guarantee needs bounded local bursts or another finite-time envelope.

## Exact work ledger and physical scope

Every complete block has sum(q_i)=0, regardless of s and z. Thus integral(deltaP_i)=0, integral(P_i)=P0_i T, and under the declared affine law

    w_i(t)=wbar_i+kappa_i deltaP_i(t),

integral(w_i)=wbar_i T. Nonnegative instantaneous work additionally requires wbar_i>=|kappa_i| rho a_i. A completed 257-block word has duration 514 s and work exactly 514 wbar_i. This is a symbolic conditional identity, not an empirical work calibration or a queueing/latency claim.

At the positive Kundur point P0_i=50 MW, the complete-word energy is exactly 25700 MW s = 7.1388888889 MWh per port. The WECC source has P0_i=0; its signed segments include negative demand, and its zero energy ledger is only an incremental mathematical computation. The WECC case is not a physical compute-load realization. All radial thresholds concern zero-mean fluctuation amplitude, not added average load or additional completed work.
