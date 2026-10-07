"""Independent constructive runner audit: AST equality and static helper calls only.

No run(), plant RHS, integrator, or optimization is called. Temporary reference
arrays are synthetic arithmetic fixtures, not trajectories; they are removed.
"""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import math
import sys
sys.dont_write_bytecode = True
import tempfile
from unittest.mock import patch
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
import run_constructive as rm
EXPECTED_RUNNER='e9bceab631ec7f26c9639aa3a2887ddf21f8cefdd63390c76fbeb1d3d30563c5'
EXPECTED_OLD='9e4ca7f83570e6e62bf7f3fef9096cde5c44782a0ca7b27026dcd47978662eae'
RESULTS=[]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(name,details):RESULTS.append({'name':name,'status':'PASS','details':details})
def dump(n):return ast.dump(n,include_attributes=False)
def forbidden(*a,**k):raise AssertionError('Physical run/RHS/integration/optimization is forbidden in this audit')
def blocked(call,label):
    try:call()
    except (RuntimeError,ValueError):return label
    raise AssertionError('Expected rejection: '+label)

OLD_SOURCE=(ROOT/'current_guard_gate1/run_models.py').read_text()
NEW_SOURCE=(HERE/'run_constructive.py').read_text()
OLD=ast.parse(OLD_SOURCE);NEW=ast.parse(NEW_SOURCE)
def byname(tree,name):return next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)

class NormalizeApprovedRunChanges(ast.NodeTransformer):
    def visit_ImportFrom(self,n):
        if n.module=='guarded_allocator_controller':n.module='guarded_controller'
        return n
    def visit_If(self,n):
        if ast.unparse(n.test)=="Path(sys.modules[CommonGuard.__module__].__file__).resolve() != GUARD_SOURCE":
            assert len(n.body)==1 and ast.unparse(n.body[0])=="raise RuntimeError('CommonGuard resolved to an unexpected source path')"
            return None
        return self.generic_visit(n)
    def visit_Assign(self,n):
        if len(n.targets)==1 and ast.unparse(n.targets[0])=='guard.nominal_allocator':
            assert ast.unparse(n.value)=="case['allocator']";return None
        if len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='q':
            assert isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=='dict'
            removed={'allocator','controller_source_path','guard_source_path','allocator_source_path','allocator_source_sha256','external_known_Q_guard_controls'}
            n.value.keywords=[kw for kw in n.value.keywords if kw.arg not in removed]
            for kw in n.value.keywords:
                if kw.arg in {'evidence','controller_source_sha256','guard_source_sha256'}:kw.value=ast.Constant(value='APPROVED_METADATA_VARIATION')
        return self.generic_visit(n)
    def visit_Call(self,n):
        if isinstance(n.func,ast.Name) and n.func.id=='allocator_controller':
            assert ast.unparse(n.args[-1])=="case['allocator']" and len(n.args)==7
            n.func.id='controller';n.args=n.args[:-1]
        return self.generic_visit(n)


def test_ast_equivalence():
    assert sha(HERE/'run_constructive.py')==EXPECTED_RUNNER
    assert sha(ROOT/'current_guard_gate1/run_models.py')==EXPECTED_OLD
    names=['sha','jsonable','dump','tag_for','service','inventory','energy_necessary_condition','flattened_scalars','TimingSummary','recovery_score']
    for name in names:assert dump(byname(OLD,name))==dump(byname(NEW,name)),name
    oldrun=NormalizeApprovedRunChanges().visit(copy.deepcopy(byname(OLD,'run')))
    newrun=NormalizeApprovedRunChanges().visit(copy.deepcopy(byname(NEW,'run')))
    assert dump(oldrun)==dump(newrun),'Run body changed outside enumerated import/policy/metadata adaptations'
    constant_names=['STATE_NAMES','COLS','CI','CONTROL_COLS','INTERVAL_COLS','NORMALIZED_NAMES','HARD_NAMES']
    for name in constant_names:
        def find(tree):return next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
        assert dump(find(OLD))==dump(find(NEW)),name
    run=byname(NEW,'run');nested={n.name:n for n in ast.walk(run) if isinstance(n,ast.FunctionDef)}
    row=nested['row_margins'];ns={'np':np}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[row],type_ignores=[])),'<row_margins>','exec'),ns)
    a=np.zeros(26);a[14]=1.01;a[15]=1.05;a[23]=.6;a[16]=970000.;a[17]=900000.;a[4]=-900000.
    target=[-.01,.09,.25,.05,.4,.2,1-970000/950000,1+970000/950000,1-math.hypot(970000,900000)/1.2e6,1.9,.1]
    np.testing.assert_allclose(ns['row_margins'](a),target,rtol=0,atol=1e-14)
    calls=[n for n in ast.walk(run) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='allocator_controller']
    assert len(calls)==1 and ast.unparse(calls[0].args[-1])=="case['allocator']"
    assignments=[n for n in ast.walk(run) if isinstance(n,ast.Assign) and any(ast.unparse(t)=='guard.nominal_allocator' for t in n.targets)]
    assert len(assignments)==1 and ast.unparse(assignments[0].value)=="case['allocator']"
    emit('AST equality to sealed runner, allowing only enumerated adaptations',{'unchanged_top_level_helpers':names,'unchanged_column_and_hard_limit_schemas':constant_names,'entire_run_body_equal_after_exact_whitelist':True,'allowed_run_differences':['wrapper import name','guard source path verification','guard.nominal_allocator from case','nominal allocator call using the same case allocator','summary provenance and unmatched external-Q context'],'unchanged_execution':['13-dimensional RHS and quadratures','full-state checkpoint reconstruction','100us sample clock','event and off-grid end splits','DOP853 tolerances and hard root functions','hard margins and stopping rules','accepted/failed guard state checks','request errors and inventory','common-window reference arithmetic','conservative 50ms/150ms recovery criteria','original source/PLL gains and antiwindup','no clipping or reset added']})


def test_design_and_initialization():
    results=[]
    base=json.loads((ROOT/'protocol/GATE1_MPSC_SIX_MODELS_V1.json').read_text())
    proposal=json.loads(rm.PROTOCOL.read_text())
    spec=json.loads((ROOT/base['base_Gate0_design']).read_text())
    original=json.loads((ROOT/spec['base_protocol']).read_text())
    numeric={k:v for k,v in original.items() if isinstance(v,(int,float)) and not isinstance(v,bool)}
    numeric.update(battery_source_tau_s=.002,battery_source_ramp_up_W_per_s=5e7,battery_source_ramp_down_W_per_s=5e7)
    run=byname(NEW,'run');b=run.body
    start=next(i for i,n in enumerate(b) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='y' for t in n.targets))
    end=next(i for i,n in enumerate(b[start:],start) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='guard' for t in n.targets))
    init_code=compile(ast.fix_missing_locations(ast.Module(body=copy.deepcopy(b[start:end]),type_ignores=[])),'<frozen initialization>','exec')
    for cid in rm.CASE_IDS:
        f,g,case,d,full,cp=rm.load_design(cid)
        assert d==numeric and full==original and g==spec
        assert cp==json.loads((ROOT/proposal['checkpoint']).read_text())
        assert f['fixed_guard_design']==base['fixed_guard_design']
        assert case['port']=='fast' and case['end_time_s']==2.75005
        assert case['allocator']==('p_priority' if cid.startswith('P') else 'radial')
        assert case['event']==(None if '0-fast' in cid and '50-fast' not in cid else {'start_s':.60005,'end_s':.75005,'retained_source_pu':.4})
        ns={'cp':cp,'d':d,'np':np,'copy':copy,'normstate':rm.normstate}
        exec(init_code,ns)
        assert len(ns['y'])==13 and np.array_equal(ns['y'][:7],cp['plant_state']) and np.array_equal(ns['y'][7:],np.zeros(6))
        assert rm.serial_ctl(ns['ctl'])==cp['controller']
        np.testing.assert_allclose(ns['initial_norm'],cp['normalized_state'],rtol=0,atol=1e-12)
        ts=np.array([k*1e-4 for k in range(6000,int(np.ceil(case['end_time_s']/1e-4)))])
        assert np.all(np.abs(np.diff(ts)-1e-4)<1e-14)
        assert np.array_equal(np.round((ts-.6)/1e-4).astype(int),np.arange(len(ts)))
        results.append({'case':cid,'allocator':case['allocator'],'checkpoint_max_normalized_error':float(np.max(np.abs(ns['initial_norm']-np.array(cp['normalized_state'])))),'sample_count_if_completed':len(ts),'first_sample_s':ts[0],'last_sample_s':ts[-1],'exact_end_s':case['end_time_s'],'event':case['event']})
    rejects=[]
    for cid in ['all','C0-fast','C0-slow','P0-slow','R1-fast']:
        rejects.append(blocked(lambda cid=cid:rm.load_design(cid),'undeclared case '+cid))
    paths=[rm.PROTOCOL,ROOT/proposal['fixed_guard_protocol'],rm.GUARD_SOURCE,rm.ALLOCATOR_SOURCE,ROOT/base['base_Gate0_design'],ROOT/spec['base_protocol'],ROOT/proposal['checkpoint']]
    original_sha=rm.sha
    for path in paths:
        with patch.object(rm,'sha',side_effect=lambda p,path=path: '0'*64 if Path(p)==path else original_sha(p)):
            rejects.append(blocked(lambda:rm.load_design('P0-fast'),'changed frozen bytes '+str(path.relative_to(ROOT))))
    emit('Frozen four-case design, all scalar resources, full checkpoint, clock and hash rejection',{'cases':results,'fixed_guard_design':base['fixed_guard_design'],'source_port':proposal['port'],'negative_checks':rejects,'nominal_request':proposal['nominal_request']})


def synthetic_trace(d,cp):
    ep=np.zeros((3,len(rm.COLS)));ep[:,0]=[.6,.6001,.6002]
    ep[:,1:8]=np.array(cp['plant_state']);ep[:,14]=.7;ep[:,15]=1.;ep[:,23]=.5
    ep[:,8]=[0.,80.,160.];ep[:,9]=[0.,70.,140.]
    ep[:,12]=[0.,10.,20.];ep[:,13]=[0.,7.,14.]
    states=np.zeros((3,len(rm.NORMALIZED_NAMES)));states[:,0]=ep[:,0]
    return ep,states


def write_reference(output,case,admitted=True):
    _,_,_,d,_,cp=rm.load_design(case['id']);healthy=rm.healthy_case_id(case)
    trace=output/(rm.tag_for(healthy,1e-5)+'.npz');ep,states=synthetic_trace(d,cp)
    np.savez(trace,endpoint_trace=ep,normalized_state=states)
    summary={'case':healthy,'allocator':case['allocator'],'source_port':'fast','event':None,'protocol_sha256':rm.EXPECTED_PROTOCOL_SHA256,'guard_source_sha256':rm.EXPECTED_GUARD_SHA256,'allocator_source_sha256':rm.EXPECTED_ALLOCATOR_SHA256,'controller_source_sha256':sha(HERE/'guarded_allocator_controller.py'),'runner_source_sha256':sha(HERE/'run_constructive.py'),'checkpoint_sha256':'ca8a1d63f9bb406ab83b0560986ae43b29bd831018f1cbfedb60af4afaa48152','same_full_state':True,'source_tau_s':.002,'source_ramp_W_per_s':5e7,'no_fault_physical_admission':admitted,'trace_sha256':sha(trace),'numerical_refinement_indicated':False,'stop_reason':'synthetic audit fixture only'}
    path=output/(rm.tag_for(healthy,1e-5)+'.json');path.write_text(json.dumps(summary));return path,trace,summary


def test_admission_and_pairing():
    f,_,_,d,_,cp=rm.load_design('P0-fast');cases={c['id']:c for c in f['execution_order']};rejects=[]
    with tempfile.TemporaryDirectory(prefix='synthetic_interface_',dir=HERE) as tmp:
        output=Path(tmp)
        with patch.object(rm,'OUTPUT',output):
            rm.check_run_admission(f,cases['P0-fast'],1e-5)
            for cid in ['R0-fast','P50-fast','R50-fast']:
                rejects.append(blocked(lambda cid=cid:rm.check_run_admission(f,cases[cid],1e-5),'missing staged health '+cid))
            ppath,ptrace,pref=write_reference(output,cases['P0-fast'],False)
            rm.check_run_admission(f,cases['R0-fast'],1e-5)
            rpath,rtrace,rref=write_reference(output,cases['R0-fast'],True)
            rejects.append(blocked(lambda:rm.check_run_admission(f,cases['P50-fast'],1e-5),'P fault blocked by own failed P healthy'))
            rm.check_run_admission(f,cases['R50-fast'],1e-5)
            ppath,ptrace,pref=write_reference(output,cases['P0-fast'],True)
            rm.check_run_admission(f,cases['P50-fast'],1e-5)
            rejects.append(blocked(lambda:rm.check_run_admission(f,cases['R50-fast'],1e-5),'both healthy pass: P fault required before R fault'))
            (output/(rm.tag_for('P50-fast',1e-5)+'.json')).write_text('{}')
            rm.check_run_admission(f,cases['R50-fast'],1e-5)
            for field,bad in [('case','R0-fast'),('allocator','radial'),('source_port','slow'),('event',{'start_s':.6}),('protocol_sha256','bad'),('guard_source_sha256','bad'),('allocator_source_sha256','bad'),('controller_source_sha256','bad'),('runner_source_sha256','bad'),('checkpoint_sha256','bad'),('same_full_state',False),('source_tau_s',.02),('source_ramp_W_per_s',5e6),('no_fault_physical_admission',False),('trace_sha256','bad')]:
                wrong=copy.deepcopy(pref);wrong[field]=bad;ppath.write_text(json.dumps(wrong))
                rejects.append(blocked(lambda:rm.read_healthy_reference(cases['P50-fast']),'wrong own-reference '+field))
            ppath.write_text(json.dumps(pref));saved=ptrace.read_bytes();ptrace.unlink()
            rejects.append(blocked(lambda:rm.read_healthy_reference(cases['P50-fast']),'missing own trace'))
            ptrace.write_bytes(saved)
            rejects.append(blocked(lambda:rm.check_run_admission(f,cases['P0-fast'],1e-5),'existing primary cannot overwrite'))
            rejects.append(blocked(lambda:rm.check_run_admission(f,cases['R0-fast'],5e-6),'unindicated refinement'))
            refined=copy.deepcopy(rref);refined['numerical_refinement_indicated']=True;rpath.write_text(json.dumps(refined))
            rm.check_run_admission(f,cases['R0-fast'],5e-6)
            (output/(rm.tag_for('R0-fast',5e-6)+'.started.json')).write_text('{}')
            rejects.append(blocked(lambda:rm.check_run_admission(f,cases['R0-fast'],5e-6),'refinement started evidence cannot overwrite'))
            for h in [2e-5,1e-6,0.]:rejects.append(blocked(lambda h=h:rm.check_run_admission(f,cases['P0-fast'],h),'undeclared step '+str(h)))
            # Healthy reports cannot open Q or any alternate reference trace.
            with patch.object(rm.np,'load',forbidden):
                for cid in ['P0-fast','R0-fast']:
                    out,rn=rm.reference_comparison(cases[cid],None,None,d)
                    assert out['status']=='NOT_AVAILABLE' and out['reference'] is None and rn is None
            # Both own-allocator mappings and the exact common-window arithmetic.
            pairing=[]
            for cid in ['P50-fast','R50-fast']:
                ep,states=synthetic_trace(d,cp);ep[-1,8]+=3.;ep[-1,9]-=4.;ep[-1,12]+=2.;ep[-1,13]-=1.
                out,rn=rm.reference_comparison(cases[cid],ep,states,d)
                assert out['reference_case']==rm.healthy_case_id(cases[cid]) and out['allocator']==cases[cid]['allocator']
                assert out['reference']=='same_allocator_same_port_guarded_no_fault'
                assert out['same_initial_7_state_exact'] and out['full_observed_case_covered'] and out['same_initial_normalized_full_state_exact']
                assert out['P_integral_difference_J']==3. and out['Q_integral_difference_var_s']==-4.
                assert out['P_absolute_error_integral_difference_J']==2. and out['Q_absolute_error_integral_difference_var_s']==-1.
                assert out['max_normalized_state_difference']==0.
                pairing.append(out)
                for field in [1,5,8,12,14]:
                    wrong_states=states.copy();wrong_states[0,field]+=1e-9
                    rejects.append(blocked(lambda wrong_states=wrong_states:rm.reference_comparison(cases[cid],ep,wrong_states,d),'normalized initial mismatch '+cid+' field '+str(field)))
            q=rm.external_q_guard_controls()
            assert len(q)==2 and all(x['matched_own_allocator_reference'] is False and x['used_for_recovery_scoring'] is False for x in q)
    emit('Own-allocator admission, sequence, negative provenance checks and paired reference scoring',{'negative_checks':rejects,'positive_scenarios':['P0 initial allowed','R0 allowed even if P0 fails','R50 allowed after both healthy records when R passes and P fails','P50 allowed after own P0 pass','R50 allowed after prior admitted P50 recorded','same-case indicated 5us refinement allowed'],'healthy_reference':'NOT_AVAILABLE; no alternate or Q-priority reference read','synthetic_fault_pair_checks':pairing,'external_Q_role':'explicit unmatched context, excluded from recovery','temporary_fixtures_removed':not Path(tmp).exists()})


def test_pure_scoring_and_timing():
    _,_,case,d,_,cp=rm.load_design('P0-fast')
    initial=np.r_[cp['plant_state'],np.zeros(6)];final=initial.copy();final[7:13]=[12.,-3.,0.,0.,4.,5.]
    score=rm.service(initial,final,.2)
    assert score['P_signed_request_error_integral_J']==12-800000*.2
    assert score['Q_signed_request_error_integral_var_s']==-3-700000*.2
    assert score['P_absolute_request_error_integral_J']==4 and score['Q_absolute_request_error_integral_var_s']==5
    zero=rm.service(initial,initial,0.)
    assert zero['mean_P_W'] is None and zero['mean_absolute_P_error_W'] is None
    timing=rm.TimingSummary();timing.add({'time_s':888.,'sample_k':99000,'observation':{'causal_phase_rad':555.},'solver':{'success_flag':False,'accepted_suboptimal':True,'timing':{'solve_s':.001}},'selection':{'type':'shifted_plan'}},.002)
    out=timing.result();assert max(x['maximum_s'] for x in out['seconds'].values())==.002
    assert out['counts']=={'calls':1,'guard_failures':0,'solver_success_false':1,'backup_calls':1,'accepted_nonoptimal_calls':1}
    healthy=rm.recovery_score(case,True,True,None,None,None,d);assert healthy['status']=='NOT_APPLICABLE_NO_FAULT'
    _,_,fault,_,_,_=rm.load_design('P50-fast')
    stopped=rm.recovery_score(fault,False,True,np.array([[.65,0.]]),None,None,d)
    assert stopped['status']=='NOT_SCORED_INCOMPLETE_TRAJECTORY' and stopped['joint_recovery_time_s'] is None and not stopped['clearance_observed']
    no_ref=rm.recovery_score(fault,True,True,None,None,None,d);assert no_ref['status']=='NOT_SCORED_REFERENCE_UNAVAILABLE'
    emit('Static absolute service, zero duration, real-wall timing and unobserved recovery checks',{'service':score,'timing':out,'incomplete_recovery':stopped,'unavailable_recovery':no_ref})


def main():
    frozen=[ROOT/'current_guard_gate1/run_models.py',ROOT/'current_guard_gate1/common_guard.py',ROOT/'baseline_allocation/allocators.py',ROOT/'gate_a/dq_bench.py',rm.PROTOCOL]
    before={str(p.relative_to(ROOT)):sha(p) for p in frozen}
    # Calling rm.run is explicitly disallowed; load_design and pure helpers only.
    with patch.object(rm,'run',forbidden),patch.object(rm,'rhs',forbidden),patch.object(rm,'solve_ivp',forbidden):
        for test in [test_ast_equivalence,test_design_and_initialization,test_admission_and_pairing,test_pure_scoring_and_timing]:test()
    after={str(p.relative_to(ROOT)):sha(p) for p in frozen};assert before==after
    out={'status':'PASS_STATIC_RUNNER_ONLY','test_groups':len(RESULTS),'results':RESULTS,'physical_trajectories_executed_by_audit':0,'real_optimization_calls':0,'runner_sha256':sha(HERE/'run_constructive.py'),'audit_source_sha256':sha(__file__),'sealed_driver_sha256':EXPECTED_OLD,'frozen_sources_before_and_after':after,'frozen_sources_unchanged':True,'qualification':'Static source and synthetic arithmetic/helper validation only. Physical admission and actual trajectory/artifact reconciliation remain pending.'}
    (HERE/'audit_interface_runner_results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:out[k] for k in ['status','test_groups','physical_trajectories_executed_by_audit','runner_sha256','audit_source_sha256']},indent=2))
if __name__=='__main__':main()
