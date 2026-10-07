# G6: exact structure, arithmetic approximation complexity, and workload semantics

## Executive assessment

The support series, its rational-angle reduction, and the contracting self-similarity framework are prior art. In particular, Duda's *Analysis of the convex hull of the attractor of an IFS*, arXiv:0710.3863v2, equations (14)–(15), explicitly contains the same exponentially weighted absolute-trigonometric support family (up to scale, rotation, and reciprocal notation for contraction). Do not present those facts as a new theorem.

Two narrower results are proved here for further novelty review:

1. **Arithmetic complexity classification:** on every fixed compact interior capacity-slope interval, the minimal number of polyhedral pieces/halfspaces needed for error epsilon is Theta(log(1/epsilon)) exactly when the rotation has finite exponential approximation type. Infinite exponential type admits sublogarithmic subsequences. This applies both to fixed-cohort and truly dynamic optional-amplitude admission.
2. **A sharp masking threshold for optional fixed cohorts:** the maximal safe downward core can be exactly rectangular despite irrational rotation and dense kinks. Such rectangles occur for sufficiently small irrational angles for every r>1/2; they are impossible for every observable angle when r<=1/2. This threshold does not apply to dynamically changing optional amplitudes, whose exact admission remains nonpolyhedral for every irrational angle.

These are mathematical derivations, not an established novelty claim. The first proof combines elementary convex approximation, irrational-rotation recurrence, and a folding construction. The second combines convex vertex testing with a geometric-distribution calculation. Their potential scientific value is in the exact assumptions and conclusions, not a claim that support functions themselves are new.

## 1. Frozen model and three contracts

Let A=r R_theta, C=(1,0), 0<r<1, and x_0=0. The state is carried:

    x_{k+1}=A x_k+s_k b_k,       s_k in {-1,+1}.

Capacities are a=(a_1,a_2)>=0. Distinguish:

- **Fixed cohort:** b_k=a in every block.
- **Optional fixed cohort:** one b in [0,a] is chosen and held fixed forever; safety is required for every such b.
- **Dynamic optional amplitude:** b_k in [0,a] may be chosen anew in every block.

The common sign is essential. Independent per-port signs produce a different, simpler admission set.

Write

    u_k=(cos(k theta),-sin(k theta)),
    F(a)=sum_{k>=0} r^k |u_k dot a|,
    c_1=F(1,0),   c_2=F(0,1),   L(a)=c_1 a_1+c_2 a_2.

All series converge uniformly on bounded capacity sets, since their summands are bounded by r^k ||a||_2. Unless theta is an integer multiple of pi, c_2>0 and F is a norm on R^2. Indeed, its k=0 and k=1 summands already separate every nonzero vector.

### Proposition 1: exact robust support from zero state

Fixed-cohort admission is exactly

    A_fixed={a>=0:F(a)<=1}.

**Proof.** At time N,

    C x_N=sum_{j=0}^{N-1} r^j (u_j dot a) s_{N-1-j}.

The signs can be chosen independently, so the maximum absolute output is exactly F_N(a)=sum_{j<N}r^j|u_j dot a|. Thus every finite-time output is safe iff F_N(a)<=1 for every N, which is equivalent to F(a)<=1 by monotone convergence. If F(a)>1, a finite partial sum exceeds 1, giving a finite violating sequence. No state reset, stationary initial condition, or single sequence maximizing all horizons is needed. QED.

The convex hull of the reachable disturbance sum is a countable zonotope. This is the usual support-function/minimal-invariant-set calculation, not a new control principle.

## 2. Rational directions, dense kinks, and exact nonpolyhedrality

### Proposition 2: rational orbit

If theta/pi=p/q in lowest terms, q>=1, then

    F(a)=(1-r^q)^(-1) sum_{j=0}^{q-1} r^j |u_j dot a|.

This follows from u_{j+q}=(-1)^p u_j and a geometric series. For B=I on the positive quadrant, exactly floor((q-1)/2) distinct cancellation rays lie in its interior. Consequently F has exactly ceil(q/2) linear regions there, including the degenerate q=1 strip case. For q>=2 the corresponding non-axis boundary inequalities are all active. The exact count is specific to this B=I quadrant; a changed input matrix changes the cone geometry.

### Proposition 3: irrational kink noncancellation

Suppose theta/pi is irrational. Away from the origin, F is nondifferentiable exactly at the countable collection of lines u_j dot a=0. These lines are dense in projective direction. In the positive quadrant the interior cancellation rays are dense.

**Proof.** Two distinct u_j and u_k cannot be parallel: parallelism would imply (j-k)theta in pi Z. Fix a nonzero a on u_j dot a=0. All summands except j are differentiable there. Their gradient norms are at most r^k, so dominated convergence permits differentiation of their sum at a. Thus

    F(a+h)=F(a)+g dot h+r^j |u_j dot h|+o(||h||),

where g=sum_{k!=j}r^k sign(u_k dot a)u_k. Along any transverse v, the two one-sided derivatives differ by exactly 2r^j|u_j dot v|>0. The rest of the dense kink set cannot cancel this jump: its contribution has a derivative at this particular a. At a point on none of the lines, the same dominated-convergence argument differentiates the full series. Irrational-rotation density supplies the density statement. QED.

### Proposition 4: strict convexity of the unit ball

For irrational theta/pi, the norm F has a strictly convex unit ball. Consequently every nontrivial open interior-quadrant arc of F=1 is nonpolygonal, and A_fixed admits no exact finite-halfspace description.

**Proof.** If a and b are nonzero and not positive multiples, there is an open set of directions u for which u dot a and u dot b have opposite signs. Some u_k belongs to that set, by density. The scalar triangle inequality is then strict for that summand, while it is weak for every other summand. Therefore F(a+b)<F(a)+F(b). In particular, two distinct points on F=1 cannot have a boundary segment joining them. A finite polygon would have such segments on every nontrivial boundary arc. Alternatively, its gauge would be a finite maximum of linear forms, contradicting the dense genuine kinks. QED.

Here “strictly convex norm” means strict convexity of its unit ball; F itself is homogeneous and is not strictly convex along positive rays. The boundary has a countable dense set of corners and a unique supporting normal at the remaining interior-quadrant points. No smooth-curvature claim is intended.

## 3. Optional fixed cohorts: vertex testing and a sharp masking threshold

Define the robust downward core, not the downward hull,

    A_static_down={a>=0: [0,a] is a subset of A_fixed}.

### Theorem 5: three-vertex formula and rectangle/nonpolyhedron dichotomy

For c_1,c_2>0,

    A_static_down={a>=0: max(c_1 a_1,c_2 a_2,F(a))<=1}.

Let Q=F(1/c_1,1/c_2). Then A_static_down is exactly the axis-intercept rectangle

    R=[0,1/c_1] x [0,1/c_2]

iff Q<=1. If theta/pi is irrational and Q>1, A_static_down is nonpolyhedral.

**Proof.** A convex function reaches its maximum over a rectangle at a vertex: writing any b in [0,a] as a convex combination of the four vertices shows F(b) is no larger than their maximum. The four values are 0,c_1a_1,c_2a_2,F(a). The axis constraints force the robust core inside R. If the far corner of R is safe, convex vertex testing makes the whole rectangle safe. Conversely, equality with R makes that corner safe. If Q>1, the point (1/c_1,1/c_2)/Q lies on F=1 strictly inside R. A whole local boundary arc is therefore inherited from F=1, and Proposition 4 rules out a polyhedral robust core. QED.

### Theorem 6: r=1/2 is the exact existence threshold

(a) For every theta with sin(theta)!=0 and every 0<r<=1/2, Q>1. Thus irrational angles in this range never give an exactly rectangular static downward core.

(b) For every fixed 1/2<r<1 there is delta(r)>0 such that every 0<theta<delta(r), including irrational theta/pi, satisfies Q<1. Thus exactly rectangular static downward cores exist throughout this memory range.

**Proof of (a).** At the normalized corner put alpha_k=r^k cos(k theta)/c_1 and gamma_k=r^k sin(k theta)/c_2. Both sequences have l1 norm 1, alpha_0=1/c_1, and gamma_0=0. The reverse triangle inequality on their tails gives

    Q=sum |alpha_k-gamma_k|
      >=1/c_1 + |1-(1-1/c_1)|=2/c_1.

Since sin(theta)!=0, at least one |cos(k theta)|<1 and c_1<1/(1-r). Hence Q>2(1-r)>=1.

**Proof of (b).** As theta decreases to zero,

    c_1 -> 1/(1-r),
    c_2/theta -> r/(1-r)^2.

Dominated convergence applies to the latter because |sin(k theta)|/theta<=k. Applying it again to the normalized support gives

    Q -> L_r=sum_{k>=0}(1-r)r^k |1-k(1-r)/r|.

Let K have the geometric distribution P(K=k)=(1-r)r^k, with mean mu=r/(1-r), and let n=floor(mu). Memorylessness yields

    E[(K-mu)_+]=(n+1)r^(n+1),
    L_r=E|K-mu|/mu=2(n+1)(1-r)r^n.

At r=1/2 this equals 1. On each interval n/(n+1)<=r<(n+1)/(n+2), its derivative has the sign of n-(n+1)r, hence is negative in the interval interior. Adjacent formulas agree at the endpoints. Therefore L_r is strictly decreasing for r>1/2 and L_r<1. Continuity of Q at the above limiting normalization proves the claim. QED.

**An explicit fully analytical irrational-angle example.** Set r=9/10 and theta=1/100 radians. Then theta/pi is irrational. Let C_1=1/(1-r), C_2=r/(1-r)^2, and

    D_1=theta^2 r(1+r)/(2(1-r)^3),
    D_2=theta^2 r(1+4r+r^2)/(6(1-r)^4).

The inequalities 1-cos(x)<=x^2/2 and 0<=x-sin(x)<=x^3/6 for x>=0 bound the l1 distances between the normalized trigonometric sequences and their theta=0 limits. In particular, when D_i<C_i,

    Q <= L_r+2D_1/(C_1-D_1)+2D_2/(C_2-D_2).

Here L_r=387420489/500000000, D_1=171/2000, D_2=1623/2000, and the right side is exactly

    477668581548737879 / 589506255500000000 < 1

(approximately 0.810286). Thus the rectangle conclusion does not rely on a floating-point plot. The direct numerical Q is about 0.780421.

This r threshold uses B=I and C=(1,0); it is not asserted for arbitrary port geometry.

## 4. True dynamic optional amplitudes: hexagonal uncertainty and a clean identity

### Theorem 7: exact dynamic admission

If b_k may vary independently in [0,a] every block while retaining the common sign s_k, then robust sampled admission is exactly

    A_var={a>=0:H(a)<=1},

where

    H(a)=sum_{k>=0}r^k max{a_1|cos(k theta)|,
                           a_2|sin(k theta)|,
                           |a_1 cos(k theta)-a_2 sin(k theta)|}
        = [F(a)+c_1a_1+c_2a_2]/2.

**Proof.** The one-block uncertainty set is [0,a] union -[0,a]. Its convex hull is the hexagon with vertices plus/minus a_1e_1, plus/minus a_2e_2, and plus/minus a. Linear output maximization may be performed over this convex hull without changing the maximum. At every lag, block amplitude and sign can be selected independently, giving the sum of the displayed maxima. Finally, for any real p,q,

    max{|p|,|q|,|p+q|}=(|p|+|q|+|p+q|)/2.

Take p=a_1 cos(k theta), q=-a_2 sin(k theta), and sum. The finite-time/limit argument is identical to Proposition 1. QED.

Consequences:

- H is coordinatewise nondecreasing, since increasing a expands every block uncertainty box. Thus A_var is genuinely downward closed.
- It has the same axis intercepts as A_fixed.
- For irrational theta/pi, H has exactly the same interior kink rays as F, with half the derivative-jump size. Its positive-quadrant unit boundary has no line segments, because adding a linear function to F/2 preserves strict triangle inequality on nonparallel positive vectors.
- At the normalized far corner, H(1/c_1,1/c_2)=1+Q/2>1. Hence dynamic optional-amplitude admission is never the full axis rectangle.
- The exact inclusions are A_independent_signs subset A_var subset A_static_down subset A_fixed, where A_independent_signs={a>=0:L(a)<=1}. Independent per-port signs eliminate the shared-mode cancellation and give one non-axis halfspace.

The hexagon support identity is elementary zonotope geometry; the scientifically interesting issue is that the workload contract selects which exact domain applies.

## 5. Precise approximation metric and counting convention

Fix J=[l,u] with 0<l<u<infinity. Use either f(t)=F(1,t) or h(t)=H(1,t). Let N_J(epsilon) be the minimum number of affine pieces of a continuous piecewise-affine function g on J with uniform error at most epsilon. Allowing nonconvex g only strengthens the lower bound. The upper constructions below are convex and are actual gauges of inner admission polyhedra.

For the halfspace version, require an origin-containing convex admission polyhedron P with finite strictly positive radial extent on every ray in J. With m non-axis inequalities it has a gauge on J of the form

    g_P(t)=max_{1<=j<=m}(v_{j1}+v_{j2}t),

after normalizing each positive right-hand side to 1. Such an upper envelope has at most m affine pieces. An inequality with zero right-hand side is either irrelevant on the entire slope interval or excludes a positive ray and cannot approximate the strictly positive target radii. Therefore the piece lower bound also bounds halfspace count.

The target slope-radial function is lambda(t)=1/f(t) (or 1/h(t)): the boundary point on the ray (1,t) is lambda(t)(1,t). Both target gauges lie between 1 and M_J=sqrt(1+u^2)/(1-r). If |g-f|<=epsilon<1/2, reciprocal conversion bounds slope-radial error by 2epsilon. Conversely, radial error at most epsilon<=1/(2M_J) implies gauge error at most 2M_J^2 epsilon. Multiplication by ||(1,t)|| changes this to usual Euclidean radial distance with another fixed factor. Thus all these local metrics have the same asymptotic count. The radial statement counts polygon gauges g and their reciprocal radial functions 1/g; it does not count ordinary piecewise-affine interpolation of the target radial function 1/f.

This is a local uniform approximation theorem on a nontrivial slope interval, not an assertion about a single operating point, data-dependent finite test sets, or all possible nonlinear certificates.

## 6. Logarithmic upper bounds with safe polyhedra

Let tau_N=r^N/(1-r). For a>=0,

    F_N(a)<=F(a)<=F_N(a)+tau_N(a_1+a_2).

The upper bound is a convex piecewise-linear homogeneous gauge with at most N+1 regions on the positive quadrant. It therefore provides a safe inner polyhedron using at most N+1 non-axis inequalities. On J its error is at most tau_N(1+u). Choosing

    N>= log((1+u)/((1-r)epsilon))/log(1/r)

gives O(log(1/epsilon)) pieces and certified inner admission.

The same statement holds for H: use its first N hexagonal-support terms and the identical tail bound. Each term is linear on the positive quadrant except possibly for one kink, so there are at most N+1 regions. In dimension two one must not confuse a naive 2^N sign enumeration with the actual O(N) number of angular regions.

## 7. A quantitative kink-obstruction lemma

Choose an inner interval J_0=[l_0,u_0] strictly inside J and set eta=min(l_0-l,u-u_0)>0. Its projective angular measure is

    rho=(arccot(l_0)-arccot(u_0))/pi >0.

For irrational alpha=theta/pi, equidistribution implies that the number of indices 1<=k<=K with t_k=cot(k theta) in J_0 is at least rho K/2 for every sufficiently large K.

Suppose these kink locations have pairwise separation at least d_K. Set

    delta_K=min(eta/2,d_K/3).

The intervals [t_k-delta_K,t_k+delta_K] are disjoint and contained in J. On J_0 the absolute-value weight of the k-th kink of f is

    w_k=r^k |sin(k theta)|>=r^K/sqrt(1+u_0^2).

For h it is half this weight. Let zeta=1 for f and zeta=1/2 for h.

### Lemma 8: missing one kink costs a fixed amount

If g is affine on one of these intervals and ||g-f||_infinity<=epsilon, then

    epsilon >= zeta r^K delta_K / (2 sqrt(1+u_0^2)).

**Proof.** Convexity makes every summand's centered second difference nonnegative. The chosen kink alone contributes 2 zeta w_k delta_K. An affine g has zero centered second difference, while three pointwise approximation errors bound the target second difference by 4epsilon. Rearrangement proves the result. This argument is unaffected by arbitrarily many smaller kinks in the same interval. QED.

If g has m pieces, it has at most m-1 breakpoints. Take K=ceil(4m/rho), sufficiently large that equidistribution applies. There are at least 2m disjoint kink intervals, so one contains no breakpoint of g. Lemma 8 then applies.

## 8. Sharp arithmetic classification of approximation order

Define

    beta(alpha)=limsup_{q->infinity} [log(1/||q alpha||_Z)]/q.

The distance is to the nearest integer. This beta is not the usual polynomial irrationality exponent.

### Theorem 9: finite exponential type gives Theta(log(1/epsilon))

For fixed irrational alpha, fixed 0<r<1, and fixed nontrivial J in the positive interior, if beta(alpha)<infinity then

    N_J(epsilon)=Theta(log(1/epsilon)) as epsilon decreases to zero.

The same order holds for minimal non-axis halfspace count, for either fixed-cohort or dynamically optional-amplitude admission, under the gauge or local radial metric. It also holds if approximations are required to be safe inner polyhedra.

**Proof.** Choose B>beta(alpha), B>0. By the limsup definition, there is c>0 such that

    ||q alpha||_Z>=c exp(-Bq) for every integer q>=1.

For any distinct k,j<=K whose kink angles lie in the same positive-quadrant angular interval, their angular separation is at least pi c exp(-BK). The derivative of cotangent has absolute value at least 1, so their slope separation also satisfies

    d_K>=pi c exp(-BK).

Consequently delta_K>=c_0 exp(-BK), where c_0=min(eta/2,pi c/3)>0. Apply Lemma 8 with K=ceil(4m/rho). It gives constants C_0,C_1>0, independent of m, such that every m-piece approximation satisfies

    epsilon>=C_0 exp(-C_1 m).

Hence m>=C_1^(-1)log(C_0/epsilon), establishing the logarithmic lower bound. Section 6 gives the upper bound with safe convex approximants. Section 5 transfers the statement to halfspaces and radial error. QED.

Badly approximable angles and any finite polynomial Diophantine type are sufficient but unnecessarily restrictive. They have beta=0. The proof needs no quantitative equidistribution rate: for fixed theta, the eventual count threshold merely changes the accuracy threshold at which the asymptotic theorem applies.

### Lemma 10: near-return folding

For any integer q>=1 let Delta_q=dist(q theta,pi Z), and define

    G_q(a)=(1-r^q)^(-1) sum_{j=0}^{q-1}r^j |u_j dot a|.

Then

    |F(a)-G_q(a)|
      <= ||a||_2 Delta_q r^q / ((1-r)(1-r^q)).

**Proof.** Write k=j+lq. Rotation by q theta equals a sign times rotation by an angle of absolute value Delta_q. After taking the absolute projection, sign disappears. The unit-direction discrepancy after l returns is at most l Delta_q. Therefore the error is bounded by

    ||a|| Delta_q [sum_{j<q}r^j] [sum_{l>=0}l r^(lq)]
      =||a|| Delta_q r^q/((1-r)(1-r^q)).

The inequality remains valid even when l Delta_q is large; it is an upper bound, not a local expansion. QED.

The same bound holds for H when G_q is replaced by the q-folded sum of its hexagon-support terms. Indeed, the support of [0,a] union -[0,a] is Lipschitz in the unit output direction with constant max_{b in [0,a]}||b||=||a||.

For certified safety add tau_q^fold(a_1+a_2) to the folded gauge, with

    tau_q^fold=Delta_q r^q/((1-r)(1-r^q)).

The resulting upper gauge dominates the exact one and has at most q+1 linear regions. Its error on J is at most 2(1+u)tau_q^fold. Folding uses the true first-q directions, not rounded rational directions.

### Theorem 11: infinite exponential type gives sublogarithmic subsequences

If beta(alpha)=infinity, there is a sequence epsilon_j decreasing to zero such that

    N_J(epsilon_j)/log(1/epsilon_j) -> 0.

This is achievable by certified inner polyhedra for either workload contract. Thus the Theta(log(1/epsilon)) characterization in Theorem 9 holds **if and only if** beta(alpha)<infinity.

**Proof.** Choose q_j increasing with log(1/||q_j alpha||_Z)/q_j tending to infinity. Lemma 10 and its safety correction give approximants with at most q_j+1 pieces and error

    epsilon_j=2(1+u) pi ||q_j alpha||_Z r^(q_j)
                  /((1-r)(1-r^(q_j))).

After passing to a subsequence these errors decrease to zero. Their negative logarithms divided by q_j tend to infinity, whereas piece count divided by q_j remains bounded. The ratio therefore tends to zero. No lower bound of order log(1/epsilon) can hold at all sufficiently small accuracies. QED.

This result does not claim that the ratio tends to zero at every accuracy when beta is infinite. Nor does it assert a sharp leading constant when beta is finite.

## 9. Bounded zero-area physical templates realizing B=I

The sampled model can be realized without impulsive forcing, a workload-side battery, or a state reset. This is a realization theorem for the stated linear plant, not evidence that any particular production power system has these modal parameters.

Fix a block duration T>0 and set

    A_c=-lambda I+omega J,    lambda=-log(r)/T>0,
    omega=theta/T,            J=[[0,-1],[1,0]].

Then exp(A_c T)=r R_theta. Let each scalar load port have a nonzero input direction g_i in R^2. Consider deviation dynamics

    xdot=A_c x+sum_i g_i (p_i-P_0i).

Define on [0,T]

    h_i(t)=exp(A_c(T-t))g_i,
    hbar_i=T^(-1)integral_0^T h_i(t)dt,
    W_i=integral_0^T (h_i(t)-hbar_i)(h_i(t)-hbar_i)^T dt.

### Proposition 12: exact zero-area column assignment

If omega!=0, W_i is positive definite. For any desired sampled input column v_i, the fixed scalar template

    q_i(t)=(h_i(t)-hbar_i)^T W_i^(-1) v_i

is continuous, bounded, exactly zero-area, and satisfies

    integral_0^T q_i(t)dt=0,
    integral_0^T exp(A_c(T-t))g_i q_i(t)dt=v_i.

**Proof.** If z^T W_i z=0, continuity gives z^T h_i(t)=constant. Differentiating gives z^T A_c exp(A_c(T-t))g_i=0 for every t, up to an immaterial sign. Differentiating once more shows z is orthogonal to A_c g_i and A_c^2 g_i (after evaluating at t=T). These vectors are linearly independent: A_c is invertible, and g_i,A_c g_i have determinant omega ||g_i||^2, up to orientation. Hence z=0. The zero-area identity follows from centering. For the input-column identity, write h_i=(h_i-hbar_i)+hbar_i; the centered cross integral equals W_i and the mean term integrates to zero. QED.

Choose v_1=e_1 and v_2=e_2. On block k use

    p_i(kT+t)=P_0i+b_{ik}s_k q_i(t),   0<=t<T.

The sampled update is exactly x_{k+1}=A x_k+s_k b_k. To ensure physical nonnegative bounded power for capacities in 0<=a_i<=A_i, choose P_0i>=A_i ||q_i||_infinity and a nameplate upper limit at least P_0i+A_i||q_i||_infinity. Each block consumes exactly P_0i T energy, for either sign and every optional amplitude. The same fixed templates work for every block and every sequence. Their zero incremental energy does not mean zero baseline work or zero endpoint state.

Identical completed work follows if the workload model explicitly has constant energy e_i per work unit and instantaneous processing rate p_i/e_i; every block then completes P_0i T/e_i units. If actual task power/performance is nonlinear, equal energy alone does not prove equal work. That would require a separate task-level realization/validation. There is no dedicated storage device in this construction, but the dynamic plant naturally carries its own modal state and physical stored energy.

Under this fixed-baseline construction, capacity a_i is a load-shape/modulation-amplitude budget around a fixed amount of work. It is not automatically an admitted task count or an increase in total throughput. Translating these amplitude budgets into those operational quantities requires an additional explicit workload model.

Conditioning is a practical limitation: W_i can be ill-conditioned for small rotation over a block. Exact B=I may then require large ||q_i|| and large baselines. The small-angle masking example is mathematically physicalizable but must not be sold as a low-cost practical design without those checks.

A bounded finite-phase realization also exists. The curve h_i has full affine span by the same positive-definiteness proof. Choose three distinct times with affinely independent h_i values and three sufficiently short disjoint intervals about them. The 3-by-3 matrix whose columns are (interval length, integral of h_i over that interval) is invertible, by continuity. Solve this matrix against (0,v_i) and use its three solution entries as constant template levels on those intervals, with q_i=0 elsewhere. This realizes exactly zero area and the exact desired sampled column using finitely many bounded power levels. It adds no impulsive input or reset; finite slew-rate restrictions would still require a separate realization check.

## 10. Continuous-time safety is a different theorem

Let D(t) have columns d_i(t)=integral_0^t exp(A_c(t-v))g_i q_i(v)dv. Within a block,

    x(kT+t)=exp(A_c t)x_k+s_k D(t)b_k.

For fixed cohort a, the exact supremum of the absolute output at phase t over all histories and all block counts is

    F_t(a)=|C D(t)a|
           +sum_{j>=0}|C exp(A_c t) A^j a|.

Continuous-time robust safety is exactly sup_{0<=t<=T}F_t(a)<=1. At t=0 and t=T this reduces to F(a), but intermediate phases can add stricter constraints. For dynamic optional amplitudes, replace every absolute linear projection in this expression by max_{b in [0,a]}|row dot b|, separately for the present block and every past lag. The same hexagon identity applies term by term, but the phase supremum can change the approximation problem.

Therefore the arithmetic results above are carefully labeled sampled-state admission theorems. The physical realization proves exact block dynamics and balanced work, not the disappearance of intersample constraints.

## 11. Scope, limitations, and source anchors

- Neither basic support summation nor rational/irrational polygon behavior should be marketed as novel in view of Duda's explicit formula.
- The arithmetic result is about convex polyhedral representation accuracy, not an impossibility theorem for IQCs, semialgebraic certificates, or arbitrary algorithms.
- Its constants are nonuniform as r approaches 1, as the slope interval shrinks, or as the angle approaches rational resonances. No claim is made that deciding beta from finite data is computationally feasible.
- Static-cohort optional adoption and dynamic optional amplitude are different uncertainty models. Only the latter allows a new amplitude every block.
- Independent per-port signs destroy the geometric coupling that motivates this example.
- B=I is obtained with fixed zero-area templates, but realizability under application-specific peak, ramp, minimum-task, or nonlinear performance limits remains to be checked.
- All safety statements assume x_0=0 deviation from the modeled baseline. Nonzero uncertain initial state adds a separate transient support term.
- The threshold and arithmetic proofs are potentially useful narrow additions, but their novelty status must be decided by targeted comparison, not absence-of-hit language.

Primary source anchors inspected during this derivation:

1. Jarek Duda, *Analysis of the convex hull of the attractor of an IFS*, arXiv:0710.3863v2 (2008), especially Section 3 and equations (14)–(15): https://arxiv.org/abs/0710.3863v2 and https://arxiv.org/pdf/0710.3863v2
2. S. V. Rakovic, E. C. Kerrigan, K. I. Kouramas, D. Q. Mayne, *Invariant approximations of the minimal robust positively invariant set*, IEEE TAC 50(3), 406–410 (2005), DOI 10.1109/TAC.2005.843854; author-institution record: https://www.imperial.ac.uk/electrical-engineering/research/control-and-power/publications/?id=36410&noscript=noscript&respub-t4-action=citation.html
3. *Remarks on random countable stable zonotopes*, Statistics & Probability Letters, publisher page (countable Minkowski sums and their boundary geometry): https://www.sciencedirect.com/science/article/abs/pii/S0167715219301798
4. *Optimal Approximation of Zonoids and Uniform Approximation by Shallow Neural Networks*, Constructive Approximation (2025), DOI 10.1007/s00365-025-09712-9: https://link.springer.com/article/10.1007/s00365-025-09712-9

Sources 2–4 establish surrounding classical frameworks; the narrow arithmetic and r-threshold statements above are independently proved here and are not attributed to those papers without a matching theorem.
