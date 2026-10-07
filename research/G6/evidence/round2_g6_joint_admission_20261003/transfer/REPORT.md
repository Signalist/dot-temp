# G6: two-port, carried-state, continuous-time network transfer

## Result and interpretation

The same-information classical support calculation exactly reproduces the candidate. There is no new solver gain. The quantitative effect is a change in the admissible joint input set, together with the important distinction between fixed amplitudes and optional use independently chosen every block. These tests transfer that structural distinction to two independently qualified public linear network models.

The frozen supplemental ports have **zero baseline power** in both models. Their negative waveform segments are therefore signed incremental injections, not a demonstrated nonnegative physical compute load. Existing background constant-impedance demand cannot silently supply the missing controllable-compute baseline. Every MW number below is the total allowed **zero-mean fluctuation amplitude** along a specified allocation ray. It is not added average demand, nameplate adoption capacity, additional completed work, a new loadflow, or an operational nonlinear guarantee.

Equal-split ray: a=(0.5,0.5), a1+a2=1. The bracket [lower,upper] means a sufficient admissible radial amplitude from the analytic floating error bound, and a finite-word obstruction above the upper endpoint. All generator frequency deviations must remain within 0.05 Hz.

| Input contract | Kundur amplitude bracket (MW) | WECC amplitude bracket (MW) |
|---|---:|---:|
| Committed amplitudes, one common sign per block | 32.805328–32.884663 | 74.088449–74.376979 |
| Fixed optional adoption, one b in [0,a] forever | 32.805328–32.884663 | 67.795100–68.036614 |
| Dynamic optional use, independent b_k in [0,a] each block | 30.186622–30.253783 | 65.644634–65.871044 |
| Independent signed ports, information relaxation | 25.309284–25.356479 | 56.416271–56.583417 |
| Invalid reset-every-block screen | 118.292227–119.330307 | 100.954788–101.491272 |
| Invalid single-sign repeated-block screen, including startup | 91.373376–91.991522 | 80.398887–80.738774 |

At equal split, allowing amplitudes to vary independently each block reduces the committed-common threshold by at least 7.78% in Kundur and 11.09% in WECC. WECC also separates fixed optional adoption from a committed cohort: a committed-cohort feasible set need not be downward closed. Dynamic optional use retains an information benefit over independent signs: at least 19.05% in Kundur and 16.01% in WECC at equal split.

Across all 41 frozen rays, common versus independent and dynamic-optional versus independent decisions separate on all 39 interior rays for both models. Fixed-common versus dynamic-optional separates on 39 Kundur rays and 38 WECC rays. Maximum dynamic-optional improvement over independent signed ports is at least 24.28% for Kundur and 19.44% for WECC. These are information-contract gains, not algorithmic gains.

## Frozen physical contract and quantifiers

T=2 s, with four 0.5 s segments. Port 1 uses q1=(1,1,−1,−1), port 2 q2=(1,−1,−1,1). Each block has one shared s_k in {−1,+1}. With committed amplitudes δP_i(t)=s_k a_i q_i(t−kT); with dynamic optional use δP_i(t)=s_k b_ki q_i(t−kT), 0≤b_ki≤a_i. Both amplitudes are constant inside a block. Initial incremental electrical state is zero; it is subsequently carried continuously forever. No storage or electrical reset is introduced.

An explicit *conditional* workload law is required to use the words equal work: P_i(t)=P_i^0+δP_i(t) and dW_i/dt=ρ_i+κ_iδP_i(t), with fixed P_i^0≥a_i and ρ_i≥|κ_i|a_i. Since every template has zero area, each block has energy P_i^0T and work ρ_iT for all signs and allowed amplitude choices. The frozen supplemental ports in fact have P_i^0=0, so no nonzero symmetric amplitude can satisfy this nonnegative-load condition there. This law is therefore a separate conditional physical-realization proposition, not a physical property established for these frozen transfer experiments. Adding a positive compute baseline requires its own valid operating point, loadflow, relinearization and qualification. Existing background loads are not silently reclassified. The law is a declared affine workload assumption, not an empirical compute-power model. The network models have no representation that validates actual compute throughput. Background nonlinear load voltage dependence and finite-amplitude state changes are outside this local contract.

The distinct quantifiers are retained throughout:
- Committed: one a is fixed forever, every block sign may vary
- Fixed optional: for every fixed b in [0,a], that same b remains fixed forever
- Dynamic optional: each b_k may be chosen afresh each block
- Independent ports: every port/block sign may vary independently

## Exact support and same-information baseline

For output o and phase τ, let g_0(τ) be the two-port zero-start current-block coefficient, and g_(j+1)(τ)=C_o exp(A(τ+jT)) d_i be the coefficient of the j-th most recent completed block. All terms retain both port contributions before taking absolute value. The committed support is J_o(τ,a)=Σ_j |a·g_j(τ)|, including current j=0. The independent-port support is I_o(τ,a)=Σ_j Σ_i a_i|g_ji(τ)|.

For exactly two ports, dynamic optional support is D_o(τ,a)=Σ_j max{|a1 g_j1|,|a2 g_j2|,|a1 g_j1+a2 g_j2|}=0.5[J_o(τ,a)+I_o(τ,a)]. This identity holds coefficient-by-coefficient and is not an interchange of maximization and summation. The separately implemented vertex-support baseline matches within 1.31e−18 Hz/MW in Kundur and 1.09e−18 in WECC. The committed formula is the classical Minkowski/support series itself.

Fixed optional support is max of the three global peaks obtained at vertices (a1,0),(0,a2),(a1,a2); the zero vertex contributes zero. Convexity in the one fixed b justifies this vertex reduction. It does not give the dynamic contract.

Unrestricted-sign and optional supports grow monotonically with available history, so their infinite-history supremum dominates every zero-start prefix. A finite maximizing word of 256 past blocks plus the current partial block is a real zero-state startup witness. The single-sign comparator separately maximizes all prefixes, including startup, because its signed sums are not monotone. No run-limited language is asserted in this bounded network transfer.

## Continuous-time bounds, not sampled safety

The frozen rule uses N=256 past blocks and 2048 uniform phase intervals, h=2/2048 s, including every segment switch and both block endpoints. Neither model required prespecified refinement: the largest interpolation-plus-tail gap divided by the committed peak is 0.2539% for Kundur and 0.4714% for WECC.

For each stable modal residue R_omi and template integral I_i(λ_m,T), the omitted past-block tail for port i/output o is bounded by Σ_m |R_omi I_i(λ_m,T)| exp(Re(λ_m)TN)/(1−exp(Re(λ_m)T)). The radial error takes the maximum across outputs after multiplying by a. The current block is never truncated. Equal-split tail bounds are 2.24e−34 Hz/MW for Kundur and 1.13e−17 Hz/MW for WECC.

The phase error is (h/2)L. L is the smaller of a direct global first-derivative bound and a sampled sum-absolute first-derivative maximum plus the derivative tail and (h/2) times a global analytic second-derivative bound. At every segment switch, both one-sided derivatives are included. Within each segment the coefficients are analytic; frequency is continuous across input switches. The second derivative bound sums modal absolute values and integrates exp(Re λ t), including all infinite history. This yields a whole-continuous-phase inequality rather than a grid-only claim. Derivations and all numerical bound components are in run_transfer.py and *_bound_components.npz.

**All bounds apply to the numerically qualified stable modal kernel and are evaluated in ordinary floating point. The eigensystem/residue and source-model approximation error is not uniformly enclosed. No outward rounding, global interval proof, uniform descriptor/model-error bound, uncertain-parameter guarantee, or full nonlinear physical certificate is claimed.**

## Explicit numerical admission reversals

### Kundur

- dynamic_optional_vs_independent_relaxation: total fluctuation 27.771550 MW; dynamic_optional upper bound 0.045999766 Hz, while independent_ports has a finite witness at 0.054762237 Hz; separation 0.008762471 Hz
- fixed_cohort_not_optional_capacity: total fluctuation 31.529555 MW; committed upper bound 0.048055540 Hz, while dynamic_optional has a finite witness at 0.052108452 Hz; separation 0.004052912 Hz
- invalid_reset_screen: total fluctuation 75.588445 MW; screen upper bound 0.031949878 Hz, but a carried-state common-sign finite word produces 0.114929634 Hz
- invalid_single_sign_periodic_screen: total fluctuation 62.129019 MW; screen upper bound 0.033997332 Hz, but a carried-state common-sign finite word produces 0.094465040 Hz

### Wecc

- dynamic_optional_vs_independent_relaxation: total fluctuation 61.114025 MW; dynamic_optional upper bound 0.046549140 Hz, while independent_ports has a finite witness at 0.054003477 Hz; separation 0.007454337 Hz
- fixed_cohort_not_optional_capacity: total fluctuation 69.979747 MW; committed upper bound 0.047227164 Hz, while dynamic_optional has a finite witness at 0.053118747 Hz; separation 0.005891584 Hz
- invalid_reset_screen: total fluctuation 87.665883 MW; screen upper bound 0.043418388 Hz, but a carried-state common-sign finite word produces 0.058933479 Hz
- invalid_single_sign_periodic_screen: total fluctuation 77.387933 MW; screen upper bound 0.048127490 Hz, but a carried-state common-sign finite word produces 0.052024117 Hz

The rejected independent-port word belongs to a different, larger input set and is not a violation of the common-sign contract. In contrast, the dynamic-optional word demonstrates why a committed-cohort conclusion cannot be generalized to independent optional use. Reset and periodic witnesses directly violate the real carried-state common-sign contract while passing the invalid screen. Every ray’s decisions and full input words are retained.

## Qualification and independent checks

- Kundur: all 51 retained differential states, after the prequalified uniform-angle gauge removal; P@bus7 and P@bus8; all four generator frequencies. Original A,B,C resolvent tests pass. All 123 stored common/dynamic/independent finite words across 41 rays replay through original-state augmented matrix exponentials with maximum relative discrepancy 7.85e−14
- WECC: the original verified 2405×2405 descriptor, P@bus1 and P@bus4, all 29 generator frequencies. Algebraic elimination is followed by generalized finite residues and repeated-root block biorthogonalization. It does not use the rejected ordinary finite-state QZ model. Nine complex resolvent tests compare both input columns and every frequency output against direct sparse solves of the original descriptor
- WECC has 565 finite eigenvalues before grouping; only the structurally unobservable uniform-angle gauge is excluded. Its computed eigenvalue is 5.526e−13/s and frequency residue at most 1.454e−17. The rightmost retained real part is −0.0333333/s. The maximum repeated-eigenvalue biorthogonal condition number is 3.389e12; this severe conditioning is explicitly retained as a limitation despite accurate input-output checks
- Three full 256-past-block equal-split maximizing words also replay on the original WECC descriptor for 512–514 seconds, with no reset. Refinement dt=1/64,1/128,1/256 s produces approximately fourfold error reduction; the final maximum relative discrepancy is 4.032e−5. This corroborates the finite witnesses independently of the modal summation
- Independent direct full-descriptor evolution for the two templates converges through dt=1/1024 s, with maximum frequency discrepancy 1.174e−8 Hz/MW, 1.114e−5 relative to the peak. This is supplementary time-domain numerical qualification, not a nonlinear proof
- Exhaustive 2^12 common-sign and 7^4 optional-vertex word enumeration agrees with the finite support formulas to at most 2.17e−19 Hz/MW. Comparing explicitly summed lags N..2N with the analytic tail never exceeds the bound in the tested phases; this check supplements, rather than establishes, the analytic inequality

## Evidence and reproduction

- TRANSFER_FREEZE.json: analysis choices frozen before model support outcomes
- run_transfer.py: original qualified-model extraction, two-port lifted coefficients, all-time supports, phase/tail bounds, every-ray witnesses
- validate_transfer.py: independent small-word exhaustion, original Kundur state replay, tail checks, invalid-screen decisions
- verify_wecc_descriptor_time.py: independent original descriptor time-domain template qualification
- replay_wecc_witnesses.py: additional original descriptor long-horizon equal-split witness refinement
- *_coefficients.npy: full raw [output,phase,port,current+256-past] coefficient tensors. Kundur 4×2049×2×257; WECC 29×2049×2×257. These are approximately 278 MB (265 MiB) combined and can be distributed separately from the compact reproducibility core
- *_kernel.npz, *_bound_components.npz, *_support_arrays.npz, *_witnesses.npz: complete numerical kernel, error components, radial support results, and maximizing finite words
- *_rays.csv, *_decisions.json, *_summary.json, *_qualification.json, *_validation.json: machine-readable numerical results and caveats

Reproduce only this isolated transfer using existing numpy/scipy: OPENBLAS_NUM_THREADS=1 python run_transfer.py; then python validate_transfer.py kundur wecc. The source public-model files are read-only. This linear replay uses the qualified numerical fixtures without changing the source models.

## Conclusion for the G6 innovation gate

This is a valid structural/application result: the joint block input contract changes numerical admission decisions, persists with carried state on two multiport public network models, and is not erased by continuous-time tail/interpolation error bounds. The result does not pass as a novel admission solver, because the strongest same-information mature support baseline is identical. The dynamic-optional amendment is necessary; ignoring it overstates standard capacity-like conclusions. Any claim about added compute load, operating-point changes, nonlinear limits, measured workload equivalence, or interval-certified numerical robustness requires a separate study.
