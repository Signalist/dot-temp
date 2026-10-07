# Independent focused audit: Kundur information-contract transfer

Reviewed 2026-10-04 UTC: network_transfer/METHOD_AND_LIMITS.md, phase_lipschitz.py, certify_binned.py, openloop_continuous_lower.py, and the relevant definitions in design_controller.py. The review did not rerun nonlinear cases and makes no nonlinear continuum claim.

## Result

No substantive mathematical error was found in the phase-Lipschitz construction, PWL continuous-time interpolation bound, periodic-tail bound, or terminal-free measurable-control lower relaxation. One floating endpoint helper issue was reported and the exact-bin/phase-free-online correction was directly inspected and closed, as recorded below. The current result remains a same-conventional-family resource comparison. The universal no-feedback lower 64.616246553 MWs is below the feedback witness 94.264936753 MWs and does not establish a universal network information-resource gap.

## 1. Spectral assumptions and all-future phase allowance

For a fixed observation-history bin the applied battery trajectory is common, so it cancels from the difference between two LTI worlds. The derivative of their uncontrolled frequency with respect to first-edge time is the 50 MW alternating impulse-response train. On lag t=5m+a, 0<=a<5, its modal amplitude is

    exp(lambda*a)*(-1)^m*b_m*[1-(-q)^(m+1)]/(1+q), q=exp(5lambda).

The implementation omits the global factor (-1)^m when bounding absolute output, which is harmless. It explicitly bounds m=0,...,19. For every m>=20 the residual from the limiting alternating orbit is bounded by |q|^21, so the tail's exponent is correct. Both sides of the impulse-train discontinuities are included through adjacent closed segment evaluations. Frequency itself has no direct load feedthrough and is continuous, so bounded one-sided phase derivatives imply a global Lipschitz bound.

The exponential curvature enclosure is valid when all Re(lambda)<=0:

    |y''(a)| <= |CV|*|lambda|^2*|z|,

and endpoint linear interpolation then incurs at most that componentwise bound times h^2/8. The recursive half-interval update uses the correct propagated modal coefficient. Taking the maximum across the four generator outputs preserves the bound.

Independent numerical model checks:

- 51-by-51 stable quotient
- max Re(lambda)=-0.13953444562568046
- min |lambda|=0.14146437308940077
- max |exp(5lambda)|=0.4977425875171122
- min |1+exp(5lambda)|=0.9021280047882577
- eigenvector condition number approximately 12124.6578
- max elementwise diagonalization residual approximately 3.43e-13

No zero eigenvalue, unstable eigenvalue, or near-zero geometric denominator was found. The moderately ill-conditioned modal basis reinforces the existing qualification: these are analytic inequalities evaluated in ordinary floating point, not a directed-rounding proof for the exact supplied matrix.

The stated phase allowance 0.05*0.0887232453644≈0.00443616226822 Hz follows directly from the maximum within-bin displacement. It cannot be reused for phase intervals whose controller histories differ.

## 2. Continuous-time PWL and periodic-tail certificate

For a modal state driven on one interval by q+r*t,

    z(h)=exp(lambda*h)*(z0+b*q/lambda+b*r/lambda^2)
         -b*(q+r*h)/lambda-b*r/lambda^2.

This is exactly the advance routine. Its second derivative comes entirely from the exponential term, so the curvature bound in bound_interval is correct. All load edges, PWL knots, and the support/tail endpoints are explicitly split. Endpoint values are a lower diagnostic; endpoints plus curvature form the upper certificate.

The periodic initial state solves the high-five/low-five fixed-point equation

    z0=q5^2*z0+(100*q5+50)*v5,
    v5=b*(exp(5lambda)-1)/lambda.

The code's perstate expression agrees. At time 100, ten complete periods have elapsed, so the initial phase theta=(5-r) for high start or (10-r) for low start is again the correct periodic reference phase. Since battery injection is zero after 60, the future difference is homogeneous. The bound PER+max_i sum_j |CV_ij|*|residual_j| is valid for all t>=100 because every modal exponential decays in magnitude.

The recovery/SOC model is also internally consistent: support is nonnegative, recharge is nonpositive, and the trapezoid has area D/eta^2. Its loss-aware SOC change is -D/eta+eta*(D/eta^2)=0. Full common initial SOC E is essential to the claimed resource contract. Bounds on actual power, slew, and both endpoints of v=u+tau*u_dot control the whole affine-command interval; command jumps are explicitly allowed.

## 3. Continuous no-feedback lower relaxation

Let a_j and b_j be the true positive and negative AC-power integrals in a cell. Physical waveforms satisfy a_j,b_j>=0 and a_j+b_j<=P*h. The cumulative loss-aware depletion sum(a_j/eta-eta*b_j) is in [0,E] because initial SOC is full. Allowing both auxiliaries to be positive and ignoring intersample constraints, PCS, slew, recovery and terminal conditions only enlarges the feasible set.

For an output impulse kernel g and its cell mean W, the convolution replacement error is bounded by P*integral_cell |g-W|. The implementation's midpoint quadrature remainder is valid: if L bounds |g'|, then |g-W| is L-Lipschitz, and n midpoint panels have total integral error at most L*h^2/(4n). Its derivative bound

    L <= |g'(midpoint)|+(h/2)*sup_cell |g''|

uses the same stable-modal envelope correctly. Reversing the lag-cell means for each timestamp is the correct convolution indexing. Keeping only finitely many phases and generator-frequency sample times is appropriate for a necessary lower bound, not an all-phase upper.

The LP dual has nonpositive inequality multipliers. Negative reduced costs in the two finite cell-moment blocks are repaired using each variable's bound P*h. The E reduced cost must be nonnegative because no finite upper bound on E is used. In the saved h=.01 result it is positive even when the relevant multipliers are summed using exact binary-to-Decimal conversion:

    E reduced cost = 2.3657291403633706750042620114982128143310546875e-16.

The saved maximum positive dual violation is zero. The remaining kernel/dual arithmetic is ordinary floating point, as disclosed. An outward certificate would need to enclose this network calculation too; it is not inherited from the separate two-state interval certificate.

## 4. Timestamp boundary implementation caveat

The intended exact sensor theorem is correct: bins ((j-1)*.1,j*.1] share all future sampled stage histories because plateau length 5 equals exactly 50 sampling periods. The first-edge bin and subsequent integer shifts determine every sampled class.

The initially inspected p_class helper instead used

    floor((t-r)/5 + 1e-10).

This can flip a later edge early for phases just above a sample-grid boundary. For example t=5.1, r=.1000000001 is still before the second physical edge; the added tolerance can nevertheless increment the flip count. Such a phase then fails to share the offline helper's entire history with its bin midpoint. This is a numerical boundary artifact, not a counterexample to the exact information-bin theorem.

Recommended fix: define the offline mapping through the first sample-detection index, then use integer period shifts; equivalently use an explicitly exact decimal/rational timestamp convention. The physical controller consumes received classes and need not know r. Retain all frozen outcomes and disclose the boundary fix. The midpoint design and the listed finite holdout phases away from these boundaries are unaffected.

Closure at 03:07 UTC: directly inspected network_transfer/exact_observation_contract.py and BOUNDARY_CONTRACT_AUDIT.json. The replacement defines the first-edge index as ceil(10r), subsequent flips by integer 50-sample periods, and the online target solely from received measured P. All fifty midpoint mappings are unchanged. The original 1,388 boundary tests included 392 preserved legacy-helper disagreements; online measured-P reconstruction differs from exact-bin power by at most 8.88e-16 MW. The substantive equivalence/nonanticipativity issue is closed. Frozen coefficients and replay inputs were not changed.

Final parser closure at 03:13 UTC: directly inspected the replacement using fractions.Fraction and integer ceiling (10*numerator+denominator-1)//denominator. No finite decimal precision context or floating operation remains in phase-bin selection. Independently reran all 15 supplied 100-digit parser cases, including the exact rejection immediately above r=5; all passed. The expanded boundary report has 1,444 policy tests (including 56 long-phase policy checks), preserves the 392 legacy-helper disagreements, and keeps every frozen midpoint mapping unchanged. The optional 60-digit precision finding is closed.

The remaining numerical qualification is unchanged: the audit reports maximum command 50.00000000000077 MW and explicitly declares command tolerance 1e-9 MW. This is consistent with ordinary-floating numerical acceptance, not an outward proof of a strict exact 50 MW inequality. The network calculation must not be labeled interval-certified.

## 5. Claims that should remain separate

- All-phase/all-future LTI upper under the exact two-level/sampling/PCS/efficiency contract
- Same-family sampled-P versus initial-P-only constructive resource comparison
- Nonseparating lower for all measurable initial-P-only controls
- Finite frozen nonlinear confirmations and stresses, including any failures

Neither a finite nonlinear success nor the stronger same-family comparator converts the nonseparating universal lower into a universal network theorem. The changed network recovery contract also cannot be substituted for the two-state exact electrical reset at H20.
