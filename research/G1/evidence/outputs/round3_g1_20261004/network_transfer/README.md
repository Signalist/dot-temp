# G1 round3: qualified network transfer

**Completed:** conventional delayed/noisy sampled-P control on the full Kundur quotient, exact loss-aware recovery, a genuine all-phase/all-future LTI certificate, frozen nonlinear transfer, and retained failures. The two-state theorem is not automatically transferred.

## Main evidence

| Evidence | Result | Limit |
|---|---:|---|
| Sampled-P conventional LP, usable excursion |94.264936753 MWs|Restricted constructive upper bound |
| Initial-P-only same-family LP, usable excursion |127.134534346 MWs|Same initial SOC, actuator, band, recovery |
| Same-family reduction |25.854184909%|Not a universal information-optimality theorem |
| All-phase/all-future LTI upper, sampled P |0.097452398756 Hz|Analytic floating point, not nonlinear or interval arithmetic |
| All-phase/all-future LTI upper, initial P only |0.097457280096 Hz|Same scope |
| Arbitrary measurable OL continuous lower |64.616246553 MWs|Below feedback upper; universal separation is unproved |
| Original frozen nonlinear confirmation |22/22 completed and passed|Includes4 stresses and2 timestep repeats, not independent trials |
| Worst of8 nominal unseen sampled-P points |0.093579120388 Hz|Individual-generator endpoint, not COI |
| Worst of8 nominal unseen initial-P-only points |0.092807536365 Hz|Higher service resource, similar grid performance |
| Separately frozen +10% high-start stress |0.105061904679 Hz at fine step|Explicit retained failure; not in original22 counts |

The final controller observes only initial high/low class and later noisy P classes sampled every.1 s and delayed.05 s. Errors up to5 MW do not change the nominal square-wave class. It uses50 MW command headroom, matched tau=.05 s PCS, eta=.95,500 MW/s slew, full initial usable SOC, and exact recovery by60 s. Synthetic50/100 MW load continues forever. This is effective service energy, not installed battery nameplate sizing or capital cost.

## Read first

- METHOD_AND_LIMITS.md: full method, exact information contract, phase sensitivity derivation, continuous lower relaxation, failure history, and permitted interpretations
- BOUNDARY_CONTRACT_AUDIT.json and exact_observation_contract.py: exact sample-edge semantics and1,444 near-boundary checks; frozen numerical helpers must not define infinitesimal boundary histories
- BINNED93_LTI_CERTIFICATES.json: per-bin continuous and tail bounds, SOC/PCS checks
- NONLINEAR_CONFIRMATION_SUMMARY.csv/.json: every original frozen result, including input-matched linear discrepancies
- AMPLITUDE_STRESS_ADDENDUM_RESULTS.json: outcome-informed +10% coarse/fine failure, kept separate
- figure_network_transfer.png/.svg: publication-oriented four-panel scientific summary
- REPRODUCE.md: commands, provenance, and result-count discipline

## Negative evidence preserved

An11-phase development controller violates its command cap on unseen phases (74.778 MW versus50 MW) and is rejected. At a tighter.0915 Hz design target, the initial-P-only low-start restricted family becomes infeasible after output refinement. The unrestricted OL lower does not separate the constructive feedback upper. The +10% nonlinear amplitude challenge fails at both timesteps. No failure was relabeled as a pass or removed.

## Integrity and artifact size

New schedules, results and ANDES caches are isolated in this directory. The round2 model, workbooks, simulator sources, results and old caches are unchanged; ROUND2_INTEGRITY_CHECK.json verifies266 locked files. Raw nonlinear observables and exact schedules are preserved, while the simulator environment is not duplicated or redistributed. The qualification/provenance input remains round2/grid_transfer/README_qualification.md and kundur_reduced51.npz, SHA-25631e798abc23bdcb6c3b46aeb488caf96636127390935eac4d9f0e2fdd5601828.


### Serialized-input numerical precision

The formula-defined SOC recovery is exact, and the original stored physical metrics refer to the in-memory model arrays. The actual nonlinear replay CSVs use12 significant digits. Independent re-integration of those unchanged CSVs gives worst absolute terminal SOC depletion1.4824097505084e-10 MWs and maximum command50.000000000050036 MW. The declared numerical audit tolerances are1e-8 MWs for terminal recovery and1e-9 MW for command feasibility; all24 case records satisfy them. These tiny serialization/arithmetic residuals are disclosed, not described as exact zero recovery or strict binary-floating-point <=50 MW. Original stored array metrics remain unchanged. SERIALIZED_INPUT_NUMERICAL_AUDIT.json records each case, both cumulative and pairwise summation results, and input hashes.
