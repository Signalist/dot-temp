# G3 handoff: prefix exclusion and sampled recovery

Status on 2026-10-07: **conditional application-theory candidate; not paper-ready**. The authoritative third-round result is **808 ≤ Qsup ≤ 812.5 kvar**, with the 812.5 endpoint itself excluded, under the stated averaged model. Earlier 834.4145309 kvar bounds are historical, not the current frontier. No general solver novelty or physical deployment qualification is established.

## Exact research question

For a continuing, pointwise-fixed workload d(t), a grid-import P cap and reactive-support Q floor, a limited lag/ramp battery port, common initial state, and full recovery, can every alternative P/Q allocation be excluded by coupling cumulative lost grid delivery to temporary inductive-energy release? Can a sampled battery command provide an inner witness under the same physical and workload contract?

The third-round answer is yes within the specified balanced averaged model. The outer certificate uses only the prefix through 23.9 ms, so it does not need terminal recovery or a late recharge budget. The inner retains the original 0.2 s exact recovery contract. Read `evidence/round3/theory/PREFIX_COUPLED_CERTIFICATE.md` for equations and quantifiers; never reconstruct formulas from a prose summary.

## Current findings and negative limits

- At 100 kW active service, 100 J net-cap allowance and fixed known parameters, a battery command held every 25 μs before 40 ms and every 100 μs afterward certifies 808 kvar, with all-time modulation-energy margin at least 1.852973 J
- The inner is a rational base command plus an analytically defined two-block endpoint correction. Exact recovery is a mathematical identity, not a promise that a rounded command table resets real hardware
- A frozen 30-digit outward interval prefix certificate excludes 812.5 kvar and all higher Q floors. The 4.5 kvar bracket is 82.96% narrower than the previous bracket; this is not an 82.96% capacity gain. The exploratory root near 812.27 is not a certified threshold
- The 50 and 100 μs fixed-path inner approximations have negative margin. This neither excludes all allocations nor proves optimal hold-rate requirements
- A matched-information mature CLARABEL SOCP reproduces the old continuous-command 808 kvar witness. Its stronger actuation permission differs from held commands. No solver advantage is claimed
- Ordered weaker-port parameters inherit the outer exclusion: command 400–450 kW, rising ramp 25–30 MW/s, lag 5–6 ms, initial delay 1–2 ms. The 808 inner is not robust over that box
- Fixed d(t) is the computing-service contract. No AI-specific mathematical mechanism, real GPU power calibration, complete PWM same-contract near-boundary closure, uncertain-parameter robust inner or hardware validation is established
- The old 600 kvar / 34-run PWM finite-tolerance recovery campaign is retained as history. It has a different contract and cannot certify the new 808 kvar exact-recovery result

## Read in order

1. `docs/RESEARCH_ROADMAP.md` and `docs/STOPPING_AND_PERMISSIONS.md`
2. `evidence/round3/G3_THIRD_ROUND_RESEARCH_DOSSIER_ZH.md`
3. `evidence/round3/theory/PREFIX_COUPLED_CERTIFICATE.md`
4. `evidence/round3/review/INDEPENDENT_SUPPORT_REVIEW.md`
5. `evidence/round3/SCIENTIFIC_CLOSURE.json` and `FINAL_RESULT_INDEX.json`
6. `evidence/round3/literature/ROUND3_PRECISE_COMPARISON.md`

`evidence/round2` retains full recovered second-round source, numerical witnesses, failed attempts and recovery/PWM sources. `evidence/early_audits` retains earlier G3 model/allocation/current-guard audits for diagnosis; those historical alternatives are not promoted to current paper claims. Large traces already omitted from the recovered cores cannot be recreated from hashes alone. The omitted-trace index and generation source are retained.

## Portable reproduction

From the repository root:

```sh
cd research/G3
python3 tools/verify_handoff.py
python3 tools/smoke_test.py
python3 -m venv .venv
.venv/bin/python -m pip install -r evidence/round3/requirements.txt
.venv/bin/python tools/reproduce.py --mode exact --output ../g3-exact-run
.venv/bin/python tools/reproduce.py --mode full --output ../g3-full-run
```

Outputs must be new directories outside this handoff. `exact` rechecks saved certificates/profile rationals and the source scientific assertions without reoptimizing; it needs NumPy, SciPy and mpmath. `full` additionally regenerates held controls, baselines, ablations and figures and needs all pinned dependencies. A full-mode solver may select different valid floating coordinates; review residuals and exact certificate semantics, never silently substitute its solution for the frozen witness. Historical C++17 PWM rebuilds are separate and costly; see `docs/REPRODUCIBILITY.md`.

Fresh validation for this handoff is recorded in `validation/HANDOFF_VALIDATION.json`; historical replay logs are not fresh validation. The root `PUBLIC_MANIFEST.json` is authoritative for this sanitized distribution. Older manifests are provenance, may name intentionally excluded files, and must not be presented as a current all-files pass. No credentials, user-specific paths, raw third-party papers or environment binaries are included.

See `provenance/PUBLIC_SOURCES.md` for source/rights limits and download guidance, and `AGENT_START.md` for a safe next-agent prompt.
