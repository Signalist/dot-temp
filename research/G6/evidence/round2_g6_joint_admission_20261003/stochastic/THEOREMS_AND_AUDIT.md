# G6 C2: lifetime joint chance admission, startup caveats, and finite missions

Date: 2026-10-03. Scope: exact finite-dimensional conditional LTI models, not field calibration. All computations use original code and exact integer/rational arithmetic. The experiment cases were frozen before results in `FROZEN_STOCHASTIC_PROTOCOL.json`.

## Bottom line

For the zero-start common-sign model

\[
x_{k+1}=Ax_k+s_kBa,\quad x_0=0,\quad s_k\in\{-1,+1\},\quad \rho(A)<1,
\]

with iid positive sign probabilities or a time-homogeneous Markov sign chain having every transition positive, define

\[
\gamma_i(a)=\sum_{j=0}^\infty |c_iA^jBa|,\qquad \Gamma(a)=\max_i\gamma_i(a).
\]

Then, including equality as safe,

\[
\Pr\{ |c_ix_k|\le1\text{ for every }i,k\}=\begin{cases}1,&\Gamma(a)\le1,\\0,&\Gamma(a)>1.\end{cases}
\]

Consequently every lifetime joint chance set with risk budget \(0\le\delta<1\) equals the robust support admission set \(\{a:\Gamma(a)\le1\}\). Mode probabilities change waiting times, not this lifetime admission boundary. This is a useful quantifier correction, but not a new ergodic or support theorem.

There is a fully explicit forcing-word finite-mission bound, an optional sharpened outer-convergence corollary, and exact independent validation below. The sharpened corollary is a conservative combination of standard support-tail and pattern-waiting arguments. This audit does **not** identify a defensible high-novelty stochastic theorem beyond those ingredients.

## 1. Assumptions and the exact safety event

Fix one allocation \(a\); its input vectors are fixed throughout the mission. Modes are exogenous, not a schedule chosen to avoid unsafe words. Outputs have already been normalized by their positive safety thresholds. Mission safety is

\[
S_N(a)=\Pr\{x_k\in\mathcal S,\;k=0,\ldots,N\},\qquad
\mathcal S=\{x:|c_ix|\le1\ \forall i\},
\]

and lifetime safety is \(S_\infty=\lim_NS_N\). Here \(N\) counts **block updates**, with the electrical state carried between blocks.

If \(c_ix_k\) only measures a block endpoint, this certifies endpoints only. Continuous-time or within-block safety requires adding all relevant within-block output functionals, including any dependence on the current block mode and direct feedthrough. It is invalid to infer full within-block safety from a single boundary sample. The same forcing-word logic applies to a strictly unsafe finite block trajectory once that trajectory is represented in the actual safety event; the simple displayed support formula may need additional rows or current-mode maximization.

The Markov assumption here is \(P_{st}>0\) for all symbol pairs, not merely irreducibility. The starting previous mode can be fixed. If only the first-symbol distribution is specified, a lower-bound calculation can include that distribution, or skip its first symbol before starting uniform trials. A full-support stationary ergodic process also gives qualitative word recurrence, but need not give the quantitative uniform bounds used here. Unconditional positivity of all finite-word probabilities, by itself, is insufficient for the quantitative argument or for recurrence in a nonergodic/time-inhomogeneous process.

## 2. General stable affine-system theorem

Consider \(x_{k+1}=Ax_k+b_{s_k}\), with finitely many \(b_s\), common Schur-stable \(A\), and a closed convex safe set \(\mathcal S\). Define the compact attractor

\[
K=\left\{\sum_{j=0}^\infty A^jb_{v_j}:v_j\text{ any alphabet symbols}\right\},\qquad Z=\operatorname{conv}K.
\]

Every infinite series converges uniformly over symbol sequences. The affine maps obey \(AK+b_s\subseteq K\) and \(AZ+b_s\subseteq Z\). For iid positive probabilities, \(K\) is the support of the stationary state law. With positive Markov transitions, the union of conditional stationary state supports is the same full-word attractor.

**Theorem 1 (correct startup-qualified collapse).** Suppose every fixed finite word has a strictly positive lower bound on its conditional probability at every trial time. This includes the specified iid and positive-transition finite Markov models.

1. If \(K\not\subseteq\mathcal S\), then lifetime survival is zero from every fixed initial state.
2. If \(K\subseteq\mathcal S\) and \(x_0\in Z\), then every admissible mode sequence is safe, so lifetime survival is one.
3. Thus for \(x_0\in Z\), lifetime chance admission with \(\delta<1\) equals robust attractor inclusion. Without the startup condition, conclusion 2 is false.

**Proof of 1.** Choose \(z\in K\setminus\mathcal S\). Since \(\mathcal S\) is closed, there is an \(\epsilon>0\) such that the ball of radius \(\epsilon\) about \(z\) is unsafe. All trajectories from the fixed initial state lie in a bounded ball, say \(\|x_k\|\le M\), because \(A\) is Schur stable and the inputs are bounded. Write \(z=\sum_{j\ge0}A^jb_{v_j}\), and let \(z_L\) be its first \(L\) terms. Use the chronological word \(w=(v_{L-1},\ldots,v_0)\). Its endpoint from any reachable state \(x\) is \(A^Lx+z_L\). Choose \(L\) so that

\[
\|A^L\|M+\max_s\|b_s\|\sum_{j\ge L}\|A^j\|<\epsilon.
\]

Every occurrence of this word forces an unsafe endpoint. If its conditional probability is at least \(q>0\), then conditional multiplication on disjoint length-\(L\) trials gives \(S_N\le(1-q)^{\lfloor N/L\rfloor}\), with the initial-symbol convention from Section 1. Letting \(N\to\infty\) proves the claim. The same argument after any deterministic time shows strict violations recur infinitely often almost surely. No independence between trial successes is needed.

**Proof of 2.** Convexity gives \(Z\subseteq\mathcal S\). Each affine mode maps \(Z\) into itself. Induction from \(x_0\in Z\) proves robust safety.

The attractor/support construction is classical [Hutchinson 1981](https://doi.org/10.1512/iumj.1981.30.30055). The qualitative recurrence conclusion is an elementary special case of classical contractive-system ergodic results; [Elton 1987](https://doi.org/10.1017/S0143385700004168) is directly relevant prior art. The finite forcing-word proof is included to expose startup assumptions and produce numerical bounds, not to claim a new recurrence principle.

## 3. Specialization to common signs and joint admissions

Put \(v=Ba\) and \(b_\pm=\pm v\). The attractor is centrally symmetric, so \(0\in Z\), even when \(0\notin K\). Its convex hull is the infinite Minkowski sum

\[
Z=\sum_{j\ge0}[-A^jv,A^jv],
\]

with support \(h_Z(c_i)=\gamma_i(a)\). Therefore \(K\subseteq\mathcal S\) iff \(\Gamma(a)\le1\), and Theorem 1 proves the stated exact collapse.

For \(\Gamma\le1\), the direct finite-time proof is particularly simple:

\[
|c_ix_k|\le\sum_{j=0}^{k-1}|c_iA^jBa|\le\gamma_i(a)\le1.
\]

This includes the boundary \(\Gamma=1\); no zero-measure or strict-interior assumption is needed. If \(\Gamma>1\), a strict violation exists with a finite support truncation and a sufficiently long forcing word.

The summand is \(|c_iA^jBa|\), with the joint port contributions added **inside** the absolute value. Replacing it by \(\sum_\ell |c_iA^jB_\ell|a_\ell\), for nonnegative allocations, replaces common signs by independent port signs and can enlarge the uncertainty set. That is a different information model, not a probabilistic improvement or a competing solver on the same problem.

## 4. Explicit washout word and finite-mission bounds

For a row with \(\gamma=\gamma_i(a)>1\), define

\[
H_L=\sum_{j=0}^{L-1}|c_iA^jv|,\qquad
T_L=\sum_{j=L}^\infty|c_iA^jv|,\qquad \gamma=H_L+T_L.
\]

Choose a chronological word with

\[
w_{L-1-j}=\operatorname{sign}(c_iA^jv),\quad 0\le j<L,
\]

choosing either sign at a zero coefficient. For any \(x\in Z\),

\[
c_i(A^Lx+\sum_{j=0}^{L-1}A^jw_{L-1-j}v)
\ge H_L-h_Z(c_iA^L)=H_L-T_L=\gamma-2T_L.
\]

Hence **\(H_L-T_L>1\)** is a directly checkable uniform forcing certificate. The negative word forces the opposite violation. In floating computations, replacing \(T_L\) by a valid analytical upper bound gives a sufficient certificate. A numerical tail estimate without outward rounding is not automatically a proof.

For \(A=rR_\theta\),

\[
T_L\le \|c_i\|_2\|Ba\|_2\frac{r^L}{1-r}.
\]

It is enough to check \(H_L-\|c_i\|\|Ba\|r^L/(1-r)>1\). This combines construction and washout; it never assumes a state reset.

For iid signs with \(\Pr(+)=p\), a fixed word with \(n_+\) plus and \(n_-\) minus symbols has probability \(q_w=p^{n_+}(1-p)^{n_-}\). If both \(w,-w\) are used, their disjoint word probabilities add. For a Markov chain, a uniform single-word lower bound is

\[
q_w=\min_t P_{t,w_0}\prod_{j=1}^{L-1}P_{w_{j-1},w_j}>0.
\]

For a same-length family \(W\) of forcing words, the sharper lower bound is

\[
q_W=\min_t\sum_{w\in W}P_{t,w_0}\prod_{j=1}^{L-1}P_{w_{j-1},w_j}.
\]

Include the first-word probability in the minimum if no preceding mode is specified. Then

\[
S_N(a)\le(1-q_W)^{\lfloor N/L\rfloor},\qquad
\Pr\{\text{some violation by }N\}\ge1-(1-q_W)^{\lfloor N/L\rfloor}.
\]

These are **lower bounds on failure**, useful for rejecting an allocation. They do not certify small failure risk. Exact weighted pattern-avoidance computation gives a stronger upper bound on survival for a selected forcing-word family. It is exact for physical safety only when that family is proved to characterize every unsafe path, as in Section 7.

## 5. Optional sharpened mission-to-admission outer bound

The following corollary removes an avoidable logarithmic factor from the disjoint-trial argument. It is useful but is not claimed as new probability theory.

Assume uniformly over allocation directions and the relevant output rows that

\[
T_L(a)\le K\rho^L\gamma_i(a),\qquad K\ge1,\quad0<\rho<1.
\]

Assume the conditional probability of each sign, given the past, is between \(p_{\min}>0\) and \(p_{\max}<1\). For iid signs these are the smaller/larger sign probabilities; for Markov signs use the smallest/largest transition entries, with a preceding mode specified. An unrestricted first symbol costs only an extra update.

For any chosen word of length \(L\), consider a deliberately simple matching procedure: start matching the word, discard an attempt at its first mismatch, and start a fresh attempt on the next symbol. Each attempt succeeds with conditional probability at least \(p_{\min}^L\), and its expected length, conditional on starting, is at most

\[
\sum_{j=0}^{L-1}p_{\max}^j\le\frac1{1-p_{\max}}.
\]

The probability that attempt \(m\) is started is at most \((1-p_{\min}^L)^{m-1}\). Summing expected attempt lengths yields

\[
\mathbb E\tau_w\le\frac1{(1-p_{\max})p_{\min}^L}.
\]

The actual first word occurrence is no later than the completion time of this wasteful procedure. If the word forces failure, the first failure time \(T\) is no later still.

Let \(\gamma=\Gamma(a)>1\), \(\eta=(\gamma-1)/(2\gamma)\), and

\[
\alpha=\frac{\log p_{\min}}{\log\rho}>0.
\]

Choose \(L=\lfloor\log(\eta/K)/\log\rho\rfloor+1\), ensuring \(K\rho^L<\eta\) and \(p_{\min}^L\ge p_{\min}(\eta/K)^\alpha\). Therefore

\[
S_N(a)=\Pr(T>N)
\le \frac{K^\alpha}{(1-p_{\max})p_{\min}\,N\,\eta^\alpha}.
\]

If \(S_N(a)\ge1-\delta\), define

\[
d_N=K\left[(1-p_{\max})p_{\min}(1-\delta)N\right]^{-1/\alpha}.
\]

Whenever \(d_N<1/2\), it follows that

\[
\Gamma(a)\le\frac1{1-2d_N}.
\]

Thus the finite-mission chance region is sandwiched between the robust set and a support-gauge inflation of order \(N^{-1/\alpha}\), for fixed \(\delta<1\). This is a conservative upper rate, not an exact universal exponent or a sharp constant. Its constants can be extremely weak for rare transitions or poorly observable directions.

For \(A=rR_\theta\), \(c=(1,0)\), and \(\sin\theta\ne0\), one explicit choice follows from

\[
O=\begin{pmatrix}1&0\\r\cos\theta&-r\sin\theta\end{pmatrix},\quad
\gamma(v)\ge\|Ov\|_1\ge\sigma_{\min}(O)\|v\|_2.
\]

One may take \(\rho=r\) and \(K=[(1-r)\sigma_{\min}(O)]^{-1}\). If \(\sin\theta=0\), the observed scalar subspace instead has the exact identity \(T_L=r^L\gamma\), so \(K=1\). The generic two-dimensional constant should not be used at its singular angle.

Pattern occurrence and overlap-aware avoidance are classical subjects; [Guibas–Odlyzko 1981](https://doi.org/10.1016/0097-3165(81)90005-4) is a central primary source. The displayed rate packages these ideas with a support-tail bound; this audit does not establish novelty of that packaging.

## 6. Arbitrary startup: exact counterexample and strict-interior reduction

The startup caveat holds even in the principal rotation family. Set

\[
A=\tfrac12 R_{\pi/2},\quad v=(\tfrac14,0)^T,\quad c=(1,0),\quad x_0=(0,-2)^T.
\]

The attractor support is \(\gamma=\frac{1/4}{1-1/4}=1/3<1\), and the initial measured output is zero. But

\[
cx_1=1+s_0/4,
\]

so the first plus sign causes \(1.25>1\), while a minus sign gives \(0.75\). For \(k\ge2\), all possible outputs are safe: the initial contribution is zero at even times and has magnitude at most \(1/4\) at odd times \(k\ge3\), while the forced contribution is at most \(1/3\). Thus lifetime survival equals \(\Pr(s_0=-1)\), exactly \(1/2\) for fair signs. A safe attractor alone does not make survival one or force all nonrobust startup risks to recur.

More generally, suppose \(K\) has strictly positive distance \(\varepsilon\) from the unsafe region. Pick a closest \(z_0\in K\) and evolve it with the same symbols. Then

\[
\|x_n-z_n\|\le\|A^n\|\operatorname{dist}(x_0,K),\qquad z_n\in K.
\]

Choose \(n_0\) so that the right side is less than \(\varepsilon\) for every \(n\ge n_0\). Every trajectory is safe after \(n_0\), regardless of its earlier history. Lifetime survival is exactly a finite-prefix survival probability. If \(K\) merely touches the safety boundary, there need not be a uniform finite washout time, so this finite-prefix reduction must not be asserted without a margin.

## 7. Exact scalar validation: unsafe paths equal forbidden runs

Freeze \(L\in\{2,3,4\}\), put

\[
g_L=\frac{2^{L-1}}{2^{L-1}-1},\quad x_{k+1}=\tfrac12x_k+\tfrac12g_Ls_k,\quad x_0=0,
\]

and retain safety \(|x_k|\le1\). Write \(y=x/g_L\), so the normalized threshold is \(t_L=1-2^{1-L}\).

**Proposition 2.** A finite trajectory first violates safety exactly when it first contains \(L\) equal consecutive signs.

**Proof.** If the terminal run has length \(h\), then for a positive run

\[
y_k=1-2^{-h}+2^{-h}y_{k-h}.
\]

If \(h=k\), the last term is zero. Otherwise the preceding sign was negative, and the finite zero-start recursion has \(-1<y_{k-h}<0\). Hence any positive run of length at least \(L\) gives \(y_k>1-2^{1-L}\); if \(h<L\), then \(y_k\le1-2^{-h}\le1-2^{1-L}\). The negative case follows by symmetry. For an initial run of exactly \(L-1\), equality occurs and remains safe. This distinguishes non-strict safety from an incorrect boundary rejection.

The two independent computations are:

1. Enumerate every finite sign prefix through depth 16, using the exact integer state numerator \(y_n=m_n/2^n\) and \(m_{n+1}=m_n+s_n2^n\). Decide safety by cross multiplication; no pattern assumption enters this numeric safety calculation.
2. Propagate exact integer probability weights through an automaton with states `(last sign, current run length)` and discard a transition reaching run length \(L\).

The cases are fair iid signs; iid \(\Pr(+)=7/10\); and Markov transition matrix, in order \((-,+)\),

\[
P=\begin{pmatrix}4/5&1/5\\3/10&7/10\end{pmatrix},\qquad \alpha_0=(2/5,3/5).
\]

All 1,179,630 path prefixes agree, with zero classification mismatches and 18 exact boundary equalities checked. All weighted survival probabilities agree exactly through horizon 16. Automaton values at 20, 50, 100, and 1000 are exact rational calculations; they were not exhaustively enumerated at those larger horizons.

Selected results for \(L=3\), \(g=4/3\):

| Sign process | N=10 | N=20 | N=100 | N=1000 |
|---|---:|---:|---:|---:|
| Fair iid | 0.173828125 | 0.0208778381 | 9.04268e-10 | 1.31274e-92 |
| Biased iid | 0.0920043306 | 0.0053785340 | 7.35438e-13 | 7.85765e-124 |
| Persistent Markov | 0.0093938688 | 0.0000326566 | 7.25794e-25 | 5.80462e-246 |

The fair iid \(N=100\) disjoint-word survival upper bound is 7.53393e-5, valid but much looser than the exact 9.04268e-10. This gap is overlap/temporal structure, not a changed uncertainty set. The full exact fractions, cases, word bounds, and source/protocol hashes are in `RESULTS.json`; `FINITE_MISSION_SUMMARY.csv` is convenient for plotting.

At fair \(r=1/2\), the stationary normalized state is uniform on \([-1,1]\). Thus for \(g=4/3\), stationary per-time failure probability is only \(1/4\), while eventual failure probability is one. More generally, for \(g_L\), the stationary per-time failure probability is \(2^{1-L}\), which can be made arbitrarily small without changing eventual failure from one. This is precisely why per-time, single-block, finite-mission joint, and lifetime joint chance constraints must not be interchanged.

## 8. Endpoint tail exponent is known, and is not a universal pure-power law

For the stationary scalar recursion

\[
Y_{k+1}=rY_k+(1-r)s_k,\quad \Pr(s_k=+1)=p,
\]

let \(D=1-Y=2(1-r)\sum_{j\ge0}r^j\mathbf1_{s_j=-1}\). A sufficiently long initial string of plus signs ensures \(D\le\epsilon\). Conversely, when \(\epsilon\) is small, any minus among sufficiently many early digits prevents \(D\le\epsilon\). These necessary and sufficient string lengths both equal \(\log\epsilon/\log r+O(1)\). Consequently

\[
\lim_{\epsilon\downarrow0}\frac{\log\Pr(D\le\epsilon)}{\log\epsilon}=\frac{\log p}{\log r}.
\]

This is the endpoint local dimension of a Bernoulli convolution, not a new G6 exponent. Theorem 4.3's proof in [Hare–Hare–Ng 2018](https://doi.org/10.4153/CJM-2017-025-6) explicitly treats the corresponding endpoint formula as standard. The exponent alone does not justify a constant-prefactor asymptotic \(C\epsilon^\alpha\); oscillatory/log-periodic behavior can matter.

A particularly relevant recent primary source is [Kern–Sterk, arXiv:2608.14155](https://arxiv.org/abs/2608.14155), submitted 14 August 2026, which studies AR(1) Bernoulli-convolution stationary laws, log-periodic endpoint structure, and uniform convergence of normalized-maxima distributions. The verified abstract establishes close prior-art territory; this audit does not assert that it proves the exact multidimensional support-gauge corollary above.

## 9. Physical interpretation and stop decision

A task block can have exactly zero **incremental** net power energy, \(\int_0^{T_b}\Delta P(t)dt=0\), while still exciting a carried LTI electrical state. This needs no storage device and creates no energy. Negative incremental power can mean consumption below a positive baseline. An actual feasibility claim must still check nonnegative total consumption and any power/ramp limits.

Equal net incremental electrical energy implies equal baseline work only under an explicitly supplied affine relation between work rate and power (with the relevant coefficients fixed over the comparison), or another separately proved workload identity. No such relation should be inferred from zero energy alone. These models and examples are not data calibration, network identification, nonlinear-grid validation, or a physical deployment certificate.

**C2 audit verdict:** retain the exact collapse theorem as a correctly qualified structural result; retain finite forcing-word bounds and exact pattern calculations as constructive mission-risk tools; retain the startup counterexample as a required limitation. Do not present invariant-support recurrence, Bernoulli endpoint dimension, classical pattern avoidance, or the conservative rate assembly as established new research. No high-innovation stochastic result survived this bounded audit.
