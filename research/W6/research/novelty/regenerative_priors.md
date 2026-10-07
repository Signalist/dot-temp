# W6: regenerative, transition-cost, and slew-aware priors

Review date: 2026-10-04 UTC. Targeted primary-source inspection, not an exhaustive novelty certificate. No new experiments, external code, purchases, authentication, outreach, or paper redistribution. The W6 statements being compared were read in `outputs/round3_w6_20261004/theory/FULL_CYCLE_THEOREMS.md`.

**Reconstruction note:** The execution environment reset at approximately 14:16 UTC removed the earlier copy of this file. This note was reconstructed at 14:17 UTC from retained context of the direct primary-source reads made around 14:09–14:13 UTC. Sources have not been downloaded or reread after the reset. The parent is separately restoring the original W6 package.

## Decision

The broad ingredients are established: complete return-cycle energy accounting, stochastic terminal-mode return costs, global stochastic optimization, critical energy-per-work speeds, and deterministic convex processor scheduling with a slew constraint. These ingredients must not be advertised independently as new.

The positively identified distinction is the coupling in W6 between useful service during a continuously slew-limited power trajectory and a mandatory fastest physical return from the random EOS state. With its particular full-cycle ledger this produces `H'(z)=G(z)/R`; this is the premise behind the exact recovery projection and the sharp power-law tail-hazard convexity result. The primary models below do not instantiate that coupling: their explicit transition models, service rules, and objective classes are different. This supports a narrow theorem-level positioning; it does not certify priority for the theorem.

## R1. Rao and Vrudhula, DAC 2005

**Title:** Energy Optimal Speed Control of Devices with Discrete Speed Sets. DAC 2005, pp. 901–904.

**Primary full text:** [UCI proceedings copy](https://websrv.cecs.uci.edu/~papers/dac05/papers/2005/dac05/pdffiles/p901.pdf)

**Read locators:** Section 2, printed p.902; Section 3, printed p.903, Lemmas 1–6, Corollaries 1–2, Theorem 1. This four-page proceedings text states that proofs are omitted for space; the linked extended version was not obtained.

**Result:** For known work and a fixed time allowance, the paper reduces the W-convex discrete-speed problem to at most two used speeds. Its Q-function is energy per work; Corollary 2 makes it monotone on either side of the task-independent minimizing speed. Theorem 1 chooses between that speed and the minimum feasible speed pair, accounting for fixed energy overheads. Transition delays are treated as small relative to deadlines.

**W6 inclusion/separation:** Critical-speed existence and unimodal energy-per-work reasoning are precedents. A fixed overhead and negligible-delay transition is not W6's productive ramp with slope constraint and EOS-dependent return integral. W6's cap needs its own feasible-path argument.

**Related final article, metadata only:** Rao and Vrudhula, IEEE TCAD 25(12):2737–2746 (2006), [institution record](https://experts.azregents.edu/en/publications/energy-optimal-speed-control-of-a-generic-device/), DOI 10.1109/TCAD.2006.882598. Do not attribute an inspected full-text theorem to this version.

## R2. Simunic, Boyd, and Glynn, IEEE TVLSI 2004

**Title:** Managing Power Consumption in Networks on Chips. IEEE TVLSI 12(1):96–107. DOI 10.1109/TVLSI.2003.820533.

**Primary full text:** [author-hosted final article](https://web.stanford.edu/~glynn/papers/2004/SimunicBoydG04.pdf); [author publication record](https://stanford.edu/~boyd/papers/pwr_noc.html)

**Read locators:** Section V, pp.100–102, Figs.4–5, equations (7)–(14); Section VI, p.103, equation (15). Also checked [author manuscript](https://cseweb.ucsd.edu/~trosing/papers/tvlsi03.pdf), whose equations are more legible in text extraction.

**Result/separation:** Whole-renewal costs include transitions and service. Equations (10)–(11) convert a performance-per-renewal-time objective with power constraint into an LP. The state model has discrete active voltage/frequency settings, sleep states, exogenous arrivals and randomized idle timeouts. It is a direct precedent for full-cycle stochastic accounting. W6 instead optimizes a per-job weighted cycle cost while continuously producing work during bounded power ramps; identifying the objectives requires more than calling both systems regenerative.

## R3. Simunic, Benini, Glynn, and De Micheli, IEEE TCAD 2001

**Title:** Event-Driven Power Management. IEEE TCAD 20(7):840–857.

**Primary full text:** [author-hosted final article](https://web.stanford.edu/~glynn/papers/2001/SimunicBeniniGMicheli01.pdf); [author record](https://web.stanford.edu/~glynn/papers/2001/SimunicBeniniGMicheli01.html)

**Read locators:** Section IV-A, pp.846–848, equations (6)–(10), Fig.9 and Table III; Section V-A, pp.849–851, Theorem V.1, equations (12)–(20); Section V-B, pp.851–852, equations (21)–(23).

**Result:** Renewal and time-indexed semi-Markov formulations handle general first-arrival distributions, transition time/energy and globally optimized power-management policies. Theorem V.1 is an average-cost optimality equation; its proof is referred to the paper's reference [38]. The time-indexed formulation retains elapsed-time information for nonmemoryless events.

**W6 inclusion/separation:** Neither renewal optimization, survival conditioning, nor DP/state augmentation is new. Here requests wait until a physical mode transition completes; the state/action model does not continuously allocate productive service on a bounded actual-power ramp. The theorem provides a general stochastic-control framework, not the stated W6 recovery-domain convexity certificate.

## R4. Irani, Shukla, and Gupta, ACM TECS 2003

**Title:** Online Strategies for Dynamic Power Management in Systems with Multiple Power-Saving States. ACM TECS 2(3):325–346. DOI 10.1145/860176.860180.

**Primary full text:** [author-lab PDF](https://mesl.ucsd.edu/pubs/irani_tecs03.pdf)

**Read locators:** Section 3, pp.330–331; Section 5.1, pp.333–334, equations (1)–(4), Theorem 2; Appendix proof of Theorem 2, pp.343–344.

**Result/separation:** Their random idle-period objective pays both idle energy and terminal-mode start-up energy. Additive downward costs can be folded into power-up parameters. Theorem 2 bounds the probability-based policy relative to an offline comparator. W6 shares random-horizon running-plus-return-cost structure, but controls a productive ramp rather than thresholds among idle modes; its hazard theorem certifies path-functional convexity, not a competitive ratio.

**Independent comparison calculation:** Differentiating their two-state equation (1) gives `J'(tau)=S(tau)[alpha-b h(tau)]`, with `b` the startup cost. Thus a hazard-based running/return-cost balance is already inherent in that model. This derivative is our comparison, not a named result claimed from their text.

## R5. Official Stanford processor-slew convex exercise

**Title:** Minimum energy processor speed scheduling, Problem 5, printed p.7 of the EE364a final-exam PDF. Publication date not verified; not a research-paper citation.

**Primary text:** [Stanford course PDF](https://see.stanford.edu/materials/lsocoee364a/final.pdf)

**Explicit formulation:** It gives fixed job work, releases/deadlines, convex per-period energy, a discrete-time speed bound and `|s[t+1]-s[t]|<=R`, and asks for a convex formulation (using service-allocation variables).

**Use:** This is an authoritative sanity check against claiming that slew-aware processor energy scheduling is intrinsically novel or nonconvex. Its calendar-time speed slew and fixed known work do not equal W6's actual-power slew and EOS-dependent terminal recovery. Do not use an unverified 2007 date.

## Exact model-comparison ledger

| W6 claim component | Direct precedent or diagnostic | Safe positioning |
|---|---|---|
| Full return-cycle energy and time ledger | R2–R3 renewal time and cost calculations | Established modeling principle |
| Random ending plus state-dependent return/start-up cost | R4 Section 5.1 | Established structural idea |
| Critical energy-per-work speed | R1 Corollary 2 and Theorem 1 | Established; cite before W6 cap lemma |
| Nonmemoryless survival information and global control | R3 TISMDP; existing Xu2007 comparison | Established methods |
| Convex deterministic processor scheduling with slew | R5; parent's independent Wu–Li–Chen check | No broad novelty claim |
| W6 `H'=G/R` cancellation | Requires same mandatory physical return and running ledger | Specific identity, with elementary integration-by-parts proof |
| Exact `min(z,R(M-x))` recovery projection | Requires productive maximum descent to consume stopping-work reserve | Candidate structural increment; compare exact hypotheses |
| Critical cap with nonzero initial forced-descent prefix | Requires path feasibility under W6 slew and terminal fee | Candidate extension of an established critical-speed idea |
| Sharp `h(x)(M-x)<=(1+2 beta)/(1+beta)` convexity boundary | R4 hazard balance concerns a different scalar optimization | Candidate narrow theorem; no priority certification here |

## Analytical guardrails for paper framing

1. Do not equate a renewal-reward ratio with W6's `E[E_cycle]+c E[T_cycle]`. If independent repeated jobs regenerate only at full return, throughput and average power would be ratios involving mean cycle duration. W6's chosen weighted per-cycle objective remains legitimate, but that interpretation must be stated.
2. Generic stochastic control can represent very broad models after state enlargement; representation is not a theorem-level inclusion of W6's exact projection or convexity threshold. Conversely, naming familiar transformations and DP does not establish novelty.
3. The defensible claim to test is the combined structural result under the explicit W6 contract, especially recovery projection followed by the sharp convexity threshold. The critical-power root alone and the terminal-to-running cost rearrangement alone are weak novelty candidates.
4. For R4, the unknown variable is elapsed idle time before an exogenous request. In W6, work determines EOS and its physical time depends on the chosen power. Replacing one independent variable by the other changes service dynamics and must be justified, not assumed.

## Access / evidence ledger

- Before the reset, read primary full-text pages through the web text tool on UCI, Stanford, UCSD and the authors' laboratory domains. No reliance on ResearchGate, Scribd or search-result claims for theorem content.
- R1 is the published short proceedings paper; its omitted proofs and the uninspected 2006 final are disclosed.
- R2 final text and author manuscript were both available. Two screenshot attempts (R2 and R5) returned cache-miss errors; no screenshot retained. Text inspection succeeded; equations (10)–(11) were cross-checked in the legible author manuscript.
- No access denial, paid gate or login was bypassed. No external executable or new simulation was used.
- Stored material is this original comparison, limited mathematical expressions and source locators, not article text or figures.
- This file is a reconstruction from retained direct-read results, not a fresh post-reset read or a claim that the original local input files remain available.
