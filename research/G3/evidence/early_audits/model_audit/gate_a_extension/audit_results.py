"""Read-only audit of the new Gate A abc results. No plant integration."""
from pathlib import Path
import hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=[]
for stem in ['sag085_10us','sag0475_10us','sag0475_5us']:
    jp=HERE/'results'/f'{stem}.json';npz=jp.with_suffix('.npz');s=json.loads(jp.read_text());z=np.load(npz);a=z['trace'];c=z['control'];cols=z['columns'].tolist();cc=z['control_columns'].tolist()
    assert a.shape[1]==len(cols) and c.shape[1]==len(cc)
    assert np.isfinite(a).all() and np.isfinite(c).all() and sha(npz)==s['npz_sha256']
    post=c[c[:,cc.index('side')]==1];bits=post[:,cc.index('limiter_bits')].astype(int);tt=post[:,0]
    release={};events={}
    for i,name in enumerate(s['recovery']['formal_limiter_names']):
        active=(bits&(1<<i))!=0;ev=[]
        for k in range(1,len(tt)):
            if active[k]!=active[k-1]:ev.append({'t_s':float(tt[k]),'active':bool(active[k])})
        released=[e['t_s'] for e in ev if not e['active']]
        release[name]=None if active[-1] or not released else released[-1]
        events[name]={'ever_active':bool(active.any()),'active_at_final_record':bool(active[-1]),'transitions':ev,'observed_last_release_time_s':release[name]}
    consecutive=0;first=None;checks=[]
    for q in s['recovery']['checks']:
        good=q['target_state_error']<=1e-5 and q['self_cycle_error'] is not None and q['self_cycle_error']<=1e-5
        consecutive=consecutive+1 if good else 0
        restored=consecutive>=3 and q['trailing_frequency_ok']
        safe=restored and q['trailing_window_safe'] and q['all_formal_limiters_released'] and q['all_post_checkpoint_safe']
        if safe and first is None:first=q['time_s']
        checks.append(dict(q,joint_target_and_cycle=good,consecutive_joint_checks=consecutive,joint_complete_safe_electrical_control_recovery=safe))
    m=np.hypot(c[:,cc.index('m_applied_alpha')],c[:,cc.index('m_applied_beta')]);mq=np.hypot(c[:,cc.index('m_queued_alpha')],c[:,cc.index('m_queued_beta')]);modmax=float(max(m.max(),mq.max()))
    threshold=1e-3; margins=s['normalized_min_limit_margin'];near=any(margins[k]<threshold for k in ['actual_current','dc_low','dc_high','Ppcc','Spcc'])
    row={'stem':stem,'case':s['case'],'step_s':s['h_max_s'],'simulation_status':s['status'],'simulated_end_s':s['final_time_s'],'event_clearance_s':s['clearance_s'],'complete_event_observed':s['final_time_s']>=s['clearance_s'],'current_peak_pu':s['actual_current_peak_pu'],'dc_min_pu':s['Vdc_min_pu'],'dc_max_pu':s['Vdc_max_pu'],'Ppcc_abs_peak_W':s['Ppcc_abs_peak_W'],'Spcc_peak_VA':s['Spcc_peak_VA'],'all_applied_and_queued_modulation_peak':modmax,'all_applied_and_queued_modulation_within_bound':modmax<=0.5484827557301445+1e-8,'safe_observed_prefix_with_roundoff':s['roundoff_safety_pass'],'strict_raw_safety_pass':s['strict_safety_pass'],'physical_boundary_stop':s['status']!='completed','raw_target_only_recovery_time_s':s['recovery']['complete_safe_recovery_time_s'],'authoritative_joint_electrical_control_recovery_time_s':first,'complete_safe_recovery':bool(first is not None and s['status']=='completed' and s['roundoff_safety_pass']),'recovery_delay_after_clearance_s':None if first is None else first-s['clearance_s'],'recovery_criterion_note':'Formal score additionally requires three consecutive joint target and 50ms self-cycle comparisons; both are derived from already simulated full abc trajectory, without rerun or extrapolation. Battery inventory is bounded and accounted, not restored.','limiter_transition_records':events,'corrected_observed_release_time_s':release,'release_summary_correction':'The raw summary last-active-plus-Ts estimate is not an observed release if the next sample never occurred; use these transition-derived fields. Raw JSON/NPZ retained unchanged.','near_boundary_refinement_trigger':near,'energy_residual_J':s['energy_residual_J'],'raw_schema_verified':True,'raw_rows':len(a),'control_rows':len(c),'source_json_sha256':sha(jp),'source_npz_sha256':sha(npz),'recovery_checks_joint':checks}
    rows.append(row)
coarse=np.load(HERE/'results/sag0475_10us.npz');fine=np.load(HERE/'results/sag0475_5us.npz');cc=coarse['control_columns'].tolist();nidx=[cc.index('norm'+str(i)) for i in range(14)];a=coarse['control'];b=fine['control'];assert a.shape==b.shape and np.max(np.abs(a[:,:2]-b[:,:2]))<1e-12
refinement={'same_checkpoint_and_controller':True,'normalized_control_state_max_difference':float(np.max(np.abs(a[:,nidx]-b[:,nidx]))),'DC_stop_time_difference_s':abs(rows[1]['simulated_end_s']-rows[2]['simulated_end_s']),'current_peak_difference_pu':abs(rows[1]['current_peak_pu']-rows[2]['current_peak_pu']),'both_stop_before_clearance':all(not r['complete_event_observed'] for r in rows[1:])}
comparison=[]
for r in rows:
    h='1e-05' if r['step_s']==1e-5 else '5e-06';p=ROOT/'gate_a_extension/results'/f"{r['case']}_h{h}.json"
    if not p.exists():continue
    d=json.loads(p.read_text());m=d['metrics'];current=abs(r['current_peak_pu']-m['max_actual_current_pu']);vmax=abs(r['dc_max_pu']-m['max_dc_pu']);vmin=abs(r['dc_min_pu']-m['min_dc_pu'])
    e=abs(r['simulated_end_s']-d['final_time_s']) if r['physical_boundary_stop'] else None
    comparison.append({'stem':r['stem'],'dq_result_sha256':sha(p),'current_peak_difference_pu':current,'Vdc_peak_difference_pu':vmax,'Vdc_min_difference_pu':vmin,'DC_stop_time_difference_s':e,'joint_electrical_control_recovery_time_abc_s':r['authoritative_joint_electrical_control_recovery_time_s'],'recovery_time_dq_s':d['recovered_time_s'],'event_or_recovery_time_matches':abs(e)<1e-9 if e is not None else r['authoritative_joint_electrical_control_recovery_time_s']==d['recovered_time_s'],'numerical_agreement_pass':current<1e-8 and vmax<1e-8 and vmin<1e-8 and (e is None or e<1e-9),'P_S_scope_note':'abc includes the checkpoint pre-update left side. For sag0475 the parent dq reported extrema begin after the initial sample update, so its P/S maxima exclude that initial point. This is a recorded observation-scope difference, not a current/voltage trajectory difference.','end_time_scope_note':'abc sag085 continues through clearance+2s; dq sag085 stops on successful joint recovery at1.3s.'})
out={'status':'audited_new_abc_extension','new_integration_performed_by_this_audit':False,'results':rows,'coarse_fine_comparison':refinement,'abc_dq_result_comparison':comparison,'signed_rhs_check':{'path':'signed_rhs_check.json','sha256':sha(HERE/'signed_rhs_check.json')},'periodic_coverage':'No independent abc periodic replay; only the separate signed algebra checks cover charge/discharge branches.','source_sha256':sha(__file__)}
(HERE/'authoritative_summary.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'rows':[{k:v for k,v in r.items() if k in ['stem','simulation_status','current_peak_pu','dc_max_pu','authoritative_joint_electrical_control_recovery_time_s','complete_safe_recovery','near_boundary_refinement_trigger','simulated_end_s']} for r in rows],'refinement':refinement,'abc_dq_comparison':comparison},indent=2))
