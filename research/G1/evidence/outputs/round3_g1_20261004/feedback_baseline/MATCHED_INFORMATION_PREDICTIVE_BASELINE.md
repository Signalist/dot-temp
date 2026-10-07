# Matched-information mature feedback baseline for G1

## Main result

A conventional **set-membership observer plus scalar robust predictive safety projection**, followed by a fixed three-pulse terminal recovery, satisfies the continuing-load G1 contract with sampled, delayed, bounded-noise observations. No exact phase, angle, instantaneous frequency, or current power is supplied to the power-only controller. It needs no scenario-tree optimization or offline energy-optimal schedule.

| Sensor contract | Common e0 (unrounded) | Common E (unrounded) | Safe rounded (e0,E) |
|---|---:|---:|---:|
| Power, abs noise <= .1 | .350693495131612 | .353910424738462 | (.350694,.353911) |
| Frequency, abs noise <= .005 | .351326868206371 | .354549586918271 | (.351327,.354550) |
| Frequency, abs noise <= .01 | .353819184205240 | .357064765888287 | (.353820,.357066) |
| Frequency, abs noise <= .02 | .358563935315661 | .361853042434309 | (.358564,.361854) |
| Frequency, abs noise <= .05 | .369017405333602 | .372402407000157 | (.369018,.372404) |

For every row, the permitted P is .5; the actual worst command is at most .499999999000002. Independent continuous-phase/continuous-time reduction gives max abs(y) <= .599957499456683, below .6. SOC and both control-induced electrical states recover exactly at 20 by linear terminal equations; floating residual is at most 3.5e-18. The post-20 bound is .367879482394515 with u=0. A single common pair e0=.369018, E=.372404 also works for **all five sensor rows simultaneously**, if identical physical resources across sensor cases are desired.

Evidence level: finite analytic reduction over the full continuous phase family and continuous time, evaluated in ordinary double precision and independently checked by dense numerical replay. This is **not outward-rounded interval arithmetic**, nor a guarantee under plant-model error. The finite number of policy histories is a consequence of the sensor contract, not a finite replacement of the continuous phase family.

The result removes a weak-comparator objection: a mature predictive controller with the same sampled P interface is feasible below the round2 sampled-P tree E=.381890, even with .05 delay and bounded noise. More importantly, the delayed **frequency-only** observer is already sufficient at E=.372404 for eta_y=.05. Therefore this model does not support a broad claim that power telemetry is necessary, that ordinary frequency feedback cannot achieve the resource contract, or that the scenario tree is an algorithmic innovation. The original no-future-observation versus causal-feedback separation can still be valid; it is a different information-class comparison.

## 1. Common plant and information contract

Plant:

    x' = y
    y' = p - 2 y - x - u
    e' = -u
    x(0)=y(0)=0

The unchanged load alternates between 1 and 2 every five time units and continues after 20. Its initial class p0 in {1,2} is common side information. Its first future edge a belongs to [0,5], with endpoint closures used for conservative coverage. The actual class at a=0 can be defined by right continuity; including both limiting class descriptions only enlarges the validation family.

Samples have timestamps t_k=.1 k and arrive at d_k=t_k+.05. Noise is arbitrary and independently variable at every timestamp subject to its absolute bound. Applied controls, the exact plant, initial state, and exact clock/waveform family are known. There are no x or phase measurements. The first action is zero on [0,.05], so the power implementation can obtain its initial class from the delayed t=0 sample and does not actually need the earlier side-information delivery.

The controller acts at d_k for k=0,...,29, holds its action for .1, sets u=0 on [3.05,10], and applies the recovery controls on [10,11], [11,19], [19,20]. All future controls are zero. The cutoff and all numeric parameters are the same across the reported rows.

### Power observer

Threshold at 1.5 exactly classifies both levels despite abs(noise)<=.1. Before the first changed sample is delivered, the feasible first-edge interval at decision k is [.1k,5]. This interval deliberately allows the load to have switched between the sample timestamp and delivery, and also allows a switch during the next hold interval. It is not a zero-delay current-class oracle.

If the first changed sample is j, the interval becomes [(.1)(j-1),(.1)j], and remains there. There are two initial classes times 50 closed first-edge cells. The representative cell index is never revealed to the policy before its first distinguishing observation. Tests compare equal-history commands directly.

### Frequency observer

Let g(t)=t exp(-t) for t>=0 and zero otherwise. Let c_y(t) be the known control-induced y computed only from applied u. Put sigma=3-2p0, and correct each measured frequency by

    R_k = sigma [m_y(t_k) - c_y(t_k) - p0 g(t_k)].

Before the first edge this is bounded noise alone. Before the second edge, its noise-free signal is g(t_k-a). Trigger exactly once, on the first R_k>eta_y. Set tau to an upward-rounded bound on the increasing-branch root of g(tau)=2 eta_y, so g(tau)>=2 eta_y. All four rows have tau+.1<1:

    eta .005: tau=.0101015272
    eta .01:  tau=.0204124441
    eta .02:  tau=.0417034085
    eta .05:  tau=.1118325592

With no detection by sample k, the observer uses [max(0,.1k-tau),5]. First detection at sample j gives [max(0,.1(j-1)-tau), min(5,.1j)]. After detection, no later amplitude samples are used. This is an implementable detector with memory, not an exact inversion of noisy y.

**All-noise coverage proof.** Before a, R<=eta so false detection is impossible. The first sample strictly later than a+tau has age at most tau+.1<1, so g(age)>2 eta and detection must already have occurred by that sample for every admissible noise sequence. At the preceding nondetecting sample, any positive age is still on g's increasing branch; nondetection implies g(age)<=2 eta, hence age<=tau. Current detection implies a<=.1j, and the preceding sample implies a>=.1(j-1)-tau. The same argument gives the no-detection interval. Closed intervals cover equality cases. Detection occurs before the second edge. Thus enumerating all 102 or 104 detection histories and validating their overapproximating continuous intervals covers every bounded-noise realization, including adversarial ones.

## 2. Standard robust predictive projection

The nominal command is zero. At each delivery t, enumerate the admissible first-edge interval I from the observer. For a hypothetical candidate u held until t+h, h=.1, predict the original load for every a in I, apply a fixed maximum-discharge backup B=.5-1e-9 after t+h, and constrain the predicted output on s=0,.01,...,5:

    v(t+s,a;u) = y_free(t+s,a) + c_past(t+s)
                  - u [g(s)-g(s-h)] - B g(s-h)

    -.59995 <= v(t+s,a;u) <= .59995
    0 <= u <= B
    minimize u^2/2

The phase supremum and infimum are evaluated analytically, not by a phase grid. Each collocated inequality is affine in the scalar u, so the implementation intersects scalar intervals and projects zero. It reports infeasibility if the interval is empty; there is no silent clipping of an infeasible request. The 1e-9 converter margin avoids claiming a few floating ulps above .5 as feasible.

The predictive construction is conventional: an observer uncertainty set, a fixed backup trajectory, and a minimally invasive constrained projection. We do not assert that this particular finite-horizon/collocated implementation inherits a generic published theorem. In particular, its hypothetical maximum-discharge backup is **not** claimed to satisfy finite SOC forever. Actual finite-prefix energy feasibility and all-future safety are established separately by the saved complete-policy validation and exact recovery. SOC is fully accounted for in the certified common resource pair, rather than erased or reset.

Provenance of the mature method family:

- Wabersich and Zeilinger, *A predictive safety filter for learning-based control of constrained nonlinear dynamical systems*, Automatica 129 (2021), 109597, https://arxiv.org/abs/1812.05506 and https://doi.org/10.1016/j.automatica.2021.109597
- Chen, Jankovic, Santillo and Ames, *Backup Control Barrier Functions: Formulation and Comparative Study*, 2021, https://arxiv.org/abs/2104.11332
- Ames, Xu, Grizzle and Tabuada, *Control Barrier Function Based Quadratic Programs for Safety Critical Systems*, IEEE TAC 62(8), 2017, https://arxiv.org/abs/1609.06408

These establish method provenance. They are not represented as prior proofs of the precise G1 resource constants, or as code from which the implementation was copied. Only public primary records were used.

## 3. Independent continuous-phase and time validation

For a fixed delivered-observation history, all controls are fixed and independent of the still-unknown a. Write

    y_free(t,a) = p0 g(t) + sigma Q(t-a)
    Q(r) = sum_{j>=0} (-1)^j g(r-5j).

At a given time, extrema over a closed interval occur at its endpoints, at a moving kink t-a=5j, or at a stationary lag of Q. On the lag segment [5m,5(m+1)], define

    S0 = sum_{j=0}^m (-1)^j exp(5j)
    S1 = sum_{j=0}^m j (-1)^j exp(5j)
    Q(r) = exp(-r) (S0 r - 5 S1).

Its only possible stationary lag is r=1+5S1/S0. The validator explicitly includes all kink lags 0,5,10,15,20 as well as stationary roots. There is no assumption that the kink cannot be an extremum.

For endpoint phases, the frequency is a finite sum of terms c_i g(t-t_i). On any segment between its known events, with s measured from the segment's left endpoint l,

    y(l+s) = exp(-s) (Y + M s),
    Y = sum c_i (l-t_i) exp(-(l-t_i)),
    M = sum c_i exp(-(l-t_i)).

For a stationary or kink phase-lag candidate, add the constant sigma Q(r), and restrict t to [a_min+r,a_max+r]. On each segment, extrema occur at endpoints or s=1-Y/M when inside. This is a finite analytic candidate reduction for the full continuous-time/phase problem, not a simulation mesh. The independent file validate_continuous.py imports no controller code.

The synthesis time mesh .01 is therefore not promoted to a continuous-time proof. The actual saved policies are checked afterwards by this analytic reduction. All saved control timestamps and observer endpoints are canonicalized to ten decimal places. Frequency tau is rounded upward to ten decimals, with g(tau)>=2 eta checked at 60-digit precision. The independent validator additionally widens each phase interval by 1e-10 at both ends, clipped to [0,5], closing floating endpoint gaps. Pre-rounding artifacts are preserved in pre_endpoint_rounding/. The final worst peak is .599957499456683, slightly greater than the synthesis-grid threshold .59995, and safely less than .6.

## 4. Common SOC and exact recovery

Let z10 be accumulated discharge by time 10 and c10=(x_c,y_c) the state induced only by past u. Both are available from applied-control history alone. Let A=[[0,1],[-1,-2]], b=[0,-1]^T. For recovery intervals [a_j,b_j]=[10,11],[11,19],[19,20], form

    C[0,j] = b_j-a_j
    C[1:3,j] = exp(A(20-b_j)) A^-1 [exp(A(b_j-a_j))-I] b.

The recovery amplitudes are the three-by-three linear solve

    C r = [-z10; -exp(10A)c10].

This sets total discharge and both control-induced states to zero at 20. It uses no future phase/load information. SOC extrema occur at the boundaries of constant-control intervals. The reported common e0 is the maximum z over every history, and common E=e0-min z over every history. Thus the initial SOC is not chosen separately for each phase. The rounded capacity accounts for the upward rounding of e0 as well as E.

After 20 the controlled system exactly rejoins the uncontrolled continuing-load trajectory. For arbitrary measurable p in [1,2], the critical-damping kernel gives abs(y_free(t))<=1/e+t exp(-t) for t>=1. Hence abs(y)<=.367879482394515 at and after 20.

## 5. Failed straightforward sampled CBF baselines

As a diagnostic after the predictive design, we sampled the standard exponential CBF at the same delayed delivery times, reconstructing x and y from the midpoint of the current admissible phase interval and the known controls. Its nominal command is zero, and alpha is the previously considered 6 or 10. Requested commands beyond P are retained and flagged, never clipped and relabeled feasible.

| CBF gain | max abs(y) | max abs(u) | Failed frequency cells | Failed power cells |
|---|---:|---:|---:|---:|
| 6 | .603432487936205 | .490490581050074 | 14/100 | 0/100 |
| 10 | .615432315657671 | .550499546758029 | 15/100 | 49/100 |

These failures establish that the round2 ideal continuous CBF certificate cannot just be relabeled sampled/noisy. They do not establish a limitation of CBFs generally. The predictive/set-membership baseline supplies the stronger mature comparator instead.

### Frozen same-method no-feedback ablation

A final, untuned ablation retains exactly the same scalar projection, sampling/control times, tightening, backup, cutoff and recovery, but fixes the uncertainty interval to [0,5] forever. It receives only p0, so its two command sequences are open-loop conditional on the common initial class. The two groups share one e0 and E.

It succeeds with common e0=.468264002370365, E=.472559239418614, max abs(y)=.599953543128020, max abs(u)=.499999999000001, and terminal residual below 7.1e-20. A six-decimal conservative pair is (.468265,.472561). This is **not** a new best blind upper: it is looser than the previously available .4606265 upper. It is retained without tuning because it isolates the information change in the same mature controller: E=.47255924 without later observations, .35391042 with delayed noisy P, and .37240241 with delayed noisy frequency at eta_y=.05.

The ablation files are no_feedback_ablation.py and no_feedback_policy.json, no_feedback_validation.json, no_feedback_results.json. It is covered by the same continuous-phase/time validator and the replay/resource tests. This comparison attributes the gain to usable observations rather than to replacing a weak solver with a new algorithm.

## 6. Transfer qualification and a concrete failure

A damping change is not covered by the nominal model proof. For the altered plant y'=p-2 zeta y-x-u with zeta=.8, the original P=.5 all-phase contract is already impossible, regardless of controller or capacity. The high-start phase remains at p=2 for five units. Its constant-input y step response is

    g_zeta(t)=exp(-zeta t) sin(sqrt(1-zeta^2)t)/sqrt(1-zeta^2).

Up to its first maximum t*=1.072501847988807, the output impulse response is nonnegative. Since p-u>=1.5, every admissible control has

    y(t*) >= 1.5 g_.8(t*) = .636012939780041 > .6.

The necessary initial converter power is at least .584934450687030. This is a genuine failed transfer, not a controller-tuning defect. Damping 1.2 and smooth ramps were deferred when the fair frequency-only comparator became the higher-priority task. They are not claimed tested. In particular, square-wave threshold classification cannot be silently reused as an all-noise observer for ramped measurements.

## 7. Reproducibility, tests, and correction history

Environment: outputs/round2_20261003/andes_env/bin/python. No prior round2 artifact was edited; all new work is in this folder. The production baseline is robust_filter.py, not the exploratory prototype.py. Reproduce by running robust_filter.py, validate_continuous.py, frequency_observer.py, nominal_sampled_cbf.py, no_feedback_ablation.py, test_feedback.py in that order.

The seven QA tests cover analytic phase envelopes, explicit phase kinks, P-policy nonanticipativity, frequency-policy nonanticipativity, deterministic/adversarial frequency-detector interval coverage, dense phase/time replay against analytic maxima, and common resources/terminal recovery. All pass. These finite QA tests supplement the analytic coverage argument and do not themselves create an all-noise theorem.

An early independent validator incorrectly used M=sum(c_i exp(-(l-t_i)))-Y rather than M=sum(c_i exp(-(l-t_i))). The dense replay test caught the underreported per-history maximum. The error was corrected, every controller and frequency certificate was rerun, and the first failed test log is retained as tests_first_failure.log. Resource policies were unchanged; the corrected worst peak is .599957499456683 rather than the earlier .599950... report. No failed or premature certificate should be quoted.

Exploratory choices: five-second predictor horizon, .01 collocation, .00005 safety tightening, .1 control hold, zero nominal action, and the prior three-pulse recovery were selected by development. No preregistration or held-out tuning claim is made. The final continuous-phase validation covers the entire stated family, so adding random phase trials is QA rather than extra independent scientific evidence. This work refutes an algorithmic-novelty/weak-baseline narrative; it does not claim controller optimality or hardware readiness.
