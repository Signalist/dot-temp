"""Independent abc sag diagnostics for the frozen Gate A extension.

Imports only the unchanged independent abc reference, never parent dq code.
No controller, plant, initialization, or protection-law modification.
Instrumentation and checkpoint/event/recovery orchestration are new.
"""
from __future__ import annotations
import argparse, hashlib, json, math, sys
from collections import deque
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'model_audit/abc_reference'))
from reference_abc import ABCReference,complex_from_abc,clip

RAW_COLUMNS=['t','side','ia','ib','ic','Wdc','Pbat','Ebat','Iactual_pu','Iref_pu','Vdc','Ppcc','Qpcc','Pinv','Psource','Pbus','Pdeplete','Pcopper','Ploss','Pbat_cmd','theta_PLL','omega_PLL','modulation_norm','int_Pinv','int_Psource','int_copper','int_inverter_loss','int_Pbus','int_Pbat','int_depletion','safety_violation_bits','limiter_bits','source_slew_active']
SAFETY_NAMES=['actual_current','Ppcc','Spcc','dc_low','dc_high','Pbat','soc_low','soc_high','modulation']
LIMITER_NAMES=['current_reference','modulation','battery_command','PLL_frequency']
STATE_COLUMNS=['t','side']+['y'+str(i) for i in range(13)]+['theta_PLL','omega_PLL','z_PLL','zi_d','zi_q','m_applied_alpha','m_applied_beta','m_queued_alpha','m_queued_beta','source_command','ref_alpha','ref_beta']+['norm'+str(i) for i in range(14)]+['limiter_bits','PLL_low_voltage_freeze','i_request_abs_A','u_raw_abs_V','u_limit_V','battery_command_raw_W','omega_raw_rad_s']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pack_flags(flags):return sum((1<<i) for i,v in enumerate(flags) if v)

class ExtensionABC(ABCReference):
    def __init__(self,p,ext,case,h,checkpoint):
        self.ext=ext; self.condition=case; self.cp=checkpoint
        case0={'id':case['id'],'P_req_W':case['P_W'],'Q_req_var':case['Q_var'],'source_voltage_pu':1.0,'event':None}
        super().__init__(p,case0,h)
        c=checkpoint; self.start=float(c['time_s'])
        self.theta=c['theta_PLL'];self.omega=c['omega_PLL'];self.zpll=c['z_PLL'];self.zi=complex(*c['z_i'])
        self.m_applied=complex(*c['m_applied']);self.m_queued=complex(*c['m_queued']);self.source_command=c['source_command_W'];self.ref=complex(*c['last_reference_ab'])
        self.onset=self.start+case['event_after_checkpoint_s'];self.clearance=self.onset+case['duration_s']
        self.case['event']={'start_s':self.onset,'end_s':self.clearance,'retained_voltage_pu':case['retained_source_voltage_pu']}
        self.end=self.clearance+ext['recovery_rule']['max_after_event_or_clearance_s']
        self.raw=[];self.controls=[];self.vectors=deque(maxlen=1000);self.safety_window=deque();self.limiter_window=deque()
        self.flags=[False]*4;self.low_voltage=False;self.diag=[0.0]*5;self.last_active=[None]*4;self.first_active=[None]*4
        self.first_violation={x:None for x in SAFETY_NAMES};self.max_violation=np.full(9,-np.inf)
        self.recovery_checks=[];self.consecutive=0;self.state_restored_time=None;self.safe_recovery_time=None
        self.continuous_crossing=None;self.minimum_margin=np.full(9,np.inf);self.target=np.array(c['normalized_vector'])
        self.max_ref=0.0;self.max_mod=0.0

    def orbit(self,t,y):
        i=complex_from_abc(y[:3])*np.exp(-1j*self.w0*t)/self.ibase;z=self.zi/self.vbase
        a=self.m_applied*np.exp(-1j*self.w0*t);q=self.m_queued*np.exp(-1j*self.w0*t)
        return np.array([i.real,i.imag,y[3]/self.Wref,y[4]/1e6,self.theta-self.w0*t,self.zpll/self.w0,z.real,z.imag,a.real,a.imag,q.real,q.imag,self.omega/self.w0,self.source_command/1e6])

    def instrument_sample(self,t,y):
        # Reproduce only the algebra needed to observe clipping; base sample is the sole state updater.
        Vdc,u,eg,vabc,norm,Pi,Ps,Pr,Pl,Pbus,Pdep=self.algebra(t,y,self.source_level(t))
        rot=np.exp(-1j*self.theta);v=complex_from_abc(vabc)*rot;i=complex_from_abc(y[:3])*rot
        V=abs(v);floor=self.p['pll_normalization_floor_pu']*self.vbase;self.low_voltage=V<floor
        wraw=self.omega
        if not self.low_voltage:
            wraw=self.w0+self.p['pll_Kp_per_s']*v.imag/max(V,floor)+self.zpll
            wn=clip(wraw,2*math.pi*self.p['pll_frequency_min_Hz'],2*math.pi*self.p['pll_frequency_max_Hz'])
        else:wn=self.omega
        ep=v/max(V,floor);eq=-1j*ep
        a=self.case['P_req_W']/(1.5*max(V,floor));b=self.case['Q_req_var']/(1.5*max(V,floor));lim=self.p['current_reference_limit_pu']*self.ibase
        bl=clip(b,-lim,lim);cap=math.sqrt(max(0.0,lim**2-bl**2));al=clip(a,-cap,cap)
        ir=al*ep+bl*eq;ur=v+1j*wn*self.Lf*i+self.p['current_Kp_ohm']*(ir-i)+self.zi
        ul=self.p['svpwm_linear_voltage_derating']*Vdc/math.sqrt(3)
        eta=self.p['eta_dc_dc'];bus=Pi+Pl+self.p['auxiliary_power_W'];ff=bus/eta if bus>=0 else bus*eta
        bc=ff+self.p['dc_energy_feedback_gain_per_s']*(self.Wref-y[3])
        tol=self.ext['hard_limits']['comparison_roundoff_tolerance']
        self.flags=[max(abs(a-al),abs(b-bl))/self.ibase>tol, max(0.0,abs(ur)-ul)/self.vbase>tol,
            max(0.0,bc-self.p['battery_terminal_power_max_W'],self.p['battery_terminal_power_min_W']-bc)/1e6>tol,abs(wn-wraw)/self.w0>tol]
        self.diag=[math.hypot(a,b),abs(ur),ul,bc,wraw]
        for j,active in enumerate(self.flags):
            if active:
                if self.first_active[j] is None:self.first_active[j]=t
                self.last_active[j]=t
        super().sample(t,y)
        self.max_ref=max(self.max_ref,abs(self.ref)/self.ibase);self.max_mod=max(self.max_mod,abs(self.m_applied),abs(self.m_queued))
        self.limiter_window.append((t,not any(self.flags)))

    def control_snapshot(self,t,y,side):
        self.controls.append([t,side,*y,self.theta,self.omega,self.zpll,self.zi.real,self.zi.imag,self.m_applied.real,self.m_applied.imag,self.m_queued.real,self.m_queued.imag,self.source_command,self.ref.real,self.ref.imag,*self.orbit(t,y),pack_flags(self.flags),float(self.low_voltage),*self.diag])

    def log_point(self,t,y,side,level=None):
        if level is None:level=self.source_level(t)
        Vdc,u,eg,v,I,Pi,Ps,Pr,Pl,Pbus,Pdep=self.algebra(t,y,level)
        S=1.5*complex_from_abc(v)*complex_from_abc(y[:3]).conjugate();soc=y[5]/self.Ebase;vpu=Vdc/self.p['V_dc_initial_V'];H=self.ext['hard_limits']
        violations=np.array([I/H['actual_current_pu']-1,abs(S.real)/H['P_pcc_abs_W']-1,abs(S)/H['S_pcc_VA']-1,H['dc_pu'][0]-vpu,vpu-H['dc_pu'][1],abs(y[4])/H['P_battery_terminal_abs_W']-1,H['soc'][0]-soc,soc-H['soc'][1],abs(self.m_applied)/H['modulation_norm_max']-1])
        self.max_violation=np.maximum(self.max_violation,violations);self.minimum_margin=np.minimum(self.minimum_margin,-violations)
        tol=H['comparison_roundoff_tolerance'];bad=violations>tol
        for j,x in enumerate(SAFETY_NAMES):
            if bad[j] and self.first_violation[x] is None:self.first_violation[x]=float(t)
        safe=not bool(np.any(bad));freq=abs(self.omega-self.w0)/(2*math.pi)<=self.ext['recovery_rule']['frequency_deviation_Hz']
        self.safety_window.append((t,safe,freq));cut=t-self.ext['recovery_rule']['hard_safe_window_s']
        while self.safety_window and self.safety_window[0][0]<cut-1e-12:self.safety_window.popleft()
        while self.limiter_window and self.limiter_window[0][0]<cut-1e-12:self.limiter_window.popleft()
        dr=(self.source_command-y[4])/self.p['battery_source_tau_s'];slew=dr>self.p['battery_source_ramp_up_W_per_s'] or dr<-self.p['battery_source_ramp_down_W_per_s']
        self.raw.append([t,side,*y[:6],I,abs(self.ref)/self.ibase,Vdc,S.real,S.imag,Pi,Ps,Pbus,Pdep,Pr,Pl,self.source_command,self.theta,self.omega,abs(self.m_applied),*y[6:],pack_flags(bad),pack_flags(self.flags),float(slew)])

    def current_margin(self,y):return 1.0-math.sqrt(2/3*float(y[:3]@y[:3]))/self.ibase

    def recover_check(self,t,y,n):
        vec=self.orbit(t,y);self.vectors.append((t,vec))
        per=round(self.ext['recovery_rule']['compare_period_s']/self.Ts)
        if n%per or t<self.clearance+self.ext['recovery_rule']['compare_period_s']-1e-12 or len(self.vectors)<per:return
        recent=np.array([v for _,v in list(self.vectors)[-per:]])
        err=float(np.max(np.abs(recent-self.target)));tol=self.ext['recovery_rule']['full_state_normalized_tolerance']
        ok=err<=tol;self.consecutive=self.consecutive+1 if ok else 0
        enough=t>=self.clearance+self.ext['recovery_rule']['hard_safe_window_s']-1e-12
        safe=enough and all(x[1] for x in self.safety_window);freq=enough and all(x[2] for x in self.safety_window)
        release=enough and bool(self.limiter_window) and all(x[1] for x in self.limiter_window)
        state=self.consecutive>=self.ext['recovery_rule']['successive_checks'] and freq
        if state and self.state_restored_time is None:self.state_restored_time=t
        all_past_safe=all(x is None for x in self.first_violation.values())
        recovered=state and safe and release and all_past_safe
        if recovered and self.safe_recovery_time is None:self.safe_recovery_time=t
        selferr=None
        if len(self.vectors)>=2*per:
            old=np.array([v for _,v in list(self.vectors)[-2*per:-per]]);selferr=float(np.max(np.abs(recent-old)))
        self.recovery_checks.append({'time_s':t,'target_state_error':err,'self_cycle_error':selferr,'consecutive_target_checks':self.consecutive,'trailing_window_safe':safe,'trailing_frequency_ok':freq,'all_formal_limiters_released':release,'all_post_checkpoint_safe':all_past_safe,'restored_state':state,'complete_safe_recovery':recovered})

    def run_extension(self):
        y=np.array(self.cp['plant_state'],float);y0=y.copy();t=self.start;n=round(t/self.Ts)
        self.log_point(t,y,-1)
        while t<self.end-1e-12 and self.stop is None:
            self.recover_check(t,y,n);self.control_snapshot(t,y,-1)
            self.instrument_sample(t,y);self.control_snapshot(t,y,1);self.log_point(t,y,1)
            nxt=min((n+1)*self.Ts,self.end);ev=[self.onset,self.clearance]
            breaks=[t]+[x for x in ev if t+1e-12<x<nxt-1e-12]+[nxt]
            for left,right in zip(breaks[:-1],breaks[1:]):
                lev=self.source_level((left+right)/2);steps=max(1,math.ceil((right-left)/self.h-1e-9));h=(right-left)/steps
                if abs(left-self.onset)<1e-12 or abs(left-self.clearance)<1e-12:self.log_point(left,y,2,lev)
                for j in range(steps):
                    tj=left+j*h;candidate=self.rk4(tj,y,h,lev);used=h;reached=False
                    if self.stop_margin(candidate)<=0:
                        lo,hi=0.,h
                        for _ in range(35):
                            mid=(lo+hi)/2
                            if self.stop_margin(self.rk4(tj,y,mid,lev))>0:lo=mid
                            else:hi=mid
                        used=hi;candidate=self.rk4(tj,y,used,lev);reached=True
                    if self.continuous_crossing is None and self.current_margin(y)>=0 and self.current_margin(candidate)<0:
                        lo,hi=0.,used
                        for _ in range(35):
                            mid=(lo+hi)/2
                            if self.current_margin(self.rk4(tj,y,mid,lev))>=0:lo=mid
                            else:hi=mid
                        self.continuous_crossing=tj+hi
                    y=candidate;self.theta+=used*self.omega;t=tj+used
                    self.log_point(t,y,-1 if abs(t-right)<1e-12 else 0,lev)
                    if reached:
                        I=math.sqrt(2/3*float(y[:3]@y[:3]))/self.ibase;v=math.sqrt(2*y[3]/self.C)/self.p['V_dc_initial_V'];soc=y[5]/self.Ebase
                        m={'actual_current_emergency':self.p['current_emergency_stop_pu']-I,'dc_undervoltage':v-self.p['V_dc_min_pu'],'dc_overvoltage':self.p['V_dc_max_pu']-v,'soc_low':soc-self.p['soc_min'],'soc_high':self.p['soc_max']-soc};self.stop=min(m,key=m.get);break
                if self.stop:break
            n+=1
        a=np.array(self.raw);d=y-y0;wl=lambda v:.5*self.L*float(v[:3]@v[:3]);duration=t-self.start
        recovery={'state_restored_time_s':self.state_restored_time,'complete_safe_recovery_time_s':self.safe_recovery_time,'clearance_observed':t>=self.clearance,'post_clearance_observed_s':max(0.,t-self.clearance),'checks':self.recovery_checks,'formal_limiter_names':LIMITER_NAMES,'first_active_s':dict(zip(LIMITER_NAMES,self.first_active)),'last_active_s':dict(zip(LIMITER_NAMES,self.last_active)),'release_delay_after_clearance_s':{k:(None if v is None else max(0.,v+self.Ts-self.clearance)) for k,v in zip(LIMITER_NAMES,self.last_active)},'never_active':[k for k,v in zip(LIMITER_NAMES,self.last_active) if v is None]}
        summary={'case':self.condition['id'],'h_max_s':self.h,'status':self.stop or 'completed','start_time_s':self.start,'onset_s':self.onset,'clearance_s':self.clearance,'final_time_s':t,'first_actual_current_crossing_gt_1_s':self.continuous_crossing,'actual_current_peak_pu':float(a[:,8].max()),'reference_current_peak_pu':self.max_ref,'Vdc_min_pu':float(a[:,10].min()/self.p['V_dc_initial_V']),'Vdc_max_pu':float(a[:,10].max()/self.p['V_dc_initial_V']),'Ppcc_abs_peak_W':float(np.abs(a[:,11]).max()),'Spcc_peak_VA':float(np.hypot(a[:,11],a[:,12]).max()),'modulation_peak':self.max_mod,'strict_safety_pass':bool(np.max(self.max_violation)<=0),'roundoff_safety_pass':bool(np.max(self.max_violation)<=self.ext['hard_limits']['comparison_roundoff_tolerance']),'normalized_max_limit_violation':dict(zip(SAFETY_NAMES,self.max_violation.tolist())),'normalized_min_limit_margin':dict(zip(SAFETY_NAMES,self.minimum_margin.tolist())),'first_roundoff_exceeding_violation_s':self.first_violation,'recovery':recovery,'energy_residual_J':{'ac':float(d[6]-d[7]-d[8]-(wl(y)-wl(y0))),'dc':float(d[10]-d[6]-d[9]-self.p['auxiliary_power_W']*duration-d[3]),'battery':float(d[5]+d[12])},'energy_integrals_delta_J':{'Pinv':float(d[6]),'Psource':float(d[7]),'copper':float(d[8]),'inverter':float(d[9]),'Pbus':float(d[10]),'Pbat':float(d[11]),'depletion':float(d[12]),'battery_stored':float(d[5]),'dc_stored':float(d[3]),'inductor_stored':float(wl(y)-wl(y0))},'initial_checkpoint':self.cp,'final_checkpoint':{'t':t,'plant_state':y.tolist(),'theta_PLL':self.theta,'omega_PLL':self.omega,'z_PLL':self.zpll,'z_i':[self.zi.real,self.zi.imag],'m_applied':[self.m_applied.real,self.m_applied.imag],'m_queued':[self.m_queued.real,self.m_queued.imag],'source_command_W':self.source_command,'last_reference_ab':[self.ref.real,self.ref.imag],'normalized_vector':self.orbit(t,y).tolist()},'raw_side_codes':{'-1':'interval endpoint or control preupdate, old applied/source side','0':'ordinary internal point','1':'control postupdate, newly promoted applied command','2':'right side of external source event'},'claims':'Independent fundamental switching-cycle-average abc model; no projection; stopped before unmodeled protection. All violations retained. Frozen extension recovery test only; periodic trajectory not independently replayed.'}
        return a,np.array(self.controls),summary

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',required=True,choices=['sag085','sag0475']);ap.add_argument('--h',type=float,required=True);args=ap.parse_args()
    extpath=ROOT/'protocol/GATE_A_EXTENSION_V1.json';ext=json.loads(extpath.read_text());pp=ROOT/ext['base_protocol'];p=json.loads(pp.read_text());assert sha(pp)==ext['base_protocol_sha256']
    assert sha(extpath)=='a1c399415c6a4b8d17ccf6193963ed73b712fca0890856fbbbf9dcfe1af6bdb8'
    cpfile=ROOT/'model_audit/abc_reference/revalidation_results/preconditioned_v2_1_h10us.json';cp=json.loads(cpfile.read_text())['checkpoint'];case=next(c for c in ext['cases'] if c['id']==args.case)
    sim=ExtensionABC(p,ext,case,args.h,cp);a,c,s=sim.run_extension()
    s['provenance']={'extension_sha256':sha(extpath),'base_protocol_sha256':sha(pp),'abc_source_sha256':sha(ROOT/'model_audit/abc_reference/reference_abc.py'),'extension_source_sha256':sha(__file__),'checkpoint_source_sha256':sha(cpfile),'checkpoint_source':str(cpfile.relative_to(ROOT)),'new_experiment':True,'numpy_version':np.__version__}
    out=Path(__file__).parent/'results';out.mkdir(exist_ok=True);stem=out/(args.case+'_'+str(round(args.h*1e6))+'us')
    np.savez_compressed(str(stem)+'.npz',trace=a,columns=np.array(RAW_COLUMNS),control=c,control_columns=np.array(STATE_COLUMNS))
    s['npz_sha256']=sha(str(stem)+'.npz');s['raw_rows']=len(a);s['control_rows']=len(c)
    Path(str(stem)+'.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k not in ['initial_checkpoint','final_checkpoint']},indent=2),flush=True)
if __name__=='__main__':main()
