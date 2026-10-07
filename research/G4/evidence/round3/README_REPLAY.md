# G4 sanitized third-round replay

This tree preserves the scientific producer/checker logic and frozen numerical evidence. The publication handoff changes private/cache paths, updates portable documentation and rebuilds EVIDENCE_INDEX.json. Original SHA-256 values and public SHA-256 values are recorded in the handoff-level provenance/SOURCE_TO_PUBLIC.json. It is not a byte-identical copy of the previous archive.

From the handoff root:

```sh
python3 -S evidence/round3/tools/replay.py --mode exact --output ../g4-exact-run
python3 evidence/round3/tools/replay.py --mode checks --output ../g4-checks-run
python3 evidence/round3/tools/replay.py --mode full --output ../g4-full-run
```

Use new output directories outside the entire handoff. Exact mode uses the standard library only; checks needs NumPy/SciPy and full additionally needs SymPy/Matplotlib. Pinned requirements are requirements-replay.txt in this folder. The wrapper verifies this sanitized payload, copies source/G4_round3, runs the selected scientific stages and compares JSON ignoring only declared timing/environment metadata. It does not rewrite frozen evidence.

The 89-record independent check covers 77 primary and 12 transfer finite rational LP certificates. Separate ideal-efficiency/PCC-step examples are outside that declared coverage. Floating leakage/finite-horizon checks remain floating point. Full-text third-party literature and Python environments are not included. Original science/literature manifests are provenance; they may name excluded files.

Optional unchanged historical-round2 verification cannot be claimed using the sanitized historical subset. See the root README and docs/REPRODUCIBILITY.md for withheld grid prerequisites and all scope limits. Neither a replay pass nor this packaging establishes novelty, physical realism or publication readiness.
