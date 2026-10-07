# G1: an input-free conventional barrier witness with sampled, delayed, noisy observations

Date: 2026-10-04 UTC. Independent round-3 derivation; frozen round-2 files are unchanged.

## Result

The model is x'=y, y'=p-2y-x-u, e'=-u, x(0)=y(0)=0. The unchanged continuing load alternates between 1 and 2 on plateaus of length 5, with arbitrary initial phase. The limit is |y|<=0.6, |u|<=0.5. All worlds use one initial SOC and capacity. At H=20 the SOC and the entire control-induced electrical state must return exactly to their initial values, after which u=0.

A **conventional robust barrier law with no load-power measurement and no phase estimate** meets this contract. The analytical expressions below give

- gain alpha=5, outer frequency bound h=0.6, barrier-expression estimation error budget M=0.003
- common initial SOC D=0.3904094856857374
- common capacity (1+gamma)D=0.3939910040190165, gamma=0.0091737482427927
- prefix power <=0.4889795645699768; recovery power <=0.3939910040190165
- all post-10 frequency magnitudes <=0.5240561077502858
- exact SOC and control-state reset at 20

Conservative printed resources may be e0=0.390410, E=0.393992, P=0.5; the excess initial SOC shifts every SOC upward but does not change the recovery calculation. The exact theorem uses the formulas, not finite printed digits.

Two sufficient observation contracts are:

1. State samples every 0.001, fixed delivery delay 0.0005, componentwise x/y errors <=0.0001
2. Frequency-only samples every 0.0002, fixed delivery delay 0.0002, frequency error <=0.00001; x is obtained by integrating the delivered samples with a finite-horizon error allowance

These are dimensionless model-time contracts. The predictor and barrier can evolve continuously between sensor arrivals. **This is not a zero-order-hold actuator theorem**, and it does not certify parameter error, unknown actual port power, battery losses, PCC observability, or physical sensor calibration. Its value is to remove ideal continuous/noiseless plant telemetry from a resource witness without inventing a new controller.

The common capacity is below the frozen terminal-free first-five-unit lower bound 0.442710930662431 for every initial-P-conditioned, no-subsequent-observation policy. The newly reviewed outward prefix lower improves this to E>=.45561533648360674445 (see INDEPENDENT_INTERVAL_CERTIFICATE_AUDIT.md). This preserves a strict information-resource separation under nonzero sampling/delay/noise. It does **not** establish a resource premium for power telemetry over ordinary frequency feedback.

## 1. A nominal input-free barrier family

Write g(t)=t exp(-t), F(t)=1-(1+t)exp(-t), and k(t)=(1-t)exp(-t). Set

    kappa_b(x,y) = [2-alpha*b-x+(alpha-2)*y]_+.

Here b is a design frequency bound. We will use alpha=5 and b in {0.5988, 0.6}. Initially disregard the power cap; the derived power bound proves that no saturation is needed.

### 1.1 Safety and positivity

On the upper face y=b, kappa_b >= 2-2b-x, hence y'<=0 for every p<=2. At the lower face y=-b, kappa_b=0 whenever x>=0, since 2-2(alpha-1)b<0. Since u>=0, the nonnegative angle kernel gives x<=2F(t)<=2. Consequently y'>=1+2b-2=2b-1>0 on the lower face.

During control activity,

    q=p-u=p-2+x+2b+(alpha-2)(b-y) >= x+2b-1.

During inactivity q=p>=1. The positive convolution kernel and continuation from zero therefore give x>=0, completing the joint positivity/safety argument. In particular 0<=q<=2. These statements are global for the uncapped nominal law.

### 1.2 Entry comparison without assuming an upward load edge

An important correction to a tempting shortcut: the input-free barrier can first activate shortly **after** an initial high-to-low edge. Its expression does not jump downward with p. Therefore the old proof restricted to sums of upward step responses is not sufficient here.

The following bounded-input rearrangement inequality handles all phases. For any measurable 0<=q<=2 and zero initial state, if 0<=y<=b<2/e, let a in [0,1) satisfy 2g(a)=y. Then

    x >= 2F(a).

Proof: extend q(t-r) by zero outside r in [0,t], put lambda=a/(1-a), and note

    g(r)-lambda*k(r)=exp(-r)*((1+lambda)r-lambda).

This expression is negative on [0,a) and nonnegative afterward. Its integral against 0<=q<=2 is therefore at least its integral against 2 on [0,a]. Hence x-lambda*y >= 2F(a)-lambda*2g(a), proving the claim. This is an elementary rearrangement/supporting-line argument, not a new optimal-control method.

Let f=F composed with the increasing-branch inverse of g. At first activity,

    x=2-alpha*b+(alpha-2)y,
    2-alpha*b+(alpha-2)y-2f(y/2) >= 0.

The expression on the left is strictly increasing on [0,b], since its derivative is alpha-2-a/(1-a)>0 for the present parameters. Its first root y_a is the constant-high onset value. Thus y_entry>=y_a, including low-plateau first entries.

Define t_a as the smaller positive root

    2[1+(alpha-1)t_a]exp(-t_a)=alpha*b,
    y_a=2g(t_a), d_a=b-y_a, K=(alpha-1)^2/alpha.

For an active high plateau with elapsed activity s and entry deficit d,

    y=b-d exp(-alpha*s),
    u_high(s)=K*d(1-exp(-alpha*s))-b*s.

Therefore d<=d_a. Let T_b be the positive zero of u_high for d=d_a, and s_peak=log(alpha*K*d_a/b)/alpha. Define

    U_b=K*d_a(1-exp(-alpha*s_peak))-b*s_peak,
    D_b=K*d_a[T_b-(1-exp(-alpha*T_b))/alpha]-b*T_b^2/2.

### 1.3 A downward edge cannot increase the episode beyond that envelope

During activity, a deficit 2-p contributes to u through

    J(r)=1/alpha-K exp(-alpha*r).

Let tau=log(alpha*K)/alpha=2log(alpha-1)/alpha. Then J<=0 for r<=tau. If the load is low from an activity entry, or drops to low during activity, the putative low-active continuation at elapsed tau from the start of the low portion satisfies

    u(tau) = 1-2b+2/alpha - x_at_low_start - (b-1/alpha)*tau < 0.

The strict inequality follows from x>=0 and the checked scalar parameter inequality. Thus the activity must end before tau in the low portion. Until it ends, its correction to the high-plateau envelope is nonpositive. It follows that the entire first episode is bounded pointwise by u_high(s;d_a), lasts at most T_b, and has peak <=U_b and discharge <=D_b.

### 1.4 There is no second episode

A pure low onset never activates: its maximum barrier expression equals

    1-alpha*b+(alpha-1)exp(-(alpha-2)/(alpha-1)) < 0.

After natural exit on a fixed plateau, the barrier expression has the form

    -C+exp(-v)(C+Bv), B<=C, C>0,

and is nonpositive thereafter. This proves no same-plateau reentry.

If a high-plateau episode ends naturally and a down edge occurs d>=0 later, put v=d+r and C=alpha*b. The barrier expression afterward is bounded above by

    1-C+exp(-v)(C+C*v)-exp(-r)(1+(alpha-1)*r)
    <= -(C-1)+exp(-r)((C-1)+(C-alpha+1)*r)
    <= -(C-1)+(C-1)(1+r)exp(-r) <= 0.

Thus a later down edge also cannot restart activity. A first low-plateau episode cannot restart before the next up edge by the same-plateau argument.

Before any activity x>=F(t). While the first episode is high, q>=2b>1, so x>=F(t) still holds. Therefore its entry, and any down edge during it, precede t_b solving F(t_b)=2-2b. Its support ends before t_b+tau<5. The next potentially activating up edge is at least time 5. Up to a hypothetical second episode the total discharge is <=D_b, hence

    x(t) >= F(t)-D_b/e.

For t>=5 this is strictly above 2-2b for the stated parameters. Since y<=b, the barrier expression is negative there. A second episode is impossible.

This establishes an all-phase, continuous-time nominal resource bound, not a finite phase enumeration. All scalar positivity conditions are recorded in theory_constants.json.

## 2. Robustification by cooperative comparison

Let the estimator's barrier-expression error obey

    |-xhat+(alpha-2)yhat - (-x+(alpha-2)y)| <= M

at every time before 10. Apply the ordinary robust barrier

    u=[2-alpha*h-xhat+(alpha-2)yhat+M]_+.

It can be written u=[2-alpha*h-x+(alpha-2)y+b(t)]_+ with 0<=b(t)<=2M. Let h0=h-2M/alpha. Then at every state

    kappa_h <= actual law <= kappa_h0.

The pointwise ordering alone is not enough to compare applied power or energy along different trajectories. The following comparison supplies that missing argument.

Set r=x+y. The closed-loop nominal vector field is

    x'=r-x,
    r'=p-r-[2-alpha*b-(alpha-1)x+(alpha-2)r]_+.

Its off-diagonal derivatives are nonnegative. Where the positive part has slope a in [0,1], its Jacobian is

    [[-1, 1], [(alpha-1)a, -1-(alpha-2)a]].

The row sums are 0 and a-1<=0, so it is nonexpansive in the infinity norm. Cooperative comparison gives

    (x_h0,r_h0) <= (x_actual,r_actual) <= (x_h,r_h).

Write d=2M. Comparing the two ideal trajectories, the forcing caused by changing h0 to h is between 0 and d and is supported only where the tighter ideal law is active. Section 1 bounds that support's duration by T_h0. The nonexpansive Jacobian therefore gives

    0 <= r_h-r_h0 <= d*T_h0,
    0 <= x_h-x_h0 <= d*T_h0.

Consequently

    u_actual <= U_h0 + (alpha-2)*d*T_h0.

For cumulative discharge Z(t)=integral_0^t u, the plant identity is

    Z(t)=integral_0^t p - r(t)-x(t)-integral_0^t x.

The componentwise comparison implies 0<=Z_actual(t)<=Z_h0(t)<=D_h0 for every t. This is the useful resource robustification lemma: there is no exponentially growing Gronwall penalty and no conversion of a phase grid into an all-phase statement.

For h=.6, alpha=5, M=.003, h0=.5988, the bound is P_prefix<=.488979565<.5. Positivity follows from p-u>=.5, and on y=-h the actual control is zero because 2-2(alpha-1)h+2M<0. On y=h the robust barrier gives y'<=0. Thus the actual trajectory satisfies both frequency faces.

The cumulative mass bound also gives x>=F(t)-D_h0/e. The inequality

    F(5)-D_h0/e > 2-2h+2M

implies that the actual law is identically zero at all times t>=5 (until the recovery module starts). This bounds its discharge support without requiring the noisy law itself to have only one episode.

## 3. Nonzero sample, delay, and noise contracts

At sample timestamp t_k, receive noisy x/y values. The packet arrives at t_k+delta. Between arrivals, propagate a state estimate from the latest timestamp using the known actual applied u and the ordinary midpoint model

    xhat'=yhat, yhat'=1.5-2yhat-xhat-u.

No power measurement is used. Before the first packet, propagate the known exact initial state in the same way. If a is the age of the newest available timestamp, a<=Delta+delta.

Let C=[-1,alpha-2]. With Phi(a)=exp(Aa),

    C Phi(a)=exp(-a)[-1-(alpha-1)a, (alpha-2)-(alpha-1)a].

For a<=(alpha-2)/(alpha-1), the disturbance kernel C Phi(r)[0,1]^T is nonnegative. The exact scalar error bound is

    M(a)<=exp(-a){[1+(alpha-1)a]epsilon_x
                  +[(alpha-2)-(alpha-1)a]epsilon_y}
          +(1/2){-F(a)+(alpha-2)g(a)}.

A simpler sufficient uniform budget is

    M >= [1+(alpha-1)a_max]epsilon_x
         +(alpha-2)epsilon_y +(alpha-2)a_max/2.

For Delta=.001, delta=.0005, epsilon_x=epsilon_y=.0001, this is .0026506<.003. The sampled errors may be arbitrary, adversarial, time-correlated and discontinuous. The bound does not assume zero mean or a noise distribution.

### Frequency-only realization with explicit integration bias

If only y is sampled, estimate x(t_k) with the left Riemann sum Delta*sum_{j<k}y_measured(t_j). Do not assert that noisy integration reconstructs x exactly.

Until time 10, |y'|<=2 when 0<=u<=.5. To see this, q=p-u lies in [.5,2], while w=x+2y has convolution kernel (2-t)exp(-t). Splitting its positive and negative parts yields 0<=w<=2(1+exp(-2)), hence -1.770671<q-w<=2. More exactly the lower derivative bound is .5-2(1+exp(-2)). Therefore

    |xhat(t_k)-x(t_k)| <= t_k*epsilon_y + t_k*Delta <= 10(epsilon_y+Delta).

With Delta=.0002, delta=.0002, epsilon_y=.00001 this gives epsilon_x=.0021 and the preceding barrier budget becomes .00273336<.003. A first-exit argument closes the apparent dependence on the power bound: prior to a first power-cap crossing this derivative estimate is valid, and the strict robust bound .48898 prevents the crossing. This uses the exact known initial state, exact model, timestamps, and actual applied-control history.

The high sampling rate and small noise bound are a conservative mathematical existence row, not measured device specifications. The state-sensor row is less demanding on the y channel but assumes an independent x observation.

## 4. Exact finite recovery survives the noisy sensor

At time 10 use only accumulated actual control: Z_10=integral u and c_10=[x_c,y_c], with c'=Ac+Bu, c(0)=0, B=[0,-1]^T. On intervals [10,11), [11,19), [19,20), apply constant coefficients

    a=C_recovery^{-1}[-Z_10; -Phi(10)c_10].

The matrix is exactly the same three-moment map as the frozen classical recovery proof. It needs no current plant or phase measurement and no SOC reset. It imposes total integral u=0 and c(20)=0 exactly.

For a unit discharge at s in [0,5], its three recovery coefficients are

    C_recovery^{-1}[-1; (20-s)exp(s-20); -(19-s)exp(s-20)].

Every coefficient has the form c0+exp(s)(c1+c2*s). Endpoints and at most one derivative root give their exact extrema. The cumulative discharge minimum per unit mass is -gamma, gamma=.0091737482427927. Hence e0=D_h0 and E=(1+gamma)D_h0 suffice for all sensor errors and phases. The final tiny nonzero terminal range in the JSON is floating matrix arithmetic only; the defining linear equations give exactly zero.

For t>=10, the uncontrolled continuing-load bound is 1/e+10exp(-10). The prefix mass contributes at most D_h0*4exp(-5), because it is supported before 5. The three rectangular recovery pulses contribute at most their absolute amplitudes divided by e. The resulting total .524056108 is below .6. After 20 the entire control-induced state is zero and no battery action is used.

## 5. What this changes in the paper

1. The strict common-SOC/resource witness can use ordinary electrical feedback with no P sensor. The frozen continuous x/y/p CBF was stronger in its stated sensing interface than necessary.
2. The new all-adversarial-noise witness strengthens robustness of the old no-feedback-versus-feedback separation. It does not make no-feedback a standard practical frequency-control baseline.
3. A claim that ongoing compute-phase/P telemetry is necessary, or generically saves storage compared with conventional frequency feedback, is unsupported. Matched-information ordinary controllers remain the appropriate baseline.
4. Robust CBFs, predictors, cooperative comparison, bounded-input rearrangement, and terminal moment matching are established tools. The possible paper increment is the explicit continuing-load/common-SOC/finite-recovery resource statement, with honest sensor contracts.
5. Numerical constants here are ordinary floating evaluations of analytical expressions. There is no outward-rounded arithmetic certification. Both the inherited lower decimal and the new upper decimal need that qualification.

## 6. Independent numerical falsification checks

check_nominal_witness.py tests both nominal bounds b=.5988 and b=.6 on 113 phases each, including very early down edges and sample-boundary limiting cases. All 226 runs satisfy the analytical peak-power, frequency, discharge, support-end and single-episode bounds within the declared numerical tolerance. These tests are a check against errors in the nominal proof, not its basis. The resource constants and all strictly positive scalar margins are independently recomputed by compute_theory_constants.py.
