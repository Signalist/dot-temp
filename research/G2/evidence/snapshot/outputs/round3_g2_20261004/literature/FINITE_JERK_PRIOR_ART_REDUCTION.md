# Classical reductions for finite jerk and bounded workload slope

2026-10-04 UTC

## Conclusion

The finite-jerk m^-3 upper is a direct third-order perfect-spline interpolation consequence, and the bounded-slope m^-4 output upper is a fourth-order primitive interpolation plus weak-error estimate. Changing the controlled derivative order does not create a new approximation principle. The complete positive equal-energy common-clock full-future response-value realization remains the narrow candidate for further historical review.

Two direct classical reductions even improve the safe switch counts in the draft: 3M global jerk switches suffice for the m^-3 upper, and 4M suffice for the m^-4 upper. They replace the respective local-concatenation counts 4M−1 and 5M−1. A primitive argument also improves the displayed order-four leading constant by a factor eight. None of these improvements should be represented as a new spline theorem.

This note examines `theory_worker/FINITE_JERK_AND_BANDWIDTH_THEOREMS.md` without editing it. It uses the same inactive acceleration/speed contract and common continuation. It does not supply an active-band finite-jerk interpolation theorem.

## 1 Third-order interpolation gives the jerk compression directly

Use [Goodman–Lee Theorem 1 and Corollary 6](https://www.researchgate.net/publication/243060150_Another_extremal_property_of_perfect_splines), [DOI](https://doi.org/10.1090/S0002-9939-1978-0481760-9), with derivative order k=3. At M+1 mesh points prescribe theta, theta', theta''. Repeating every mesh point three times gives 3M+3=n+k data, hence n=3M. The interpolating perfect spline has third derivative ±J and at most 3M internal knots.

As in the degree-two reduction, if J exceeds the minimum possible derivative norm, choose strictly feasible data representative and apply Theorem 1; if equality holds use Corollary 6. All endpoint acceleration, speed and phase data survive. The draft's redundancy proof then ensures the entire interpolant obeys the acceleration and speed limits.

On each cell, d=theta_hat−theta has its first three Taylor data zero at both ends and |d'''|<=2J. Taylor's integral remainder from the nearer end yields

    ||d||_infinity <= J Delta³/24.

The energy-primitive output Lipschitz transfer gives J B/(24 M³), exactly the displayed strong-error upper constant, with a better global switch count. Thus for m>=3 one may use M=floor(m/3) rather than floor((m+1)/4). This is a representation existence bound. Finding the old theorem's knots or an unknown good clock is a separate computational issue.

The draft's moment-body proof is valid classical polynomial-moment saturation. It gives a constructive conceptual local route, whereas the global spline theorem avoids the extra intercell switch charge. Neither provides a new third-order approximation rate.

## 2 Fourth-order primitive interpolation gives the weak-output bound

Define the ordinary time primitive

    F(t)=integral_0^t theta(s)ds.

Then F'=theta, F''=v, F'''=a and F''''=j. Apply the same old theorem with k=4 and four repeated data at each mesh point: F,F',F'',F'''. There are 4M+4=n+4 data, hence at most 4M global switches in the bang jerk F_hat''''. Set theta_hat=F_hat'. This preserves the phase/speed/acceleration data and gives, on every cell,

    integral_cell (theta_hat-theta)dt=0.

Let G=F_hat−F. Its derivatives through order three vanish at every mesh point, while |G''''|<=2J. Therefore

    ||G||_infinity <= J Delta⁴/192.

Also d=G'=theta_hat−theta still obeys ||d||<=J Delta³/24. Continue both clocks identically after t=1; G stays zero there because F_hat(1)=F(1).

For each port and observation time tau, write b=min(tau,1), assume h_j(0)=0, and Taylor-expand the energy primitive:

    E_j(theta_hat)-E_j(theta)=e_j(theta)d+r_j,
    |r_j|<=L_j d²/2.

On [0,b], put f_j(t)=h_j'(tau-t)e_j(theta(t)). The linear term is a weak functional of d and can be integrated once:

    integral_0^b f_j d = f_j(b)G(b)-integral_0^b f_j'G.

This formula automatically handles the one possible partial observation cell. With T=1, u=1.1 and the draft's kernel norms,

    ||f_j||_infinity<=e_max,j M1,j,
    integral_0^b |f_j'|<=e_max,j M2,j+L_j u M1,j.

Consequently the same hypotheses yield

    sup_tau |Delta y(tau)| <= C4_new Delta⁴+C6 Delta⁶,
    C4_new=(J/192) sum_j [e_max,j M2,j+L_j u M1,j+e_max,j M1,j],
    C6=(J²/1152) sum_j L_j M1,j.

For tau>=1 the boundary G(b) is zero, so retaining its bound is conservative. Use M=floor(m/4) for m>=4. The order-four term is an ordinary integration-by-parts/weak-error consequence of moment cancellation; the Taylor remainder is an elementary nonlinear correction. The assumptions h_j(0)=0 and a uniform profile slope are substantive. Without them, the stronger conclusion is not supplied by this argument.

## 3 The m^-3 scalar value lower also has a classical linear baseline

The following self-contained construction further narrows the novelty claim. Put k=2 pi N and maximize

    L_N(eta)=-integral_0^1 sin(kt)eta(t)dt,

under eta,eta',eta'' zero at both endpoints and |eta'''|<=J. Three integrations give

    L_N(eta)=k^-3 integral_0^1 j(t)cos(kt)dt.

Every m-jump jerk in [-J,J] therefore satisfies

    |L_N|<=2Jm/k⁴.

There is a fixed bounded unit-cell jerk with all three required moments zero and a positive cosine correlation. One explicit choice is

    p2(s)=6s²−6s+1,
    c=15/pi²,
    u(s)=[cos(2 pi s)−c p2(s)]/(1+c).

Since |p2|<=1, |u|<=1. Direct integration gives integral s^r u=0 for r=0,1,2, and

    c0=integral_0^1 u(s)cos(2 pi s)ds
      =[1/2−45/pi⁴]/[1+15/pi²]>0.

Let b'''=u with all three initial data zero; the moment conditions make its three final data zero as well. Repeating the bridge gives

    eta_N(t)=J N^-3 b({Nt}),       j_N(t)=J u({Nt}),
    L_N(eta_N)=J c0/k³.

Thus whenever m<=pi c0 N/2, the low-jump value is at most half the witness value, giving a gap at least J c0/(16 pi³ N³). Choosing N proportional to m yields an m^-3 gap. The inactive contract ensures acceleration and speed feasibility. No nonlinear-width theorem is required.

This establishes only a baseline mechanism with a freely chosen linear objective, using elementary classical operations. It does not independently establish the nonlinear workload theorem: all low-jump nonlinear competitors still need the inverse-phase BV estimate, and every future observation still needs the uniform kernel argument.

## 4 A bounded-slope matching rate is already a rescaling corollary

The finite-jerk theorem's exact opposite-kernel construction has e1,N=1+P_N'/2, e2,N=1−P_N'/2, and P_N is linear in A. At every clock and observation the common baseline cancels, so output is exactly linear in A. Since A is positive, both unrestricted and restricted absolute-peak values scale by A.

Replace the common family amplitude A by A/N, leaving J, the kernels, Q, clock contract and energy constraints fixed. The old all-time upper and witness lower are both divided by N. In particular the condition m<=alpha N−beta is unchanged, while the gap becomes gamma/N⁴.

At the same time,

    ||e_j,N'|| <= (A/(2N))[2 pi N Q0+2Q1+Q2/(2 pi N)]
               <= (A/2)[2 pi Q0+2Q1+Q2/(2 pi)] =: L.

The profile class therefore has one fixed finite slope bound L, strict positivity, and unit energy per port. Combining the scaled lower with the order-four upper yields

    sup_(profiles in this fixed bounded-slope amplitude class)
          [R(e)−R_m(e)] = Theta(m^-4).

Equivalently, the restricted scaled sequence itself has the same matching rate, because the upper applies uniformly to every member. This is a direct homogeneity corollary conditional on the draft's established lower constants; it is not a new lower-bound mechanism.

It is crucial that bandwidth remains unbounded: the scaled profiles still have degree N+2. This proves no matching m^-4 lower at a fixed Fourier cutoff K. The linearized fixed-cutoff exact-switch result in the companion note is a different statement. Smoothness of fixed finite order and exact bandwidth truncation are not interchangeable contracts.

## 5 Narrow residual contribution and publication boundaries

A defensible residual claim concerns the **constrained realization** of classical representation/value-gap mechanisms: fixed stable filtered output, positive equal-energy shared-clock loads, exact service completion and continuation, finite jerk, all-time peak quantifiers, and the regularity boundary between amplitude-only and uniformly slope-bounded profiles.

It remains synthetic. Replacing two opposite kernels by three non-opposite ones while retaining an exact aggregate nullspace does not create a generic grid realization. Shrinking perturbation tolerances give finite-instance stability, not an open fixed-radius robustness theorem. The response scale and model-error tolerance shrink with N. None of the exponents is a lower bound on all numerical, symbolic or oracle algorithms.

This pass verifies direct reductions and supplies missing mathematical comparisons. It does not establish historical originality of the final constrained embedding; further theorem-level literature review remains appropriate.
