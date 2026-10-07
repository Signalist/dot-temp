# Skeptical mathematical audit: finite jerk, workload regularity, and coherent kernels

Date: 2026-10-04 UTC

## Verdict

**The repaired, explicitly scoped mathematical results pass this audit.** I found no counterexample to the fixed-kernel full-future representation gap, the moment-saturation construction, the bounded-slope upper, the amplitude-rescaled bounded-slope matching lower, or the coherent-kernel post-service two-candidate theorem.

A genuine missing hypothesis in the initial general upper was found and reported: integrability of the derivative of a kernel does not ensure a finite infinite-horizon absolute peak. The authors added local absolute continuity, kernel integrability, and bounded common additive response. These repairs leave the concrete stable-kernel lower unchanged. Separate positivity/class and robustness-topology clarifications were also requested; the final status is recorded below.

The accepted conclusions are narrow:

- With the specified **inactive-band finite-jerk contract**, positive unit-energy workloads of unbounded Fourier degree, and the fixed synthetic fourth-order opposite-kernel output, the worst-profile full-future peak-value gap is Theta(m^-3)
- A uniformly bounded workload slope yields an O(m^-4) full-future upper. Exact amplitude rescaling supplies a matching Theta(m^-4) family whose Fourier degree is still unbounded
- A fixed Fourier cutoff K gives the stated O(m^-4) upper, but the supplied work does **not** establish its sharp rate or a nonlinear exact finite-switch theorem at fixed K
- Three pairwise non-opposite kernels reproduce the hard example through an exact aggregate nullspace; this is not generic noncancellation or open-neighborhood robustness
- Coherent kernels give two exact three-switch jerk candidates for signed terminal/post-service observations and the absolute peak restricted to tau >= 1. This does not include the within-service absolute peak
- The other two-switch boundary is a **bounded-acceleration** theorem. Its acceleration jumps are not finite-jerk controls

These are representation-of-value statements. They are not computational-runtime lower bounds, physical grid validation, or historical novelty certificates.

## 1. Files and method

Primary files reviewed:

1. `../theory_worker/FINITE_JERK_AND_BANDWIDTH_THEOREMS.md`
2. `../theory/NONCANCELLING_KERNEL_BOUNDARY.md`
3. `../theory_worker/COHERENT_KERNEL_EXACT_BOUNDARY.md`

The optional `../theory_worker/CONSTRUCTIVE_THREE_MOMENT_LEMMA.md` was checked as a supplementary algebraic construction. The frozen round-2 full-peak lower and active-band bridge theorem were read for conventions and the separate acceleration-class boundary. The scalar and primitive arguments in `../literature/FINITE_JERK_PRIOR_ART_REDUCTION.md` were checked algebraically; this audit does not independently certify the cited Goodman–Lee theorem's source transcription or priority claim.

The audit reconstructed derivatives, endpoint moments, BV atoms and boundaries, nonlinear remainder orders, switch counts, quantifier order, and tail handling. Ordinary floating-point diagnostics were added independently. They are evidence of implementation/algebra consistency, not outward-rounded certificates or substitutes for proof.

The final reviewed content hashes are in `THEORY_AUDIT_INPUT_SHA256.json`. No author proof was edited by this audit.

## 2. Issues discovered and disposition

### 2.1 Real general-upper gap: potentially infinite risk values — repaired

The initial upper assumed only finite h(0) and integrable h'. That permits h(s) = 1. With one positive port e = 1, every clock has y(tau) = theta(tau) = tau after service. Hence R = R_m = infinity, and R - R_m is undefined, despite a perfectly meaningful bounded trajectory-difference estimate.

An arbitrary unbounded common additive response creates the same problem even with stable kernels. Local absolute continuity is also needed for the displayed integration by parts if h' is interpreted as an almost-everywhere classical derivative rather than a weak derivative: singular continuous functions are not covered merely by integrability of their a.e. derivative.

The repaired assumptions h locally absolutely continuous, h and h' in L1, uniformly bounded powers, and bounded common additive response ensure finite peaks. The bounded-slope theorem explicitly inherits them. These assumptions are sufficient rather than minimal: a bounded nominal total response together with the difference estimate would also suffice. The concrete h = s^3 exp(-s) family satisfied them throughout.

### 2.2 Acceleration versus jerk and positive speed — repaired

The separate noncancelling-kernel note originally left the positive rho range implicit. Its theorem uses discontinuous acceleration and no acceleration endpoint constraints. It cannot be imported into the finite-jerk feasible class. The revised header explicitly states that separation, and the contract now requires 0 < rho < 4 and a strictly positive speed band.

The experiment rho = .05 was never affected. The inactive band assertion is valid for the entire endpoint-feasible acceleration class, not just its envelope; a proof is given in Section 8 below.

### 2.3 Coherent theorem: bounded inputs and topology — repaired

The post-service coherent theorem needs bounded continued inputs for its finite absolute-peak interpretation. Continuous strictly positive profiles alone do not imply this: e(theta) = exp(theta) is a counterexample under nominal continuation, even for a stable decaying-exponential kernel. Explicit global amplitude bounds are the clean repair.

The mixed-sign terminal example also has h'(0) = g'(0) = 0. Strict derivative positivity at every interior lag is not, by itself, an open condition in an unweighted C1 norm. For example, g_delta(s) = g(s) - delta*s*exp(-s) has g_delta'(0) = -delta and can reverse the phase derivative near lag zero for every delta > 0, however small. A coefficient-family or weighted relative-derivative robustness statement is valid; unrestricted C1 robustness is not.

Final rereading confirmed both repairs: the note now explicitly assumes globally bounded positive profiles and confines the mixed-sign robustness statement to its coefficient parameterization or a relative-derivative topology. Neither repair changes the duality proof or its exact candidate switch times.

### 2.4 Remaining wording cautions, not failures of the displayed inequalities

- The executive summary was repaired to describe delta_out <= c*N^-3 as a **sufficient generic norm-based certificate**, explicitly allowing structured perturbations to preserve the gap more broadly. This does not become a necessity theorem
- The finite-jerk witness is smooth on the service interval and C3 across the prescribed continuation junction; it is not generally C-infinity across that junction. Its required bounded-jerk regularity is fully satisfied
- The order-four theorem now explicitly assumes C2 kernels, resolving the possible ambiguity about a merely a.e. second derivative. The supplied smooth finite-dimensional kernels satisfy this
- The amplitude-rescaled lower has gap scale N^-4, so its generic perturbation certificate also scales N^-4. The N^-3 tolerance displayed for the original amplitude-only family must not be transferred unchanged

## 3. Feasible class and moment saturation

### 3.1 Finite jerk really means jerk arcs

Acceleration is absolutely continuous with a' = j a.e. and |j| <= J. A finite piecewise constant acceleration that is absolutely continuous has no nonzero jumps and must be constant. Under a(0) = a(1) = 0 it is then identically zero. Thus switching the representation from acceleration arcs to piecewise constant jerk is essential, not cosmetic.

Finite jerk arcs produce continuous piecewise affine acceleration, continuously differentiable velocity, and the required phase regularity. The prescribed return of jerk to zero at t = 1 is allowed and is explicitly excluded from the interior switch budget.

### 3.2 Entire-class inactive envelopes

For every jerk-feasible clock with a(0) = a(1) = 0,

    |a(t)| <= J min(t,1-t),
    integral_0^1 |a(t)|dt <= J/4.

Therefore |v(t)-1| <= J/4 = 1/16 and |a(t)| <= J/2 = 1/8. Both stated acceleration/speed bands are strictly inactive for the whole feasible set. This is the correct reason local moment replacements remain feasible between nodes. Endpoint matching alone would not justify that conclusion under an active band.

### 3.3 Moment-body proof

For |u| <= J, the moment body of degrees 0 through n is a compact convex set: bounded L-infinity balls are weak-star compact, and the finitely many polynomial integral maps are continuous. Fixing the first n moments leaves a nonempty compact fiber. A maximizer of moment n lies on the boundary of the full body, including when the prescribed lower moments already lie on their boundary.

A supporting hyperplane supplies a nonzero polynomial p of degree at most n. Equality in

    integral p u <= J integral |p|

forces u = J sign(p) a.e. Since a nonzero polynomial has finitely many zeros and at most n sign changes, a matching bang function with at most n switches exists. No normality or interior-point assumption is being smuggled into this proof.

For n = 3, matching moments of degrees 0, 1, 2 preserves a, v, theta at the right endpoint. For n = 4 it additionally preserves the cell integral of theta. Joining M cells gives at most 4M-1 or 5M-1 interior jerk jumps, respectively. These are safe upper counts; equal adjacent values or degenerate intervals can only reduce them.

The optional explicit two-interval density construction also checks out: its mean-preserving family stays in the cell, its second moment increases as

    nu(g) = nu_min + x(q-x)g(1+g/q),

and the displayed quadratic root solves the target moment equation. Its degenerate cases are necessary and are explicitly handled. It is not needed for the main moment-body proof.

## 4. Uniform amplitude-only upper

For the phase difference d on one cell, d, d', d'' vanish at both ends and |d'''| <= 2J. Integrating from either endpoint yields

    |d(s)| <= (J/3) min(s^3,(Delta-s)^3),
    ||d||_infinity <= J Delta^3/24.

The replacement has exactly the original endpoint work, speed, and acceleration, and the entire-class envelope argument supplies positive speed at every intermediate time. With bounded measurable e, its primitive E is Lipschitz. Positive bi-Lipschitz clocks justify the chain rule dE(theta)/dt = e(theta)v a.e.; no workload derivative is required.

The output-difference identity is correct, including the h(0) current-phase boundary. The primitive difference is identically zero after service because the clocks have the same endpoint and identical continuation. Thus the h' L1 norm controls all future observations, not just the service window. The finite-risk repair makes the near-optimal-clock/supremum-norm argument legitimate without assuming an attained optimum or attained time maximum.

Consequently U1–U3 hold with the stated constants and m >= 3. Common bounded additive responses cancel from differences; they need not cancel from individual peak values for this upper argument.

## 5. Fixed-kernel all-future lower

### 5.1 Workloads and witness

Q = (1-cos(2*pi*x))^2 has the stated Fourier expansion and derivative bounds. Q and its first three derivatives vanish at integers. The top frequency N+2 in each profile is nonzero even at N = 1, so the exact-degree assertion is correct. The bound |P_N'| <= 7A is conservative and implies the stated strict positivity. Periodicity of P_N gives exactly one unit of energy per port.

The witness phase perturbation J Q(Nt)/(d0 N^3) has its phase/speed/acceleration perturbations zero at both endpoints and jerk bounded by J because d0 = 48*pi^3 bounds ||Q'''||. Its feasibility does not use a small-J limit. It need not belong to the finite-jerk-arc class in order to lower-bound the unrestricted value.

### 5.2 Exact observation formula and derivatives

The phase formula L2 follows from the original power convolution, P_N(0) = 0, h(0) = 0, and the positive-clock change of variable. It continues to integrate through phase theta(tau) for tau > 1. The periodic post-service forcing is retained, not zeroed out or replaced by a homogeneous tail.

Both displayed derivatives in L3 are correct. In particular the jerk contribution is

    -j H1 Q / v^4.

A jerk jump therefore contributes exactly -Delta j H1 Q/v^4 to F''. There is no jump in a or v. The return to zero jerk at t = 1 has no atom because Q(1) = 0.

### 5.3 Third integration by parts and all-time bound

F and F' vanish at both integration endpoints. F'' at the upper endpoint does **not** generally vanish:

    F''(b-) = 6 Q(b)/v(b)^3.

It has been retained correctly. Writing k = 2*pi*N, the exact last-stage identity has the form

    y = (A/k^4) [F''(0+) - F''(b-)cos(kb)
                 + integral_(0,b) cos(kx) dF''(x)].

The initial term is zero. The final term is bounded by B0. The BV atoms are bounded by 2JmS. The monomial differentiation rules are correct: dH_r/dx = -H_(r+1)/v, da/dx = j/v, and dv/dx = a/v. Every resulting power of v can be bounded using v >= l after converting dx = v dt. The kernel L1 norms then give a uniform bound independent of tau and the number of continued nominal periods.

The K1 value is the exact total variation of s^3 exp(-s). K2, K3, K4 are valid polynomial-coefficient integral bounds. L5 consequently bounds every restricted clock at every future observation, including arbitrary non-bang jerk levels in [-J,J].

### 5.4 Leading lower term and nonlinear remainder

At tau = 1, w = h'(1-t) is nonnegative and integrates to 1/e. The stated I0 follows, for example, by noting h' is increasing over [1/3,2/3], hence w >= h'(1/3) > 8/(27e), while Q >= 9/4.

The cell mean integral Q(s)cos(2*pi*s)ds = -1 gives the positive leading term A J I/(d0 N^3). The mean-zero averaging error is O(N^-4) with the displayed conservative factor 5. The remaining Q' term is O(N^-4). The nominal zero-state response is correctly retained and bounded by three integrations by parts using g, g', g'' zero at both endpoints.

The Taylor remainder is not neglected:

    remainder <= (1/(2e)) ||P_N''|| ||eta_N||^2
               <= A J^2 C_R N^-5.

It can safely be absorbed into the displayed N^-4 error bound. All constants are independent of N. The threshold N0 makes the positive leading term dominate the combined error at fixed J.

For arbitrary bounded jerk, two integrations in phase and the a.e. F'' formula also give a uniform O(N^-3) unrestricted-risk bound. Thus the actual risk scale is Theta(N^-3), rather than merely having a decaying feasible witness.

### 5.5 Quantifiers and gap algebra

The argument compares an attained finite-time observation of one unrestricted witness against an upper bound for **all** restricted clocks and **all** tau >= 0. This is the needed full-peak comparison; a terminal-only lower by itself would not suffice.

Substituting alpha, beta into L5 makes the restricted bound at most gamma/N^3, whereas L10 is at least 2*gamma/N^3. Hence the displayed gap follows. Choosing N_m = max(N0, ceil((m+beta)/alpha)) is in the correct inequality direction and yields Omega(m^-3). The uniform compression upper supplies the matching O(m^-3).

No maximizing observation time, exact unrestricted optimizer, or finite time horizon is assumed. The order of suprema is legitimate; no limiting interchange with an uncontrolled tail is required.

## 6. Uniform slope, fixed Fourier cutoff, and rescaled sharpness

The fourth matched jerk moment gives integral_cell d = 0 exactly. In the output difference,

    E(theta_hat)-E(theta) = e(theta)d + r,
    |r| <= L d^2/2.

For f(t) = h'(tau-t)e(theta(t)), the stated Lipschitz constant is correct. Subtracting one cell value of f on a complete cell gives an O(Delta^5) local linear error; summing at most M cells gives O(Delta^4). The one possible partial observation cell contributes O(Delta^4) using its length, the phase bound, and ||f||. The quadratic term is O(Delta^6) over the total interval. Therefore S2 and S3 are valid for every observation time, not merely mesh-node observations. h(0) = 0 removes a current-phase boundary that this proof cannot control at order four.

The optional primitive sharpening is also valid without any external spline theorem. Let G(t) be the time primitive of d starting at a cell boundary. Four-moment matching gives G, G', G'', G''' zero at both cell ends. Hence |G| <= J Delta^4/192. The identity

    integral_0^b f d = f(b)G(b) - integral_0^b f'G

handles the partial cell automatically and improves J/24 to J/192 in the leading C4. The quadratic constant C6 is unchanged. The original weaker constant remains correct.

The elementary Fourier coefficient bound gives the claimed uniform slope at fixed K. Accordingly a fixed-K Omega(m^-3) worst-profile gap is ruled out on this contract. No fixed-K matching m^-4 lower follows.

For A_N = A/N, every output under the exactly cancelling zero-state model is exactly 1/N times the original output, for every clock and observation. Therefore both optimized peak values scale exactly, not just their first variations. Positivity and unit energy survive, and

    ||e_j,N'|| <= (A/2)[2*pi Q0 + 2Q1 + Q2/(2*pi)]

is a common slope bound. The same N0 and m <= alpha N - beta condition yield gap gamma/N^4. Combined with S3 this proves Theta(m^-4) for the specified bounded-slope family and any fixed amplitude/slope-bounded class containing it under the same kernel and clock contract. Its bandwidth is still unbounded. Exact scaling would fail with an arbitrary nonzero common additive response, so the stated zero-state qualification is essential.

## 7. Cancellation and perturbations

For h1 = h, h2 = -h+g, h3 = -g and p2 = p3, the output identity is exact. Linear independence of h and g ensures that no two kernels are proportional. Nevertheless h1+h2+h3 = 0 and the paired profiles are correlated. The example removes pairwise opposition without removing aggregate cancellation. It supplies no robustness against independently varying those profiles or no-nullspace physical network theorem.

For unchanged bounded workloads, convolution gives the stated uniform output error delta_out from L1 kernel errors plus the common additive-response error. A supremum of absolute outputs is 1-Lipschitz under a uniform output perturbation. Both optimized values move by at most delta_out, so the gap can decrease by at most 2*delta_out. The claimed finite-instance sufficient tolerance is therefore correct.

This norm argument is one-sided. It neither proves that every fixed perturbation destroys the asymptotic lower nor proves that an open fixed-radius neighborhood preserves it. Subtracting a nominal common-mode response leaves the clock-dependent term involving v-1, exactly as the note warns.

## 8. Separate bounded-acceleration monotonicity boundary

The energy-primitive terminal formula and its phase derivative are exact. On 0 < s <= 1, h'(s) > 0 and g'(s) > h'(s). Thus 2*epsilon >= A with epsilon > 0 makes q strictly positive on the service interior, including equality in the coefficient threshold. The pointwise maximal phase envelope maximizes the nonlinear terminal response without linearization. Strictness plus continuity gives uniqueness of its phase trajectory.

For completeness, the inactive speed-band bound rho/4 is valid. Normalize w = (v-1)/rho. Then w(0) = w(1) = 0, |w'| <= 1, and integral w = 0. If w(t) = b >= 0, the endpoint Lipschitz constraints imply b <= min(t,1-t), and the smallest possible integral compatible with that value is

    b^2/2 + b/2 - [t^2+(1-t)^2]/4.

For fixed b, its minimum over b <= t <= 1-b is b-1/4. Zero mean therefore forces b <= 1/4. Applying the same argument to -w proves the lower speed bound.

The universal (+,-,+) acceleration pattern at 1/4, 3/4 is phase maximal: compared with it, a competing velocity difference is initially nonpositive, nondecreasing across the middle downward ramp, and finally nonnegative. Its total integral is zero, so every prefix integral is nonpositive. The active-band counterpart follows from the already established clipped five-arc envelope, within the separate acceleration class.

The note appropriately does not transfer this signed terminal conclusion to a full-future absolute peak or to finite jerk.

## 9. Coherent finite-jerk exact candidates

The fixed endpoint contract is equivalent to three zero jerk moments of degrees 0, 1, 2. Its feasible set is convex and weak-star compact. Triple integration makes the phase map compact in the uniform topology; continuity of E and integrability of h' make each fixed-time objective continuous. Exact maxima and minima exist.

At a nonlinear optimum j_star, differentiation along any feasible line segment gives a linear support problem with

    F(s) = (1/2) integral_s^1 q_theta_star(t)(t-s)^2 dt,
    F''' = -q_theta_star.

This is a necessary first-order condition, which is sufficient for the stated reduction because the subsequent support problem has only the two possible moment-feasible extremizers. No convexity of the nonlinear objective is assumed.

A best L1 quadratic approximant p exists by finite-dimensional coercivity. If q has one strict sign, or that sign with no interval of zeros as specified, F'' is strictly monotone. Then F-p has at most three distinct zeros: four zeros would force two distinct zeros of its strictly monotone second derivative. In particular its zero set has measure zero. Differentiating the L1 approximation objective yields zero moments for sign(F-p), which proves the dual identity and attainment directly. Equality forces any support maximizer to be bang almost everywhere.

Fewer than three switches cannot satisfy all three zero moments: a polynomial of degree at most two with exactly those switch roots can be signed to have strictly positive product with the bang jerk a.e., contradicting its vanishing moment integral. With exactly three switches, the moment equations reduce to

    x1-x2+x3 = 1/2,
    x1^2-x2^2+x3^2 = 1/2,
    x1^3-x2^3+x3^3 = 1/2.

They give x2 = 1/2, x1+x3 = 1, x1*x3 = 1/8 and hence the stated (2 ± sqrt(2))/4 endpoints. The explicit phase formula differentiates to the correct bang jerk and satisfies all endpoint conditions. The maximum and minimum must therefore be among these two trajectories.

For positive mixtures of decaying exponentials, every h_j' is strictly negative, so arbitrary positive bounded profiles preserve the condition for each tau >= 1. At each time every feasible output lies between the two candidate outputs. Taking an absolute value and then a time supremum proves the two-trajectory post-service peak formula, even with a bounded common additive response.

The positive coefficient/rate region is genuinely open in that fixed finite-dimensional parameter family. The note correctly warns that infinite-horizon sign coherence is not open in every unweighted function topology. A small slower-decaying perturbation can eventually control the tail.

For 0 < tau < 1, the current phase is not fixed and the h(0) endpoint contribution can change the first variation. The presented proof does not establish a whole-time absolute-peak reduction. No early-time extension is accepted or needed in this audit.

## 10. Independent diagnostics and interpretation

Reproducible files:

- `verify_jerk_audit.py`
- `JERK_AUDIT_DIAGNOSTICS.json`
- `jerk_audit_diagnostics.log`

The script checks 28 combinations of N in {1,2,7,19} and observations from .08 through 5.8, using a three-switch moment-feasible jerk trajectory. The original power convolution, energy-primitive expression, and full third-integration BV expression agree to about 1.30e-16. The diagnostic retains both jerk atoms and the upper observation boundary. This is a useful independent check against a missing-tail or missing-boundary error.

The smooth witness was evaluated for N = 1,2,3,4,8,16,32,64,128. Its nominal startup term can dominate and change the sign at small N, which is consistent with the theorem's large-N condition. N^3*y(1) approaches approximately 9.44047e-7. The stated conservative remainder inequalities hold on those checks. Nine independent bounded-acceleration LP comparisons also reproduce the simultaneous phase envelope on an aligned grid.

The diagnostic constants include C_cont approximately 33073.88, C_star approximately 11.90678, N0 = 1,734,133, alpha approximately .000585087, beta approximately 3620.22872, and gamma approximately 3.43307e-8. These are ordinary floating-point evaluations of exact definitions. The very conservative sufficient index is not evidence of a useful engineering margin. Small-N numerical observations do not certify the formal asymptotic value gap.

SciPy reports a roundoff warning at the requested stringent quadrature tolerance; no interval enclosure is claimed. The algebraic proof, not those quadrature tolerances, establishes the results. No numerical search here computes a globally optimized unrestricted full-future peak.

## 11. Final publication boundary

The mathematical package now supports a synthetic constrained realization and regularity boundary. It does not support any of the following stronger statements:

1. A sharp m^-4 rate at fixed finite workload bandwidth
2. An active-band finite-jerk compression theorem
3. A noncancelling generic physical grid lower or fixed-radius robust hard family
4. A whole-time peak reduction from the coherent post-service theorem
5. A runtime lower bound for symbolic/Fourier/oracle algorithms
6. A large or increasing physical hazard as N increases
7. A claim of historical novelty for moment saturation, perfect splines, oscillatory/BV integration, or sign-coherent support reduction

Subject to these boundaries and the final incorporated hypothesis fixes, the core theorem statements are mathematically credible and internally consistent.

## 12. Final reread and closure

The final versions were reread after the authors applied the finite-risk/AC, positive-speed/class, bounded-input, C2, sufficient-tolerance, and robustness-topology fixes. The optional C4/8 improvement and exact amplitude-rescaling corollary are included and mathematically valid. The coherent note labels its possible early-observation extension unproved and does not use it; this audit makes no claim about that extension. A quick claim-scope scan of `../report/G2_ROUND3_RESEARCH_DOSSIER_ZH.md` found the key distinctions preserved, including its very small normalized gap certificate, unbounded-degree qualification, separate acceleration class, and post-service-only coherent reduction.

No unresolved material mathematical gap remains in the accepted results. Remaining cautions are the global smoothness wording at the continuation junction, the separate N^-4 perturbation scale for the rescaled family, and the substantive unproved extensions listed above. The final source hashes accompany this audit.
