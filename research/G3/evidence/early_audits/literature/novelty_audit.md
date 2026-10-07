# Recovery status: recovered_text

Recovered on 2026-10-02 from this worker's retained 2026-10-01 file-writing tool call. The original literature cutoff remains 2026-10-01. No searches, downloads, simulations, or source revalidation were rerun for this recovery. Historical references below to downloaded files describe the original audit only; original HTML, PDFs, supplements and other binaries have not been recovered. New file hashes certify this recovered text, not byte identity with lost files. paper_ready=false remains in force.

# G3 novelty audit: constrained P/Q service arbitration

Audit date: 2026-10-01 UTC. Literature research and primary-source inspection only. No simulation, controller reproduction, benchmark, or empirical novelty demonstration was performed.

## Bottom line

**The original G3 framing is not safely novel.** There are already strong collisions for concurrent P/Q regulation using AC/DC- and SoC-dependent capability, current-limited converter safety and recovery, service-constrained energy-headroom boundaries, and even simultaneous sustained AI-load forcing plus a voltage sag under QP coordination. “Utility-side,” a different bus system, a different forcing frequency, adding a sinusoid, or replacing a hydrogen hub by a BESS do not by themselves establish a new scientific mechanism.

A narrow lead remains, conditional on a real theorem or counterexample: **phase-conditioned, signed oscillatory-service loss and return-to-service feasibility under a voltage-dependent current bottleneck and finite AC/DC energy, while the exogenous disturbance continues.** This is a research hypothesis, not a verified literature gap. The strongest potential contribution is a physical impossibility/necessary-resource result and a demonstrated separation between instantaneous feasibility and sustainable service, not another weighted optimizer.

## Source-level collision map

### C1. Jaramillo, Carrión, Aguila Téllez (2026): closest boundary-method collision

[Primary article](https://www.mdpi.com/1996-1073/19/18/4464); DOI [10.3390/en19184464](https://doi.org/10.3390/en19184464). Energies 19(18), 4464. Published **21 September 2026**; accepted 16 September. Publisher metadata and full HTML verified. Main evidence anchors: §§3.4, 4.1–4.3, Table 2, §§7.8–7.9, 10.

The paper combines a 17-state averaged GFM-BESS with source/DC/current/modulation/thermal/SoC constraints and explicit delivered-service tests. Equations (30)–(32) impose a sag-dependent positive active-power floor and accumulate positive-part scheduled and floor deficits. Equation (34) searches a reserve threshold feasible at all larger tested reserves. Recovery targets constant dispatch and angle/frequency tolerances with final limiter inactivity. Repeated faults are already tested. It is not a study of bidirectional periodic service tracking or restoration to a continuing forced orbit. **Do not claim novelty for service-feasibility classification, reserve/service trade-offs, repeated events, nonmonotone boundaries, or recovery-aware governance.**

### C2. Shamseldein: closest simultaneous-forcing coordination collision

Mohamed Shamseldein, “Impedance-passivity coordination of hydrogen-coupled AI data centers for oscillation damping and fault ride-through at transmission interfaces.” [Publisher article](https://www.sciencedirect.com/science/article/abs/pii/S0378779626008503); DOI [10.1016/j.epsr.2026.113557](https://doi.org/10.1016/j.epsr.2026.113557). EPSR 262, 113557; issue date January 2027. Publisher text was indexed and accessible through search at the audit cutoff. Crossref created the DOI record 29 June 2026, but provides **no online-publication date**. Do not invent a September first-publication date.

Sections 4.1–4.4 use four QP variables: d/q current, damping power and electrolyzer setpoint; current constraints are polygonally approximated, with voltage-dependent weights. Section 5.3 combines ongoing 15 Hz forcing and workload burst with a 0.6 pu, 100 ms sag, then returns to a forced residual. Section 5.6 finds weak damping/recovery sensitivity to weights under saturation. This uses a co-located hydrogen-process actuator, not workload scheduling, and does not establish a utility-BESS signed service-loss certificate. Numerical results are reduced-model plus complementary average-value network checks; code availability is promised/on request, with no repository verified.

### C3. Zecchino et al.: variable capability is old, experimentally demonstrated

Antonio Zecchino, Zhao Yuan, Fabrizio Sossan, Rachid Cherkaoui, Mario Paolone, “Optimal Provision of Concurrent Primary Frequency and Local Voltage Control from a BESS Considering Variable Capability Curves: Modelling and Experimental Assessment.” [arXiv 1910.04052v2](https://arxiv.org/html/1910.04052v2); original submission 9 October 2019, v2 8 April 2020; EPSR 190 (2021), 106643.

Equation (3) uses a feasible P/Q set dependent on AC voltage, DC voltage and SoC; DC voltage prediction uses a three-time-constant battery model. The paper explicitly rejects a universal fixed MVA circle. Section III fits commercial converter capability curves; experiments use a 720 kVA/560 kWh utility-scale BESS. Therefore AC/DC-dependent P/Q projection, battery-state-aware capability, and simultaneously providing frequency/voltage regulation cannot support G3 novelty. The inspected paper addresses real-time operating-point regulation rather than a persistent-forcing fault/recovery service boundary.

### S10. Gerini et al.: multi-service GFM plus feasible reference conversion

Francesco Gerini et al., “Optimal Grid-Forming Control of Battery Energy Storage Systems Providing Multiple Services: Modelling and Experimental Validation.” [arXiv 2110.10052v1](https://arxiv.org/html/2110.10052v1); [journal DOI](https://doi.org/10.1016/j.epsr.2022.108567). Preprint 19 October 2021; EPSR 212 (2022), 108567.

Three stages combine robust scheduling, dispatch MPC and real-time converter-feasible reference conversion. Equations (16)–(25) explicitly use AC/DC/SoC-dependent capability and weighted P/Q setpoint error. The final feasibility adjustment is performed each second; underlying GFM response is faster. Physical feeder experiments support simultaneous dispatch, frequency containment and voltage services. This is a strong baseline lineage, but does not certify subcycle current-limiter dynamics or continuing oscillatory service after a sag.

### S8. Norouzi and Morel: physical P/Q impossibility already exists

Amir Norouzi and Michael Morel, “Voltage Ride-Through in Large Loads—A Dual PQ Approach.” [arXiv 2605.00769v1](https://arxiv.org/html/2605.00769v1), 1 May 2026.

Sections II–III use load-side power circles to expose practical current and theoretical voltage-support limits. Equations (4)–(5) identify source-voltage boundaries for constant load voltage under substation apparent-power limits. Active support can extend the region beyond reactive-only support, but sufficiently deep dips remain impossible. The current-to-MVA conversion assumes the controlled load voltage stays fixed, so this is not the same as assuming constant inverter capability at a dipping PCC. It supplies an essential algebraic impossibility baseline, not a dynamic BESS service/recovery law.

### S9. Mao, Mathieu and Dvorkin: exogenous AI load and P/Q/SoC optimization already combined

Yanyong Mao, Johanna L. Mathieu, Vladimir Dvorkin, “Online Feedback Optimization of Energy Storage to Smooth Data Center Grid Impacts.” [arXiv 2603.20564v1](https://arxiv.org/html/2603.20564v1), 20 March 2026.

The plant is the distribution grid and distributed batteries; AI load is exogenous. Equation (1) includes voltage constraints, a fixed apparent-power circle, SoC evolution/bounds and terminal energy equality. Online feedback uses measured voltage and SoC rather than perfect load forecasts; anti-windup and realistic battery losses are included. Validation uses OpenDSS three-phase feeder simulations. G3 cannot claim the utility/exogenous boundary or feedback P/Q/SoC optimization as a distinguishing invention. Genuine additional work would concern dynamic current limitation and a formally specified oscillatory service under fault/recovery, rather than voltage smoothing alone.

### S1. Kundu et al.: grid-side digital-load mitigation and joint safety already combined

“Managing Risks from Large Digital Loads Using Coordinated Grid-Forming Storage Network.” [arXiv 2508.11080v1](https://arxiv.org/html/2508.11080v1), 14 August 2025.

IEEE68 studies use WECC REGFM_A1 storage and simplified ZIP digital loads. Fixed aggregate storage power supports comparisons of collocated and distributed storage. Adopted safety-consensus control combines local voltage/frequency safety with system-level regulation and sharing. Case 1 concerns fault-induced instability; Case 2 concerns load-induced wide-area oscillations. The inspected paper does not give G3's proposed signed service-loss/recovery boundary. Still, grid-side coordinated storage against data-center oscillations plus voltage/frequency risk is not an open generic topic.

### S16. Ross and Follum, PNNL: usable environmental-model reference, not field truth

“Electromagnetic Transient Modeling of Large Data Centers for Grid-Level Studies,” PNNL-38817. [Official report PDF](https://www.energy.gov/sites/default/files/2026-01/Data_Center_EMT_Models.pdf), January 2026.

The DML is generic PSCAD code and requires site expertise/data for site-specific representation. Report §§6.8–6.10 describe current-priority behavior, limiter functions, and average-value/switching converter counterparts; §6.13 describes load playback whose exogenous process continues through a fault while electrical demand obeys current limits and reconnection ramps. Thus ongoing load playback across a sag is already an available modeling feature. It is appropriate as a fixed/uncertain external load model, not as a controllable facility UPS in G3 and not as evidence of a particular site's behavior.

### C4. Schneeberger, Dörfler and Mastellone: safety-filter plus nominal recovery already exists

“Advanced Safety Filter for Smooth Transient Operation of a Battery Energy Storage System.” [arXiv 2405.14427](https://arxiv.org/abs/2405.14427), 23 May 2024; CDC 2024 paper.

The filter combines CBF/CLF construction through sum-of-squares with a QCQP, current safety, input constraints and finite-time return to a nominal-control region. Simulations compare a load-step response against vector current control. Therefore a current-limiting QP/CBF supervisor with recovery to nominal control is directly occupied. A G3 implementation must compare against or explain departures from this class; renaming it “service arbitration” is not enough.

### C5. Arjomandi-Nezhad et al.: limiter release conditions and outcome classes

Ali Arjomandi-Nezhad, Yifei Guo, Bikash C. Pal and Guangya Yang, “Modeling Fault Recovery and Transient Stability of Grid-Forming Converters Equipped With Current Reference Limitation.” [arXiv 2403.05236](https://arxiv.org/abs/2403.05236); [DTU primary record](https://orbit.dtu.dk/en/publications/modeling-fault-recovery-and-transient-stability-of-grid-forming-c/); DOI 10.1109/TEC.2024.3507544. IEEE TEC 40(2), 1140–1152 (2025).

It provides a closed-form necessary condition for escape from saturation and distinguishes normal equilibrium, saturated equilibrium and divergence according to current angle and trajectory. Recovery cannot be judged from an instantaneous P/Q point alone. G3 must treat this as prior mechanism knowledge, not rediscover that saturation can prevent post-fault recovery.

### C6. Large-signal and repeated-saturation literature

Baeckeland, Yang and Seo, “Unified Model of Current-Limiting Grid-Forming Inverters for Large-Signal Analysis,” [IEEE primary record](https://ieeexplore.ieee.org/document/11077947/), DOI 10.1109/TPWRS.2025.3587224; online 10 July 2025, TPWRS 41(1), 198–213 (2026). A unified limiter-angle representation connects common current-limiters and analyzes large-signal behavior, with numerical, EMT and hardware evidence.

“Dynamic Evolution and Stability Analysis of GFM-Based Renewable Energy Resources Considering Repeated & Continuous Current Saturation,” [IEEE primary record](https://ieeexplore.ieee.org/document/11079878/), DOI 10.1109/TSTE.2025.3588818; online 14 July 2025, TSTE 17(1), 242–258 (2026). Hybrid switching conditions distinguish repeated/continuous saturation; a desaturation-region design addresses persistent overvoltage and failed recovery. Abstract/metadata inspected; authors/full derivation not independently audited here. Repeated-saturation physics itself is not new.

### C7. Periodic invariant battery operation is established

Kotaro Hashikura, Kazuki Namba and Akira Kojima, “Periodic constraint-tightening MPC for switched PV battery operation,” [primary article](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/iet-cta.2017.1174), DOI 10.1049/iet-cta.2017.1174, 1 October 2018, IET CTA 12(15), 2010–2021.

Periodic invariant target sets and constraint tightening ensure recursive feasibility while switching battery charge schedules under prediction errors. This is slow PV/battery operation, not fault-current arbitration, but it directly defeats a generic claim that periodic recovery/invariant battery tubes are new. A timescale change alone is not a contribution.

## Proposed distinction: precise acceptance bar

These are original audit recommendations, not findings attributed to a source.

1. **Define the service in the network.** A controller can track the wrong local active-power waveform perfectly and still worsen a remote electromechanical mode. Decide whether the contract is signed P tracking, a bound on a modal-band network output, or both. If the derivation only certifies tracking, do not call it a network-damping guarantee.
2. **Separate physical state and service state.** Use battery energy and DC-link energy as distinct states; retain converter/filter/limiter memory where needed. A constant SoC endpoint is insufficient to establish resumption of sustainable periodic operation.
3. **Measure both signs.** For a signed request r(t), the scalar integral of [r(t)-p(t)]+ ignores failed absorption when r<0 and p=0. A service norm, separate upward/downward shortfall budgets, or phase-resolved Fourier error is required. This observation is elementary; only a substantive derived consequence could become novel.
4. **Demonstrate phase/history matters beyond peak clipping.** Hold forcing amplitude/frequency, sag depth/duration, hardware and initial mean SoC fixed. Vary sag inception phase after reaching the same nominal periodic orbit. Seek a case where an instantaneous current-headroom classifier predicts feasibility for every phase, but a dynamic service/recovery certificate separates phases because finite source ramp, losses, DC energy or recovery current is binding.
5. **Produce a tight obstruction, not just a computed failure map.** An impossibility certificate should say why no admissible policy with the stipulated information and actuator can meet both services and recovery. A sufficient design alone or finite-policy comparison cannot establish physical impossibility.
6. **Bound the claim exactly.** A convex reduced-model certificate is conditional on its approximation. Validate certificate boundary points in an independently implemented averaged converter, then selected switching cases for limiter claims. Any mismatch becomes an uncertainty margin or a limited claim.
7. **Do not choose a losing baseline.** Include an AC/DC-capability-aware allocator, a tuned Q-priority law with anti-windup and explicit recovery, and a constrained predictive reference governor. Give every causal policy the same measurements and preview. A noncausal oracle can bound performance but is not a fair deployable competitor.

### A useful reject-or-continue gate

Continue only if at least one analytically explained mechanism survives those comparators and full state restoration under continuing forcing. It should change a practical conclusion, such as the admissible service fraction, necessary reserve, recharge time, or an impossible phase sector at fixed installed hardware. Mere improvement from adding lookahead to a one-step clipper is insufficient.

Stop or reposition as a reproducible benchmark if:
- the boundary is just P²+Q² ≤ V²Imax² plus ordinary energy integration;
- an off-the-shelf predictive capability projection produces the same frontier;
- the claimed superiority is purchased by less active service, additional preview, relaxed current duration or a looser recovery criterion;
- all claimed differences vanish once saturation, signed service error and continued post-fault forcing are accounted for;
- the “new” feature is merely utility ownership, AI nomenclature, GFL/GFM substitution, or a changed test-network size.

## Research limits

This is a targeted primary-literature pass, not proof that no prior work exists. Bibliographic verification is strongest for C1 and the arXiv papers. C2's issue date and DOI are verified, but its first online date and public code availability remain unresolved. Literature claims are separated from proposed mechanisms. No publication likelihood or experimental gain is inferred.
