# G1 observation contracts: indistinguishability, sharp prefix opacity, and exact-sensor caveats

Date: 2026-10-04 UTC. These are analytical implications of an explicitly specified observation channel. They are not controller novelty claims.

## 1. A controller-independent shared-prefix lower-bound lemma

Consider a finite or compact family W of exogenous load worlds in the same LTI plant and with the same initial plant state. Give the controller identical initial side information in all worlds in W. Write the scalar measured output as

    y_w(t)=f_w(t)+K[u](t),

where f_w is the uncontrolled output and the control operator K is identical in every world. At timestamp s_j the measured packet is y_w(s_j)+n_{w,j}, with |n_{w,j}|<=eta, delivered at a known common time d_j>=s_j. Observations may instead be continuous with a common delay.

Assume that at every timestamp whose packet is delivered before T,

    sup_w f_w(s_j)-inf_w f_w(s_j) <= 2*eta.                 (1)

Then for every deterministic causal output-feedback controller there is an admissible family of noise sequences for which all worlds in W have exactly the same observation/control history on [0,T). The same statement holds for pathwise robust randomized controllers after fixing a common random seed.

Proof. Choose m_j=(sup_w f_w(s_j)+inf_w f_w(s_j))/2 and n_{w,j}=m_j-f_w(s_j). These noises are bounded by eta and depend only on the exogenous worlds, not on the controller. By induction over packet arrivals, identical past records give identical control prefixes. The common delivered record is m_j+K[u](s_j), since all controls up to that timestamp coincide. The induction closes. For continuous observations the same construction and causality/uniqueness close the argument. Controls cannot create information through this particular additive common channel because their effect is known and identical. QED.

### Resource consequence

An admissible controller must therefore supply one shared control prefix for W. Any optimization requiring that shared prefix, but giving the controller perfect world revelation and unrestricted world-specific recourse after T, is a relaxation of the original robust feedback problem. Its optimum is a lower bound for the required capacity. Dropping terminal recovery, keeping only finitely many worlds, or enforcing safety only at selected times weakens this lower bound but does not invalidate it. A common initial SOC must remain common across the worlds and across initial-information groups.

This is useful even if the optimization returns no strict separation: a failure to separate is evidence about the chosen lower relaxation, not a proof that feedback has no resource value.

### Nonanticipativity pitfalls

- Use packet delivery times to determine the shared control prefix; use sensor timestamps to evaluate (1)
- Initial stage, exact angle/state, SOC telemetry, event bits and other side information must also match, or be covered by their own noisy-channel intersections
- Overlapping observation intervals do not form equivalence classes. Pairwise overlap chains are insufficient; the whole chosen group needs a common intersection. In one scalar dimension this is exactly (1)
- For several outputs with independent componentwise noise bounds, impose the diameter test for every component. A pairwise Euclidean-distance test alone does not guarantee a common intersection for three or more noise balls
- A phase world may appear with more than one admissible noise realization in a scenario construction. That is legitimate for an all-noise robust lower bound, but those copies and their observation histories must be explicit
- Identical SOC and controller memories do not add information when the initial SOC and applied controls are identical
- An extra exact output generally destroys the construction unless its free responses coincide too

## 2. Sharp whole-family opacity from step-response geometry

Suppose the first load edge has unknown time r in (0,L], the initial level p0 is known, its jump is sigma*Delta_p with sigma in {-1,+1}, and no second edge can occur before the prefix horizon H<=L. Let G be the plant's scalar response to a unit step in load, with G(a)=0 for a<0 and G(0)=0. Then

    f_r(t)=p0*G(t)+sigma*Delta_p*G(t-r),   0<=t<=H.

At a fixed t, as r varies, the closure of the output range has diameter

    D(t)=Delta_p*[max_{0<=a<=t}G(a)-min_{0<=a<=t}G(a)].     (2)

The value 0 is already included at a=0. For continuously observed output through H, the smallest uniform bounded-noise radius permitting one identical record for the entire phase family is exactly

    eta_star = (Delta_p/2)*[max_{0<=a<=H}G(a)-min_{0<=a<=H}G(a)].  (3)

Sufficiency follows by the midpoint construction. Necessity follows from any pair of phases approaching the extreme free outputs at a timestamp where the range exceeds 2eta. Endpoints r=0 may be absent from the physical initial-stage group; the supremum/closure argument still makes every eta<eta_star impossible. Thus this is sharp for **whole-family simultaneous opacity**, not a claim about the exact resource-optimal sensor threshold.

With fixed observation delay delta, replace the observed timestamp horizon by max(H-delta,0). With discrete samples, take half the maximum D(s_j) over timestamps delivered before the control-prefix endpoint. Arbitrarily long unobserved initial intervals must be treated explicitly.

### G1 specialization

Here G=g=t exp(-t), Delta_p=1, H=L=5. The maximum of g is 1/e, attained at age 1, and its minimum including age 0 is zero. Therefore

    eta_star=1/(2e)=0.18393972058572117.

If the delivered timestamp range contains age 1 or any timestamp >=1 within the first-five-unit prefix, the same threshold applies. Every initial-high phase can share one record; every initial-low phase can share another. The two groups are allowed separate controls because initial P is granted, but must retain a common initial SOC/capacity.

Consequently any valid terminal-free, first-five-unit lower bound for initial-P-conditioned no-future-observation controls transfers to **all causal frequency-feedback policies under adversarial |noise|<=1/(2e)**. One may grant perfect noiseless phase information after the prefix. The older floating lower was approximately 0.442710930662431 at P=.5. The new outward interval certificate is 0.455615336483606744450103432347843489227562181116369545721325; see INDEPENDENT_INTERVAL_CERTIFICATE_AUDIT.md for its signs, continuous-control relaxation and scope. This consequence is not caused by an exact-recovery endpoint, since the lower drops that endpoint entirely.

The noise threshold is approximately 30.7% of the allowed .6 frequency limit. It is intentionally a large-error existence result, not a realistic PMU claim. No strict capacity lower follows for smaller eta merely because full-family opacity then fails. Subsets can still be indistinguishable, and controllers can still need more capacity than full-information ones.

### A valid strict observation separation, if a matched upper is supplied

If a power-sampled policy meets the same plant, actuation, noise-independent initial SOC and recovery contract with capacity strictly below the transferred lower, granting that power channel has strict resource value under this coarse frequency channel. The power controller can ignore the coarse frequency channel. Its load measurement must have a separately stated noise and delay contract (e.g. two-level decoding needs absolute noise strictly below 1/2). This is a precision/telemetry contract theorem, not evidence that power telemetry beats a well-resolved ordinary frequency loop.

## 3. Exact sampled frequency recovers almost every first-edge phase

Assume the exact model, exact applied-control history, known initial load level p0, exact y samples at t_k=k*Delta, and 0<Delta<1. Samples arrive after the same fixed delay as the power samples to be compared. Let r in (0,5] be the first edge.

Subtract the known control convolution from a delivered y sample to obtain the exact uncontrolled response f_r(t_k). Before the first edge its value is p0*g(t_k). At the first sample strictly after the edge, the residual is

    f_r(t_k)-p0*g(t_k)=sigma*g(a), a=t_k-r in (0,Delta].

Since g'(a)=(1-a)exp(-a)>0 on [0,Delta], inversion uniquely recovers a and hence r. The known continuing periodic waveform is then known for all future times. Until that sample, all non-edge-crossing power samples just report p0. Thus **for first-edge phases not aligned with a sample timestamp**, exact sampled frequency can causally reproduce the sampled-P record and then provides strictly finer phase timing information than a mere stage bit.

### An all-phase exception that must not be deleted

If r=t_k exactly, y(t_k) is continuous and g(0)=0. The sample cannot distinguish edge-now from edge-later, whereas a right-continuous power sample sees the new level at t_k. The frequency sample one period later identifies r, but that is too late to emulate an arbitrary power-based action immediately after delivery of the aligned sample. For example, worlds r=t_k and r=t_k+epsilon have identical frequency histories through t_k yet different P(t_k).

Therefore an unqualified all-phase Blackwell/information dominance assertion is false. Valid formulations are:

- almost every phase, excluding sample-aligned edges
- all phases if the power sensor reports the left limit P(t_k-), since at an aligned edge it too reports the old level, and at the next sample frequency has identified the edge
- a separately proved all-phase resource equality/continuity result, which is not supplied by the inversion alone

The absence of a meaningful positive gap in a small-noise lower-bound search should not be overwritten by a claim that P telemetry must be essential.

## 4. What is genuinely added and what is classical

The indistinguishability construction is a basic set-membership/nonanticipativity argument. The exact-inversion calculation is elementary identifiability of a known step response. Neither is a new general information theorem. The task-specific useful statements are:

1. an explicit step-response-geometry opacity threshold that transfers a terminal-free storage lower to a genuine feedback class
2. an exact characterization of the phase-grid timing exception that prevents a careless all-phase information-dominance claim
3. together with INPUT_FREE_ROBUST_CBF_PROOF.md, a resource upper for a conventional electrical feedback loop under nonzero sample/noise/delay, with no load telemetry

These support a narrowly honest observation-quality/resource paper and substantially limit stronger telemetry-necessity or controller-novelty narratives.
