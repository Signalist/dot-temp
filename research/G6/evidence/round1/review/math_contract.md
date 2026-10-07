# G6 independent mathematical contract review

Date: 2026-10-02. Scope: mathematical review and a proposed bounded validation contract. No experiments were performed for this review. All numerical tolerances and budgets below are proposed preregistration choices, not achieved results.

## Verdict

The proposed site-waveform support identity is correct, under the assumptions below, but it is a classical support-function/robust-optimization identity. Exact event-periodic response plus certified continuous uncertainty can make a valid conditional synthetic certificate. Neither replacing harmonic triangle bounds by exact waveform maxima nor applying interval certification to the classical robust counterpart establishes a new capacity method. Set `paper_ready=false` if the same-information classical method is algebraically identical; improvement over harmonic l1 alone does not rescue this gate.

The most defensible bounded first endpoint is certified capacity on a few predeclared allocation rays, with a rigorous lower/upper capacity bracket. Do not entangle the first certificate with an unconverged global allocation optimizer.

## 1. Quantifiers and the actual robust counterpart

Let a_i >= 0 be peak-amplitude scales. Let eta denote shared grid parameters and any shared workload parameters. Let nu_i denote genuinely independent per-site uncertain parameters, e.g. (T_i,d_i,tau_i) if their admissible set is a Cartesian product. Let q_ji(phi_i;eta,nu_i) be the scalar steady-periodic response at monitor j to unit-amplitude site i. It is continuous in phase for a strictly proper response; when there is feedthrough, use one-sided event values and supremum.

At a fixed eta and nu, arbitrary independent site phases give exactly

    sup_{phi_1,...,phi_n} sum_i a_i q_ji(phi_i;eta,nu_i)
      = sum_i a_i max_{phi_i} q_ji(phi_i;eta,nu_i).

For sign sigma in {+1,-1}, define

    m_ji^sigma(eta) = sup_{nu_i,phi_i} sigma q_ji(phi_i;eta,nu_i).
    R_j^sigma(a) = sup_eta sum_i a_i m_ji^sigma(eta).

The exact robust feasible set for rectangular monitor limits is

    a >= 0,
    R_j^+(a) <= b_j^+,
    R_j^-(a) <= b_j^-  for every j.

Important qualifications:

- Shared uncertainty remains outside the sum. Replacing R_j by sum_i a_i sup_eta m_ji changes the problem and is generally conservative. Per-site grid parameters cannot be independently adversarial if they describe one physical grid.
- A common uncertain T or common duty constraint belongs in eta. Correlated local parameters require retaining their joint admissible set. Independent site maxima are exact only for the stated Cartesian product.
- Different site periods need no common aggregate period: at any selected time, arbitrary initial phases can realize independent site maximizers. This is a worst-case-over-phases statement, not a guarantee that an arbitrary fixed realized trajectory ever reaches every phase combination.
- Each monitor/sign may have a different adversarial phase tuple. That is correct for robust box constraints. For a coupled output constraint use its corresponding vector support direction or the coupled objective; do not silently replace it by marginal coordinate maxima.
- Harmonics within site have phases k*phi_i plus their fixed Fourier phase. Giving every harmonic its own arbitrary phase enlarges the uncertainty set.
- Cross-site phase diversity gives no robust benefit when phases are entirely unrestricted. The potential tightening is within-site spectral consistency.
- Signed a_i would require max_phi a_i q rather than the formula above. Keep a_i nonnegative.
- If nonzero means or fixed base disturbances are included, retain their signed contribution; do not discard DC terms by calling everything a deviation.

For fixed uncertainty, the constraints are linear in a. Their intersection is a classical convex robust feasible region. Different mathematical notation does not change this object.

## 2. Minimal physically interpretable synthetic model

For site i, use a fixed first-order PCC shaping state z_i driven by a zero-mean periodic job waveform u_i:

    z_i' = -gamma_i z_i + gamma_i u_i,  gamma_i=1/tau_i > 0.
    xi_ri' = v_ri.
    v_ri' = -omega_r^2 xi_ri - 2*zeta_r*omega_r*v_ri - kappa_ri*z_i.
    q_ji = sum_r c_jr v_ri.

Use zero-mean u_i=1-d_i on the on interval and u_i=-d_i on the off interval. The corresponding physical 0/1 demand has mean d_i; its baseline power must be accounted for separately. Specify all units: xi in modal angle units, v in angle/time, kappa in compatible power-to-acceleration units, and c including Hz conversion if required.

This is an externally forced, fixed-coefficient modal model. It is not an AC power-flow feasibility certificate, voltage-stability result, protection certificate, full-grid closed-loop stability result, or UPS feasibility guarantee. A full swing network often has a rotational angle mode; remove/reference that mode or use the correct frequency/regulation realization before asserting the entire A is Hurwitz. Positive damping of the selected modal model is not evidence that an unmodeled real grid is stable.

Two modes are preferable if claiming nontrivial multi-monitor geometry. One scalar mode observed at several buses often gives proportional outputs and a degenerate set of constraints. One mode is acceptable as a numerical proof-of-concept if described honestly.

Treat tau and modal residues as fixed declared synthetic quantities in the first study. If tau is optimized as smoothing, it must not create free flexibility: a storage realization needs energy and power constraints and a compute-deferral realization needs throughput/latency constraints. For an ideal lossless first-order storage interpretation of a physical 0/1 load r, the required storage energy swing is a_i*tau_i*(max z_i-min z_i), in consistent power-time units; this alone is not a complete UPS model.

## 3. Event-periodic response, with no harmonic truncation

For any fixed parameter tuple write x'=A x+B u, q=C x, with A Hurwitz. Define

    F(t)=exp(A t),
    G(t)=integral_0^t exp(A s) B ds.
    h=d*T, ell=(1-d)*T, u_H=1-d, u_L=-d.
    x_1=F(h)x_0+G(h)u_H.
    beta=F(ell)G(h)u_H+G(ell)u_L.
    x_0=(I-F(T))^{-1} beta.

Use the block exponential of [[A,B],[0,0]] to obtain F and G without an A inverse. A numerical inverse or expm alone is not a certificate.

Parameterize each event segment by s in [0,1]:

    x_H(s)=F(s*h)x_0+G(s*h)u_H.
    x_L(s)=F(s*ell)x_1+G(s*ell)u_L.

This fixes event boundaries while T and d vary. Certify both segments and their endpoints. If a nonzero feedthrough D is introduced, include q=Cx+D*u on each side of each event.

This formulation has no Fourier truncation. Its numerical exponential/solve enclosures still have nonzero approximation and rounding errors that must be included. Calling the flow “exact” means the mathematical formula, not floating-point evaluation.

## 4. A concrete analytic contraction certificate

For strictly underdamped modes, assume declared compact bounds

    omega_r >= omega_r,min > 0,
    0 < zeta_r,min <= zeta_r <= zeta_r,max < 1,
    gamma_i >= gamma_i,min > 0,
    T_i >= T_i,min > 0.

Set a_r=zeta_r*omega_r, b_r=omega_r*sqrt(1-zeta_r^2), and

    S_r = [[b_r,0],[a_r,1]].

Direct calculation gives

    S_r [[0,1],[-omega_r^2,-2*a_r]] S_r^{-1}
      = [[-a_r,b_r],[-b_r,-a_r]].

For differences of two trajectories under the same forcing, w_ri=S_r*(xi_ri,v_ri) obeys

    D+ ||w_ri||_2 <= -a_r ||w_ri||_2 + |kappa_ri| |delta z_i|,
    D+ |delta z_i| <= -gamma_i |delta z_i|.

Choose positive beta_ri with beta_ri >= 2*kappa_ri,max/a_r,min (choose any positive beta for an uncoupled mode), and define the weighted block norm

    ||delta x_i||_* = max( |delta z_i|,
                          max_r ||S_r delta x_ri||_2 / beta_ri ).

The upper right Dini derivative satisfies

    D+ ||delta x_i||_* <= -alpha_i ||delta x_i||_*,
    alpha_i = min(gamma_i,min, min_r a_r,min/2) > 0.

Therefore the period map is a contraction in this norm with

    rho_i <= exp(-alpha_i*T_i,min) < 1.

This is an elementary modal/block-norm derivation, not a claimed new theorem. The norm depends on the fixed physical parameters through S_r, which is permissible: the bound applies to every fixed tuple. Evaluate S_r and its inverse with interval bounds when converting residual and output enclosures over a parameter cell. Exclude the critical-damping limit from this particular transformation or switch to a separately verified Lyapunov-norm construction there.

For any approximate periodic starting state xhat, certify the residual over a parameter cell:

    epsilon >= sup || F(T)*xhat + beta - xhat ||_*.

Then the exact periodic starting state satisfies

    ||x_0 - xhat||_* <= epsilon/(1-rho_i).

xhat can come from an ordinary floating-point solve; its residual and the bound must use verified arithmetic. This residual correction is usually much tighter than bounding ||x_0|| by ||beta||/(1-rho). Map the error ball through S_r^{-1}, or bound output rows directly. Low damping/small T can make the denominator small: report a wide enclosure or an unresolved case, not a false pass.

A verified enclosure of (I-F(T))^{-1} beta is an equally acceptable baseline alternative. No requirement exists to force this contraction proof when another validated method is sharper.

## 5. Continuous uncertainty and peak certification

Use a deterministic interval branch-and-bound with outward-rounded arithmetic. A useful implementation contract is:

1. Store the exact input boxes, units, correlations, model expressions and rational/decimal source constants.
2. Maintain an exhaustive leaf-box cover of the shared uncertainty eta. Within each shared cell, bound each site's local (T,d,s) search on both segments.
3. Each node returns a rigorous response interval, using certified matrix exponentials and the periodic-state enclosure above. Interval automatic differentiation or an analytically verified derivative bound can tighten it.
4. A center-plus-gradient upper bound is valid only if every derivative is bounded over the entire box: U <= f(center)_upper + sum_k sup_box |partial_k f|*radius_k. The centered expression can be intersected with a direct interval enclosure. Observed finite differences or maxima of sampled derivatives are not derivative bounds.
5. For a fixed shared cell, sum the site upper bounds with nonnegative a_i. This is safe even though different sites may attain them at different eta values inside that cell; refining the shared cell controls this conservatism.
6. Lower-bound witnesses must use one common eta and compatible local tuples. Evaluating site maxima at incompatible grid points is not a witness.
7. Take the largest upper bound over all unpruned shared cells. Never replace it by the largest sampled point. Preserve all surviving leaves when the budget expires.
8. Terminate with CERTIFIED_SAFE, CERTIFIED_VIOLATION, or UNRESOLVED. Exhausted budget, failed interval inversion, or excessive enclosure width means UNRESOLVED.

For an elementary matrix-exponential inclusion, a Taylor polynomial with a rigorous norm remainder is sufficient: if ||M|| <= R, the remainder after degree m is bounded in that induced norm by exp(R)*R^(m+1)/(m+1)!. Scaling/squaring can reduce cost and dependency loss. All arithmetic including scalar transcendental bounds must be outward rounded. Arbitrary “1e-10 safety margins,” ordinary double precision expm, high precision without directed enclosures, or independent floating-point agreement are not substitutes.

## 6. Bounded first study and auditable capacity brackets

Recommended small scope: three sites, two modes, two monitors, a one- or two-dimensional shared resonance/damping box, independent bounded T_i and d_i, fixed tau_i and residues. Publish the boxes before running. Keep this synthetic and do not invent calibration claims.

Use three predeclared nonnegative amplitude profiles w with sum_i w_i=1, e.g. (1/3,1/3,1/3), (0.6,0.3,0.1), (0.1,0.3,0.6), plus single-site sanity checks. Do not select profiles after seeing where l1 looks weakest.

For a= lambda*w define

    W(w)=max_{j,sigma} R_j^sigma(w)/b_j^sigma.

A certified bracket L <= W(w) <= U implies the exact radial capacity bracket

    1/U <= lambda_star(w) <= 1/L,

when 0<L<=U. The lower capacity is safe; the upper capacity is an impossibility bound. Include a concrete adversarial witness supporting L and a box-cover certificate supporting U. This closes a precise question without requiring an allocation optimizer. If duty is uncertain, sum a_i is peak amplitude, not guaranteed average throughput: declare the desired throughput measure separately.

Suggested preregistration: seek <=1% relative capacity bracket per ray; hard cap each method at a declared wall-time and interval-node count, e.g. 30 minutes and 100,000 nodes on recorded hardware; never convert cap exhaustion into success. These are bounded evaluation limits, not a claim of convergence within them. Record unresolved outputs and use identical proof tolerances/budgets where methods are being compared. If a full capacity-region optimizer is later added, separately certify its robust feasibility and objective optimality gap; a successful local solution is not the latter.

## 7. Strongest same-information baselines

Mandatory baseline A: the classical exact waveform-support robust counterpart above, using event-periodic solutions or an equivalent sufficiently certified response representation and a certified pessimizing oracle. It gets the identical waveforms, phase constraints, parameter correlations, uncertainty boxes, output definitions, and numeric accuracy. If G6 implements exactly this, report equality and no new capacity advantage. Comparing only against a weaker l1 bound would hide the decisive baseline.

Baseline B: harmonic l1 with the same waveform information, same continuous uncertainty, and a certified tail. For a zero-mean unit square wave,

    U_k = exp(-i*pi*k*d)*sin(pi*k*d)/(pi*k), k != 0.
    max_phi q_ji(phi) <= 2*sum_{k>=1} |H_ji(i*k*Omega)*U_k|.

For the modal-frequency model, if k*Omega >= sqrt(2)*omega_max and tau >= tau_min,

    |H_ji(i*k*Omega)|
      <= 2*sum_r |c_jr*kappa_ri| / (tau_min*(k*Omega)^2).

Using |U_k|<=1/(pi*k), Omega>=Omega_min, and sum_{k>K} k^-3 <= 1/(2*K^2), a uniform two-sided harmonic tail bound is

    tail_K <= 2*sum_r |c_jr*kappa_ri|_max
                  / (pi*tau_min*Omega_min^2*K^2),

provided (K+1)*Omega_min >= sqrt(2)*omega_max. Keep shared eta outside the site sum when optimizing this baseline as well. This bound is for the stated frequency-output transfer, not arbitrary outputs; RoCoF changes the high-frequency order. A direct-feedthrough square-wave response can make harmonic l1 divergent.

Baseline C: finite sampled uncertainty/phase checks, explicitly labeled non-certifying diagnostics. They can show missed violations but cannot certify absence. Dense or random sweeps and the old 4/72-model checks remain diagnostics only.

The robust cutting-set framework with exact worst-case analysis is established; approximate oracles do not inherit its exact conclusions. See Mutapcic and Boyd (2009): https://web.stanford.edu/~boyd/papers/prac_robust.html . Support functions as pointwise suprema are standard convex analysis: https://web.stanford.edu/~boyd/cvxbook/index.html . Interval exponential enclosures and dependency loss are established numerical-analysis issues; Goldsztejn (2009) discusses interval scaling/squaring and hardness of sharp interval-exponential enclosure: https://arxiv.org/abs/0908.3954 . These sources support baseline/proof-method positioning; the formulas and proposed study above are derived for this review.

## 8. Decisive falsification and release gates

### Mathematical/semantic gates

- G1, quantifiers: proof and code implement the stated shared/local uncertainty and independent-site phase contract. Any hidden sitewise copy of shared eta fails exactness.
- G2, state/model: all admitted A are Hurwitz, the modeled outputs/units are explicit, and no discarded zero mode or nonzero DC contribution changes the claim.
- G3, steady-state scope: label the guarantee steady-periodic. Startups, job transitions, time-varying T/d, and arbitrary initial states are excluded unless independently bounded. For a specified initial mismatch, add the corresponding certified decaying transient output bound; do not silently assume periodic initialization.
- G4, waveform: the same linked harmonic phases and input normalization are supplied to all same-information methods.
- G5, novelty: if G6 reduces algebraically to baseline A and offers no independently defined new algorithmic/proof result beyond existing validated robust optimization, `paper_ready=false` regardless of its gain over B/C.

### Numerical certificate gates

- G6, coverage: a machine-checkable exhaustive parameter/event cover and its maximum upper bound are saved. No continuous parameter is covered by samples alone.
- G7, rounding/truncation: verified outward arithmetic encloses every exponential, residual/inverse and peak bound. If spectral evaluation is used, its uniform omitted-harmonic tail is included.
- G8, witness: a certified evaluated tuple exceeding a proposed limit falsifies safety immediately. Check resonance crossings, phase extrema, event endpoints, duty boundaries, and uncertainty-box boundaries as diagnostics, without pretending they exhaust the continuum.
- G9, proof gap: each released radial-capacity value has the declared [1/U,1/L] bracket and meets the preregistered tolerance. A wide but valid bound is recorded as valid/wide, not as a tight certified frontier.
- G10, representation check: at fixed non-adversarial points, event-periodic and independent harmonic-plus-tail enclosures must overlap. Nonoverlap is an implementation failure. Agreement alone does not certify the whole uncertainty domain.
- G11, independent replay: a checker replays the saved cover/bounds and accepts without trusting optimizer status or plotting scripts. Store model/inputs, source revision, arithmetic backend, precision, leaf coverage, worst-case witness, timing and unresolved counts.

### Stop/go interpretation

- A verified violation: reject that capacity and retain the witness.
- No violation but incomplete bound: UNRESOLVED, never safe.
- Valid continuous certificate and tight bracket: valid conditional synthetic engineering result.
- Classical same-information equality: no demonstrated new capacity method; `paper_ready=false` unless a separately articulated and supported new contribution survives review.
- Full AC/voltage/UPS/real-job robustness claims: unsupported by this study even if all synthetic gates pass.
