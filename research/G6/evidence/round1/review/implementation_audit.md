# G6 implementation audit

Date: 2026-10-02. Reviewed `src/g6_model.py`, `src/run_certificates.py`, the frozen protocol and arithmetic amendment. Production files were not edited by this reviewer. Review-only scripts and results are in this directory.

## Verdict

After the two recorded arithmetic corrections, no algebraic sign, normalization, parameter-coverage, or phase-curvature underbound was found. The design4 saved certificate was independently replayed in full: its 8,001 rectangles form an exact endpoint-matching partition of the padded continuous parameter domain, every stored upper bound was reproduced bit-for-bit, the global upper equals their maximum, and all lower witnesses were reproduced at points inside the nominal decimal domain.

This is a valid conditional enclosure under the stated arithmetic/backend assumptions, with a wide unresolved tightness gap. The current design4 `max_relative_gap=0.15342555289879944` and `tolerance_met=false` must remain visible. It is not a 2%-accurate frontier. The full exact shared-kappa frontier is not computed by these files.

## Blocking defects found in the initial version, now corrected

1. Ordinary `mpmath` values expanded by adjacent binary64 numbers did not enclose exact trigonometric grid zeros. Reproduction: the original interval for sin(pi) was [1.0716696564844045e-81, 1.071669656484405e-81], excluding the exact value 0. The assertion in `iconst` only checked the approximate mpmath value. Replacing pi/sin/cos generation with `mpmath.iv` followed by outward conversion fixes this example and the reviewed constant-generation contract.
2. Adding nonnegative squared interval lower endpoints can produce a negative subnormal under outward rounding. Calling sqrt on that value could produce NaN. Clipping the sum-of-squares lower bound to zero before sqrt is mathematically valid and fixes this issue.

The parent preserved the invalid run and recorded `stage0/AMENDMENT_01_ARITHMETIC.md`. Only fresh post-fix results are accepted here.

## Algebra and units

The transfer implementation corresponds to

    theta_dot = 2*pi*Delta_f,
    M*Delta_f_dot = -D*Delta_f - kappa*L*theta - p.

Thus the modal angle denominator is

    kappa*lambda - M*omega^2/(2*pi) + i*D*omega/(2*pi),

with a negative angle response to positive demand p. Frequency output multiplies the angle response by i*omega/(2*pi); oriented line flow is kappa*K*(theta_i-theta_j). Both signs and 2*pi factors in `transfer`, `transfer_interval` and `linear_state` are consistent with this convention.

The returned transfer coefficients are **normalized constraint ratios per MW of fundamental amplitude**, not Hz/MW or physical MW/MW: frequency is divided by 0.05 Hz and line flow by 15 MW. Current labels `f_Hz_bus...` and `flow_MW_...` can mislead if copied directly to figures. Declare normalized units in saved metadata/plots, or convert back before attaching physical units. M has compatible units MW*s/Hz, D MW/Hz and K MW/rad under this convention; the numbers are synthetic.

XOR modal residues are exact dyadic rationals for n=4 or 8. Integer eigenvalues and direct Laplacian/modal diagonalization were checked exactly for all four listed models. Every nonzero mode is positive. The complete angle-state model still has a free uniform-angle mode; do not call its full A Hurwitz. That mode does not invalidate the stated zero-mean steady-periodic frequency/line-flow response: an arbitrary constant common angle is unobservable in these outputs.

For input sin(h*theta)/h and complex transfer H(h*f), the real response is

    Re(H)/h * sin(h*theta) + Im(H)/h * cos(h*theta).

The implementation matches this. Because h=1,3,5 are all odd,

    q(theta+pi) = -q(theta).

Therefore positive maximum, negative maximum in magnitude and absolute peak coincide. One signed support array is sufficient for symmetric frequency/flow limits. This shortcut would cease to be valid if an even harmonic, DC component or asymmetric threshold were introduced.

## Interval and phase logic

- Basic interval +, -, multiplication, division away from zero and square use outward expansion. Sequential summation avoids reliance on a floating-point reduction order. Exact integer/dyadic inputs are representable; pi and trigonometric grid constants now come from the interval backend.
- The imaginary modal denominator is nonzero over the declared positive-frequency domain, so the squared modulus used for complex inversion remains positive when needed by division. Repeated appearances of pi, f and kappa widen the intervals but do not invalidate inclusion.
- For q(theta)=sum_h q_h(theta), |q''| <= sum_h h^2*|H_h|/h. A smooth periodic maximizer has derivative zero and is within Delta/2 of a grid point. Taylor's theorem gives max q <= max_grid q + Delta^2*max|q''|/8. The implemented term has the correct factor and harmonic powers.
- Point evaluations give lower bounds only. The saved upper comes from every retained leaf's interval upper, not from the seeds or root-finding oracle. Stale priority-queue scores can affect efficiency but cannot invalidate this cover.
- The padded binary64 root rectangle contains the exact decimal domain [0.08,0.75] x [0.85,1.15]. A shared bisection endpoint creates no gap. The design4 saved lower witnesses all fall inside the unpadded nominal domain.
- Initial seed lower values and root-solver diagnostic values are not used as upper bounds. The stationary-polynomial root solver is an ordinary floating-point cross-check, not a certified root isolator; that is acceptable in its current diagnostic role.
- When the node budget is exhausted, all queued leaves are retained. This correctly preserves a valid upper enclosure while reporting failure to meet tightness tolerance.

The arithmetic claim depends on standard correctly rounded binary64 basic operations/sqrt, no flush-to-zero mode and a trusted supported interval implementation for pi/sin/cos. Pin NumPy, mpmath and source versions. mpmath's official documentation describes interval inclusion but flags the interval context as experimental; it does not turn ordinary high precision into a proof. The reviewed installed versions were NumPy 2.3.5 and mpmath 1.3.0. Official documentation: https://mpmath.org/doc/current/contexts.html and https://mpmath.org/doc/current/technical.html .

## Important mathematical-baseline qualification

The fixed-parameter site support oracle is the classical exact template support problem. However the candidate joint region uses

    sum_i a_i sup_kappa m_ji(kappa),

whereas the strongest same-information exact joint region uses

    sup_kappa sum_i a_i m_ji(kappa).

These are generally different; the former is conservative. Fixed-parameter stationary-root agreement does not establish execution or equality of the full shared-kappa robust capacity baseline. The frozen protocol should retain its conservative-relaxation disclosure and qualify any blanket statement that the complete candidate and exact baseline have the same boundary. Equality for a particular model would require evidence. No additional optimizer is required to be honest: report the full shared-kappa frontier as not computed and keep `paper_ready=false`.

## Remaining nonblocking release cautions

- `maxboxes=16000` currently permits 16,001 evaluations because a split adds two after checking the old count. This is not an enclosure defect, but the recorded effective count rather than a strict 16,000 cap must be reported.
- The metadata does not yet bind each result to source/protocol hashes, backend versions and the input template. The review output captures the current model hash and artifact hash; production provenance should also capture the runner and arithmetic amendment.
- Downstream capacity polygons and accepted points still need a final outward-rounded feasibility check against the certified coefficient matrix. A floating-point polygon intersection is not automatically a rigorous inner polytope vertex certificate. An area computed from ordinary vertices is a numerical summary unless separately enclosed.
- A relative-gap comparison performed in ordinary floating point can be off by rounding at the exact tolerance boundary. It does not affect the physical coefficient upper bound. Use outward gap evaluation if advertising mathematically exact tolerance satisfaction.
- The finite 1/3/5 actual-PCC template has no omitted harmonic tail by definition. Any use of a real square wave, extra harmonics, duty changes or frequency drift is a different contract, not a zero-tail consequence of this certificate.
- The actual input scale is fundamental amplitude a_i in MW. It is neither rated data-center MW nor average useful compute throughput.

## Reproducible checks completed

`audit_implementation.py` and `implementation_diagnostics.json`:

- 1,536 sine/cosine grid entries: quadrantal values checked exactly, remaining values compared against 140-digit independent evaluation; no failures
- 17,280 scalar real/imag transfer components across four models, three harmonics and 20 fixed random parameter points per model enclosed their independent 140-digit formula values; no failures
- Four exact Laplacian/modal diagonalization identities passed
- Direct-network versus modal normalized transfer disagreement at most 4.443059973708341e-16
- 80 fixed-parameter stationary-root maxima fell inside the corresponding point-parameter phase-grid/curvature brackets
- Half-wave antisymmetry residuals in floating diagnostics were below 9e-17
- These finite diagnostics are not a substitute for the analytic interval inclusion argument

`replay_certificate.py design4` and `design4_certificate_replay.json`:

- All 8,001 saved leaves passed an exact endpoint-order partition check, with neither holes nor overlapping interiors
- All 8,001 saved leaf upper bounds matched fresh post-fix evaluation bit-for-bit
- Saved global upper equaled max over leaf uppers exactly
- All saved lower witnesses reproduced their bound and belonged to the nominal domain
- All arrays were finite; source remained unchanged during replay
- Artifact SHA256: de748090b289f8e861f1aec6ec576984e00763a4481392f27a38f84a51a08719
- Reviewed model SHA256: c8e399945e2a63bf6923fef0ec8179c7ee1917338f1bb676d96675f2a90774ed
- Reviewed runner SHA256: 88a2bdb0bca49f7857513d3b6e7b35f5fd4fee39cdc616498cadf25a91d4dc0c
- Frozen protocol SHA256: e1df664a1bace4d66286aa4f0debe5f3b725412de29b19341da023162d9f862a

No claim is made that the other three saved certificates have been fully replayed by this reviewer at this stage. No production files, model choices or optimization parameters were changed.

## Addendum: resolvent refinement and shared-kappa strip proposal

The preceding full replay and hashes concern the preserved rectangular v1 implementation/results, now also retained under `raw/rectangle_v1`. The following review concerns model source SHA256 `c9cefdd319c40411658d005d28edd9d4a4480d069e25dbdb7d69fc132f82d6c6` and `AMENDMENT_02_RESOLVENT.md`. Do not associate the v1 full replay with a new refined certificate.

The resolvent refinement is sound on algebraic inspection. For each modal denominator d(p) and center dc, the code obtains an upper rho on |d-dc| and a lower dcmin on |dc|. With margin=dcmin-rho>0, it bounds

    |1/d - 1/dc| <= rho/(dcmin*margin),
    |1/d| <= 1/margin.

All signs in these inequalities are used conservatively: rho is upper, dcmin/margin are lower, and subsequent ratios/sums are outward bounded. For a modal sum S=sum_m r_m/d_m, the sums sr and sm bound |S-Sc| and |S|. For transfer H=N(p)S(p), the exact identity

    H-Hc = Nc*(S-Sc) + (N-Nc)*S

justifies the implemented radius |Nc|*sr + |N-Nc|*sm. Both frequency and line-flow numerator variation are included. The center transfer itself is enclosed by the original rectangular method. The final intersection of two enclosing rectangles is valid. Requiring all modal margins positive can lose tightening opportunities but is safe. The split weighting changes efficiency only and need not itself be a certified derivative bound.

Fresh-seed diagnostics (`audit_resolvent.py`, `resolvent_diagnostics.json`, seed 6022027) evaluated 240 nonzero-width box/harmonic combinations across all four plants. The refinement actually changed 226 enclosures. Across 86,400 real/imaginary scalar components at box corners and centers, independently evaluated at 140 digits, there were no containment failures, empty intersections or interval enlargements. The source did not change during the checks. These are diagnostics supporting the inspected proof, not a proof of the whole domain by sampling. A saved post-refinement certificate has not yet been replayed by this reviewer.

The proposed stronger shared-kappa construction is also sound subject to explicit coverage checks. Partition kappa at every saved leaf boundary. For each resulting closed strip [k_l,k_u], select leaves whose kappa interval contains that entire strip. Verify their frequency intervals cover the entire declared frequency domain. Then, for each monitor j and site i,

    U_strip,j,i = max_selected_leaf leaf_upper[j,i]

bounds the phase/frequency site support for every kappa in that strip. For a>=0,

    sup_kappa sum_i a_i m_ji(kappa)
      <= max_strip sum_i a_i U_strip,j,i
      <= sum_i a_i max_all_leaves leaf_upper[j,i].

Use outward-rounded weighted sums, retain boundary strips/points, and preserve nonnegative amplitudes. This gives a certified approximation to the exact shared-kappa envelope that is at least as strong as the independent-kappa relaxation. It does not establish an exact frontier or a 2% shared-envelope gap without compatible common-kappa lower witnesses and a matching objective-wise upper/lower comparison. The lower support witnesses used for a weighted sum must all use the same kappa; each site may independently choose its frequency and phase under the contract.

## Final design4 certificate and envelope audit

The final refined design4 certificate completed at 33,053 evaluations with 16,527 retained leaves, `max_relative_gap=0.019998365812185077`, and `tolerance_met=true`. A full fresh replay against the resolvent source `c9cefdd...` succeeded:

- Every one of the 16,527 leaf upper arrays reproduced bit-for-bit
- The exact binary-endpoint partition check found no holes or overlapping interiors
- Global upper equals the maximum leaf upper exactly
- All saved lower witnesses reproduce and lie inside the nominal exact-decimal parameter domain
- Arrays were finite and source remained unchanged during replay
- Final certificate artifact SHA256: `00fd39bd444ce54131475c0ce94308135d9ffa4033052871867f63d7fae4a62d`
- Full replay record: `design4_certificate_replay.json`; the earlier replay remains separately in `design4_certificate_replay_rectangle_v1.json`

The final shared-kappa construction has 294 strips. Independent checking confirmed that every selected leaf contains its entire closed strip, each strip's frequency intervals cover the padded full frequency range, saved shared bounds reproduce exactly, and shared bounds do not exceed the independent-kappa maxima.

### Additional defects caught and corrected before accepting envelope exports

1. The first sample-lower kappa grid used floating literal 0.85, which lies just below exact decimal 0.85. Its endpoint was moved inward, with the upper endpoint also consistently moved inward. The full corrected lower-support arrays now replay at feasible parameter tuples.
2. The original saved `sample_witness` phases came from a 64-phase search while the certified lower support came from a 256-phase grid. They are now labeled `sample_search_seed`, and separate validated template/l1 frequencies plus the 256-grid size are saved. These reproduce the actual lower support; no claim is made that a search-seed phase attains that bound.
3. Originally only polygons were inward-shrunk/verified; scalar capacities and allocation rays were ordinary numerical boundary values, and polygon area was measured before shrinking. All safe exported amplitudes now receive inward scaling and an outward feasibility check. Area is recomputed from the stored polygon and explicitly labeled a numerical geometry estimate.
4. Nonlinear challenge metadata originally used an ambiguous `out_of_contract` flag. It now distinguishes `waveform_or_initial_contract_breach` from `nonlinear_model_extension`, and saves both requested and effective clipped drift amplitudes.

`audit_envelope_artifacts.py` and `design4_envelope_artifact_audit.json` replayed the corrected saved design4 envelope. All lower-support entries matched, all lower witness parameters were feasible, and every exported safe polygon vertex, axis/balanced endpoint and allocation-ray point was nonnegative and outward-feasible. The largest outward constraint ratio among these exports was 0.9999999999000005. The envelope artifact was unchanged during review.

- Final reviewed analyzer SHA256: `b8efa577199d9f491d456b85acf8a5a0a20c710941e21c7196bd9a66a329dc6e`
- Corrected envelope artifact SHA256: `8134df9b2bbe7ef43a4315bf21964cffba45a72c15e39f2ac2d197b7a1ac9fa5`
- Reviewed challenge code SHA256: `f63f54e091fc2545dce547ccef5e028c10427c2445ef93c7a58ba99f0da5de9d`

### Challenge bookkeeping review

The design4 case file contains 40 paired fixed-template base scenarios, each evaluated by four methods (160 method-runs), plus 36 variants of selected base scenarios. These are not 196 independent statistical observations. Realizations are saved and hashed before integration. Full states and actual PCC loads are saved; the overall worst case and the worst fixed-template shared-baseline case get dt/2 reruns. The drift phase formula differentiates to f_i + drift_i*sin(2*pi*t/35), so clipping drift as implemented preserves the frequency band.

All simulations use nonlinear sin(angle) flows and linear-periodic rather than nonlinear-periodic initial states. Thus even fixed-template cases are nonlinear stress tests outside the LTI theorem, not certified nonlinear trajectories. The metadata states this limitation. Peaks are sampled in time; RK4/dt-half comparisons are numerical convergence diagnostics, not continuous-time nonlinear certificates. Contract-break variants with no observed violations do not establish robustness to those violations.

No further blocker was found in this bounded code and design4-artifact review. The other plants' final certificates were not fully replayed here. Source-version binding, arithmetic-backend assumptions, conditional synthetic scope, classical baseline positioning and `paper_ready=false` limitations remain applicable.

## Interior4 and transfer8_cube final audits

Both final certificates were fully replayed against unchanged resolvent source SHA256 `c9cefdd319c40411658d005d28edd9d4a4480d069e25dbdb7d69fc132f82d6c6`.

- **interior4:** 29,479 evaluations, 14,740 leaves. Every leaf upper reproduced bit-for-bit. Exact partition coverage, finite arrays, global leaf maximum and feasible/reproduced lower witnesses all passed. Reported maximum relative support gap is 0.01999933326588847; the 2% target is met. Certificate SHA256: `07ea763b6e593288cb02302a947364bdb233b490cdd5bd7944988d079a7bfb43`.
- **transfer8_cube:** 60,001 evaluations, 30,001 leaves. Every leaf upper reproduced bit-for-bit. The same coverage, finite-array and witness checks passed. Reported maximum relative support gap is 0.029988803415185533; **the 2% target is not met**. This is a valid wider enclosure after budget exhaustion, not a 2% result or a proof of an exact frontier. Certificate SHA256: `966a9e4565dfbe9eac318ac263d2bfa402f63a3bba4a9e0e5b0be71f4d161580`.

Complete replay records are `interior4_certificate_replay.json` and `transfer8_cube_certificate_replay.json`. They explicitly preserve the producer's tightness status separately from successful enclosure replay.

Their envelope audits also passed. Interior4 has 295 closed kappa strips and cube has 297; every selected leaf contains the full strip, all strip frequency covers are complete, and saved shared coefficients reproduce exactly and do not exceed independent-kappa maxima. All saved template and phase-free l1 lower coefficients reproduce at feasible kappa/frequency witnesses. The newly added phase-free sampled outer constraints are the same necessary-halfspace construction applied to validated l1 support lower bounds. All exported safe vertices, endpoint capacities and allocation rays were nonnegative and passed outward feasibility, with largest checked ratio 0.9999999999000005. Area remains explicitly a numerical geometry estimate.

- Reviewed analyzer SHA256: `77612d0115dabde006f11734a72aa069e780e1fae0c1d9d70704eec451e1fe0e`
- Interior4 envelope SHA256: `f147a24221cca781f051c9ae2627930dc970b17b6bd1eead57eddbd5e94214cc`
- Cube envelope SHA256: `a3ee10006b908a7c38bfbe86f01036fe851e8e97531f6bad9f006574a8eaf95f`
- Detailed records: `interior4_envelope_artifact_audit.json`, `transfer8_cube_envelope_artifact_audit.json`

An economical raw-data audit read all stored coarse trajectory chunks for both models without running a new integration. Each model's chunks cover exactly cases 0 through 195, all arrays are finite, case-file hashes match metadata, peak ratios recomputed from saved states match stored ratios and CSV values exactly, and grouped violation counts match the saved summaries. Loads reconstructed at four stored times per chunk agree within 2.503e-13 MW for interior4 and 5.860e-13 MW for cube, consistent with floating-point timestamp evaluation. Each trace chunk's hash and shape are retained in `interior4_trace_artifact_audit.json` and `transfer8_cube_trace_artifact_audit.json`. This checks artifact consistency, not nonlinear integration accuracy or continuous-time safety.

The proof report `reports/CONTINUOUS_ENCLOSURE_PROOF_ZH.md` was reviewed for substantive mathematical errors; none was found in the reviewed version, SHA256 `54bb389ec7ad2c4bc9edd54113bfd9a3039caa3f503f3720067c77bdefb3eec6`. In particular, the 14a/15 template absolute peak is correct, the common-angle zero mode is disclosed, shared-kappa quantifiers are correct, the resolvent numerator variation is retained, the curvature coefficient is correct, and numerical areas/nonlinear stress results are not promoted to continuous safety or exact-region gain claims.

The final transfer8_mesh certificate has not been reviewed in this addendum. No production files were modified, and no new optimization or time integration was run by this reviewer.

## Mesh final replay and final all-four status

The final transfer8_mesh certificate passed full replay against unchanged source `c9cefdd319c40411658d005d28edd9d4a4480d069e25dbdb7d69fc132f82d6c6`: all 30,001 leaf upper bounds matched bit-for-bit; exact endpoint partition, finite arrays, feasible reproduced lower witnesses and global upper aggregation passed. The source stayed unchanged. Certificate SHA256: `2c5349cd3886755b8e3abd3d82ff02b810d3f27318fe0a933c47b7bc9698cf63`.

The mesh result used 60,001 evaluations and has maximum relative support gap 0.028135006052652584. Its 2% tightness target is **not met**. This does not imply infeasibility; its wider upper enclosure remains valid. Mesh's 367 shared-kappa strips, saved template/l1 lower coefficients and safe exports all passed the same independent artifact audit. Envelope SHA256: `a438dd33cc26bff4c0fe174e399f61c3453efd69293ca79cafe602310ecfb192`.

All mesh coarse trace chunks were also checked without reintegration: exact case coverage, finite arrays, case-file hash matching metadata, and recomputed peak ratios/CSV summary counts all passed. Four-time load reconstruction checks differed by at most 5.663e-13 MW. The latest design4 envelope, including the subsequently added phase-free sampled outer constraints, was re-audited successfully; its current envelope SHA256 is `ab88bf51036fdfe853ecfde8796585241cb627e637cf8c3d0a2a51cb1811176d`. Design4 coarse traces were checked with the same routine and passed, with load reconstruction error at most 3.451e-13 MW.

The final all-four total is 91,269 completely replayed leaves, 1,253 audited shared-kappa strips and 974 outward-verified exported safe points. Design4/interior4 meet the support tightness target; cube/mesh do not. Current artifact versions and individual hashes were reconciled in `FINAL_ALL_FOUR_VERIFICATION.json`; the concise narrative is `FINAL_ALL_FOUR_VERIFICATION.md`.

The assumption ledger's claim that a future contract must be nonseparable was flagged as overly universal. The parent amended it to a chosen project-specific reopening criterion and distinguished historical observations from an enforced future waveform contract. The amended ledger has no remaining substantive issue in this review. No production files were modified by this reviewer.
