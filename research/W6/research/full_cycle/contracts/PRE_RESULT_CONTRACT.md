# W6 round3 pre-result contract
Frozen before new numeric outcomes (2026-10-04 UTC).

Purpose: test a new exact reduction for a full recovery cycle, not rehabilitate the failed round2 hard-deadline candidate. No GPU measurements, physical deployment, or claims of first discovery.

Single unknown task W∈[0,1], EOS immediately observable, known distribution, dx/dt=s(p), actual dynamic p≥0 with |p_dot|≤R, fixed p(0)=p0. Before EOS all dynamic p performs productive work; after EOS fastest dissipative return to zero. No pre-EOS burn/pause, concurrency, battery, thermal state, command tracking, or extra observations. Objective J=E[dynamic energy]+c E[complete recovery-cycle duration], c=facility idle power + cycle-time multiplier. Facility idle power is assumed constant until return; no post-cycle accounting or task-time-only multiplier. All cost models dimensionless and explicitly synthetic.

Candidate new theorem: work state z=A(p); whole-cycle reserve identity, no-loss cap z≤R(1−x), critical cap, convexity under a curve/distribution curvature condition. Power laws s=p^β and tail hazard h(x)(1−x)≤(1+2β)/(1+β) are the initial sufficient class; uniform belongs. Nonzero initial state either prepaid descent or forced critical prefix plus convex residual. Independent mathematical review must precede a positive disposition.

Numeric designs:
1. Twelve primary uniform models β∈{.5,.8}, R∈{.5,4}, c∈{.25,1,4}; piecewise-linear z meshes 64/128, selected 256 refinements. Same-information optimizer, optimal clipped constant-target baseline, old task-time-only optimized policy reevaluated on full-cycle costs, and global finite-state Bellman baseline. No baseline is denied EOS or distribution information.
2. Independent exact/quad physical reconstruction including W near0, interior, near1 and1; stable log1p/expm1 integration, equal-endpoint limits, and whole ledger. Do not copy unstable old integrals.
3. Transfer: source uniform policy evaluated without retuning under lower-tail survival power, truncated exponential, endpoint-atom mixture; target-specific full-cycle oracle separately labeled. At least one distribution outside the sufficient condition, and interior atoms, must be tested as theory boundaries rather than silently excluded.
4. Nonzero initial cases must include below and above critical, as well as z0≥R; evaluate prefix/free-descent claims against matched global baseline.
5. Continuous primal–dual weak bound evaluated with numerical quadrature, mesh linearization gap, residuals, quadrature/refinement differences. None is an outward-rounded certificate. DP finite-grid optimum is not a continuous global lower bound unless a separate error bound is supplied.
6. Preserve all original round2 files and canonical erratum provenance. New outputs only in this round3 directory; model configurations, curves and distributions never called measured GPU data.

Stopping/disposition: complete exact theorem and boundary proofs, primary matched experiments, transfer and ablation, independent skeptical code/proof audit and reproducible replay. Report a meaningful theorem if supported; do not label high innovation confirmed or paper-ready solely from numeric success.
