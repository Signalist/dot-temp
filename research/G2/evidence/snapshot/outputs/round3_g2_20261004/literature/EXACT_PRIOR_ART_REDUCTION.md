# Exact prior art reductions for the G2 representation theorem

2026-10-04 UTC

## Conclusion

The inactive-band upper theorem, including its two-moment construction, at-most-2M switch count, and phase-error constant 1/8, reduces to classical perfect-spline and moment-recovery results. Its output and optimal-value upper bounds follow by a short Lipschitz transfer. The square-root accuracy exponent is not a defensible standalone novelty claim.

The amplitude-only lower theorem is not a consequence of ordinary Sobolev nonlinear widths. However, the m^-2 **optimal-value gap mechanism** already has an elementary exact linear-functional realization. The narrow unresolved contribution is the realization of that mechanism by positive, per-port equal-energy, common-clock workloads with a fixed pair of stable kernels, plus a uniform all-observation-time bound under the declared continuation and active band. This audit found no directly applicable prior theorem establishing that complete realization. That is a bounded literature finding, not a novelty certification.

An additional exact reduction is recorded in `FIXED_BAND_LINEARIZED_SWITCH_BOUND.md`: for the inactive-band linearized terminal problem, a fixed finite Fourier dictionary and fixed finite-dimensional LTI kernel imply a uniform finite switch bound, by L1 duality and the exponential-polynomial zero theorem of Aldaz, Kounchev and Render. The existing amplitude-only m^-2 lower does not establish an asymptotic lower for a fixed Fourier cutoff.

## Claims and precise status

| Candidate statement | Status after exact comparison | Remaining issue |
|---|---|---|
| Any local acceleration can be replaced with a two-switch bang control matching two moments | Direct algebraic identity with Scarinci–Veliov (3.14)–(3.15) | None for inactive state constraints |
| Hermite interpolation at M+1 nodes by a fixed-amplitude perfect spline with at most 2M switches | Direct Goodman–Lee Theorem 1 and Corollary 6 specialization | No first-derivative path constraint in that theorem |
| Clamped phase difference at most rho Delta²/8 | Direct scaling of Goodman–Lee's clamped degree-two special case | No independent constant novelty |
| Bandwidth-independent O(m^-2) terminal-output upper and O(epsilon^-1/2) representation | Elementary energy-primitive/Lipschitz corollary of trajectory compression | Useful model-specific formulation; no new approximation exponent |
| Five-arc active-band bridge and consequent peak upper | Not a direct corollary of the cited unconstrained spline results | State constraints require the separate clipping construction; historical exclusivity unproved |
| Ordinary nonlinear width lower implies this scalar value gap | Invalid inference | Different quantifiers; support functions see convex hulls |
| Arbitrary bounded m-jump acceleration suffers an m^-2 linear-functional value gap | Elementary exact oscillatory/BV construction below | Classical mechanism; not a novel complexity phenomenon |
| Fixed positive equal-energy workload family has nonlinear terminal m^-2 gap | Not directly reduced to a checked prior theorem | Must control every low-jump competitor, including large phase excursions |
| Same family has full-future peak gap | Not implied by terminal gap or widths | All-time low-jump bound, startup and continuing baseline, boundary cancellations |
| Fixed Fourier cutoff restores a finite exact switch count | Proved here as a classical corollary for the linearized inactive-band terminal problem | Does not automatically cover nonlinear composition or active state multipliers |

## 1 Direct upper reductions

### 1.1 The cell formula is the same two-moment recovery

[Scarinci and Veliov, Higher-order numerical scheme for linear quadratic problems with bang–bang controls](https://www.wu.ac.at/fileadmin/wu/d/i/statmath/Research_Seminar/WS_2017-18/veliov_paper1.pdf), 2018, DOI [10.1007/s10589-017-9948-z](https://doi.org/10.1007/s10589-017-9948-z): §3.2 (3.6) describes attainable pairs of moments; §3.3 (3.14) imposes their preservation and (3.15) recovers a three-arc control. Their Theorem 3.1 additionally assumes an LQ problem and switching-function growth; those optimizer-convergence assumptions are not needed for the moment formula alone.

Here is the literal algebraic substitution. On a cell of length Delta define

    alpha = -(1/Delta) integral a(s) ds,
    beta  = -(1/Delta²) integral s a(s) ds.

Apply their recovery to u=-a on the unit interval. Its positive interval has

    length = (1+alpha)/2,
    center = (1+2 beta)/(2(1+alpha)).

Multiplying by Delta and reversing sign gives a_hat=+1 outside a negative interval with

    q = (Delta - integral a)/2,
    center = (Delta²/2 - integral s a)/(2q).

These are exactly the candidate formulas. The degenerate alpha=-1 case is their constant control; the alpha=1 case is also covered. Moment preservation for the double integrator is exact, because its endpoint state depends on no higher control moments. A union of M negative intervals has at most 2M boundary points, so the global count follows without a join surcharge.

### 1.2 The global count and the constant are perfect-spline corollaries

[Goodman and Lee, Another extremal property of perfect splines](https://www.researchgate.net/publication/243060150_Another_extremal_property_of_perfect_splines), Proc. AMS 70 (1978), 129–135, [publisher DOI](https://doi.org/10.1090/S0002-9939-1978-0481760-9): Theorem 1 gives a fixed-amplitude Hermite interpolant with at most n interior knots for n+k data, together with two envelope splines. Corollary 6 handles the minimum attainable derivative norm. Their degree-k convention concerns the k-th derivative.

For the candidate choose k=2, repeat each of the M+1 mesh nodes twice, and prescribe phase and speed. There are 2M+2=n+2 data, hence n=2M. Let B be the minimum second-derivative norm among these interpolants. B<=rho because the original clock is feasible. If B<rho, select a feasible interpolant of norm strictly below rho and use Theorem 1 with A=rho. If B=rho, use Corollary 6. Thus the non-strict bound is already covered by the old theorem, with at most 2M knots and |theta_hat''|=rho a.e.

The same paper's (3.10)–(3.12), pp.134–135, specializes to clamped endpoint data and knots at zeros of a Chebyshev polynomial of the second kind. For k=n=2, affine rescaling to [0,Delta] gives knots Delta/4 and 3Delta/4. Integrating acceleration +A,-A,+A gives a maximum A Delta²/16. Apply this to f=theta_hat-theta, with f=f'=0 at both endpoints and |f''|<=2rho:

    ||f||_infinity <= rho Delta²/8.

This accounts for the numerical phase constant as well as the rate. The specified inactive-band promise then protects intermediate speeds; the cited theorem itself does not enforce a separate speed band.

### 1.3 Output and value transfer are one-way corollaries

For fixed final phase, the boundary terms cancel and the exact model identity is

    J_e(theta_hat)-J_e(theta)
      = sum_j integral h_j'(T-t)[E_j(theta_hat(t))-E_j(theta(t))] dt.

Since E_j is e_max,j-Lipschitz, this gives |Delta J|<=B||Delta theta||_infinity. Apply the trajectory upper to an arbitrarily near-optimal theta, then take its objective supremum. No existence of an attained optimizer, workload derivative bound, or new minimax theorem is required. For full trajectories retain the h_j(0) term. Identical post-service clocks and integrable kernel derivatives extend the bound to all future times. Finally, the absolute supremum norm is 1-Lipschitz.

These are useful consequences of the energy-per-work contract. They do not turn representation into an algorithm for finding the supplied near-optimal trajectory.

### 1.4 Why the active-band upper needs an additional argument

Goodman–Lee and the two-moment formula constrain theta'', not theta'. A cell with both endpoint speeds u and displacement u Delta has only the feasible velocity v=u. A pure bang acceleration cannot reproduce it while staying below u. Therefore inserting the old spline theorem unchanged is invalid.

The five-arc clipped construction supplies the missing path-feasible bridge. Once that bridge is proved, the same clamped difference bound and Lipschitz transfer apply. This audit has not found a checked prior result whose exact hypotheses directly supply its full five-arc statement. Clipped double-integrator reachability is nevertheless classical, so absence of an exact citation here is not positive evidence of historical novelty.

## 2 Why nonlinear widths do not prove the value lower

[DeVore, Howard and Micchelli, Optimal nonlinear approximation](https://gwern.net/doc/cs/algorithm/1989-devore.pdf), Manuscripta Mathematica 63 (1989), 469–478, [DOI](https://doi.org/10.1007/BF01171759): definitions (1.3)–(1.4) require a continuous parameter selection; Theorem 3.1 uses a Bernstein-width/Borsuk argument, and Theorems 4.2 and 5.1 establish the Sobolev nonlinear-width scale. The paper explicitly warns that unrestricted continuous one-parameter decoding can be space filling. The original scan was checked; its authors' bibliographic record is also available at [IBM Research](https://research.ibm.com/publications/optimal-nonlinear-approximation).

For the present comparison write K for feasible trajectories and S_m for feasible m-jump trajectories. Three different quantities must remain separate:

    continuous nonlinear width:
      inf_(encoder,decoder) sup_(theta in K)
          ||theta-decoder(encoder(theta))||,

    best representation error for a fixed class:
      d_m = sup_(theta in K) inf_(s in S_m) ||theta-s||,

    workload-optimal-value gap:
      G_m = sup_e [sup_(theta in K) J_e(theta)-sup_(s in S_m) J_e(s)].

A uniform B-Lipschitz objective gives G_m<=B d_m. It gives no reverse inequality. Further, the candidate does not require a continuous choice of a near-optimal clock as e varies. A width theorem with that requirement cannot silently be reinterpreted as a bound on all representation maps.

There is a stronger obstruction even for linear objectives. For a bounded closed convex K in a Banach space and S subset K, let C be the closed convex hull of S. Hahn–Banach separation gives

    sup_(||ell||<=1) [h_K(ell)-h_S(ell)]
      = sup_(x in K) dist(x,C).

This is a distance to C, not to S. For a square K and S its four vertices, every linear support value is exact while the center has a strictly positive distance to S. Thus even access to every linear functional does not convert an arbitrary norm-approximation lower into the desired value lower. Restricting the available functionals to physically realizable workloads makes the proposed implication weaker still. For nonlinear E(theta), there is not even a fixed linear-functional space on theta without changing to workload-dependent features.

## 3 An exact elementary value-gap mechanism already exists before the workload embedding

The following is a self-contained reduction, not an assertion that a searched paper states this exact normalization. It uses only integration by parts, bounded variation and pointwise maximization of a linear functional.

Let T=r=rho=1. Set eta=theta-t, impose eta=eta'=0 at 0 and 1, and |eta''|<=1. For integer N let k=2 pi N and

    L_N(eta) = -integral_0^1 cos(kt) eta(t) dt.

Two integrations by parts give

    L_N(eta) = k^-2 integral_0^1 a(t) cos(kt) dt.

The control a_N=sign(cos kt) has zero zeroth and first moments on each period. It is feasible, and it attains the pointwise upper bound:

    V_N^lin = 2/(pi k²) = 1/(2 pi³ N²).

For every arbitrary-amplitude piecewise-constant a in [-1,1] with at most m interior jumps, sin k=sin 0=0 and TV(a)<=2m yield

    |integral a cos(kt)dt| <= TV(a)/k <= 2m/k,
    V_N,m^lin <= 2m/k³.

Consequently, if m<=N,

    V_N^lin - V_N,m^lin >= 1/(4 pi³ N²).

For m>=1 choose N=m. This already proves an Omega(m^-2) value gap against arbitrary bounded constant-acceleration segments. Classical cell compression gives the matching upper. The construction's speed deviation is at most 1/(4N), so the same lower also holds on the fixed genuinely active band [.9,1.1] when N>=3. The optimal witness happens to lie in its interior.

This removes a possible overstatement: the response-value lower is not interesting merely because it is a scalar value lower rather than a trajectory lower. A simple freely chosen oscillatory linear functional already supplies it. What remains to justify is the constrained nonlinear workload realization and the all-time observation statement.

[Scarinci–Veliov §2, (2.3) and (2.6)](https://www.wu.ac.at/fileadmin/wu/d/i/statmath/Research_Seminar/WS_2017-18/veliov_paper1.pdf) is a direct optimal-control source for the sign-of-switching-function mechanism. [Caponigro et al., Regularization of chattering phenomena via bounded variation controls](https://arxiv.org/pdf/1303.5796), introduction and Theorems 1–2, studies value convergence under TV penalization and additional controllability assumptions. It therefore establishes close methodological precedent, but neither its quantifiers nor its conclusions give this workload-family lower. A single Fuller-type problem with infinitely accumulating switches is also different from a family indexed by N.

## 4 The exact obstruction to reducing the nonlinear terminal and peak statements

The candidate realizes an oscillatory cost by e1=1+D_N'/2 and e2=1-D_N'/2. A flat periodic primitive D_N guarantees positive bounded profiles and equal cycle energy; opposite port kernels remove the common load from the signed observation. This is a restriction on the permissible objectives, not a free choice of q(t).

At the high-switch witness eta_N=O(N^-2), a Taylor expansion transfers the linear oscillatory gain with an O(N^-3) remainder. That alone does not prove a value gap: low-jump competitors may have order-one phase excursions. A Taylor remainder with ||D_N''|| growing like N is not uniformly small over those competitors. Therefore the global inverse-phase/BV calculation is a substantive remaining step, not something supplied by the linearized lower.

For the full-future peak theorem the necessary quantifiers are

    some feasible high-switch clock and some observation time:
      |y| >= c N^-2,

    every feasible low-jump clock and every observation time tau>=0:
      |y| <= C(m+1) N^-3.

A terminal-only estimate only establishes the second line at tau=1 and cannot replace its all-time quantifier. The special assumptions h(0)=h'(0)=0, flat primitive at phase 0, integrable higher kernel derivatives, common zero initial state and common nominal continuation are what permit the candidate proof to control the other observations. The second integration boundary must be retained at arbitrary phase. A nonzero common homogeneous output can dominate the peak and remove the desired value gap.

No checked spline/width/TV theorem above simultaneously supplies these fixed-kernel, positive-profile, equal-energy and full-future quantifiers. Conversely, no broad claim about raw grid frequency, arbitrary initial states, fixed-bandwidth loads or all algorithms follows from this example.

## 5 Recommended manuscript scope

A supportable formulation is:

“Using classical moment-preserving spline compression, we derive bandwidth-independent second-order response bounds for continuously clocked energy-per-work loads. An explicit fixed two-port example shows that this rate cannot be improved uniformly over an amplitude-only workload class when the clock is represented by finitely many constant-acceleration segments. A separately proved all-time estimate extends the example to an absolute future-peak objective under a stated stable relative-degree-three observation and prescribed continuation.”

Avoid first/novel labels until a specialist prior-art review confirms the remaining realization claim. Cite the two-moment and perfect-spline sources at the upper theorem itself. Present the elementary linear-functional example as a baseline that narrows the alleged novelty, and use fixed-bandwidth tests to avoid attributing the asymptotic N~m difficulty to a workload class that excludes that sequence.

## 6 Search boundary and reproducibility

Primary full texts checked in this pass: Goodman–Lee Theorem 1, Corollary 6 and (3.10)–(3.12); Scarinci–Veliov §§2 and 3.2–3.3; DeVore–Howard–Micchelli definitions and width theorems; Cerf–Mariconda Theorem 3.1/Corollary 1/Remark 3.2; Aldaz–Kounchev–Render §2 Theorem 9; Caponigro et al. introduction and main theorem setting. Aronsson's 1979 publisher abstract was checked, but not a full theorem; it is not used to claim subsumption or exclusion. Its differential-expression minimax problem is only an adjacent lead: [official article](https://www.sciencedirect.com/science/article/pii/0021904579900042).

Searches included perfect/free-knot splines with linear functionals, nonlinear Sobolev widths, bounded-switch optimal-value approximation, and exponential-polynomial zero bounds. Results outside these precise targets were not treated as evidence. Unlocated matching statements and inaccessible complete texts remain uncertainty, not proof of absence. `PRIMARY_SOURCE_EXCERPTS.json` records verified URLs, theorem locations, short excerpts and applicability limits. `verify_reductions.py` checks the cell mapping and exact oscillatory normalizations; it is a consistency check, not a proof assistant.
