# Fixed-site grid-service decision certificate

This addendum separates a declared grid-service decision from source or workload identification. It proves that identical complete PCC prehistories can leave opposite service-feasibility answers, and gives a causally available guarded SOC bit that safely resolves acceptance. The primary witness has positive converter losses, smooth positive continuing compute, a finite first-order PCS, finite power/command/slew limits, fixed completion, and exact recovery. The earlier step example is retained separately as an ideal-actuation comparison.

No physical service was dispatched. These are synthetic, explicitly declared model certificates. The conservation and robust-state estimation arguments are classical; no superiority over a same-information robust baseline is asserted.

## 1. Physical contract and smooth task profile

Time is in seconds. Stored energy has capacity B=18 and starts at E0=9. Let η_c=η_d=η=19/20. Let b be realized battery AC discharge power, so positive b serves the load and negative b charges. The physical equations are

  P=d-b,
  e_dot=-b/η for b>=0, and e_dot=-η b for b<0,
  τ b_dot=u-b, τ=0.01.

Realized power and command satisfy |b|<=12, |u|<=12. Realized slew satisfies |b_dot|<=100. The recovery PCC cap is P<=18 and the deadline is t=6. Initial realized power is b(0)=0.

A smooth nonnegative pulse h on [0,1] has ramp fraction r=1/5:

  h(s)=sin²(πs/(2r))/(1-r),                  0<=s<r,
  h(s)=1/(1-r),                            r<=s<=1-r,
  h(s)=sin²(π(1-s)/(2r))/(1-r),             1-r<s<=1.

Outside the slot h is zero. It is continuously differentiable, h and h' vanish at the endpoints, integral h=1, max h=5/4, and max |h'|=π/[2r(1-r)].

Six positive tasks run in six consecutive one-second slots. Five have constant power6. One has power6+12h during its slot, with energy18 and peak21. The diamond dependency A->{B,H}->D->E->F permits the two orders A,H,B,D,E,F and A,B,H,D,E,F. Both complete the same first three tasks by t=3 and have exactly the same future tasks D,E,F at constant power6. Total task energy is48; compute never pauses or drops below6.

The two worlds differ only in whether the high task occupies slot2 or slot3. The public PCC prefix is identical throughout [0,3]:

  P_pre(t)=6+4h(t-1)+(19/2)h(t-2).

The battery follows b=d-P_pre with feedforward u=b+τb_dot. This is causal when the current task selection and its prescribed profile/phase are known locally before its ramp. It needs no future hidden task order. Both worlds have b(3)=0 and u(3)=0.

## 2. Exact prefix states and ordinary continuation feasibility

Call the high-in-slot2 world L and the high-in-slot3 world H. Direct energy integration gives

  e_L(3)=9-8/η+η(19/2)=7299/760≈9.6039473684,
  e_H(3)=9+4η-(5/2)/η=966/95≈10.1684210526.

Both PCC histories and completed work are identical. The prefix minimum energy is11/19>0 and maximum across the worlds is64/5<18.

The ambiguity is not caused by an already-invalid future. Without accepting a new service, both worlds can complete the remaining work and recover to9. For example, on [3,6] use the small discharge pulse b=A h((t-3)/3), with

  A_L=153/800, A_H=37/100.

Each consumes exactly its excess stored energy above9, starts/ends with b=0, remains far inside power/slew limits, and keeps all future compute at6.

## 3. Prespecified service and an all-control impossibility proof

The service contract is fixed before observing the SOC bit. On [3,5] it requires

  P(t)<=P_req(t)=6-(4693/1000)h((t-3)/2).

This is an import-curtailment service, not literal zero import. Its target is nonnegative: min P_req=0.13375. The future workload is fixed at d=6 throughout the service and recovery; load shedding, deferral, or a different completion time is not permitted.

Since b=6-P, every admissible controller honoring the service has

  b(t)>=(4693/1000)h((t-3)/2)>=0.

Charging is forbidden by the service cap itself. The stored-energy expenditure is therefore at least

  E_req=(1/η) integral_3^5 (4693/1000)h((t-3)/2) dt
       =247/25=9.88.                         (1)

This inequality applies to every measurable causal or noncausal control satisfying the declared physical and service constraints, not just a selected controller. Extra discharge/export only increases energy expenditure. No controller can avoid it through a different charge/discharge schedule while maintaining P<=P_req and the mandatory load.

World L starts with less energy than (1):

  E_req-e_L(3)=1049/3800≈0.2760526316>0.

Thus it cannot honor the full service: integrating e_dot<=-b_req/η would require negative terminal energy. Power or slew refinements cannot repair this energy violation. The no-service continuation above remains feasible.

World H has positive reserve after the same service:

  e_H(5)=e_H(3)-E_req=137/475≈0.2884210526.

The equality target b=b_req is feasible with the finite PCS by setting u=b_req+τb_req_dot. On [5,6], recharge using

  b(t)=-(16552/1805)h(t-5).

Its AC charge energy is16552/1805 and its stored-energy gain is9-137/475, so e(6)=9 exactly. Both service and recovery start/end with b=b_dot=0; there is no instantaneous power jump at t=3 or5.

## 4. Continuous command, power, and slew certificates

For a signed pulse b(t)=±A h((t-t0)/T), feedforward u=b+τb_dot has the exact absolute peak

  U_max(A,T)=A[1+sqrt(1+(πτ/(rT))²)]/[2(1-r)]. (2)

Its realized power peak is A/(1-r), and realized slew peak is

  S_max(A,T)=Aπ/[2r(1-r)T].                  (3)

To prove (2), on the rising ramp write θ=πs/r. The command is proportional to 1-cosθ+c sinθ, c=πτ/(rT), whose maximum is1+sqrt(1+c²). The descending-ramp negative overshoot has smaller magnitude; the plateau is also smaller. Sign reversal does not change absolute peaks. Thus these are continuous-time bounds, not maxima on a sampled plot.

Apply them to prefix amplitudes8,19/2,4,5/2; service amplitude4693/1000 with T=2; and recovery amplitude16552/1805 with T=1. The overall command maximum is below12, realized slew below100, realized power below12, and recovery PCC below18. Stored energy decreases monotonically during the accepted service and increases monotonically to9 during recovery, so its minimum is137/475 and it never approaches capacity18.

This is a different waveform/service contract from the ideal step example. Its numbers are established independently and do not inherit a step-model capacity claim.

## 5. A causal guarded one-bit acceptance certificate

The SOC query has nominal sample time2.995, sample-time uncertainty at most0.001, and guaranteed delivery by2.999. The sample therefore occurs in [2.994,2.996] and arrives before the fixed service starts at3. The public PCC prefix remains prescribed until3; sensing does not permit extra precharging.

Suppose the energy measurement error is at most ε_E=0.02. A valid prefix state-slope bound in both worlds is

  M=361/32=11.28125.

The oldest admissible sample is0.006 seconds before the commitment, so its measurement m satisfies

  |m-e(3)|<=δ_E=1/50+(361/32)(3/500)
              =1403/16000=0.0876875.         (4)

The local sensor returns the single bit

  accept=1 iff m>=E_req+δ_E
                    =159483/16000=9.9676875. (5)

If the bit is1, (4) proves e(3)>=E_req. This is a safe acceptance certificate for continuous SOC uncertainty; it does not rely on restricting energy to the two example values. Bit0 means “abstain / not certified” in general. It is not a generic proof of infeasibility.

In the two declared worlds, the high world always returns1 because its worst-case measurement clears the threshold by

  e_H(3)-E_req-2δ_E≈0.1130460526>0.

The low world always returns0 because even its largest possible measurement stays below (5). Its physical infeasibility follows separately from the exact energy deficit, not from interpreting every zero bit as rejection.

The before-commitment delivery guarantee is essential. A timestamp-error bound by itself is not a latency guarantee. Equations (4)-(5) use the latest causal amendment, not the superseded noisier/older query.

## 6. Sufficiency for every accepted continuous SOC state

Besides SOC, the certified operating contract includes b(3)=0, the known future load6, the plant parameters/limits, and the deadline. For every e(3) in [E_req,18], use the same service pulse. Its ending state is

  e_5=e(3)-E_req in [0,8.12].

Then choose the recovery pulse amplitude causally from the current local state:

  A_rec=(9-e_5)/η.

It is nonnegative and at most9/η=180/19. Thus the worst recovery satisfies

  max |b|<=225/19≈11.8421053<12,
  max P<=6+225/19≈17.8421053<18,
  max |u|=U_max(180/19,1)<12,
  max |b_dot|=S_max(180/19,1)<100.

The service state stays nonnegative, recovery is monotone toward9, and the full path remains within capacity18. This proves that the guarded bit certifies the entire service-plus-recovery decision, not merely its energy component.

Exact recovery amplitude selection uses the local controller's current SOC or equivalent exact model state in this declared deterministic plant. The external one-bit report may be stale/noisy without removing that local control information. If local state knowledge is also uncertain, exact recovery needs its own robust target interval or feedback contract; it must not be silently assumed from the bit alone.

## 7. What the information comparison establishes

The two complete PCC prehistories are identical pointwise, at the same known site, with the same physical parameter contract, initial states, elapsed time, completed work, future tasks, and service request. Any noiseless, arbitrarily high-bandwidth observer receiving only that PCC prefix must give the same answer in the two worlds. Since the physical service-feasibility answers differ, such an observer cannot both safely accept H and correctly exclude L in every case. A robust same-information baseline must abstain from guaranteeing the service.

Adding the guarded SOC bit supports safe acceptance in H and abstention in L. A correct conventional robust baseline receiving the same additional bit obtains the same result. This is an information-sufficiency and matched-decision certificate, not an estimator-accuracy, algorithmic-superiority, sensor-cost, source-localization, or AI-cause claim.

## 8. Separate ideal-actuation zero-import witness

For reference only, use constant step tasks6/18 and common PCC prefix [6,10,18]. The high-in-slot2 world reaches1138/95; high-in-slot3 reaches64/5. Both complete the same three tasks and have identical future constant load6.

A prespecified P<=0 service lasting49/25=1.96 seconds from t=3 requires at least1176/95 stored energy. The low world has an exact deficit2/5; the high world retains8/19. Charging for the remaining26/25 seconds at AC power40750/4693 restores9, with recovery PCC6+40750/4693<18.

This proves the all-control ideal energy distinction. It does not have a valid direct finite-PCS transfer: the high world's realized b is0 before t=3 while literal zero import immediately requires b=6. Any finite slew or finite first-order command bound prevents that instantaneous jump. The smooth service above resolves this separately by starting its curtailment pulse at zero with zero slope, rather than claiming the step witness already meets finite-actuation constraints.
