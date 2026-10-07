# G6 theory-review assumptions (frozen before numerical illustrations)

1. Fix `0 < r < 1`, a real angle `theta`, the conventional counterclockwise rotation `R_theta`, scalar output `C=(1,0)`, and initial deviation state `x_0=0`.
2. The sampled plant is `x_{k+1}=r R_theta x_k+s_k b_k`, with one common block mode `s_k in {-1,+1}`. The plant state is carried between blocks; it is never reset.
3. Three distinct workload contracts are considered separately:
   - fixed cohort: `b_k=a` for all k;
   - optional fixed cohort: choose one `b in [0,a]` and hold it fixed for all k;
   - dynamic optional amplitude: independently choose `b_k in [0,a]` in every block, retaining the common sign.
4. `a=(a_1,a_2)>=0`. The safety requirement in the discrete theorems is `|C x_k|<=1` for every finite k and every admissible sequence. It is a sampled-state requirement. No continuous-time safety claim is inferred from it.
5. The main nonpolyhedral and approximation results assume `alpha=theta/pi` irrational. Rational formulas are separately stated. The exact common-input matrix is `B=I`; the physical realization constructs fixed templates giving this matrix rather than silently changing capacity coordinates.
6. Approximation complexity counts non-axis halfspaces of a convex admission polyhedron, or affine pieces of its gauge on a fixed compact positive slope interval `J=[l,u]`, `0<l<u<infinity`. Accuracy is uniform additive gauge error or the equivalent local slope-radial error. Constants may depend on `r,theta,J`; they do not depend on accuracy.
7. The arithmetic invariant is `beta(alpha)=limsup_{q->infinity} log(1/||q alpha||_Z)/q`, with values in `[0,infinity]`.
8. Continuous physical templates are bounded and exactly zero-area, not impulsive. Every block has fixed positive baseline energy. Identical work is asserted only under an explicit constant energy-per-work model. No task-side energy storage or ideal state reset is used.
9. Numerical checks are illustrations and implementation tests; proofs carry the conclusions. Literature novelty is not inferred from an unsuccessful search.
