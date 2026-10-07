# G3 recovery phase2 V2: causal capacitor-plus-inventory recovery

## Outcome
34/34 runs satisfy every frozen V2 contract component: two nominal runs, sixteen known-regression runs and sixteen fresh-confirmation runs. This is finite numerical evidence for the enumerated cells, not uniform parameter robustness, hardware validation, exact continuous-time recovery or the original exact-service contract.

## Versioned evidence and causal controller
V1A is preserved with 14 passes and 4 failures. Its four failures were the 5 kW paired incremental command budget at actual tau=4ms/slew 25 MW/s. V2 is a separate authorized revision, frozen before its own results, and never tuned after its fresh confirmation. The V2 freeze preceded a later request to clarify filter-energy accounting; that later clarification did not change controller, thresholds or results.

At each 10 kHz PWM boundary, eS=71600−(W+B) J, cP=clip(100eS+2500zS,±4500W), and zS is conditionally integrated by Ts eS with the same antiwindup rule. Inventory control is uB=clip(20(B−50000),±10000W). W/B measurements are ideal, noiseless, instantaneous sampled values; there is no added measurement filter or delay. The legacy source column zw stores zS in this version. Current PI/PWM, original command polynomial, physical plant and all service-clock rules are unchanged.

The loop regulates capacitor-plus-inventory energy S=W+B, not full physical energy. With Z=LΣi²/2, Sdot=Pgrid−RΣi²−d−Zdot. Only the internal battery transfer b cancels. Zdot remains an explicit disturbance; Z is separately evaluated from actual measured currents and is never merged into copper loss.

At service, cP/zS are held and uB=0, preserving the original port feedforward. At recovery, the same causal feedback resumes against constant setpoints. The continuing workload remains650kW afterward, with its original prescribed positive service-time schedule unchanged. No load shedding, no state reset, no future actual workload and no online matched-health trajectory are used. Actual tau/ramp enter only the plant.

Exactly one fresh 2 s nominal healthy checkpoint per integration resolution initializes every corresponding V2 case. It includes plant, current PI, energy PI, held correction and PWM/grid timing. Healthy and service branches use the same gates and clocks; the healthy branch removes service P/Q/d/u feedforward only. The known midpoint P/Q predictor can act just before an off-PWM onset; pre-onset state and energy are separately recorded and whole cost starts at the common 2 s checkpoint. Onset states are not asserted identical for 19 us or 37 us.

## Frozen scope and numerical acceptance
- Nominal: actual tau=5ms/slew30MW/s/onset0, integrationsteps 1 us and0.5us
- Known regression: actual tau=4/6ms × slew25/35MW/s × onset37/73us, each at both steps; these cells were already seen inV1A
- Fresh confirmation: actual tau=4.5/5.5ms × slew27/33MW/s × onset19/61us, each at both steps; frozen before anyV2 execution
- Hardware: voltage1080–1320V, each phase and space-vector current≤1500A, B0–100kJ, |b|/|u|≤450kW, declared actual slew, and PWM feasibility
- Service: actual and nominal command means computed over identical20ms bins; |P error|≤2kW and |Q error|≤10kvar
- Physical return: over the final five20ms cycles endingT+0.5s, common1us sampled |ΔW|/|ΔB|≤2J and each |Δi|≤2A
- Recovery budget: paired incremental |cP|≤5kW; |signed|, positive-only and absolute-integral incremental grid energies each≤100J fromT toT+0.5s; an additional0.2s continuing observation exposes downstream debt
- The100J V2 recovery budgets differ from the core100J net late-P allowance during the exact0–0.2s averaged contract; equal units/values do not make the contracts equivalent

## Fine-step results

| Cell | evidence | max ΔW J | max ΔB J | max Δi A | max incremental cP W | signed recovery J | positive J | absolute J | full pass |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| nominal_h05 | nominal | 6.37018e-05 | 2.96117e-07 | 2.82673e-06 | 23.7934 | -0.235908 | 0.0453609 | 0.32663 | True |
| tau4_r25_o37_h05 | regression | 0.226772 | 0.22567 | 0.000296509 | 29.2096 | -0.286216 | 0.136859 | 0.565311 | True |
| tau4_r25_o73_h05 | regression | 0.226527 | 0.225491 | 0.000296631 | 19.5235 | -0.186283 | 0.129036 | 0.453261 | True |
| tau4_r35_o37_h05 | regression | 0.00144979 | 0.00149393 | 3.60868e-06 | 28.0874 | -0.278566 | 0.0479964 | 0.374675 | True |
| tau4_r35_o73_h05 | regression | 0.00144564 | 0.00149084 | 3.42839e-06 | 18.3919 | -0.182054 | 0.0346028 | 0.251459 | True |
| tau6_r25_o37_h05 | regression | 0.0325103 | 0.0322991 | 4.35218e-05 | 31.5202 | -0.311548 | 0.0855621 | 0.484193 | True |
| tau6_r25_o73_h05 | regression | 0.0324745 | 0.0322736 | 4.36458e-05 | 21.8052 | -0.214105 | 0.0748941 | 0.366443 | True |
| tau6_r35_o37_h05 | regression | 0.000179788 | 0.000252713 | 3.5005e-06 | 31.0305 | -0.307853 | 0.0592739 | 0.426319 | True |
| tau6_r35_o73_h05 | regression | 0.000180411 | 0.000254022 | 3.29348e-06 | 21.3143 | -0.211485 | 0.0456483 | 0.302647 | True |
| tau4.5_r27_o19_h05 | confirmation | 0.0762781 | 0.0758795 | 0.000101489 | 26.7086 | -0.261547 | 0.0974513 | 0.460611 | True |
| tau4.5_r27_o61_h05 | confirmation | 0.0761918 | 0.0758076 | 0.000101597 | 18.0622 | -0.177721 | 0.0926552 | 0.365084 | True |
| tau4.5_r33_o19_h05 | confirmation | 0.000115236 | 5.65946e-05 | 2.64418e-06 | 26.0811 | -0.258707 | 0.0466309 | 0.352022 | True |
| tau4.5_r33_o61_h05 | confirmation | 0.000116826 | 5.76074e-05 | 2.47123e-06 | 17.4322 | -0.172792 | 0.0346789 | 0.242172 | True |
| tau5.5_r27_o19_h05 | confirmation | 0.0222475 | 0.022151 | 2.8522e-05 | 27.8215 | -0.274801 | 0.0668851 | 0.409983 | True |
| tau5.5_r27_o61_h05 | confirmation | 0.0222225 | 0.0221306 | 2.86332e-05 | 19.1653 | -0.189585 | 0.0568892 | 0.304053 | True |
| tau5.5_r33_o19_h05 | confirmation | 5.61875e-05 | 0.000124721 | 3.12992e-06 | 27.5458 | -0.273271 | 0.0524711 | 0.378151 | True |
| tau5.5_r33_o61_h05 | confirmation | 5.64191e-05 | 0.000125555 | 2.94644e-06 | 18.8888 | -0.1873 | 0.040461 | 0.268189 | True |

Worst across all34 runs: |ΔW|=0.226772J, |ΔB|=0.22567J, phase-current difference=0.000296632A, paired incremental cP=31.5206W, signed-energy magnitude=0.311569J, positive energy=0.136859J and absolute recovery energy=0.565316J.
Hardware extrema across all runs: V=1119.680130–1262.805434V, peak phase current=971.585044A, space-vector current=993.426078A. Maximum20ms P/Q errors=98.928699W/533.870327var.

## Filter-energy accounting and justified bound
FILTER_ENERGY_ACCOUNTING.json records exact matched ΔZ at the deadline/final observation, maximum phase-matched ΔZ over every PWM boundary in recovery, and dense1us ΔZ over the final100ms. ENERGY_COST_TABLE_V2.csv gives separate incremental ΔW, ΔB and ΔZ for every window. These are post-result disclosure clarifications; no pass criterion changed.

Given both branch space-vector amplitudes≤1500A, ||i||₂≤√(3/2)1500. If each paired phase current differs by≤2A, ||δi||₂≤√3·2. Therefore |ΔZ|≤(L/2)(||is||₂+||ih||₂)||δi||₂≤1.909188J for L=0.3mH. This bounds filter-energy mismatch implied by the engineering current tolerance; actual observed ΔZ is independently computed, not replaced by that bound.
Observed maximum recovery-window PWM-boundary |ΔZ|=0.0143813J, final100ms dense |ΔZ|=9.4686e-05J, and exact-deadline |ΔZ|=7.94497e-06J. No continuous-time unsampled extremum guarantee is inferred.

## Health, energy and costs
The common-clock no-service identity test is bitwise equal. Both nominal warmups and each final healthy comparison satisfy the 0.1 J/0.2A successive-cycle qualification. The healthy bias learned before service is about52.4W in cP on average and 45.1W at the held phase, while actual continuing grid increment vs model baseline is about1.14W. The command bias compensates sampled tracking, not52W of extra physical load.

ENERGY_COST_TABLE_V2.csv includes all nominal/regression/confirmation cells at both steps for checkpoint→onset, service, recovery, post-deadline, onset→final and checkpoint→final. It reports gross AC and net-after-copper increments vs matched health AND the theoretical model baseline, plus absolute and positive-only cost. Signed energies use physical quadrature/snapshots; absolute/positive metrics use matched PWM-cycle average power, not instantaneous switched-power absolute integrals. The model baseline gross P is654498.72485653043W, copper loss4498.72485653043W, net650000W.

Fine nominal example:

| Window | gross Δ health J | net-after-copper Δ health J | gross Δ model J | net-after-copper Δ model J | positive Δ health J | absolute Δ health J |
|---|---:|---:|---:|---:|---:|---:|
| service_cost | 134.914959366 | 0.232671705 | 133.679392861 | -1.208380716 | 3635.887945 | 7136.860931 |
| recovery_cost | -0.235908268 | -0.232664194 | 1.787011732 | 1.206247193 | 0.045361 | 0.326630 |
| post_deadline_cost | -0.000012788 | -0.000012614 | 0.224908094 | -0.000658706 | 0.000000 | 0.000013 |
| checkpoint_total_cost | 134.679038310 | -0.000005103 | 135.691312687 | -0.002792229 | 3635.933306 | 7137.187574 |

Maximum full-trajectory numerical physical-energy closure residual=0.0108819J. Two-step convergence is retained in SUMMARY_V2.json. These residuals check the numerical simulator, not real measurement accuracy. Ideal switches, prescribed balanced grid, known L/R/C, noiseless sampling and the selected tau/ramp uncertainties limit the physical interpretation.

## Files and reproduction
Authoritative protocol: PROTOCOL_V2.json plus the pre-result LEDGER_ADDENDUM_PRE_RESULT.json. Frozen code/executable hashes: EXECUTION_FREEZE_V2.json. Run warmup, nominal, regression, confirmation in that order with run_campaign.py; run summarize.py then make_report.py. Independent audit lives in the recovery_phase2/audit area. No V1A frozen file or original theory/source/audit/validation/result file is modified by this revision.

Complete controller/inventory/duty residuals are retained as diagnostics; the claim remains finite-window physical recovery to declared tolerances. There is no claim of exact full-state equality, guaranteed return at every intermediate moment, or uniform uncertainty robustness.

## Explicit one-time V2 warmup cost

- h1: two-second warmup gross AC increment vs model baseline 2.325549593 J; net-after-copper increment 0.070522153 J; final-five-cycle mean cP 52.408896 W and actual mean AC increment 1.134258 W
- h05: two-second warmup gross AC increment vs model baseline 2.346501603 J; net-after-copper increment 0.089498317 J; final-five-cycle mean cP 52.418233 W and actual mean AC increment 1.144732 W

Warmup costs are separate from every service/recovery budget and are retained in WARMUP_COSTS.json.
