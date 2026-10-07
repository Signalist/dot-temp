# Sharp finite-bang-arc approximation complexity

2026-10-03. This result concerns REPRESENTATION of epsilon-optimal continuously clocked trajectories. It is not an oracle, runtime, sample-complexity, or lower bound for all risk-certification algorithms. A many-switch clock may have a short formula such as sign(cos(2*pi*N*t)). Historical novelty has not been established.

## 1. General bounded-workload upper theorem

Use the fixed endpoint clock contract

    theta'=v, v'=rho*a, |a|<=1,
    theta(0)=theta0, v(0)=r,
    theta(T)=theta0+r*T, v(T)=r,

and the inactive-band condition rho*T/4<=min(r-omega_min,omega_max-r). Let multi-port powers be

    p_j=e_j(theta)*v,      0<=e_j<=e_max,j.

All ports share the same unwrapped phase. The energy primitive E_j is Lipschitz, with constant e_max,j. Profiles may have arbitrary bandwidth and need not have a uniformly bounded derivative. Let h_j be strictly proper LTI impulse responses with absolutely integrable derivatives on [0,T]. Initial electrical conditions and constant idle loads are the same across compared clocks.

Define

    B=sum_j e_max,j * integral_0^T |h_j'(u)|du.

For ANY feasible acceleration a and integer M>=1, there exists a feasible bang acceleration a_hat taking only +/-1, with at most 2M switches, such that

    max_t |theta_hat(t)-theta(t)| <= rho*T^2/(8*M^2),
    |y_hat(T)-y(T)| <= rho*T^2*B/(8*M^2).                                (1)

The replacement preserves the original phase and speed at every cell endpoint, not merely at final T. Consequently work, terminal speed, and energy at every port are exactly preserved. No arbitrary clock reset is introduced.

### 1.1 Constructive cell replacement

Partition [0,T] into M equal cells of length Delta=T/M. In local cell coordinate s in [0,Delta], put b(s)=(1-a(s))/2 and let

    q=integral b(s)ds,
    mu=integral s*b(s)ds.

Because 0<=b<=1,

    0<=q<=Delta,
    q^2/2 <= mu <= Delta*q-q^2/2.                                      (2)

The extremal first moments at fixed q are obtained by placing unit density in the leftmost or rightmost interval of length q. Thus, if 0<q<Delta, the interval

    I=[mu/q-q/2, mu/q+q/2]

lies inside the cell. Replace b by the indicator of I and set a_hat=1-2*indicator_I. This matches both the zeroth and first moments of a. For q=0 use all +1; for q=Delta use all -1.

In terms of the original acceleration moments A0=integral a, A1=integral s*a,

    q=(Delta-A0)/2,
    center=(Delta^2/2-A1)/(2q),

with the same degenerate conventions.

Global a_hat equals +1 outside a union of at most M negative intervals. That union has at most 2M boundary switches, including all cases where intervals touch cell boundaries or merge. A separate per-cell boundary-switch surcharge is unnecessary.

### 1.2 Phase and output error proof

Equal cellwise moments imply equal phase and speed at both ends of every cell. The difference acceleration is bounded in magnitude by 2rho. Apply the sharp clamped phase envelope on a cell: the largest absolute displacement is (2rho)*Delta^2/16=rho*Delta^2/8. This proves the first part of (1).

The endpoint-energy terms cancel exactly in integration by parts, leaving

    y_hat(T)-y(T)
       =sum_j integral_0^T h_j'(T-t)
              [E_j(theta_hat(t))-E_j(theta(t))]dt.

The primitive Lipschitz bound then gives the second part of (1). No bound on e_j' occurs. Global endpoint moments ensure that a_hat also satisfies the speed band under the inactive-band condition.

The theorem does not cover active speed bounds without modification: preserving cell endpoints alone does not guarantee that a replacement stays inside a tighter intermediate speed band. A finite jerk or continuous-acceleration requirement also needs a separate smoothing/error argument.

## 2. Consequence for finite-arc optimal values

For a given workload profile collection e, let V(e) be the exact supremum of terminal output over all feasible clocks, and V_m(e) the supremum over feasible bang accelerations with at most m switches. For m>=2,

    0<=V(e)-V_m(e)
       <= rho*T^2*B / [8*floor(m/2)^2].                                  (3)

The same bound applies to approximation of the worst absolute terminal output: | |y_hat|-|y| |<=|y_hat-y|.

An epsilon-optimal bang representation therefore exists with

    m <= 2*ceil(sqrt(rho*T^2*B/(8*epsilon))),

apart from the harmless minimum of two switches. This is bandwidth-independent O(epsilon^-1/2) representation complexity.

The result is constructive when a suitable feasible clock is ALREADY supplied: compress its cell moments. It does not provide an efficient algorithm for finding an unknown optimal clock, nor does it show that evaluating or certifying V requires that many computational operations.

## 3. Matching lower theorem with fixed grid, rho, work, and energy

Use the fixed model and workload sequence proved in MULTIPORT_SWITCH_COMPLEXITY_ADDENDUM.md:

    T=r=rho=1, speed band [3/4,5/4],
    h1(u)=-exp(-u), h2(u)=exp(-u),
    e_j are C-infinity, period one, 3/4<=e_j<=5/4,
    integral_0^1 e_j(theta)dtheta=1 at BOTH ports.

The allowed workload class contains no bandwidth or derivative constraint. Let chi, A, I_chi, W_max, C_W, C_V be the FIXED constants from that addendum, and write C=C_W+C_V.

The matching Theta(m^-2) rate below is for this amplitude-only class. It is not asserted for classes with fixed uniform slope or C^r bounds. Such bounds do not, however, imply a uniform EXACT switch bound: rescaling the counterexample by A_N=A0*N^-r preserves its exact optimizers while bounding C^r norms and shrinking the objective to order N^-(r+2). A sharp approximation rate for those smoother classes would require a separate theorem.

For all sufficiently large integers N, the constructed profile e^(N) has

    V(e^(N)) >= A*I_chi/(4*pi^3*N^2),                                   (4)

while every feasible m-switch bang trajectory has

    |y(1)| <= A/(8*pi^3*N^3) * [2m*W_max+C].                            (5)

The latter also applies to arbitrary piecewise-constant accelerations in [-1,1] with at most m jumps: their total variation is at most 2m, the only property used in the bound.

Set

    alpha=I_chi/(2W_max)>0,
    beta=C/(2W_max),
    gamma=A*I_chi/(8*pi^3)>0.

Whenever m<=alpha*N-beta, equations (4)-(5) imply

    V(e^(N))-V_m(e^(N)) >= gamma/N^2.                                  (6)

This is a constant-relative-quality gap, rather than merely a statement that the exact optimizer has many switches. The same gap holds for worst absolute output versus its m-switch approximation.

For each sufficiently large m, choose

    N_m=max(N0, ceil((m+beta)/alpha)),

where N0 is any fixed threshold beyond which the witness lower (4) holds. Then (6) supplies

    sup_e [V(e)-V_m(e)] >= gamma/N_m^2
                         >= gamma*alpha^2/(m+beta+alpha)^2              (7)

once the N0 branch is inactive.

The independent analytical audit supplies N0=2304, L1<=16, L2<=416, and I_chi>=exp(-1/2)/3, so none of these existence constants requires unvalidated numerical derivative norms.

Combined with the uniform upper (3), this gives the sharp asymptotic statement

    sup_e [V(e)-V_m(e)] = Theta(m^-2),       m -> infinity,              (8)

for this FIXED two-port grid and fixed clock/work/energy/amplitude contract. Equivalently, the worst-case number of finite bang arcs or piecewise-constant acceleration segments required for epsilon-optimal representation is Theta(epsilon^-1/2) as epsilon -> 0.

For this workload class an explicit common upper constant is

    B=(5/2)*(1-exp(-1)),
    K=B/8=5*(1-exp(-1))/16,

so the upper error in (3) is K/floor(m/2)^2. The lower constants are conservative but strictly positive and independent of m, N, and the workload selected from the sequence.

## 4. Interpretation and boundaries

- The upper theorem shows that unrestricted workload bandwidth does NOT prevent useful fixed-absolute-accuracy approximation by a finite clock representation.
- The mixed-sign construction shows that the exponent 1/2 cannot be uniformly improved for that representation class under amplitude/work/energy information alone.
- Exact optimizer switches can grow without bound, while an epsilon-optimal representation still has a bandwidth-independent bound. These statements are compatible.
- Uniform slope or any fixed finite-order C^r bound alone does not restore a uniform exact switch bound. The sharp Theta(epsilon^-1/2) representation rate proved here remains scoped to the amplitude-only workload class; no matching rate for C^r-constrained classes is claimed.
- The example's worst risk is Theta(N^-2). The lower bound does not imply large physical violations or increasing hazard at large N.
- This is NOT a lower bound on the runtime, oracle queries, or memory of every optimization or certification method. Symbolic formulas, averaging, duality, or other compressed representations may avoid enumerating all switches.
- The upper bound compresses a supplied witness. A global solver is still needed if one wants a numerical value certificate and no sufficiently good witness is known.
- The sharp rate is for scalar terminal output under the fixed final work/speed promise. Peak-over-time, active speed bands, measurement uncertainty, finite jerk, and nonlinear electrical systems require separately stated extensions.
- Moment matching, bang-bang approximation, and bounded-variation estimates are classical tools. Literature comparison is still required before presenting the sharp combined result as historically new.
