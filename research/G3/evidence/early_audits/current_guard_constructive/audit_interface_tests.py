"""Independent constructive-controller audit. Static fixtures only; no plant run.

The independent controller oracle below uses only protocol scalars and explicit
circuit/controller equations, not allocators.controller or dq_bench.signals.
The existing allocator is also compared bit-for-bit as a separate passthrough
check. Frozen common-guard regression tests use isolated algebraic fixtures and
mocked optimizers only. No ODE, plant RHS, or physical trajectory is evaluated.
"""
from pathlib import Path
import ast
import cmath
import copy
import hashlib
import importlib.util
import json
import math
import sys
sys.dont_write_bytecode = True
from unittest.mock import patch
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
for name in ['gate_a','baseline_allocation','current_guard_gate1']:
    sys.path.insert(0,str(ROOT/name))
sys.path.insert(0,str(HERE))
import dq_bench as dq
import allocators
import common_guard as cg
from guarded_allocator_controller import guarded_controller
from audit_algebra_oracle import AlgebraOracle

O=AlgebraOracle()
D={k:v for k,v in O.d.items() if isinstance(v,(int,float)) and not isinstance(v,bool)}
CP=O.cp
EXPECTED={
 'protocol/next_constructive/FOUR_BASELINE_PROPOSAL_V1.json':'104b5f9102c286a2005e856da777b2a203a475c368fccd56d447e54ea43275f3',
 'current_guard_gate1/common_guard.py':'89e47d8429f893d09c2fd7cac5a38de360e76d7dc225ad5e0eb940b1a96fbe03',
 'baseline_allocation/allocators.py':'485e9ac80c8de58ee676d286972b92e7c398d1e2155a7f45dc025e2faffcb95a',
 'gate_a/preconditioned_dq/h1e-05_checkpoint.json':'ca8a1d63f9bb406ab83b0560986ae43b29bd831018f1cbfedb60af4afaa48152',
 'protocol/GATE1_MPSC_SIX_MODELS_V1.json':'be681761f993c6beaefaca0a54ece73dc2e3263d56b5b7f869ab476e87c96fa3'}
RESULTS=[]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clamp(x,lo,hi):return min(hi,max(lo,x))
def ctl():return {k:complex(*v) if isinstance(v,list) else v for k,v in CP['controller'].items()}
def pair(z):return [float(z.real),float(z.imag)]
def emit(name,details):RESULTS.append({'name':name,'status':'PASS','details':details})

def oracle(t,y,old,d,request,vs,policy):
    """Independent explicit SI equations. Does not call production helpers."""
    out=copy.deepcopy(old)
    current=complex(y[0],y[1]);vdc=math.sqrt(2*y[2]/d['C_dc_F'])
    voltage=old['applied']*vdc*cmath.exp(-1j*d['omega_base_rad_s']*t)
    lf,lg,rf,rg=[d[k] for k in ['filter_L_H','grid_L_H','filter_R_ohm','grid_R_ohm']]
    vp=(lg*(voltage-rf*current)+lf*(d['V_phase_peak_base_V']*vs+rg*current))/(lf+lg)
    frame=cmath.exp(1j*(d['omega_base_rad_s']*t-old['theta']))
    ic=current*frame;vc=vp*frame;vnorm=abs(vc)
    floor=d['pll_normalization_floor_pu']*d['V_phase_peak_base_V']
    pll_error=vc.imag/max(vnorm,floor)
    wu=d['omega_base_rad_s']+d['pll_Kp_per_s']*pll_error+old['zpll']
    wn=clamp(wu,2*math.pi*d['pll_frequency_min_Hz'],2*math.pi*d['pll_frequency_max_Hz'])
    ts=d['control_sample_s']
    if vnorm>=floor:
        zpll=old['zpll']+ts*(d['pll_Ki_per_s2']*pll_error+d['pll_Kaw_per_s']*(wn-wu))
    else:zpll=old['zpll'];wn=old['omega']
    pref=clamp(request['P_req_W'],-d['converter_active_service_limit_W'],d['converter_active_service_limit_W'])
    requested=complex(pref,request['Q_req_var'])/(1.5*max(vnorm,floor))
    limit=d['current_reference_limit_pu']*d['I_phase_peak_base_A']
    if policy=='p_priority':
        active=clamp(requested.real,-limit,limit)
        remainder=math.sqrt(max(0,limit*limit-active*active))
        reactive=clamp(requested.imag,-remainder,remainder)
    elif policy=='radial':
        scale=1 if abs(requested)<=limit else limit/abs(requested)
        active=requested.real*scale;reactive=requested.imag*scale
    else:raise ValueError(policy)
    ir=complex(active,-reactive)*vc/max(vnorm,1e-30)
    error=ir-ic
    unconstrained=vc+1j*wn*lf*ic+d['current_Kp_ohm']*error+old['zi']
    ulim=d['svpwm_linear_voltage_derating']*vdc/math.sqrt(3)
    sat=1 if abs(unconstrained)<=ulim else ulim/abs(unconstrained)
    constrained=unconstrained*sat
    zi=old['zi']+ts*(d['current_Ki_ohm_per_s']*error+d['current_Kaw_per_s']*(constrained-unconstrained))
    modulation=constrained*cmath.exp(1j*old['theta'])/vdc
    inverter_power=1.5*(voltage*current.conjugate()).real
    loss=d['inverter_loss_constant_W']+d['inverter_loss_current_squared_W_at_1pu']*(abs(current)/d['I_phase_peak_base_A'])**2
    need=inverter_power+loss
    feedforward=need/d['eta_dc_dc'] if need>=0 else need*d['eta_dc_dc']
    pb=clamp(feedforward+d['dc_energy_feedback_gain_per_s']*(.5*d['C_dc_F']*d['V_dc_initial_V']**2-y[2]),d['battery_terminal_power_min_W'],d['battery_terminal_power_max_W'])
    out.update(zpll=zpll,omega=wn,zi=zi,applied=old['queued'],queued=modulation,pb_command=pb)
    cc=[t,abs(ir)/d['I_phase_peak_base_A'],abs(constrained)/max(abs(unconstrained),1e-30),wn/(2*math.pi),pb,active,reactive,abs(modulation)]
    obs={'i_ab':current*cmath.exp(1j*d['omega_base_rad_s']*t),'vp_ab':vp*cmath.exp(1j*d['omega_base_rad_s']*t),'vdc':vdc,'applied_ab':old['applied'],'queued_ab':old['queued']}
    return out,cc,obs

class IdentityGuard:
    def __init__(self,policy,offset=0j,selection='optimized'):
        self.nominal_allocator=policy;self.offset=offset;self.selection=selection;self.calls=[]
    def command(self,t,k,observation,nominal):
        self.calls.append((t,k,copy.deepcopy(observation),nominal))
        return nominal+self.offset,{'selection':{'type':self.selection}}
class RejectGuard:
    def __init__(self,policy):self.nominal_allocator=policy
    def command(self,*args):raise cg.GuardFailure('audit injected failure',{'admitted':False})


def fixture(q,level,mode):
    # Solve the algebraic PCC measurement relation for the OLD applied hold.
    # These arbitrary isolated fixtures are intentionally not admitted plant runs.
    y=np.array(CP['plant_state'],float);c=ctl();t=.6+(q*9+mode)*D['control_sample_s']
    current=(.22+.07*q)*D['I_phase_peak_base_A']*cmath.exp(1j*(.31+q*math.pi/2))
    y[:2]=[current.real,current.imag];vdc=[1120.,1400.,1540.][mode];y[2]=.5*D['C_dc_F']*vdc**2
    vs=.4 if level<.5 else 1.;target=level*D['V_phase_peak_base_V']*cmath.exp(1j*(.13+.28*q))
    lf,lg,rf,rg=[D[k] for k in ['filter_L_H','grid_L_H','filter_R_ohm','grid_R_ohm']]
    u=((lf+lg)*target-lf*(D['V_phase_peak_base_V']*vs+rg*current))/lg+rf*current
    c['applied']=u/vdc*cmath.exp(1j*D['omega_base_rad_s']*t)
    c['queued']=(.31-.13j)*cmath.exp(.37j*q)
    c['theta']+=.16*q;c['zi']+=[0j,3000-2400j,-2900+3300j][mode]
    c['zpll']+=[0.,150.,-170.][mode];c['omega']+=1.1*q
    signs=[(1,1),(-1,1),(-1,-1),(1,-1)][q]
    request={'P_req_W':signs[0]*(800000. if mode!=2 else 1200000.),'Q_req_var':signs[1]*700000.}
    return t,y,c,request,vs


def test_frozen_sources():
    observed={name:sha(ROOT/name) for name in EXPECTED}
    assert observed==EXPECTED,observed
    assert Path(cg.__file__).resolve()==(ROOT/'current_guard_gate1/common_guard.py').resolve()
    assert Path(allocators.__file__).resolve()==(ROOT/'baseline_allocation/allocators.py').resolve()
    assert not (HERE/'common_guard.py').exists(),'Unexpected new guard copy shadows frozen source'
    emit('Frozen protocol, guard, nominal allocator and full-state checkpoint hashes',observed)


def test_controller():
    fixtures=[];max_oracle_state=0.;max_oracle_cc=0.;saturated=0;low_voltage=0
    for policy in ['p_priority','radial']:
        for quadrant in range(4):
            for voltage_pu in [1.,.4,.05]:
                for mode in range(3):
                    t,y,c,request,vs=fixture(quadrant,voltage_pu,mode)
                    before=copy.deepcopy(c);yb=y.copy();nominal=copy.deepcopy(c)
                    expected_cc=allocators.controller(t,y.copy(),nominal,D,request,vs,policy)
                    independent,icc,iobs=oracle(t,y,before,D,request,vs,policy)
                    guard=IdentityGuard(policy)
                    actual_cc,log=guarded_controller(t,y,c,D,request,vs,guard)
                    assert c.keys()==before.keys()==nominal.keys()==independent.keys()
                    exact_diffs={k:float(abs(c[k]-nominal[k])) for k in c}
                    assert max(exact_diffs.values())==0,exact_diffs
                    np.testing.assert_array_equal(actual_cc,expected_cc)
                    np.testing.assert_array_equal(y,yb)
                    state_diffs={k:float(abs(c[k]-independent[k])) for k in c}
                    for k in c:np.testing.assert_allclose(c[k],independent[k],rtol=5e-13,atol=3e-9,err_msg=k)
                    np.testing.assert_allclose(actual_cc,icc,rtol=5e-13,atol=3e-9)
                    max_oracle_state=max(max_oracle_state,max(state_diffs.values()))
                    max_oracle_cc=max(max_oracle_cc,float(np.max(np.abs(np.array(actual_cc)-icc))))
                    gt,gk,observed,mnom=guard.calls[0]
                    assert (gt,gk)==(t,round((t-.6)/D['control_sample_s']))
                    assert set(observed)==cg.CommonGuard.observation_keys=={'i_ab','vp_ab','vdc','applied_ab','queued_ab'}
                    for key in observed:np.testing.assert_allclose(observed[key],iobs[key],rtol=5e-13,atol=2e-10)
                    assert observed['applied_ab']==before['applied'] and observed['queued_ab']==before['queued']
                    assert c['applied']==before['queued'] and mnom==nominal['queued']
                    assert max(abs(complex(*log[k])) for k in ['antiwindup_delta_zi'])==0
                    saturated+=int(actual_cc[2]<1.-1e-12);low_voltage+=int(voltage_pu<.1)
                    fixtures.append({'allocator':policy,'quadrant':quadrant+1,'P_W':request['P_req_W'],'Q_var':request['Q_req_var'],'PCC_voltage_pu':voltage_pu,'Vdc_V':[1120.,1400.,1540.][mode], 'exact_passthrough_field_differences':exact_diffs,'oracle_field_differences':state_diffs,'oracle_control_max_error':float(np.max(np.abs(np.array(actual_cc)-icc))),'voltage_saturation_factor':actual_cc[2]})
    assert saturated>0 and low_voltage>0
    emit('Two allocators: four-quadrant low-voltage saturation full-field passthrough plus independent oracle',{'fixture_count':len(fixtures),'voltage_saturated_count':saturated,'below_PLL_floor_count':low_voltage,'max_independent_state_error':max_oracle_state,'max_independent_control_error':max_oracle_cc,'fixtures':fixtures})


def test_zero_voltage_and_zero_requests():
    report=[]
    for policy in ['p_priority','radial']:
        for request in [{'P_req_W':0.,'Q_req_var':0.},{'P_req_W':800000.,'Q_req_var':0.},{'P_req_W':0.,'Q_req_var':-700000.}]:
            t=.6001;y=np.array(CP['plant_state']);y[:2]=0.;c=ctl();c['applied']=0j
            pre=copy.deepcopy(c);expected,cc,obs=oracle(t,y,c,D,request,0.,policy)
            actual,log=guarded_controller(t,y,c,D,request,0.,IdentityGuard(policy))
            assert all(np.isfinite(x) for x in c.values())
            for key in c:np.testing.assert_allclose(c[key],expected[key],rtol=0,atol=1e-12)
            np.testing.assert_allclose(actual,cc,rtol=0,atol=1e-12)
            assert c['zpll']==pre['zpll'] and c['omega']==pre['omega']
            report.append({'allocator':policy,'request':request,'PLL_state_frozen':True})
    emit('Zero PCC voltage, zero/axis requests: finite result and frozen low-voltage PLL',report)


def test_common_aw_failure_and_whitelist():
    report=[]
    for policy in ['p_priority','radial']:
        for selection in ['optimized','shifted_plan','terminal']:
            for quadrant in range(4):
                t,y,c,request,vs=fixture(quadrant,.4,quadrant%3);before=copy.deepcopy(c);yb=y.copy();nom=copy.deepcopy(c)
                allocators.controller(t,y.copy(),nom,D,request,vs,policy)
                offset=.017-.023j;guard=IdentityGuard(policy,offset,selection)
                cc,log=guarded_controller(t,y,c,D,request,vs,guard)
                vdc=math.sqrt(2*y[2]/D['C_dc_F'])
                delta=D['control_sample_s']*D['current_Kaw_per_s']*vdc*offset*cmath.exp(-1j*before['theta'])
                assert abs((c['zi']-nom['zi'])-delta)<2e-12
                assert abs((c['queued']-nom['queued'])-offset)<1e-15
                for key in set(c)-{'zi','queued'}:assert c[key]==nom[key],key
                np.testing.assert_array_equal(y,yb)
                np.testing.assert_allclose(log['antiwindup_delta_zi'],pair(delta),rtol=0,atol=2e-12)
                assert c['applied']==before['queued']
                assert cc[7]==abs(c['queued'])
                report.append({'allocator':policy,'selection':selection,'quadrant':quadrant+1,'max_AW_error':float(abs(c['zi']-nom['zi']-delta))})
        t,y,c,request,vs=fixture(0,.4,1);before=copy.deepcopy(c);yb=y.copy()
        try:guarded_controller(t,y,c,D,request,vs,RejectGuard(policy))
        except cg.GuardFailure:pass
        else:raise AssertionError('Failed guard unexpectedly admitted')
        assert c==before and np.array_equal(y,yb)
    t,y,c,request,vs=fixture(0,.4,0)
    for bad_policy in ['q_priority','adaptive','',None]:
        before=copy.deepcopy(c);g=IdentityGuard(bad_policy)
        try:guarded_controller(t,y,c,D,request,vs,g)
        except ValueError:pass
        else:raise AssertionError('Undeclared allocator accepted')
        assert c==before and not g.calls
    source=(HERE/'guarded_allocator_controller.py').read_text();tree=ast.parse(source)
    observations=[n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='observation' for x in n.targets)]
    assert len(observations)==1 and isinstance(observations[0].value,ast.Dict)
    keys={k.value for k in observations[0].value.keys};assert keys==cg.CommonGuard.observation_keys
    calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='command']
    assert len(calls)==1 and [ast.unparse(x) for x in calls[0].args]==['t','k','observation','mnom'] and not calls[0].keywords
    assert not any(isinstance(n,ast.Name) and n.id in {'event','case','reference','clearance','future','schedule','workload'} for n in ast.walk(tree))
    emit('Common AW, immutable committed hold, atomic rejection, exact causal observation fields',{'AW_fixtures':report,'failed_allocators_preserve_full_controller_and_plant':['p_priority','radial'],'rejected_undeclared_policies':['q_priority','adaptive','',None],'guard_command_arguments':['t','k','observation','mnom'],'observation_fields':sorted(keys)})


def test_common_guard_regression():
    spec=importlib.util.spec_from_file_location('frozen_gate1_interface_audit',ROOT/'current_guard_gate1/audit_interface_tests.py')
    legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    names=['test_geometry','test_observation','test_primal','test_solver_failure_paths','test_backup_frames','test_no_valid_backup','test_plan_metadata']
    for name in names:getattr(legacy,name)()
    g=cg.CommonGuard(D)
    np.testing.assert_allclose(g.K,np.block([O.Ki*np.eye(2),O.Kq*np.eye(2)]),rtol=0,atol=1e-13)
    assert g.N==O.N==10 and g.Ts==O.Ts==1e-4
    for a,b in [('r','r'),('epsI','current_radius'),('utight','utight'),('itight','itight'),('chord','chord')]:
        assert abs(getattr(g,a)-getattr(O,b))<1e-13
    emit('Unmodified common guard: independent fixed N/K/envelope and saved-plan backup regressions',{'legacy_test_functions':names,'legacy_results':legacy.RESULTS,'N':g.N,'K':g.K.tolist(),'r':g.r,'itight':g.itight,'utight':g.utight,'chord':g.chord,'optimizer_calls':'mocked only; no real optimization or physical trajectory'})


def forbidden(*args,**kwargs):raise AssertionError('Physical or optimization execution is forbidden during this static audit')

def main():
    frozen=list((ROOT/'current_guard_gate1').glob('*.py'))+[ROOT/name for name in EXPECTED]
    before={str(p.relative_to(ROOT)):sha(p) for p in frozen}
    with patch.object(dq,'rhs',forbidden),patch.object(dq,'initial',forbidden),patch.object(dq,'run',forbidden),patch.object(dq,'solve_ivp',forbidden),patch.object(cg,'minimize',forbidden):
        for test in [test_frozen_sources,test_controller,test_zero_voltage_and_zero_requests,test_common_aw_failure_and_whitelist,test_common_guard_regression]:test()
    after={str(p.relative_to(ROOT)):sha(p) for p in frozen}
    assert before==after,'Frozen source changed during audit'
    result={'status':'PASS_STATIC_INTERFACE_ONLY','physical_trajectory_count':0,'new_physical_conditions_executed':0,'real_optimization_calls':0,'test_groups':len(RESULTS),'results':RESULTS,'audited_source_sha256':{'guarded_allocator_controller.py':sha(HERE/'guarded_allocator_controller.py'),'audit_interface_tests.py':sha(__file__)},'frozen_sources_before_and_after':after,'frozen_files_unchanged':True,'qualification':'Finite static arithmetic/interface and saved-plan tests only. Does not establish closed-loop safety, successful health admission, joint DC/SoC invariance, interval proof, or real-time feasibility.'}
    (HERE/'audit_interface_results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ['status','test_groups','physical_trajectory_count','real_optimization_calls','audited_source_sha256']},indent=2))
if __name__=='__main__':main()
