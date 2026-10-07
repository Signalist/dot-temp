"""Text transformation recovered from the prior tool-call input; does not run a model or certificate."""
from pathlib import Path
base=Path(__file__).resolve().parents[1]
s=(base/'recovered_source/dc_bound_gate_a.py').read_text()
s=s.replace("PARAM = ROOT / 'protocol/GATE_A_LOCKED_V1.json'", "PARAM = ROOT / 'protocol/GATE_A_LOCKED_V2_1.json'")
s=s.replace("TF, DUR = 0.20005, 0.15", "PRIMARY_REPORT = json.loads((ROOT / 'gate_a/preconditioned_dq/h1e-05.json').read_text())\nTF = PRIMARY_REPORT['fault_start_s']\nDUR = D['prerun_convergence']['fault_duration_s']")
s=s.replace("OUT = ROOT / 'protocol/DC_BOUND_GATE_A.json'", "OUT = ROOT / 'protocol/DC_BOUND_GATE_A_V2_1.json'")
start=s.index('def read_checkpoint(tag):')
end=s.index("s, audit = read_checkpoint('1e-05')")
reader='''def read_checkpoint(tag):
    path = ROOT / f'gate_a/preconditioned_dq/h{tag}.npz'
    with np.load(path) as z:
        a = z['trace'].copy()
    # Frozen layout independently read from dq_preconditioned.py::rec.
    names = ['t','id','iq','Wdc','Pb','deltaEb','intPsource','intLoss','Ipu','Vdcpu',
             'Ppcc','Qpcc','Vpccpu','Pinv','Psource','WL','energy_residual','soc','Vs','PLL_Hz']
    assert a.shape[1] == len(names)
    ix = {k:n for n,k in enumerate(names)}
    report = json.loads(path.with_suffix('.json').read_text())
    cp_path = path.with_name(path.stem+'_checkpoint.json')
    cp = json.loads(cp_path.read_text())
    assert report['protocol_sha256'] == digest(PARAM) == cp['full_protocol_sha256']
    assert abs(report['fault_start_s']-TF) < 1e-14
    hits = np.flatnonzero(np.isclose(a[:,ix['t']],TF,rtol=0,atol=1e-14))
    assert len(hits), 'Fault boundary must be exact; do not interpolate.'
    row = a[hits[0]]
    state = {k:float(row[ix[k]]) for k in ['t','id','iq','Wdc','Pb','WL','Ipu','Vdcpu']}
    t_cp = cp['time_s']
    healthy_start = t_cp-D['prerun_convergence']['hard_safe_window_s']
    healthy = a[(a[:,0]>=healthy_start-1e-12)&(a[:,0]<=t_cp+1e-12)]
    s_all = np.hypot(a[:,ix['Ppcc']],a[:,ix['Qpcc']]); kmax=int(np.argmax(s_all))
    assert cp['safe_window'] == report['checks'][-1]['metrics']
    assert report['checks'][-1]['successive'] == D['prerun_convergence']['successive_checks_required']
    assert abs(t_cp+D['prerun_convergence']['fault_after_checkpoint_s']-TF)<1e-14
    cp_states = dict(zip(cp['plant_state_names'],cp['plant_state']))
    cp_wl = .75*(D['filter_L_H']+D['grid_L_H'])*(cp_states['id']**2+cp_states['iq']**2)
    audit = dict(
        trace_path=str(path),trace_sha256=digest(path),report_path=str(path.with_suffix('.json')),
        report_parameter_sha256=report['protocol_sha256'],
        trace_layout_source=str(ROOT/'gate_a/dq_preconditioned.py'),
        trace_layout_source_sha256=digest(ROOT/'gate_a/dq_preconditioned.py'),
        trace_columns=names,
        warmup_checkpoint_path=str(cp_path),warmup_checkpoint_sha256=digest(cp_path),
        warmup_checkpoint_time_s=t_cp,
        warmup_checkpoint=dict(Wdc_J=cp_states['Wdc'],WL_J=cp_wl,Pb_W=cp_states['Pb'],
          Wdc_normalized_to_nominal_energy=cp_states['Wdc']/(.5*D['C_dc_F']*D['V_dc_initial_V']**2),
          WL_normalized_to_rated_inductor_energy=cp_wl/(.75*(D['filter_L_H']+D['grid_L_H'])*D['I_phase_peak_base_A']**2),
          energy_normalization_nominal_Wdc_J=.5*D['C_dc_F']*D['V_dc_initial_V']**2,
          energy_normalization_rated_WL_J=.75*(D['filter_L_H']+D['grid_L_H'])*D['I_phase_peak_base_A']**2),
        convergence_final_difference=report['checks'][-1]['max_normalized_cycle_difference'],
        full_qualification_checks=report['checks'],
        healthy_window_s=[healthy_start,t_cp],
        healthy_max_Ipu=float(healthy[:,ix['Ipu']].max()),
        healthy_max_pcc_apparent_VA=float(np.hypot(healthy[:,ix['Ppcc']],healthy[:,ix['Qpcc']]).max()),
        healthy_min_Vdcpu=float(healthy[:,ix['Vdcpu']].min()),
        healthy_max_Vdcpu=float(healthy[:,ix['Vdcpu']].max()),
        full_run_max_pcc_apparent_VA=float(s_all[kmax]),full_run_max_pcc_apparent_time_s=float(a[kmax,0]),
        observed_first_current_crossing_after_fault_s=report['fault_metrics']['first_actual_current_crossing_s']-TF,
        observed_dc_stop_after_fault_s=report['last_time_s']-TF,
        observed_actual_current_peak_pu=report['fault_metrics']['max_actual_current_pu'],
        observed_stop_reason=report['stop_reason'],
        healthy_electrical_controller_cycle_is_not_closed_battery_energy_orbit=True)
    return state,audit

'''
s=s[:start]+reader+s[end:]
s=s.replace("Vs = next(x['event']['retained_voltage_pu'] for x in D['case_registry'] if x['id']=='reference_clip_counterexample')", "Vs = D['prerun_convergence']['retained_source_voltage_pu']")
s=s.replace('816000','815600').replace('21918','21915').replace('277','276')
s=s.replace('assert conservative_margin > 600','assert conservative_margin > 590')
s=s.replace("'Model-conditioned analytic any-current-safe-policy DC-overvoltage obstruction; no full safety claim'", "'V2.1: analytic any-current-safe-policy DC obstruction from first preregistered converged checkpoint plus 50 us; no full safety claim'")
s=s.replace("'The certificate starts at the declared 0.20005 s common physical state; it is not a safety certificate for sampled startup.'", "'The certificate starts at the exact 0.60005 s fault-onset state, 50 us after the first preregistered 0.6 s converged checkpoint; it does not certify sampled startup.'")
s=s.replace('17.035 ms','17.088 ms')
s=s.replace('20 ms contradiction has >600 J margin.','20 ms contradiction has >590 J margin.')
(base/'recovered_source/dc_bound_gate_a_v2_1.py').write_text(s)
