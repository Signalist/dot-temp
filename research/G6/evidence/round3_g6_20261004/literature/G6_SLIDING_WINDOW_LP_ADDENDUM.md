# Addendum: the single sliding-window contract has an exact classical LP/flow baseline

2026-10-04. This strengthens §5 of the robustness audit. A suffix-state DP is a general fallback, not a necessary or novel complexity for this contract.

## Exact reduction

Fix the capacity vector, the shared constant plant parameter, an output direction, and a finite horizon `N`. Let `p_j,q_j` be the two signed port contributions at lag `j`, including their discount factors. Optimizing the free common sign gives agreement reward `|p_j+q_j|` and disagreement reward `|p_j-q_j|`. Thus, with

`d_j=|p_j-q_j|-|p_j+q_j|`,

endpoint support equals

`sum_j |p_j+q_j| + max {sum_j d_j z_j : Az<=B*1, 0<=z<=1}`,

where `z_j=1` means a disagreement and row `s` of `A` selects the indices in one length-`L` window. This continuous LP has an integral optimal vertex: in increasing window-start order, every column of `A` has consecutive ones; hence `A` is totally unimodular, and adjoining the identity bounds preserves total unimodularity. The right-hand side is integral. Negative `d_j` require no special algorithm; an optional disagreement with negative profit can simply be omitted. The guarantee requires free common-sign choices and the stated additive objective; extra restrictions can change the problem.

A directly readable proof of the matrix theorem appears in Thomas Rothvoss's *Discrete Optimization*, §6.3, Lemma 55; Theorem 56 applies it to weighted interval scheduling. His §6.2, Corollary 53 and Lemma 54, gives integral flow/circulation optimization. [Author lecture notes, Spring 2020, PDF pp. 68–69](https://sites.math.washington.edu/~rothvoss/lecturenotes/DisOpt409-Spring2020.pdf).

## Equivalent capacity-B interval scheduling and min-cost flow

Associate disagreement `j` with interval `[j,j+L)` and profit `d_j`. At any integer time `t`, overlapping selected intervals have start indices in `[t-L+1,t]`; requiring at most `B` overlaps is exactly a rolling disagreement-count bound.

Construct nodes at the sorted distinct start/end times (at most `2N`). Add a zero-cost time arc of capacity `B` between consecutive nodes. For each `j`, add a job arc `j -> j+L`, capacity one and cost `-d_j`. Send `B` units from the earliest node to the latest. The network has `O(N)` nodes/arcs after endpoint compression.

For an integral flow, a job arc carrying one unit selects its interval. Every time cut carries `B` units, so no more than `B` selected intervals cross the cut. Conversely, intervals with overlap at most `B` can be greedily assigned to `B` nonoverlapping tracks; each track forms a path of job and time arcs. Thus the minimum cost is exactly the negative optimal disagreement profit. This is the standard fixed-interval scheduling reduction, not a new G6 optimizer.

Arkin–Silverberg's original *Scheduling jobs with fixed start and end times* (1987) treats maximum-value selection on `k` identical machines; its institution-hosted abstract states an `O(n^2 log n)` algorithm. [Primary institutional record](https://researchconnect.suny.edu/en/publications/scheduling-jobs-with-fixed-start-and-end-times/). Allan Borodin's author lecture explicitly identifies its min-cost-flow reduction and the equivalent TU formulation. [Lecture 6, 2012, slide 3](https://www.cs.toronto.edu/~bor/2420f12/L6.pdf). The original 1987 full proof was not obtained here; the independent network equivalence above supplies the exact G6 mapping.

## Boundary and complexity qualifications

- The interval formulation corresponds to a word extendable by agreement outside the finite horizon, so boundary-clipped windows are included. If `N>=L`, these extra partial-window inequalities are implied by the first/last full window and nonnegativity. If `N<L`, a convention checking only complete in-horizon windows is vacuous, whereas the extendable contract requires `sum z_j<=B`; do not conflate these semantics
- A specified prehistory may reduce initial window budgets. The LP remains integral when the resulting right-hand sides are integral; the simple uniform-capacity flow construction above then needs the appropriate boundary adaptation
- Fixed continuous plant uncertainty stays outside the conditional LP; refreshing it between lag rewards changes the problem
- Exact LP integrality is valid for real costs, but bit-complexity/runtime claims require rational cost encoding or certified numerical evaluation of the trigonometric weights
- With a geometric tail, `N=O(log(1/epsilon))` suffices for an approximate scalar support query at fixed contraction. This does not bound the number of facets needed to represent the entire capacity domain
- Arbitrary extra automaton, work-completion, multiport, or other coupling constraints do not inherit this TU result automatically

**Revised novelty conclusion:** a single bounded-disagreement sliding-window contract admits a mature polynomial-size, same-information exact LP/min-cost-flow baseline. Demonstrating improvement over exponential suffix-state enumeration alone would not demonstrate a new algorithmic advantage.
