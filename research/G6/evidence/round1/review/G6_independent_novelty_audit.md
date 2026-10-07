# G6 independent literature and mathematical novelty audit

Audit date: 2026-10-02. Scope: G6 only, multi-data-center dynamic joint hosting-capacity envelopes. No experiments were run; no main code was changed. This is an independent audit of the proposed phase-free, within-site harmonic-locking formulation, not a claim that a real joint grid–facility–job trace library exists.

## Decision

**Do not promote the current G6 formulation as a new hosting-capacity theory.** The mathematically defensible version is a useful certified screening/benchmark construction, but its exact same-information baseline is algebraically identical. Harmonic-l1 improvement, independent-versus-joint geometry, or phase/location observations do not establish novelty.

There is particularly close recent prior art: Krajacic et al., arXiv:2609.27698v1, published 23 September 2026. Equations (2)–(4) give square-wave harmonics and their locked phases; (8) gives the summed filtered waveform; (10)–(12) analyze two data centers and transfer-phase interaction. Its longitudinal example tests synchronized/unsynchronized starts and spatial deployment. The paper also studies nonlinear periodic-response failure with Floquet and algebraic-Jacobian tools. It does **not**, on the inspected material, claim a uniformly certified robust multi-site envelope over continuous frequency/duty/grid uncertainty. That is a possible scope distinction, not yet a novelty result. [Primary full text](https://arxiv.org/html/2609.27698v1)

Confidence: high for the mathematical collision and the cited source contents; medium for a negative literature claim, because a targeted search cannot establish exhaustive absence.

## 1. A useful, falsifiable proposition with an honest novelty label

### Proposition: exact independent-phase robust envelope and same-information equivalence

For each grid output j, suppose its steady periodic deviation at a fixed grid model g is

    y_j = sum_i a_i q_ji(theta_i, u_i; g),    a_i >= 0.

Here q_ji is the **actual PCC-input-to-grid-output** periodic response, including the facility transfer if the input originates behind the PCC. Each site's admissible pair (theta_i,u_i) belongs to a compact set U_i(g); start phases are independently arbitrary, while harmonics inside a site's waveform are locked by that waveform. Cross-site independence means the uncertainty set is a Cartesian product conditional on the **same** g. The q functions are continuous, or suprema replace maxima where appropriate.

Define s_ji^sigma(g) = sup_{(theta_i,u_i) in U_i(g)} sigma q_ji(theta_i,u_i;g), for sigma in {+1,-1}. Then

    R_j^sigma(a) = sup_g sum_i a_i s_ji^sigma(g)

is the exact worst-case signed output. Consequently the robust envelope for limits L_j^sigma is exactly

    A = {a >= 0 : R_j^sigma(a) <= L_j^sigma for every j and sigma}.

For fixed g this is an intersection of halfspaces in a. With shared uncertain g, it is an intersection of potentially infinitely many halfspaces and remains convex. It is not generally a finite polytope unless the grid uncertainty admits a finite exact representation. These statements require q not to change with a; if increasing capacity moves the operating point or changes dynamics, that dependence must be retained.

Proof: for fixed g, the objective is separable in a product uncertainty set. An upper bound follows by replacing each summand with its supremum; choosing independent site maximizers attains it, or approaches it arbitrarily closely. Taking the common outer supremum over g completes the result. Each resulting inequality is affine in a.

The same-information exact waveform peak/support optimizer computes precisely R, so its envelope equals G6's envelope. The difference is identically zero, apart from certified numerical tolerance. This is a **classical separability/support-function result**, useful as an audit proposition rather than a claimed new theorem.

Falsification protocol: give the comparator exactly the same PCC waveforms, load law, common g uncertainty, frequency/duty admissibility, transient convention, output limits, and verified numerical tolerance. A strict G6 capacity gain over that comparator falsifies the claimed equivalence of information/physics or exposes a numerical/model error. Differences from harmonic-l1 do not falsify the proposition: l1 expands the admissible harmonic phases and therefore solves a more conservative problem.

Important quantifier detail: universally bounded output rows may have different worst-case phases and different worst-case g. Their rowwise intersection remains exact for a requirement that **every** row obey its limit under **every** admissible realization. A single simultaneous worst-case witness for all rows is unnecessary.

### Shared uncertainty is not independent uncertainty

Do not replace sup_g sum_i a_i s_i(g) by sum_i a_i sup_g s_i(g) and call the latter an exact baseline. For g in [-1,1], q_1=(1+g)cos(theta_1)/2 and q_2=(1-g)cos(theta_2)/2 with a_1=a_2=1 have exact joint support 1, while independently worst-casing g per site gives 2. Preserving shared uncertainty is useful but already standard robust optimization. Any gain here is a correlation-of-uncertainty gain available to the same-information comparator, not AI-specific grid physics.

## 2. Strong baselines that must be included

1. **Exact waveform support, fixed model.** Globally maximize each full one-site filtered periodic waveform over its single start phase, preserving all harmonic relations. Sum those supports. This is the decisive same-information baseline and is identical to the proposition above. A dense time/phase sample is a lower bound on the maximum, not a safety certificate.

2. **Validated trigonometric-polynomial optimization.** For finite harmonic order H, certify t-q(theta)>=0 on the unit circle with a Gram-matrix/SOHS representation, or use certified real/complex root isolation after polynomialization. Univariate trigonometric positivity and exact hybrid numeric-symbolic certificates are established methods, including Magron et al.'s algorithms and complexity analysis. A floating SDP result by itself is not a rigorous certificate. [Magron et al.](https://arxiv.org/abs/2202.06544)

3. **Continuous-uncertainty robust support.** Keep the common grid variable shared; solve the outer uncertainty supremum with valid enclosure, SOS where applicable, or interval branch-and-bound with a documented upper/lower gap. One must not describe a finite frequency/duty/model sweep as uniform robustness. Generalized KYP already treats eligible finite-frequency inequalities without gridding; it is a strong comparator when the claimed condition actually has its form, but it does not automatically encode exact waveform peak constraints. [Iwasaki–Hara primary report](https://www.keisu.t.u-tokyo.ac.jp/data/2003/METR03-27.pdf)

4. **Robust multiport feedback stability/performance.** Where facility/grid dynamics are uncertain feedback interconnections, use the same LFT blocks and compare with structured singular-value bounds or appropriate IQCs. These are not interchangeable with an exact deterministic peak-support problem. A lower bound on mu or successful sampled test cannot establish robust safety; an upper-bound certificate must match the stability/performance question. [Doyle](https://authors.library.caltech.edu/records/9de69-h7s46), [Megretski–Rantzer](https://services.montefiore.uliege.be/systems/grad04/megretski97.pdf)

5. **Nonlinear revalidation and dynamic hosting baseline.** The same operating point, fault list, converter limits, load response, and source waveform must be passed through the same nonlinear plant/checker. A fixed linear transfer result must not be compared with a baseline forced to absorb unmodeled operating-point or converter effects. [Ren et al.](https://arxiv.org/html/2609.03030v1), [Krajacic et al.](https://arxiv.org/html/2609.27698v1)

6. **Observed-coherence comparator only for a statistical claim.** A common cross-spectral-density or covariance uncertainty set must be shared with the comparator. H S H* output spectral propagation addresses second-order behavior; estimated low coherence is not a hard future-phase constraint and does not certify trajectory peaks. [Chaudhary et al.](https://arxiv.org/html/2606.13847v1)

Independent boxes, harmonic-l1, constant-MW planning, randomized phase Monte Carlo, and isolated-site studies are useful ablations or practice baselines. They are insufficient as the sole novelty comparator.

## 3. Certification conditions and port/phase break tests

### Tail requirements

For q(theta)=sum_{h>=1} Re(c_h exp(ih theta)), a valid absolute tail bound is E_H >= sum_{h>H}|c_h|. Then the true maximum lies within E_H of the truncated maximum. If certified uniformly |c_h|<=C/h^(r+1), with r>0, then E_H<=C/(r H^r). Square-wave input coefficients decay as 1/h; absolute convergence of the **output** tail requires sufficient transfer decay or another direct argument. An ideal direct feedthrough square wave does not justify a summable 1/h triangle tail. Exact piecewise waveform analysis can handle cases where this Fourier-tail shortcut fails.

Frequency must be bounded away from zero for many simple uniform high-frequency gain bounds. Resonant transfer peaks, gain coefficients, and derivative bounds must themselves be enclosed over the entire admissible grid set. Coefficient estimates from telemetry introduce measurement/model uncertainty; they are not exact rational coefficients merely because a certificate routine accepts floating values.

### Required counterexamples/limits

- **AI-label invariance:** identical actual PCC P/Q trajectories, initial conditions, network model, and constitutive load/control laws imply identical grid trajectories under uniqueness. Job labels cannot alter the result. Equal P alone or equal nominal power factor is insufficient.
- **Port break:** the same rack trace through two different UPS/PFC/control/current-limit arrangements need not produce the same PCC P/Q. A server or rack spectral promise is not a PCC promise without a validated transfer/error relation.
- **Switching/drift break:** bounds for fixed-period steady-state orbits do not cover frequency drift, mode switches, changing duty, or startup transients simply because every frozen parameter lies in the admissible interval. Convolution carries memory; certify the trajectory class or add an independently valid residual/transient term.
- **Phase observation break:** current inter-site cancellation is not a future guarantee. Arbitrary independent starts require independent phase suprema; accepting cancellation requires a bounded-duration verified prediction or enforceable control contract and fault behavior.
- **Peak versus stability break:** a nominally stable LTI response certificate does not prove nonlinear periodic-orbit stability, fault ride-through, converter non-saturation, or protection coordination.
- **Capacity rescaling break:** if a changes the network operating point, q(g) must become q(g,a). The halfspace conclusion can then disappear; recomputing only a subset of transfer models does not establish uniform validity.
- **Duty/mean break:** changing square-wave duty changes the DC component unless the waveform is explicitly recentered. Preserve mean demand, power flow, reserve use, and the resulting operating point; do not present a changed-mean comparison as a pure harmonic benefit.
- **Output-functional break:** scalar row supports do not automatically certify nonlinear apparent-power magnitudes, RMS/energy windows, or protection timers. Those functionals need their own exact or conservative support/reachability treatment.

These are testable limits of a useful screening certificate, not reasons to invent a broader G6 claim.

## 4. Primary-source audit and precise novelty exclusions

### RATLLE / PNNL-39459

The PDF cover says **June 2026**; the PNNL publication page says **22 September 2026**. Keep both dates distinct. The report presents location/frequency screening, positive-sequence oscillation simulation, and consequence metrics on public WECC240 and a detailed 2031 winter case. Its stated phasor-domain scope is approximately below 10 Hz; source load profiles include monoperiodic/biperiodic square waves. The public repository now reports a 29 September update adding load-sharing metrics and a screening dashboard. None of these sources alone supplies a calibrated joint job/port/network validation dataset. [Report](https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-39459.pdf), [publication page](https://www.pnnl.gov/publications/methodology-evaluate-grid-reliability-impact-oscillations-induced-large-loads), [repository](https://github.com/pnnl/LL-risk-assessment), [DOI](https://doi.org/10.2172/3422382)

### VRT hosting / arXiv:2609.03030

Ren, Sun, and Teng already jointly optimize hosting across candidate buses with facility VRT constraints. The workflow derives tightened affine surrogate margins from sampled cases and accepts optimized allocations only after network plus internal-model nonlinear re-simulation across tested faults/periods. It uses reduced-order GFL/GFM response models. Thus joint dynamic hosting, internal converter headroom, and spatial allocation are already occupied. It does not supply an all-continuous-uncertainty forced-oscillation certificate; finite tested-case validation should not be relabeled as one. [Primary full text](https://arxiv.org/html/2609.03030v1)

### Dynamic data-center model / arXiv:2505.16575

Jimenez-Ruiz and Milano model UPS behavior, cooling induction motor, pulsing workload, reconnection/flapping, and load ramp response on an Irish-system case. They already discuss staggered reconnection and de-synchronization of periodic tasks. This undercuts claims that pulse loads, fault-sensitive port behavior, or staggering alone make G6 new. The case is not a real synchronized multi-site spectral-contract dataset. [Primary full text](https://arxiv.org/html/2505.16575v1)

### DML / DOI 10.21227/ev1a-g183

Direct retrieval of the current DataPort landing and its **V32 Manual – Current** link verified V032 as the current model package and a **14 August 2026** availability announcement. The downloaded manual is **PNNL-38817 Beta**, dated **August 2026**, and says beta work completed in July. A separate official PNNL beta-report webpage is published **22 September 2026**. Thus September 22 is a valid report webpage date, not the V032 package availability date. The landing retains an older alpha/unvalidated paragraph, which must not be used to deny the current beta manual. The manual describes generic models needing expertise and site data; its mixed-architecture example is fictitious. Section 5 describes job-stage power signatures, so stage annotations are not new by themselves. [DataPort](https://ieee-dataport.org/open-access/data-center-model-library-electromagnetic-transient-analysis-pscad), [DOI](https://doi.org/10.21227/ev1a-g183), [PNNL beta-report webpage](https://www.pnnl.gov/publications/electromagnetic-transient-modeling-large-data-centers-grid-level-studies-beta-release)

### Workload stage and aggregation sources

Choukse et al. use production training telemetry, describe synchronous compute/communication stages, and discuss frequency specifications plus software/GPU/storage mitigation. Ko and Zhu model stochastic periodic training/fine-tuning profiles and evaluate multi-site deployment, frequency spread, capacity, and grid effects on WECC179. Chaudhary et al. analyze evolving inter-bus correlation using synthetic three-site RTDS traces. These support the relevance of job structure and nonstationarity; none grants a persistent PCC waveform or future inter-site phase promise. [Choukse et al.](https://arxiv.org/html/2508.14318v2), [Ko–Zhu](https://arxiv.org/html/2508.16457v1), [Chaudhary et al.](https://arxiv.org/html/2606.13847v1)

### Robust envelopes and control sources

Liu–Braslavsky already derive robust DOE allocations and exploit customer operating status and controllable Q. Related work addresses superellipsoid formulations and nonconvex OPF. De Carvalho et al. address robustness throughout the allocated three-phase envelope, rather than checking only extremes. Here “dynamic” generally denotes time-updated operating allowances, so these are methodological rather than identical electromechanical baselines. [Liu–Braslavsky](https://arxiv.org/html/2212.03976v3), [superellipsoids](https://arxiv.org/abs/2308.14293), [nonconvex OPF](https://arxiv.org/abs/2404.03355), [de Carvalho et al.](https://arxiv.org/html/2607.08578v1)

Structured robust power-system assessment is also longstanding. Castellanos et al. (2005) assess large-system uncertainties using mu; Sumsurooah et al. (2016) retain dependence of operating points on uncertain parameters. Merely adding multiport uncertain blocks or state-dependent grid sensitivity is not new. [Castellanos et al.](https://doi.org/10.1016/j.ijepes.2005.02.001), [Sumsurooah et al.](https://eprints.whiterose.ac.uk/id/eprint/107001/)

## 5. What would actually change this verdict?

Evidence must establish a new result beyond computing the classical support under relabeled inputs. Plausible qualifying evidence would be a substantially stronger, sound and tractable certificate for a well-defined nonseparable nonlinear/time-varying trajectory class; a provably better algorithm with error/complexity guarantees relative to the strongest compatible certified methods; or a validated, enforceable port-level contract and demonstrated useful robustness/hosting trade-off that existing contractual methods cannot achieve with the same information.

No such result is established here. A new empirical benchmark could still be valuable, but it requires calibrated joint data and a truthful contribution label. With the present evidence, the most defensible completion is a bounded audit/reproduction: show exact-baseline equality, quantify l1 conservatism separately, certify the toy model's numerical gaps and tails, and publish the drift/port/label counterexamples as scope checks. This recommendation does not open another route.

## 6. Local evidence files

- PNNL-39459.pdf and PNNL-39459.txt: public primary report, cover date June 2026
- DML_V032_manual.pdf and DML_V032_manual.txt: current public DataPort documentation, Beta August 2026
- dml_primary_landing_excerpt.txt: current landing text retrieved 2026-10-02, including V032 and August availability

Only documentation was retrieved. The DML model package, a jointly calibrated library, and commercial simulation execution were not obtained or performed.
