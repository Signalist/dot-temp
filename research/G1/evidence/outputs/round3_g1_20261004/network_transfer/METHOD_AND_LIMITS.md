# Network transfer of the information contract

## Result type and scope

This study transfers the **information contract**, not the two-state theorem, to the qualified full Kundur model. It constructs an ordinary robust sampled-disturbance-feedback LP controller on the 51-state stable quotient (only the uniform rotor-angle gauge is removed). It also constructs an initial-P-only controller in the same conventional family. The grid equations, machines, governors, exciters, background ZIP convention, parameters and operating point are unchanged from the round2 qualification.

The input is synthetic and externally imposed: supplemental active demand at bus8 is 50/100 MW, alternates every five seconds, and continues after battery service ends. No GPU-to-PCC measurement claim, equipment sizing claim, hardware verification or operational safety claim follows. The endpoint is maximum absolute frequency deviation of **each of four generators**, with research band 0.1 Hz. COI is an additional diagnostic, never a substitute. Voltage results are reported, but no voltage compliance criterion is certified.

## Shared observation and service contract

The grid starts at its recovered original equilibrium. Reconnection is at absolute time1 s, relative time0. The initial high/low class is known, but remaining time r in the first stage is unknown, with 0<r<=5 s. Subsequent samples of P occur at relative 0.1,0.2,... s and arrive 0.05 s later. Errors satisfy |n|<=5 MW, i.e. 10% of the 50 MW step and strictly below half the separation. Threshold75 MW gives the exact plateau class for every such error. The controller receives the time, this delayed class history and its own applied battery power. It receives no frequency, network state, exact phase, true future samples, or arbitrary future trajectory.

Both controller families have 50 MW effective active-power headroom, known matched first-order PCS time constant tau=.05 s, maximum actual-power slew500 MW/s, eta_c=eta_d=.95, and full initial usable SOC E. The same global E is used for both possible initial classes; a phase-dependent excursion smaller than E simply leaves unused charge. Recovery restores that initial SOC exactly by relative60 s. Actual battery power is zero thereafter, while the periodic load continues. There is no imposed exact network-state reset: the correct stable-LTI tail reference is the forced periodic orbit. This differs from an exact-state-reset contract and must not be mixed with it.

## Conventional causal reference controller

Actual battery power u is continuous piecewise linear. Its support-stage knots are0,.05,.15,...,12.15 s, with u(0)=u(12.15)=0. A target at the next knot is selected at the beginning of the intervening ramp, from fixed coefficients indexed by elapsed time, known initial class and latest **received** P class. For example, the sample at .1 s arrives at .15 s and first affects the target at .25 s. This deliberate finite-ramp response is part of the conventional implementation, not hidden zero-delay feedback. The first targets use the known initial class.

The reference targets are nonnegative during support. Their common LP coefficients are optimized across all50 observation-history bins. The initial-P-only variant ties the two later-class targets at each time, so it has exactly the same initial information and actuator/recovery family but no use of subsequent P. Neither family is a novel control algorithm. The LP is a restricted constructive resource upper-bound search, not global optimization over all causal policies.

For every ramp, the matched PCS command is v=u+tau*u_dot. Bounds are imposed on actual power, both affine-command endpoints and slope; hence they hold throughout each segment. Command jumps at target knots are allowed; actual power is continuous. This is a finite active-power-service model, not an EMT/current-limit model or robustness to unknown tau.

Let D be the actual AC discharge area accumulated during support, reconstructed from applied power. After support completes, the controller charges with a fixed trapezoid:0 at20 s, plateau -D/(eta^2*39) at21..59 s, and0 at60 s. Its charging area is D/eta^2, so the exact signed loss-aware SOC change is -D/eta+eta*(D/eta^2)=0. Each interval has a fixed sign; there are no simultaneous charge/discharge variables in the constructed service. The required usable excursion is D/eta. Recovery amplitude is computed only after D has been observed, so no future phase is used. All confirmation schedules are independently reconstructed from timestamped noisy measurements and checked against the analytical history mapping.

## Why fifty bins give a meaningful LTI certificate

For fixed initial class, the complete received class history is the same for every r in a bin ((j-1)*.1,j*.1], because the alternating period is exactly10 s and sampling is exactly.1 s. The controller consequently produces the **same entire actual-power trajectory** for all phases in that bin, including the debt-based recovery. A representative r_j=(j-.5)*.1 therefore proves the hardware and SOC bounds for its whole bin. This is an information-equivalence argument, not a claim that nearby optimized trajectories are continuous.

The remaining phase dependence is only in the uncontrolled LTI response. Write g(t)=C exp(A t) B for t>=0. Differentiating the free response with respect to r gives plus or minus50 times the alternating impulse train

q(t)=sum_{k>=0}(-1)^k g(t-5k),

where causal terms with negative argument vanish. On t=5m+a, 0<=a<5, each modal coefficient is

b_i exp(lambda_i a) (-1)^m [1-(-exp(5 lambda_i))^(m+1)]/[1+exp(5 lambda_i)].

The implementation bounds the first20 five-second segments using analytic exponential curvature enclosures. For later segments it bounds the limiting periodic impulse response plus the geometric residual. It obtains an all-future phase Lipschitz constant0.0887232453644 Hz/s. A representative is at most.05 s from any phase in its bin, giving a uniform allowance0.00443616226822 Hz. This remains valid at load jumps because frequency has no direct feedthrough and is continuous; the bounded one-sided phase derivatives imply the Lipschitz bound.

For each representative trajectory, exact modal propagation over every PWL/load interval plus a second-derivative interpolation bound yields a continuous-time peak upper bound. The periodic orbit and modal residual at100 s yield an all-future tail bound. Adding the uniform phase allowance establishes all-phase/all-future admissibility **in the supplied stable LTI model**, under the exact observation, input, PCS and efficiency contract. These are rigorous-form analytic inequalities evaluated in ordinary floating point. There is no directed-rounding/interval-arithmetic proof, and no transfer of the bound to the nonlinear system.

## Resource result and fair interpretation

At the common0.093 Hz midpoint design target, with the same0.1 Hz research acceptance band and all other constants fixed:

- Sampled-P conventional family: maximum usable excursion94.264936753 MWs =0.026184704654 MWh; all-phase/all-future LTI upper0.0974523987564 Hz
- Initial-P-only conventional family: maximum usable excursion127.134534346 MWs =0.035315148429 MWh; all-phase/all-future LTI upper0.0974572800956 Hz
- Difference32.869597593 MWs, or25.8541849092% of the initial-P-only family's upper bound

The high-start branch excursions are70.046221637 and83.425783721 MWs respectively; the low-start branches determine the common E. Both families use the same full initial SOC and recovery rule. This is a same-family resource comparison of two conventional controllers. It does **not** establish a universal optimal resource gap, superiority over ordinary feedback, battery nameplate/capital-cost savings, or compute-exclusive behavior.

## Continuous initial-P-only lower bound: deliberately non-separating

A separate terminal-free prefix relaxation covers arbitrary bounded measurable open-loop active injection at P<=50 MW. For each control cell it introduces the true positive and negative power integrals. Their sum is bounded by50 times the cell duration; cumulative signed loss-aware depletion lies in[0,E]. Allowing simultaneous positive/negative auxiliaries enlarges the feasible set and is used only in this lower-bound relaxation, never to synthesize a physical battery service.

Sampled-frequency convolution is approximated by cell-mean kernels, with an explicit worst-case remainder for arbitrary within-cell bounded waveforms. The integral of |g-mean(g)| is upper bounded by midpoint quadrature plus a derivative-envelope remainder. Thus the relaxation includes every measurable physical input, rather than incorrectly assuming unknown controls were ZOH. Terminal SOC, recovery, slew and PCS constraints are removed. A repaired feasible LP dual gives a lower bound in the LTI model only.

The10 s low-start prefix gives60.804948631 MWs on.02 s cells and64.616246553 MWs on.01 s cells. The latter's maximum frequency remainder is0.00134211576201 Hz. Both are below94.264936753 MWs. Therefore this calculation **does not certify a universal information-resource separation on Kundur**. The no-feedback lower bound is useful negative evidence; it is not silently replaced by the stronger restricted-family comparator.

## Preserved development failures

The first sparse phase-training set (eleven remaining-stage values) produced a feedback schedule that appeared feasible on its design set but violated the50 MW command cap at untrained phases, reaching74.778313109 MW. It is retained in the development phase sweep and is rejected as a controller witness. This is why the final design uses every observation-history bin; a phase plot alone would have missed the actuator defect.

At the stronger0.0915 Hz midpoint target, the initial-P-only low-start restricted family becomes infeasible after adding off-grid frequency violations. Its initially feasible coarse-output LP is not accepted as a solution. The two feedback branches and high-start open-loop branch at that tighter target are retained as development sensitivities, not mixed into the common0.093 comparison.

## Nonlinear confirmation discipline

HOLDOUT_PLAN.json predeclares four previously unevaluated remaining-stage values (.137,.813,2.347,4.927 s), both initial classes, both conventional controllers, four amplitude/shape stresses, and two timestep repeats. CONFIRMATION_FREEZE.json hashes all22 inputs, fixed coefficients and independent noisy-observation records before the first new nonlinear evaluation. None of these exact holdout phases was used in design or the earlier.025 s diagnostic sweep.

Replays use unchanged ANDES2.0.0 Kundur equations, exact IT ZOH timestamps, and actual BESS PWL interpolation; they do not reoptimize from exact phase. The nominal errors alternate +5,-5 MW. Every bounded error of this magnitude gives the same nominal class history, but that invariance does not extend to the ramped-input stress. The ramp stress is explicitly a.5 s transition represented by.01 s ZOH steps, not an exact smooth nonlinear input.

All outcomes, including failures, are retained. A finite successful nonlinear trajectory is empirical benchmark evidence, not an all-phase/all-future nonlinear guarantee, a unique-attractor proof, or an independent statistical trial. The service command and loss-accounting assumptions are checked separately from the grid replay. ANDES HOME, generated pycode and MPL caches are isolated in the new round3 directory;266 round2 source/cache/model files are locked and checked again afterward.

## Reproduction and provenance

Use the existing round2 andes_env Python; do not redistribute the environment. Commands and compact manifest are in REPRODUCE.md. Core model and original source qualifications are in round2/grid_transfer/README_qualification.md and ORIGINAL_SOURCE_INTEGRITY_CHECK.json. The unchanged workbook SHA-256 isf725e03ba12d8207616f68acdd606bbd35e7c4a68f13e66d7db43925adac2ed8. The model/source locks, complete solver logs, controller arrays, physical certificates, lower-bound duals, freezes and nonlinear outcomes are retained separately.

## Exact sample-boundary implementation audit

Independent review identified that the frozen development helper p_class contains a small epsilon inside a floor operation. Although harmless at all saved representatives and confirmation phases, it can advance a later synthetic transition for a phase infinitesimally above a sample boundary. That numerical helper is therefore not the semantics of the continuum controller claim.

The exact contract is now explicitly implemented in exact_observation_contract.py: represent a sample by its integer index n, set the first-edge index to ceil(10r), and repeat each edge after exactly50 sample indices. The corresponding bin is ((j-1)/10,j/10]. The deployable online law takes only measured samples and the known initial class; it never takes r or an inferred exact phase. BOUNDARY_CONTRACT_AUDIT.json records1,444 one-sided/at-boundary tests, exact equality of every saved representative mapping, and online-versus-bin power agreement to8.88e-16 MW. It also retains392 test cases where the old helper's class history differs, rather than hiding the discrepancy.

Frozen coefficients, inputs, nonlinear runs, and representative LTI results are unchanged. All50 exact history mappings have the same command/slew/energy bounds as before. The geometric bin radius remains.05 s, so the continuous LTI phase certificate applies to this exact online policy without enlarging the phase allowance. Do not use the epsilon-tolerant frozen helper to generate infinitesimal-boundary policies in later studies; use the exact contract implementation and timestamped observed classes.

## Completed nonlinear results and model-mismatch boundary

All22 originally frozen evaluations complete to101 s and remain below0.1 Hz. The eight nominal unseen phases for each controller have maximum peaks0.0935791203882 Hz (sampled P) and0.0928075363652 Hz (initial P only). The +5% amplitude stresses peak at0.0966363467146 and0.0987940223119 Hz; the.5 s transition stresses peak at0.0903745332340 and0.0926392684957 Hz. These are finite combination results; the latter two use.01 s staircase ramps and noisy threshold measurements, outside the exact-square-wave certificate.

The two original fine-step repeats give0.0915721467615 Hz for sampled P and0.0914145919980 Hz for initial P only at low-start r=2.347 s. Their coarse/fine peak differences are29.843 and2.135 microHz. These repetitions do not change the pass/fail outcome.

After the near-band +5% high-start result was observed, one +10% high-start amplitude challenge and its fine-step repeat were separately frozen in AMPLITUDE_STRESS_ADDENDUM_FREEZE.json. This is an outcome-informed follow-on, not an original holdout or independent validation sample. No controller coefficient was changed. The unchanged policy fails: coarse peak0.105025505264 Hz and fine peak0.105061904679 Hz. The5.062 mHz fine-step exceedance is much larger than the36.399 microHz coarse/fine change. Thus successful nominal/ramp/+5% confirmation does not imply arbitrary amplitude robustness.

The maximum candidate-specific full-trace linear/nonlinear discrepancy over the eight nominal points is0.006860832577 Hz for sampled P and0.006918155124 Hz for initial P only. These discrepancies are not uniform model-error bounds. They further explain why the LTI phase certificate is not promoted to nonlinear continuum safety. All266 locked round2 source/cache/model files remain byte-identical after the24 runs.


Final parser hardening: first-edge indexing uses fractions.Fraction and integer ceil(10*numerator/denominator), with no fixed-precision Decimal context. The audit includes15 parser tests using100-digit finite phase strings, including a rejected value infinitesimally above5 s, and56 additional phase-free online-policy tests. The total is1,444 boundary-policy tests. All frozen midpoint mappings and outcomes remain unchanged. The raw maximum command is50.00000000000077 MW; the explicit numerical feasibility tolerance is1e-9 MW. This ordinary floating-point residual is disclosed rather than claimed to satisfy a strict machine-arithmetic <=50 comparison.


Reproduction guard repair: independent replay review found that the original freeze utility checked for an existing manifest only after constructing its CSV inputs. The current wrapper now refuses at the first main entry, before any directory creation or input generation. The78-file regression verifies that rerunning against the existing freeze changes no hashes, modification times, sizes or input inventory. The original source bytes matching the frozen source hash are preserved separately under provenance/freeze_confirmation_at_v1_freeze.py; that archival snapshot is not for execution. The frozen manifest, policies, schedules, observations and nonlinear outcomes are untouched. See REPRODUCIBILITY_GUARD_HARDENING.json and FREEZE_REFUSAL_REGRESSION.json.


### Serialized-input numerical precision

The formula-defined SOC recovery is exact, and the original stored physical metrics refer to the in-memory model arrays. The actual nonlinear replay CSVs use12 significant digits. Independent re-integration of those unchanged CSVs gives worst absolute terminal SOC depletion1.4824097505084e-10 MWs and maximum command50.000000000050036 MW. The declared numerical audit tolerances are1e-8 MWs for terminal recovery and1e-9 MW for command feasibility; all24 case records satisfy them. These tiny serialization/arithmetic residuals are disclosed, not described as exact zero recovery or strict binary-floating-point <=50 MW. Original stored array metrics remain unchanged. SERIALIZED_INPUT_NUMERICAL_AUDIT.json records each case, both cumulative and pairwise summation results, and input hashes.
