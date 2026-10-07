# Reproducing the W6 grid-memory extension

This folder is self-contained for CPU execution. It requires Python 3, numpy,
scipy, mpmath and matplotlib. No GPU, cloud credentials, GPU driver, proprietary
dataset or network request is required. `ENVIRONMENT.json` records versions.

## Preserve the frozen evidence

Copy this complete folder to a fresh working directory before rerunning. Several
scripts write their raw outputs next to the code. An exploratory rerun's timestamp
or timing fields will change; this does not create a new independent sample.
Never overwrite the master evidence when comparing runs.

The two original W6 solver modules are bundled byte-identically in
`guard_eval/code/vendor_original/`; their hashes are in that study's receipt. The
existing Kundur linear model is in `inputs/`, with source SHA256 and scope in
`inputs/SOURCE_RECEIPT.json`. No restoration-only absolute path is necessary.

## Quick checks

From this directory:

```sh
export OPENBLAS_NUM_THREADS=1
export MPLCONFIGDIR=/tmp/w6-matplotlib
export XDG_CACHE_HOME=/tmp/w6-cache
python -m compileall -q code review guard_eval/code guard_eval/code/vendor_original
python review/verify_swing_exact.py
python review/verify_network_transfer.py
python review/verify_slew_support.py
python review/verify_slew_support_repair.py
```

`verify_swing_exact.py` enumerates every active-segment stationary point and the
first tail extrema, exploiting their exact geometric decay. It also runs the
saved rational-node midpoint witness. The network verifier compares the modal
implementation with direct matrix exponentials and independent physical-cost
quadrature. These are independent floating/high-precision validations, not
directed-rounding certificates.

## Fresh auxiliary simulations

```sh
python code/slew_support.py
python code/kundur_transfer.py
python code/plot_grid_boundaries.py
```

The support script creates twelve amplitude/slew LP runs, inward feasible
witnesses, exact serialized path checks and residual-aware weak dual upper
evaluations. The network script runs four **exploratory** linear-model transfers,
not new nonlinear-grid experiments. Both include explicit infinite-tail budgets.

The frozen primary guard, executor and separately amended knee-aligned studies
have their exact commands in `guard_eval/reports/GRID_GUARD_STUDY.md`. Run those
on the copied folder. They contain
one design and eight frozen confirmations, 72 executor combinations, and an
explicit post-confirmation numerical-resolution amendment; do not merge the
amendment silently into the original confirmation table.

## What reproduction establishes

- Same mathematical model and controller implementation
- Full actual-power return and complete modeled grid tail
- Cost ledger, fixed work, common cap/slew/EOS information and honest baseline scope
- Reproducible ordinary-float results and independent formula checks

It does not establish actual GPU realizability, a valid facility PCC map,
identified model uncertainty, a site-specific frequency limit, concurrency,
nonlinear network validity, or hardware safety. The parent delivery contains a
separate GPU measurement handoff for those remaining obligations.
