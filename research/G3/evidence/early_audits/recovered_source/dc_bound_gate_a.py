"""Independent analytic Gate A DC obstruction; no controller/performance search.
Reads only the locked physical constants and the declared fault-onset state.
Postfault PCC voltage/power are never used in the universal inequality.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
PARAM = ROOT / 'protocol/GATE_A_LOCKED_V1.json'
D = json.loads(PARAM.read_text())
TF, DUR = 0.20005, 0.15
OUT = ROOT / 'protocol/DC_BOUND_GATE_A.json'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read_checkpoint(tag):
    path = ROOT / f'gate_a/dq_results/reference_clip_counterexample_{tag}.npz'
    with np.load(path) as z:
        a = z['trace'].copy()
        names = list(z['trace_columns'])
    ix = {k: n for n, k in enumerate(names)}
    hits = np.flatnonzero(np.isclose(a[:, ix['t']], TF, rtol=0, atol=1e-14))
    assert len(hits), 'Fault boundary must be recorded exactly; no interpolation.'
    row = a[hits[0]]
    # Only the continuous physical checkpoint variables enter the certificate.
    state = {k: float(row[ix[k]]) for k in ['t', 'id', 'iq', 'Wdc', 'Pb', 'WL', 'Ipu', 'Vdcpu']}
    summary = json.loads(path.with_suffix('.json').read_text())
    healthy = a[(a[:, ix['t']] >= .15) & (a[:, ix['t']] <= TF)]
    s = np.hypot(a[:, ix['Ppcc']], a[:, ix['Qpcc']])
    kmax = int(np.argmax(s))
    audit = dict(
        trace_path=str(path), trace_sha256=digest(path),
        report_path=str(path.with_suffix('.json')),
        report_parameter_sha256=summary['parameter_sha256'],
        healthy_window_s=[.15, TF],
        healthy_max_Ipu=float(healthy[:, ix['Ipu']].max()),
        healthy_max_pcc_apparent_VA=float(np.hypot(healthy[:, ix['Ppcc']], healthy[:, ix['Qpcc']]).max()),
        healthy_min_Vdcpu=float(healthy[:, ix['Vdcpu']].min()),
        healthy_max_Vdcpu=float(healthy[:, ix['Vdcpu']].max()),
        full_run_max_pcc_apparent_VA=float(s[kmax]),
        full_run_max_pcc_apparent_time_s=float(a[kmax, ix['t']]),
        observed_first_current_crossing_after_fault_s=summary['first_current_limit_crossing_s']-TF,
        observed_dc_stop_after_fault_s=summary['final_time_s']-TF,
        observed_stop_reason=summary['stop_reason'],
    )
    return state, audit

s, audit = read_checkpoint('1e-05')
Imax = D['current_continuous_limit_pu'] * D['I_phase_peak_base_A']
Rt = D['filter_R_ohm'] + D['grid_R_ohm']
Lt = D['filter_L_H'] + D['grid_L_H']
eta = D['eta_dc_dc']
ramp = D['battery_source_ramp_down_W_per_s']
pmin = D['battery_terminal_power_min_W']
Vs = next(x['event']['retained_voltage_pu'] for x in D['case_registry'] if x['id']=='reference_clip_counterexample')
p_source_max = 1.5 * Vs * D['V_phase_peak_base_V'] * Imax
p_inv_loss_max = D['inverter_loss_constant_W'] + D['inverter_loss_current_squared_W_at_1pu']*(Imax/D['I_phase_peak_base_A'])**2
p_copper_max = 1.5 * Rt * Imax**2
p_out_max = p_source_max + p_inv_loss_max + p_copper_max
wdc_max = .5 * D['C_dc_F'] * (D['V_dc_max_pu']*D['V_dc_initial_V'])**2
wl_max = .75 * Lt * Imax**2
headroom = wdc_max + wl_max - s['Wdc'] - s['WL']
a = eta*s['Pb'] - p_out_max
b = eta*ramp
zero = s['Pb']/ramp
peak_t = a/b
peak_gain = a*a/(2*b)
assert 0 < peak_t < DUR < zero
assert peak_gain > headroom
cross = (a-math.sqrt(a*a-2*b*headroom))/b

def bus(p):
    return eta*p if p>=0 else p/eta

def primitive(p):
    return .5*(eta if p>=0 else 1/eta)*p*p

def source_lower(t):
    return bus(max(pmin, s['Pb']-ramp*t))

def integrated_source_lower(t):
    falling_time = min(t, (s['Pb']-pmin)/ramp)
    pend = s['Pb']-ramp*falling_time
    return (primitive(s['Pb'])-primitive(pend))/ramp + max(0,t-falling_time)*bus(pmin)

def F(t):
    return integrated_source_lower(t)-p_out_max*t

# Direct checks of the physical identity, independently from dq_bench.py.
rng = np.random.default_rng(4871)
identity_errors = []
for k in range(25):
    i = Imax*rng.uniform(0,1)*np.exp(1j*rng.uniform(-np.pi,np.pi))
    u = rng.uniform(0,850)*np.exp(1j*rng.uniform(-np.pi,np.pi))
    e = Vs*D['V_phase_peak_base_V']
    pb = rng.uniform(-1e6,1e6)
    di = (u-e-Rt*i)/Lt-1j*D['omega_base_rad_s']*i
    pinv = 1.5*np.real(u*np.conj(i))
    loss = D['inverter_loss_constant_W']+D['inverter_loss_current_squared_W_at_1pu']*(abs(i)/D['I_phase_peak_base_A'])**2
    lhs = bus(pb)-pinv-loss + 1.5*Lt*np.real(np.conj(i)*di)
    rhs = bus(pb)-1.5*np.real(e*np.conj(i))-loss-1.5*Rt*abs(i)**2
    identity_errors.append(abs(lhs-rhs))

quadrature_errors = []
for t in [.02, .15, .2, .4]:
    cuts = [0.] + [x for x in [zero, (s['Pb']-pmin)/ramp] if 0<x<t] + [t]
    numeric = sum(quad(source_lower, x, y, epsabs=1e-8, epsrel=1e-12)[0] for x,y in zip(cuts[:-1],cuts[1:]))
    quadrature_errors.append(abs(numeric-integrated_source_lower(t)))
root_numeric = brentq(lambda t:F(t)-headroom, 0, peak_t, xtol=1e-14)

# Outward-rounded certificate: 20 ms contradiction has >600 J margin.
# These bounds apply to the declared initial state; this is not interval validation
# of the preceding numerical warm-up or an uncertain real-world state estimator.
assert s['Pb'] >= 816000 and s['Wdc'] >= 21918 and s['WL'] >= 277
assert p_source_max <= 480001 and p_inv_loss_max <= 7200
assert p_copper_max <= 23941 and wdc_max <= 26137 and wl_max <= 398
conservative_headroom = 26137+398-21918-277
conservative_a = eta*816000-(480001+7200+23941)
conservative_gain_20ms = conservative_a*.02-.5*b*.02**2
conservative_margin = conservative_gain_20ms-conservative_headroom
assert conservative_margin > 600

refinement = None
try:
    s5, audit5 = read_checkpoint('5e-06')
    refinement = dict(checkpoint=s5, trace_sha256=audit5['trace_sha256'],
                      report_parameter_sha256=audit5['report_parameter_sha256'],
                      difference_5us_minus_10us={k:s5[k]-s[k] for k in s})
except FileNotFoundError:
    refinement = {'status':'refinement file unavailable during read'}

checks = dict(
    WL_from_current_error_J=abs(s['WL']-.75*Lt*(s['id']**2+s['iq']**2)),
    Wdc_from_voltage_error_J=abs(s['Wdc']-.5*D['C_dc_F']*(s['Vdcpu']*D['V_dc_initial_V'])**2),
    source_base_consistency_error_W=abs(p_source_max-Vs*D['S_base_VA']),
    identity_random_check_count=len(identity_errors),
    max_energy_derivative_identity_error_W=max(identity_errors),
    piecewise_source_integral_test_times_s=[.02,.15,.2,.4],
    max_piecewise_source_quadrature_error_J=max(quadrature_errors),
    root_analytic_numeric_error_s=abs(cross-root_numeric),
    F_at_analytic_root_minus_headroom_J=F(cross)-headroom,
    all_numeric_checks_passed=bool(max(identity_errors)<1e-8 and max(quadrature_errors)<1e-7 and abs(cross-root_numeric)<1e-10)
)
assert checks['all_numeric_checks_passed']
result = dict(
    status='Model-conditioned analytic any-current-safe-policy DC-overvoltage obstruction; no full safety claim',
    parameter_path=str(PARAM), parameter_sha256=digest(PARAM), checkpoint=s,
    source_voltage_pu=Vs, fault_duration_s=DUR,
    constants=dict(I_phase_peak_limit_A=Imax,R_total_ohm=Rt,L_total_H=Lt,
                   source_power_upper_W=p_source_max,inverter_loss_upper_W=p_inv_loss_max,
                   copper_loss_upper_W=p_copper_max,total_energy_exit_upper_W=p_out_max,
                   Wdc_upper_J=wdc_max,WL_upper_J=wl_max,aggregate_headroom_J=headroom,
                   Pb_lower_at_150ms_W=s['Pb']-ramp*DUR,source_lower_positive_until_s=zero),
    bound=dict(formula_until_source_zero='F(t)=(eta*Pb0-Pexit_max)*t-0.5*eta*Rdown*t^2',
               initial_excess_power_lower_W=a,excess_power_down_slope_W_per_s=b,
               first_headroom_equality_after_fault_s=cross,first_headroom_equality_absolute_s=TF+cross,
               maximum_prefix_time_s=peak_t,maximum_prefix_gain_J=peak_gain,
               maximum_prefix_headroom_excess_J=peak_gain-headroom,
               gain_at_20ms_J=F(.02),headroom_excess_at_20ms_J=F(.02)-headroom,
               gain_at_150ms_J=F(.15),clearance_endpoint_alone_proves_failure=False),
    conservative_20ms_certificate=dict(
        Pb0_lower_W=816000,Wdc0_lower_J=21918,WL0_lower_J=277,
        source_export_upper_W=480001,inverter_loss_upper_W=7200,copper_loss_upper_W=23941,
        Wdc_upper_J=26137,WL_upper_J=398,aggregate_headroom_upper_J=conservative_headroom,
        accumulated_energy_gain_lower_J=conservative_gain_20ms,
        contradiction_margin_J=conservative_margin),
    startup_and_observed_trace_audit=audit,refinement=refinement,numeric_selfcheck=checks,
    limits=[
        'The certificate starts at the declared 0.20005 s common physical state; it is not a safety certificate for sampled startup.',
        'All-current-safe means actual current at or below 1 pu continuously, with no overload allowance.',
        'All active export, maximum allowed passive losses, and full allowable inductor headroom are granted; Q service and modulation constraints are relaxed.',
        'No candidate postfault PCC voltage or PCC power bounds are used.',
        'No brake/chopper, additional storage, extra freewheel/bypass energy-disposal path, or shutdown/reset is modeled. The bidirectional battery source cannot disconnect or jump power; it obeys the locked continuous slew law.',
        'The full-precision 17.035 ms root is an outer-relaxation obstruction, not an exact physical failure time.',
        'The outward-rounded 20 ms certificate is robust to the displayed rounding intervals; numerical warm-up refinement is not a proof of a real-world state-estimation error bound.'
    ])
OUT.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'certificate':str(OUT),'crossing_s':cross,'headroom_J':headroom,'margin_20ms_J':F(.02)-headroom,
                  'outward_rounded_margin_J':conservative_margin,'selfcheck':checks},indent=2))
