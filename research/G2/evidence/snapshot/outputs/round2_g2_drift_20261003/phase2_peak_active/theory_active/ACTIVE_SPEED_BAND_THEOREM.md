# Active speed bands: exact bridges, second-order compression, and peak certificates

2026-10-03. This extends the stated clock contract, not the novelty claim. Bounded-acceleration bridge reachability, clipped bang/coast extremals, trajectory scaling, and moment-preserving spline approximation are classical. The clipped envelope already appears in `../../theory/CLOCK_DRIFT_THEOREMS.md`, §2.1. This note supplies the missing path-constrained compression and its consequences for the energy-per-work output contract. It does not rename standard trajectory scaling as a new algorithm.

## 1. Contract and main conclusions

Fix a common physical horizon T. The continuously running, unwrapped clock satisfies

    θ′=v,  |v′|≤ρ a.e.,  0<l≤v≤u,
    (θ(0),v(0))=(θ₀,v₀),  (θ(T),v(T))=(θ_T,v_T).

Here ρ>0; initial and final speeds and phases may be noncentral. Every electrical port has p_j=e_j(θ)v, with measurable 0≤e_j≤e_max,j and primitive E_j. Strict positivity can be imposed without changing any bound. Fixed θ_T fixes work and each port's electrical energy. All compared clocks have the same initial electrical state and idle-power history. Electrical outputs have strictly proper LTI kernels h_j with h_j absolutely continuous on [0,T]. Finite-dimensional LTI kernels satisfy the stronger regularity usually wanted for numerical evaluation.

The speed band can be genuinely active. No condition ρT/4≤min(v₀−l,u−v₀) is assumed.

**Results.**

1. Local bridge feasibility has exact scalar inequalities, and any feasible local bridge has a constructive replacement with at most five constant-acceleration arcs, each acceleration in {+ρ,0,−ρ}. The replacement preserves both endpoint phases and speeds and the full speed band.
2. On a mesh of maximum cell length Δ, replacements satisfy ‖θ_hat−θ‖∞≤ρΔ²/8. With M cells they use at most 5M arcs, or 5M−1 acceleration switches. These deliberately safe counts include degenerate and joining arcs.
3. The full output trajectory, and therefore its absolute peak, has amplitude-only uniform error at most (ρΔ²/8) B_peak, where

       B_peak=Σ_j e_max,j (|h_j(0)|+∫₀ᵀ|h_j′(s)|ds).

   At the common terminal time the h_j(0) terms disappear exactly. No bound on workload derivatives or bandwidth is needed.
4. Consequently O(ε^−1/2) bang/coast arcs suffice for ε-optimal terminal or full-window peak representation. The preceding two-port lower construction remains Θ(m^−2) for terminal-value representation even on the genuinely active fixed band [0.9,1.1]. We do not infer a matching peak-optimal-value lower bound from a terminal lower bound.
5. The resulting finite family supports rigorous accept/reject/unknown decisions if its global upper, feasible lower, and numerical/model errors are certified. The approximation theorem is not a global optimizer or a runtime bound.

## 2. Exact local bridge feasibility

Consider a cell [0,d], prescribed speeds w₀,w₁ and displacement D. Necessarily

    l≤w₀,w₁≤u,   |w₁−w₀|≤ρd.

Under these conditions the pointwise lowest and highest feasible velocities are

    v_−(s)=max(l,w₀−ρs,w₁−ρ(d−s)),
    v_+(s)=min(u,w₀+ρs,w₁+ρ(d−s)).

Their areas are

    A_+=(w₀+w₁)d/2+ρd²/4−(w₁−w₀)²/(4ρ)
        −(w₀+w₁+ρd−2u)_+²/(4ρ),
    A_−=(w₀+w₁)d/2−ρd²/4+(w₁−w₀)²/(4ρ)
        +(2l−w₀−w₁+ρd)_+²/(4ρ).

The exact necessary and sufficient condition is

    A_−≤D≤A_+.

Necessity follows from v_−≤v≤v_+. Sufficiency follows already by convexly mixing v_− and v_+: both have the prescribed endpoint speeds and obey the convex acceleration and speed constraints. The areas are obtained by integrating two intersecting ramps and subtracting the clipped cap (or adding the clipped floor). This argument also proves there are no untested interior speed constraints hidden in the area test.

For ρ=0 feasibility means w₀=w₁ and D=w₀d. For d=0 it means identical phases and speeds. For l=u it means the unique constant-speed bridge. These cases must be handled before formulas that divide by ρ or d.

## 3. Canonical five-arc bridge and scalar construction

Put

    U₀(s)=min(u,w₀+ρs),
    L₁(s)=max(l,w₁−ρ(d−s)),
    v_c(s)=max(L₁(s), min(U₀(s), c−ρs)),
    c∈[w₀,w₁+ρd],   Q(c)=∫₀ᵈv_c(s)ds.

The endpoint-speed compatibility implies L₁≤U₀. Every v_c is ρ-Lipschitz, lies in [l,u], starts at w₀ and ends at w₁. Q is continuous and nondecreasing, Q(w₀)=A_−, and Q(w₁+ρd)=A_+. Thus every feasible D has a solution of Q(c)=D, including area-degenerate cases.

The chronological acceleration pattern is a subsequence of

    +ρ, 0 at u, −ρ, 0 at l, +ρ.

Indeed, U₀ is nondecreasing and the middle line is decreasing, so min(U₀,c−ρs) moves from U₀ to the line at most once. It then crosses the nondecreasing L₁ at most once. Each of U₀ and L₁ has at most two pieces. No unexplained extra switches occur.

An explicit breakpoint formula, allowing coincident points, is

    s_down=max((c−w₀)/(2ρ), (c−u)/ρ),
    s_up=min((c−l)/ρ, (c−w₁+ρd)/(2ρ)),
    s_cap=min((u−w₀)/ρ, s_down),
    s_lift=max(d−(w₁−l)/ρ, s_up).

For feasible endpoint data these satisfy

    0≤s_cap≤s_down≤s_up≤s_lift≤d.

The nodes 0,s_cap,s_down,s_up,s_lift,d, evaluated through v_c, give the exact piecewise-affine velocity. Integrate each segment by its trapezoid formula to obtain Q. Zero-length segments are removed. Areas and phase within each arc are quadratic, with no time quadrature needed.

Only the thresholds c=2u−w₀ and c=2l−w₁+ρd change the nondegenerate formula; Q is piecewise quadratic. Solve the appropriate scalar quadratic, or use monotone interval bisection. Away from degenerate points Q′(c)=s_up−s_down. The map can be flat, so do not assume uniqueness or uniformly conditioned inversion. If A_−=A_+, use the unique feasible velocity directly; any c that produces it suffices.

### 3.1 Simultaneous phase maximality

The selected v_c is the frontloaded bridge: its cumulative phase is simultaneously maximal at every point among bridges with the same D,w₀,w₁,d.

For another feasible v, v−v_c is nonpositive while v_c=U₀, nondecreasing while v_c has slope −ρ, and nonnegative while v_c=L₁. Thus it changes sign at most once, from negative to positive. Since its full integral is zero, every prefix integral is nonpositive. This establishes θ≤θ^+, where θ^+ is the phase of v_c.

Reverse time, swap endpoint speeds, apply the same construction for D, and reverse back to obtain θ^−. Then θ^−≤θ≤θ^+ simultaneously. This uses no electrical kernel and is classical bounded-acceleration envelope structure.

## 4. Active-band moment compression theorem

Partition [0,T] into M cells. For an arbitrary supplied feasible clock, retain each cell's initial/final speed and displacement. They pass §2 by construction. Replace the cell by §3's frontloaded bridge and concatenate. The replacements agree in phase and speed at joins, so the concatenation has continuous phase and speed, globally Lipschitz velocity, the original terminal contract, and the speed band everywhere. Its acceleration can jump; no finite jerk is claimed.

This is exactly local two-moment matching in a path-constrained form. For physical acceleration α=v′,

    ∫₀ᵈ α(s)ds=w₁−w₀,
    ∫₀ᵈ sα(s)ds=dw₁−D.

Both moments are preserved, even though a pure two-switch ±ρ replacement need not respect the band.

Let f=θ_hat−θ on a cell. Then f,f′ vanish at both endpoints and |f″|≤2ρ. The sharp clamped second-derivative envelope from the earlier note gives

    0≤f(s)≤2ρ b_d(s)≤ρd²/8,

where b_d is the three-piece envelope with maximum d²/16. Nonnegativity follows from frontloaded maximality; the absolute bound only needs moment matching. Taking the maximum over cells proves

    ‖θ_hat−θ‖∞≤δ_M:=ρΔ²/8.

There are at most 5M nonempty affine-velocity arcs before merging adjacent arcs with equal slope. Hence at most 5M−1 switches suffice. For a uniform mesh Δ=T/M this is O(M^−2) phase error with O(M) representation.

**No search claim:** this compresses a supplied feasible trajectory. Applied to an unknown optimizer it proves existence of a near-optimal finite representation, not that its parameters are known or quickly discoverable.

### 4.1 Why coast arcs cannot be omitted

Take a cell with w₀=w₁=u and D=ud. The only band-feasible bridge is v≡u, so α=0 almost everywhere. An acceleration taking only ±ρ cannot satisfy this same contract, no matter how many switches it has.

Applying the old unconstrained two-moment compression to α=0 gives +ρ on [0,d/4], −ρ on [d/4,3d/4], +ρ on [3d/4,d]. Its speed reaches u+ρd/4 and violates the upper bound. Matching endpoint phases and speeds alone does not protect an intermediate speed band. The same obstruction applies at l.

## 5. Full-window output and support error

For any observation time τ≤T, the exact integration-by-parts identity for two clocks starting at the same phase is

    y_hat(τ)−y(τ)
      =Σ_j h_j(0)[E_j(θ_hat(τ))−E_j(θ(τ))]
       +Σ_j∫₀^τ h_j′(τ−s)[E_j(θ_hat(s))−E_j(θ(s))]ds.

This identity remains valid for bounded measurable e_j: E_j is Lipschitz, its composition with a strictly increasing bi-Lipschitz phase is absolutely continuous, and dE_j(θ)/dt=e_j(θ)v almost everywhere. There is no workload derivative in the identity or bound.

Since |E_j(x)−E_j(z)|≤e_max,j|x−z|,

    |y_hat(τ)−y(τ)|
       ≤δ_M Σ_j e_max,j (|h_j(0)|+∫₀^τ|h_j′(s)|ds)
       ≤δ_M B_peak.

At τ=T, or any retained cell endpoint, θ_hat=θ so the boundary term is exactly zero. The terminal constant is B_T=Σ_j e_max,j∫₀ᵀ|h_j′|.

For positive e_j and frontloaded compression, the energy differences are nonnegative. Thus a sharper directional bound is

    −δ_M B_+(τ) ≤ y(τ)−y_hat(τ) ≤ δ_M B_−(τ),
    B_±(τ)=Σ_j e_max,j ((±h_j(0))_+ +∫₀^τ(±h_j′(s))_+ds).

These signs are important: the upper correction for the original output uses negative parts of the kernel. At retained endpoints remove h_j(0). One may also use the exact cellwise phase width θ^+−θ^−, rather than δ_M, and exact primitive differences for a posteriori tightening.

Let R=sup_feasible θ sup_{0≤τ≤T}|y_θ(τ)|, including the common deterministic electrical response, and let R_M restrict θ to the concatenated canonical family. Then

    0≤R−R_M≤δ_M B_peak.

The same statement holds for terminal absolute output with B_T. More sharply, for signed full-window supports V_+=sup_θ,τ y and V_−=sup_θ,τ (−y), their respective approximation losses are bounded by δ_M sup_τ B_−(τ) and δ_M sup_τ B_+(τ). A linear direction in a multi-output electrical observation is handled by combining its output kernels first.

For ε>0, M=max(1,ceil(sqrt(ρT² B_peak/(8ε)))) and at most 5M arcs suffice. This is independent of workload bandwidth, although evaluating E_j and globally optimizing the finite family may depend on how the workload is represented.

### 5.1 Peak sampling is a separate issue

The O(Δ²) trajectory-to-trajectory error does not itself certify a sampled maximum. Either maximize over τ continuously or add a validated time-grid error. A generic amplitude-only bound is Lipschitz:

    L_y≤‖y_det′‖∞ + u Σ_j e_max,j (|h_j(0)|+∫₀ᵀ|h_j′|).

For a τ-grid including 0 and T with largest gap q, sup_τ|y(τ)|≤max_grid|y|+L_y q/2. With amplitude-only workloads there is no uniform bound on y″; a generic second-order smooth interpolation claim would be unjustified. Workload jumps and arbitrarily rapid bounded variation can create unresolved narrow peaks. To preserve an overall O(Δ²) budget with this generic grid method, choose q=O(Δ²); optimizing τ as another variable can be preferable.

## 6. Exact endpoint-state parametrization and global certificates

For fixed cell lengths d_i, use node phases θ_i and speeds w_i. Fix the external endpoints and require, independently for each cell,

    l≤w_i≤u, |w_{i+1}−w_i|≤ρd_i,
    A_−(d_i,w_i,w_{i+1})≤θ_{i+1}−θ_i≤A_+(d_i,w_i,w_{i+1}).

These conditions are necessary AND sufficient for continuous-clock realizability of the complete endpoint-state list; concatenating §3 constructs a witness. Thus the state/event abstraction has no fictitious feasible endpoints and requires only 2(M−1) free variables. It differs from an independent box for each event: neighboring times/speeds/phase increments are coupled by exact bridge inequalities.

For event B&B an alternative avoids numerical inversion: use the M−1 interior speeds and M parameters c_i, with

    w_i≤c_i≤w_{i+1}+ρd_i,
    Σ_i Q_i(c_i)=θ_T−θ₀.

Endpoint compatibility and the speed band remain required. Prefix phases are obtained by accumulating Q_i. There are 2M−1 scalar coordinates and one endpoint-work equality. All arc breakpoints and phase polynomials are explicit. Q_i is monotone and piecewise quadratic. Boxes can be rejected if the validated interval sum of Q_i misses the terminal displacement; interval endpoint feasibility tests can prune further.

For fixed d_i,l,u,ρ, the min/max formula is nonexpansive:

    ‖v_c−v_c_tilde‖∞≤max(|w₀−w₀_tilde|,|w₁−w₁_tilde|,|c−c_tilde|).

Thus parameter boxes give direct, workload-bandwidth-independent phase tubes, with accumulated phase width at most Σ_i d_i ε_i when the cell parameter radii are ε_i. Combine Lipschitz E_j, interval kernel integrals, and a τ interval to produce global upper bounds. This does not prove a favorable B&B runtime; degeneracy, high dimension, and expensive workload primitive oracles remain real costs.

For a practical admission interface, obtain:

    L = a validated absolute peak from one or more exactly feasible witnesses,
    U_M = a global upper for R_M, including time maximization and numerical errors,
    ε_repr = δ_M B_peak.

Then L≤R≤U_M+ε_repr. Add any separately justified model/measurement margin ε_model to the upper; account symmetrically for witness output error when claiming a physical lower. For a threshold H:

    accept if U_M+ε_repr+ε_model≤H;
    reject if a validated physical feasible lower exceeds H;
    otherwise unknown.

A merely local optimizer or a dense sample of clocks supplies a lower, never U_M. Ordinary floating-point quadrature is not a validated enclosure. Equality constraints satisfied only to a tolerance do not by themselves define a feasible witness; use exact/algebraic or outward-enclosed bridge construction and certify the terminal area.

### 6.1 Useful node-conditioned enclosure

For any fixed feasible node-state list, construct the lower/upper phases θ^−,θ^+ cellwise. At any τ the original clock lies in this phase corridor. Apply monotonicity of E_j to each term of the integration-by-parts identity, choosing the lower or upper primitive according to the sign of h_j(0) and h_j′. This gives a rigorous (possibly conservative) output enclosure for ALL clocks sharing those nodes. It retains the common-horizon terminal condition and can form a B&B node bound. Shared-phase dependencies between ports should not be called independent controls; separate port bounding is explicitly a relaxation.

### 6.2 Standard convex reachability support baseline

The exact node-feasibility set is convex. Write D=θ_{i+1}−θ_i and d=d_i. Its nonlinear inequalities can be written

    g_+=D−(w₀+w₁)d/2−ρd²/4
          +(w₁−w₀)²/(4ρ)+(w₀+w₁+ρd−2u)_+²/(4ρ)≤0,
    g_−=(w₀+w₁)d/2−ρd²/4−D
          +(w₁−w₀)²/(4ρ)+(2l−w₀−w₁+ρd)_+²/(4ρ)≤0.

Both are affine plus squared affine and squared positive-part affine functions, so are convex jointly in D,w₀,w₁. Together with the linear band and endpoint-slope constraints they have a standard rotated second-order-cone representation. For example, introduce s_+≥0, s_+≥w₀+w₁+ρd−2u and t_+=(w₀+w₁)d/2+ρd²/4−D; impose (w₁−w₀)²+s_+²≤4ρt_+. The lower inequality is analogous. Nothing here is a new SOCP or cutting-plane method.

If an outer LP is used, the tangent inequality g(z₀)+∇g(z₀)·(z−z₀)≤0 is valid for every exactly feasible z, because the convex function lies above its tangent. LP maximization of a linear objective therefore gives an upper, with the LP and coefficient errors separately certified. A candidate can be contracted toward a strictly feasible nominal node sequence: for each convex constraint, λ≤−g_nom/(g_candidate−g_nom) when g_candidate>0 guarantees feasibility of (1−λ)z_nom+λz_candidate. Band/slope constraints also need verification. This repair is not valid without modification if the nominal has zero slack, as can occur on a band edge or a degenerate bridge.

For a first-order output baseline, choose a feasible affine nominal phase φ and assume each e_j has Lipschitz constant L_e,j. Let d_θ=θ−φ. The signed output expansion at any τ is

    y_θ(τ)=y_φ(τ)+ℓ_τ(d_θ)+R_τ,
    ℓ_τ(d)=Σ_j[h_j(0)e_j(φ(τ))d(τ)
                  +∫₀^τh_j′(τ−s)e_j(φ(s))d(s)ds].

Use the exact global active-band phase envelope to bound β(s)=max(|θ^+(s)−φ(s)|,|θ^−(s)−φ(s)|). Then

    |R_τ|≤(1/2)Σ_j L_e,j[|h_j(0)|β(τ)²
                       +∫₀^τ|h_j′(τ−s)|β(s)²ds].

This extra Taylor assumption is needed only for this first-order baseline; the nonlinear compression theorem in §5 remains amplitude-only.

Let Iθ be piecewise-linear interpolation of the node phases. The ordinary second-derivative interpolation estimate gives |θ−Iθ|≤ρΔ²/8, without assuming that Iθ is an admissible clock. The quantity ℓ_τ(Iθ−φ) is exactly a linear function of the phase-node variables (integrate against their hat basis, retaining the earlier-time boundary term). If S_mesh is its exact maximum over the convex reachable node set and S_cont is the true continuous-clock linear support, then

    |S_cont−S_mesh|≤(ρΔ²/8) Σ_j e_max,j
                       (|h_j(0)|+∫₀^τ|h_j′|).

One direction follows by mapping every feasible clock to its nodes. The other follows by reconstructing a feasible bridge for every feasible node list. Therefore an LP outer upper plus this interpolation correction and the Taylor remainder is a valid nonlinear directional upper. An exactly reconstructed candidate gives a feasible nonlinear lower. This provides a strong same-information, continuous-speed-band baseline; a finite action-grid DP alone would not give the same upper guarantee.

If τ is a phase mesh node, θ(τ)=Iθ(τ), so the h_j(0) contribution to the interpolation correction is zero. Its Taylor remainder generally remains at an interior mesh node because θ(τ) need not equal φ(τ). At the common terminal time both boundary contributions are zero. If observations include 0 and T, the known initial output is still included in the physical peak; it must not be discarded with a clock-difference term.

## 7. Terminal sharpness on a genuinely active fixed band

Use the exact fixed-grid workload family from `../../theory/MULTIPORT_SWITCH_COMPLEXITY_ADDENDUM.md`, with T=r=ρ=1, h₁=−exp(−t), h₂=exp(−t), 3/4≤e_j≤5/4 and ∫₀¹e_j=1. Change only the speed contract to [0.9,1.1]. This band is genuinely active: the old unconstrained extremal reaches 1±1/4 and is excluded.

The earlier witness a_N=sign(cos(2πNt)) satisfies |v_N−1|≤1/(4N), hence belongs to the new band for every integer N≥3. Its established output lower remains

    V_active(e^(N))≥A I_χ/(4π³N²),   N≥2304.

The earlier low-switch estimate applies to ANY piecewise-constant acceleration a∈[−1,1] with m jumps, not just pure bang: TV(a)≤2m is the only property used. Restricting speeds to [0.9,1.1] only shrinks the candidate set, so the SAME bound remains valid:

    |y(1)|≤A[2m W_max+C_W+C_V]/(8π³N³).

The old [3/4,5/4] constants remain valid conservative bounds for this subset. Consequently the same choice N proportional to m proves a strictly positive Ω(m^−2) worst-case terminal optimal-value gap for bang/coast or arbitrary piecewise-constant acceleration representations.

Conversely §4–5 gives, for m≥4 and M=floor((m+1)/5),

    sup_e[V_active(e)−V_active,m(e)]≤ρT²B_T/(8 floor((m+1)/5)²).

Hence the amplitude-only terminal representation rate on this fixed, genuinely active contract is Θ(m^−2), or Θ(ε^−1/2) arcs. The same transfer applies to terminal absolute output. The exponent is unchanged; allowing active bands changes the construction, not this worst-case rate.

This is not an exact optimizer bang/coast-count theorem. The old proof that every optimizer is bang relies on inactive state constraints and is not transferred. Nor does the terminal lower prove a lower on the peak-optimal-value gap: a low-switch path might achieve a competing larger output earlier. Degenerate bands or a mean speed forced to a band edge can have only one constant clock, so no lower bound is asserted for every possible active-band contract.

## 8. Scope and checks

- This closes active speed bands for exact local feasibility, finite representation, and full-window LTI output approximation under a common final phase/speed promise
- It does not close finite jerk, direct feedthrough, nonlinear electrical reachability, or speed-dependent energy-per-work
- Endpoint-event variables alone are not exact sufficient statistics for e(θ)v electrical output; canonical reconstruction plus its explicit error is needed
- `active_speed_bridges.py` and `verify_active_speed_bridges.py` provide constructive floating-point diagnostics, not outward-rounded machine proofs; analytical statements above do not rely on those samples
- Classical bounded-acceleration bridge/envelope and second-order approximation methods are direct prior techniques. The energy/work semantics, active-band certificate interface, and scoped rate transfer are the application-level deliverables; historical novelty is not established
