# G3 import-port viability: primary-literature novelty-threat audit

Audit date and cutoff: 2026-10-03 UTC. This is a fresh targeted literature audit, not a literature-exhaustiveness proof. Historical recovered files were read only. No experiments, controller implementations, or hardware claims were validated here.

## Result

**The narrow candidate is not ruled out, but all of its generic components have strong prior-art collisions.** An exact dynamic convex characterization with a realizable policy and a quantified, same-parameter outer/inner recovery gap could remain a contribution. Simply combining convex P/Q allocation, finite buffering, ramp constraints, workload energy, and SoC recovery is not a defensible novelty claim.

The strongest comparisons are Streitmatter et al. (current-limited converter convexity), Evans et al. (exact discharge feasibility and constructive recovery), EasyRider (compute-load LC/buffer smoothing with energy-sizing and SoC readiness), Liu et al. (compute-task/storage/interconnection co-optimization), and Murgovski et al. (energy-coordinate convexification). These sources must appear in the theorem positioning, not only the introduction.

The later fixed-P/Q-path admission route is separately audited in `FIXED_PATH_CERTIFICATE_ADDENDUM.md`. It removes the free-loss-slack concern; its interpolation and exact-cell reachability claims face additional structural antecedents.

## A. Closest primary threats

### T01. Streitmatter, Joswig-Jones, Zhang: convex current-limited converter region

**Source:** “Convexity and Optimal Online Control of Grid-Interfacing Converters with Current Limits,” arXiv:2603.17135v1, **17 March 2026**. [Primary full text](https://arxiv.org/html/2603.17135v1).

**Exact anchor:** Theorem 1 proves convexity of the achievable two-dimensional output region for each pair chosen from P, Q, V² under a current-ball constraint and general equivalent filter impedance. Section IV-A gives an equivalent SDP output representation; Section IV-B recovers physical current. Theorem 2 gives convergence of the regularized projected-gradient controller.

**Threat:** Exact convex P/Q feasibility and current-limited service tradeoffs are occupied. Section II-A explicitly includes rectifiers, so reversing the power sign does not establish novelty.

**Boundary:** Equation (1) neglects high-frequency filter/line dynamics, using an algebraic equivalent impedance and timescale separation. There is no DC-link energy, buffer inventory, lag/ramp actuator state, or compute-task completion contract. Its exactness is an output-region result, not the requested dynamic trajectory/recovery result. Cite it precisely rather than claiming all converter dynamics have already been convexified.

### T02. Evans, Tindemans, Angeli: exact discharge and guaranteed recovery

**Source:** “Flexibility Framework with Recovery Guarantees for Aggregated Energy Storage Devices,” arXiv:2110.08549v1, **16 October 2021**; IEEE TSG 13(5), 3519–3531, **2022**, DOI 10.1109/TSG.2022.3173900. [Primary full text](https://arxiv.org/html/2110.08549v1), [institutional journal record](https://atiro.turing.ac.uk/esploro/outputs/journalArticle/Flexibility-Framework-With-Recovery-Guarantees-for/9919628909548).

**Exact anchor:** Property II.5 gives necessary-and-sufficient discharge feasibility through domination of the E–p transform. Theorem III.1 preserves the feasible discharge set under energy-conditioned fleet truncation and guarantees a known terminal state. Equations (13)–(14) derive recharge energy and fastest recovery time; Section III-D constructs a sufficient recovery virtual battery. Theorem IV.1 aggregates discharge capability.

**Threat:** A service-feasibility set, associated dispatch, loss-aware inventory restoration, and recovery time are already a rigorous package.

**Boundary:** Pure discharge followed by recharge, constant device power limits, no cross-charging, and no rate/lag, reactive-current competition, DC modulation, or computing process. A temporal-order-sensitive dynamic import bottleneck can differ, but adding the word “recovery” cannot.

### T03. Jensen et al.: EasyRider directly combines compute, LC, and buffer sizing

**Source:** “EasyRider: Mitigating Power Transients in Datacenter-Scale Training Workloads,” v1 **16 April 2026**, inspected v2 **11 September 2026**. [Primary v2](https://arxiv.org/html/2604.15522v2), [version metadata](https://arxiv.org/abs/2604.15522).

**Exact anchor:** Sections 5.1–5.4 combine a passive LC filter, rack voltage regulation, and an active energy buffer. Appendix B, equations (10)–(17), derives an import-ramp limit, worst-case buffer energy proportional to power swing divided by smoothing rate, usable-capacity scaling, and buffer power rating. Appendix C includes time-to-ready SoC targeting and an authors-described receding-horizon QP. Section 7.4 demonstrates restoration while a training trace continues. A 10 kW/400 VDC prototype is reported.

**Threat:** Compute-load buffering, LC-plus-battery timescale separation, analytic ramp/energy sizing, and ready-again inventory control have a direct hardware antecedent.

**Boundary:** It is rack-side DC smoothing, not sag-dependent AC P/Q arbitration with a simultaneous task-service/recovery feasibility theorem. The claimed QP's piecewise-efficiency state equation is not independently rederived here; do not import its convexity assertion as a proof.

### T04. Liu, Shin, Deka: compute contracts plus constrained grid withdrawal and storage

**Source:** “Watts vs. Bytes: Turning Data Centers into Grid Assets via Storage–Compute Co-Optimization,” arXiv:2605.16190v1, **15 May 2026**. [Primary full text](https://arxiv.org/html/2605.16190v1).

**Exact anchor:** Section II-A models net grid withdrawal with interconnection/ramping and market-participation constraints. Section II-B, equations (8)–(9), couples release times, deadlines, total work, job rates, DVFS, and service-quality penalties. Section II-C models scenario-dependent battery/SoC operation. Section III provides continuous/discrete-DVFS reformulations.

**Threat:** “Compute task + battery + limited import + ramping + grid services” is already a joint optimization problem, including the distinction between internal compute capacity and net interconnection capacity.

**Boundary:** Hourly day-ahead scheduling and soft tardiness/noncompletion differ from fast hard current/DC viability. The inspected v1 has conflicting terminal-SoC descriptions: Section V-A mentions a 60% terminal requirement; V-B1 says no terminal constraint and corrects depletion economically. Therefore do not claim either universal inventory recovery or universal omission of recovery from this source.

### T05. Hashmi et al.: ramp/energy/deadline linear modeling

**Source:** “Linear energy storage and flexibility model with ramp rate, ramping, deadline and capacity constraints,” arXiv:2409.08084v1, **12 September 2024**. [Primary full text](https://arxiv.org/html/2409.08084v1).

**Exact anchor:** Equations (1)–(6) impose storage inventory, charging/discharging efficiency, converter efficiency, power, and inter-period rate constraints. Equations (7)–(8) impose an arrival/departure-window cumulative energy target with nonnegative flexible-load consumption. Section III gives LP formulations for arbitrage.

**Threat:** Linear power/ramp/inventory feasibility with a preserved load-energy contract is not new. Their word “ramp” sometimes means power and “ramp rate” means its time difference; translate units carefully.

**Boundary:** No converter current vector, AC sag, inductor/DC-link energy, modulation reconstruction, or full dynamic recovery certificate. A G3 result must not reduce merely to this LP with renamed variables.

### T06. Murgovski, Johannesson, Sjöberg: energy-state convexification

**Source:** “Convex modeling of energy buffers in power control applications,” IFAC Proceedings Volumes 45(30), 92–99, **October 2012**, DOI 10.3182/20121023-3-FR-4025.00009. [Author institutional PDF](https://publications.lib.chalmers.se/records/fulltext/164597/local_164597.pdf), [publisher record](https://www.sciencedirect.com/science/article/pii/S1474667015351442).

**Exact anchor:** Section 3.2, equations (10)–(12), replaces capacitor voltage by stored energy, relaxes nonlinear state equality to a concave energy hypograph, and argues tightness at an energy-cost optimum. Section 3.3 extends energy-buffer convex modeling; the setup includes charge-sustaining operation and quadratic losses.

**Threat:** Squared-voltage/energy coordinates, nonlinear buffer-loss convexification, and optimization with endpoint inventory preservation are established.

**Boundary:** Its objective-specific slack-removal argument does not prove equality of arbitrary service-feasibility projections. G3 must prove whether loss slack can be removed while preserving import tracking, DC upper/lower limits, actuator rates, and terminal recovery.

### T07. Despeghel, Tant, Driesen: quadratic converter-loss SOCP and slack caveat

**Source:** “Convex Optimization of PV-Battery System Sizing and Operation with Non-Linear Loss Models,” arXiv:2307.15507v1, **28 July 2023**; Applied Energy 353, 121976, **1 January 2024**, DOI 10.1016/j.apenergy.2023.121976. [Primary preprint](https://arxiv.org/html/2307.15507v1).

**Exact anchor:** Equations (12) and (20) replace quadratic-over-rating loss equalities with rotated SOC inequalities. Equation (27) is inventory dynamics; beginning/ending battery energy is equated. Section 4.6 explicitly reports artificial loss and simultaneous-charge/discharge slack in the cost-optimal first solve and adds a second loss-minimizing solve.

**Threat:** SOCP battery/converter loss lifting and cyclic inventory are occupied.

**Boundary:** Do not repeat the abstract's equivalence statement as a universal trajectory-feasibility theorem. Their implementation is 15-minute techno-economic operation, not fast RL/DC transients. The explicit slack discussion is directly relevant to the correctness bar for G3.

## B. Supporting collisions that eliminate broader framings

### T08. Ardakanian, Rosenberg, Keshav: import-capacity/storage tradeoffs

**Source:** “On the impact of storage in residential power distribution systems,” University of Waterloo report, **2 May 2012**. [Primary institutional record](https://uwspace.uwaterloo.ca/items/f3ce54be-4999-405c-897b-7b1f74fa90b6), [author PDF](https://cs.uwaterloo.ca/sites/default/files/uploads/documents/cs-2012-08.pdf).

Sections 2–4 use the electricity/queueing equivalence and burst/mean/peak demand envelopes to jointly size constrained transformer supply and finite storage against loss-of-load risk. Equation (5) bounds storage power by peak demand minus transformer supply. Assumptions include ideal efficiency, fixed power factor, and sufficiently fast storage. This defeats generic constrained-import/buffer sizing novelty; sag-varying P/Q and actuator-memory dynamics remain outside it.

### T09. Al Taha, Vincent, Bitar: certified inner flexibility approximation

**Source:** “An Efficient Method for Quantifying the Aggregate Flexibility of Plug-in Electric Vehicle Populations,” arXiv:2207.07067, initial submission **14 July 2022**; inspected v3 **18 January 2024**. [Primary preprint](https://arxiv.org/abs/2207.07067), [primary full manuscript](https://arxiv.org/pdf/2207.07067v3).

The inspected full manuscript constructs tractable polytope-containment-based inner approximations. Theorem 2 gives sufficient linear containment conditions, and Section IV constructs an affine disaggregation of every admitted profile into individually feasible profiles. Thus a certified inner set with constructive realization is established methodology. Older search-indexed versions discussed outer approximations and volume ratios, but those unversioned claims are not used here. The problem is aggregation of polyhedral EV flexibility rather than one nonlinear converter's state recovery. Theorem numbering refers to the inspected full manuscript; the abstract record verifies the initial submission date.

### T10. East, Cannon: convex hybrid-buffer allocation with hard energy constraints

**Source:** “Optimal Power Allocation in Battery/Supercapacitor Electric Vehicles Using Convex Optimization,” arXiv:2005.03678, **7 May 2020**; IEEE TVT 69(11), 12751–12762, online **10 September 2020**. [Primary full text](https://arxiv.org/html/2005.03678v1), [publisher metadata](https://ieeexplore.ieee.org/document/9193947/).

Sections II–III formulate energy/power-constrained allocation between two buffers, including nonlinear losses and an inner linear bound for a problematic concave upper constraint. This is a useful stronger comparator than a low-pass split. It blocks a generic claim that constrained optimal splitting of fast/slow buffers is novel. It has no AC reactive-service conflict or compute-task service contract.

### T11. Carpinelli, Mottola, Proto: data-center UPS active/reactive optimization

**Source:** “Optimal scheduling of a microgrid with demand response resources,” IET GTD 8(12), 1891–1899, first published **1 December 2014**, DOI 10.1049/iet-gtd.2013.0758. [Primary full text](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/iet-gtd.2013.0758).

Section 2.4, equations (15)–(17), includes data-center UPS battery active power, converter reactive power, rectifier/inverter efficiencies, and converter rating in a constrained microgrid scheduling problem. This establishes that data-center UPS P/Q coordination itself is old. It does not furnish a fast current/DC/task-recovery viability theorem.

### T12. Gururprasad et al.: compute elasticity with a small physical battery

**Source:** “Coupling a small battery with a datacenter for frequency regulation,” IEEE PES GM, **16–20 July 2017**, IEEE posting **1 February 2018**, DOI 10.1109/PESGM.2017.8274094. [Primary IEEE record](https://ieeexplore.ieee.org/document/8274094/).

The inspected primary abstract describes Lyapunov-based job scheduling that makes data-center elasticity complement fast physical battery response. It defeats the basic fast-buffer/slow-compute synergy framing. Full theorem-level text was not obtained in this audit; no unverified hard-deadline or recovery theorem is attributed to it.

### T13. Ulbig, Andersson: power–ramp–energy reach sets

**Source:** “Analyzing Operational Flexibility of Power Systems,” arXiv:1312.7618, **30 December 2013**; IJEPES 72, 155–164, **November 2015**. [Primary preprint](https://arxiv.org/abs/1312.7618), [publisher](https://www.sciencedirect.com/science/article/pii/S0142061515001118).

The Power Nodes framework treats controllable load, generation, and storage through power, ramp, and energy capabilities. Intertemporal ramp/power/energy linkage and operating-set reachability are established. A piecewise boundary where one of these constraints becomes active is expected methodology; G3 needs an analytically nontrivial coupling or certified gap, not a plotted constraint switch alone.

## C. Consequences for the proposed theorem

The following are this audit's recommendations, not claims attributed to the papers.

### Keep four mathematical claims distinct

1. An invertible nonlinear coordinate change to total electrical energy can be exact without making the trajectory set convex.
2. Replacing a quadratic loss equality by an inequality produces an outer relaxation unless an exactness theorem is proved.
3. Recovering one optimizer for a particular increasing-energy cost is weaker than equality of every feasible service/inventory projection.
4. Constructing a certified feasible trajectory is an inner result. It must satisfy the original modulation, actual-current, buffer, workload, and endpoint constraints under the same parameter tuple as the outer bound.

### Minimum physical sign and service discipline

Use p_g > 0 for power imported from the grid, p_c >= 0 for actual compute consumption, p_b > 0 for discharge from storage into the DC bus, and e_b' < 0 under discharge. For an ideal buffer and total fast electrical energy h, the balance is h' = p_g + p_b - p_c - losses, e_b' = -p_b, hence (h+e_b)' = p_g - p_c - losses. Separate buffer/converter losses if efficiencies are nonideal.

The grid service is a reduction/increase of import relative to a specified baseline, not fabricated positive BESS export. Reducing import during a sag increases buffer depletion unless compute consumption is actually reduced. A Q request consumes current headroom; a lost compute joule must have a declared consequence: forbidden unmet load, allowed shed work, or queued work with release/deadline/throughput constraints. Merely integrating electrical consumption does not prove useful task completion under DVFS, leakage, or dummy load.

### Tests that would justify the remaining narrow lead

- Derive outer and constructive inner sets as functions of exactly the same initial current, DC energy, buffer power/inventory, task backlog, sag, current rating, modulation bound, lag/ramp limits, and recovery deadline.
- Establish a positive, parameter-explicit gap bound (or equality on a nontrivial regime), rather than comparing two unrelated sufficient/necessary tests.
- Identify which constraint causes the gap: dynamic modulation/current realizability, loss relaxation, finite actuator acceleration, task deadline, or endpoint inventory. Distinguish this from simply insufficient energy.
- Include the relevant limiting cases: zero filter dynamics/current-only convex set; instantaneous buffer/ramp-energy scheduling; no reactive request; no task flexibility; lossless operation; and long recovery horizon.
- If temporal order matters, compare waveforms with identical peaks, total energy, and static capability score. Prove why memory changes feasibility, rather than presenting generic phase-lag effects.
- A state-restoring current waveform must reconstruct an admissible rectifier modulation input at all times. A pointwise P/Q curve does not supply that proof.

### Stop/reposition conditions

Stop calling the result an exact convex lifting if a loss/rank slack survives, if modulation reconstruction fails, or if terminal buffer/compute constraints are changed to obtain exactness. Reposition as a conditional relaxation plus constructive certificate if that is what is actually established. If the novel statement reduces to an energy-deficit area, standard ramp-energy LP, static converter feasible set, or a reparameterized battery recovery curve, treat it as synthesis or application rather than a new general theorem.

## D. Audit limits and exclusions

- No examined source proves the entire proposed combination of dynamic inductive/DC energy, rate/lag buffer, hard compute-service contract, sag-dependent P/Q current competition, and quantified same-parameter recovery sandwich. This is a bounded search finding, not proof that no such work exists.
- Several abstracts advertising exact convexity were found to require qualifications in the full text. The report deliberately distinguishes inspected propositions from abstract claims.
- Historical sources on Zecchino/Gerini capability curves, safety filters, current-limiter fault recovery, and the earlier G3 energy obstruction remain applicable. They were not re-audited comprehensively in this pass.
- Supplemental leads: Le Boudec–Tomozei's 2015 worst-case battery filling under service-curve contracts; Alaperä et al.'s 2018 UPS primary-frequency feasibility; “Stability Enhancement of Centralized UPS Data Center Systems Under Weak-Grid Conditions,” arXiv:2606.21536; “Large-Load Demand Flexibility as Virtual Storage,” arXiv:2607.04564. These reinforce context but do not replace T01–T13 as the principal comparisons.

**Recommendation:** continue only on a precisely stated dynamic feasibility/recovery theorem. Novelty status remains conditional; paper readiness is not established by this audit.
