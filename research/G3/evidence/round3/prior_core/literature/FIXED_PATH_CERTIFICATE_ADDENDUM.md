# Fixed-path and energy-tight service certificates: adversarial novelty addendum

2026-10-03 UTC. The parent changed the theorem route during the audit. The assessed candidate now fixes a P/Q/current/compute path, eliminates electrical dynamics exactly, and certifies buffer-charge admission in a moving corridor. This differs materially from optimizing freely over a purported exact convex electrical lift.

## Updated verdict

**No directly matching full theorem was located, but most proposed mathematical ingredients are mature.** The plausible residual contribution is a carefully scoped exact lag/ramp charge-cell characterization embedded in the physical converter corridor, with same-parameter constructive recovery and a consequence that changes service admission. The O(h²)/O(h⁴) orders and cubic SOCP representation should not be the headline novelty.

The subsequent energy-tight inequality-contract bridge was also audited. It legitimately extends the fixed-path admission quantifier to every allocation allowed by a narrowly specified zero-slack service envelope. Its rigidity and small-slack interpolation ingredients are classical. The additional plausible contribution is their explicit coupling to inductive-energy release and a controller-independent DC-underenergy exclusion, subject to the limitations recorded below.

## Narrow primary threats

### N01. Johnson–Hauser 2012: exact endpoint/corridor reachability

Jeff Johnson and Kris Hauser, “Optimal Acceleration-Bounded Trajectory Planning in Dynamic Environments Along a Specified Path,” ICRA **2012**, DOI 10.1109/ICRA.2012.6225233. [Author-hosted primary paper](https://motion.cs.illinois.edu/papers/ICRA2012-Johnson-optimal.pdf).

Section III gives endpoint-constrained velocity interval propagation for bounded-acceleration paths. Section IV and Theorem 1 prove the exact set of terminal velocities through path-time channels, using upper/lower feasible trajectories and convex combinations. Theorem 2 identifies an exact minimum-time endpoint result, with backward reconstruction described in Section V.

Under C ↔ position, b ↔ velocity, and b′ ↔ acceleration, this is a substantive antecedent for the pure-ramp moving-corridor limit of the proposed result. The paper's conclusion explicitly identifies velocity/history-dependent acceleration as an extension, so it does not itself settle the combined lag/ramp case. A claim to first exact corridor reachability or first constructive endpoint-preserving envelope is untenable; a particular converter/lag extension may be defensible.

### N02. Pham–Pham 2017/2018: forward/backward intervals and intersample error

Hung Pham and Quang-Cuong Pham, “A New Approach to Time-Optimal Path Parameterization Based on Reachability Analysis,” initial arXiv submission **23 July 2017**; IEEE TRO 34(3), 645–659, **2018**, DOI 10.1109/TRO.2018.2819195. [Primary full text](https://arxiv.org/html/1707.07239v2), [institutional journal copy](https://dr.ntu.edu.sg/bitstream/10356/105499/1/A%20New%20Approach%20to%20Time-Optimal.pdf).

Section III recursively computes reachable/controllable intervals under path-dependent affine state-control constraints. Section II-C and Appendix D distinguish O(h) collocation constraint error from O(h²) first-order-interpolation constraint error. Section IV also analyzes optimality and vanishing suboptimality around switching cases.

This directly threatens an abstract contribution framed as “state-dependent bounds plus interval reachability and second-order intersample accuracy.” It does not give the same exact cell charge moment, converter modulation floor, buffer inventory, or task service. The difference must be specified at the level of dynamics, constrained moment set, and preserved endpoints.

### N03. Xia–Alizadeh 2015: exact cubic nonnegativity SOCP

Yu Xia and Farid Alizadeh, “Second-Order Cone Programming for P-Spline Simulation Metamodeling,” manuscript dated **26 April 2015**. [Primary manuscript](https://optimization-online.org/wp-content/uploads/2015/06/4966.pdf).

Section 2 applies the Markov–Lukács interval representation to nonnegative cubics; Section 4 explicitly converts the two 2×2 positive-semidefinite Gram constraints into rotated second-order cones. This is an exact conic representation, unlike requiring all Bernstein coefficients to be nonnegative.

Therefore “exact continuous-interval cubic inequalities can be solved as SOCP” is established. Applying those constraints to electrical-energy and actuator polynomials is legitimate but is not a new convexity theorem by itself. Its utility is that no intermediate-time sampling is needed for the polynomial inner witness.

### N04. Al Taha–Bitar 2024: exact energy-profile reformulation

Feras Al Taha and Eilyan Bitar, “When are Lossy Energy Storage Optimization Models Convex?”, arXiv:2403.14010, **20 March 2024**. [Primary metadata](https://arxiv.org/abs/2403.14010), [author manuscript](https://bitar.engineering.cornell.edu/papers/AlTahaSubmitted2024.pdf).

Theorem 1 constructs an invertible piecewise-affine power-to-energy mapping. Theorem 2 gives an exact convex polytope of feasible energy profiles. Theorem 3 adds sufficient objective monotonicity conditions for a convex optimization problem after substitution.

This is particularly important when positioning exact charge-coordinate admission. It already distinguishes an exact feasible energy domain from potentially nonconvex feasible power profiles. Its standard storage dynamics lack the G3 lag/ramp mixed constraint, converter inductive energy, modulation floor, and workload contract. Do not claim energy-domain exactness as a general discovery.

### N05. Baier–Lempio 1994: second-order reachable-set approximation

Robert Baier and Frank Lempio, “Approximating Reachable Sets by Extrapolation Methods,” **1994**. [Primary institutional record](https://epub.uni-bayreuth.de/id/eprint/5434/).

The paper gives Hausdorff convergence orders for set-valued integral approximations and applies them to linear differential-inclusion reachable sets; at least second order holds for broad classes, with higher orders under extra smoothness. This is a secondary structural comparison: second-order set convergence alone is not new, but it is not a direct collision with a state-constrained exact-cell plus polynomial-inner sandwich. The record/abstract, rather than every proof detail, was inspected.

## Mathematical reductions that sharpen the contribution claim

These are original audit deductions, not claims attributed to the sources.

### 1. The density construction is cubic Hermite interpolation

Let C′=b. On each cell, a quadratic b_h matching b at both endpoints and matching the cell integral produces a cubic C_h satisfying C_h(t_k)=C(t_k), C_h(t_{k+1})=C(t_{k+1}), and C_h′ at each endpoint equal to C′. It is exactly the ordinary cubic Hermite interpolant of C.

Thus under b∈W^{3,∞}, the inventory error O(h⁴), power error O(h³), and slope error O(h²) are the standard Hermite derivative hierarchy. Exact cell integral matching prevents accumulation of the inventory error across cells, but that is inherent in this Hermite construction. It is a useful implementation theorem; its approximation order alone is weak novelty.

Event alignment matters: if b′ or higher derivatives jump at actuator switching or service events, the smooth-cell hypothesis must be stated and enforced. An unknown switching point cannot silently be treated as a known knot for a causal online claim.

### 2. The actuator class has a constrained-double-integrator interpretation

Within the admissible invariant range of b, the proposed saturated-lag admissible derivative interval can be represented by linear inequalities in b and v=b′: derivative limits plus a command strip for b+τv. Then C′=b, b′=v is a double integrator with a polyhedral mixed state-control constraint. This identifies classical constrained reachability and path-velocity planning as the appropriate comparison class, rather than only battery scheduling.

Check the invariant-range condition carefully. If b starts outside the command range, merely intersecting |v|≤R with a command strip need not represent a clipped lag at all states. State precisely the reachable initial-state domain on which the equivalence is exact.

### 3. Pure-lag closed forms are a two-dimensional LTI moment set

Without the derivative cap, (C,b) is a two-state linear system with bounded input. Endpoint and integral constraints are two linear moments of that input. Bang-bang boundary controls and exponential/logarithmic inversion are consequently expected from classical bounded-input reachability, even if no directly matching formula was found in this search.

An exponential-cone encoding may be useful and compact; its novelty should be evaluated as an explicit representation for this contracted problem, not as discovery of bang-bang optimality or convex reachability. Distinguish a new formula from a new mechanism.

### 4. Necessary energy accounting is essential but elementary

If both fast electrical energy and buffer inventory must recover, then total imported electrical energy must cover compute consumption and losses. A zero-net-import-perturbation service cannot restore both stores when it adds positive dissipation and there is no compensating compute reduction or loss offset elsewhere. Pure reactive service ordinarily changes copper losses. This is a required contract correction, not independently high-novelty physics.

Similarly, an inadmissible modulation value at service onset cannot be repaired by arbitrary later buffer capacity. The stronger scientific target is how the trajectory-dependent modulation energy floor competes with the buffer corridor and task completion over a nonzero interval, yielding a certified and consequential active-constraint switch.

## Residual claim that may survive

A defensible candidate claim is: for a specified grid-import P/Q trajectory and compute-energy/task contract, derive an exact charge-corridor equivalence and exact lag/ramp cell moment constraints; combine a controller-independent outer test with a continuously feasible, inventory-restoring polynomial inner test using the same physical parameters; give explicit state/actuator margins and demonstrate a nontrivial modulation-versus-buffer/recovery constraint switch that simpler energy/ramp/capability tests miss.

This must be described as a specialized certificate result unless further evidence establishes a broader theorem. A quantitative amplitude/admission-value gap needs transversality/regularity linking constraint slack to the amplitude parameter. State-tube O(h²) does not by itself prove admission-value O(h²), and a finite numerical gap is not a convergence theorem.

## Search outcome and limits

Targeted searches covered endpoint reachability, bounded-acceleration trajectory channels, damped-double-integrator control, rate-limited lag, constrained spline approximation, integral-preserving quadratic histopolation, exact cubic nonnegativity, storage energy-profile convexity, and reachable-set error orders. The exact full lag/ramp (b0,b1,∫b) plus physical converter corridor construction was not located. This is a bounded negative finding and warrants further specialist review before a first-of-kind claim.

## Extension for the energy-tight service-envelope bridge

Audited against Section 6 of `theory/EXACT_PORT_CONTRACT_THEORY.md` as available on 2026-10-03 at 08:58 UTC. The new contract allows any import-only allocation 0≤P≤Pbar, Q≥Qmin≥0, with fixed continuing workload, ideal buffer, constant grid voltage, positive copper resistance, and common initial/final electrical energy, buffer inventory, and current. This is a change in the theorem's quantifier, not permission to replace compute consumption by exported battery power.

### B01. Sz.-Nagy 1941: the exact interpolation ingredient and tent limit

Béla v. Sz.-Nagy, “Über Integralungleichungen zwischen einer Funktion und ihrer Ableitung,” Acta Sci. Math. 10, 64–74. [Original paper](https://acta.bibl.u-szeged.hu/13524/1/math_010_064-074.pdf). The journal's [publication list, item 23](https://acta.hu/download.phtml?id=2490) dates it **1941**; the [repository record](https://acta.bibl.u-szeged.hu/13524/) labels the volume item **1943**. Both precede the cutoff; the article records receipt on 4 December 1940.

Equation (1), p. 64, is a sharp function/derivative integral inequality, with extremizers given on p. 65. Its derivative-norm exponent p→∞ yields, for zero-extended compactly supported Lipschitz y,

    ||y||∞^(a+1) ≤ ((a+1)/2) ||y′||∞ ∫|y|^a.

The limiting extremizer is a tent. Setting a=1 or a=2 gives exactly the proposed square-root or cube-root amplitude exponents, including constants. These endpoint deductions are direct historical threats to claiming new exponents or a new triangular construction. Finite-horizon zero extension preserves Lipschitz regularity when both endpoint values vanish.

### B02. Willems 1972: endpoint cancellation and supply accounting

Jan C. Willems, “Dissipative Dynamical Systems, Part I: General Theory,” Archive for Rational Mechanics and Analysis 45, 321–351, **January 1972**. [Author-hosted original](https://homes.esat.kuleuven.be/~sistawww/smc/jwillems/Articles/JournalArticles/1972.1.pdf), [publisher](https://doi.org/10.1007/BF00276493).

Definition 2 gives the storage/supply inequality. Returning to the same state cancels the storage difference and constrains integrated supply. Theorem 1 characterizes dissipativity by finite available storage; Theorem 2 supplies the complementary required-supply bound. This is foundational ancestry for endpoint energy cancellation, not a statement of this rectifier's unique P/Q path. The latter follows only after establishing the model's nonnegative strict supply gap.

### B03. Faulwasser–Korda–Jones–Bonvin 2015/2017: integral coercivity and trajectory concentration

“On Turnpike and Dissipativity Properties of Continuous-Time Optimal Control Problems,” initial preprint **24 September 2015**; Automatica 81, 297–304, **July 2017**. [Version history](https://arxiv.org/abs/1509.07315), [primary v2](https://arxiv.org/pdf/1509.07315v2).

Definition 3, Eq. (12b), in the inspected v2 subtracts a coercive deviation penalty from the supply rate. Theorem 2's proof bounds its trajectory integral, then the measure of time spent away from the reference. Its hypotheses include strict dissipativity along optimal trajectories, bounded storage, and exponential reachability.

The G3 estimate ε≥μ∫δP is the same integral-coercivity mechanism with an explicit linear penalty and exact energy cancellation. Unlike that optimal-trajectory result, G3's pointwise algebra can apply to every feasible allocation, including a time-varying reference. This is a useful specialization; do not describe the abstract mechanism as new or import the turnpike theorem while dropping its hypotheses.

### B04. Burke–Ferris 1993: linear gap-to-distance error bounds

James V. Burke and Michael C. Ferris, “Weak Sharp Minima in Mathematical Programming,” SIAM Journal on Control and Optimization 31(5), 1340–1359, **September 1993**. [Author-hosted journal paper](https://sites.math.washington.edu/~burke/papers/reprints/19-WSM-burke-ferris.pdf), [publisher](https://epubs.siam.org/doi/10.1137/0331063).

The opening definition bounds distance to the minimizer set by the objective gap. Theorem 2.2 gives derivative/subdifferential characterizations, with equivalences under convexity. The scalar nonnegative deficit function μδ+cδ²≥μδ is an elementary sharp-minimum instance; at μ=0 only quadratic growth remains. This finite-dimensional work is conceptual ancestry for the linear gap and its degeneration, not a theorem directly covering G3's trajectory space.

### B05. Chaudhary–Benidris–Mitra 2026: the lossless load-envelope precursor

“Large-Load Demand Flexibility as Virtual Storage,” arXiv:2607.04564v1, **6 July 2026**. [Primary paper](https://arxiv.org/html/2607.04564v1).

Section II-C, Eqs. (5)–(9), introduces nonnegative curtailment δ=pbar−p and converts a throughput energy window into an exact curtailment budget. Section III-A, Eqs. (13)–(14), proves equivalence to a charge-only virtual-storage accounting trajectory. Zero available curtailment budget immediately forces the rated-load path; that is a corollary of its displayed constraints, not a separately claimed theorem.

The base model has energy-window coupling only and explicitly places detailed service/rebound physics outside that abstraction. It lacks converter copper loss, inductor energy, AC P/Q, and modulation dynamics. Thus it threatens generic load-envelope saturation claims, while leaving the new physical bridge open. Its accounting “storage” must not be mistaken for the G3 physical buffer or a task-completion model.

### B06. Guthrie–Mallada 2020: import-only dynamic loading with conic feasibility and periodic endpoints

James Guthrie and Enrique Mallada, “Minimum-Time Charging of Energy Storage in Microgrids via Approximate Conic Relaxation,” ECC, **12–15 May 2020**, DOI 10.23919/ECC51009.2020.9143992. [Author-hosted proceedings paper](https://guthriejd1.github.io/files/ecc2020.pdf).

Theorem 1 states feasibility equivalence of its discrete source/load formulation and SOCP, with a suboptimal surrogate objective. Section IV imposes periodic physical voltage/current, continuing constant-power load, positive/import-only power, and current/voltage rate bounds while charging a pulsed-load energy bank. Its controller-integrator state need not recover. Section III explicitly links finite-horizon energy maximization to economic MPC and dissipativity.

This is a close comparator for dynamic import, continuing load, endpoint return, and conic optimization. It does not establish the G3 AC P/Q-envelope rigidity, exact continuous-time lag/ramp charge cells, or polynomial intersample certificate. Its energy objective approximation must not be described as globally exact optimal charging or an exact continuous-time viable set.

### B07. Deakin et al. 2017/2018: loss-induced nonmonotonic power transfer

Matthew Deakin, Thomas Morstyn, Dimitra Apostolopoulou, and Malcolm McCulloch, “Loss Induced Maximum Power Transfer in Distribution Networks,” preprint **21 October 2017**, submitted to PSCC 2018. [Primary metadata](https://arxiv.org/abs/1710.07787), [primary paper](https://arxiv.org/pdf/1710.07787v1).

Theorem 1, Eqs. (20)–(24), distinguishes thermal and marginal-loss-induced transfer limits under voltage/current constraints; beyond the latter, extra generation causes a larger loss increase than useful transfer. This is a static distribution-generation result, with different signs and no workload or recovery dynamics. It nevertheless prevents presenting loss-induced nonmonotonicity, or a marginal-loss vertex, as new physics. G3's P−cP² vertex is its especially simple fixed-voltage version.

## Bridge deductions and claim boundaries

These deductions concern the proposed G3 model and are not attributed as electrical theorems to the papers above.

Write δ=Pbar−P≥0 and η=Q−Qmin≥0. Exact algebra gives

    net(Pbar,Qmin)−net(P,Q)
      =(1−2cPbar)δ+cδ²+2cQminη+cη².

With c>0 and Pbar≤Pmax<1/(2c), full terminal recovery gives

    ε ≥ μ∫δ+c∫δ²+c∫η²,    μ=1−2cPmax>0.

At ε=0 every nonnegative term vanishes, so P=Pbar and Q=Qmin almost everywhere. This validates applying the exact fixed-path corridor to *all* allocations allowed by this energy-tight envelope. It does not solve free P/Q optimization for positive slack, variable workload scheduling, or a contract whose terminal energy differs. A prescribed nonzero total-energy increment must be subtracted in the slack definition. If c=0, Q rigidity fails; if Qmin<0, the required square monotonicity fails.

For K-Lipschitz δ with δ(0)=δ(T)=0, a maximum H forces a full tent underneath δ. The stronger scalar estimate is

    ε ≥ μ H²/K + 2c H³/(3K).

Consequently H≤sqrt(Kε/μ) is a valid simple bound and its exponent is asymptotically sharp as ε→0 when μ>0. It is not exactly attained at positive c,ε. At μ=0 the scalar estimate becomes H≤(3Kε/(2c))^(1/3); zero-slack rigidity still holds. With only one zero endpoint, half-tent constants replace the full-tent constants. The K used for an all-allocation claim must uniformly follow from the physical current/DC/modulation limits and the envelope's Lipschitz constant.

The physical transfer is more informative than the interpolation lemma. With common initial current, the difference of unbuffered DC-energy offsets is

    Aactual−Abar=−G+k(Pbar²−P²+Qmin²−Q²)
                 ≤2kPmax H,    0≤G≤ε.

Combining this with any valid same-contract upper reachable buffer-charge envelope gives a controller-independent DC-underenergy exclusion. This captures a possible O(sqrt(ε)) transient benefit from releasing inductive energy even when the total energy slack is only ε. The theory's compensation-tail construction is a plausible route to demonstrating exponent sharpness within the physical model; an explicit family satisfying current, modulation, DC, buffer, endpoint and fixed-workload constraints is needed for physical sharpness, beyond sharpness of the scalar tent inequality. Exact leading constants require additional matching assumptions.

There is deliberately no analogous pointwise modulation-robustness claim. Shrinking tents have amplitude and area tending to zero while their derivative supremum remains K. Since the modulation floor depends on current derivatives, neither the L1 nor amplitude estimate makes that floor uniformly close. Weak/integrated witnesses or stronger derivative regularity would be needed.

Finally, the power-loss vertex is far outside the declared device's nominal operating range. It is a mathematical boundary of the stated hypotheses, not evidence of a newly observed converter regime. Above the vertex, equal net delivery at distinct nonnegative P values already defeats strict rigidity.

## Revised residual contribution

The full package remains a candidate specialized contribution: exact lag/ramp charge-cell certificates for the physical moving corridor, continuous-time constructive recovery under a continuing-workload contract, and an energy-tight envelope bridge that explains exactly when a fixed-path test is globally valid across allowed P/Q allocations and how much small positive slack can repair a DC-energy shortage. This bounded search found no complete direct predecessor. It did find direct antecedents for the rigidity mechanism, the interpolation exponents and extremizers, periodic dynamic-load conic feasibility, and loss-induced nonmonotonicity. These findings do not establish publication-level novelty or paper readiness.
