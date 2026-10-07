"""Locked V2 first-converged-checkpoint test using the independent abc plant."""
from __future__ import annotations
import argparse,copy,hashlib,json,math
from collections import deque
from pathlib import Path
import numpy as np
from reference_abc import ABCReference,abc_from_complex,complex_from_abc

class PreconditionedABC(ABCReference):
    def __init__(self,p,case,h):
        case=copy.deepcopy(case);case['event']=None
        super().__init__(p,case,h)
        self.safe_history=deque()
        self.sample_vectors=[]
        self.checks=[]
        self.cp=None
        self.consecutive=0
        self.pre=p['prerun_convergence']
        self.interval_samples=round(self.pre['check_period_s']/self.Ts)
        self.compare_samples=round(self.pre['period_compare_s']/self.Ts)
        self.after_checkpoint_duration=0.5

    def orbit_vector(self,t,y):
        ig=complex_from_abc(y[:3])*np.exp(-1j*self.w0*t)/self.ibase
        zi=self.zi/self.vbase
        ma=self.m_applied*np.exp(-1j*self.w0*t)
        mq=self.m_queued*np.exp(-1j*self.w0*t)
        return np.array([ig.real,ig.imag,y[3]/self.Wref,y[4]/1e6,self.theta-self.w0*t,
            self.zpll/self.w0,zi.real,zi.imag,ma.real,ma.imag,mq.real,mq.imag,
            self.omega/self.w0,self.source_command/1e6])

    def log(self,t,y):
        super().log(t,y)
        a=self.rows[-1]
        # Every internal point, including both sides of controller updates.
        I,S,v,Pb,soc,w=a[7],math.hypot(a[10],a[11]),a[9]/self.p['V_dc_initial_V'],a[5],a[6]/self.Ebase,a[17]
        safe=(I<=1.0 and S<=self.p['S_base_VA'] and self.p['V_dc_min_pu']<=v<=self.p['V_dc_max_pu']
            and self.p['battery_terminal_power_min_W']<=Pb<=self.p['battery_terminal_power_max_W']
            and self.p['soc_min']<=soc<=self.p['soc_max']
            and abs(w-self.w0)/(2*math.pi)<=self.pre['frequency_deviation_tolerance_Hz'])
        self.safe_history.append((t,safe))
        cutoff=t-self.pre['hard_safe_window_s']
        while self.safe_history and self.safe_history[0][0]<cutoff-1e-12:self.safe_history.popleft()

    def checkpoint_check(self,t,y,n):
        count=self.compare_samples
        if n>=2*count and n%self.interval_samples==0:
            a=np.array(self.sample_vectors[-count:]);b=np.array(self.sample_vectors[-2*count:-count])
            err=float(np.max(np.abs(a-b)))
            converged=err<=self.pre['normalized_full_orbit_tolerance']
            self.consecutive=self.consecutive+1 if converged else 0
            safe=bool(t>=self.pre['hard_safe_window_s'] and self.safe_history and all(s for _,s in self.safe_history))
            passed=self.consecutive>=self.pre['successive_checks_required'] and safe
            self.checks.append({'t_s':t,'normalized_orbit_error':err,'converged':converged,'consecutive':self.consecutive,'hard_safe_window':safe,'checkpoint':passed})
            if passed:
                self.cp={'time_s':t,'plant_state':y.tolist(),'theta_PLL':self.theta,'omega_PLL':self.omega,
                         'z_PLL':self.zpll,'z_i':[self.zi.real,self.zi.imag],
                         'm_applied':[self.m_applied.real,self.m_applied.imag],
                         'm_queued':[self.m_queued.real,self.m_queued.imag],
                         'source_command_W':self.source_command,'last_reference_ab':[self.ref.real,self.ref.imag],
                         'normalized_vector':self.orbit_vector(t,y).tolist(),
                         'check_record':self.checks[-1],
                         'source_integrals_at_checkpoint':y[6:].tolist()}
                start=t+self.pre['fault_after_checkpoint_s']
                self.case['event']={'start_s':start,'end_s':start+self.pre['fault_duration_s'],'retained_voltage_pu':self.pre['retained_source_voltage_pu']}
                return True
        return False

    def run_preconditioned(self):
        y=np.zeros(13);y[:3]=abc_from_complex(self.eq['i_ab']);y[3]=self.Wref;y[4]=self.eq['Pbat'];y[5]=self.p['soc_initial']*self.Ebase
        y0=y.copy();t=0.0;n=0;end=self.pre['max_prerun_s']
        while t<end-1e-12 and self.stop is None:
            # V2.1: pre-update vectors, right-closed comparison windows.
            if self.cp is None:
                self.sample_vectors.append(self.orbit_vector(t,y))
                if self.checkpoint_check(t,y,n):end=t+self.after_checkpoint_duration
            self.sample(t,y);self.log(t,y)
            nextsample=min((n+1)*self.Ts,end)
            ev=self.case['event'];events=[ev['start_s'],ev['end_s']] if ev else []
            breaks=[t]+[e for e in events if t+1e-12<e<nextsample-1e-12]+[nextsample]
            for left,right in zip(breaks[:-1],breaks[1:]):
                level=self.source_level((left+right)/2);steps=max(1,int(math.ceil((right-left)/self.h-1e-9)));h=(right-left)/steps
                for j in range(steps):
                    tj=left+j*h;candidate=self.rk4(tj,y,h,level);used=h;reached=False
                    if self.stop_margin(candidate)<=0:
                        lo,hi=0.0,h
                        for _ in range(35):
                            mid=(lo+hi)/2
                            if self.stop_margin(self.rk4(tj,y,mid,level))>0:lo=mid
                            else:hi=mid
                        used=hi;candidate=self.rk4(tj,y,used,level);reached=True
                    y=candidate;self.theta+=used*self.omega;t=tj+used;self.log(t,y)
                    if reached and self.stop is None:self.stop='hard_boundary_event'
                    if self.stop:break
                if self.stop:break
            n+=1
        a=np.array(self.rows)
        status=self.stop or ('completed' if self.cp else 'no_converged_checkpoint')
        result={'case':'preconditioned_reference_clip_counterexample','status':status,'h_max_s':self.h,
                'checkpoint':self.cp,'convergence_checks':self.checks,'final_time_s':t,
                'counterexample_found_after_checkpoint':None,'event':self.case['event']}
        if self.cp:
            post=a[a[:,0]>=self.cp['time_s']-1e-12]
            result.update({'post_checkpoint_actual_current_peak_pu':float(post[:,7].max()),
               'post_checkpoint_reference_peak_pu':float(post[:,8].max()),
               'post_checkpoint_apparent_power_peak_VA':float(np.hypot(post[:,10],post[:,11]).max()),
               'post_checkpoint_Vdc_min_pu':float(post[:,9].min()/self.p['V_dc_initial_V']),
               'post_checkpoint_Vdc_max_pu':float(post[:,9].max()/self.p['V_dc_initial_V']),
               'counterexample_found_after_checkpoint':bool(post[:,7].max()>1 and post[:,8].max()<=.95+1e-12)})
            iy=post[post[:,7]>1.0]
            result['first_recorded_post_checkpoint_current_gt_1_s']=float(iy[0,0]) if len(iy) else None
            yc=np.array(self.cp['plant_state']);WL=lambda yy:.5*self.L*float(yy[:3]@yy[:3]);d=y-yc
            result['post_checkpoint_energy_residual_J']={'ac':float(d[6]-d[7]-d[8]-(WL(y)-WL(yc))),
               'dc':float(d[10]-d[6]-d[9]-d[3]),'battery':float(d[5]+d[12])}
        result['initialization_apparent_power_peak_VA']=float(np.hypot(a[:,10],a[:,11]).max()) if not self.cp else float(np.hypot(a[a[:,0]<self.cp['time_s'],10],a[a[:,0]<self.cp['time_s'],11]).max())
        return a,result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--protocol',required=True);ap.add_argument('--h',type=float,default=1e-5);ap.add_argument('--out',required=True);args=ap.parse_args()
    raw=Path(args.protocol).read_bytes();p=json.loads(raw);case=next(x for x in p['case_registry'] if x['id']=='reference_clip_counterexample')
    sim=PreconditionedABC(p,case,args.h);a,s=sim.run_preconditioned()
    s['protocol_sha256']=hashlib.sha256(raw).hexdigest();s['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    s['abc_component_sha256']=hashlib.sha256(Path(__file__).with_name('reference_abc.py').read_bytes()).hexdigest()
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(str(out)+'.npz',trace=a)
    Path(str(out)+'.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
if __name__=='__main__':main()
