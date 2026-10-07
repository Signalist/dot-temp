"""Independent abc replication of the single frozen fast P-priority condition.

The only control-law edit is Q-to-P ordering in ABCReference.sample. Runtime
imports the existing abc implementation only. The shared physical checkpoint is
coordinate transformed once, not used for state projection during integration.
"""
from pathlib import Path
import argparse, copy, difflib, hashlib, inspect, json, math, sys, textwrap
import numpy as np
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT/'model_audit/abc_reference'))
import reference_abc as original
from preconditioned_abc import PreconditionedABC

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
jsonwrite = lambda p,x: Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
SOURCE = textwrap.dedent(inspect.getsource(original.ABCReference.sample))
OLD = '''    blim = clip(b,-Imax,Imax)
    alim = clip(a,-math.sqrt(max(0.0,Imax**2-blim**2)),math.sqrt(max(0.0,Imax**2-blim**2)))'''
NEW = '''    alim = clip(a,-Imax,Imax)
    blim = clip(b,-math.sqrt(max(0.0,Imax**2-alim**2)),math.sqrt(max(0.0,Imax**2-alim**2)))'''
assert SOURCE.count(OLD)==1
PATCHED = SOURCE.replace(OLD, NEW).replace('Q-priority projection','P-priority projection')
assert PATCHED.replace(NEW,OLD).replace('P-priority projection','Q-priority projection') == SOURCE
# Returning local temporaries adds diagnostics without changing the state update.
INSTRUMENTED = PATCHED + '    return locals()\n'
namespace = dict(vars(original))
exec(compile(INSTRUMENTED,str(OUT/'sample_p_priority.py'),'exec'),namespace)
P_SAMPLE = namespace['sample']
(OUT/'sample_p_priority.py').write_text('from reference_abc import *\n\n'+INSTRUMENTED)

PARAM = ROOT/'protocol/GATE_A_LOCKED_V2_1.json'
FREEZE = ROOT/'protocol/GATE_A_ALLOCATION_BASELINES_V1.json'
F=json.loads(FREEZE.read_text()); p0=json.loads(PARAM.read_text())
CPFILE=ROOT/F['common_initial_checkpoint']; CP=json.loads(CPFILE.read_text())
assert sha(CPFILE)==F['checkpoint_sha256'] and sha(PARAM)==F['base_sha256']
p=copy.deepcopy(p0)
p.update(battery_source_tau_s=.002,battery_source_ramp_up_W_per_s=50e6,battery_source_ramp_down_W_per_s=50e6)
c=copy.deepcopy(next(c for c in p['case_registry'] if c['id']=='reference_clip_counterexample'))
c.update(id='fast_p_priority_independent_abc',duration_s=2.75005,event={'start_s':.60005,'end_s':.75005,'retained_voltage_pu':.4})
INPUTS=[PARAM,FREEZE,CPFILE,ROOT/'protocol/GATE_A_SOURCE_SPEED_V1.json',ROOT/'baseline_allocation/allocators.py',ROOT/'baseline_allocation/ALLOCATION_CHANGE_AUDIT.json',ROOT/'model_audit/abc_reference/reference_abc.py',ROOT/'model_audit/abc_reference/preconditioned_abc.py',ROOT/'model_audit/abc_reference/revalidation_results/preconditioned_v2_1_h10us.json',ROOT/'baseline_allocation/results/fast_p_priority_h1e-05.json',ROOT/'baseline_allocation/results/fast_p_priority_h1e-05.npz']
INPUT_HASHES={str(x.relative_to(ROOT)):sha(x) for x in INPUTS}

CTL_COLS=['theta','omega','zpll','zi_re','zi_im','applied_re','applied_im','queued_re','queued_im','source_command']
TRACE_COLS=['t','phase','source_pu','ia','ib','ic','Wdc','Pbat','Ebat','int_Pinv','int_Psource','int_copper','int_inverter_loss','int_Pbus','int_Pbat','int_depletion','Iactual_pu','Vdc_pu','Ppcc_W','Qpcc_var','Vpcc_pu','Pinv_W','Psource_W','WL_J','PLL_Hz','reference_last_pu']+CTL_COLS
DIAG_COLS=['t','Iactual_pu','Vdc_pu','Vpcc_pu','PLL_e','PLL_wraw','PLL_omega_new','a_raw','b_raw','a_limited','b_limited','iref_re','iref_im','iref_pu','i_PLL_re','i_PLL_im','v_PLL_re','v_PLL_im','uu_re','uu_im','us_re','us_im','voltage_saturation_factor','current_error_re','current_error_im','Ki_error_re','Ki_error_im','Kaw_residual_re','Kaw_residual_im','source_command','mnorm','Ppcc_W','Qpcc_var']

class IndependentPABC(PreconditionedABC):
    def __init__(self,h):
        super().__init__(copy.deepcopy(p),copy.deepcopy(c),h)
        self.case=copy.deepcopy(c)
        q=CP['controller']; t=CP['time_s']; yy=CP['plant_state']
        self.theta=q['theta'];self.omega=q['omega'];self.zpll=q['zpll'];self.zi=complex(*q['zi'])
        self.m_applied=complex(*q['applied']);self.m_queued=complex(*q['queued']);self.source_command=q['pb_command']
        y=np.zeros(13);y[:3]=original.abc_from_complex(complex(*yy[:2])*np.exp(1j*self.w0*t))
        y[3:6]=[yy[2],yy[3],self.p['soc_initial']*self.Ebase+yy[4]]
        # Last reference is diagnostic-only and absent in the DQ checkpoint.
        # Mark it unavailable until the first sample computes it.
        self.ref=complex(float('nan'),float('nan'))
        self.yinitial=y.copy();self.trace=[];self.before=[];self.after=[];self.pre_norm=[];self.post_norm=[];self.diag=[]
        self.crossings=[];self.events=[];self.reason=None
    def ctl(self):
        return [self.theta,self.omega,self.zpll,self.zi.real,self.zi.imag,self.m_applied.real,self.m_applied.imag,self.m_queued.real,self.m_queued.imag,self.source_command]
    def record(self,t,y,phase,level):
        A=self.algebra(t,y,level);Vdc,u,eg,v,norm,Pi,Ps,Pr,Pl,Pbus,Pdep=A
        vi=original.complex_from_abc(v);ii=original.complex_from_abc(y[:3]);S=1.5*vi*ii.conjugate()
        self.trace.append([t,phase,level,*y,norm,Vdc/1400,S.real,S.imag,abs(vi)/self.vbase,Pi,Ps,.5*self.L*float(y[:3]@y[:3]),self.omega/(2*np.pi),abs(self.ref)/self.ibase,*self.ctl()])
    def sample(self,t,y):
        self.before.append([t,*y,*self.ctl()]);self.pre_norm.append([t,*self.orbit_vector(t,y)])
        self.record(t,y,0,self.source_level(t))
        d=P_SAMPLE(self,t,y)
        self.after.append([t,*y,*self.ctl()]);self.post_norm.append([t,*self.orbit_vector(t,y)])
        vi=original.complex_from_abc(d['vabc']);ii=original.complex_from_abc(y[:3]);S=1.5*vi*ii.conjugate()
        ki=self.p['current_Ki_ohm_per_s']*d['ei'];aw=self.p['current_Kaw_per_s']*(d['us']-d['uu'])
        self.diag.append([t,d['norm'],d['Vdc']/1400,d['V']/self.vbase,d.get('err',float('nan')),d.get('wraw',float('nan')),self.omega,d['a'],d['b'],d['alim'],d['blim'],d['iref'].real,d['iref'].imag,abs(d['iref'])/self.ibase,d['i'].real,d['i'].imag,d['v'].real,d['v'].imag,d['uu'].real,d['uu'].imag,d['us'].real,d['us'].imag,abs(d['us'])/abs(d['uu']),d['ei'].real,d['ei'].imag,ki.real,ki.imag,aw.real,aw.imag,self.source_command,abs(d['new_mod']),S.real,S.imag])
        self.record(t,y,1,self.source_level(t))
    def imargin(self,y):return 1.0-math.sqrt(2/3*float(y[:3]@y[:3]))/self.ibase
    def locate(self,t,y,h,level,margin):
        lo,hi=0.,h
        for _ in range(45):
            mid=(lo+hi)/2
            if margin(self.rk4(t,y,mid,level))>0:lo=mid
            else:hi=mid
        return hi
    def run_one(self):
        y=self.yinitial.copy();t=.6;end=c['duration_s']
        for k in range(round(t/self.Ts),math.ceil(end/self.Ts)):
            t=k*self.Ts;te=min((k+1)*self.Ts,end);self.sample(t,y);theta0=self.theta
            cuts=sorted(set([t,te]+[z for z in [.60005,.75005] if t+1e-14<z<te-1e-14]))
            for left,right in zip(cuts[:-1],cuts[1:]):
                level=self.source_level((left+right)/2)
                self.record(left,y,2,level)
                n=max(1,math.ceil((right-left)/self.h-1e-9));dt=(right-left)/n
                for j in range(n):
                    tj=left+j*dt;used=dt;candidate=self.rk4(tj,y,dt,level)
                    if self.stop_margin(candidate)<=0:
                        used=self.locate(tj,y,dt,level,self.stop_margin);candidate=self.rk4(tj,y,used,level)
                        self.reason='actual_current_numerical_emergency' if math.sqrt(2/3*float(candidate[:3]@candidate[:3]))/self.ibase>=1.1-1e-10 else 'dc_or_soc_stop'
                    if self.imargin(y)>0 and self.imargin(candidate)<=0:
                        cr=self.locate(tj,y,used,level,self.imargin);self.crossings.append(tj+cr)
                    y=candidate;tlast=tj+used;self.theta=theta0+(tlast-t)*self.omega
                    self.record(tlast,y,3,level)
                    if self.reason:break
                if abs(tlast-.60005)<1e-12 or abs(tlast-.75005)<1e-12:
                    self.events.append({'t':tlast,'plant_state':y.tolist(),'controller':self.ctl(),'note':'theta advanced to boundary, all held quantities preserved'})
                if self.reason:break
            if self.reason:break
        a=np.array(self.trace);d=np.array(self.diag);yi=self.yinitial;dy=y-yi
        energy={'ac_residual_J':float(dy[6]-dy[7]-dy[8]-(.5*self.L*float(y[:3]@y[:3])-.5*self.L*float(yi[:3]@yi[:3]))),'dc_residual_J':float(dy[10]-dy[6]-dy[9]-self.p['auxiliary_power_W']*(tlast-.6)-dy[3]),'battery_residual_J':float(dy[5]+dy[12])}
        target=np.array(CP['normalized_state'])
        old=json.loads((ROOT/'model_audit/abc_reference/revalidation_results/preconditioned_v2_1_h10us.json').read_text())['checkpoint']
        initial_norm=np.array(self.pre_norm)[0,1:]
        result={'case':c['id'],'physical_conditions':1,'max_step_s':self.h,'integrator':'original independent abc fixed RK4 with original RHS, exact sample/event splitting and bisection stop location','start_s':.6,'stop_s':tlast,'stop_reason':self.reason or 'completed','actual_1pu_crossings_s':self.crossings,'actual_Imax_pu':float(max(a[:,16])),'iref_max_pu':float(max(d[:,13])),'Vdc_min_pu':float(min(a[:,17])),'Vdc_max_pu':float(max(a[:,17])),'sample_Vpcc_min_pu':float(min(d[:,3])),'PLL_max_frequency_deviation_Hz':float(max(abs(d[:,6]/(2*np.pi)-60))),'voltage_saturation_factor_min':float(min(d[:,22])),'current_antiwindup_term_max_V_per_s':float(max(np.hypot(d[:,27],d[:,28]))),'max_abc_current_sum_A':float(max(abs(a[:,3:6].sum(axis=1)))),'energy':energy,'full_same_initial_state_normalized_max_error':float(max(abs(initial_norm-target))),'independent_original_abc_checkpoint_normalized_max_difference':float(max(abs(np.array(old['normalized_vector'])-target))),'initial_battery_E_J':float(yi[5]),'initial_battery_energy_normalized_roundtrip_error':float(abs((yi[5]-p['soc_initial']*self.Ebase)-CP['plant_state'][4])/self.Ebase),'event_boundary_states':self.events,'final_state':y.tolist(),'final_controller':self.ctl(),'claims':'Independent coordinate/integration implementation of the same fundamental averaged synthetic controlled-port model. Actual 1.0pu is the hard constraint. 1.1pu only terminates numerics, not hardware protection validation. No post-stop, clearance or recovery claims.','input_sha256':INPUT_HASHES}
        tag=f'fast_p_priority_abc_h{self.h:g}'
        np.savez_compressed(OUT/f'{tag}.npz',trace=a,trace_columns=np.array(TRACE_COLS),sample_before=np.array(self.before),sample_after=np.array(self.after),sample_state_columns=np.array(['t']+TRACE_COLS[3:16]+CTL_COLS),normalized_before=np.array(self.pre_norm),normalized_after=np.array(self.post_norm),control=np.array(self.diag),control_columns=np.array(DIAG_COLS))
        jsonwrite(OUT/f'{tag}.json',result)
        return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--h',type=float,required=True);args=ap.parse_args()
    result=IndependentPABC(args.h).run_one()
    assert all(sha(ROOT/k)==v for k,v in INPUT_HASHES.items())
    audit={'input_sha256':INPUT_HASHES,'only_parameter_changes':{k:[p0[k],p[k]] for k in p if p[k]!=p0[k]},'original_sample_sha256':hashlib.sha256(SOURCE.encode()).hexdigest(),'allocation_only_control_text_verified':True,'additional_instrumentation':'return locals() only, read-only state snapshots in wrapper','sample_diff':list(difflib.unified_diff(SOURCE.splitlines(),PATCHED.splitlines(),fromfile='reference_abc.sample',tofile='P_priority_sample')),'runtime_DQ_imports':sorted(k for k in sys.modules if k in ['dq_bench','dq_preconditioned','allocators','run_baselines']),'coordinate_conversion':'iabc=Re((id+j iq) exp(j omega0 t) exp(j[0,-2pi/3,+2pi/3])); Ebat=soc_initial*Ebase+deltaEb; Wdc,Pbat and all PI/PLL/held/queued states preserved. Diagnostic-only abc integral channels start at zero; original DQ cumulative diagnostics retained in source checkpoint. Last reference is absent from DQ checkpoint and marked NaN before first sample; it never enters dynamics.','source_files_unchanged_after_run':True}
    assert not audit['runtime_DQ_imports']
    jsonwrite(OUT/'IMPLEMENTATION_AUDIT.json',audit)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
