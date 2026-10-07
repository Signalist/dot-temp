"""One common no-disturbance reference for battery-energy accounting only.
This adds no new disturbance or controller candidate. Matching horizons are the
already frozen sag tests' actual stop/recovery times, never optimized horizons.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from scipy.integrate import solve_ivp
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'gate_a'))
from dq_bench import controller,rhs,signals
from dq_preconditioned import serial_ctl
D=json.loads((ROOT/'protocol/GATE_A_LOCKED_V2_1.json').read_text());OUT=ROOT/'gate_a_extension/results'
cpfile=ROOT/'gate_a/preconditioned_dq/h1e-05_checkpoint.json';cp=json.loads(cpfile.read_text());y=np.r_[cp['plant_state'],np.zeros(2)];ys=y.copy();ctl={k:(complex(*v) if k in ['zi','applied','queued'] else v) for k,v in cp['controller'].items()}
t0=cp['time_s'];Ts=D['control_sample_s'];req=dict(P_req_W=800000.,Q_req_var=700000.)
sags=[json.loads((OUT/f'{c}_h1e-05.json').read_text()) for c in ['sag085','sag075','sag0475']]
targets=sorted(set([s['final_time_s'] for s in sags]+[s['event_start_s'] for s in sags]));end=max(targets)
rows=[];matched={};WL0=.75*(D['filter_L_H']+D['grid_L_H'])*(y[0]**2+y[1]**2)
def record(t,yy):
 i,vdc,u,v,pi,sp,ps=signals(t,yy,ctl,D,1.);wl=.75*(D['filter_L_H']+D['grid_L_H'])*abs(i)**2
 er=yy[4]-ys[4]+yy[2]-ys[2]+wl-WL0+yy[5]-ys[5]+yy[6]-ys[6]
 return [t,*yy,abs(i)/D['I_phase_peak_base_A'],vdc/D['V_dc_initial_V'],sp.real,sp.imag,er]
def augmented_rhs(tt,yy):
 sg=signals(tt,yy,ctl,D,1.)
 return np.r_[rhs(tt,yy,ctl,D,1.),sg[5].real,sg[5].imag]
rows.append(record(t0,y));maxI=0.;maxErr=0.
for k in range(round(t0/Ts),int(np.ceil(end/Ts))):
 t=k*Ts;te=min((k+1)*Ts,end);controller(t,y,ctl,D,req,1.)
 cuts=sorted(set([t,te]+[z for z in targets if t+1e-14<z<te-1e-14]))
 for a,b in zip(cuts[:-1],cuts[1:]):
  sol=solve_ivp(augmented_rhs,(a,b),y,method='DOP853',rtol=1e-10,atol=1e-8,max_step=1e-5)
  assert sol.success
  for tt,yy in zip(sol.t,sol.y.T):
   rr=record(tt,yy);maxI=max(maxI,rr[10]);maxErr=max(maxErr,abs(rr[14]))
  y=sol.y[:,-1]
  for target in targets:
   if abs(b-target)<1e-12:matched[str(target)]={'time_s':target,'plant_state':y.tolist()}
 ctl['theta']+=ctl['omega']*(te-t);rows.append(record(te,y))
pairs=[]
for s in sags:
 t=s['final_time_s'];ref=matched[str(t)]['plant_state'];final=json.loads((OUT/f"{s['case']}_h1e-05_final_state.json").read_text())['plant_state'];diff=final[4]-ref[4]
 pairs.append(dict(case=s['case'],comparison_time_s=t,comparison_reason=s['stop_reason'],fault_battery_stored_energy_change_since_checkpoint_J=final[4]-ys[4],no_fault_battery_stored_energy_change_since_checkpoint_J=ref[4]-ys[4],fault_minus_reference_stored_energy_J=diff,extra_energy_debt_J=max(0.,-diff),energy_surplus_J=max(0.,diff),interpretation='Positive difference is retained energy / surplus, not energy recovery; it may accompany missed active service. Negative difference is extra battery energy debt. Neither is forced to zero by electrical-state recovery.',fault_minus_reference_remote_active_energy_J=final[5]-ref[5],fault_minus_reference_total_dissipation_J=final[6]-ref[6],fault_minus_reference_PCC_active_energy_J=final[7]-ref[7],fault_minus_reference_PCC_reactive_integral_var_s=final[8]-ref[8],fault_minus_reference_DC_energy_J=final[2]-ref[2],fault_minus_reference_inductor_energy_J=.75*(D['filter_L_H']+D['grid_L_H'])*(final[0]**2+final[1]**2-ref[0]**2-ref[1]**2)))
result=dict(status='new_paired_accounting_reference_v2_with_passive_PCC_quadratures',purpose='Shared no-fault reference for the same three prespecified sag conditions',checkpoint_sha256=hashlib.sha256(cpfile.read_bytes()).hexdigest(),initial_time_s=t0,final_time_s=end,control_sample_s=Ts,max_step_s=1e-5,max_actual_current_pu=maxI,max_energy_conservation_residual_J=maxErr,evaluation_states=matched,paired_battery_accounts=pairs)
(OUT/'matched_no_fault_reference_v2.json').write_text(json.dumps(result,indent=2)+'\n');np.savez_compressed(OUT/'matched_no_fault_reference_v2.npz',endpoint_trace=np.array(rows));print(json.dumps(result,indent=2))
