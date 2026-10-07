# Independent abc switching validation

Status: independent reference tests and target analytical-witness tests complete. See TARGET_VALIDATION_REPORT.md and BOUNDARY_VALIDATION_REPORT.md for the target outcomes, including failed exact DC recovery.

This is a newly written software model, not a replay of old dq/abc transforms, not execution of motulator, and not hardware qualification. The C++ plant integrates three physical phase currents driven by actual binary bridge leg states. dq coordinates appear only in the controller and power reporting.

## Model and signs

The 3-wire, ideal two-level bridge has leg states s_k in {0,1}, common-mode-neutral terminal voltages e_k=Vdc(s_k-mean(s)), and import-positive currents from grid to converter:

L di_k/dt = v_k - R i_k - e_k.

With balanced phase voltages v_k=Vp cos(omega*t-2*pi*k/3), i_k=id*cos(theta_k)-iq*sin(theta_k), active grid import is p=sum(v_k*i_k)=1.5*Vp*id. Positive reactive grid support is q_support=1.5*Vp*iq, the negative of reactive consumption. The physical bridge power is p_dc=sum(e_k*i_k) and i_dc=p_dc/Vdc=sum(s_k*i_k). These equalities are checked independently on emitted switched waveforms.

The state W=C*Vdc^2/2 obeys Wdot=p_dc-d+b, where d>0 is continuing compute load and b>0 is battery discharge into the bus. Bdot=-b; bdot=clip((clip(u,-umax,umax)-b)/tau,-ramp,ramp). Neither W nor B is artificially clamped to its admissible bounds. A collapse at W<=0 is an integration failure, not a successful certificate.

The independent total-energy audit checks:

W(t)+B(t)+(L/2)sum(i_k(t)^2) - initial total energy = integral[p_grid-R sum(i_k^2)-d]dt.

The RHS uses grid-terminal phase power rather than requested dq power. DC bridge energy, battery inventory, balanced-current sum, and abc reactive cross-product signs are checked separately.

## Numerical method and controller

Center-aligned, common-carrier PWM is implemented through exact turn-on/turn-off instants calculated from the three held duties. Switch edges and all exogenous polynomial knots split integration intervals. Within each interval explicit midpoint RK2 takes steps no larger than the requested step size. The DC state is W rather than Vdc, preserving its balance without division by a vanishing DC voltage. The L-current portion of the total-energy audit is not forced by construction; its residual converges on step refinement.

A current PI is sampled once per PWM period. Reference RL/rotating-frame/di-dt feedforward is evaluated at the next half-period; measured current error is sampled at period start. Kp=L*2000 and Ki=R*2000. The voltage reference is rotated to the half-period angle; min/max common-mode injection creates duties, which are bounded to [0,1]. Integrator accumulation is frozen during modulation clipping. No outer DC-voltage controller changes the specified grid-power request. Actual current, DC excursion, clipping, and tracking error are retained.

The averaged comparison uses precisely the same current controller, sample period, initial states, source waveform and battery command, replacing binary s_k with its held duty. Thus increasing PWM frequency tests genuine averaging convergence; shrinking the integrator step alone does not remove physical switching ripple.

Initial iabc equals the initial requested current, PI integrals are zero, and battery/DC initial states are identical in each comparison. There is no hidden warmup, fault-time state reset, or case-specific state preconditioning.

## Frozen reference cases

The physical baseline was fixed before the analytical witnesses: 1 MW scaling; 690 V line-line RMS, 50 Hz, L=100 uH per phase, R=5 mOhm per phase, C=0.02 F, Vdc0=1400 V, W0=19600 J, B0=100 kJ, tau=20 ms, |u|<=500 kW. The default switching frequency is 10 kHz. Ramp limiting is inactive for these initial reference cases.

1. Constant: d=650 kW, q=0, u=0. p0 solves p0-R*p0^2/(1.5*Vp^2)=650 kW. This includes baseline copper loss.
2. Smooth service: h=sin(pi*(t-.04)/.08)^2 on [.04,.12] s and zero elsewhere. p=p0-100 kW*h, q=200 kvar*h, d=650 kW, u=100 kW*h. The finite battery lag is retained. This is a test waveform, not an optimized or exactly restorative witness.

Both use a 0.2 s horizon. Step tests are 2,1,0.5 us at 10 kHz. Averaging tests use 5,10,20,40 kHz with matched averaged runs. The original reference cases are retained separately from the later target-device parameters.

## Reference findings

All 200 deterministic audit checks pass. At 1 us and 10 kHz, the smooth-service run has a maximum total-energy residual of 0.00451 J. Its phase-vector current maximum is 830.35 A, compared with 774.52 A in the averaged run; this approximately 56 A instantaneous ripple difference is a physical reason not to infer a hard switched-current limit from an averaged current circle.

For the smooth pulse, halving the integration step from 2 to 1 us changes W by at most 0.004712 J; halving again changes it by 0.001300 J. The PWM-versus-average RMS W difference at 5/10/20/40 kHz is 10.281/2.574/0.646/0.161 J. The corresponding RMS active-power difference is 539.09/134.78/33.70/8.43 W. This is approximately second-order cycle-average convergence, while current ripple decreases approximately as 1/f_sw.

The 10 kHz smooth-service DC-voltage range is 1346.77–1400.59 V, no modulation cycles clip, and active/reactive RMS command tracking errors are 160.54 W / 1150.52 var. Neither tracking nor exact terminal restoration is asserted to be perfect. The reference pulse ends with W=19610.15 J and nonzero battery tail, as expected for its intentionally unoptimized finite-response command.

Machine-readable numbers, run commands and trace files are in REFERENCE_RESULTS.json. REFERENCE_AUDIT.json records every checked identity. REFERENCE_FREEZE.json records waveform/physical choices. Each run emits full cycle traces and an actual 2 ms final switching-waveform excerpt. reference_validation.png shows the service, voltage, battery, phase-current and energy traces.

## Primary model references

- [Aalto Electric Drives, Voltage-Source Converter](https://aalto-electric-drives.github.io/motulator/model/common/converters.html): ideal binary two-level bridge, capacitor and switched DC-current identities, explicit carrier event times, and duty-averaged model. The simulator here is independently written and reverses the documentation's output-current direction to import-positive.
- [Aalto Electric Drives, AC Filter and Grid Impedance](https://aalto-electric-drives.github.io/motulator/model/grid/filter_and_grid.html): continuous RL-filter model. Our abc KVL uses the same circuit with the declared current-direction change.
- [Aalto Electric Drives, DC-Bus Voltage Control](https://aalto-electric-drives.github.io/motulator/control/grid/dc_voltage_ctrl.html): DC-capacitor energy and power-balance interpretation. No such outer voltage controller is introduced into this validation.

Accessed 2026-10-03. Sources provide physical reference equations; they do not certify this implementation or the parameter choices.

## Limitations

Ideal switches, no dead time, no conduction/switching device losses beyond the specified RL copper loss, no measurement noise, exact grid angle, stiff balanced sinusoidal grid, no thermal limits, and an ideal DC battery power converter with finite command dynamics. Device identification, semiconductor-level switching transients, robustness, grid faults, PLL behavior, and real compute hardware are outside this evidence. A high-frequency switched simulation strengthens physical consistency of a witness but cannot establish real-hardware feasibility.
