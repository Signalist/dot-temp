"""Read-only onset/clearance electrical-jump and 150ms service/energy audit.
No ODE or new trajectory. Exact event states and retained numerical nodes only.
"""
from pathlib import Path
import argparse,cmath,gzip,hashlib,json,math,sys
sys.dont_write_bytecode=True
import numpy as np
from unittest.mock import patch
import audit_artifact_checks as audit
rm=audit.rm
HERE=Path(__file__).resolve().parent

def check(path):
    q=json.loads(path.read_text());assert q['event'] is not None
    _,_,case,d,_,cp=rm.load_design(q['case']);ev=case['event']
    a,b=ev['start_s'],ev['end_s'];assert a==.60005 and b==.75005
    with np.load(path.parent/q['trace_file'],allow_pickle=False) as archive: dense=archive['dense_trace'];iv=archive['interval_extrema']
    recorded={};sample=None
    with gzip.open(path.parent/q['full_sample_log_file'],'rt') as stream:
        for line in stream:
            r=json.loads(line)
            if r['record']=='sample_update':sample=r
            elif r['record']=='external_event_boundary':
                state={k:v for k,v in r.items() if k!='record'}
                assert state==q['event_boundary_states'][format(r['time_s'],'.12f')]
                assert sample is not None
                pre=sample['controller_post_update'];post=state['controller']
                for key in pre:
                    if key!='theta':assert pre[key]==post[key],key
                audit.close(post['theta'],pre['theta']+pre['omega']*(r['time_s']-sample['time_s']),atol=0,rtol=0)
                assert state['controller_theta_storage_before_advance']==pre['theta']
                # Events are strictly interior to a 100us hold, with no sample reset.
                assert 0<r['time_s']-sample['time_s']<1e-4
                recorded[r['time_s']]=state
                if len(recorded)==2:break
    assert set(recorded)=={a,b}
    bounds=[];lf,lg,rf,rg=[d[k] for k in ['filter_L_H','grid_L_H','filter_R_ohm','grid_R_ohm']]
    for t,source_left,source_right in [(a,1.,.4),(b,.4,1.)]:
        event=recorded[t];y=np.array(event['plant_state']);ctl=audit.unserial(event['controller'])
        assert (event['source_left_pu'],event['source_right_pu'])==(source_left,source_right)
        rows=dense[dense[:,0]==t]
        assert len(rows)>=2 and set(rows[:,24])=={source_left,source_right}
        assert all(np.array_equal(row[1:14],y) for row in rows),'Any event state jump invalidates continuity'
        current=complex(*y[:2]);vdc=math.sqrt(2*y[2]/d['C_dc_F'])
        u=ctl['applied']*vdc*cmath.exp(-1j*d['omega_base_rad_s']*t)
        sides={}
        for vs in [source_left,source_right]:
            vp=(lg*(u-rf*current)+lf*(d['V_phase_peak_base_V']*vs+rg*current))/(lf+lg)
            power=1.5*vp*current.conjugate();psrc=1.5*d['V_phase_peak_base_V']*vs*current.real
            selected=rows[rows[:,24]==vs]
            for row in selected:
                audit.close([row[16],row[17],row[18],row[19],row[20]],[power.real,power.imag,abs(vp)/d['V_phase_peak_base_V'],1.5*(u*current.conjugate()).real,psrc],atol=2e-8,rtol=1e-11)
            sides[str(vs)]={'P_W':power.real,'Q_var':power.imag,'V_PCC_pu':abs(vp)/d['V_phase_peak_base_V'],'source_P_W':psrc}
        direct_jump=1.5*(lf/(lf+lg))*d['V_phase_peak_base_V']*(source_right-source_left)*current.conjugate()
        left=sides[str(source_left)];right=sides[str(source_right)]
        audit.close([right['P_W']-left['P_W'],right['Q_var']-left['Q_var']],[direct_jump.real,direct_jump.imag],atol=2e-8,rtol=1e-11)
        bounds.append({'time_s':t,'state_and_integrator_continuity_exact':True,'held_applied_and_queued_unchanged':True,'no_extra_control_sample':True,'left':left,'right':right,'P_jump_W':direct_jump.real,'Q_jump_var':direct_jump.imag,'dense_exact_boundary_rows':len(rows)})
    onset=np.array(recorded[a]['plant_state']);clear=np.array(recorded[b]['plant_state']);dy=clear-onset;duration=b-a
    service={'duration_s':duration,'P_actual_integral_J':dy[7],'Q_actual_integral_var_s':dy[8],'mean_P_W':dy[7]/duration,'mean_Q_var':dy[8]/duration,'P_signed_request_error_J':dy[7]-800000*duration,'Q_signed_request_error_var_s':dy[8]-700000*duration,'P_absolute_request_error_J':dy[11],'Q_absolute_request_error_var_s':dy[12]}
    wl=lambda y:.75*(lf+lg)*(y[0]**2+y[1]**2)
    energy={'battery_stored_change_J':dy[4],'DC_change_J':dy[2],'RL_change_J':wl(clear)-wl(onset),'remote_source_integral_J':dy[5],'loss_integral_J':dy[6],'battery_terminal_integral_J':dy[9],'battery_draw_integral_J':dy[10]}
    residual=dy[4]+dy[2]+wl(clear)-wl(onset)+dy[5]+dy[6]
    assert abs(residual)<1e-5,residual
    energy['conservation_residual_J']=residual
    # Fault-level retained data contain both exact onset-right and clearance-left.
    f=dense[(dense[:,0]>=a)&(dense[:,0]<=b)&(dense[:,24]==.4)]
    # Keep duplicate-time left/right samples: voltage promotion can jump P/Q
    # while physical states stay continuous. Deduplication would smear a hold.
    assert np.min(np.diff(f[:,0]))>=0
    assert f[0,0]==a and f[-1,0]==b
    p_approx=np.trapezoid(f[:,16],f[:,0]);q_approx=np.trapezoid(f[:,17],f[:,0])
    selected=iv[(iv[:,0]<b)&(iv[:,1]>a)]
    assert len(selected)==1501 and selected[0,0]==.6 and selected[-1,1]==.7501
    return {'case':q['case'],'status':'PASS_EVENT_CONTINUITY_JUMP_AND_FAULT_QUADRATURE','summary_sha256':audit.sha(path),'boundaries':bounds,'actual_fault_service':service,'actual_fault_energy':energy,'dense_trapezoid_sanity_only':{'nodes_including_left_right_samples':len(f),'P_integral_J':p_approx,'Q_integral_var_s':q_approx,'P_difference_from_integrated_quadrature_J':p_approx-dy[7],'Q_difference_from_integrated_quadrature_var_s':q_approx-dy[8],'note':'Descriptive numerical cross-check retaining all left/right hold jumps; exact service uses saved ODE quadrature states at split boundaries.'},'sample_intervals_overlapping_fault':len(selected),'hard_contacts_total':len(q['all_hard_contacts']),'full_case_complete_hard_safe':q['complete_hard_safe'],'event_splits_exact':True,'no_physical_projection_or_boundary_reset_observed':True}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--case',choices=['P50-fast','R50-fast']);args=parser.parse_args()
    output=HERE/'audit_event_results.json';old=json.loads(output.read_text()) if output.exists() else {};rows={r['case']:r for r in old.get('results',[])}
    with patch.object(rm,'run',audit.forbidden),patch.object(rm,'rhs',audit.forbidden),patch.object(rm,'solve_ivp',audit.forbidden),patch.object(audit.cg,'minimize',audit.forbidden):
        for cid in ([args.case] if args.case else ['P50-fast','R50-fast']):
            path=HERE/'results'/f'{cid}_h1e-05.json'
            if path.exists():rows[cid]=check(path)
    out={'status':'PASS_AVAILABLE_FAULT_BOUNDARIES','results':list(rows.values()),'physical_trajectories_executed':0,'real_optimization_calls':0,'source_sha256':audit.sha(__file__),'pending_faults':[cid for cid in ['P50-fast','R50-fast'] if cid not in rows]}
    output.write_text(json.dumps(audit.plain(out),indent=2,allow_nan=False)+'\n')
    print(json.dumps(audit.plain(out),indent=2))
if __name__=='__main__':main()
