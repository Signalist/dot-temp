"""Independent function-level gate1 tests. Never calls rhs/solve_ivp/run.
Every plant input below is an isolated static fixture, not a physical trajectory.
"""
from pathlib import Path
import ast
import cmath
import copy
import hashlib
import json
import math
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
from audit_algebra_oracle import AlgebraOracle, as_complex, as_real, state
import common_guard as cg
from guarded_controller import guarded_controller, original_controller

HERE=Path(__file__).resolve().parent
O=AlgebraOracle()
D={k:v for k,v in O.d.items() if isinstance(v,(str,int,float,bool))}
CP=O.cp
S0=np.array(O.results['observation_interface']['aligned_initial_s0'])
Z=np.array(O.saved['nominal_states']);V=np.array(O.saved['nominal_inputs'])
MN=np.array(O.saved['first_nominal_PI_modulation'])
REQ={'P_req_W':800000.,'Q_req_var':700000.}
RESULTS=[]


def emit(name, details=None):
    RESULTS.append({'name':name,'status':'PASS','details':details or {}})


def ctl():
    return {k:(as_complex(v) if isinstance(v,list) else v) for k,v in CP['controller'].items()}


def observation(s,phi,source_pu=1.,applied=.21-.09j,vdc=1400.):
    i=as_complex(s[:2])*O.Ibase*cmath.exp(1j*phi)
    q=as_complex(s[2:])*cmath.exp(1j*phi)
    ap=applied*cmath.exp(1j*phi)
    e=source_pu*O.Ebase*cmath.exp(1j*phi)
    lf,lg=D['filter_L_H'],D['grid_L_H'];rf,rg=D['filter_R_ohm'],D['grid_R_ohm']
    vp=(lg*(vdc*ap-rf*i)+lf*(e+rg*i))/(lf+lg)
    return {'i_ab':i,'vp_ab':vp,'vdc':vdc,'applied_ab':ap,'queued_ab':q}


def failed_solve(*args):
    return None,{'success_flag':False,'status':9,'message':'audit injected solver failure',
                 'independent_primal':{'accepted':False},
                 'timing':{'setup_s':0.,'solve_s':0.,'validation_s':0.,'point_total_s':0.}}


def start_seed(g,phi=.73):
    g.solve_point=failed_solve
    m,log=g.command(.6,0,observation(S0,phi),as_complex(MN)*cmath.exp(1j*phi))
    assert log['admitted'] and log['selection']['type']=='shifted_plan'
    return m,log


def simple_solver(x,success):
    def fake(*args,**kwargs):
        return SimpleNamespace(x=np.array(x),success=success,status=0 if success else 9,
                               message='audit fake candidate',nit=1,fun=0.)
    return fake


def test_geometry():
    g=cg.CommonGuard(D)
    sample_cases=[]
    for w0,w1 in [(0j,0j),(.4*O.r*cmath.exp(.3j),.7*O.r*cmath.exp(-.6j)),(1.01*O.r+0j,0j)]:
        error=O.omega_forward(w0,w1)
        actual=g.omega_witness(error);expected=O.omega_inverse(error)
        assert actual['inside_numeric']==expected['inside']
        np.testing.assert_allclose(actual['disk_norms'],expected['disk_norms'],rtol=0,atol=1e-14)
        sample_cases.append(actual)
    fp=state(.9*O.current_radius+0j,.9*O.input_radius+0j)
    assert not g.omega_witness(fp)['inside_numeric']
    emit('Omega explicit inverse and correlated-set rejection',{'fixtures':sample_cases})


def test_observation():
    g=cg.CommonGuard(D)
    phi0=.73;t0=.6
    s,p,rec=g.observe(t0,observation(S0,phi0))
    np.testing.assert_allclose(s,S0,rtol=0,atol=3e-14)
    assert abs(p-phi0)<1e-13 and rec['domain_ok']
    checks=[]
    for j in [1,9,10,500]:
        phi=phi0+O.omega*j*O.Ts
        sp,pp,rp=g.observe(t0+j*O.Ts,observation(O.sbar,phi,source_pu=.4))
        np.testing.assert_allclose(sp,O.sbar,rtol=0,atol=3e-14)
        assert abs(pp-phi)<1e-12 and rp['domain_ok']
        checks.append({'sample':j,'phase_error':pp-phi})
    bad=observation(S0,phi0)
    bad['event']={'start_s':.61}
    try:g.observe(t0,bad)
    except ValueError:pass
    else:raise AssertionError('event object accepted')
    fresh=cg.CommonGuard(D);fresh.observe(t0,observation(S0,phi0))
    _,_,phase_bad=fresh.observe(t0+O.Ts,observation(S0,phi0+O.omega*O.Ts+.01))
    assert not phase_bad['domain_ok'] and not phase_bad['flags']['source_phase']
    for amp in [.39,1.01]:
        _,_,r=fresh.observe(t0,observation(S0,phi0,source_pu=amp))
        assert not r['domain_ok']
    emit('Measured nonzero phase, fixed 60Hz advancement, zero-current handling and whitelist',{'clock_checks':checks})


def test_primal():
    g=cg.CommonGuard(D)
    check=g.validate_plan(S0,Z,V,np.array(O.saved['initial_Omega_witnesses']))
    reference=O.validate_plan(S0,Z,V)
    assert check['accepted'] and reference['accepted']
    assert abs(check['max_residual']-reference['max_primal_residual'])<1e-14
    invalids={}
    for field in ['input','queue','current','terminal','nonfinite']:
        z=Z.copy();v=V.copy()
        if field=='input':v[4,0]=3
        elif field=='queue':z[3,2]=3
        elif field=='current':z[2,0]=3
        elif field=='terminal':z[-1,0]+=.01
        else:v[4,0]=np.nan
        bad=g.validate_plan(S0,z,v)
        assert not bad['accepted'],field
        invalids[field]=bad
    broad=AlgebraOracle('broad_circle').saved
    bp=g.validate_plan(S0,np.array(broad['nominal_states']),np.array(broad['nominal_inputs']))
    assert not bp['accepted']
    emit('Independent full-plan primal checks and invalid candidate rejection',{'saved_plan':check,'bad_candidates':invalids,'broad_failed_plan':bp})


def test_one_cold_solve():
    g=cg.CommonGuard(D)
    plan,info=g.solve_point(S0,MN)
    assert plan is not None and info['independent_primal']['accepted']
    independent=O.validate_plan(S0,plan['z'],plan['v'])
    assert independent['accepted']
    m=as_complex(plan['v'][0])+O.feedback(S0-plan['z'][0])
    assert abs(abs(m-as_complex(MN))-.214580692240)<2e-7
    assert info['timing']['setup_s']>=0 and info['timing']['validation_s']>=0
    emit('One fixed cold-start algebraic SLSQP and independent postcheck',{'solver':info,'independent':independent,'first_modification':abs(m-as_complex(MN))})


def test_solver_failure_paths():
    xgood=np.r_[np.array(O.saved['initial_Omega_witnesses']).ravel(),V.ravel()]
    wide=AlgebraOracle('broad_circle').saved
    xbad=np.r_[np.array(wide['initial_Omega_witnesses']).ravel(),np.array(wide['nominal_inputs']).ravel()]
    reports=[]
    for success in [True,False]:
        g=cg.CommonGuard(D)
        with patch.object(cg,'minimize',simple_solver(xbad,success)):
            m,log=g.command(.6,0,observation(S0,0),as_complex(MN))
        assert not log['solver']['independent_primal']['accepted']
        assert log['selection']['type']=='shifted_plan'
        expected=as_complex(V[0])+O.feedback(S0-Z[0])
        assert abs(m-expected)<3e-14
        reports.append({'claimed_success':success,'chosen':log['selection'],'candidate_residual':log['solver']['independent_primal']['max_residual']})
    g=cg.CommonGuard(D)
    with patch.object(cg,'minimize',simple_solver(xgood,False)):
        m,log=g.command(.6,0,observation(S0,0),as_complex(MN))
    assert log['solver']['accepted_suboptimal'] and log['selection']['type']=='optimized'
    g=cg.CommonGuard(D)
    with patch.object(cg,'minimize',simple_solver(np.full_like(xgood,np.nan),True)):
        m,log=g.command(.6,0,observation(S0,0),as_complex(MN))
    assert not log['solver']['independent_primal']['accepted'] and log['selection']['type']=='shifted_plan'
    emit('Reject failed wide/nonfinite output despite success flag; flag feasible nonoptimal acceptance',{'wide_injections':reports})


def test_backup_frames():
    reports=[]
    for j in [1,O.N-1,O.N,O.N+3]:
        g=cg.CommonGuard(D);start_seed(g)
        error=O.omega_forward(.21*O.r*cmath.exp(.43j),.39*O.r*cmath.exp(-.67j))
        center=Z[j] if j<O.N else O.sbar
        nominal=as_complex(V[j]) if j<O.N else O.mbar
        s=center+error;phi=.73+O.omega*j*O.Ts
        obs=observation(s,phi,source_pu=.7)
        before=copy.deepcopy(obs)
        m,log=g.command(.6+j*O.Ts,j,obs,as_complex(MN)*cmath.exp(1j*phi))
        expected=(nominal+O.feedback(error))*cmath.exp(1j*phi)
        assert abs(m-expected)<4e-13
        assert log['selection']['plan_index']==j
        assert log['selection']['type']==('shifted_plan' if j<O.N else 'terminal')
        assert obs==before
        reports.append({'j':j,'selection':log['selection'],'phase_rad':phi,'modulation_error':abs(m-expected)})
    g=cg.CommonGuard(D);start_seed(g)
    assert g.backup(-1,S0)[0] is None
    bad=state(.9*O.current_radius+0j,.9*O.input_radius+0j)
    assert g.backup(O.N,O.sbar+bad)[0] is None
    emit('Forced backup j=1,N-1,N,N+3, negative/outside index, phase and immutable observation',{'fixtures':reports})


class PassGuard:
    def __init__(self,offset=0j,selection='optimized'):
        self.offset=offset;self.selection=selection;self.received=None
    def command(self,t,k,obs,mnom):
        self.received=copy.deepcopy(obs)
        return mnom+self.offset,{'selection':{'type':self.selection}}


class RejectGuard:
    def command(self,*args):
        raise cg.GuardFailure('audit forced no valid backup',{'admitted':False})


def diff_fields(a,b):
    return {k:float(abs(a[k]-b[k])) for k in a}


def test_controller():
    fixtures=[]
    for variant in [0,1,2,3]:
        y=np.array(CP['plant_state'],float);c=ctl();t=.6+variant*.0001;vs=[1.,.8,.4,1.][variant]
        if variant:
            y[0]*=1-.09*variant;y[1]*=1-.07*variant
            y[2]*=1+.003*variant;c['zi']+=complex(7*variant,-2*variant)
            c['theta']+=.04*variant
        ybefore=y.copy();c0=copy.deepcopy(c);expected=copy.deepcopy(c)
        ec=original_controller(t,y,expected,D,REQ,vs)
        guard=PassGuard();ac,log=guarded_controller(t,y,c,D,REQ,vs,guard)
        errors=diff_fields(c,expected)
        assert max(errors.values())==0.,errors
        np.testing.assert_array_equal(ac,ec);np.testing.assert_array_equal(y,ybefore)
        assert c['applied']==c0['queued']
        assert guard.received['applied_ab']==c0['applied'] and guard.received['queued_ab']==c0['queued']
        assert set(guard.received)==cg.CommonGuard.observation_keys
        fixtures.append({'variant':variant,'all_controller_fields_max_error':max(errors.values())})
    antiwindup=[]
    for selection in ['optimized','shifted_plan','terminal']:
        c=ctl();y=np.array(CP['plant_state']);old=copy.deepcopy(c);nom=copy.deepcopy(c)
        original_controller(.6,y,nom,D,REQ,1.)
        offset=.017-.023j;guard=PassGuard(offset,selection)
        _,log=guarded_controller(.6,y,c,D,REQ,1.,guard)
        vdc=math.sqrt(2*y[2]/D['C_dc_F'])
        expected_delta=D['control_sample_s']*D['current_Kaw_per_s']*vdc*offset*cmath.exp(-1j*old['theta'])
        assert abs(c['zi']-nom['zi']-expected_delta)<2e-13
        assert abs(c['queued']-nom['queued']-offset)<1e-15
        for k in ['zpll','omega','pb_command','theta','applied']:assert c[k]==nom[k],k
        antiwindup.append({'selection':selection,'delta_expected':as_real(expected_delta).tolist(),'delta_observed':log['antiwindup_delta_zi']})
    c=ctl();y=np.array(CP['plant_state']);before=copy.deepcopy(c);yb=y.copy()
    try:guarded_controller(.6,y,c,D,REQ,1.,RejectGuard())
    except cg.GuardFailure:pass
    else:raise AssertionError('guard failure swallowed')
    assert c==before;np.testing.assert_array_equal(y,yb)
    emit('Original Q-priority pass-through, pre-promotion source/PLL, held queue, same-Kaw AW and atomic failure',{'pass_through_fixtures':fixtures,'antiwindup':antiwindup})


def test_no_valid_backup():
    g=cg.CommonGuard(D);g.solve_point=failed_solve
    s=state(.98+0j,0j)
    obs=observation(s,.73)
    before=copy.deepcopy(obs)
    try:g.command(.6,0,obs,as_complex(MN))
    except cg.GuardFailure as ex:
        assert not ex.record['admitted'] and ex.record['reason']=='lost_certificate_no_valid_backup'
    else:raise AssertionError('Unadmitted state obtained arbitrary command')
    assert obs==before
    g=cg.CommonGuard(D)
    obs=observation(S0,.73,vdc=1550.)
    with patch.object(g,'solve_point',side_effect=AssertionError('Solver called after domain failure')):
        try:g.command(.6,0,obs,as_complex(MN))
        except cg.GuardFailure as ex:assert ex.record['reason']=='domain_or_contract_lost'
        else:raise AssertionError('Invalid Vdc admitted')
    emit('No valid backup stops; domain rejection precedes optimization; no observation mutation')



def test_plan_metadata():
    required={'origin_k','phase_origin_rad','phase_origin_time_s','origin_frame_phase_rad',
              'certificate_version','primal_validation','backup_ready'}
    g=cg.CommonGuard(O.d)
    assert all(isinstance(v,(int,float)) and not isinstance(v,bool) for v in g.d.values())
    assert 'case_registry' not in g.d and 'prerun_convergence' not in g.d
    start_seed(g)
    assert required.issubset(g.last_plan)
    assert g.last_plan['primal_validation']['accepted'] and g.last_plan['backup_ready']
    checks=[]
    for key,value in [('backup_ready',False),('certificate_version','wrong'),
                      ('phase_origin_rad',g.phase0+.1),('phase_origin_time_s',g.t0+.1)]:
        old=g.last_plan[key];g.last_plan[key]=value
        command,info=g.backup(0,S0)
        assert command is None and not info['valid']
        checks.append({'tampered':key,'rejection':info['reason']})
        g.last_plan[key]=old
    # An accepted (mocked optimizer) feasible plan at a later sample must get
    # that sample's origin, rather than inherit the initial seed's origin.
    g=cg.CommonGuard(D)
    xgood=np.r_[np.array(O.saved['initial_Omega_witnesses']).ravel(),V.ravel()]
    with patch.object(cg,'minimize',simple_solver(xgood,True)):
        g.command(.6,0,observation(S0,.73),as_complex(MN)*cmath.exp(.73j))
        phi=.73+7*O.omega*O.Ts
        _,log=g.command(.6+7*O.Ts,7,observation(S0,phi),as_complex(MN)*cmath.exp(1j*phi))
    assert required.issubset(g.last_plan)
    assert g.last_plan['origin_k']==7 and log['selection']['plan_origin_k']==7
    assert abs(g.last_plan['origin_frame_phase_rad']-phi)<1e-13
    u,b=g.backup(8,Z[1])
    expected=as_complex(g.last_plan['v'][1])+O.feedback(Z[1]-g.last_plan['z'][1])
    assert b['valid'] and b['plan_index']==1 and abs(as_complex(u)-expected)<1e-14
    emit('Saved plan provenance, numeric parameter whitelist, and metadata tamper rejection',{'rejections':checks,'later_plan_origin':g.last_plan['origin_k']})

def main():
    for test in [test_geometry,test_observation,test_primal,test_one_cold_solve,test_solver_failure_paths,test_backup_frames,test_controller,test_no_valid_backup,test_plan_metadata]:
        test()
    files=['common_guard.py','guarded_controller.py','audit_interface_tests.py','audit_algebra_oracle.py']
    out={'status':'PASS_FUNCTION_LEVEL_ONLY','test_groups':len(RESULTS),'results':RESULTS,
         'source_sha256':{f:hashlib.sha256((HERE/f).read_bytes()).hexdigest() for f in files},
         'physical_trajectory_count':0,'new_physical_conditions_executed':0,
         'qualification':'Finite arithmetic/algebraic interface tests, not closed-loop qualification, interval proof, joint DC/SoC invariance or realtime feasibility.'}
    (HERE/'audit_interface_results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':out['status'],'test_groups':len(RESULTS),'source_sha256':out['source_sha256']},indent=2))

if __name__=='__main__':main()
