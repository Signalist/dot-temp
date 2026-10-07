"""Read-only completed-artifact reconciliation for frozen P/radial + common guard.
No run/RHS/integration/real optimizer call. Reuses sealed algebraic artifact
checks and adds independent full-sample allocator/AW/command/recovery checks.
"""
from pathlib import Path
import argparse
import cmath
import copy
import gzip
import hashlib
import importlib.util
import json
import math
import sys
sys.dont_write_bytecode=True
import time
import traceback
from unittest.mock import patch
import numpy as np

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'current_guard_gate1'));sys.path.insert(0,str(HERE))
import run_constructive as rm
import audit_interface_tests as interface
import common_guard as cg
from audit_algebra_oracle import AlgebraOracle,as_complex,as_real,state
EXPECTED_RUNNER='e9bceab631ec7f26c9639aa3a2887ddf21f8cefdd63390c76fbeb1d3d30563c5'
EXPECTED_WRAPPER='50f4b5f97cb8caad08463451e3dfe959528119cf10b140c78af57409608f52f6'
EXPECTED_LEGACY=''
LEGACY_PATH=ROOT/'current_guard_gate1/audit_runner_checks.py'
spec=importlib.util.spec_from_file_location('sealed_artifact_audit',LEGACY_PATH)
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
# In-memory parameterization only. The frozen old file remains unchanged.
legacy.rm=rm;legacy.EXPECTED=EXPECTED_RUNNER;legacy.HERE=HERE

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def forbidden(*a,**k):raise AssertionError('Physical/optimization execution is forbidden in artifact audit')
def close(a,b,atol=1e-8,rtol=1e-11):np.testing.assert_allclose(a,b,atol=atol,rtol=rtol)
def unserial(c):return {k:complex(*v) if isinstance(v,list) else v for k,v in c.items()}
def plain(v):
    if isinstance(v,dict):return {k:plain(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [plain(x) for x in v]
    if isinstance(v,np.generic):return v.item()
    return v

def compare_mapping(actual,expected):
    for k,v in expected.items():
        assert k in actual,k
        if isinstance(v,bool) or v is None or isinstance(v,str):assert actual[k]==v,(k,actual[k],v)
        elif isinstance(v,dict):compare_mapping(actual[k],v)
        elif isinstance(v,list):
            assert len(actual[k])==len(v),(k,len(actual[k]),len(v))
            for a,e in zip(actual[k],v):
                if isinstance(e,dict):compare_mapping(a,e)
                else:close(a,e)
        else:close(actual[k],v,atol=2e-10,rtol=1e-11)


def independent_recovery(summary,states,intervals,refstates,d):
    event=summary['event'];stored=summary['recovery']
    if event is None:
        compare_mapping(stored,{'status':'NOT_APPLICABLE_NO_FAULT','joint_recovery_time_s':None,'checks':[]})
        return {'status':'NOT_APPLICABLE_NO_FAULT'}
    if not summary['simulation_completed']:
        expected={'status':'NOT_SCORED_INCOMPLETE_TRAJECTORY','joint_recovery_time_s':None,'checks':[], 'clearance_observed':bool(states[-1,0]>=event['end_s'])}
        compare_mapping(stored,expected);return expected
    if refstates is None:
        expected={'status':'NOT_SCORED_REFERENCE_UNAVAILABLE','joint_recovery_time_s':None,'checks':[]}
        compare_mapping(stored,expected);return expected
    ts=d['control_sample_s'];period=round(.05/ts);checks=[];streak=0;recovery=None
    first=math.ceil((event['end_s']+.15-1e-12)/.05)
    last=math.floor((float(states[-1,0])+1e-11)/.05)
    for cycle in range(first,last+1):
        end=cycle*.05
        indices=np.where((states[:,0]>end-.05+1e-11)&(states[:,0]<=end+1e-11))[0]
        if len(indices)!=period or indices[0]<period:continue
        times=states[indices,0];rids=np.searchsorted(refstates[:,0],times-1e-11)
        if np.any(rids>=len(refstates)) or np.max(np.abs(refstates[rids,0]-times))>1e-10:continue
        selfdiff=float(np.max(np.abs(states[indices,1:]-states[indices-period,1:])))
        targetdiff=float(np.max(np.abs(states[indices,1:]-refstates[rids,1:])))
        window=intervals[(intervals[:,1]>end-.15+1e-11)&(intervals[:,1]<=end+1e-11)]
        covered=len(window)>=round(.15/ts) and window[0,0]<=end-.15+1e-10
        # Explicit all-resource hard margins; same frozen numerical tolerances.
        tests=[np.max(window[:,2])<=1+1e-8,np.min(window[:,3])>=.8-1e-8,np.max(window[:,4])<=1.1+1e-8,
               np.max(window[:,5])<=1.2e6*(1+1e-8),np.max(window[:,6])<=.95e6*(1+1e-8),np.max(window[:,7])<=1e6*(1+1e-8),
               np.min(window[:,8])>=.2-1e-8,np.max(window[:,9])<=.8+1e-8,np.max(window[:,17])<=d['svpwm_linear_voltage_derating']/math.sqrt(3)*(1+1e-8)] if len(window) else [False]
        safe=bool(covered and all(tests));free=bool(covered and not np.any(window[:,12:17]>.5))
        freq=float(np.max(window[:,10])) if len(window) else None
        good=bool(safe and free and selfdiff<=1e-5 and targetdiff<=1e-5 and freq is not None and freq<=.001)
        streak=streak+1 if good else 0
        checks.append({'time_s':end,'self_50ms_difference':selfdiff,'same_time_guarded_no_fault_difference':targetdiff,'safe_150ms':safe,'unclipped_including_guard_150ms':free,'PLL_max_error_Hz':freq,'qualifying':good,'successive':streak})
        if streak>=3 and recovery is None:recovery=end
    expected={'status':'SCORED_COMPLETED_TRAJECTORY','joint_recovery_time_s':recovery,'checks':checks,
              'global_safe_recovery':bool(summary['no_physical_hard_contact_up_to_stop'] and recovery is not None),'earlier_violation_cannot_be_erased':True,'battery_inventory_excluded_from_orbit':True}
    compare_mapping(stored,expected)
    failures={'self_cycle':0,'matched_target':0,'hard_safe_window':0,'unclipped_including_guard':0,'PLL_frequency':0}
    for row in checks:
        failures['self_cycle']+=int(row['self_50ms_difference']>1e-5)
        failures['matched_target']+=int(row['same_time_guarded_no_fault_difference']>1e-5)
        failures['hard_safe_window']+=int(not row['safe_150ms'])
        failures['unclipped_including_guard']+=int(not row['unclipped_including_guard_150ms'])
        failures['PLL_frequency']+=int(row['PLL_max_error_Hz'] is None or row['PLL_max_error_Hz']>.001)
    return {'status':'PASS_ALL_FROZEN_RECOVERY_SUBITEMS','checks_recomputed':len(checks),'joint_recovery_time_s':recovery,'global_safe_recovery':expected['global_safe_recovery'],'failed_subitem_counts':failures,'qualifying_count':sum(r['qualifying'] for r in checks),'last_check':checks[-1] if checks else None,'no_criterion_relaxed':True}


def independent_reference(summary,ep,ns,d):
    stored=summary['matched_reference'];policy=summary['allocator']
    if summary['event'] is None:
        assert stored['status']=='NOT_AVAILABLE' and stored['reference'] is None and stored['allocator']==policy
        return {'status':'PASS_NO_FABRICATED_HEALTHY_REFERENCE'},None
    cid={'p_priority':'P0-fast','radial':'R0-fast'}[policy]
    p=HERE/'results'/f'{cid}_h1e-05.json';ref=json.loads(p.read_text())
    assert ref['case']==cid and ref['allocator']==policy and ref['no_fault_physical_admission'] is True
    for k in ['protocol_sha256','controller_source_sha256','runner_source_sha256','guard_source_sha256','allocator_source_sha256','checkpoint_sha256','physical_protocol_sha256','source_tau_s','source_ramp_W_per_s','source_port','initial_time_s','initial_plant_state','initial_controller']:
        assert ref[k]==summary[k],k
    trace=p.parent/ref['trace_file'];assert sha(trace)==ref['trace_sha256']==stored['reference_sha256']
    assert sha(p)==stored['reference_summary_sha256']
    with np.load(trace,allow_pickle=False) as data:rp=data['endpoint_trace'];rn=data['normalized_state']
    assert np.array_equal(ep[0],rp[0]) and np.array_equal(ns[0],rn[0])
    end=min(ep[-1,0],rp[-1,0]);own=np.array([np.interp(end,ep[:,0],ep[:,j]) for j in range(ep.shape[1])]);other=np.array([np.interp(end,rp[:,0],rp[:,j]) for j in range(rp.shape[1])])
    idx={'P_integral_difference_J':8,'Q_integral_difference_var_s':9,'battery_stored_energy_difference_J':5,'DC_energy_difference_J':3,'remote_source_integral_difference_J':6,'total_loss_integral_difference_J':7,'P_absolute_error_integral_difference_J':12,'Q_absolute_error_integral_difference_var_s':13}
    expected={k:float(own[j]-other[j]) for k,j in idx.items()}
    expected.update(status='OBSERVED_COMMON_WINDOW_ONLY',reference='same_allocator_same_port_guarded_no_fault',reference_case=cid,allocator=policy,common_start_s=.6,common_end_s=end,full_observed_case_covered=bool(rp[-1,0]>=ep[-1,0]-1e-12),same_initial_7_state_exact=True,same_initial_normalized_full_state_exact=True,no_past_service_restoration_claim=True,RL_energy_difference_J=.75*(d['filter_L_H']+d['grid_L_H'])*(own[1]**2+own[2]**2-other[1]**2-other[2]**2))
    indices=np.searchsorted(rn[:,0],ns[:,0]-1e-11);mask=(indices<len(rn));mask[mask]=np.abs(rn[indices[mask],0]-ns[mask,0])<1e-10
    count=int(sum(mask));maximum=float(np.max(np.abs(ns[mask,1:]-rn[indices[mask],1:]))) if count else None
    expected.update(matched_sample_count=count,max_normalized_state_difference=maximum)
    compare_mapping(stored,expected)
    return {'status':'PASS_OWN_ALLOCATOR_REFERENCE_ALL_DIFFERENCES','reference_case':cid,'common_end_s':end,'matched_sample_count':count,'max_normalized_state_difference':maximum},rn


def root_margin(record,d):
    y=np.array(record['plant_state']);c=unserial(record['controller']);t=record['time_s'];vs=record['source_level_pu']
    current=complex(*y[:2]);vdc=math.sqrt(2*y[2]/d['C_dc_F']);u=c['applied']*vdc*cmath.exp(-1j*d['omega_base_rad_s']*t)
    vp=(d['grid_L_H']*(u-d['filter_R_ohm']*current)+d['filter_L_H']*(d['V_phase_peak_base_V']*vs+d['grid_R_ohm']*current))/(d['filter_L_H']+d['grid_L_H'])
    power=1.5*vp*current.conjugate();ipu=abs(current)/d['I_phase_peak_base_A'];vdpu=vdc/d['V_dc_initial_V'];soc=d['soc_initial']+y[4]/(d['battery_energy_MWh']*3.6e9)
    return {'actual_current':1-ipu,'actual_current_emergency':1.1-ipu,'dc_low':vdpu-.8,'dc_high':1.1-vdpu,'soc_low':soc-.2,'soc_high':.8-soc,'AC_P_positive':1-power.real/950000,'AC_P_negative':1+power.real/950000,'AC_S':1-abs(power)/1.2e6,'Pb_positive':1-y[3]/1e6,'Pb_negative':1+y[3]/1e6,'modulation':1-max(abs(c['applied']),abs(c['queued']))/(d['svpwm_linear_voltage_derating']/math.sqrt(3))}[record['name']]


def augmented_check(path):
    summary=json.loads(path.read_text());policy=summary['allocator'];case=summary['case']
    assert summary['runner_source_sha256']==EXPECTED_RUNNER and summary['controller_source_sha256']==EXPECTED_WRAPPER
    _,_,declared,d,_,cp=rm.load_design(case)
    assert summary['protocol_sha256']==rm.EXPECTED_PROTOCOL_SHA256 and summary['guard_source_sha256']==rm.EXPECTED_GUARD_SHA256 and summary['allocator_source_sha256']==rm.EXPECTED_ALLOCATOR_SHA256
    assert summary['event']==declared['event'] and policy==declared['allocator']
    assert summary['initial_controller']==cp['controller'] and summary['initial_plant_state']==cp['plant_state']+[0.]*6
    with np.load(path.parent/summary['trace_file'],allow_pickle=False) as data:
        ep=data['endpoint_trace'];ns=data['normalized_state'];iv=data['interval_extrema'];ct=data['control']
    o=AlgebraOracle();count=0;failed=0;plan_count=0;root_count=0;max_plan=0.;max_root=0.
    max_nominal=0.;max_aw=0.;max_command=0.;max_observation=0.;max_fullstate={};header=None
    request={'P_req_W':800000.,'Q_req_var':700000.}
    with gzip.open(path.parent/summary['full_sample_log_file'],'rt') as stream:
        for line in stream:
            row=json.loads(line);kind=row['record']
            if kind=='run_header':
                header=row;assert row['physical_parameters']==d and row['case']==declared
                assert row['same_full_checkpoint']==cp and row['control_sample_s']==1e-4
                assert row['max_step_s']==summary['h_s'];continue
            if kind=='hard_contact':
                margin=root_margin(row,d);root_count+=1
                if row['kind']=='continuous_event_root':
                    max_root=max(max_root,abs(margin));assert abs(margin)<1e-7,(row['name'],margin)
                elif row['normalized_margin'] is not None:close(margin,row['normalized_margin'],atol=2e-9,rtol=1e-10)
                continue
            if kind not in ('sample_update','guard_failure'):continue
            t=row['time_s'];pre=unserial(row['controller_pre']);y=np.array(row['plant_pre'])
            event=declared['event'];vs=event['retained_source_pu'] if event and event['start_s']<=t<event['end_s'] else 1.
            nominal,ncc,obs=interface.oracle(t,y,pre,d,request,vs,policy)
            old_cc=row['original_control'] if kind=='sample_update' else row['nominal_control']
            close(old_cc,ncc,atol=1e-8,rtol=1e-11)
            max_nominal=max(max_nominal,abs(nominal['queued']-as_complex(row['m_nom'])))
            close(as_complex(row['m_nom']),nominal['queued'],atol=1e-12,rtol=1e-11)
            if kind=='guard_failure':
                assert row['controller_after_exception']==row['controller_pre'] and row['plant_after_exception']==row['plant_pre'];failed+=1;continue
            post=unserial(row['controller_post_update']);safe=as_complex(row['m_safe']);guard=row['guard'];observed=guard['observation']
            delta=d['control_sample_s']*d['current_Kaw_per_s']*obs['vdc']*(safe-nominal['queued'])*cmath.exp(-1j*pre['theta'])
            expected=copy.deepcopy(nominal);expected['queued']=safe;expected['zi']+=delta
            for key in post:
                err=abs(post[key]-expected[key]);max_fullstate[key]=max(max_fullstate.get(key,0.),float(err));close(post[key],expected[key],atol=2e-8,rtol=1e-11)
            max_aw=max(max_aw,abs(post['zi']-nominal['zi']-delta));close(guard['antiwindup_delta_zi'],as_real(delta),atol=2e-9,rtol=1e-11)
            expected_cc=ncc.copy();expected_cc[7]=abs(safe);close(row['control'],expected_cc,atol=1e-8,rtol=1e-11)
            phi=observed['phase_origin_rad']+d['omega_base_rad_s']*(t-observed['phase_origin_time_s'])
            s=state(obs['i_ab']*cmath.exp(-1j*phi)/d['I_phase_peak_base_A'],obs['queued_ab']*cmath.exp(-1j*phi))
            max_observation=max(max_observation,float(np.max(np.abs(s-np.array(observed['state'])))))
            close(s,observed['state'],atol=2e-12,rtol=1e-11)
            plan= row['certified_backup_plan'];selection=guard['selection'];j=row['k']-6000-plan['origin_k']
            assert selection['plan_index']==j and selection['plan_origin_k']==plan['origin_k'] and plan['backup_ready'] and plan['primal_validation']['accepted']
            center=np.array(plan['z'][j]) if j<o.N else o.sbar
            nominal_input=as_complex(plan['v'][j]) if j<o.N else o.mbar
            command=(nominal_input+o.feedback(s-center))*cmath.exp(1j*phi)
            max_command=max(max_command,abs(command-safe));close(command,safe,atol=2e-12,rtol=1e-11)
            witness=o.omega_inverse(s-center);assert witness['inside']
            if selection['type']=='optimized':
                assert j==0
                primal=o.validate_plan(s,np.array(plan['z']),np.array(plan['v']))
                assert primal['accepted'],(case,row['k'],primal)
                max_plan=max(max_plan,primal['max_primal_residual']);plan_count+=1
            count+=1
    assert header and count==summary['accepted_control_count']
    reference,refstates=independent_reference(summary,ep,ns,d)
    recovery=independent_recovery(summary,ns,iv,refstates,d)
    contacts=summary['all_hard_contacts'];mod=summary['metrics']['modulation_max']
    physically_safe=not contacts and not summary['first_observed_beyond_roundoff'] and mod<=d['svpwm_linear_voltage_derating']/math.sqrt(3)*(1+1e-8)
    assert physically_safe==summary['no_physical_hard_contact_up_to_stop']
    assert summary['complete_hard_safe']==bool(summary['simulation_completed'] and physically_safe and failed==0)
    return {'status':'PASS_INDEPENDENT_CONSTRUCTIVE_ARTIFACT_CHECKS','allocator':policy,'all_accepted_samples_replayed_algebraically':count,'guard_failures_with_preserved_state':failed,'max_nominal_modulation_error':max_nominal,'max_common_AW_error':max_aw,'max_command_plan_index_frame_error':max_command,'max_observation_state_error':max_observation,'max_full_controller_field_errors':max_fullstate,'accepted_optimizer_plans_independently_revalidated':plan_count,'max_revalidated_plan_primal_residual':max_plan,'hard_contacts_recomputed':root_count,'max_continuous_root_margin_abs':max_root,'own_allocator_reference':reference,'conservative_recovery':recovery,'physical_admission_reconciled':True}


def audit_one(path):
    start=time.monotonic();oldhash=sha(LEGACY_PATH)
    base=legacy.artifact_check(path)
    extra=augmented_check(path)
    assert sha(LEGACY_PATH)==oldhash
    return {'case':base['case'],'h_s':base['h_s'],'status':'PASS_COMPLETED_ARTIFACT_RECONCILIATION','summary_sha256':sha(path),'legacy_energy_tube_root_timing_checks':base,'independent_allocator_reference_recovery_checks':extra,'audit_wall_s':time.monotonic()-start}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--case',choices=rm.CASE_IDS);args=parser.parse_args()
    assert sha(HERE/'run_constructive.py')==EXPECTED_RUNNER and sha(HERE/'guarded_allocator_controller.py')==EXPECTED_WRAPPER
    before={str(p.relative_to(ROOT)):sha(p) for p in [LEGACY_PATH,ROOT/'current_guard_gate1/common_guard.py',ROOT/'current_guard_gate1/run_models.py',ROOT/'baseline_allocation/allocators.py']}
    result_path=HERE/'audit_artifact_results.json'
    previous=json.loads(result_path.read_text()) if result_path.exists() else {}
    checks={r['case']+'_'+format(r['h_s'],'g'):r for r in previous.get('completed_artifacts',[])}
    todo=[args.case] if args.case else list(rm.CASE_IDS)
    with patch.object(rm,'run',forbidden),patch.object(rm,'rhs',forbidden),patch.object(rm,'solve_ivp',forbidden),patch.object(cg,'minimize',forbidden):
        for cid in todo:
            for h in [1e-5,5e-6]:
                path=HERE/'results'/f'{cid}_h{h:g}.json'
                if not path.exists():continue
                print('Checking completed '+path.name,flush=True)
                try:checks[cid+'_'+format(h,'g')]=audit_one(path)
                except Exception as exc:
                    checks[cid+'_'+format(h,'g')]={'case':cid,'h_s':h,'status':'FAIL_AUDIT','summary_sha256':sha(path),'error':repr(exc),'traceback':traceback.format_exc()}
                print(json.dumps({k:checks[cid+'_'+format(h,'g')][k] for k in ['case','h_s','status']}),flush=True)
    assert before=={str(p.relative_to(ROOT)):sha(p) for p in [LEGACY_PATH,ROOT/'current_guard_gate1/common_guard.py',ROOT/'current_guard_gate1/run_models.py',ROOT/'baseline_allocation/allocators.py']}
    rows=list(checks.values());failed=[r for r in rows if r['status']!='PASS_COMPLETED_ARTIFACT_RECONCILIATION']
    pending=[cid for cid in rm.CASE_IDS if cid+'_1e-05' not in checks]
    out={'status':'FAIL_AUDIT' if failed else ('PASS_AVAILABLE_COMPLETED_ARTIFACTS' if pending else 'PASS_ALL_FOUR_COMPLETED_ARTIFACTS'),'completed_artifacts':rows,'pending_primary_artifacts':pending,'physical_trajectories_executed_by_audit':0,'real_optimization_calls':0,'source_sha256':{'run_constructive.py':EXPECTED_RUNNER,'guarded_allocator_controller.py':EXPECTED_WRAPPER,'audit_artifact_checks.py':sha(__file__),'sealed_audit_runner_checks.py':sha(LEGACY_PATH)},'frozen_sources_before_and_after':before,'qualification':'Read-only stored evidence and algebraic replay. Retained-node tube checks do not prove unretained continuous extrema or machine intervals; frozen recovery criteria retained exactly.'}
    result_path.write_text(json.dumps(plain(out),indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':out['status'],'completed_count':len(rows),'pending':pending,'failures':[r.get('error') for r in failed]},indent=2))
if __name__=='__main__':main()
