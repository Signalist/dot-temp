"""No physical solve or CommonGuard construction: AST, imports, scoring, admission."""
from __future__ import annotations
import ast
import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OLD = ROOT / 'current_guard_gate1/run_models.py'
NEW = HERE / 'run_constructive.py'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
old_bytes = OLD.read_bytes()
old = ast.parse(old_bytes)
new = ast.parse(NEW.read_text())
nodekey = lambda n: ast.dump(n, include_attributes=False)
def defs(tree):
    return {n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
o, n = defs(old), defs(new)
unchanged = ['sha','jsonable','dump','tag_for','service','inventory','energy_necessary_condition',
             'flattened_scalars','TimingSummary','recovery_score']
for name in unchanged:
    assert nodekey(o[name]) == nodekey(n[name]), name
# Every nested RHS, measurement, hard-limit, clock-phase, root/event helper is exact.
of, nf = defs(o['run']), defs(n['run'])
nested_unchanged = sorted(set(of) & set(nf))
for name in nested_unchanged:
    assert nodekey(of[name]) == nodekey(nf[name]), name
# Full gzip trajectory block must be AST-identical after ONLY the declared nominal
# allocator sampler substitution. Includes exception/rollback, flags, solve_ivp,
# event splits, sample state and all raw guard/timing/plan logs.
old_block = next(x for x in o['run'].body if isinstance(x,ast.With) and any(isinstance(c,ast.Call) and isinstance(c.func,ast.Attribute) and isinstance(c.func.value,ast.Name) and c.func.value.id=='gzip' for c in ast.walk(x.items[0].context_expr)))
new_block = copy.deepcopy(next(x for x in n['run'].body if isinstance(x,ast.With) and any(isinstance(c,ast.Call) and isinstance(c.func,ast.Attribute) and isinstance(c.func.value,ast.Name) and c.func.value.id=='gzip' for c in ast.walk(x.items[0].context_expr))))
replacements = 0
for call in ast.walk(new_block):
    if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='allocator_controller':
        assert len(call.args)==7 and nodekey(call.args[-1])==nodekey(ast.parse("case['allocator']",mode='eval').body)
        call.func.id='controller'; call.args.pop(); replacements += 1
assert replacements == 1
assert nodekey(old_block) == nodekey(new_block), 'trajectory/logging block changed beyond nominal sampler'
# All physical column layouts and hard names are identical.
constants = ['STATE_NAMES','COLS','CI','CONTROL_COLS','INTERVAL_COLS','NORMALIZED_NAMES','HARD_NAMES']
for name in constants:
    pick=lambda tree:next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets))
    assert nodekey(pick(old))==nodekey(pick(new)),name
# No top-level calls to run/CommonGuard/solve_ivp; import alone must not launch.
assert not any(isinstance(x,ast.Expr) and isinstance(x.value,ast.Call) and isinstance(x.value.func,ast.Name) and x.value.func.id in ('run','CommonGuard','solve_ivp') for x in new.body)
spec=importlib.util.spec_from_file_location('constructive_static_subject',NEW)
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
assert 'common_guard' not in sys.modules, 'Runner imported guard eagerly'
assert not r.OUTPUT.exists(), 'Unexpected real result directory before authorized physical start'
assert r.sha(r.GUARD_SOURCE)==r.EXPECTED_GUARD_SHA256
loaded={}
for cid in r.CASE_IDS:
    f,g,c,d,full,cp=r.load_design(cid);loaded[cid]=(f,g,c,d,full,cp)
    assert c['port']=='fast' and c['end_time_s']==2.75005
    assert d['battery_source_tau_s']==.002
    assert d['battery_source_ramp_up_W_per_s']==d['battery_source_ramp_down_W_per_s']==50000000
    assert all(isinstance(v,(int,float)) and not isinstance(v,bool) for v in d.values())
    assert 'allocator' not in d and 'event' not in d
    if c['event']: assert c['event']=={'start_s':.60005,'end_s':.75005,'retained_source_pu':.4}
    else: assert r.reference_comparison(c,None,None,d)[0]['status']=='NOT_AVAILABLE'
for invalid in ['C0-fast','C0-slow','P0-slow','Q0-fast']:
    try: r.load_design(invalid)
    except ValueError: pass
    else: raise AssertionError(invalid)
# Pure quadrature arithmetic with analytic known values, no plant integration.
y0=r.np.zeros(13); y1=y0.copy();y1[7]=1600000;y1[8]=1400000;y1[11]=20000;y1[12]=30000
score=r.service(y0,y1,2)
assert score['mean_P_W']==800000 and score['mean_Q_var']==700000
assert score['P_signed_request_error_integral_J']==0 and score['Q_signed_request_error_integral_var_s']==0
assert score['mean_absolute_P_error_W']==10000 and score['mean_absolute_Q_error_var']==15000
assert r.service(y0,y0,0)['mean_P_W'] is None
assert r.recovery_score(loaded['P0-fast'][2],True,True,None,None,None,loaded['P0-fast'][3])['status']=='NOT_APPLICABLE_NO_FAULT'
for q in r.external_q_guard_controls():
    assert q['matched_own_allocator_reference'] is False and q['used_for_recovery_scoring'] is False
# Admission tests use temporary synthetic metadata/arrays; never create physical
# result claims or use fake evidence in the real results directory.
original_output=r.OUTPUT
with tempfile.TemporaryDirectory(prefix='constructive_static_',dir=str(HERE)) as td:
    r.OUTPUT=Path(td)
    def rejected(case, h=1e-5):
        try:r.check_run_admission(loaded[case][0],loaded[case][2],h)
        except (RuntimeError,ValueError):return True
        return False
    assert not rejected('P0-fast')
    assert rejected('R0-fast') and rejected('P50-fast') and rejected('R50-fast')
    assert rejected('P0-fast',5e-6) and rejected('P0-fast',2e-5)
    def fake_healthy(cid, admitted=True):
        _,_,c,_,_,cp=loaded[cid]
        trace=r.OUTPUT/(r.tag_for(cid,1e-5)+'.npz')
        initial=r.np.r_[.6,cp['plant_state'],r.np.zeros(6),r.np.zeros(len(r.COLS)-14)]
        end=initial.copy();end[0]=2.75005
        normalized=r.np.array([[.6,*cp['normalized_state']],[2.75005,*cp['normalized_state']]])
        r.np.savez_compressed(trace,endpoint_trace=r.np.array([initial,end]),normalized_state=normalized)
        q=dict(case=cid,allocator=c['allocator'],source_port='fast',event=None,
               protocol_sha256=r.EXPECTED_PROTOCOL_SHA256,guard_source_sha256=r.EXPECTED_GUARD_SHA256,
               allocator_source_sha256=r.EXPECTED_ALLOCATOR_SHA256,
               controller_source_sha256=r.sha(HERE/'guarded_allocator_controller.py'),runner_source_sha256=r.sha(NEW),
               checkpoint_sha256='ca8a1d63f9bb406ab83b0560986ae43b29bd831018f1cbfedb60af4afaa48152',
               same_full_state=True,source_tau_s=.002,source_ramp_W_per_s=50000000.,
               no_fault_physical_admission=admitted,trace_sha256=r.sha(trace),numerical_refinement_indicated=False)
        r.dump(r.OUTPUT/(r.tag_for(cid,1e-5)+'.json'),q)
        return q,initial,end,normalized
    pq,initial,end,normalized=fake_healthy('P0-fast')
    assert not rejected('R0-fast')
    fake_healthy('R0-fast',False)
    assert not rejected('P50-fast') and rejected('R50-fast')
    # Synthetic own-allocator comparison preserves zero matched integrals.
    c=loaded['P50-fast'][2];d=loaded['P50-fast'][3]
    comparison,rn=r.reference_comparison(c,r.np.array([initial,end]),normalized,d)
    assert comparison['reference_case']=='P0-fast'
    assert comparison['same_initial_normalized_full_state_exact']
    assert comparison['P_integral_difference_J']==comparison['Q_integral_difference_var_s']==0
    assert comparison['max_normalized_state_difference']==0
    # Q-priority and mismatched source provenance are rejected even if flagged safe.
    pq['allocator']='q_priority';r.dump(r.OUTPUT/(r.tag_for('P0-fast',1e-5)+'.json'),pq)
    assert rejected('P50-fast')
    fake_healthy('P0-fast',False)
    assert rejected('P50-fast')
    fake_healthy('R0-fast',True)
    assert not rejected('R50-fast'), 'Failed P does not prevent admitted radial fault'
    assert rejected('P0-fast'), 'Existing evidence must never be overwritten'
r.OUTPUT=original_output
assert not r.OUTPUT.exists()
assert OLD.read_bytes()==old_bytes
changed=sorted(name for name in set(o)&set(n) if nodekey(o[name])!=nodekey(n[name]))
report=dict(status='PASS_STATIC_ONLY_NO_PHYSICAL_RUN',physical_trajectories_executed=0,
            guard_instances_constructed=0,guard_solve_calls=0,
            unchanged_top_level_definitions=unchanged,unchanged_nested_run_helpers=nested_unchanged,
            unchanged_physical_schemas=constants,
            full_trajectory_and_logging_block='AST_IDENTICAL_AFTER_ONE_SAME_ALLOCATOR_NOMINAL_SAMPLER_SUBSTITUTION',
            modified_top_level_definitions=changed,new_top_level_definitions=sorted(set(n)-set(o)),
            source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [OLD,NEW,r.GUARD_SOURCE,r.ALLOCATOR_SOURCE,r.PROTOCOL,HERE/'guarded_allocator_controller.py']},
            dynamic_checks=['read-only module import; no eager CommonGuard import','four-case frozen protocol/hash/port/event/full-checkpoint load',
                'reject undeclared and slow cases','healthy matched reference NOT_AVAILABLE',
                'absolute service arithmetic and no-fault recovery status','own-allocator fault admission and strict reference provenance',
                'both healthy before faults; failed allocator does not block other admitted allocator',
                'synthetic paired-reference scoring, full normalized initial-state match','existing evidence and unindicated5us rejection',
                'historical Q+guard explicitly unmatched external context'],
            scope='AST/import/pure arithmetic and temporary synthetic admission fixtures only; no physical propagation or optimizer calls')
(HERE/'RUNNER_STATIC_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
(HERE/'RUNNER_DIFF_FROM_GATE1.patch').write_text(''.join(difflib.unified_diff(old_bytes.decode().splitlines(True),NEW.read_text().splitlines(True),fromfile='current_guard_gate1/run_models.py',tofile='current_guard_constructive/run_constructive.py')))
print(json.dumps(report,indent=2))
