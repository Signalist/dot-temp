from guard_study import *
s=json.loads((ROOT/'raw/STUDY_SUMMARY.json').read_text());a=json.loads((ROOT/'raw/ALIGNED_RESULTS.json').read_text());rows={r['id']:json.loads((ROOT/f"raw/{r['id']}.json").read_text()) for r in a};design=rows['design'];e=json.loads((ROOT/'raw/EXECUTOR_RESULTS.json').read_text())
lines=[]
for r in a[1:]:
 c=r['config'];n=r['policies']['nominal_aligned_optimal'];b=rows[r['id']]['policies']['nominal_target'];rob=r['policies']['robust_aligned_optimal'];lines.append(f"| {c['beta']} | {c['R']} | {c['mode_Hz']} | {n['parts']['objective']:.8f} | {b['parts']['objective']:.8f} | {n['gain_vs_global_target_percent']:.6f} | {n['frequency_nominal']['peak_Hz']:.6f} | {n['frequency_transfer_worst']['peak_Hz']:.6f} | {rob['frequency_transfer_worst']['peak_Hz']:.6f} |")
text=f'''# W6 isolated-cycle grid-guard study

## Result and limits

The amplitude guard gives a sufficient all-time frequency guarantee in the stated stable linear grid model, including the entire tail after actual dynamic power returns to zero. It does not give a grid-reset or repeated-cycle regeneration guarantee. In **7/8 frozen nominal guarded confirmation cases**, the numerically worst EOS produces its frequency maximum **after power return**. This is the strongest empirical structural observation of this study.

The eight fixed confirmations have nominal guarded peaks **0.012236–0.019794 Hz**, and tested uncertain-grid peaks **0.017059–0.025320 Hz**. The budget **0.05 Hz is a declared modeling/planning study budget**, not a compliance threshold or empirical facility allowance. These finite tests do **not** demonstrate failure of the nominal guard under mismatch. They show substantial conservatism. The robust guard restores the analytic whole-box guarantee and has a measurable cost premium.

Matched-cap target policies are strong baselines. Supplementary knee-aligned convex profiles improve weighted full-cycle cost by **0.000730–1.401856%** under nominal guards and **0.000148–0.711037%** under robust guards. The smallest improvements are operationally negligible. There is no claimed improvement over an exact globally optimal, same-information reference.

No hardware traces, measured facility responses, hardware power commands, empirical service-curve fit, multi-task grid-reset guarantee, or regulatory claim is included.

## Contract and provenance

One isolated task has fixed unknown work W uniformly distributed on [0,2]. Initial actual dynamic power and initial grid state are zero. Service is s(p)=p^β, actual power is nonnegative, and |p_dot|≤R. EOS is instantaneous in the optimization study. Actual power returns at −R after EOS and all remaining dissipation is charged. The objective is E[E_dynamic]+E[T_powercycle], with c=1. Dynamic energy is in normalized model-power×seconds; the hypothetical PCC disturbance is 20 MW×p. Service time, recovery time and energy are separately recorded. Grid decay after actual power reaches zero is observed but adds no active power-cycle cost.

Design: β=.5, R=1, mode=.4 Hz, ζ=.1. Confirmation: the complete cross product β∈{{.5,.8}}, R∈{{.5,2}}, mode∈{{.25,.7}} Hz, at ζ=.08. All cases use M=2, c=1. The original unit-work implementation is used with R_eff=R M and all reported physical costs/times multiplied by M, so z slopes in physical work remain bounded by R.

A filesystem reset erased the first draft protocol before any numerical job ran. The lost hash is recorded only as provenance, not as an extant artifact. Published prior W6 sources were subsequently restored from the verified portable archive and imported read-only. The fresh protocol was frozen before design/confirmation results:

`{s['protocol_sha256']}`

`PROTOCOL.json` fixes the split, controllers, uniform meshes, EOS grid, grid model, uncertainty box and numerical qualifications. Original source hashes remain unchanged (`raw/QA.json`).

## Exact sign-split guard

Let ω=2π f_mode, a=ζω, d=ω sqrt(1−ζ²), b=g/M_H, and M_H=2HS/f0=133.333333 MW·s/Hz for H=4 s, S=1000 MW and f0=60 Hz. The stipulated stable swing model has

f''+2a f'+ω²f=−b p_dot,

and impulse response from p to f

h(t)=−b exp(−at)[cos(dt)−(a/d)sin(dt)].

Its signed integral is zero. Writing k=ζ/sqrt(1−ζ²), the positive and negative impulse areas are exactly equal:

G = integral h_+ = integral h_- = (b/ω) exp[−k acos(ζ)] / [1−exp(−πk)].

Proof: the step response is −(b/d) exp(−at)sin(dt). Its first extremum has magnitude (b/ω)exp[−k acos ζ]; consecutive extrema alternate sign with geometric ratio exp(−πk). Summing absolute changes yields total variation 2G, while the signed integral is zero. Consequently, every measurable 0≤p≤p_cap with zero initial grid state obeys |f(t)|≤p_cap G for every t≥0. The guarantee needs no EOS sampling and survives any execution delay that preserves the actual-power cap.

The optional slew-only diagnostic is

|f| ≤ R b/ω² coth[πζ/(2sqrt(1−ζ²))].

The minimum of the amplitude and slew bounds is valid. It is not presented as an optimal joint amplitude/slew bound.

For the design case, G=0.1901466801229238 Hz/model-power. Floating signed-area integration to 397.887 s agrees to about 6e−17, with analytic envelope tail bound 2.24e−44. This is a floating check, not an outward-rounded certificate. Closed-form segment propagation and an independent augmented matrix exponential agree within 2.78e−17 in the saved design test.

## Robust box and its proof

The uncertainty box is gain g∈[20,22] MW/model-power, mode frequency in [.9,1.1] times its nominal value, and damping in [.8,1] times nominal. G is linear in g and inverse in ω. Moreover, with θ=acos ζ,

d(log G)/dζ = [−θ+ζ sqrt(1−ζ²)−π/(exp(πk)−1)]/(1−ζ²)^(3/2) < 0,

because θ−sinθ cosθ>0 on (0,π/2). Therefore the supremum over the entire box occurs at g=22, mode factor .9, damping factor .8. This is not a corner-sampling surrogate for the supremum. The eight corners are additional transfer experiments only.

In the design case, nominal p_cap=0.2629548934 and robust p_cap=0.1721713416. The aligned robust cost is 8.55% higher than the aligned nominal-guard cost. Across confirmations the robust cost premium ranges 0.99–33.52%. This is a price of a conservative sufficient guarantee, not evidence that these actual trajectories otherwise violate the budget.

## Fixed confirmation outcomes

The table uses the transparently appended knee-aligned diagnostic, with the original frozen uniform-mesh outputs retained separately. Both convex and target policies use the same cap, EOS information and complete physical cycle cost. `Nominal peak` and `transfer peak` are dense-EOS-plus-local-refinement numerical maxima over all future time.

| β | R | mode Hz | Aligned J | Target J | Gain % | Nominal peak Hz | Nominal-policy transfer Hz | Robust-policy transfer Hz |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(lines)}

The no-guard original optimum is only an infeasibility/conservatism diagnostic. It exceeds the study budget in 3/8 nominal grid tests and 5/8 uncertain-grid tests. It is never treated as a fair feasible comparator under the stricter cap. The design no-guard trajectory itself remains below the budget, an explicitly retained negative finding.

## Numerical agreement and preserved failure

The frozen implementation used uniform work meshes N=64,128,256 and positive endpoint-transformed quadrature orders 32/96. Its independently implemented Bellman reference exactly minimizes the same uniform-EOS objective over its finite state/edge grid, using N=64/sub=4 and N=128/sub=8 and appending the guard cap as a state. It is a global restricted feasible optimum, not a continuous lower certificate. Bellman edge integration agrees with independent positive quadrature to 8.9e−15 across saved cases.

A real discretization failure is retained: β=.8,R=2,mode=.25 gives a nominal N256 mesh cost 0.040332% worse than the exact target because its short capped ramp is not mesh-aligned. The largest frozen N128→256 relative cost change across guarded cases is 0.561157%. Solver success alone therefore does not establish adequate continuous accuracy.

`AMENDMENT_KNEE_ALIGNMENT.json`, frozen before supplementary outputs, adds exact cap/target ramp knees to N=128 and N=256 meshes for **all nine cases and both guards**, without replacing the frozen results or selecting cases. Its hash is `{s['amendment_sha256']}`. The largest supplementary refinement relative change is 8.14e−7; maximum reported finite-mesh linearization gap is 4.74e−7 in objective units. The problematic nominal gain becomes only 0.000730%, so no practically meaningful advantage is inferred. These are floating numerical diagnostics, not interval certificates or universal error bounds.

Every main frequency run evaluates a fixed 2049-point EOS grid on [0,2], refines all detected local maxima, propagates each linear-power segment in closed form, evaluates analytic segment stationary points, and evaluates the infinite zero-input tail analytically. Dense/refined EOS searches do not prove universal worst-case EOS optimality. Universal safety follows only from the analytic cap theorem under its model assumptions.

## Executable simulated actual-power controller

`EXECUTOR_PROTOCOL.json` was separately frozen before executor outputs. Three cases are fixed: design, β=.5/R=.5/mode=.25, and β=.8/R=2/mode=.7. For each, nominal/robust convex and same-cap target profiles are tested with event-driven execution and a .01 s sampled tracker, at EOS delays 0,.03,.1 s (72 combinations). The sampled tracker uses observed work before true EOS and a potential-service ghost-progress estimate during unobserved EOS; it clips its requested actual slew and enforces actual-power cap/zero boundaries. This is an ideal actual-power simulator, not an API that commands hardware.

Useful work is exactly W; potential service after true EOS is waste. Full post-EOS dissipation and physical return time are charged. Every grid tail is observed after the charged power cycle. Expected costs use a 1025-point EOS quadrature with a 513-point check; the maximum relative difference is 1.37e−5. All tested paths complete supported work and meet cap/slew within floating tolerance. The largest dense-EOS executor peak is 0.022987 Hz.

For pure delay, the pathwise bound ΔJ≤2(p_cap+c)δ holds in all recorded checks. This bound is **not** used to bound sampling error. Sampling-only mean-cost changes relative to the finite-mesh event profile span −0.020285% to +0.016539%; small negative differences reflect different feasible path discretizations and do not imply superiority to the continuous optimum. In the design nominal convex case, .03/.1 s observation delays increase event-driven mean cost by 1.3114%/4.3237%; the corresponding sampled figures are 1.3107%/4.3230%. Cap-based model safety survives both delay and sampling.

## Files and reproduction

- `raw/POLICY_SUMMARY.csv`: energy, service time, recovery time, cycle time, objective and peaks for every policy
- `raw/EXECUTOR_SUMMARY.csv`: 72 complete executor summaries
- `raw/STUDY_SUMMARY.json`, `raw/QA.json`, original per-case JSON and aligned/raw executor outputs
- `curves/*_path.csv`: explicit work/z/power/time controller paths
- `curves/*_eos.npz`: dense EOS curves for nominal and all eight uncertainty corners
- `curves/*_executor.csv`, `*_executor_EOS.npz`: executable waveforms and per-EOS energy/work/cost ledgers
- `plots/design_policy_and_eos.png`, `confirmation_peaks_and_cost.png`, `post_return_grid_memory.png`, `executor_delay_tradeoff.png`

From this `code/` directory with existing NumPy/SciPy/Matplotlib:

1. `OPENBLAS_NUM_THREADS=1 python guard_study.py design`
2. `OPENBLAS_NUM_THREADS=1 python guard_study.py confirmation`
3. `OPENBLAS_NUM_THREADS=1 python aligned_study.py`
4. `OPENBLAS_NUM_THREADS=1 python executor_study.py`
5. `MPLCONFIGDIR=/tmp/w6-mpl OPENBLAS_NUM_THREADS=1 python summarize_study.py`
6. `python write_report.py`

Do not rerun the freeze script over existing protocols. No new package installation is required. Byte-identical original solver copies are included in `code/vendor_original/` for standalone portability; their restored-archive provenance and SHA256 hashes are recorded in the protocol. Imports prefer these bundled copies and otherwise use the restored archive. The four saved plot images were visually inspected after generation. Recorded CPU-only optimization timers total 11.7507 s for 81 SLSQP solves and 20.6149 s for 36 Bellman runs (32.3656 s combined). These are process-internal wall timers for optimization calls, not end-to-end CPU seconds; frequency evaluation, executor sweeps and artifact generation were not included in that timer.
'''
(ROOT/'reports/GRID_GUARD_STUDY.md').write_text(text)
# Hash all deliverables, excluding this manifest to avoid recursion.
files=[]
for p in sorted(ROOT.rglob('*')):
 if p.is_file() and '__pycache__' not in str(p) and p.name!='MANIFEST.json':files.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(ROOT/'MANIFEST.json').write_text(json.dumps({'created_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'files':files},indent=2));print('report',len(text),'chars',len(files),'files')
