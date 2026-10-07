# G3 theory review: text recovery

Recovery date: 2026-10-02. This is a newly organized, condensed reconstruction of the earlier THEORY_REVIEW.md from this worker's prior tool-call text. The original file is unavailable. No numerical calculation, simulation, source lookup, or performance search was rerun during recovery. Numerical illustrations and prior-paper metadata below are historical records, not newly verified evidence.

## Claim boundary

The defensible target is a necessary signed-service-loss certificate, a separately certified feasible policy, and their remaining gap. A failed controller does not prove physical impossibility. A necessary bound below the service budget does not prove feasibility. The scalar results below are elementary storage/optimal-control geometry, useful as a transparent baseline but insufficient alone for a strong novelty claim. Periodic terminal sets, periodic MPC, and generic P/Q allocation are established ideas.

Previously identified primary-source collisions, with links retained from the prior review:

- Jaramillo et al., *Service-Constrained Critical Energy-Headroom Boundaries for Current-Limited Grid-Forming Battery Converters*, Energies 2026, 19(18), 4464: https://www.mdpi.com/1996-1073/19/18/4464 . The earlier review found finite source, current, modulation, DC link, SoC, service deficits, recovery and repeated disturbances already covered. A new joint constraint classifier is not a sufficient distinction.
- Shamseldein, *Impedance-passivity coordination of hydrogen-coupled AI data centers for oscillation damping and fault ride-through at transmission interfaces*, https://doi.org/10.1016/j.epsr.2026.113557 . Earlier publisher/Crossref retrieval identified EPSR 262, article 113557, January 2027 issue with online records available in 2026; sustained 15 Hz forcing and a four-variable coordination QP were already described.
- Dynamic/periodic target MPC: https://arxiv.org/abs/1911.03304
- Periodic repetitive-task MPC: https://arxiv.org/abs/1911.07535
- Storage optimal control with rate constraints and losses: https://arxiv.org/abs/1307.0800

The potentially substantive distinction requires a materially sharp and physically realistic connection between signed oscillatory service, phase-dependent dynamic DC/current/modulation recovery, and sustainable operation. This remains a hypothesis to falsify, not an established novelty finding.

## Signed service contract

Take positive P as injection at a specified PCC. Freeze the continuous exogenous request r(t), reactive obligation, sag, charging allowance, recovery deadline and terminal tolerance before comparing controllers. Distinguish battery, DC bus, inverter-terminal, PCC and ideal grid-source powers.

    J_plus  = integral [r-P]_+ dt
    J_minus = integral [P-r]_+ dt
    J = J_plus+J_minus = integral |P-r| dt.

A one-sided discharge deficit can conceal failure to absorb negative half-cycles. Net integral error can cancel large misses in both directions. Retain directional, peak and per-cycle/phase-bin metrics. Reactive support must have a common hard requirement or a preregistered Pareto tradeoff.

For prescribed V and normalization kappa, actual current requires P^2+Q^2 <= (kappa V Imax)^2. With Q>=Qreq>=0, |P|<=sqrt((kappa V Imax)^2-Qreq^2). Qreq>kappa V Imax is itself infeasible. A current-reference circle does not establish actual current safety. A dynamic DC or modulation condition is generally not an exogenous P interval.

## Exact endpoint-only scalar result

Consider the reduced ideal model

    E_dot=-P, l(t)<=P(t)<=u(t), E(0)=E0, E(T)=ET,

with integrable, exogenous bounds and no intermediate energy constraint. Define

    p0=clip(r,l,u), D0=integral |p0-r|,
    S0=integral p0, R=E0-ET.

The endpoint is reachable iff integral l <= R <= integral u. When reachable,

    min J = D0 + |R-S0|.                            (1)

For any admissible P, the one-dimensional projection identity gives |P-r|=|p0-r|+|P-p0|. Integration gives the lower bound. If R>=S0, choose P=p0+alpha(u-p0), alpha=(R-S0)/integral(u-p0), to attain it; use interpolation toward l when R<S0. The equality case handles a zero denominator directly.

For a terminal energy band, intersect its required integrated-power interval [E0-ET_high,E0-ET_low] with [integral l,integral u]. Empty intersection proves infeasibility. Otherwise the second term in (1) becomes distance(S0,intersection). Honest terminal tolerance can therefore eliminate a purported recovery penalty.

D0 measures unavoidable instantaneous clipping. The second term is the additional signed service loss required to repay the clipped trajectory's energy mismatch. A mathematical illustration: r=A sin(omega t) over a cycle, P forced to zero on its positive half and allowed within +/-A on its negative half. Returning to the original ideal energy requires J=4A/omega, although instantaneous clipping alone costs only 2A/omega. This illustration is not a proposed utility operating case.

The prior work recorded 12 small 8-step LP checks agreeing with (1) at floating-point precision. Those old checks have not been recovered as raw outputs and are not revalidated here.

## Intermediate bounds, efficiency and cheap feasible allocation

For piecewise-constant sampled P and reference, ideal storage with intermediate bounds has an exact LP:

    minimize sum h_k z_k
    z_k>=P_k-r_k, z_k>=r_k-P_k
    E_(k+1)=E_k-h_k P_k
    l_k<=P_k<=u_k, Emin<=E_k<=Emax
    E_N in the declared terminal band.

This is exact for that sampled model, not automatically for a continuous sinusoid. Align disturbances to the mesh and bound quadrature and intersample errors.

For efficiencies, let g(P)=P/eta_d for P>=0 and eta_c P for P<=0, so E_next=E-h g(P). Since g is continuous and increasing, exact scalar feasibility still admits backward intervals. If K_next=[L,U],

    K = [Emin,Emax] intersect [L+h g(l), U+h g(u)].   (2)

Start from the terminal band. Empty K proves reduced-model infeasibility. With constant state limits and held P, energy is monotone within a step, so endpoint checks suffice. Time-varying limits require intersample treatment.

At state E, a next-step feasible interval is

    [l,u] intersect
    [g_inverse((E-U)/h), g_inverse((E-L)/h)].         (3)

Projection of the reference onto (3) preserves finite-horizon feasibility under these assumptions. It does not by itself certify minimum total tracking loss. This is a low-dimensional baseline policy, not a novel periodic-control principle.

The efficiency-aware necessary bound

    J >= D0 + eta_d |R-integral g(p0)|               (4)

follows from max g'=1/eta_d. For a terminal band replace absolute mismatch by distance. It is generally not exact. A stronger one-dimensional concave dual bound is

    J >= sup_lambda {lambda R + integral min_(P in [l,u])
                       [|P-r|-lambda g(P)]}.       (5)

The inner minimum needs only interval endpoints, zero if admissible, and r if admissible. Do not claim dual exactness for held-control sampled systems without proving the relevant strong-duality conditions.

Exact sampled signed tracking may use a MILP with discharge d>=0, charge c>=0, P=d-c, draw d/eta_d-eta_c c, and binary exclusivity; or a scalar dynamic program with certified approximation error. Dropping charge/discharge exclusivity can invent simultaneous cycling to dispose of energy and meet a terminal target without honest PCC tracking error. Such an LP is only a relaxation unless exactness is established.

## Physical DC/current lifting

The reduced battery equation cannot simply be assigned to PCC power during a transient. With electrochemical battery energy Eb, DC energy Edc and interface-inductor energy Ef,

    Eb_dot=-g_b(Pb)
    Edc_dot=Pb-Pinv-loss_dc
    Ef_dot=Pinv-Ppcc-loss_filter.

Hence

    integral Ppcc = Etot(0)-Etot(T)-Loss_total,      (6)

where Etot=Eb+Edc+Ef and passive loss includes integral(g_b(Pb)-Pb). This identity prevents a false impossibility certificate that ignores transient DC/inductor energy supply. Enclose endpoint energies and losses, obtain an interval R_ac for integral Ppcc, and combine it with a valid outer P interval:

    J >= D0 + distance(S0,R_ac),                    (7)

with reachable-budget intersection and emptiness checks. This is necessary for the full model, not generally sharp. An inner interval useful for safe control cannot prove that all physically feasible controls fail.

Source slew gives additional prefix energy cuts. If Pb(t)<=min(Pb,max,Pb(0)+Rup t), then

    integral_0^t Pinv <= Edc(0)-Edc,min
                        + integral_0^t Pb_upper,  (8)

sharpened by valid loss lower bounds. A companion lower cut needs a source lower envelope and loss upper bound. Neither cut establishes current/modulation realizability.

The physical interface obeys u=v+Ri+L i_dot+omega L J i, with actual norm(i)<=Imax and norm(u)<=k_mod Vdc. A static apparent-power circle cannot establish voltage feasibility during fast tracking or sag edges. A rigorous extension needs validated predecessor/reachable sets including current, DC energy, source lag and battery energy, or a proved inner-loop error tube with tightened outer constraints. Grid-forming models must also retain or bound synchronization and relevant integrator states. A low-dimensional command does not make those states disappear.

A local certificate on a declared compact domain is acceptable. Gridded simulation without interpolation/integration-error bounds is numerical evidence only. Use three verdicts: impossible when a valid outer certificate rules it out; feasible when a validated witness establishes it; unresolved otherwise. Nonlinear-solver failure or emptiness of a conservative inner set does not prove impossibility.

## Sustainable orbit and realistic scale

With forcing phase phi_dot=omega, a scalar periodic orbit requires integral_0^(2pi) g(Pstar(phi)) dphi=0 and

    Estar(phi)=Ebar-(1/omega) integral_0^phi g(Pstar(theta))dtheta.

The full plant also needs periodic electrical/source states and replenishment of all losses. Permanent positive mean battery injection is finite discharge, not an indefinitely sustainable battery-energy orbit. An electrically periodic pre-run can legitimately exclude drifting battery energy from its convergence test only if this distinction is explicit and SoC remains bounded over its finite duration.

For Pstar=b+A sin(phi), the uncompensated sinusoid consumes mean electrochemical power A(1/eta_d-eta_c)/pi. A sustainable bias b is negative. For |b|<A it solves

    0=.5(1/eta_d+eta_c)b
      +.5(1/eta_d-eta_c)(2/pi)
        [sqrt(A^2-b^2)+b asin(b/A)].

Historically computed illustration, not rerun: eta_c=eta_d=.96 and A=1 MW gave b approximately -25.98 kW before additional converter/filter losses. A strict +/-1 MW device cannot track that biased 1 MW-amplitude request at the charging trough. Reduce amplitude or declare an alternative replenishment schedule, shared by all comparators.

Recovery should target the actual-phase periodic physical state or a declared sustainable family/tube. Constant SoC under continuing forcing is not generally the right target. Conversely an artificially narrow energy-offset requirement can create a purely contractual advantage when the service permits a broad sustainable family.

Historical scale illustrations, not revalidated numerical outputs: a 1 MW/2 MWh battery changes ideal energy by 0.278 kWh in one second (0.0139% of capacity), or 1.389 kWh in five seconds (0.0694%). A 1 MW, 15 Hz sinusoid has only 2.95 Wh ideal energy amplitude (0.000147% of capacity). Ordinary SoC is normally nonbinding over seconds. Do not manufacture conflict through implausible C-rate or unexplained few-Wh reserve margins. Credible terminal tolerance can erase phase-sensitive battery-energy penalties; integrated power debt may be more meaningful than sub-Wh absolute SoC claims. DC/current/modulation dynamics may remain materially phase sensitive.

## Minimum mechanism test and stop criteria

Freeze one realistic plant and evidence-backed current, capacitance, voltage, slew/bandwidth, efficiency and modulation assumptions. Continue exogenous forcing throughout sag and recovery; initialize on the correct healthy operation. Do not resize equipment after failures.

A small first test uses four onset phases and three event strengths: inactive-constraint negative control, near-boundary competition, and a case ruled impossible by an outer certificate. Avoid making every sag an integer number of oscillation cycles. Compare a proper reactive-priority baseline, the proposed low-dimensional policy, strong periodic MPC, and separately labeled offline best-available full-horizon feasible optimization. Give MPC the same phase/forcing information, dynamic constraints, loss replacement, terminal tube and sufficient recovery horizon. Do not handicap it with constant SoC targets, missing DC states, different charging access or undisclosed solver restrictions.

A globally optimal controller for the same model and objective cannot be beaten on that objective. A useful low-dimensional result can instead be a near-optimal service gap, certified safety, and reduced computation. Report directional/per-cycle error, physical current amplitude/duration, modulation margin, DC energy/voltage, source MW/slew, SoC margin, phase-correct terminal distance, recovery time, timing and the inner/outer gap.

Ablate phase conditioning, loss compensation and dynamic DC/current tightening one at a time. Sweep credible terminal-energy tolerance before expanding simulations. Stop or downgrade claims that depend on generic periodic targeting, known weighted QPs, contrived C-rate/SoC, implausibly exact terminal energy, reference-current safety, power-location conflation, simultaneous-cycling relaxation, or unbounded intersample excursions. A strong periodic MPC closing the benefit defeats a performance-superiority claim; measured simplicity may remain worthwhile. Require a material dynamic effect above parameter/numerical uncertainty before broader research.
