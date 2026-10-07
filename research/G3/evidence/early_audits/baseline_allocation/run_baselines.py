"""Four preregistered standard allocation baselines; no policy tuning or candidate method."""
from pathlib import Path
import sys,json,hashlib,argparse,time
import numpy as np
from scipy.integrate import solve_ivp
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'gate_a'))
from dq_bench import rhs,signals,battery_draw
from allocators import controller
from dq_preconditioned import normstate,serial_ctl
P=R/'protocol/GATE_A_ALLOCATION_BASELINES_V1.json';F=json.loads(P.read_text());D=json.loads((R/F['base_protocol']).read_text())
OUT=R/'baseline_allocation/results';OUT.mkdir(exist_ok=True)
COLS=['t','id','iq','Wdc','Pb','deltaEb','intPsource','intLoss','intPpcc','intQpcc','intPb','intBatteryDraw','int_abs_P_error','int_abs_Q_error','Ipu','Vdcpu','Ppcc','Qpcc','Vpccpu','Pinv','Psource','WL','energy_residual','soc','Vs','PLL_Hz']

def run(cid,h):
 start=time.monotonic();c=next(c for c in F['dynamic_runs'] if c['id']==cid);ev=c['event'];port=F['ports'][c['port']];D.update(battery_source_tau_s=port['tau_s'],battery_source_ramp_up_W_per_s=port['ramp_W_per_s'],battery_source_ramp_down_W_per_s=port['ramp_W_per_s']);cp=json.loads((R/F['common_initial_checkpoint']).read_text());y=np.r_[cp['plant_state'],np.zeros(6)];ys=y.copy();ctl={k:(complex(*v) if k in ['zi','applied','queued'] else v) for k,v in cp['controller'].items()};Ts=D['control_sample_s'];req={'P_req_W':800000.,'Q_req_var':700000.};t0=.6;end=2.75005;WL0=.75*(D['filter_L_H']+D['grid_L_H'])*(y[0]**2+y[1]**2)
 def level(tt):return .4 if ev and .60005<=tt<.75005 else 1.
 def fun(tt,yy,vv):
  sg=signals(tt,yy,ctl,D,vv);s=sg[5];return np.r_[rhs(tt,yy,ctl,D,vv),s.real,s.imag,yy[3],battery_draw(yy[3],D),abs(s.real-800000.),abs(s.imag-700000.)]
 def measure(tt,yy,vv):
  i,vdc,u,v,pi,s,ps=signals(tt,yy,ctl,D,vv);wl=.75*(D['filter_L_H']+D['grid_L_H'])*abs(i)**2;er=yy[4]-ys[4]+yy[2]-ys[2]+wl-WL0+yy[5]-ys[5]+yy[6]-ys[6]
  return np.array([tt,*yy,abs(i)/D['I_phase_peak_base_A'],vdc/1400,s.real,s.imag,abs(v)/D['V_phase_peak_base_V'],pi,ps,wl,er,.5+yy[4]/7.2e9,vv,ctl['omega']/(2*np.pi)])
 def ei(tt,yy):return (1.1*D['I_phase_peak_base_A'])**2-yy[0]**2-yy[1]**2
 def el(tt,yy):return yy[2]-.5*D['C_dc_F']*(.8*1400)**2
 def eh(tt,yy):return .5*D['C_dc_F']*(1.1*1400)**2-yy[2]
 def sl(tt,yy):return .5+yy[4]/7.2e9-.2
 def sh(tt,yy):return .8-(.5+yy[4]/7.2e9)
 def ic(tt,yy):return D['I_phase_peak_base_A']**2-yy[0]**2-yy[1]**2
 for e in [ei,el,eh,sl,sh]:e.terminal=True;e.direction=-1
 ic.terminal=False;ic.direction=-1
 ep=[measure(t0,y,1.)];st=[[t0,*normstate(t0,y,ctl,D)]];dense=[];ct=[];iv=[];cross=[];onsets={};reason='completed';first_seen={}
 for k in range(round(t0/Ts),int(np.ceil(end/Ts))):
  tt=k*Ts;te=min((k+1)*Ts,end);sg=signals(tt,y,ctl,D,level(tt));vmax=max(abs(sg[3]),.1*D['V_phase_peak_base_V']);ra=800000/(1.5*vmax);rb=700000/(1.5*vmax)
  cc=controller(tt,y,ctl,D,req,level(tt),c['allocator']);flags=[abs(cc[5]-ra)>1e-7 or abs(cc[6]-rb)>1e-7,cc[2]<1-1e-10,abs(cc[4])>=1e6*(1-1e-12),abs(cc[3]-45)<1e-9 or abs(cc[3]-75)<1e-9];ct.append([*cc,*map(float,flags)])
  cuts=sorted(set([tt,te]+[z for z in [.60005,.75005] if tt+1e-14<z<te-1e-14]));local=[];stop=False
  for aa,bb in zip(cuts[:-1],cuts[1:]):
   vv=level((aa+bb)/2);local.append(measure(aa,y,vv))
   sol=solve_ivp(lambda t,z:fun(t,z,vv),(aa,bb),y,method='DOP853',rtol=1e-10,atol=1e-8,max_step=h,events=[ei,el,eh,sl,sh,ic])
   local.extend(measure(t,z,vv) for t,z in zip(sol.t[1:],sol.y.T[1:]));y=sol.y[:,-1];cross.extend(sol.t_events[5].tolist())
   if abs(bb-.60005)<1e-12 or abs(bb-.75005)<1e-12:onsets[f'{bb:.5f}']={'time_s':bb,'plant_state':y.tolist(),'WL_J':.75*(D['filter_L_H']+D['grid_L_H'])*(y[0]**2+y[1]**2),'controller':serial_ctl(ctl),'note':'Physical state at exact external-event boundary; controller phase still corresponds to interval start until held-frequency advancement.'}
   if sol.status==1:reason=['current_emergency','dc_low','dc_high','soc_low','soc_high'][next(j for j in range(5) if len(sol.t_events[j]))];stop=True;break
   if not sol.success:reason='solver_failure';stop=True;break
  a=np.array(local);actual=float(sol.t[-1]);mxS=max(np.hypot(a[:,16],a[:,17]));mxP=max(abs(a[:,16]));iv.append([tt,actual,max(a[:,14]),min(a[:,15]),max(a[:,15]),mxS,mxP,max(abs(a[:,4])),min(a[:,23]),max(a[:,23]),max(abs(a[:,25]-60)),max(abs(a[:,22])),*map(float,flags)])
  screens={'actual_current':a[:,14]>1+1e-8,'dc_low':a[:,15]<.8-1e-8,'dc_high':a[:,15]>1.1+1e-8,'AC_S':np.hypot(a[:,16],a[:,17])>1.2e6*(1+1e-8),'AC_P':abs(a[:,16])>950000*(1+1e-8),'Pb':abs(a[:,4])>1e6*(1+1e-8),'SoC_low':a[:,23]<.2-1e-8,'SoC_high':a[:,23]>.8+1e-8}
  for key,mask in screens.items():
   if key not in first_seen and np.any(mask):first_seen[key]=float(a[np.flatnonzero(mask)[0],0])
  near=(max(a[:,14])>=.999 or min(a[:,15])<=.801 or max(a[:,15])>=1.099 or mxS>=.999*1.2e6 or mxP>=.999*950000)
  if ev and (tt<=.80005 or near):dense.extend(local)
  ctl['theta']+=ctl['omega']*(actual-tt);ep.append(measure(actual,y,level(np.nextafter(actual,-np.inf))));st.append([actual,*normstate(actual,y,ctl,D)])
  if stop:break
 ep=np.array(ep);st=np.array(st);iv=np.array(iv);ct=np.array(ct);left=ep[0]
 metrics=dict(I_peak_pu=float(max(max(iv[:,2]),left[14])),Vdc_min_pu=float(min(min(iv[:,3]),left[15])),Vdc_max_pu=float(max(max(iv[:,4]),left[15])),S_peak_VA=float(max(max(iv[:,5]),np.hypot(left[16],left[17]))),P_abs_peak_W=float(max(max(iv[:,6]),abs(left[16]))),Pb_abs_peak_W=float(max(max(iv[:,7]),abs(left[4]))),soc_min=float(min(iv[:,8])),soc_max=float(max(iv[:,9])),energy_residual_max_J=float(max(iv[:,11])),modulation_max=float(max(max(ct[:,7]),max(np.hypot(st[:,9],st[:,10])),max(np.hypot(st[:,11],st[:,12])))),reference_I_peak_pu=float(max(ct[:,1])))
 safe=not first_seen and metrics['modulation_max']<=.95/np.sqrt(3)*(1+1e-8)
 q=dict(case=cid,evidence='new_fixed_standard_allocation_diagnostic',allocator=c['allocator'],port=c['port'],allocator_source_sha256=hashlib.sha256((R/'baseline_allocation/allocators.py').read_bytes()).hexdigest(),topology_scope='Synthetic controlled DC port, not a validated DC/DC loop and not a directly connected battery',counterfactual='Same full initial state; standard allocation change and separately declared synthetic port speed',protocol_sha256=hashlib.sha256(P.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_tau_s=D['battery_source_tau_s'],source_ramp_W_per_s=D['battery_source_ramp_up_W_per_s'],h_s=h,initial_time_s=t0,final_time_s=float(ep[-1,0]),stop_reason=reason,no_numerical_hard_violation_up_to_stop=bool(safe),complete_hard_safe=bool(safe and reason=='completed'),current_continuous_crossings_s=cross,first_observed_beyond_roundoff=first_seen,terminal_contact={reason:float(ep[-1,0])} if reason!='completed' else {},metrics=metrics,event_boundary_states=onsets,final_plant_state=y.tolist(),final_controller=serial_ctl(ctl),wall_time_s=time.monotonic()-start,storage='100us endpoints/full state/controls/interval extrema; dense fault-onset through50ms after clearance and near-hard-boundary intervals; no ordinary full dense duplicate')
 tag=f'{cid}_h{h:g}';(OUT/f'{tag}.json').write_text(json.dumps(q,indent=2)+'\n');np.savez_compressed(OUT/f'{tag}.npz',endpoint_trace=ep,normalized_state=st,control=ct,interval_extrema=iv,dense_trace=np.array(dense),endpoint_columns=np.array(COLS),control_columns=np.array(['t','Irefpu','voltage_sat_factor','PLL_Hz','Pb_cmd','ip_ref','iq_ref','mnorm','current_ref_clipped','voltage_clipped','source_cmd_clipped','PLL_clipped']),interval_columns=np.array(['start','end','Imax','Vdcmin','Vdcmax','Smax','P_absmax','Pb_absmax','socmin','socmax','frequency_error_max','energy_residual_max','current_ref_clip','voltage_clip','source_cmd_clip','PLL_clip']))
 print(json.dumps(q,indent=2),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--h',type=float,default=1e-5);a=p.parse_args();run(a.case,a.h)
