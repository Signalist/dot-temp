"""Frozen Gate0 tube-MPSC lifted to a causal, offline sampled interface.
Existing common inner-layer baseline; no joint DC/SoC or real-time qualification.
"""
from pathlib import Path
import json,time,copy,hashlib
import numpy as np
from scipy.optimize import minimize,LinearConstraint,NonlinearConstraint
ROOT=Path(__file__).resolve().parents[1]

def v2(z):return np.array([z.real,z.imag])
def c2(x):return complex(*x)
def rot(phi):return np.array([[np.cos(phi),-np.sin(phi)],[np.sin(phi),np.cos(phi)]])
class GuardFailure(RuntimeError):
    def __init__(self,reason,record):super().__init__(reason);self.record=record

class CommonGuard:
    """Only command's observed electrical fields cross the information interface."""
    observation_keys=frozenset(['i_ab','vp_ab','vdc','applied_ab','queued_ab'])
    def __init__(self,d):
        self.d={k:v for k,v in d.items() if isinstance(v,(int,float)) and not isinstance(v,bool)};d=self.d;self.Ts=1e-4;self.N=10;self.Ib=d['I_phase_peak_base_A'];self.Eb=d['V_phase_peak_base_V'];self.w=d['omega_base_rad_s'];self.L=d['filter_L_H']+d['grid_L_H'];self.R=d['filter_R_ohm']+d['grid_R_ohm'];self.lam=self.R/self.L
        self.Vbar=1400.;self.Vlo=1120.;self.Vhi=1540.;self.mmax=.95/np.sqrt(3);self.num=1e-8;self.Ec=.7*self.Eb
        self.a=self.aof(self.Ts);self.b=self.bof(self.Ts);self.c=self.cof(self.Ts);self.Rot=rot(-self.w*self.Ts);self.Ki=-self.a*self.a/self.c;self.Kq=-self.a
        self.K=np.block([self.Ki*np.eye(2),self.Kq*np.eye(2)]);self.A=np.zeros((4,4));self.A[:2,:2]=self.a*self.Rot;self.A[:2,2:]=self.c*self.Rot;self.B=np.zeros((4,2));self.B[2:]=self.Rot;self.F=self.A+self.B@self.K
        self.r=self.b*(280*self.mmax+.3*self.Eb)/self.Ib;self.epsI=(1+self.a)*self.r;self.umargin=abs(self.Ki)*self.r;self.utight=self.mmax-self.umargin
        qbar=self.Ec*self.je(self.Ts)/(self.Vbar*self.b);self.sbar=np.r_[np.zeros(2),v2(qbar)];self.mbar=v2(np.exp(1j*self.w*self.Ts)*qbar);self.aff=np.r_[-self.Rot@v2(self.Ec*self.je(self.Ts)/self.Ib),np.zeros(2)]
        mu_domain=1+(self.Vbar*self.utight+self.Ec)*self.b/self.Ib;d1=(self.Vbar*self.utight+self.Ec+self.R*self.Ib*mu_domain)/(self.L*self.Ib);self.M2=self.lam*d1+self.w*self.Ec/(self.L*self.Ib);self.chord=self.M2*(self.Ts/4)**2/8;self.itight=1-self.epsI-self.chord-self.num
        self.Tomega=np.zeros((4,4));self.Tomega[:2,:2]=np.eye(2);self.Tomega[:,2:]=self.F[:,:2]
        old=json.loads((ROOT/'current_guard_gate0/GATE0_RESULTS.json').read_text())['contracts'][1]
        for key,val in [('A',self.A),('B',self.B),('K',self.K),('terminal_center_sbar',self.sbar),('terminal_nominal_input_mbar',self.mbar)]:assert np.max(abs(np.array(old[key])-val))<1e-14,key
        assert abs(self.r-old['disturbance_radius_current_pu'])<1e-14
        self.seed={'z':np.array(old['nominal_states']),'v':np.array(old['nominal_inputs']),'origin_k':0,'source':'audited_Gate0_plan'}
        self.certificate_version='GATE0_MPSC_DESIGN_V1:'+hashlib.sha256((ROOT/'protocol/GATE0_MPSC_DESIGN_V1.json').read_bytes()).hexdigest()
        self.last_plan=None;self.phase0=None;self.t0=None
    def aof(self,t):return np.exp(-self.lam*t)
    def bof(self,t):return -np.expm1(-self.lam*t)/self.R
    def cof(self,t):return self.Vbar*self.bof(t)/self.Ib
    def je(self,t):return (np.exp(1j*self.w*t)-np.exp(-self.lam*t))/(self.R+1j*self.w*self.L)
    def omega_witness(self,error):
        w1=self.Rot.T@error[2:]/self.Ki;w0=error[:2]-self.a*self.Rot@w1
        norms=np.array([np.linalg.norm(w0),np.linalg.norm(w1)])
        residual=np.max(abs(self.Tomega@np.r_[w0,w1]-error))
        return {'witnesses':[w0.tolist(),w1.tolist()],'disk_norms':norms.tolist(),'max_disk_excess':float(max(norms)-self.r),'inverse_residual_inf':float(residual),'inside_numeric':bool(max(norms)<=self.r+self.num and residual<=self.num)}
    def observe(self,t,obs):
        if set(obs)!=self.observation_keys:raise ValueError('Guard observation whitelist mismatch')
        vals=np.r_[v2(obs['i_ab']),v2(obs['vp_ab']),obs['vdc'],v2(obs['applied_ab']),v2(obs['queued_ab'])]
        if not np.all(np.isfinite(vals)):raise ValueError('Nonfinite measured interface')
        d=self.d;i=obs['i_ab'];vp=obs['vp_ab'];u=obs['vdc']*obs['applied_ab']
        e=(self.L/d['filter_L_H'])*vp-(d['grid_L_H']/d['filter_L_H'])*(u-d['filter_R_ohm']*i)-d['grid_R_ohm']*i
        if self.phase0 is None:self.phase0=float(np.angle(e));self.t0=float(t)
        phi=self.phase0+self.w*(t-self.t0);rr=np.exp(-1j*phi);ep=e*rr/self.Eb;s=np.r_[v2(i*rr/self.Ib),v2(obs['queued_ab']*rr)]
        flags={'Vdc_domain':bool(self.Vlo<=obs['vdc']<=self.Vhi),'source_magnitude':bool(.4-self.num<=ep.real<=1+self.num),'source_phase':bool(abs(ep.imag)<=self.num),'committed_modulation':bool(abs(obs['queued_ab'])<=self.mmax+self.num),'actual_current':bool(abs(i)/self.Ib<=1+self.num)}
        return s,phi,{'source_estimate_ab':v2(e).tolist(),'source_in_causal_frame_pu':v2(ep).tolist(),'causal_phase_rad':phi,'phase_origin_rad':self.phase0,'phase_origin_time_s':self.t0,'state':s.tolist(),'flags':flags,'domain_ok':all(flags.values())}
    def validate_plan(self,s,z,v,witnesses=None):
        """Direct physical-form recomputation separate from the lifted optimizer matrices."""
        if z.shape!=(self.N+1,4) or v.shape!=(self.N,2) or not np.all(np.isfinite(np.r_[z.ravel(),v.ravel()])):return {'accepted':False,'reason':'bad_shape_or_nonfinite'}
        om=self.omega_witness(s-z[0]);dyn=max(float(np.max(abs(z[j+1]-self.A@z[j]-self.B@v[j]-self.aff))) for j in range(self.N));terminal=float(np.max(abs(z[-1]-self.sbar)))
        input_ex=max(np.linalg.norm(x)-self.utight for x in v);queue_ex=max(np.linalg.norm(x[2:])-self.utight for x in z);node_ex=-np.inf
        for j in range(self.N):
            for t in np.linspace(0,self.Ts,5):
                current=self.aof(t)*c2(z[j,:2])+self.cof(t)*c2(z[j,2:])-self.Ec*self.je(t)/self.Ib
                node_ex=max(node_ex,abs(current)-self.itight)
        u0=v[0]+self.K@(s-z[0]);actual_input_ex=np.linalg.norm(u0)-self.mmax
        witness_eq=0. if witnesses is None else float(np.max(abs(self.Tomega@np.array(witnesses).ravel()-(s-z[0]))))
        maxres=float(max(0,dyn,terminal,input_ex,queue_ex,node_ex,om['max_disk_excess'],om['inverse_residual_inf'],witness_eq,actual_input_ex))
        return {'accepted':bool(maxres<=self.num and np.linalg.norm(u0)<=self.mmax),'max_residual':maxres,'dynamics_inf':dyn,'terminal_inf':terminal,'input_norm_excess':float(input_ex),'queue_norm_excess':float(queue_ex),'current_node_norm_excess':float(node_ex),'actual_command_norm_excess':float(actual_input_ex),'initial_witness_equality_inf':witness_eq,'initial_Omega':om,'terminal_tail_correction_applied':False}
    def solve_point(self,s,mnom):
        start=time.monotonic();nx=4+2*self.N;P0=np.zeros((4,nx));P0[:,:4]=-self.Tomega;J=[P0];off=[s.copy()]
        for j in range(self.N):
            pj=self.A@J[-1];pj[:,4+2*j:6+2*j]+=self.B;J.append(pj);off.append(self.A@off[-1]+self.aff)
        E=J[-1];eb=off[-1]-self.sbar;norms=[]
        def add(M,o,rad,label):norms.append((np.array(M),np.array(o),float(rad),label))
        for j in [0,1]:
            M=np.zeros((2,nx));M[:,2*j:2*j+2]=np.eye(2);add(M,np.zeros(2),self.r,'initial_Omega_w'+str(j))
        for j in range(self.N):
            M=np.zeros((2,nx));M[:,4+2*j:6+2*j]=np.eye(2);add(M,np.zeros(2),self.utight,'nominal_input_'+str(j))
        for j in range(self.N+1):add(J[j][2:],off[j][2:],self.utight,'nominal_queue_'+str(j))
        for j in range(self.N):
            for k,t in enumerate(np.linspace(0,self.Ts,5)):
                Cflow=np.block([self.aof(t)*np.eye(2),self.cof(t)*np.eye(2)]);add(Cflow@J[j],Cflow@off[j]-v2(self.Ec*self.je(t)/self.Ib),self.itight,'current_'+str(j)+'_'+str(k))
        Cfirst=np.zeros((2,nx));Cfirst[:,4:6]=np.eye(2);Cfirst[:,:4]+=self.K@self.Tomega
        def obj(x):e=Cfirst@x-mnom;return float(e@e)
        def grad(x):return 2*Cfirst.T@(Cfirst@x-mnom)
        def g(x):return np.array([rad*rad-np.sum((M@x+o)**2) for M,o,rad,_ in norms])
        def gj(x):return np.array([-2*(M@x+o)@M for M,o,rad,_ in norms])
        xstart=np.linalg.lstsq(E,-eb,rcond=None)[0];before=time.monotonic()
        try:
            sol=minimize(obj,xstart,jac=grad,method='SLSQP',constraints=[LinearConstraint(E,-eb,-eb),NonlinearConstraint(g,0,np.inf,jac=gj)],options={'ftol':1e-12,'maxiter':500,'disp':False})
            after=time.monotonic();x=sol.x;z=np.array([p@x+o for p,o in zip(J,off)]);v=x[4:].reshape(self.N,2);check=self.validate_plan(s,z,v,x[:4].reshape(2,2));last=time.monotonic()
            info={'success_flag':bool(sol.success),'status':int(sol.status),'message':str(sol.message),'iterations':int(sol.nit),'objective':float(sol.fun),'independent_primal':check,'accepted_suboptimal':bool(check['accepted'] and not sol.success),'nominal_states':z.tolist(),'nominal_inputs':v.tolist(),'initial_Omega_witnesses':x[:4].reshape(2,2).tolist(),'timing':{'setup_s':before-start,'solve_s':after-before,'validation_s':last-after,'point_total_s':last-start},'kkt_residual':None,'kkt_note':'Not recomputed online; independent primal validation required each call.'}
            return {'z':z,'v':v},info
        except Exception as exc:
            after=time.monotonic();return None,{'success_flag':False,'status':-999,'message':repr(exc),'independent_primal':{'accepted':False},'timing':{'setup_s':before-start,'solve_s':after-before,'validation_s':0.,'point_total_s':after-start}}
    def backup(self,k,s):
        p=self.last_plan
        if p is None:return None,{'valid':False,'reason':'no_saved_plan'}
        if not p.get('backup_ready',False) or p.get('certificate_version')!=self.certificate_version:return None,{'valid':False,'reason':'plan_not_ready_or_certificate_mismatch'}
        if p.get('phase_origin_rad')!=self.phase0 or p.get('phase_origin_time_s')!=self.t0:return None,{'valid':False,'reason':'plan_frame_mismatch'}
        j=k-p['origin_k']
        if j<0:return None,{'valid':False,'reason':'negative_plan_index'}
        center=p['z'][j] if j<self.N else self.sbar;nom=p['v'][j] if j<self.N else self.mbar;om=self.omega_witness(s-center);u=nom+self.K@(s-center)
        ok=om['inside_numeric'] and np.linalg.norm(u)<=self.mmax
        return (u if ok else None),{'valid':bool(ok),'type':'shifted_plan' if j<self.N else 'terminal','plan_origin_k':p['origin_k'],'plan_index':j,'membership':om,'modulation_norm':float(np.linalg.norm(u)),'source':p.get('source','accepted_online_plan')}
    def command(self,t,k,obs,mnom_ab):
        start=time.monotonic();s,phi,observed=self.observe(t,obs);mnom=v2(mnom_ab*np.exp(-1j*phi));log={'sample_k':int(k),'time_s':float(t),'observation':observed,'nominal_modulation_frame':mnom.tolist(),'conditional_scope':'current/modulation while declared source and Vdc domains hold; not jointDC/SoC'}
        if not observed['domain_ok']:
            log.update(admitted=False,reason='domain_or_contract_lost',total_wall_s=time.monotonic()-start);raise GuardFailure(log['reason'],log)
        if self.last_plan is None:
            chk=self.validate_plan(s,self.seed['z'],self.seed['v'])
            log['seed_validation']=chk
            if chk['accepted']:
                self.last_plan=copy.deepcopy(self.seed)
                self.last_plan.update(phase_origin_rad=self.phase0,phase_origin_time_s=self.t0,origin_frame_phase_rad=phi,certificate_version=self.certificate_version,primal_validation=chk,backup_ready=True)
        plan,solver=self.solve_point(s,mnom);log['solver']=solver
        if plan is not None and solver['independent_primal']['accepted']:
            plan.update(origin_k=int(k),source='accepted_online_plan',phase_origin_rad=self.phase0,phase_origin_time_s=self.t0,origin_frame_phase_rad=phi,certificate_version=self.certificate_version,primal_validation=solver['independent_primal'],backup_ready=True);self.last_plan=plan;u=plan['v'][0]+self.K@(s-plan['z'][0]);choice={'valid':True,'type':'optimized','plan_origin_k':int(k),'plan_index':0,'membership':solver['independent_primal']['initial_Omega']}
        else:u,choice=self.backup(k,s)
        total=time.monotonic()-start;log.update(selection=choice,total_wall_s=total,total_over_100us=total>self.Ts,solve_over_100us=solver['timing']['solve_s']>self.Ts)
        if u is None:
            log.update(admitted=False,reason='lost_certificate_no_valid_backup');raise GuardFailure(log['reason'],log)
        m_ab=c2(u)*np.exp(1j*phi);log.update(saved_plan_metadata={key:self.last_plan[key] for key in ['origin_k','phase_origin_rad','phase_origin_time_s','origin_frame_phase_rad','certificate_version','backup_ready']},admitted=True,safe_modulation_frame=u.tolist(),safe_modulation_ab=v2(m_ab).tolist(),nominal_modulation_ab=v2(mnom_ab).tolist(),modification_norm=float(np.linalg.norm(u-mnom)),reason='accepted_numerical_plan_or_backup')
        log['total_wall_s']=time.monotonic()-start;log['total_over_100us']=log['total_wall_s']>self.Ts
        return m_ab,log
