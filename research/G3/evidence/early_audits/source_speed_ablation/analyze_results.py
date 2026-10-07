from pathlib import Path
import ast,json,hashlib,sys
import numpy as np
from scipy.integrate import solve_ivp
R=Path(__file__).resolve().parents[1];O=R/'source_speed_ablation/results';B=R/'baseline_allocation/results'
sys.path.insert(0,str(R/'source_speed_ablation'));import run_fast_port as model
D=model.D;TS=D['control_sample_s'];Wref=.5*D['C_dc_F']*1400**2;Wmin=Wref*.8**2;Wmax=Wref*1.1**2;L=D['filter_L_H']+D['grid_L_H'];I=D['I_phase_peak_base_A'];eta=D['eta_dc_dc'];lossmin=1200.;lossmax=1200+6000+1.5*(D['filter_R_ohm']+D['grid_R_ohm'])*I**2;WLmax=.75*L*I**2
# Import only audited algebraic function definitions, not its top-level diagnostic runs.
p=R/'protocol/phase_mechanism/phase_certificate_diagnostic.py';source=p.read_text();tree=ast.parse(source);wanted={'h','hinv','env_time','env_pint','env_p','env_busint','exact_margins'}
ns={'np':np,'eta':eta,'Pmin':-1e6,'Pmax':1e6,'S':1.2e6,'lossmin':lossmin,'lossmax':lossmax,'Wmax':Wmax,'Wmin':Wmin,'WLmax':WLmax}
for n in tree.body:
 if isinstance(n,ast.FunctionDef) and n.name in wanted:exec(compile(ast.Module(body=[n],type_ignores=[]),str(p),'exec'),ns)
ref=np.load(O/'fast_reference_h1e-05.npz');ra=ref['endpoint_trace'];rn=ref['normalized_state'];rjson=json.loads((O/'fast_reference_h1e-05.json').read_text())
def unnorm(n,t):
 w=D['omega_base_rad_s'];v=D['V_phase_peak_base_V'];rot=np.exp(1j*w*t)
 return {'theta':n[4]+w*t,'zpll':n[5]*w,'zi':complex(n[6],n[7])*v,'applied':complex(n[8],n[9])*rot,'queued':complex(n[10],n[11])*rot,'omega':n[12]*w,'pb_command':n[13]*1e6}
replays=[]
def reference_at(t):
 ii=np.searchsorted(ra[:,0],t,side='right')-1
 if abs(ra[ii,0]-t)<1e-11:return ra[ii,1:14].copy()
 tb=ra[ii,0];yy=ra[ii,1:14].copy();ctl=unnorm(rn[ii,1:],tb);model.controller(tb,yy,ctl,D,{'P_req_W':800000.,'Q_req_var':700000.},1.)
 def fun(tt,y):
  sp=model.signals(tt,y,ctl,D,1.)[5];return np.r_[model.rhs(tt,y,ctl,D,1.),sp.real,sp.imag,y[3],model.battery_draw(y[3],D),abs(sp.real-800000),abs(sp.imag-700000)]
 sol=solve_ivp(fun,(tb,ra[ii+1,0]),yy,method='DOP853',rtol=1e-10,atol=1e-8,max_step=1e-5,dense_output=True)
 err=np.max(abs(sol.y[:,-1]-ra[ii+1,1:14]));assert err<1e-4
 replays.append({'requested_time_s':t,'replayed_interval_start_s':float(tb),'replayed_interval_end_s':float(ra[ii+1,0]),'max_state_error_at_recorded_next_endpoint_SI':float(err),'method':'Local <=100us re-evaluation from saved full no-fault state; no new physical condition or full trajectory.'})
 return sol.sol(t)
rows=[]
files=[O/'fast_sag04_h1e-05.json',O/'fast_sag04_h5e-06.json',*[B/(name+'_h1e-05.json') for name in ['slow_p_priority','slow_radial','fast_p_priority','fast_radial']]]
for p in files:
 s=json.loads(p.read_text());z=np.load(p.with_suffix('.npz'));a=z['endpoint_trace'];st=z['normalized_state'];iv=z['interval_extrema'];ct=z['control'];on=s['event_boundary_states']['0.60005'];y0=np.array(on['plant_state']);yt=np.array(s['final_plant_state']);tf=s['final_time_s'];Tobs=min(tf,.75005)-.60005
 yf=np.array(s['event_boundary_states']['0.75005']['plant_state']) if tf>=.75005 else yt
 amp=s['source_ramp_W_per_s'];tau=s['source_tau_s'];mp,mm,tp,tm=ns['exact_margins'](y0[3],y0[2],on['WL_J'],.4,amp,tau)
 Hplus=Wmax+WLmax-y0[2]-on['WL_J'];Hminus=y0[2]+on['WL_J']-Wmin
 services={'observed_fault_duration_s':Tobs,'fraction_of_planned_fault_observed':Tobs/.15,'P_absolute_error_integral_J':float(yf[11]-y0[11]),'Q_absolute_error_integral_var_s':float(yf[12]-y0[12]),'P_actual_signed_integral_J':float(yf[7]-y0[7]),'Q_actual_integral_var_s':float(yf[8]-y0[8]),'P_net_error_integral_J':float(yf[7]-y0[7]-8e5*Tobs),'Q_net_error_integral_var_s':float(yf[8]-y0[8]-7e5*Tobs),'full_observed_P_abs_error_J':float(yt[11]),'full_observed_Q_abs_error_var_s':float(yt[12]),'warning':'Observed-prefix costs with different stop times cannot be ranked as completed mission performance. Unobserved service after a hard stop is not fabricated.'}
 assert services['P_absolute_error_integral_J']+1e-5>=abs(services['P_net_error_integral_J']);assert services['Q_absolute_error_integral_var_s']+1e-5>=abs(services['Q_net_error_integral_var_s'])
 release={}
 for j,name in enumerate(['current_reference','voltage','source_command','PLL_frequency']):
  active=np.flatnonzero(ct[:,8+j]>.5)
  if not len(active):release[name]={'status':'never_active','release_s':None}
  elif active[-1]+1>=len(ct):release[name]={'status':'not_observed_before_stop','last_active_s':float(ct[active[-1],0]),'release_s':None}
  else:release[name]={'status':'observed_exit_no_later_reactivation','last_active_s':float(ct[active[-1],0]),'release_s':float(ct[active[-1]+1,0])}
 paired=None;checks=[];recovery=None
 if s['source_tau_s']==.002:
  yy=reference_at(tf);paired={'time_s':tf,'stored_battery_energy_fault_minus_no_fault_J':float(yt[4]-yy[4]),'PCC_active_energy_fault_minus_no_fault_J':float(yt[7]-yy[7]),'PCC_reactive_integral_fault_minus_no_fault_var_s':float(yt[8]-yy[8]),'absolute_P_error_excess_over_no_fault_J':float(yt[11]-yy[11]),'absolute_Q_error_excess_over_no_fault_var_s':float(yt[12]-yy[12]),'DC_energy_difference_J':float(yt[2]-yy[2]),'note':'Same-state, same hypothetical fast-port no-fault reference. Inventory difference does not restore past service.'}
  # Recovery assessed only where both real trajectories are recorded at identical controller clocks.
  cnt=0
  for end in np.arange(.8,tf+1e-10,.05):
   ids=np.flatnonzero((st[:,0]>end-.05+1e-11)&(st[:,0]<=end+1e-11));prior=ids-500
   if len(ids)!=500 or min(prior)<0:continue
   times=st[ids,0];ri=np.searchsorted(rn[:,0],times-1e-11);assert np.max(abs(rn[ri,0]-times))<1e-10
   dif=float(np.max(abs(st[ids,1:]-rn[ri,1:])));selfdif=float(np.max(abs(st[ids,1:]-st[prior,1:])))
   mask=(iv[:,1]>end-.15+1e-11)&(iv[:,1]<=end+1e-11);v=iv[mask]
   safe=bool(max(v[:,2])<=1+1e-8 and min(v[:,3])>=.8-1e-8 and max(v[:,4])<=1.1+1e-8 and max(v[:,5])<=1.2e6*(1+1e-8) and max(v[:,6])<=.95e6*(1+1e-8) and max(v[:,7])<=1e6*(1+1e-8) and min(v[:,8])>=.2 and max(v[:,9])<=.8)
   free=not bool(np.any(v[:,12:]));freq=float(max(v[:,10]));good=bool(end>=.90005 and dif<=1e-5 and selfdif<=1e-5 and safe and free and freq<=.001);cnt=cnt+1 if good else 0
   checks.append({'time_s':float(end),'same_time_target_difference':dif,'self_50ms_difference':selfdif,'safe_150ms':safe,'unclipped_150ms':free,'PLL_max_error_Hz':freq,'qualifying':good,'successive':cnt})
   if cnt>=3 and recovery is None:recovery=float(end)
 rows.append({'case':s['case'],'h_s':s['h_s'],'port_tau_s':tau,'port_ramp_W_per_s':amp,'allocator':s.get('allocator','q_priority'),'source_result_file':str(p.relative_to(R)),'raw_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'trace_sha256':hashlib.sha256(p.with_suffix('.npz').read_bytes()).hexdigest(),'stop_reason':s['stop_reason'],'end_time_s':tf,'complete_hard_safe':s['complete_hard_safe'],'first_actual_I_crossing_s':s['current_continuous_crossings_s'][0] if s['current_continuous_crossings_s'] else None,'metrics':s['metrics'],'actual_onset_certificate':{'upper_headroom_J':Hplus,'lower_headroom_J':Hminus,'upper_max_prefix_gain_J':float(mp+Hplus),'upper_margin_J':float(mp),'lower_margin_J':float(mm),'upper_peak_prefix_s':float(tp),'meaning':'Positive excludes every actualI/DC-safe controller under this fixed synthetic port. Nonpositive does not prove reachability.'},'service':services,'limiter_release':release,'electrical_recovery_time_s':recovery,'electrical_recovery_checks':checks,'global_safe_recovery':bool(recovery is not None and s['complete_hard_safe']),'paired_reference':paired})
result={'status':'completed_small_fixed_diagnostics','topology_scope':'Synthetic controlled DC port only; neither validated DC/DC nor directly connected battery','baseline_Q_slow_source':'gate_a/preconditioned_dq/h1e-05.json; retained earlier result, no new repeat','analytic_function_source_sha256':hashlib.sha256(source.encode()).hexdigest(),'fast_no_fault_reference':{'raw_file':'source_speed_ablation/results/fast_reference_h1e-05.json','complete_hard_safe':rjson['complete_hard_safe'],'metrics':rjson['metrics'],'P_abs_error_J':rjson['final_plant_state'][11],'Q_abs_error_var_s':rjson['final_plant_state'][12]},'results':rows,'reference_subinterval_re_evaluations':replays,'interpretation':'Faster port removes the old all-policy DC energy exclusion, but all tested fixed allocation rules still violate actual current; Q-priority additionally reaches DC upper limit. Static reference circles do not constitute dynamic current limiting. There is no new method, complete safe fault witness or joint-service success.'}
(O/'AUTHORITATIVE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps([{'case':x['case'],'stop':x['stop_reason'],'I':x['metrics']['I_peak_pu'],'Vdc':x['metrics']['Vdc_max_pu'],'electrical_recovery_s':x['electrical_recovery_time_s'],'global_safe':x['global_safe_recovery'],'service':x['service']} for x in rows],indent=2))
