# Reproduce W6 round3

Requirements: Python3, numpy, scipy, mpmath, matplotlib. Recorded environment is supplied separately. No network or GPU is needed. The complete Azure source CSV, license and derived PMF are bundled; old task-policy nodes are copied byte-for-byte under prior/.

Run from any working directory:

    python /path/to/round3_w6_20261004/code/reproduce.py

This independently recomputes saved physical ledgers, primary high-precision moments, continuous duals, transfer/initial/repair results and counterexamples. It additionally reoptimizes a convex case, a four-atom lower/upper Bellman pair and the full623-atom empirical distribution at128 state boxes. Result: audit/PORTABLE_REPLAY.json.

Full optimization regeneration, including all trace refinements through2048 boxes:

    python /path/to/round3_w6_20261004/code/reproduce.py --full

The solver outputs and timestamps may differ in last bits or elapsed time; science comparisons use the recorded tolerance. Floating bounds are never outward-rounded certificates. The standalone trace script stores shared bridge segments once, and retains every EOS's total cost; expanded duplicate prefix ledgers are unnecessary for reproduction. The initial1024 expanded ledgers were separately compressed only as development evidence and are excluded from the small core ZIP.

Source order: theorem and protocol → code → raw results → independent review → Chinese dossier → final status/manifest. The old round2 source and all authoritative errata remain unchanged. New critical-prefix tests are exactly mesh aligned; arbitrary off-grid prefix calls fail explicitly rather than pretending convexity.
