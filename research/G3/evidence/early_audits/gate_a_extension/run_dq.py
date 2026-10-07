"""Prespecified Gate A model diagnostics; unchanged V2.1 physical/controller RHS.
Additional states are passive power quadratures, never fed back into control.
No projection of current, DC energy, or any physical state is used.
"""
from pathlib import Path
import sys,json,hashlib,argparse,time
from collections import deque
import numpy as np
from scipy.integrate import solve_ivp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'gate_a'))
from dq_bench import initial,signals,controller,rhs,battery_draw
from dq_preconditioned import normstate,serial_ctl
PROTO=ROOT/'protocol/GATE_A_EXTENSION_V1.json'
D=json.loads((ROOT/'protocol/GATE_A_LOCKED_V2_1.json').read_text())
F=json.loads(PROTO.read_text());TS=D['control_sample_s'];OUT=ROOT/'gate_a_extension/results';OUT.mkdir(exist_ok=True)

def deserial(c):
 return {k:(complex(*v) if k in ('zi','applied','queued') else v) for k,v in c.items()}
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def request(c,t,event,bias):
 if c['kind']=='step':
  return dict(P_req_W=c['P1_W'] if t>=event else c['P0_W'],Q_req_var=c['Q1_var'] if t>=event else c['Q0_var'])
 if c['kind']=='periodic':
  return dict(P_req_W=bias+c['P_amplitude_W']*np.sin(2*np.pi*c['frequency_Hz']*(t-event)),Q_req_var=c['Q_var'])
 return dict(P_req_W=c['P_W'],Q_req_var=c['Q_var'])

def run(cid,h=1e-5):
 c=next(x for x in F['cases'] if x['id']==cid);kind=c['kind'];tag=f'{cid}_h{h:g}';started=time.monotonic();dense=kind=='sag'
 checks=[];crossings=[];cycles=[];first_hard_seen={};cp=None;qual=0;recovered=None;reason='running';initial_failure=None;phase='fixed';bias=0.;frozen=False;cal_count=confirm_count=period_qual=0;forcing_start=None
 if kind in ('steady','periodic'):
  req=dict(P_req_W=c['P_W'],Q_req_var=c['Q_var']) if kind=='steady' else dict(P_req_W=0.,Q_req_var=0.)
  yy,ctl,initial_record=initial(D,req);y=np.r_[yy,np.zeros(4)];t0=0.;event=None;clear=None
  if kind=='periodic':phase='prewarm'
 elif kind=='step':
  cf=OUT/f"{c['checkpoint_case']}_h{h:g}_checkpoint.json"
  if not cf.exists():cf=OUT/f"{c['checkpoint_case']}_h1e-05_checkpoint.json"
  cp=json.loads(cf.read_text());y=np.array(cp['plant_state']);ctl=deserial(cp['controller']);t0=cp['time_s'];event=t0+c['event_after_checkpoint_s'];clear=event;initial_record={'checkpoint_file':str(cf.relative_to(ROOT)),'sha256':digest(cf)}
 else:
  cf=ROOT/c['checkpoint'];cp=json.loads(cf.read_text());y=np.r_[cp['plant_state'],np.zeros(4)];ctl=deserial(cp['controller']);t0=cp['time_s'];event=t0+c['event_after_checkpoint_s'];clear=event+c['duration_s'];initial_record={'checkpoint_file':str(cf.relative_to(ROOT)),'sha256':digest(cf)}
 ystart=y.copy();WLstart=.75*(D['filter_L_H']+D['grid_L_H'])*(y[0]**2+y[1]**2)
 recovery_target=np.array(cp['normalized_state']) if kind=='sag' else None
 maxend=F['steady_rule']['max_prerun_s'] if kind in ('steady','periodic') else clear+F['recovery_rule']['max_after_event_or_clearance_s']
 trace=[];endpoint=[];states=[];ctrlrows=[];intervals=[];hist=deque(maxlen=21000);lasts={k:None for k in ['current_reference','voltage_modulation','battery_command','pll_frequency']}
 def vs(tt):return c['retained_source_voltage_pu'] if kind=='sag' and event<=tt<clear else 1.
 def decorated_rhs(tt,yy,vv):
  z=rhs(tt,yy,ctl,D,vv);sg=signals(tt,yy,ctl,D,vv)
  return np.r_[z,sg[5].real,sg[5].imag,yy[3],battery_draw(yy[3],D)]
 def measure(tt,yy,vv):
  i,vdc,u,v,pinv,s,psrc=signals(tt,yy,ctl,D,vv);wl=.75*(D['filter_L_H']+D['grid_L_H'])*abs(i)**2
  soc=D['soc_initial']+yy[4]/(D['battery_energy_MWh']*3.6e9)
  er=yy[4]-ystart[4]+yy[2]-ystart[2]+wl-WLstart+yy[5]-ystart[5]+yy[6]-ystart[6]
  return np.array([tt,*yy,abs(i)/D['I_phase_peak_base_A'],vdc/D['V_dc_initial_V'],s.real,s.imag,abs(v)/D['V_phase_peak_base_V'],pinv,psrc,wl,er,soc,vv,ctl['omega']/(2*np.pi)])
 # Row columns: time, 11 states, I=12,Vdc=13,P=14,Q=15,Vp=16,Pinv=17,Psrc=18,WL=19,res=20,SoC=21,Vs=22,f=23
 def emi(tt,yy):return (D['current_emergency_stop_pu']*D['I_phase_peak_base_A'])**2-yy[0]**2-yy[1]**2
 def lo(tt,yy):return yy[2]-.5*D['C_dc_F']*(D['V_dc_min_pu']*D['V_dc_initial_V'])**2
 def hi(tt,yy):return .5*D['C_dc_F']*(D['V_dc_max_pu']*D['V_dc_initial_V'])**2-yy[2]
 def sl(tt,yy):return D['soc_initial']+yy[4]/(D['battery_energy_MWh']*3.6e9)-D['soc_min']
 def sh(tt,yy):return D['soc_max']-D['soc_initial']-yy[4]/(D['battery_energy_MWh']*3.6e9)
 def il(tt,yy):return D['I_phase_peak_base_A']**2-yy[0]**2-yy[1]**2
 for fn in (emi,lo,hi,sl,sh):fn.terminal=True;fn.direction=-1
 il.terminal=False;il.direction=-1
 def safe_and_release(end,window):
  aa=np.array([x for x in intervals if x[1]>end-window+1e-12 and x[1]<=end+1e-12])
  if len(aa)==0:return False,False,{}
  tol=1e-8
  safe=(max(aa[:,2])<=1+tol and min(aa[:,3])>=.8-tol and max(aa[:,4])<=1.1+tol and max(aa[:,5])<=1.2e6*(1+tol) and max(aa[:,6])<=950000*(1+tol) and max(aa[:,7])<=1e6*(1+tol) and min(aa[:,8])>=.2-tol and max(aa[:,9])<=.8+tol)
  release=not np.any(aa[:,12:16])
  met=dict(max_actual_current_pu=float(max(aa[:,2])),min_dc_pu=float(min(aa[:,3])),max_dc_pu=float(max(aa[:,4])),max_pcc_S_VA=float(max(aa[:,5])),max_abs_Ppcc_W=float(max(aa[:,6])),max_abs_Pb_W=float(max(aa[:,7])),max_frequency_error_Hz=float(max(aa[:,10])))
  return bool(safe),bool(release),met
 def savecp(tt):
  return dict(time_s=float(tt),plant_state=y.tolist(),plant_state_names=['id','iq','Wdc','Pb','deltaEb','intPsource','intLoss','intPpcc','intQpcc','intPb','intBatteryDraw'],controller=serial_ctl(ctl),normalized_state=normstate(tt,y,ctl,D).tolist(),protocol_sha256=digest(PROTO),note='Full plant/controller/queue state; battery inventory retained. Fixed P equilibrium is a finite-energy state, not sustainable constant SoC.')
 def check_constant(te,allow_startup):
  nonlocal qual,recovered,cp,phase,event,clear,maxend,forcing_start,cycle_y_start
  period=500
  if len(hist)<2*period:return False
  hh=np.array(hist)[-2*period:];dif=float(np.max(abs(hh[period:]-hh[:period])))
  target_dif=float(np.max(abs(hh[-period:]-recovery_target))) if recovery_target is not None else None
  safe,release,met=safe_and_release(te,.15)
  good=dif<=1e-5 and (target_dif is None or target_dif<=1e-5) and safe and release and met.get('max_frequency_error_Hz',1e9)<=.001
  if not allow_startup and te<clear+.15-1e-12:good=False
  qual=qual+1 if good else 0
  checks.append(dict(time_s=float(te),cycle_difference=dif,target_difference=target_dif,safe_window=safe,limiters_released=release,qualifying=bool(good),successive=qual,metrics=met))
  if qual>=3:
   if kind=='periodic' and phase=='prewarm':
    cp=savecp(te);phase='calibration';forcing_start=event=te;maxend=te+20.;cycle_y_start=y.copy();hist.clear();qual=0
    return False
   recovered=float(te);cp=savecp(te) if kind=='steady' else cp
   return True
  return False
 cycle_y_start=None
 row=measure(t0,y,vs(t0));endpoint.append(row);trace.append(row) if dense else None
 firstk=round(t0/TS);k=firstk
 while k*TS<maxend-1e-12:
  t=k*TS;te=(k+1)*TS
  req=request(c,t,event,bias) if not(kind=='periodic' and phase=='prewarm') else dict(P_req_W=0.,Q_req_var=0.)
  pre=signals(t,y,ctl,D,vs(t));V=abs(pre[3]);rawa=np.clip(req['P_req_W'],-950000,950000)/(1.5*max(V,.1*D['V_phase_peak_base_V']));rawb=req['Q_req_var']/(1.5*max(V,.1*D['V_phase_peak_base_V']))
  info=controller(t,y,ctl,D,req,vs(t))
  flags=[abs(info[5]-rawa)>1e-7 or abs(info[6]-rawb)>1e-7,info[2]<1-1e-10,abs(info[4])>=1e6*(1-1e-12),abs(info[3]-45)<1e-9 or abs(info[3]-75)<1e-9]
  for name,flag in zip(lasts,flags):
   if flag:lasts[name]=float(t)
  ctrlrows.append([*info,req['P_req_W'],req['Q_req_var'],bias,*map(float,flags)])
  cuts=[t,te]
  for z in ([event,clear] if kind in ('step','sag') else []):
   if z is not None and t+1e-14<z<te-1e-14:cuts.append(z)
  cuts=sorted(set(cuts));local=[];stopped=False
  for a,b in zip(cuts[:-1],cuts[1:]):
   vv=vs((a+b)/2);local.append(measure(a,y,vv))
   sol=solve_ivp(lambda tt,yy:decorated_rhs(tt,yy,vv),(a,b),y,method='DOP853',rtol=1e-10,atol=1e-8,max_step=h,events=[emi,lo,hi,sl,sh,il])
   for tt,yy in zip(sol.t[1:],sol.y.T[1:]):local.append(measure(tt,yy,vv))
   crossings.extend(sol.t_events[5].tolist());y=sol.y[:,-1]
   if sol.status==1:reason=['actual_current_emergency','dc_low','dc_high','soc_low','soc_high'][next(i for i in range(5) if len(sol.t_events[i]))];stopped=True;break
   if not sol.success:reason='solver_failure';stopped=True;break
  actualte=float(sol.t[-1]);aa=np.array(local)
  screens={'actual_current':aa[:,12]>1+1e-8,'dc_low':aa[:,13]<.8-1e-8,'dc_high':aa[:,13]>1.1+1e-8,'apparent_power':np.hypot(aa[:,14],aa[:,15])>1.2e6*(1+1e-8),'active_power':abs(aa[:,14])>950000*(1+1e-8),'battery_terminal_power':abs(aa[:,4])>1e6*(1+1e-8),'soc_low':aa[:,21]<.2-1e-8,'soc_high':aa[:,21]>.8+1e-8}
  for key,mask in screens.items():
   if key not in first_hard_seen and np.any(mask):first_hard_seen[key]=float(aa[np.flatnonzero(mask)[0],0])
  intervals.append([t,actualte,max(aa[:,12]),min(aa[:,13]),max(aa[:,13]),max(np.hypot(aa[:,14],aa[:,15])),max(abs(aa[:,14])),max(abs(aa[:,4])),min(aa[:,21]),max(aa[:,21]),max(abs(aa[:,23]-60)),max(abs(aa[:,20])),*map(float,flags)])
  if dense:trace.extend(local)
  ctl['theta']+=ctl['omega']*(actualte-t)
  erow=measure(actualte,y,vs(np.nextafter(actualte,-np.inf)))
  endpoint.append(erow);ns=normstate(actualte,y,ctl,D)
  ns=np.r_[ns,bias/1e6] if kind=='periodic' else ns
  states.append([actualte,*ns]);hist.append(ns)
  if stopped:break
  if kind in ('steady','step','sag') or phase=='prewarm':
   if (k+1)%500==0:
    done=check_constant(te,kind=='steady' or phase=='prewarm')
    if done:reason='completed';break
  else:
   nk=round((te-forcing_start)/TS)
   if nk>0 and nk%10000==0:
    hh=np.array(hist);dif=float(np.max(abs(hh[-10000:]-hh[-20000:-10000]))) if len(hh)>=20000 else None
    de=-float(y[10]-cycle_y_start[10]);de_endpoint=float(y[4]-cycle_y_start[4]);socdelta=(D['soc_initial']+y[4]/(D['battery_energy_MWh']*3.6e9))-(D['soc_initial']+cycle_y_start[4]/(D['battery_energy_MWh']*3.6e9))
    safe,release,met=safe_and_release(te,1.)
    lastctl=np.array(ctrlrows[-10000:]);meanf=float(np.mean(lastctl[:,3]))
    good=dif is not None and dif<=1e-5 and abs(de)<=1 and safe and release and abs(meanf-60)<=.001
    period_qual=period_qual+1 if good else 0
    cy=dict(cycle=nk//10000,time_s=float(te),phase=phase,bias_W=float(bias),battery_stored_energy_delta_J=de,stored_energy_state_difference_J=de_endpoint,soc_converted_difference_J=float(socdelta*D['battery_energy_MWh']*3.6e9),full_cycle_state_difference=dif,mean_actual_Ppcc_W=float(y[7]-cycle_y_start[7]),mean_actual_Qpcc_var=float(y[8]-cycle_y_start[8]),mean_Pb_W=float(y[9]-cycle_y_start[9]),dc_energy_delta_J=float(y[2]-cycle_y_start[2]),mean_PLL_frequency_Hz=meanf,hard_safe=safe,limiters_released=release,qualifying=bool(good),successive=period_qual,metrics=met)
    cycles.append(cy);print(json.dumps({'case':cid,'cycle_update':cy}),flush=True)
    if phase=='calibration':
     cal_count+=1
     if period_qual>=3 or cal_count>=c['calibration_max_cycles']:
      frozen=True;phase='confirmation';period_qual=0;cy['bias_frozen_after_cycle']=True
     else:bias=float(np.clip(bias+de,-50000,0))
    else:
     confirm_count+=1
     if period_qual>=3:recovered=float(te);reason='completed';break
     if confirm_count>=c['confirmation_max_cycles']:reason='periodic_confirmation_failed';break
    cycle_y_start=y.copy()
  k+=1
 if reason=='running':reason='no_precondition_convergence' if kind=='steady' or phase=='prewarm' else ('periodic_confirmation_failed' if kind=='periodic' else 'recovery_timeout')
 ar=np.array(intervals);en=np.array(endpoint);st=np.array(states);ct=np.array(ctrlrows)
 safeall,releasedall,allmetrics=safe_and_release(float(en[-1,0]),float(en[-1,0]-t0)+TS)
 postlimit=np.array([z for z in intervals if kind not in ('step','sag') or z[1]>=event])
 def record_metrics(z):return dict(max_actual_current_pu=float(max(z[:,2])),min_dc_pu=float(min(z[:,3])),max_dc_pu=float(max(z[:,4])),max_pcc_S_VA=float(max(z[:,5])),max_abs_Ppcc_W=float(max(z[:,6])),max_abs_Pb_W=float(max(z[:,7])),min_soc=float(min(z[:,8])),max_soc=float(max(z[:,9])),max_frequency_error_Hz=float(max(z[:,10])),max_energy_residual_J=float(max(z[:,11])))
 summary=dict(case=cid,status='new_gate_a_diagnostic',physical_controller_version='unchanged_Gate_A_V2.1',protocol_sha256=digest(PROTO),source_sha256=digest(__file__),max_step_s=h,initial_record=initial_record,initial_time_s=t0,final_time_s=float(en[-1,0]),stop_reason=reason,checkpoint_time_s=cp['time_s'] if cp else None,event_start_s=event,event_clearance_s=clear,recovered_time_s=recovered,recovery_delay_s=(recovered-clear if recovered is not None and clear is not None else None),all_hard_limits_safe=safeall,complete_safe_recovery=bool(reason=='completed' and safeall),checks=checks,metrics=record_metrics(ar),post_event_metrics=record_metrics(postlimit),current_limit_crossings_s=crossings,first_observed_hard_violation_s=first_hard_seen,max_modulation_norm=float(max(ct[:,7])),max_reference_current_pu=float(max(ct[:,1])),last_limiter_sample_s=lasts,cycles=cycles,frozen_bias_W=float(bias) if frozen else None,calibration_cycles=cal_count,confirmation_cycles=confirm_count,wall_time_s=time.monotonic()-started,storage={'dense_internal_trace':dense,'endpoint_count':len(en),'internal_interval_count':len(ar)},numerical_energy_quadrature_crosscheck_J=float(abs((y[4]-ystart[4])+(y[10]-ystart[10]))),limits='Balanced synthetic averaged topology only; electrical numerical recurrence is not an infinite-time proof. Necessary-energy-margin points are not certified feasible.')
 (OUT/f'{tag}.json').write_text(json.dumps(summary,indent=2)+'\n')
 payload=dict(endpoint_trace=en,full_normalized_state=st,control=ct,interval_extrema=ar,endpoint_columns=np.array(['t','id','iq','Wdc','Pb','deltaEb','intPsource','intLoss','intPpcc','intQpcc','intPb','intBatteryDraw','Ipu','Vdcpu','Ppcc','Qpcc','Vpccpu','Pinv','Psource','WL','energy_residual','soc','Vs','PLL_Hz']),control_columns=np.array(['t','Irefpu','voltage_sat_factor','PLL_Hz','Pb_command','ip_ref','iq_ref_positiveQ','mod_norm','P_req','Q_req','bias','current_ref_clipped','voltage_clipped','source_command_clipped','PLL_clipped']),interval_columns=np.array(['start','end','Imax','Vdcmin','Vdcmax','Smax','Ppcc_absmax','Pb_absmax','socmin','socmax','PLL_abs_error_max','energy_residual_absmax','current_ref_clipped','voltage_clipped','source_command_clipped','PLL_clipped']))
 if dense:payload['dense_trace']=np.array(trace)
 np.savez_compressed(OUT/f'{tag}.npz',**payload)
 if cp is not None and kind in ('steady','periodic'):(OUT/f'{tag}_checkpoint.json').write_text(json.dumps(cp,indent=2)+'\n')
 (OUT/f'{tag}_final_state.json').write_text(json.dumps(savecp(float(en[-1,0])),indent=2)+'\n')
 print(json.dumps({'result_file':str((OUT/f'{tag}.json').relative_to(ROOT)),'case':cid,'stop':reason,'safe':safeall,'final_time_s':summary['final_time_s'],'recovered_time_s':recovered,'metrics':summary['metrics'],'wall_time_s':summary['wall_time_s']},indent=2),flush=True)
 return summary

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--h',type=float,default=1e-5);a=p.parse_args()
 cases=[c['id'] for c in F['cases']] if a.case=='all' else a.case.split(',')
 for cid in cases:run(cid,a.h)
