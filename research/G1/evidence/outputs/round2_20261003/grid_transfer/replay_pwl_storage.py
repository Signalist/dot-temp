"""CLI: --it IT.csv --bess actual_p.csv --label frozen_label [--dt .0078125].
Inputs are canonical arrays time_s,P_MW,Q_Mvar; IT ZOH, actual BESS PWL.
Finite PCS physics and energy bookkeeping belong to the producing controller.
"""
from grid_adapter import *
import argparse,pandas as pd,logging
logging.basicConfig(level=logging.WARNING)
OUT=ROOT/'nonlinear_replay';OUT.mkdir(exist_ok=True)
def run(it_path,bess_path,label,bus=8,tf=101.,dt=1/128):
 it_path=pathlib.Path(it_path);bess_path=pathlib.Path(bess_path);it=pd.read_csv(it_path).to_numpy(float);be=pd.read_csv(bess_path).to_numpy(float);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();src={'it_csv_sha256':h(it_path),'bess_csv_sha256':h(bess_path),'it_csv':str(it_path),'bess_csv':str(bess_path)}
 dest=OUT/(label+'.json')
 if dest.exists():
  old=json.loads(dest.read_text())
  if all(old.get(k)==v for k,v in src.items()) and old.get('dt_max_s')==dt and old.get('end_time',0)>=tf-1e-8 and old.get('tds_return'):print('RESUME_SKIP '+label,flush=True);return old
  raise ValueError('Existing label differs or failed; use a distinct versioned label')
 s=build('kundur',buses=[bus],dt=dt,tf=tf);install_it_zoh_bess_pwl(s,it,be);ok=bool(s.TDS.run());o=extract(s);t=o['t'];m=t>=1-1e-9;f=o['frequency_deviation_Hz'];w=o['coi_weights'];v=o['bus_voltage_pu'];bv=np.column_stack([np.interp(t,be[:,0],be[:,i]) for i in range(1,be.shape[1])]);iv=np.array([schedule_value(it,tt) for tt in t]);net=iv-bv
 r={'label':label,**src,'bus':bus,'dt_max_s':dt,'tds_return':ok,'busted':bool(s.TDS.busted),'err_msg':s.TDS.err_msg,'end_time':float(s.dae.t),'observation_window_s':[1,tf],'window':{'peak_abs_any_generator_Hz':float(np.max(abs(f[m]))),'peak_abs_COI_Hz':float(np.max(abs(o['coi_frequency_deviation_Hz'][m]))),'frequency_weighted_squared_integral_Hz2s':float(np.trapezoid((f[m]**2)@w,t[m])),'min_bus_voltage_pu':float(np.min(v[m])),'max_bus_voltage_pu':float(np.max(v[m])),'max_abs_relative_delta_rad':float(np.max(abs(o['relative_delta_rad'][m])))},'research_threshold_exceedances_Hz':{str(b):bool(np.max(abs(f[m]))>b) for b in [.1,.2,.3]},'injection_interpolation':'IT right-continuous ZOH, realized BESS exact PWL, net_consumption=IT-BESS','scope':'Original nonlinear Kundur; actual BESS power imposed externally. PCS command feasibility/loss-aware energy checked separately by controller producer; this result is finite-horizon grid replay, not hard nonlinear certificate.'}
 m100=(t>=1-1e-9)&(t<=101+1e-9)
 r['first_100s']={'peak_abs_any_generator_Hz':float(np.max(abs(f[m100]))),'frequency_weighted_squared_integral_Hz2s':float(np.trapezoid((f[m100]**2)@w,t[m100]))}
 if tf>=201:
  ml=t>=tf-10-1e-9;flprev=np.column_stack([np.interp(t[ml]-10,t,f[:,i]) for i in range(f.shape[1])]);r['last_two_10s_cycles']={'time_s':[tf-20,tf-10,tf],'frequency_trace_max_difference_Hz':float(np.max(abs(f[ml]-flprev))),'last_cycle_peak_Hz':float(np.max(abs(f[ml])))}
 np.savez_compressed(OUT/(label+'.npz'),t=t,frequency_deviation_Hz=f,coi_frequency_deviation_Hz=o['coi_frequency_deviation_Hz'],bus_voltage_pu=v,relative_delta_rad=o['relative_delta_rad'],branch_P_from_MW=o['branch_P_from_MW'],it_input=iv,bess_actual_input=bv,net_input=net,it_schedule=it,bess_schedule=be,coi_weights=w);dest.write_text(json.dumps(r,indent=2));print(r,flush=True);return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--it',required=True);p.add_argument('--bess',required=True);p.add_argument('--label',required=True);p.add_argument('--bus',type=int,default=8);p.add_argument('--tf',type=float,default=101.);p.add_argument('--dt',type=float,default=1/128);a=p.parse_args();run(a.it,a.bess,a.label,a.bus,a.tf,a.dt)
