# Full-cycle smoothing: exact reductions, convex regime and global nonconvex alternative

## 1. Contract and costs

One task starts at actual dynamic power p0≥0. Its work W∈[0,M] has known law μ. While it is unfinished, x_dot=s(p), p≥0, and |p_dot|≤R. EOS is instantaneous. No phase signal, external arrivals, concurrency, pre-EOS intentional burn/pause, storage, or thermal state is available. After EOS the same physical power descends at −R and all resulting energy is charged as actual dissipation. The action class is deterministic work profiles and their independent randomized mixtures; randomization cannot improve a linear expected cost. The burner must actually exist; it is not free storage.

The objective is E[E_dynamic]+c E[T_cycle], c>0. T_cycle includes the full return to zero. Equivalently c=P_idle+λ where a constant facility baseline P_idle is charged throughout the whole active/return cycle and λ weights cycle availability. This is not E_dynamic+λE[T_task]; not a fixed-calendar-horizon energy ledger; not an overlapping queue; and not a complete data-center cooling model. A serial regenerative interpretation requires each next task to begin after return and no additional persistent state.

Assume s(0)=0, s>0, s′>0 on p>0, s continuous and concave, with the stated differentiability. Let A(p)=∫₀ᵖs(q)dq, P=A⁻¹, z=A(p). Then z′(x)=p_dot, so |z′|≤R. The finite-expected-cost work-profile class maps back by t(x)=∫₀ˣ1/s(P(z))du. Finite expected cost guarantees μ-a.s. completion, not automatically hard completion at a zero-probability endpoint. The saved experiments separately reconstruct W=M.

Define G(z)=(P(z)+c)/s(P(z)), H(z)=[P(z)²/2+cP(z)]/R, S(x)=Pr(W>x). Exactly

J[z]=∫₀ᴹ S(x)G(z(x))dx+∫_[0,M]H(z(w))μ(dw).

H′(z)=G(z)/R. For finite costs, integration by parts (first on interior compact intervals, then nonnegative finite-cost limits) yields the reserve identity

J[z]=H(z0)+∫₀ᴹ S(x)G(z(x))[1+z′(x)/R]dx.                 (1)

The integrand is nonnegative. H(z0) is the unavoidable cost of returning the initial power to zero as fast as possible. Productive maximum descent z′=−R incurs no further full-cycle cost relative to that prepaid return. It can still use real time and energy; neither is deleted from the ledger.

### Dominated pre-EOS burn, throttling and waiting

The action class can be enlarged to 0≤x_dot≤s(p), including deliberate pre-EOS burn/throttling, **provided the same actual draw can always be redirected to productive service at s(p)** and there is no thermal, storage, arrival, clock, or extra-information benefit from withholding service. Fix any random seed. Simulate the original policy’s deterministic no-EOS power trajectory using its own ghost progress; follow exactly that p(t) but assign maximum service to real progress. Real progress never lags ghost progress, so its EOS is earlier. Before that EOS the simulated no-EOS history remains consistent. At the earlier EOS switch to fastest return. Any remaining original waveform has cost at least H(current z), whereas the replacement pays exactly H. This proves pathwise cost dominance and preserves causality. Independent randomization does not change the argument. Zero-power waits can also be spliced out when they have no exogenous benefit.

Thus productive use until EOS is a without-loss choice under this redirectability contract, not an unconditional claim about real GPU idle periods, synchronization or thermally beneficial waiting.

## 2. Exact terminal recovery projection

If z0≤RM, define C_Rz(x)=min{z(x),R(M−x)}. It preserves the initial state and R-Lipschitz feasibility. Wherever it changes z, its derivative is −R a.e.; its integrand in (1) is zero. Elsewhere its state and derivative agree with z a.e. Therefore J[C_Rz]≤J[z]. No probability-density assumption is needed, and the reduction is pathwise in full-cycle cost.

Thus an optimizer may be selected with z(M)=0 and z(x)≤R(M−x). This is an exact restriction of the optimization domain, not an externally imposed hard recovery deadline. Physically, once the remaining work fits inside the stopping-work reserve, simply keep doing useful work at maximum descent until EOS, then burn the rest of the same return waveform. Increasing that reserve further has no benefit for this objective.

If z0≥RM, z(x)=z0−Rx completes every admissible amount of work during a single fastest return and attains J=H(z0), the global lower bound. Its EOS=M power can remain positive; the rest is burned. The terminal-zero reduction is not applied in this case.

## 3. Critical projection and nonzero initial state

Set N(p)=s(p)−(p+c)s′(p). Since N′=−(p+c)s″≥0, G decreases until the first critical root p_c and then does not decrease. H always increases. If no root exists, omit the critical cap. From idle or p0≤p_c, z→min(z,A(p_c)) cannot raise either running or terminal costs and preserves slew.

For p0>p_c, use b(x)=max{A(p_c),z0−Rx} and replace z by min(z,b). Feasibility already gives z≥z0−Rx. Hence this forces exact fastest descent up to τ=(z0−A(p_c))/R, and leaves a residual problem with state at most A(p_c). It preserves the initial state. The recovery cap and this projection preserve each other. When z0<RM, the forced high-power prefix lies below the recovery cap.

For numerical convex residual claims, τ must be an exact mesh breakpoint. Sampling b only at neighboring uniform nodes does not suffice because b has a convex kink. The provided uniform-mesh implementation rejects nonaligned τ; all forced-prefix residual tests use τ=.25 exactly. Arbitrary initial states require inserting τ or solving the residual separately.

## 4. Convexity restored by a tail-hazard condition

Assume μ has density f in (0,M), allowing endpoint atoms at 0 and M but no interior atoms or singular-continuous interior component. The M-atom terminal cost is zero on the recovery cone. The 0-atom contributes only fixed H(z0). On the residual critical domain,

G″=[−(p+c)s″s−3Ns′]/s⁵≥0,
H″=N/(Rs³)≤0.

The integrated density F(x,z)=S(x)G(z)+f(x)H(z) is convex if f/S≤G″/(−H″). A useful service-dependent sufficient constant is

κ=inf_{0<p<p_c} A(p) G″(A(p))/[−G′(A(p))],

with the no-root domain used when appropriate. The recovery cap implies z≤R(M−x), so the condition

h(x)(M−x)≤κ, h=f/S,                                      (2)

suffices. A curve may have κ<1 or even infimum zero. General concavity of s alone does not imply uniform-EOS convexity.

For s(p)=k p^β, 0<β<1, p_c=βc/(1−β), and

G″/(−H″)=R[2β+1/(1−r)]/[(1+β)z],
r=(1−β)p/(βc)∈[0,1).

Consequently κ_β=(1+2β)/(1+β), and (2) with this constant gives a strictly convex objective on the residual feasible domain. Uniform EOS has h(M−x)=1 and qualifies. The survival family S=(1−x/M)^α qualifies whenever α≤κ_β. Mixtures of a uniform law and an endpoint atom also qualify. Linear service β=1 gives κ=3/2 without a finite critical root.

The clipped Lipschitz set is compact. Extended-value lower semicontinuity and a finite-cost triangular/trapezoidal witness give existence. Strict convexity on positive-survival variable portions gives uniqueness of the reduced representative. Uniqueness is asserted only for the reduced representative; this proof does not establish uniqueness for the whole unreduced action class.

## 5. Sharpness and non-universal cases

For S=(1−x/M)^α, α>κ_β, choose γ∈(κ_β/α,1) and a feasible terminal portion z=γR(M−x). As x approaches M, p→0 and zG″/(−G′)→κ_β; meanwhile h z/R=αγ>κ_β. F″ is strictly negative on an open terminal interval. Small compact bumps in that interval preserve positivity, both caps and slew, giving a strict midpoint violation of the complete functional. The threshold is therefore sharp for convexity of this entire reduced path class. Failure of (2) does not say every such model has a nonconvex optimum or cannot be solved.

Interior EOS atoms create concave H(z(w)) point costs below p_c. Narrow feasible perturbations at an atom can defeat surrounding integral curvature. The independent review gives a full feasible midpoint witness. A separate smooth concave s(p)=.1p+1−exp(−p/.001), c=20, R=M=1 gives uniform-EOS nonconvexity inside both admissible envelopes; arbitrary concave service is not covered by the power-law conclusion.

These witnesses are distinct from the old unrestricted local Hessian example. The old statement “cycle costs can be nonconvex” remains true, but it does not rule out exact recovery-domain convexification in the admissible subclass.

## 6. Exact bridge reduction for finite atomic EOS

Let W take positive values w₁<…<w_n=M with masses π_i, w₀=0, and idle initial state. Apply both exact projections. For endpoint states a=z(w_i), b=z(w_{i+1}), slew gives |a−b|≤RΔ, Δ=w_{i+1}−w_i. Between EOS candidates, S_i=Pr(W>w_i) is constant and there are no terminal costs. Since G decreases on the retained domain, the optimal bridge is the pointwise maximal feasible profile

z*(x)=min{a+R(x−w_i), b+R(w_{i+1}−x), z_c}.

Let q=min{(a+b+RΔ)/2,z_c}. Its exact running integral is

K(a,b,Δ)=2H(q)−H(a)−H(b)
          +G(z_c) max{0,Δ−(2z_c−a−b)/R},                (3)

omitting the last term if no finite critical cap exists. The infinite-dimensional global problem is exactly the continuous-state Bellman chain with stage S_iK+π_{i+1}H(b), z₀=z_n=0 and the usual cones. This is a structural reduction; dynamic programming, stochastic work conditioning and current-speed states are established prior methods, including Xu–Melhem–Mossé 2007.

For deterministic W=M the theorem simplifies to z*=min{Rx,R(M−x),z_c}; the physical profile rises at R, optionally holds at critical power, then falls at −R and ends exactly at EOS with no burn.

## 7. Global lower/upper Bellman bounds, not local stationarity

A finite grid of exact endpoint states and feasible edges gives a globally optimal restricted feasible policy, hence an upper bound on the continuous optimum.

For node boxes [a_l,a_h] and [b_l,b_h], an edge can be feasible iff a_l≤b_h+RΔ and b_l≤a_h+RΔ. The maximal feasible pair is a*=min(a_h,b_h+RΔ), b*=min(b_h,a_h+RΔ). K is decreasing in either endpoint: K_a=[G(q)−G(a)]/R≤0, with the corresponding capped formula. H is increasing. Therefore

S_i K(a*,b*,Δ)+π_{i+1} H(b_l)

is a lower bound for every feasible transition between the boxes. Minimize these lower stage costs in a Bellman chain. Favorable active and terminal values need not coexist; inconsistent intermediate representatives only make this chain optimistic. It gives a valid lower bound on the continuous global problem. As maximum box width vanishes, compactness and continuity of K,H close the lower/upper gap. This claim does not require convexity.

All provided numeric bounds are ordinary floating evaluations of these analytic lower/upper constructions. They are not outward-rounded interval certificates. The reported finite-state primary uniform DP is likewise not itself a continuous lower bound; only the continuous dual or interval-box construction supplies that role.

## 8. Continuous dual and duration consequence

For an absolutely continuous test costate y, fixed endpoints z(0)=z0,z(M)=0, and pointwise interval L(x)≤z≤U(x),

D[y]=−y(0)z0+∫₀ᴹ min_{v∈[L,U]}[F(x,v)−y′(x)v]dx−R∫₀ᴹ|y(x)|dx

is a weak lower bound. Under the convex regime the pointwise minimum is globally found by its monotone derivative or an endpoint. Saved y and independent quadrature make the reported numerical gap reproducible. Quadrature order agreement is not a proof of directed rounding.

Finally T_cycle(w)=∫₀ʷ1/s(P(z))dx+P(z(w))/R has derivative [1+z′/R]/s≥0. Thus its worst supported value is at M in the extended-value sense (finiteness must be established separately); on the recovery cone that equals ∫₀ᴹ1/s(P(z))dx, a convex functional. However adding a hard deadline can invalidate the critical projection. This observation is not an unrestricted hard-deadline convexification theorem.

## 9. Genuinely global simple-policy baseline and matched cycle time

For idle/uniform EOS with M=k=1, a target policy has z(x)=min{Rx,q,R(1−x)}, q=A(p)≤R/2. Its full-cycle derivative with respect to q is

J′(q)=(1−2q/R)[G(q)/R+G′(q)/2].

The unique stationary target before critical solves

(1−β)p+(2/R)p^(β+1)(p+c)=βc,

and is capped by the reachable peak P(R/2). This monotone equation avoids a generic scalar optimizer becoming trapped in the flat range of unreachable target powers. Its exact expectation uses the actual knee points q/R and1−q/R, not a nodal chord approximation.

For an atomic law, enumerate all branch boundaries q=Rw_i and R(1−w_i) in the admissible interval. Between boundaries let m be the probability of middle EOS, C=∑middle π_iw_i+Pr(late EOS), D=m+2Pr(late EOS). Then J′=mG/R+(C−Dq/R)G′. After multiplication by a positive factor, its sign is that of

m(p+c)p^(β+1)/(βc−(1−β)p)+Dq−RC,

strictly increasing when m>0; the m=0 case is linear in q. All boundaries plus the at-most-one stationary root per interval give the global target-class optimum. The code uses the algebraically equivalent uncancelled derivative to avoid a zero denominator at critical.

For uniform EOS, expected target dynamic energy is increasing with target p. Its expected cycle duration has its unique minimum at p^(β+1)=βR/2. Therefore, to compare energy at a required mean cycle duration T, either T is below this entire target class’s minimum (report infeasible), or find the unique lower-power root T_target(p)=T on the decreasing branch. This gives the minimum-energy target policy among all target policies meeting T. Comparisons use the same slew, initial state, work law, and common sufficient physical/burn capacities. A weighted-objective improvement is not substituted for this matched-time energy calculation.

## 10. Scaling and separate energy/time domination

For s=kp^β and support M, power scale a=(RM/k)^(1/(1+β)), time scale a/R and energy scale a²/R leave the normalized full-cycle problem dependent on β, c/a, p0/a and the normalized work law. Parameter sweeps related by this scaling are not independent model evidence. The 12 primary settings have10 scaling-equivalence classes.

The recovery projection dominates dynamic energy and cycle duration separately, pathwise: from the first coupling state, every possible return waveform takes at least p/R time and p²/(2R) energy. It also decreases each EOS power, preserving EOS burn-power/energy caps. Thus this projection alone preserves existing hard cycle deadlines. The critical projection can violate such deadlines, which is why the combined general hard-deadline claim remains excluded.

The full-productivity replacement also dominates total dynamic energy and cycle duration pathwise, but earlier EOS can occur at higher power. It need not preserve an EOS-only burn cap; its enlarged-action-class lemma applies to the unbudgeted full-cycle contract unless that additional constraint is checked.
