# G1: observation contracts and recoverable storage

Public handoff, 2026-10-07. Research evidence frozen 2026-10-04.

**Status: conditional paper candidate, not paper-ready.** This route studies the resource value of an observation contract; it does not propose a new predictive controller and does not establish that AI-stage telemetry is necessary.

## Exact question

For a persistent two-level load with an unknown continuous first-edge phase, common known initial power class, shared initial SOC and actuator/recovery constraints, how much recoverable storage is required when the controller receives no later observations, delayed noisy power samples, or delayed noisy frequency samples? Which observation errors make whole families indistinguishable to every causal controller?

The normalized core uses P=0.5, frequency band 0.6, sampling 0.1, delivery delay 0.05, actual zero-order-held controls, and restoration by time 20. The full mathematical contract, governing equations, policies, and proofs are in the linked dossier below. The later Kundur model has a different physical contract and is kept separate.

## Current results and limits

- No later observations: controller-independent necessary E ≥ 0.455615336483606 on the first five units, even without terminal recovery, using outward interval arithmetic
- Delayed power observations with error ≤ 0.1: a feasible same-method policy has E ≤ 0.353911 and initial SOC 0.350694
- Delayed frequency observations with error ≤ 0.05: a feasible same-method policy has E ≤ 0.372404 and initial SOC 0.369018; at error ≤ 0.005 the upper bound is 0.354550
- Whole-family observation opacity threshold is 1/(2e) ≈ 0.18393972. This is deliberately large noise, not a real PMU specification or an optimal-storage phase transition
- Strong low-noise frequency control is sufficient. Two feasible upper bounds do not prove that power telemetry beats optimal frequency control
- Exact frequency phase recovery has a sample-aligned-edge exception. Conventional sampled CBF trials failed; the stronger set-membership predictive safety filter supplied the feasible witnesses
- Kundur LTI feedback upper 94.264936753 MWs and blind necessary lower 64.616246553 MWs **do not separate**. The 25.8542% difference between same-family feasible controllers is not a universal controller-independent gain
- All 22 original finite nonlinear confirmations passed the stated frequency band. Two separately frozen, outcome-informed +10% amplitude challenges failed at about 0.10503 and 0.10506 Hz against a 0.1 Hz band. These are not 24 independent statistical trials
- No measured AI load→PCC→grid causal chain, hardware cost saving, broad nonlinear guarantee, or resolved priority claim has been established

Read [the full research dossier](evidence/outputs/round3_g1_20261004/G1_THIRD_ROUND_RESEARCH_DOSSIER_ZH.md), [machine-readable final index](evidence/outputs/round3_g1_20261004/FINAL_RESULT_INDEX.json), and [independent audit](evidence/outputs/round3_g1_independent_audit_20261004/INDEPENDENT_G1_THIRD_ROUND_AUDIT_ZH.md).

## Start and reproduce

From this branch's repository root:

```sh
cd research/G1
python3 evidence/verify_package.py
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r evidence/requirements-review.txt
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python3 evidence/validate_copy.py --work-dir /tmp/g1-review-unique-directory
```

Use a fresh, nonexistent temporary directory. Installing dependencies requires an authorized environment/network. The validator makes a disposable copy and verifies saved witnesses without resynthesis or nonlinear simulation. It checks the interval lower, six interval upper policies, seven implementation tests, 1,444 exact observation-boundary cases, frozen-input refusal, all 24 canonical CSV sets, and three representative nonlinear traces. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for scope and full-replay blockers.

## Contents and handoff

- [AGENT_START.md](AGENT_START.md): self-contained starting prompt
- [PAPER_ROADMAP.md](PAPER_ROADMAP.md): priority, experiments, ablations, transfer, baselines, stopping conditions
- [DATA_AND_LICENSES.md](DATA_AND_LICENSES.md): provenance, downloads, license boundaries and source hashes
- [PUBLICATION_NOTES.md](PUBLICATION_NOTES.md): public-copy sanitization and permissions
- `evidence/`: theory, all scientific source in the compact source archive, policies, certificates, results, canonical inputs, representative binary traces, and explicit omitted-file inventory
- `SOURCE_PROVENANCE.json`: archive identity and original→public SHA-256 map
- `PUBLIC_MANIFEST.json`: final released bytes and sizes

This is a complete **handoff of the recovered compact evidence**, not a claim that all historical dependencies or raw nonlinear arrays were recovered. The inherited archive omitted 41 large raw trace files and the qualified simulator installation. Their identities and restoration routes remain recorded. Sanitized public manifests are separate from historical scientific freezes.
