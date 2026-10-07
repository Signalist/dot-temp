# Independent mathematical audit of round-3 interval resource certificates

Date: 2026-10-04 UTC. Reviewed core/prefix_resource_lower.py, core/interval_lower_certificate.py and core/interval_validate.py, plus the saved interval outputs. This is an independent mathematical/code review, not a proof-assistant verification.

## Lower: no substantive sign, box, or discretization error found

The saved 40-digit interval certificate reports

    E >= 0.455615336483606744450103432347843489227562181116369545721325.

Scope: arbitrary measurable controls |u|<=.5, two initial-P information groups, all initial phases, one common e0/E, safety on the first five units, no terminal constraints. By the shared-observation lemma this also applies to any causal frequency-feedback controller when bounded observation noise can hide the whole phase family through that prefix.

### Analytical outer relaxation

The LP X,Y states are the **positive control compensation**, so the physical frequency is free_frequency-Y. Thus the bounds

    max_phase free - .6 - dy <= Y <= min_phase free + .6 + dy

have the correct signs. At a timestamp t<=5 the high-group free envelope is [2g(t)-g(min(t,1)),2g(t)], and the low-group envelope is [g(t),g(t)+g(min(t,1))]. These are continuum envelopes; no phase mesh is being substituted for an all-phase condition.

For an arbitrary measurable input, replace u by its average in every time cell of width dt. This preserves the SOC at cell boundaries exactly. Let V be the within-cell primitive of u-u_average; V vanishes at cell boundaries and |V|<=P*dt. Integrating the frequency convolution difference by parts gives

    |Y_true-Y_average| <= P*dt*integral_0^infinity |k'(s)| ds
                       = P*dt*(1+2exp(-2)) = dy,

where k(s)=(1-s)exp(-s). The stated constant is conservative (a sharper primitive bound is possible) but valid. Dropping intersample SOC/safety requirements only enlarges the feasible set and is valid for a lower bound.

### Dual signs and residual correction

For the minimization LP, equality multipliers are unrestricted; upper-inequality multipliers and upper-bound multipliers are nonpositive; lower-bound multipliers are nonnegative. The interval code asserts those signs. The dual objective includes the nonzero Y-bound terms and u bounds with P*(upper_dual-lower_dual). The fixed X(0)=Y(0)=0, all SOC lower bounds, objective lower bounds, and zero-RHS constraint terms contribute zero.

With residual r=c-Aeq^T*lambda-Aineq^T*mu-lower_dual-upper_dual,

    c^T*x >= dual_objective + r^T*x
           >= dual_objective - sum_j |r_j|*box_j.

The boxes are valid after restricting to E<1; E>=1 already exceeds the claimed lower:

- |X|<=P, since the angle kernel g is nonnegative with total integral 1
- |Y|<=2P/e, since the frequency impulse kernel has L1 norm 2/e
- |u|<=P
- 0<=SOC,e0,E<1

Thus the residual correction is valid even though the serialized decimal dual is not exactly stationary. The current dt=.001 implementation also uses the correct t=1 branch in the exact phase envelope. If the routine is generalized to arbitrary dt, use exact/integer comparison for that branch rather than an unchecked floating k*dt comparison.

### Numerical enclosure scope

The lower tool uses outward mpmath.iv exponential coefficients and objective/residual operations, with exact-decimal dual entries. The stored lower is the lower endpoint of dual minus the upper residual allowance. This is materially stronger than simply reporting HiGHS's objective or its floating dual. It still trusts the numerical library and the code implementing the mathematical relaxation.

Optional hardening: explicitly assert that serialized upper/lower-bound multipliers vanish on infinite sides, and that the loaded vector dimensions/metadata match the reconstructed dt/LP. The producer currently does enforce zero infinite-side multipliers; this is not an observed defect in the saved certificate.

## Upper: analytic extrema logic and recovery signs checked

For a fixed phase endpoint, the load/control step events yield on each time cell

    y(t)=exp(-t)*(A*t+B).

Its only interior stationary point when A!=0 is t=1-B/A. Time endpoints and that point therefore suffice.

For phase r varying on a closed interval, write y(t,r)=F_control_and_initial(t)+sigma*H(t-r). On the lag cell 5j<=a=t-r<=5(j+1),

    H(a)=exp(-a)*(a*S_j-5*R_j),
    S_j=sum_{k=0}^j (-1)^k exp(5k),
    R_j=sum_{k=0}^j k*(-1)^k exp(5k).

Interior phase stationarity occurs at a=1+5R_j/S_j. Therefore the global extrema are contained in:

1. phase endpoints r=lo,hi
2. the stationary-lag lines
3. load-edge kink lines a=5j

Along each line, the phase contribution is constant; optimizing the remaining one-variable exponential polynomial is correct. Intersecting an enclosed lag interval with the time domain and enclosing its constant contribution is conservative. This is an analytical finite-candidate certificate, not phase-grid validation.

The signs in the terminal 3x3 matrix, in prefix control step events, and in the recovery RHS are consistent with physical y=free-control_compensation. SOC extrema occur at boundaries of the saved constant-control intervals. The exact terminal equations, rather than the small displayed interval residual, establish exact reset.

The independent validator certifies the saved trajectory for every phase in its declared interval. It does not by itself prove that a sampled/noisy causal policy always selects an interval containing the true phase, that all possible histories are represented, or that initial side information is matched. Those remain separate sensor-interface and nonanticipativity obligations. All-future safety after time 20 additionally uses exact terminal cancellation and the bounded-input passive-tail bound.

## Two formal upper-certificate issues found and corrected

In the version first inspected:

1. prefix_recovery discarded merged events when their enclosing magnitude was <=1e-40. A nonzero term cannot be silently removed from an outward certificate. Retain every event unless its enclosure is exactly [0,0], or add an explicit remainder enclosure
2. extrema enclosed the entire time cell for A straddling zero only if its magnitude exceeded 1e-35. A tiny straddling coefficient can still produce an interior stationary point. Always enclose the cell in this branch, or use a proven derivative-sign test

These terms are orders of magnitude below the saved safety margins, so they were not evidence of a physical violation. They matter for the truth of an outward-certification claim. The issue was reported immediately. At 02:56 UTC I directly re-inspected the corrected source: only exact [0,0] merged events are discarded, and every A enclosure containing zero gets a whole-cell bound. A completed rerun confirmed, with unchanged displayed upper bounds. The two reported defects are closed. Conservative displayed capacities remain P-channel E<=.353910425, frequency eta=.05 E<=.372402408, and the no-feedback same-filter ablation E<=.472559240; the maximum frequency enclosure remains below .599957500. Sensor-interface causal coverage remains a distinct obligation as noted above.
