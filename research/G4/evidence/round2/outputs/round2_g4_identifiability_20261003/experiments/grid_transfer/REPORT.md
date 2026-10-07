# G4: source-bus distinguishability through qualified grid measurements

## Bottom line

This is mathematical and synthetic benchmark evidence, not inference of an AI workload or a real synchronized-data study.

Under a prospectively frozen P-only, one-active-source, unknown-amplitude/phase model, every tested single scalar harmonic channel is ambiguous between the configured buses. Every tested two-channel signature is non-collinear, but its conditioning and bounded-error separation differ substantially by frequency, grid, and sensor type. If independent unknown P and Q amplitudes are allowed at the candidate source, both source locations fill the entire one-/two-channel observation space in every tested configuration: the P-only localization conclusion disappears.

Known zero initial grid state does not rescue a single causal channel for unrestricted input waveforms. A separate causal convolution-commutation construction produces different source histories at Kundur buses 7 and 8 with exactly the same full voltage-at-bus-7 trace in the linear model. The numerical realization differs by only 1.42e-18 pu. This construction is not restricted to a single sinusoid and is not a nonlinear-grid identity.

Finally, internal continuing-load/buffer worlds with equal complete nodal PCC histories are indistinguishable to both direct PCC meters and any deterministic downstream grid measurements, even nonlinearly whenever the same boundary-value problem has a unique solution. An explicit nonzero, energy-neutral periodic witness is provided with finite first-order PCS dynamics, equal initial buffer states, and explicitly ideal lossless storage. No duplicate nonlinear replay can add information to this exact boundary identity.

## 1. Prospective protocol and source qualification

`PROTOCOL_FREEZE.json` was written and hashed before computing transfer results. Its SHA-256 is `d70678c27d393141c9ead63a0db5e33f3123363bc74b07404c7b4b7a71dc92f3`.

The frequency grid is 0.05, 0.1, 0.2, 0.5, 1, 2 Hz. No frequency, bus, or sensor pair was selected after inspecting the result. Five fixed scalar-channel sets are tested:

- First-source-bus voltage alone
- First selected generator-speed frequency alone
- Voltages at the two candidate source buses
- Frequencies of the two selected generators
- First-source-bus voltage plus first selected generator frequency

Kundur uses source/voltage buses 7 and 8 and generator IDs 1 and 4. WECC uses source/voltage buses 1 and 4 and generator IDs 1 and 29. “Frequency” means the exported machine-speed deviation multiplied by 60 Hz, not a separately modeled bus-frequency estimator or PMU. A channel count is not a count of PMU devices.

The unchanged input package is `outputs/round2_20261003/grid_transfer`. Kundur uses its qualified 51-state stable uniform-angle quotient. WECC uses the full 2405-dimensional chain-rule-completed descriptor pencil, including zero-mass states and algebraic variables. **The explicitly disqualified WECC ordinary EIG.As and finite-QZ ODE exports are not loaded.** No adapter is imported, so its HOME/cache behavior cannot mutate the prior study. The 11 locked input hashes are checked before and after the calculations and remain unchanged.

These local models inherit the earlier package's empirical micro-perturbation qualifications and limitations. The new harmonic calculations are not new nonlinear validation. The source signal is added consumption in MW; primary Q increments are known to be zero. The entire grid, operating point, parameters, and boundary conventions are the same between competing source hypotheses. Source origin is the candidate bus, not a workload label.

## 2. Harmonic observation and bounded error

For Kundur, the complex response to a unit P increment at angular frequency w is

H(w) = C (iw I - A)^(-1) B + D.

For WECC, the selected outputs are extracted from

Z(w) = (iw M - K_verified)^(-1) G.

All positive frequencies avoid the uniform-angle zero root. We solve the descriptor directly instead of silently deleting its algebraic structure or constructing an uncertified input ODE.

Let h1 and h2 be the selected P-only response columns, whitened by declared channel scales: 1e-4 pu for voltage and 1e-3 Hz for frequency. Observed complex channel vector z satisfies

z = h_j a + e,  ||e||_2 <= 1,

where a is an unrestricted complex amplitude in MW. The noise set is a **joint complex Euclidean ellipsoid**, not an independent full error allowance for every channel. It is an illustrative research error model, not a sensor specification. Shared clocks and known sensor response/phasing are assumed. Unknown channel-dependent delays, sensor calibration error, model error, or other unknown injections are outside this experiment.

For one nonzero scalar channel, h1 a = h2 b with b = (h1/h2)a. Thus source location is structurally unidentifiable at that frequency when amplitude/phase are unknown. This holds in all 24 one-channel tests.

For multiple channels, exact nonzero aliasing occurs if and only if the two complex columns are proportional. The normalized column correlation is rho = |h1* h2|/(||h1|| ||h2||), the principal-angle sine is sqrt(1-rho^2), and the condition number of the unit-column dictionary is sqrt((1+rho)/(1-rho)). The implementation evaluates orthogonal residuals directly to reduce cancellation near rho = 1. All 36 two-channel tests have nonzero angle.

For a true source-1 magnitude A, the closest source-2 output is its orthogonal projection onto span(h2), giving distance

d1(A) = A ||h1|| sin(theta).

The two unit-radius error balls are disjoint if d1(A) > 2. Thus the reported critical amplitude is 2/(||h1|| sin(theta)); the reverse direction has its own threshold. Equality is not a strict separation guarantee. Below the threshold, a midpoint of a closest pair is compatible with both hypotheses using bounded adversarial errors. No uniformly robust classifier exists over all nonzero amplitudes because amplitudes may approach zero.

### Representative frozen point: 0.2 Hz

| Grid | Two channels | sin(angle) | Critical MW: first / second source |
|---|---|---:|---:|
| Kundur | V at 7,8 | 0.25780 | 5.805 / 3.082 |
| Kundur | F at G1,G4 | 0.10820 | 18.333 / 25.590 |
| Kundur | V7, F at G1 | 0.48775 | 3.156 / 2.358 |
| WECC | V at 1,4 | 0.92416 | 2.994 / 5.864 |
| WECC | F at G1,G29 | 0.42008 | 28.781 / 21.689 |
| WECC | V1, F at G1 | 0.92870 | 2.930 / 10.852 |

Full unrounded values for every frozen frequency are in `results.json` and `harmonic_summary.csv`.

Conditioning alone is insufficient. For example, WECC's 2 Hz frequency pair has a nonzero angle but a source-4 threshold of about 1702 MW under the declared error scale because its source-4 gain is weak. This is **not** a validated nonlinear operating point or a recommended test amplitude. Many tabulated thresholds exceed the earlier micro-probe regime. The thresholds are linear-model extrapolations useful for comparing gain and error budgets; decreasing every error scale by a factor c decreases each threshold by c. No uniform nonlinear/model error bound has been supplied. If such a bound eta were independently established in the same norm, it must enter the separation budget rather than being ignored.

## 3. Same initial state and causal observation interfaces

A steady-state phasor identity alone is not proof that raw finite records beginning from a common equilibrium are identical. The study therefore includes two separate zero-state controls.

### 3.1 Finite, causal lock-in features with restricted sinusoidal sources

For Kundur, every source starts from the same known x(0) = 0 and has real input c cos(wt) + s sin(wt) for t >= 0. Each channel reports only the causal lock-in feature

m(T) = (2/T) integral_0^T y(t) exp(-iwt) dt, with T = 20/f.

This feature is available at the end of the observation interval; no future samples are used. The observer is not secretly given the raw time series. With Z = (iw I-A)^(-1)B and J = integral_0^T exp((A-iwI)t)dt, the exact columns are

M_cos = H - (2/T) C J Re(Z),
M_sin = -i H - (2/T) C J Im(Z).

The input's two real quadratures map to a real 2m-by-2 operator F_j. One channel yields a full-rank 2-by-2 operator for each source at every frozen frequency, so both source hypotheses yield the same feature space despite their common known initial state. Two channels yield distinct source subspaces at every tested frequency. Their principal angles and worst-phase residual singular values are saved. A worst-phase magnitude-A separation requires A sigma_min((I-P_other)F_j) > 2.

At 0.2 Hz, the finite-window voltage-pair thresholds are 5.841 and 3.107 MW, close to but not substituted for the harmonic thresholds. For a true unit cos source at bus7, the one-voltage feature is matched by source8 coefficients (cos,sin) = (0.66141738, 0.10203033). This is exact equivalence of the declared feature, not of the entire sinusoid-onset trace. An independent sampled analytic trajectory plus Simpson quadrature agrees with the finite operator to relative 1.79e-9 at this point.

### 3.2 Exact same-zero-state, one-channel full-record ambiguity

Let g7 and g8 be the causal stable scalar Kundur transfers from P at buses 7/8 to V7. For any causal drive v, define

World 1: u7 = g8 * v, u8 = 0;
World 2: u7 = 0, u8 = g7 * v.

Both physical grids and both source-generating filters start from zero incremental state. Causal LTI convolution commutes, so y1 = g7 * g8 * v = g8 * g7 * v = y2 for every time. No unstable inverse and no future observation is used. The source filter outputs are dimensionalized as MW commands by a fixed common scaling. A schedule generated in advance from a known model is allowed; it is not an inference of real IT behavior.

The frozen audit uses V7, a 0.2 Hz sine drive for 20s, and records through 40s with a 0.01s sampled piecewise-linear drive. One common normalization makes the largest incremental input 1 MW; the other source peaks at 0.66714 MW. The full observed outputs differ by at most 1.42e-18 pu, with relative L2 difference 1.05e-14. The inputs are distinct and may have either sign about a positive continuing-load background. They retain small filter tails at 40s; this example does not claim exact finite support, exact finite-cycle energy closure, or a single-sinusoid waveform class. Its algebraic equality is a linear-model theorem; applying those particular distinct nodal inputs to a nonlinear grid need not preserve equality.

## 4. Unknown reactive power is a decisive nuisance

If source j may inject an independent unknown complex P/Q pair, its observation set is the range of [h_jP, h_jQ]. Every frozen one-/two-channel configuration has full complex row rank for **each** candidate source. Consequently, each location generates the whole observation space and exact source ambiguity remains even with two channels. There are 60 recorded rank audits, including the one-channel configurations.

This is not a claim for constrained power factor, bounded P/Q ratios, a prescribed real-time waveform relationship, or three-plus sensors. A known P/Q relationship reduces the nuisance space and should be built into a new transfer calculation. Additional time/frequency observations can help only if constraints actually couple the unknown amplitudes across those observations; independent arbitrary amplitudes at every frequency do not create such coupling by themselves.

## 5. Direct PCC baseline and the correct information ordering

Two source-resolved direct P channels have H_PCC = I: their normalized columns are orthogonal with unit-column condition number 1. With the separately declared 0.1 MW joint direct-P error scale, both thresholds are 0.2 MW. One aggregate P channel has H_sum = [1,1] and is exactly source-ambiguous. These direct sensor assumptions are explicit; a meter of total demand is not secretly treated as two site-resolved meters.

At zero noise, complete time histories of source-resolved nodal P/Q and the same known grid initial state/parameters determine the downstream deterministic grid trajectory. Thus those direct histories can simulate any downstream observation: a grid transformation cannot add information about an input already observed exactly. The converse need not hold, as the causal one-channel example demonstrates. Under noise, the ordering needs matched information/error sets or a specified stochastic channel; the arbitrary voltage/frequency/P scales here do **not** establish a universal physical sensor superiority theorem. Direct P-only data also do not simulate a grid with independently unknown Q.

If competing hidden workload/buffer worlds have identical complete nodal PCC P/Q histories, direct PCC and downstream grid sensing are equally unable to distinguish their hidden decomposition. This is a different ambiguity from two distinct PCC inputs being collapsed by a sparse grid sensor.

## 6. A nontrivial continuing-load, cyclic, equal-PCC witness

The provided analytic witness uses the two internal worlds

load_+(t) = 10 + sin(2 pi t/10) MW, buffer_+(t) = sin(2 pi t/10) MW,
load_-(t) = 10 - sin(2 pi t/10) MW, buffer_-(t) = -sin(2 pi t/10) MW.

Both PCC histories are exactly 10 MW, both internal loads remain at least 9 MW, and Q is equal. Initial realized buffer power is zero and initial usable energy is 0.01 MWh in both worlds. With explicitly lossless storage, E_dot = -buffer/3600, energy returns exactly to its initial value every 10s. Both trajectories fit in 0.02 MWh; observed energy extrema are 0.00911581 and 0.01088419 MWh.

A causal first-order PCS tau p_dot + p = command, tau = 0.05s, realizes the waveform with command = p + tau p_dot. Its command peak is 1.000493 MW (below a declared 1.1 MW limit), realized power is at most 1 MW, and slew is at most 0.628319 MW/s (below 1 MW/s). The commands are known periodic clock signals; initial physical PCS and energy states agree. Positive efficiency losses would require additional recharge and invalidate this witness unchanged.

To turn the same-boundary construction into hidden-source-location ambiguity, keep the same positive baseline aggregates at both candidate buses; place an internally oscillating load plus its canceling buffer at the first bus in one world and at the second in the other. Every nodal PCC signal stays the same. This is a conceptual decomposition, not a claim that the prior benchmark's original load model was recalibrated as a real data center. Given equal grid initial state, boundary controller states, topology, and complete nodal P/Q, any deterministic well-posed nonlinear grid solution is identical. The exact premise is stronger than approximate agreement at a few samples.

## 7. Numerical audit and reproduction

All 12 descriptor solves pass the frozen backward-error and output-sensitivity screens. Kundur reduced-versus-descriptor output relative differences are at most 1.10e-13. WECC output changes under an independently row/column-equilibrated solve are at most 7.98e-14. These are floating-point audit results, not interval certificates; tiny backward residuals alone do not prove forward accuracy or model validity. The earlier chain-rule and nonlinear micro-probe qualifications remain necessary.

Run from the workspace root, without modifying existing inputs:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python outputs/round2_g4_identifiability_20261003/experiments/grid_transfer/run_transfer_study.py
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python outputs/round2_g4_identifiability_20261003/experiments/grid_transfer/validate_and_witness.py

`freeze_protocol.py` is retained as provenance and refuses to overwrite an existing freeze. Numerical runtime: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0.

Deliverables:

- `PROTOCOL_FREEZE.json`, its checksum, and locked original-input hashes
- `run_transfer_study.py`, `validate_and_witness.py`, their logs and `validation.json`
- `harmonic_transfer_arrays.npz`: all complex four-input/four-output response arrays for both grids
- `causal_lockin_arrays.npz`: the real finite-window source operators
- `causal_single_sensor_alias.npz`: distinct causal source traces and their identical single-channel outputs
- `cyclic_continuing_load_same_PCC.npz` and its JSON constraints/results
- `results.json`, `harmonic_summary.csv`, and `input_integrity_after.json`

The evidence supports a conditional measurement-identifiability result and precise counterexamples. It does not identify workload provenance, validate real sensors, establish nonlinear localization at the tabulated large thresholds, or provide an operational safety guarantee.
