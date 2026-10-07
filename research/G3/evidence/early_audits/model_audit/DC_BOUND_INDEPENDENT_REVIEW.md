# Independent physical-model review of the Gate A DC obstruction

Date: 2026-10-01. Verdict: **the stated inequality is valid for the locked average-value circuit and the stated state/actuator assumptions**. It is a necessary-condition obstruction for joint actual-current/DC-voltage feasibility, not a hardware conclusion, controller performance result, or exact physical failure time. No code from the theory implementation was imported in this review.

## Factor and sign audit

The Park/space-vector convention uses phase-peak current. Three-phase inductive energy is therefore

`W_L = (1/2) L_t (i_a^2+i_b^2+i_c^2) = (3/4) L_t (i_d^2+i_q^2)`.

Copper dissipation is `R_t sum(i_phase^2) = (3/2) R_t |i_dq|^2`. DC capacitor energy is `W_dc=(1/2) C_dc V_dc^2`. No extra factor of three or two is missing.

Adding the physical inductor and DC equations gives

`d(W_dc+W_L)/dt = P_bus - P_remote - P_copper - P_inverter_loss - P_aux`.

The PLL/cross-coupling rotation contributes zero to this scalar energy identity. The remote source port must be used here; replacing it with PCC power without subtracting/filtering the correct stored energy would change the proof. The locked model has P_aux=0.

For any trajectory respecting actual `|i_dq|<=I_base` during a retained source voltage `a=0.4`, Cauchy–Schwarz gives `P_remote<=1.5*a*V_phase_peak*I_peak=a*S_base=480 kW`. Total copper dissipation is at most `1.5*R_total*I_peak^2≈23.9404 kW`. The specified inverter loss law is bounded above by `1.2+6=7.2 kW` at that current bound.

Using maximum export and maximum losses simultaneously is optimistic, which is the correct direction for a necessary impossibility condition. Allowing all active current rather than reserving Q further relaxes feasibility. Ignoring modulation/PLL dynamics cannot make the resulting negative certificate unfair to a policy.

## Source ramp and reversal

The locked source obeys `dP_b/dt>=-R_down`, so starting from physical source power P_b0 it necessarily satisfies `P_b(t)>=P_b0-R_down*t` until the negative battery-power floor is reached. This is the fastest possible reduction regardless of the commanded reference or source lag. The lag and sample delay can only make the source less capable than this relaxation.

The bus-power map is monotonic:

- `h(P_b)=eta_dc*P_b` for discharge
- `h(P_b)=P_b/eta_dc` for charging

Consequently `P_bus(t)>=h(max(P_b,min,P_b0-R_down*t))`. A charging-capable source must **not** be clamped to zero in a longer-horizon bound. The theory worker's supplied piecewise antiderivative is consistent with this map. In the Gate A 20 ms certificate the lower source envelope remains positive, so the simple positive quadratic is sufficient.

Let `P_exit,max=480000+23940.4463+7200 W` and `A=eta_dc*P_b0-P_exit,max`. While the source lower envelope is positive,

`F(t)=A*t-(eta_dc*R_down/2)*t^2`

is a lower bound on the increase of total DC-plus-inductor stored energy. Its units are joules. Safety requires every prefix to fit within

`H=(W_dc,max-W_dc0)+(W_L,max-W_L0)`.

Granting the full remaining inductor storage is necessary; omitting it could produce a false DC-only impossibility claim during current ramping. Once F(t)>H, no trajectory in this model can maintain both current and DC bounds. Later negative F at fault clearance cannot undo an earlier constraint crossing. This prefix condition is the crucial mechanism.

## Assumptions that cannot be hidden

- No DC dump resistor, braking chopper, emergency disconnect, independent auxiliary sink or other unmodeled energy exit
- No instantaneous source-power jump, source bypass, or reversal faster than the fixed slew law
- No allowed actual-current overload above the 1.00 pu screen
- The initial physical state is explicitly specified; the bound does not retrospectively validate earlier startup
- Loss upper bounds remain exactly the locked modeled losses. Additional real losses could weaken this numerical obstruction and must be modeled before transferring it to equipment
- The source retained voltage/duration is the declared exogenous source event, not a candidate-dependent PCC trajectory
- A numerical checkpoint is not a certified interval state estimate; round-out margins cover only the stated rounding ranges

The first quadratic headroom root bounds the latest possible survival in an optimistic relaxation. It is not the actual failure time of a physical converter or of the implemented Q-priority controller. The observed controller can fail much earlier for a narrower set of reasons.

## Checkpoint/provenance requirement

The first `DC_BOUND_GATE_A.json` inspected was conditional on the original 0.20005 s state and mixed report hashes from initialization-wording revisions. Its mathematical form is valid, but its result must not be presented as the pre-registered settled-orbit result. The final version should bind the inequality to the first qualifying checkpoint under `GATE_A_LOCKED_V2_1.json` and then to the physical state at the new fault onset.

The independent abc V2.1 implementation selects **0.600000 s** as the first qualifying checkpoint, with converged checks at 0.50, 0.55 and 0.60 s. No later favorable checkpoint is selected. The actual source dip begins at **0.600050 s**. The independently computed bound constants from that exact abc fault-onset state are provided in `DC_BOUND_ABC_NUMERIC_CHECK.json` after the fixed refinement run finishes.

The resulting actual-current counterexample is extremely small (about 0.00746% above the strict threshold). It should be reported as a numerical falsification of the reference-clipping shortcut. The DC energy obstruction has a materially larger energy margin, but remains conditional on the synthetic no-brake/finite-ramp plant. Neither conclusion establishes service-policy novelty or an improvement over an optimized controller.
