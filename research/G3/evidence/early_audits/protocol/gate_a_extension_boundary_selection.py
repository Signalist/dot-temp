"""Analytic preselection only: no ODE integration, controller import, or new trajectory.
Writes only protocol/gate_a_extension_boundary_selection.json.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PARAM = ROOT/'protocol/GATE_A_LOCKED_V2_1.json'
REPORT = ROOT/'gate_a/preconditioned_dq/h1e-05.json'
CHECKPOINT = ROOT/'gate_a/preconditioned_dq/h1e-05_checkpoint.json'
TRACE = ROOT/'gate_a/preconditioned_dq/h1e-05.npz'
CERTIFICATE = ROOT/'protocol/DC_BOUND_GATE_A_V2_1_REVALIDATED.json'
OUT = ROOT/'protocol/gate_a_extension_boundary_selection.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
d = json.loads(PARAM.read_text())
report = json.loads(REPORT.read_text())
cp = json.loads(CHECKPOINT.read_text())
previous = json.loads(CERTIFICATE.read_text())
assert sha(PARAM) == report['protocol_sha256'] == cp['full_protocol_sha256'] == previous['parameter_sha256']
# Layout from the already audited dq_preconditioned.py, recorded in the fresh certificate.
names = previous['startup_and_observed_trace_audit']['trace_columns']
with np.load(TRACE) as z:
    trace = z['trace']
assert trace.shape[1] == len(names)
ix = {name:k for k,name in enumerate(names)}
t0 = report['fault_start_s']
hits = np.flatnonzero(np.isclose(trace[:,ix['t']],t0,atol=1e-14,rtol=0))
assert len(hits)
row = trace[hits[0]]
state = {k:float(row[ix[k]]) for k in ['t','id','iq','Wdc','Pb','WL','Ipu','Vdcpu']}
for k,value in state.items():
    assert abs(value-previous['checkpoint'][k]) < 1e-8
assert abs(cp['time_s'] + d['prerun_convergence']['fault_after_checkpoint_s'] - t0) < 1e-14
assert report['checks'][-1]['successive'] == d['prerun_convergence']['successive_checks_required']
I = d['current_continuous_limit_pu']*d['I_phase_peak_base_A']
L = d['filter_L_H']+d['grid_L_H']
R = d['filter_R_ohm']+d['grid_R_ohm']
eta = d['eta_dc_dc']
rdown = d['battery_source_ramp_down_W_per_s']
S = 1.5*d['V_phase_peak_base_V']*I
loss = d['inverter_loss_constant_W']+d['inverter_loss_current_squared_W_at_1pu']*(I/d['I_phase_peak_base_A'])**2+1.5*R*I**2
Wdcmax = .5*d['C_dc_F']*(d['V_dc_max_pu']*d['V_dc_initial_V'])**2
WLmax = .75*L*I**2
H = Wdcmax+WLmax-state['Wdc']-state['WL']
b = eta*rdown
T = d['prerun_convergence']['fault_duration_s']
assert T < state['Pb']/rdown
critical_t = math.sqrt(2*H/b)
critical_a = math.sqrt(2*b*H) if T>=critical_t else H/T+.5*b*T
critical_v = (eta*state['Pb']-loss-critical_a)/S
near_v = math.ceil(1000*critical_v)/1000
assert 0<critical_v<near_v<1

# The outward-rounded inequalities remain independently checked against these inputs.
assert state['Pb']>=815600 and state['Wdc']>=21915 and state['WL']>=276
assert Wdcmax<=26137 and WLmax<=398
assert loss<=7200+23941
rounded_H = 26137+398-21915-276

selected = []
for label,v in [('shallow_085',.85),('shallow_075',.75),('near_dc_boundary',near_v)]:
    a = eta*state['Pb']-loss-v*S
    peak_time = max(0.,min(T,a/b))
    gain = a*peak_time-.5*b*peak_time**2
    margin = gain-H
    # +1 W covers base floating-point conversion while retaining an outward bound.
    source_upper_round = v*d['S_base_VA']+1
    assert source_upper_round>=v*S
    ar = eta*815600-(source_upper_round+7200+23941)
    tr = max(0.,min(T,ar/b))
    rounded_gain = ar*tr-.5*b*tr**2
    selected.append(dict(id=label,retained_source_voltage_pu=v,duration_s=T,
       restore_full_checkpoint_time_s=cp['time_s'],fault_after_checkpoint_s=d['prerun_convergence']['fault_after_checkpoint_s'],
       fault_start_s=t0,a_initial_excess_power_lower_W=a,source_active_export_upper_W=v*S,
       prefix_max_time_s=peak_time,maximum_energy_gain_lower_J=gain,headroom_J=H,
       signed_impossibility_margin_J=margin,margin_divided_by_headroom=margin/H,
       clearance_energy_gain_lower_J=a*T-.5*b*T**2,
       outward_rounded_margin_J=rounded_gain-rounded_H,
       verdict='not excluded by this necessary DC-overvoltage bound; feasibility is NOT established'))
near = selected[-1]
assert near['signed_impossibility_margin_J'] < 0
assert abs(near['signed_impossibility_margin_J'])/H < .01
result=dict(status='Preselected analytically before any new controller trajectory; not a feasibility certificate',
  diagnostic_sag_budget=3,total_planned_diagnostic_budget=12,extra_trajectory_conditions_added=0,
  source_paths_and_hashes={str(p.relative_to(ROOT)):sha(p) for p in [PARAM,REPORT,CHECKPOINT,TRACE,CERTIFICATE]},
  exact_onset_state=state,qualified_checkpoint_time_s=cp['time_s'],
  full_checkpoint_preservation='Restore all plant/controller/held/queued states, absolute clock, and the existing 50 us fault offset; no phase reset or state projection.',
  constants=dict(S_source_per_pu_W=S,loss_upper_W=loss,eta=eta,ramp_down_W_per_s=rdown,
     quadratic_coefficient_W_per_s=b,Wdcmax_J=Wdcmax,WLmax_J=WLmax,H_J=H,
     source_lower_zero_time_s=state['Pb']/rdown,conservative_H_upper_J=rounded_H),
  boundary=dict(duration_s=T,critical_retained_voltage_pu=critical_v,critical_prefix_time_s=critical_t,
     initially_nonpositive_energy_gain_threshold_voltage_pu=(eta*state['Pb']-loss)/S,
     near_point_rule='ceil(1000*critical_retained_voltage_pu)/1000; common duration 150 ms',
     equality_is_not_strict_impossibility=True),
  selected_conditions=selected,
  local_sensitivity_at_near_point=dict(d_margin_d_voltage_J_per_pu=-S*near['prefix_max_time_s'],
     d_margin_d_initial_Pb_J_per_W=eta*near['prefix_max_time_s'],
     interpretation='Near-boundary case is deliberately sensitive; no hardware robustness claim.'),
  limitations=[
   'A positive signed margin rules out joint current/DC safety in the locked model; a nonpositive margin proves no feasibility claim.',
   'Current is actual continuous 1 pu; no overload is granted. All current is nevertheless granted to ideal-source active export for an optimistic outer bound.',
   'Reactive service, modulation, tracking, source-lag restrictions beyond the slew floor, and sampled-loop behavior are relaxed.',
   'No candidate postfault PCC voltage or power appears in the bound.',
   'No brake/chopper/additional storage/extra bypass or freewheel energy-disposal path/source disconnect/shutdown reset is modeled.',
   'The source can charge but cannot reverse instantaneously; its lower envelope remains positive for the selected 150 ms events.',
   'The near point is a diagnostic of a relaxed necessary bound, not the true feasible/infeasible plant boundary.',
   'Do not replace a planned point after observing its trajectory; any replacement needs a new preregistration and must remain within the 12-condition budget.'
  ])
OUT.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'output':str(OUT),'critical_retained_voltage_pu':critical_v,'critical_time_s':critical_t,
                  'selected_conditions':selected},indent=2))
