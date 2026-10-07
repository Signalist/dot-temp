"""Read-only driver/scoring review plus completed-artifact reconciliation.
No call to run(), solver, plant RHS, or integration. No physical state is produced.
"""
from pathlib import Path
import ast
import copy
import cmath
import gzip
import hashlib
import json
import math
import tempfile
from unittest.mock import patch
import numpy as np
import run_models as rm
from audit_algebra_oracle import AlgebraOracle, as_complex, as_real, state

HERE=Path(__file__).resolve().parent
EXPECTED='9e4ca7f83570e6e62bf7f3fef9096cde5c44782a0ca7b27026dcd47978662eae'


def close(a,b,atol=1e-9,rtol=1e-11):
    np.testing.assert_allclose(a,b,atol=atol,rtol=rtol)


def static_checks():
    actual=hashlib.sha256((HERE/'run_models.py').read_bytes()).hexdigest()
    assert actual==EXPECTED
    source=(HERE/'run_models.py').read_text()
    tree=ast.parse(source)
    rowfun=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='row_margins')
    ns={'np':np}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[rowfun],type_ignores=[])),str(HERE/'run_models.py'),'exec'),ns)
    a=np.zeros(26);a[14]=1.01;a[15]=1.05;a[23]=.6;a[16]=970000.;a[17]=900000.;a[4]=-900000.
    expected=np.array([-.01,.09,.25,.05,.4,.2,1-970000/950000,1+970000/950000,
                       1-math.hypot(970000,900000)/1.2e6,1.9,.1])
    close(ns['row_margins'](a),expected,atol=1e-14,rtol=0)
    # No call to measure/controller is present: margins use the saved left/right row.
    assert not any(isinstance(n,ast.Name) and n.id in {'measure','signals','ctl'} for n in ast.walk(rowfun))
    # Deliberately huge simulation timestamps cannot enter wall-time aggregation.
    timing=rm.TimingSummary()
    log={'sample_k':321,'time_s':9999.,'observation':{'phase_origin_time_s':8888.,'causal_phase_rad':7777.},
         'solver':{'success_flag':False,'accepted_suboptimal':True,'timing':{'setup_s':.001,'solve_s':.002,'validation_s':.003,'point_total_s':.006}},
         'selection':{'type':'shifted_plan','plan_index':9},'total_wall_s':.007}
    timing.add(log,.008)
    tr=timing.result()
    assert len(tr['seconds'])==6 and max(x['maximum_s'] for x in tr['seconds'].values())==.008
    assert tr['counts']=={'calls':1,'guard_failures':0,'solver_success_false':1,'backup_calls':1,'accepted_nonoptimal_calls':1}
    f,_,_,_,_,_=rm.load_design('C0-slow')
    case={x['id']:x for x in f['execution_order']}
    admission=[]
    with tempfile.TemporaryDirectory(prefix='g3_runner_audit_') as temp:
        with patch.object(rm,'OUTPUT',Path(temp)):
            rm.check_run_admission(f,case['C0-slow'],1e-5)
            for cid in ['C0-fast','C50-slow','C50-fast','C1-slow','C1-fast']:
                try:rm.check_run_admission(f,case[cid],1e-5)
                except RuntimeError:admission.append(cid+':blocked_before_C0')
                else:raise AssertionError(cid)
            Path(temp,'C0-slow_h1e-05.json').write_text(json.dumps({'no_fault_physical_admission':False}))
            rm.check_run_admission(f,case['C0-fast'],1e-5)
            Path(temp,'C0-fast_h1e-05.json').write_text(json.dumps({'no_fault_physical_admission':True}))
            try:rm.check_run_admission(f,case['C50-slow'],1e-5)
            except RuntimeError:admission.append('failed_slow_fault_blocked')
            else:raise AssertionError('failed slow port admitted')
            rm.check_run_admission(f,case['C50-fast'],1e-5)
            try:rm.check_run_admission(f,case['C1-fast'],1e-5)
            except RuntimeError:admission.append('admitted_port_declared_order_enforced')
            else:raise AssertionError('C1-fast ran before C50-fast')
            try:rm.check_run_admission(f,case['C0-slow'],5e-6)
            except RuntimeError:admission.append('unindicated_refinement_blocked')
            else:raise AssertionError('unindicated refinement')
            Path(temp,'C0-slow_h1e-05.json').write_text(json.dumps({'no_fault_physical_admission':False,'numerical_refinement_indicated':True}))
            rm.check_run_admission(f,case['C0-slow'],5e-6)
            Path(temp,'C0-slow_h5e-06.started.json').write_text('{}')
            try:rm.check_run_admission(f,case['C0-slow'],5e-6)
            except RuntimeError:admission.append('previous_started_evidence_not_overwritten')
            else:raise AssertionError('overwrite')
    # Every requested clock tick and exact off-grid final time are algebraically consistent.
    clocks=[]
    for c in f['execution_order']:
        ts=np.array([k*1e-4 for k in range(6000,int(np.ceil(c['end_time_s']/1e-4)))])
        assert np.all(np.abs(np.diff(ts)-1e-4)<1e-14)
        relative=np.round((ts-.6)/1e-4).astype(int)
        assert np.array_equal(relative,np.arange(len(ts)))
        clocks.append({'case':c['id'],'sample_count_if_completed':len(ts),'last_sample_s':float(ts[-1]),'exact_planned_end_s':c['end_time_s']})
    return {'status':'PASS_STATIC_FUNCTION_CHECKS','runner_sha256':actual,
            'saved_left_right_row_margins_checked':True,'timing_excludes_simulation_clock':tr,
            'admission_negative_checks':admission,'clock_algebra':clocks}


def artifact_check(path):
    summary=json.loads(path.read_text())
    npz=path.parent/summary['trace_file'];rawpath=path.parent/summary['full_sample_log_file']
    assert hashlib.sha256(npz.read_bytes()).hexdigest()==summary['trace_sha256']
    assert hashlib.sha256(rawpath.read_bytes()).hexdigest()==summary['full_sample_log_sha256']
    assert summary['runner_source_sha256']==EXPECTED
    with np.load(npz,allow_pickle=False) as data:
        ep=data['endpoint_trace'].copy();iv=data['interval_extrema'].copy();ct=data['control'].copy()
        ns=data['normalized_state'].copy();dense=data['dense_trace'].copy();yf=data['final_plant_state'].copy();y0=data['initial_plant_state'].copy()
        assert data['endpoint_columns'].tolist()==rm.COLS
        assert data['interval_columns'].tolist()==rm.INTERVAL_COLS
        assert data['control_columns'].tolist()==rm.CONTROL_COLS
        assert data['normalized_columns'].tolist()==rm.NORMALIZED_NAMES
        lastctl=json.loads(str(data['full_controller_json']))
    assert len(ep)==len(iv)+1
    assert len(ct)==summary['accepted_control_count']
    close(yf,summary['final_plant_state'],atol=0,rtol=0)
    close(y0,summary['initial_plant_state'],atol=0,rtol=0)
    assert lastctl==summary['final_controller']
    assert abs(ep[-1,0]-summary['final_time_s'])<1e-12
    close(ep[-1,1:14],yf,atol=0,rtol=0)
    for key,col,op in [('I_peak_pu',2,max),('Vdc_min_pu',3,min),('Vdc_max_pu',4,max),
                       ('S_peak_VA',5,max),('P_abs_peak_W',6,max),('Pb_abs_peak_W',7,max),
                       ('soc_min',8,min),('soc_max',9,max),('energy_residual_max_J',11,max)]:
        epcol={'I_peak_pu':14,'Vdc_min_pu':15,'Vdc_max_pu':15,'Pb_abs_peak_W':4,'soc_min':23,'soc_max':23,'energy_residual_max_J':22}.get(key)
        if key=='S_peak_VA':values=np.hypot(ep[:,16],ep[:,17])
        elif key=='P_abs_peak_W':values=np.abs(ep[:,16])
        else:
            values=ep[:,epcol]
            if key in ['Pb_abs_peak_W','energy_residual_max_J']:values=np.abs(values)
        predicted=float(op(op(values),op(iv[:,col]))) if len(iv) else float(op(values))
        close(predicted,summary['metrics'][key],atol=1e-8)
    duration=summary['final_time_s']-.6;dy=yf-y0
    for key,val in {'duration_s':duration,'P_actual_integral_J':dy[7],'Q_actual_integral_var_s':dy[8],
                    'P_signed_request_error_integral_J':dy[7]-800000*duration,'Q_signed_request_error_integral_var_s':dy[8]-700000*duration,
                    'P_absolute_request_error_integral_J':dy[11],'Q_absolute_request_error_integral_var_s':dy[12]}.items():
        close(summary['service'][key],val,atol=1e-8)
    oracle=AlgebraOracle();d=oracle.d;ebase=d['battery_energy_MWh']*3.6e9
    wl=lambda y:.75*oracle.L*(y[0]**2+y[1]**2)
    expected_inventory={'initial_soc':d['soc_initial']+y0[4]/ebase,'final_soc':d['soc_initial']+yf[4]/ebase,
                        'battery_stored_energy_change_J':dy[4],'DC_energy_change_J':dy[2],
                        'RL_energy_change_J':wl(yf)-wl(y0),'remote_source_active_integral_J':dy[5],
                        'total_loss_integral_J':dy[6],'battery_terminal_power_integral_J':dy[9],
                        'battery_draw_integral_J':dy[10],'initial_Pb_W':y0[3],'final_Pb_W':yf[3]}
    for key,value in expected_inventory.items():close(summary['inventory'][key],value,atol=1e-8)
    independently_computed_energy=ep[:,5]-y0[4]+ep[:,3]-y0[2]+.75*oracle.L*(ep[:,1]**2+ep[:,2]**2)-wl(y0)+ep[:,6]-y0[5]+ep[:,7]-y0[6]
    close(ep[:,22],independently_computed_energy,atol=1e-8,rtol=0)
    close(ep[:,15],np.sqrt(2*ep[:,3]/d['C_dc_F'])/d['V_dc_initial_V'],atol=1e-14,rtol=0)
    close(ep[:,23],d['soc_initial']+ep[:,5]/ebase,atol=1e-14,rtol=0)
    updates=intervals=failures=0;contacts=[];header=None;terminal=None;end_before=None;old_ctl=None
    outer=[];guardwall=[];solvewall=[];maxaw=0.;selections={};nonoptimal=0;failedsolvers=0
    oracle=AlgebraOracle();pending=None
    tube={'complete_sample_transitions':0,'partial_intervals_excluded':0,'max_witness_disk_norm':0.,
          'max_witness_disk_excess':-math.inf,'max_inverse_residual':0.,'numeric_membership_failures':[],
          'max_exact_terminal_disk_excess':None,'dense_nodes_checked':0,'dense_intervals_checked':0,
          'maximum_observed_hold_current_error_pu':0.,'max_observed_error_minus_tube_radius':-math.inf,
          'dense_tube_failures':[]}
    assert np.all(np.diff(dense[:,0])>=-1e-12) if len(dense) else True
    with gzip.open(rawpath,'rt') as stream:
        for line in stream:
            r=json.loads(line);kind=r['record']
            if kind=='run_header':header=r;continue
            if kind in ['sample_update','guard_failure']:
                assert abs(r['time_s']-r['k']*1e-4)<1e-12
                if end_before is not None:
                    close(r['plant_pre'],end_before,atol=0,rtol=0)
                    assert r['controller_pre']==old_ctl
                g=r['guard'];obs=g['observation'];phi=obs['phase_origin_rad']+header['physical_parameters']['omega_base_rad_s']*(r['time_s']-obs['phase_origin_time_s'])
                close(phi,obs['causal_phase_rad'],atol=1e-13,rtol=0)
                assert g['sample_k']==r['k']-6000
                outer.append(r['controller_total_wall_s_including_PI_guard_AW'])
                if 'total_wall_s' in g:guardwall.append(g['total_wall_s'])
                if 'solver' in g:
                    solvewall.append(g['solver']['timing']['solve_s'])
                    failedsolvers+=int(g['solver']['success_flag'] is False)
                    nonoptimal+=int(g['solver'].get('accepted_suboptimal',False))
                if kind=='guard_failure':
                    failures+=1
                    assert r['prestate_preserved'] and r['controller_pre']==r['controller_after_exception']
                    close(r['plant_pre'],r['plant_after_exception'],atol=0,rtol=0)
                    continue
                close(r['plant_pre'],r['plant_post_update'],atol=0,rtol=0)
                pre,post=r['controller_pre'],r['controller_post_update']
                assert post['applied']==pre['queued'] and post['queued']==r['m_safe']
                assert all(r['interface_checks'][key] for key in ['plant_unchanged','old_queue_promoted','field_whitelist_unchanged','source_PLL_equal_nominal','all_values_finite','cc_eight_columns'])
                maxaw=max(maxaw,r['interface_checks']['antiwindup_absolute_error'])
                assert r['interface_checks']['antiwindup_absolute_error']<=1e-8
                mode=g['selection']['type'];selections[mode]=selections.get(mode,0)+1
                if mode=='optimized':assert g['solver']['independent_primal']['accepted']
                else:assert g['selection']['valid']
                p=r['certified_backup_plan'];assert p['backup_ready'] and p['primal_validation']['accepted']
                assert p['phase_origin_rad']==obs['phase_origin_rad'] and p['phase_origin_time_s']==obs['phase_origin_time_s']
                close(ct[updates],r['control']+[float(x) for x in ct[updates,8:]],atol=0,rtol=0)
                delta=abs(as_complex(r['m_safe'])-as_complex(r['m_nom']))
                close(ct[updates,-1],delta,atol=1e-14,rtol=0)
                assert bool(ct[updates,12])==(delta>1e-10)
                updates+=1
                pending=r
            elif kind=='sample_interval':
                close(r['endpoint'],ep[intervals+1],atol=0,rtol=0)
                close(r['interval_extrema'],iv[intervals],atol=0,rtol=0)
                close(r['normalized_post'],ns[intervals+1,1:],atol=0,rtol=0)
                close(r['plant_post'],r['endpoint'][1:14],atol=0,rtol=0)
                row=np.array(r['endpoint']);i=complex(row[1],row[2]);vdc=math.sqrt(2*row[3]/d['C_dc_F'])
                u=as_complex(r['controller_post']['applied'])*vdc*cmath.exp(-1j*oracle.omega*row[0])
                vp=(d['grid_L_H']*(u-d['filter_R_ohm']*i)+d['filter_L_H']*(oracle.Ebase*row[24]+d['grid_R_ohm']*i))/oracle.L
                power=1.5*vp*i.conjugate()
                close([row[16],row[17],row[19]],[power.real,power.imag,1.5*(u*i.conjugate()).real],atol=2e-8)
                close(row[14],abs(i)/oracle.Ibase,atol=1e-14,rtol=0)
                assert pending is not None and pending['k']==r['k']
                selection=pending['guard']['selection'];p=pending['certified_backup_plan']
                j=selection['plan_index'];z=np.array(p['z']);tt=pending['time_s'];end=r['end_s']
                obs=pending['guard']['observation']
                phi0=obs['causal_phase_rad'];phi_end=obs['phase_origin_rad']+oracle.omega*(end-obs['phase_origin_time_s'])
                if abs(end-tt-oracle.Ts)<1e-12:
                    y=np.array(r['plant_post']);queue=as_complex(r['controller_post']['queued'])
                    inext=complex(y[0],y[1])*cmath.exp(1j*(oracle.omega*end-phi_end))/oracle.Ibase
                    qnext=queue*cmath.exp(-1j*phi_end)
                    snext=state(inext,qnext)
                    nextcenter=z[j+1] if j<oracle.N else oracle.sbar
                    witness=oracle.omega_inverse(snext-nextcenter)
                    excess=max(witness['disk_norms'])-oracle.r
                    tube['complete_sample_transitions']+=1
                    tube['max_witness_disk_norm']=max(tube['max_witness_disk_norm'],max(witness['disk_norms']))
                    tube['max_witness_disk_excess']=max(tube['max_witness_disk_excess'],excess)
                    tube['max_inverse_residual']=max(tube['max_inverse_residual'],witness['representation_residual_inf'])
                    if not witness['inside']:tube['numeric_membership_failures'].append({'k':r['k'],'t_next':end,'plan_index':j,'witness':witness})
                    if j>=oracle.N-1:
                        terminal_excess=max(oracle.omega_inverse(snext-oracle.sbar)['disk_norms'])-oracle.r
                        prev=tube['max_exact_terminal_disk_excess']
                        tube['max_exact_terminal_disk_excess']=terminal_excess if prev is None else max(prev,terminal_excess)
                else:tube['partial_intervals_excluded']+=1
                if r['dense_retained']:
                    tube['dense_intervals_checked']+=1
                    lo=np.searchsorted(dense[:,0],tt-1e-12);hi=np.searchsorted(dense[:,0],end+1e-12,side='right')
                    center=z[j] if j<oracle.N else oracle.sbar
                    for node in dense[lo:hi]:
                        tau=min(max(node[0]-tt,0.),oracle.Ts)
                        ia=complex(node[1],node[2])*cmath.exp(1j*(oracle.omega*node[0]-phi0))/oracle.Ibase
                        error=abs(ia-oracle.flow(center,tau));excess=error-oracle.current_radius
                        tube['dense_nodes_checked']+=1
                        tube['maximum_observed_hold_current_error_pu']=max(tube['maximum_observed_hold_current_error_pu'],error)
                        tube['max_observed_error_minus_tube_radius']=max(tube['max_observed_error_minus_tube_radius'],excess)
                        if excess>1e-8:tube['dense_tube_failures'].append({'k':r['k'],'node_time':float(node[0]),'error':error,'excess':excess})
                end_before=r['plant_post'];old_ctl=r['controller_post'];intervals+=1;pending=None
            elif kind=='hard_contact':contacts.append(r)
            elif kind=='run_terminal':terminal=r
    assert header and terminal
    assert not tube['numeric_membership_failures'],tube['numeric_membership_failures'][:2]
    assert not tube['dense_tube_failures'],tube['dense_tube_failures'][:2]
    for key in ['max_witness_disk_excess','max_observed_error_minus_tube_radius']:
        if not math.isfinite(tube[key]):tube[key]=None
    assert updates==len(ct) and intervals==len(iv)
    assert terminal['stop_reason']==summary['stop_reason']
    assert terminal['time_s']==summary['final_time_s']
    assert terminal['controller']==summary['final_controller']
    close(terminal['plant_state'],yf,atol=0,rtol=0)
    assert len(contacts)==len(summary['all_hard_contacts'])
    for a,b in zip(contacts,summary['all_hard_contacts']):
        assert {k:v for k,v in a.items() if k!='record'}==b
    timing=summary['timing']
    assert timing['counts']['calls']==updates+failures
    assert timing['counts']['guard_failures']==failures
    assert timing['counts']['solver_success_false']==failedsolvers
    assert timing['counts']['accepted_nonoptimal_calls']==nonoptimal
    for key,values in [('controller_total_wall_s_including_PI_guard_AW',outer),('total_wall_s',guardwall),('solver.timing.solve_s',solvewall)]:
        if not values:continue
        x=timing['seconds'][key]
        assert x['n']==len(values) and x['over_100us_count']==sum(v>1e-4 for v in values)
        close(x['sum_s'],sum(values),atol=1e-8)
        close(x['median_s'],np.median(values),atol=1e-14)
        close(x['p95_s'],np.percentile(values,95),atol=1e-14)
    if summary['event'] is None:
        expected_admission=bool(summary['simulation_completed'] and not contacts and not summary['first_observed_beyond_roundoff'] and failures==0)
        assert summary['no_fault_physical_admission']==expected_admission
    boundary_rate=None
    if summary['stop_reason']=='dc_high':
        final_i=complex(*yf[:2]);vdc=math.sqrt(2*yf[2]/d['C_dc_F'])
        final_u=as_complex(summary['final_controller']['applied'])*vdc*cmath.exp(-1j*oracle.omega*summary['final_time_s'])
        pinv=1.5*(final_u*final_i.conjugate()).real
        pbus=d['eta_dc_dc']*yf[3] if yf[3]>=0 else yf[3]/d['eta_dc_dc']
        loss=d['inverter_loss_constant_W']+d['inverter_loss_current_squared_W_at_1pu']*(abs(final_i)/oracle.Ibase)**2
        boundary_rate=pbus-pinv-loss
        assert boundary_rate>0,'Reported high-DC root is not an outward crossing'
    energy_audit={'status':'NOT_APPLICABLE_NO_FAULT'}
    if summary['event'] is not None:
        stored=summary['actual_onset_energy_necessary_condition']
        if stored['status']=='RECOMPUTED_FROM_ACTUAL_ONSET':
            onset=np.array(stored['onset_full_plant_state']);event=summary['event']
            H=.5*d['C_dc_F']*(d['V_dc_max_pu']*d['V_dc_initial_V'])**2+.75*oracle.L*oracle.Ibase**2-onset[2]-wl(onset)
            exit_upper=1.5*oracle.Ebase*event['retained_source_pu']*oracle.Ibase+d['inverter_loss_constant_W']+d['inverter_loss_current_squared_W_at_1pu']+1.5*oracle.R*oracle.Ibase**2
            rate=summary['source_ramp_W_per_s'];a=d['eta_dc_dc']*onset[3]-exit_upper;b=d['eta_dc_dc']*rate
            horizon=min(event['end_s']-event['start_s'],max(0.,onset[3]/rate));peak=min(horizon,max(0.,a/b));gain=a*peak-.5*b*peak**2
            crossing=None
            if H<=0:crossing=0.
            elif peak>0 and gain>=H:crossing=2*H/(a+math.sqrt(a*a-2*b*H))
            for key,value in [('aggregate_headroom_J',H),('exit_upper_W',exit_upper),('maximum_prefix_gain_J',gain)]:close(stored[key],value,atol=1e-8)
            assert stored['excludes_all_actual_I_DC_safe_control']==(gain>H)
            if crossing is None:assert stored['first_headroom_equality_after_fault_s'] is None
            else:close(stored['first_headroom_equality_after_fault_s'],crossing,atol=1e-12,rtol=0)
            energy_audit={'status':'PASS_INDEPENDENT_ALGEBRA','headroom_J':H,'maximum_prefix_gain_J':gain,
                          'obstruction_after_fault_s':crossing,'excludes_all_safe_control':bool(gain>H)}
    return {'case':summary['case'],'h_s':summary['h_s'],'summary_file':path.name,'status':'PASS_COMPLETED_ARTIFACT_RECONCILIATION','updates':updates,'intervals':intervals,
            'guard_failures':failures,'contacts':len(contacts),'independent_inventory_energy_and_endpoint_power_checks':True,'stop_reason':summary['stop_reason'],
            'final_time_s':summary['final_time_s'],'no_fault_admission':summary['no_fault_physical_admission'],
            'selection_counts':selections,'max_antiwindup_error':maxaw,'terminal_DC_energy_derivative_W':boundary_rate,'energy_necessary_condition_independent':energy_audit,'observed_next_step_and_dense_tube_check':tube,'raw_sha256':summary['full_sample_log_sha256'],
            'trace_sha256':summary['trace_sha256']}


def main():
    out={'static':static_checks(),'completed_artifacts':[],'physical_trajectories_executed_by_audit':0}
    for case in ['C0-slow','C0-fast','C50-slow','C50-fast','C1-slow','C1-fast']:
        for h in ['1e-05','5e-06']:
            p=HERE/'results'/f'{case}_h{h}.json'
            if p.exists():out['completed_artifacts'].append(artifact_check(p))
    (HERE/'audit_runner_results.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
