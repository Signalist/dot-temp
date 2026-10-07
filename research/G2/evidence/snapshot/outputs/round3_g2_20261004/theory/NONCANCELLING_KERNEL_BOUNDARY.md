# A non-opposite, nonproportional kernel boundary with an exact two-switch optimizer

2026-10-04. This is a structural boundary, not a robustness theorem for the old full-future lower bound. The objective here is signed terminal response; full-future absolute peak requires a separate argument. This note uses a bounded-acceleration class, separate from the finite-jerk class: its two acceleration jumps are inadmissible under a finite-jerk requirement.

## 1. Fixed positive, equal-energy work contract

Let 0<rho<4 and impose a strictly positive speed band. Let T=r=1, theta'=v, v'=rho*a, |a|<=1, theta(0)=0, theta(1)=1, v(0)=v(1)=1. Suppose the speed band contains [1-rho/4,1+rho/4], so it is inactive for the whole endpoint-feasible class. For the confirmation experiment rho=.05 and the imposed band is [.9,1.1]. After time 1 every clock continues theta=t, v=1 with the same electrical state carried forward. There is no state or phase reset.

Let D be any continuously differentiable period-one function with D(0)=0 and |D'|<=A<2. Put e1(theta)=1+D'(theta)/2 and e2(theta)=1-D'(theta)/2. The physical assumption is p_j=e_j(theta)*v. It fixes each port's energy at exactly 1 and fixes completed shared work at 1. It is an ideal energy-per-work model; it is not a calibrated DVFS model. The finite-band experiment uses D_N=-A*sin(2*pi*N*theta)/(2*pi*N), so e_j have exact Fourier degree N, and A=.01.

For s>=0, use

h(s)=s^2 exp(-s),
g(s)=(s^2+.1s^3)exp(-s),
h1=h+epsilon*g, h2=-h+epsilon*g.

For epsilon>0 these kernels are not negatives of each other, and because g/h=1+.1s they are not proportional. Both remain stable strictly proper LTI kernels. They are synthetic filtered outputs, not an identified network transfer.

## 2. Exact monotonicity theorem

Take the same zero electrical initial condition. Since h_j(0)=0, the physical terminal response is exactly

J(theta)=integral_0^1 [h'(1-t)D(theta(t))+2epsilon*g'(1-t)theta(t)]dt.

This is the sum of the two energy-primitive identities, with no nominal-baseline subtraction. At fixed t its derivative with respect to phase is

q(t,theta)=h'(1-t)D'(theta)+2epsilon*g'(1-t).

For 0<s<1,

h'(s)=(2s-s^2)exp(-s)>0,
g'(s)=h'(s)+.1(3s^2-s^3)exp(-s)>h'(s).

Consequently q>0 whenever 2epsilon>=A and epsilon>0. The classical simultaneous upper phase envelope theta_plus(t)=t+rho*b(t) dominates every admissible phase at every t. Therefore

J(theta)<=J(theta_plus),

equality only when the phases coincide everywhere. The optimizer is acceleration rho times (+1,-1,+1) with switches at 1/4 and 3/4. It uses two switches, independently of D's bandwidth, derivative oscillation count, or smoothness beyond the stated assumptions.

This proves that for this non-opposite, nonproportional family the signed-terminal response-value gap is identically zero for all m>=2. The conclusion is exact at finite rho, not just linearized. The lower phase envelope gives the exact minimum by the same monotonicity argument.

The same argument works with an active speed band after replacing the three-arc envelope by the classical clipped five-arc envelope; then at most four switches suffice. The confirmation experiment deliberately keeps the band inactive so a two-switch free-knot baseline can be matched exactly.

## 3. Robustness and what is not proved

The conclusion persists under any perturbation of the kernels/profiles that preserves positive phase derivative q. One explicit sufficient relative-derivative condition is

sum_j e_max,j |delta h_j'(s)| < (2epsilon-A)h'(s), 0<s<1.

Thus an exact opposition relation is unnecessary for the easy class. This is a weighted sign cone. It is not automatically an open ball in the unweighted C1 norm because h' vanishes at s=0; a perturbation with arbitrary endpoint derivative requires separate treatment.

This theorem does not prove that every perturbation of the hard opposite-kernel construction makes it easy. Nor does it show the old asymptotic full-peak lower survives a fixed nonzero perturbation. It instead gives a constructive family where a fixed common-mode component removes the very switching difficulty used by that lower bound. In the experiment the common-mode coefficient .01 should be compared to the .01 differential workload amplitude, not described as negligibly small compared with the useful signal.

The statement is about terminal response. The derivative signs beyond lag 1 differ, and full-future absolute peaks cannot inherit the same two-switch claim without another proof. Continuing tail operation is specified but does not affect the already fixed terminal value.

## 4. Classical ingredients and research significance

Simultaneous phase envelopes and monotone-integrand optimization are classical; the old dossier already states the scalar version. The useful refinement here is the exact, nonproportional mixed-port decomposition and cancellation threshold for a positive shared-work contract. It supports a classification result: the difficult representation behavior depends on unresolved signed competition between port kernels, while a sign-coherent aggregate phase derivative admits a constant-size exact optimizer. This is a defensible boundary/result organization, not a standalone new general optimizer.
