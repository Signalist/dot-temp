# G6 finite-resolution robustness and workload-contract novelty audit

Date: 2026-10-04. This is a targeted primary-source audit, not a proof of novelty. No new nonlinear runs, simulations, benchmarks, or external code executions were performed. Round-2 literature files and `theory_review/G6_STRUCTURAL_AND_COMPLEXITY_PROOFS.md` were read. The source ledger records exactly what was inspected and what remains inaccessible.

## Verdict

1. The rotation support series and rational folding are direct prior art. Adding a fixed uncertain parameter, a parameter mesh with a Lipschitz remainder, or a finite disagreement-language automaton does not by itself supply a new mathematical method.
2. The strongest new warning is a clean **representation-scope corollary**: arbitrarily small fixed common orientation uncertainty can create a genuinely circular active arc, destroying the known-angle logarithmic **unlifted planar** facet rate there. It follows from generic homogeneous-gauge geometry and classical polygon approximation, so should be presented as an elementary robustness consequence, not as a newly discovered approximation law.
3. A bounded sliding-window sign-disagreement contract is a standard weakly-hard/regular-language restriction. For the single-window count contract, an exact totally unimodular LP/min-cost-flow formulation is stronger than generic suffix-state DP; see `G6_SLIDING_WINDOW_LP_ADDENDUM.md`. Workload interpretation and a useful electrical certificate may be valuable, but do not establish theorem novelty without a further sharp result.
4. The earlier arithmetic iff theorem and static-cohort masking threshold remain narrower potentially original claims, with the same unresolved literature gaps. None of the new sources supplies their complete statements. This bounded audit cannot certify that no source does.

## 1. Direct support-series reduction

For `F_theta(a)=sum_{k>=0} r^k |a_1 cos(k theta)-a_2 sin(k theta)|`, write `a=||a||(cos alpha,sin alpha)`. Then `F_theta(a)/||a||=sum r^k |cos(alpha+k theta)|`. Duda's equation (14) is this family after reciprocal contraction notation, scaling and an index/angle shift; equation (15) is the rational-angle grouping. Section 3 also gives the contracting support recursion. These are exact reductions, not merely similar titles. [Duda, equations (14)–(15), PDF pp. 7–9](https://arxiv.org/pdf/0710.3863).

The support formula, ordinary geometric tail, and rational-versus-irrational exact polygon distinction must therefore be background. A sharp lower bound for the **minimum** number of pieces at a prescribed error is a different proposition; identifying a logarithmic truncation algorithm alone does not establish that lower bound.

## 2. Fixed parameter versus refreshed uncertainty

For one unknown parameter `kappa` held fixed for a trajectory, retain it in the reachability recursion:

`H_{n+1,j}(d;kappa)=max_{e:i->j}{h_{W_e(kappa)}(d)+H_{n,i}(A_e(kappa)^T d;kappa)}`.

Only after this conditional calculation take `sup_kappa`. This is the exact support recursion for reachable endpoints from the specified initial automaton nodes, with independent admissible disturbances conditional on each edge. Taking `sup_kappa` at each recurrence call instead allows new parameter values along one history. The latter generally enlarges the trajectory set. Also, `union_kappa R_kappa` need not be invariant under every `A(kappa)`; it represents parameter-correlated fibers, not a single common RPI set. Augmenting by `kappa^+=kappa` preserves the semantics, but that coordinate is neutral, so the whole augmented state is not uniformly contracting.

This distinction is established reachability methodology. The primary manuscript by Huang–Luo–Bak–Sun explicitly separates constant-parameter Algorithm 1 from time-varying-parameter Algorithm 2; Section 5.1 changes the transition enclosure for the latter. Its dependent-factor identifiers preserve parameter dependence. These are closer deterministic neighbors than robust-MDP rectangularity analogies. [Primary manuscript, §§2–5](https://arxiv.org/html/2406.11056).

**Novelty judgment:** retaining a shared fixed parameter is necessary correctness, not a standalone contribution. A result about an exact invariant family or its sharp uniform representation complexity could add something, but must not compare against an unnecessarily refreshed-parameter baseline as though both solve the same problem.

## 3. Finite tolerance in the rotation angle theta

The following are direct estimates, included to identify the finite-resolution baseline. For fixed `r<1`,

`|F_theta(a)-F_psi(a)| <= ||a|| |theta-psi| r/(1-r)^2`.

Indeed, rotation directions at lag `k` differ by at most `k|theta-psi|`, and `sum k r^k=r/(1-r)^2`. On a bounded capacity set `||a||<=B`, let a grid in a compact angle interval have covering radius `h`, and let `F_N` retain the first `N` terms. Then

`max_grid F_N <= sup_theta F_theta <= max_grid F_N + B[r^N/(1-r)+h r/(1-r)^2]`.

The same proof works for the support of each dynamic-amplitude uncertainty set using its radius. No arithmetic classification is needed. These are ordinary contraction/sensitivity bounds; constants deteriorate as `r` approaches one. They are not an output-optimal representation theorem.

Angular continuity is itself prior art: Vass, Theorem 2.4, proves continuity of an IFS attractor with respect to its rotation angles, and explicitly uses rational-angle attractors to approximate irrational ones. [Vass, Theorem 2.4, PDF p. 10](https://arxiv.org/pdf/1502.03788).

**Scope correction:** exact rationality and infinite exponential approximation type cannot be inferred from a finite-width experimental angle interval. The known-angle arithmetic theorem is not a uniform theorem for `sup_theta F_theta`. Conversely, angle uncertainty alone has not here been proved to create a circular arc; the orientation construction below is different.

## 4. Small common orientation uncertainty: correct but generic circular-arc corollary

Let `F` be any continuous positive homogeneous gauge, `I=[phi_0-delta,phi_0+delta]`, and

`G_I(a)=sup_{phi in I} F(R_phi a)`, `M=max_{||v||=1}F(v)`.

If `F(v_*)=M` and `arg(v_*)-arg(a) in I` modulo the relevant period, then `G_I(a)=M||a||`: the aligned rotation attains the global maximum and no rotation exceeds it. Consequently `{G_I<=1}` has a circle of radius `1/M` on every open angular interval satisfying that alignment. In the G6 positive capacity cone, the alignment interval must intersect the cone with nonempty interior. A preassigned `phi_0` and a preassigned slope interval need not do so. To demonstrate fragility, choosing an admissible alignment is enough; a universal claim for every location is false without this condition.

This is also the ordinary robust-set identity `{G_I<=1}=intersection_{phi in I} R_{-phi}{F<=1}`. The result holds for a polygon gauge too; dense irrational kinks are not the cause. For a fixed nonzero uncertainty width and a compact nontrivial slope interval `J` inside the arc, the gauge is `g(t)=M sqrt(1+t^2)`. Its second derivative is positive and bounded above/below on `J`. If an `m`-piece affine approximation has error `epsilon`, one of its pieces has length at least `|J|/m`; the centered second difference gives

`epsilon >= min_J g'' * |J|^2/(16m^2)`.

Uniform chord interpolation gives the matching `O(m^-2)` upper error and a safe upper gauge. Thus direct planar facet/piece complexity is `Theta(epsilon^-1/2)` on that arc. Local radial error has the same order because the gauge is bounded away from zero. This is an elementary curvature argument. Rote's primary paper, Corollaries 1–2 and §5, supplies the mature `O(m^-2)` sandwich/polygon baseline and discusses circle/parabola sharpness. [Rote, 1992](https://page.mi.fu-berlin.de/rote/Papers/pdf/The%2Bconvergence%2Brate%2Bof%2Bthe%2BSandwich%2Balgorithm%2Bfor%2Bapproximating%2Bconvex%2Bfunctions.pdf). The more general classical inscribed-polytope upper theorem is in [Bronshtein–Ivanov, 1975, p. 1110](https://m.mathnet.ru/php/getFT.phtml?jrnid=smj&option_lang=eng&paperid=4199&what=fullt).

**Essential limitation:** this is not a general certificate-size barrier. The circular-arc gauge has an exact SOC representation. Ben-Tal–Nemirovski give lifted LP approximations of SOC constraints with logarithmic dependence on inverse accuracy at fixed dimension. An inner approximation follows by the corresponding safety scaling. [Publisher's explicit complexity statement, 2001](https://pubsonline.informs.org/doi/10.1287/moor.26.2.193.10561). Nor does the local arc identify the complexity of the rest of the robust envelope. If `delta` shrinks jointly with `epsilon`, the fixed-arc asymptotic constants also change.

**Novelty judgment:** retain as a useful robustness counterexample/corollary that sharply limits the engineering interpretation of the arithmetic theorem. Do not promote it to new general robust-optimization or convex-approximation theory.

## 5. Sign-disagreement contracts and exact support DP

Suppose full-amplitude signs are `s_1,s_2 in {+1,-1}`. Set `d_k=s_{1,k}s_{2,k}` and retain a freely chosen common sign. At lag `k`, after optimizing that sign, the reward is

`w_k(d;a)=r^k |a_1 cos(k theta)-d a_2 sin(k theta)|`.

Any allowed binary language for `d` therefore gives a constrained path maximum of a sum of known rewards. A budget of at most `B` disagreements in every sliding window of length `L` is the familiar binary weakly-hard condition “at least `L-B` successes in every `L` events.” Store the recent suffix (or a minimized equivalent state) and perform longest-path DP through `N` layers. With free common signs, endpoint support is exact. For dynamic optional amplitudes replace the absolute projection by the corresponding box/symmetric-box support; do not silently reuse full-amplitude rewards.

This contract language is directly prior art: Xu et al. build its automaton in §5.1 and a product scheduler automaton in §5.2. Their task is safe weakly-hard contract/schedule synthesis. [ASP-DAC 2023, author PDF](https://bineet.cs.ua.edu/files/ASP_DAC_2023.pdf). Hobbs et al. subsequently combine weakly-hard constraints with reachability-based deviation bounds and quantitative co-synthesis. [ICCPS 2024, §III and Appendix B](https://bineet.cs.ua.edu/files/ICCPS2024.pdf).

The general dynamical reduction is already captured by graph-constrained affine reachability. Athanasopoulos–Smpoukis–Jungers give the set recursion, invariant multisets, and explicit geometric-tail iteration count in Theorem 1(ii); Proposition 3 supplies the convex version. Their main assumptions include C-set disturbances and strong connectivity, which singleton signed inputs and lifetime-budget automata may violate. For such special cases use a direct contraction/tail proof rather than quoting all their invariant-set conclusions verbatim. [2017, §§2–3](https://arxiv.org/html/1702.00598).

Three distinctions are mandatory:

- **Lag phase:** for irrational `theta/pi`, rewards vary with lag; an automaton for the workload does not magically make the entire exact Bellman equation finite-state. Use nonstationary finite-horizon DP plus the tail, or keep direction as a continuous argument. Rational rotation allows a finite phase-product graph. Classical discounted weighted automata then apply directly; Chatterjee–Doyen–Henzinger's Theorem 3 treats quantitative emptiness/optimization. [Submitted primary manuscript, pp. 5–7](https://research-explorer.ista.ac.at/download/3862/5230/IST-2012-57-v1%2B1_Quantitative_languages.pdf).
- **Words and starts:** finite-history endpoint maximization reads chronological words with reversed lag weights; a stationary past-word formulation uses the reversed language and correct eligible terminal nodes. Truncation plus a geometric tail is valid for extendable histories. A specified startup node and startup transient must still be checked.
- **Contract type:** a lifetime disagreement budget uses a finite counter; a sliding-window budget uses finite suffix memory. A mere asymptotic disagreement fraction permits any finite bad prefix followed by agreement forever. Consequently that last contract gives exactly the unrestricted finite-time robust reachable set, regardless of how small the asymptotic disagreement bound is. Expected correlation likewise does not alone forbid dangerous finite words. A prefix-density constraint is different again and need not admit a finite-state counter without an extra bounded-debt condition.

**Stronger baseline:** for a single sliding-window disagreement budget, the additive finite-horizon support optimization has an exact TU LP and an O(N)-size interval-scheduling min-cost-flow network. Exponential suffix-state DP is unnecessary; see `G6_SLIDING_WINDOW_LP_ADDENDUM.md` for the reduction, primary sources and horizon-boundary qualifications.

**Novelty judgment:** ordinary automaton encoding, product construction, support DP, sliding-window TU/flow optimization and discounted tail are baseline. A sharper result would need, for example, a proved minimal-contract/capacity characterization or output-sensitive complexity beyond these generic reductions, with the same information, startup, work, parameter and fallback semantics.

## 6. Access gaps and claim language

The 2012 Mishkinis–Gentil–Lanquetin–Sokolov IFS approximation paper remains **abstract/snippet-only** from round 2. Its blocked HAL/fulltext routes were not retried or bypassed. No statement here excludes an unseen theorem in that paper. Martyn 2009 remains a lead, not a full-text exclusion. A newly attempted publisher route for the 2025 parametric-reachability article returned 403; the separately public arXiv author manuscript is the evidence used, not the inaccessible publisher text.

Safe summary: “The support framework and finite-language/sensitivity machinery are established. We isolate a narrow arithmetic representation theorem and an elementary but consequential orientation-robustness corollary; their precise scope is direct planar approximation, and the separate arithmetic novelty check remains provisional.”
