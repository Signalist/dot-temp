"""Gate A v2: first preregistered converged checkpoint, then fixed balanced sag."""
import json,hashlib
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from dq_bench import initial,signals,controller,rhs
ROOT=Path(__file__).resolve().parents[1];PARAM=ROOT/'protocol/GATE_A_LOCKED_V2_1.json'

def serial_ctl(c): return {k:([v.real,v.imag] if isinstance(v,complex) else v) for k,v in c.items()}
def normstate(t,y,c,d):
    return np.array([y[0]/d['I_phase_peak_base_A'],y[1]/d['I_phase_peak_base_A'],y[2]/(.5*d['C_dc_F']*d['V_dc_initial_V']**2),y[3]/1e6,c['theta']-d['omega_base_rad_s']*t,c['zpll']/d['omega_base_rad_s'],c['zi'].real/d['V_phase_peak_base_V'],c['zi'].imag/d['V_phase_peak_base_V'],*(np.array([c['applied'],c['queued']])*np.exp(-1j*d['omega_base_rad_s']*t)).view(float),c['omega']/d['omega_base_rad_s'],c['pb_command']/1e6])

def execute(h=1e-5):
 d=json.loads(PARAM.read_text());rule=d['prerun_convergence'];case=dict(next(x for x in d['case_registry'] if x['id']=='reference_clip_counterexample'));case['event']=None
 y,ctl,init=initial(d,case);y0=y.copy();Ts=d['control_sample_s'];nperiod=round(rule['check_period_s']/Ts)
 traces=[];history=[];checks=[];controls=[];counter=0;cp=None;fault_start=None;fault_end=None;reason='no_convergence';first_over=None;all_events=[]
 def emi(t,y):return d['current_emergency_stop_pu']**2*d['I_phase_peak_base_A']**2-y[0]**2-y[1]**2
 def elo(t,y):return y[2]-.5*d['C_dc_F']*(d['V_dc_min_pu']*d['V_dc_initial_V'])**2
 def ehi(t,y):return .5*d['C_dc_F']*(d['V_dc_max_pu']*d['V_dc_initial_V'])**2-y[2]
 def ilim(t,y):return d['I_phase_peak_base_A']**2-y[0]**2-y[1]**2
 for f in [emi,elo,ehi]:f.terminal=True;f.direction=-1
 ilim.terminal=False;ilim.direction=-1
 def rec(t,yy,vs):
  i,vdc,u,v,pinv,spcc,psrc=signals(t,yy,ctl,d,vs);soc=d['soc_initial']+yy[4]/(d['battery_energy_MWh']*3.6e9)
  WL=.75*(d['filter_L_H']+d['grid_L_H'])*abs(i)**2;res=yy[4]+yy[2]-y0[2]+WL-init['WL0']+yy[5]+yy[6]
  traces.append([t,*yy,abs(i)/d['I_phase_peak_base_A'],vdc/d['V_dc_initial_V'],spcc.real,spcc.imag,abs(v)/d['V_phase_peak_base_V'],pinv,psrc,WL,res,soc,vs,ctl['omega']/(2*np.pi)])
 def hard_window(start,end):
  aa=np.array(traces);aa=aa[(aa[:,0]>=start-1e-12)&(aa[:,0]<=end+1e-12)]
  safe=(len(aa)>0 and np.max(aa[:,8])<=1+1e-10 and np.max(np.hypot(aa[:,10],aa[:,11]))<=d['S_base_VA']*(1+1e-10) and np.min(aa[:,9])>=d['V_dc_min_pu'] and np.max(aa[:,9])<=d['V_dc_max_pu'] and np.max(abs(aa[:,4]))<=1e6*(1+1e-10) and np.min(aa[:,17])>=d['soc_min'] and np.max(aa[:,17])<=d['soc_max'])
  return bool(safe),dict(max_actual_current_pu=float(np.max(aa[:,8])),max_pcc_S_VA=float(np.max(np.hypot(aa[:,10],aa[:,11]))),min_dc_pu=float(np.min(aa[:,9])),max_dc_pu=float(np.max(aa[:,9])))
 rec(0,y,1.)
 maxsteps=round((rule['max_prerun_s']+rule['fault_duration_s']+.001)/Ts)
 for k in range(maxsteps):
  t=k*Ts;te=(k+1)*Ts
  if cp is None and t>=rule['max_prerun_s']-1e-12:break
  def vs_at(tt):return rule['retained_source_voltage_pu'] if fault_start is not None and fault_start<=tt<fault_end else 1.
  controls.append(controller(t,y,ctl,d,case,vs_at(t)))
  cuts=sorted([t,te]+([fault_start] if fault_start is not None and t<fault_start<te else [])+([fault_end] if fault_end is not None and t<fault_end<te else []))
  stopped=False
  for a,b in zip(cuts[:-1],cuts[1:]):
   vv=vs_at((a+b)/2)
   sol=solve_ivp(lambda tt,yy:rhs(tt,yy,ctl,d,vv),(a,b),y,method='DOP853',rtol=1e-10,atol=1e-8,max_step=h,events=[emi,elo,ehi,ilim])
   for tt,yy in zip(sol.t[1:],sol.y.T[1:]):rec(tt,yy,vv)
   y=sol.y[:,-1];all_events.extend(sol.t_events[3].tolist())
   if sol.status==1:reason=['actual_current_emergency','dc_low','dc_high'][next(i for i in range(3) if len(sol.t_events[i]))];stopped=True;break
   if not sol.success:reason='solver_failure';stopped=True;break
  ctl['theta']+=ctl['omega']*(sol.t[-1]-t)
  if stopped:break
  history.append(normstate(te,y,ctl,d))
  if cp is None and (k+1)%nperiod==0 and len(history)>=2*nperiod:
   hh=np.array(history[-2*nperiod:]);diff=float(np.max(abs(hh[nperiod:]-hh[:nperiod])))
   safe,metrics=hard_window(max(0,te-rule['hard_safe_window_s']),te)
   aa=np.array(traces);freqmask=aa[:,0]>=te-rule['hard_safe_window_s'];freqerr=float(np.max(abs(aa[freqmask,19]-d['f_base_Hz'])))
   good=diff<=rule['normalized_full_orbit_tolerance'] and safe and freqerr<=rule['frequency_deviation_tolerance_Hz']
   counter=counter+1 if good else 0;checks.append(dict(time_s=te,max_normalized_cycle_difference=diff,hard_safe=safe,max_frequency_deviation_Hz=freqerr,qualifying=bool(good),successive=counter,metrics=metrics))
   if counter>=rule['successive_checks_required']:
    cp=dict(time_s=te,plant_state=y.tolist(),plant_state_names=['id','iq','Wdc','Pb','deltaEb','intPsource','intLoss'],controller=serial_ctl(ctl),normalized_state=normstate(te,y,ctl,d).tolist(),safe_window=metrics,full_protocol_sha256=hashlib.sha256(PARAM.read_bytes()).hexdigest(),note='First qualified checkpoint under frozen rule. Startup history retained; fixed positive-P pre-run is finite discharge, not sustainable zero-energy orbit.')
    fault_start=te+rule['fault_after_checkpoint_s'];fault_end=fault_start+rule['fault_duration_s'];reason='fault_running'
  if cp is not None and te>=fault_end+.05:reason='completed';break
 a=np.array(traces);ct=np.array(controls);out=ROOT/'gate_a/preconditioned_dq';out.mkdir(exist_ok=True);tag=f'h{h:g}'
 fault=a[a[:,0]>=fault_start-1e-12] if fault_start is not None else np.empty((0,a.shape[1]))
 summary=dict(protocol_sha256=hashlib.sha256(PARAM.read_bytes()).hexdigest(),max_step_s=h,stop_reason=reason,last_time_s=float(a[-1,0]),checkpoint_time_s=cp['time_s'] if cp else None,fault_start_s=fault_start,fault_end_s=fault_end,startup_max_pcc_S_VA=float(np.max(np.hypot(a[a[:,0]<.1,10],a[a[:,0]<.1,11]))),all_max_actual_current_pu=float(np.max(a[:,8])),max_reference_current_pu=float(np.max(ct[:,1])),max_abs_total_energy_residual_J=float(np.max(abs(a[:,16]))),checks=checks,
 fault_metrics=dict(max_actual_current_pu=float(np.max(fault[:,8])),max_dc_pu=float(np.max(fault[:,9])),first_actual_current_crossing_s=next((z for z in all_events if z>=fault_start),None),elapsed_to_terminal_s=float(a[-1,0]-fault_start)) if len(fault) else None)
 (out/f'{tag}.json').write_text(json.dumps(summary,indent=2)+'\n');(out/f'{tag}_checkpoint.json').write_text(json.dumps(cp,indent=2)+'\n');np.savez_compressed(out/f'{tag}.npz',trace=a,control=ct,normalized_control_snapshots=np.array(history))
 print(json.dumps(summary,indent=2),flush=True);return summary
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--h',type=float,default=1e-5);args=p.parse_args();execute(args.h)
