# Independent adversarial review of G4 workload theorems

Date: 2026-10-04 UTC. This review independently reconstructs the arguments and small models rather than assuming the producer's theorems or certificates are valid. No producer theory or experiment source was modified.

Reviewed theory snapshot: `theory/THEOREMS.md`, SHA-256 `6bbf81c7c3aaf79f5142af4e61667a4358abdefae3969ce6e465da26db10cafe`.

## Verdict

**No counterexample or proof gap found in T1–T6, T1a, and T5a under their stated mathematical contracts.** T1's nonstationary infinite-horizon reduction and its stronger additive-width lower bound survive independent scrutiny. T2 uses the correct slot-position graph, and T3 follows from it. T4 correctly delineates correlated histories. T5's invariant-hull test is exact for the stated discrete retained-state model, and T5a correctly extends its design-capacity optimum to nonstationary common schedules. T6's leakage threshold is correct for endpoint invariance in the full output cube.

One genuine formulation defect was identified in the first draft and is already fixed: an arbitrary compact convex action set need not give an LP. The current primary polytope formulation and separate convex-program extension are correct.

Independent validation now covers **89 producer primal/dual certificates**, rebuilt from the original DAGs using exact rational arithmetic, and all pass. This is exact validation of those finite models, not a formal proof of the general theorems, evidence of algorithmic novelty, or a continuous-time battery certificate.

## 1. T1: quantifiers and the strengthened lower bound

The proof's potentially delicate steps are valid:

1. Independence means each finite history attaining the lower or upper boundary can be combined with **every** present word. It is not necessary that every intermediate value in the reachable hull is itself reachable. The endpoints suffice because prefix energy depends monotonically and affinely on initial energy.
2. The same current word can be appended to the upper history. Subtracting the accumulated width therefore really gives `l_b + g_sigma,j <= B - W_(b-1)` for every prefix, not merely an endpoint inequality.
3. The affine prefix functions include their constants. Thus averaging public blocks and lower-boundary values preserves every prefix inequality exactly.
4. Compactness and convexity keep the averaged public action admissible and supply one common convergent subsequence. There are finitely many words/prefixes, so all constraints survive on that same subsequence.
5. A fixed-word repeated history is allowed, and its bounded endpoint energy forces the corresponding averaged residual to zero. No recovery condition has been covertly imposed on the original schedule.
6. `W_m` is nondecreasing and bounded by B, so the average of `W_(b-1)` tends to `W_infinity`. Including prefix zero guarantees the limiting initial state lies in the resulting reduced capacity interval.
7. The limit gives an exact-reset solution of capacity `B - W_infinity`; that is the claimed stronger inequality. If the reset problem is infeasible, the argument rules out a finite-capacity infinite schedule.
8. The converse is physical repetition of an exact-reset block. It is valid within the supplied action contract, with one common free initial state.

There is no mismatch between a history-specific endpoint argument and a universally feasible common schedule. The one-block initial state found by averaging may differ from the original initial state; this is permitted because both optimization problems allow a free common initial state.

### Exact positive-width equality witness

Take `L=1`, `H=3`, `delta=1`, `eta_c=eta_d=1/2`, `S={LH,HL}`, and the full public box. The reset optimum is `q=13/5` and `B*=8/5`.

Use first public block `(14/5,12/5)`, every subsequent public block `(13/5,13/5)`, common initial state `11/10`, and capacity `11/5`.

All first-block physical states, including both boundaries, are:

- LH: `11/10 -> 2 -> 4/5`
- HL: `11/10 -> 7/10 -> 7/5`

The first residuals are `-3/10` and `3/10`. Every subsequent residual is zero. Thus the boundary hull forever after the first block is `[4/5,7/5]`, of width `3/5`.

Every possible subsequent block has one of these four state paths:

- Start `4/5`, LH: `4/5 -> 8/5 -> 4/5`
- Start `4/5`, HL: `4/5 -> 0 -> 4/5`
- Start `7/5`, LH: `7/5 -> 11/5 -> 7/5`
- Start `7/5`, HL: `7/5 -> 3/5 -> 7/5`

Consequently `B=11/5 = 8/5 + 3/5 = B* + W_infinity`. The stronger bound is sharp for at least a nonzero-width example, not just at width zero. This does not assert equality for every prescribed width or every action set.

### Exact infeasible-reset example

For the same two words and efficiencies, restrict the public set to the singleton `(1,3)`. LH has residual zero; HL has residual `-3`. No exact-reset universal block exists, and the optimum M-block capacity is exactly `3M+1`. This agrees with T1's infinite infeasibility conclusion and cautions against interpreting any finite-horizon optimum as an infinite-horizon construction.

### T1a: finite-horizon convergence

T1a's monotonicity, upper bound, and convergence are correct, including divergence when the reset problem is infeasible. The horizon-specific schedules and initial states do not have to be consistent truncations of one infinite construction. Independently average each K-block design: the repeated-word history gives `|r_sigma(pbar_K)| <= B_K/K`; the averaged prefix constraints remain bounded by `B_K` after dropping the nonnegative width correction. If capacities have a bounded limit below `B*`, one compact subsequence produces an exact-reset solution below `B*`, a contradiction. No convergence rate follows, as the text properly states.

## 2. T2 and T3: the correct graph and DAG capacities

T2 is valid. Opposite-label adjacent incomparable swaps impose equality of the two affected slot outputs because the strict-loss coefficient is nonzero. Connectivity of the task linear-extension graph then proves sufficiency, including paths containing same-label swaps. Graph vertices must remain **slot positions**, not tasks or extensions. A connected extension graph does not imply a connected slot graph.

I exhaustively tested every natural-order-edge DAG on 2–4 tasks and every mixed binary task labeling: 74 DAG edge sets and 948 DAG/label cases. Exact rational row ranks of all word-residual differences equal the number of slot-graph edges in every case. Every residual difference has zero sum within each slot component. This checks the whole equality space, not only a candidate feasible output.

All 168 connected cases additionally match T3's prefix-count formula against a separately implemented scenario LP. A minimal strict-improvement example occurs with four tasks, two highs and two lows, and one opposite-label precedence constraint; the slot graph remains connected and capacity falls from `16/5` to `12/5` at the small-test parameters.

**Interpretation:** comparing an antichain contract with a restricted DAG changes the admissible workload language. It is a valid workload-contract ablation, but is not an algorithmic improvement over the same robust scenario problem. The genuinely matched comparison is scenario LP versus graph-derived LP using identical words, initial-state policy, efficiencies, output constraints, and horizon. The saved experiments make that comparison and agree.

The formula is explicit, but enumeration of words or prefix extrema may still be expensive. Neither the formula nor the finite LP alone establishes a new polynomial-time algorithm for arbitrary DAGs.

## 3. T4: correlated histories

The cycle/potential characterization is correct for a finite strongly connected graph, one known starting node, and one fixed repeated public block. A reachable repeatable nonzero cycle gives unbounded energy. Conversely, zero cycle sums force path-independent node potentials, and edge-prefix extrema give exactly the required capacity after one common shift.

An exact check uses A-to-B word LH and B-to-A word HL, public block `(14/5,12/5)`, and the small-test parameters above. Residuals are `-3/10` and `3/10`, potentials are `v(A)=0`, `v(B)=-3/10`, capacity is `8/5`, and common initial state at A is `7/10`. Physical states cycle as:

`7/10 -> 8/5 -> 2/5 -> 0 -> 7/10`.

The per-word residual range is positive every block, but the history restrictions prevent independent accumulation. Applying T1's width sum to this correlated system would incorrectly make it infinite. The theorem properly does not do so.

The potential characterization is a standard conservation fact, not evidence of a new graph theorem. Unknown/multiple initial automaton nodes and nonrepeated public blocks need separate formulations, as the draft acknowledges.

## 4. T5: discrete leakage and the invariant LP

The exact scalar endpoint hull recursion, stationary hull, and prefix criterion are valid. Necessity follows by convergence of the lower and upper reachable endpoints. Sufficiency follows because any common singleton initial state in the stationary hull remains inside the invariant hull for every sequence.

The invariant-interval LP is nonconservative. Its endpoint inequalities imply `l <= min(r)/(1-a)` and `u >= max(r)/(1-a)`, so any feasible invariant interval contains the stationary hull. Replacing it by that hull can only improve all prefix box inequalities. This is a useful explicit justification of the final optimization sentence.

Exact example: take `rho=9/10`, both public outputs `27/10`, and the small-test two-word parameters. The residuals are `33/200` and `31/100`; the stationary interval is `[33/38,31/19]`; its width is `29/38`. The maximum prefix state is `881/380`, and the minimum of the stationary prefix lower bounds is `69/380`. This gives a feasible positive-width leaky construction.

Independent tests compare the invariant LP with direct stationary-hull calculations at 169 fixed output pairs. All 8 feasible and 161 infeasible classifications match, including capacity values in the feasible cases. Exact rational propagation for 100 blocks from the lower endpoint, midpoint, and upper endpoint stays within the certified capacity in the explicit example.

**Scope:** these are discrete retained-state checks. They do not validate a continuous leakage ODE, subslot extrema, battery electrochemistry, charging/discharging rates, or an energy benefit from leakage. The current continuous-time warning is appropriate.

### T5a: nonstationary leaky schedules

The final T5a correctly extends the leaky invariant LP optimum to arbitrary nonstationary common public block schedules under the same fixed convex public set and independent word choices. I proposed and independently checked this extension during the review, then checked its saved proof. Its free-common-initial-state qualification is important and correct.

For a feasible schedule let `l_b,u_b` be its exact boundary hull and let `a=rho^N`. For every word,

`l_(b+1) <= a l_b + r_sigma(p_b)` and `u_(b+1) >= a u_b + r_sigma(p_b)`.

Average these and the prefix box inequalities. The averages of consecutive lower/upper endpoints differ by bounded endpoint telescoping terms divided by M, hence tend to zero. Along one compact subsequence the averaged variables converge to `(p,l,u)`. Affinity yields all invariant-interval LP inequalities:

`(1-a)l <= r_sigma(p)`, `(1-a)u >= r_sigma(p)`, and `0 <= rho^j l+g_sigma,j(p) <= rho^j u+g_sigma,j(p) <= B` in their respective lower/upper forms.

Therefore any feasible nonstationary schedule gives a feasible stationary invariant LP solution at no greater capacity. Conversely, repeat the invariant LP action and choose a common initial state in its interval. This argument uses no nonlinear averaging of the min/max functions; it averages their individual scenario inequalities.

## 5. T6: leakage threshold

The weighted-swap derivation is correct when `1 <= k <= N-1`. Every pair of positions can exchange a high/low membership within a fixed-cardinality subset. Thus all weighted F values must coincide, and that is also sufficient.

Because F is strictly decreasing and positive on the public cube, the common-C intervals intersect exactly when `eta_c eta_d <= rho^(N-1)`. At equality the intersection is a singleton and the resulting geometric output touches the public bounds at its ends. The output is increasing with slot position under the given indexing.

Independent checks cover 90 `(N,k,eta,rho)` instances with N from 2 to 6. An independently built scenario endpoint-equality LP matches the threshold in every case; all predicted-feasible cases additionally have an exact Fraction witness whose endpoint residual is identical for every word.

This is a feasibility threshold for endpoint invariance in `[L,H]^N`. Additional restrictions in P can invalidate a cube-feasible output. Even when the threshold holds, nonnegative invariant energy, capacity, power/ramp feasibility, and continuous-time feasibility remain separate. The current disclaimer correctly prevents those overclaims.

## 6. Exact assumption-failure examples

These are **not** counterexamples to the stated theorems. They show that key restrictions cannot silently be dropped.

### Nonconvex public set breaks T1's reset reduction

With `S={LH,HL}` and the small-test parameters, use the nonconvex public set `{(5/2,5/2),(27/10,27/10)}`. Each first action has common residual `-1/4`; each second action has common residual `1/4`. Neither action exactly resets, so `B*=infinity` for this set. Nevertheless, alternating the two actions works indefinitely with common initial state 1 and capacity `7/4`.

First-block states are `1 -> 7/4 -> 3/4` or `1 -> 0 -> 3/4`; second-block states are `3/4 -> 8/5 -> 1` or `3/4 -> 3/20 -> 1`. Convexifying the action set restores access to `(13/5,13/5)` and removes the contradiction.

### A private initial state invalidates the stronger width bound

Use first public block `(12/5,14/5)` followed by the reset block `(13/5,13/5)`. Allow initial energy to depend on the first private word: `3/5` for LH and `6/5` for HL. First states are respectively `3/5 -> 13/10 -> 9/10` and `6/5 -> 0 -> 9/10`. Thereafter every history starts each block at `9/10` and stays within `[1/10,17/10]`.

This gives capacity `17/10`, less than `B*+W_infinity=11/5`. It violates only the common-initial-state requirement. This is a concrete matched-information warning for any comparison allowing workload-informed precharging.

### Cross-block waveform constraints need explicit inclusion

Within-block ramp restrictions alone do not certify the last-to-first transition of a repeated block. If hardware requires a cyclic step or ramp limit, include the wraparound constraint in P or validate that transition separately. The theorem's converse is otherwise valid only for its stated action set. The draft's extra-waveform-limits disclaimer and cyclic PCC-step ablations are the right treatment.

## 7. Independent producer-certificate audit

The separate checker imports no producer code. It independently enumerates task-identity topological extensions, deduplicates label words, reconstructs adjacent-swap boundaries, checks exact physical prefix energies and reset, and reconstructs the sparse dual against a new Fraction-only scenario model. Dual signs, stationarity, objective, primal feasibility, and zero duality gap are all checked exactly.

All **77 primary DAG cases plus 12 public-pattern synthetic-power cases pass**. At `L=6`, `H=18`, `delta=1`, `eta_c=eta_d=19/20`, the requested worked results are:

| Workload contract | Distinct words | Task extensions | Exact capacity | Exact common initial state |
|---|---:|---:|---:|---:|
| Antichain six-task | 15 | 720 | 6080/187 | 3040/187 |
| Connected restricted six-task | 9 | 24 | 3800/187 | 1520/187 |
| Two three-task barriers | 9 | 36 | 3040/187 | 1520/187 |

All three have exact public output `1922/187` in each slot and attain physical prefix energies 0 and B. The disconnected barrier case's optimality is independently certified by its dual; it is not being inferred from the connected-graph T3 formula.

The 12 public-pattern cases are synthetic power-label models of graph shapes, not measured power traces or validated platform behavior. Coincident projected word languages do not constitute independent power workloads and should remain disclosed.

## Reproduction artifacts

- `independent_theory_checks.py`, `.json`, `.log`: 23 fixed-count tiny word families at four finite horizons; exact T1 positive-width and assumption-failure witnesses; 948 graph equality-space checks; 168 T3 LP comparisons; T4 rational cycle; T5 rational and 169-point grid checks
- `independent_t6_threshold_check.py`, `.json`, `.log`: 90 threshold/scenario comparisons and exact feasible witnesses
- `independent_saved_certificate_check.py`, `.json`, `.log`: independent 89-case exact primal/dual audit, with source-file SHA-256 values

Run each Python script directly from the repository workspace. Numeric LP comparisons are labeled as numerical; the certificate and explicit rational-witness checks use exact arithmetic. This review does not certify literature priority, novelty of the standard robust LP, or real hardware efficacy.
