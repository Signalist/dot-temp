from pathlib import Path
import json,hashlib,itertools
import numpy as np
R=Path(__file__).resolve().parent
PBASE=654498.72485653043

def read(tag,suffix=''):
 z=np.load(R/(tag+suffix+'.npz'));return {k:z[k] for k in z.files}
def periodic(a,end):
 t=a['t'];m=(t>end-.1-1e-10)&(t<=end+1e-10);target=t[m]-.02
 res={k:float(np.max(np.abs(a[k][m]-np.interp(target,t,a[k])))) for k in ['W','B','ia','ib','ic','b','jd','jq','zw','cp']}
 res['qualified']=res['W']<=.1 and res['B']<=.1 and max(res[k] for k in ['ia','ib','ic'])<=.2
 res['W_mean_error_J']=float(np.mean(a['W'][m])-21600);res['W_ripple_peak_to_peak_J']=float(np.ptp(a['W'][m]));res['W_cycle_mean_drift_J']=float(np.mean(a['W'][m][-200:])-np.mean(a['W'][m][:200]))
 return res

def snap(a,t):
 idx=np.argmin(abs(a['t']-t));assert abs(a['t'][idx]-t)<1e-9,(a['t'],t);return {k:float(v[idx]) for k,v in a.items()}
def costs(s,h,ss,hs,start,end):
 tt=s['t'];lo=np.r_[2,tt[:-1]];weights=np.maximum(0,np.minimum(tt,end)-np.maximum(lo,start));dp=s['Pmean']-h['Pmean'];db=s['Pmean']-PBASE
 a,b=snap(ss,start),snap(ss,end);ha,hb=snap(hs,start),snap(hs,end)
 dg=(b['grid_energy']-a['grid_energy'])-(hb['grid_energy']-ha['grid_energy']);dl=(b['loss_energy']-a['loss_energy'])-(hb['loss_energy']-ha['loss_energy']);dd=(b['load_energy']-a['load_energy'])-(hb['load_energy']-ha['load_energy']);dstored=sum((b[k]-a[k])-(hb[k]-ha[k]) for k in ['W','B','filter_energy'])
 return {'signed_incremental_grid_J':dg,'absolute_net_incremental_grid_J':abs(dg),'positive_incremental_grid_J':float(np.dot(weights,np.maximum(dp,0))),'absolute_integral_incremental_grid_J':float(np.dot(weights,np.abs(dp))),'signed_grid_vs_model_baseline_J':b['grid_energy']-a['grid_energy']-(end-start)*PBASE,'positive_grid_vs_model_baseline_J':float(np.dot(weights,np.maximum(db,0))),'absolute_integral_grid_vs_model_baseline_J':float(np.dot(weights,np.abs(db))),'signed_healthy_grid_vs_model_baseline_J':hb['grid_energy']-ha['grid_energy']-(end-start)*PBASE,'incremental_loss_J':dl,'net_after_copper_increment_vs_healthy_J':dg-dl,'net_after_copper_increment_vs_model_baseline_J':b['grid_energy']-a['grid_energy']-(b['loss_energy']-a['loss_energy'])-(end-start)*650000,'gross_healthy_grid_J':hb['grid_energy']-ha['grid_energy'],'gross_service_grid_J':b['grid_energy']-a['grid_energy'],'service_copper_loss_J':b['loss_energy']-a['loss_energy'],'healthy_copper_loss_J':hb['loss_energy']-ha['loss_energy'],'incremental_load_J':dd,'incremental_stored_energy_J':dstored,'incremental_energy_identity_residual_J':dstored-dg+dl+dd,'within_100J_net':bool(abs(dg)<=100)}

def assess(tag,tau,ramp,offset,dt):
 s,h=read(tag+'_s1'),read(tag+'_s0');sd,hd=read(tag+'_s1','_dense'),read(tag+'_s0','_dense');ss,hs=read(tag+'_s1','_snapshots'),read(tag+'_s0','_snapshots');bins=read(tag+'_s1','_bins');j=json.loads((R/(tag+'_s1.json')).read_text());onset=2+offset;end=onset+.2;deadline=end+.5;finish=deadline+.2
 assert np.array_equal(s['t'],h['t']);assert np.array_equal(sd['t'],hd['t']);assert len(sd['t'])>=99999
 diff={k:float(np.max(abs(sd[k]-hd[k]))) for k in ['W','B','ia','ib','ic','b','jd','jq','zw','cp','held','ub','da','db','dc','filter_energy']}
 terminal={};
 for label,t in [('onset',onset),('service_end',end),('deadline',deadline),('post_observation',finish)]:
  a,b=snap(ss,t),snap(hs,t);terminal[label]={'service':a,'healthy':b,'difference':{k:a[k]-b[k] for k in a}}
 physical={'Vmin':j['all']['Vmin']>=1080,'Vmax':j['all']['Vmax']<=1320,'Iphase':j['all']['Iphase']<=1500,'Ispace':j['all']['Ispace']<=1500,'Bmin':j['all']['Bmin']>=0,'Bmax':j['all']['Bmax']<=100000,'bpeak':j['all']['bpeak']<=450000+1e-6,'u':j['all']['u']<=450000+1e-6,'bdot':j['all']['bdot']<=ramp+1e-6,'PWM_admissible':j['all']['mod']<=1+1e-9}
 track={k:float(np.max(abs(bins[k+'mean']-bins[k+'cmdmean']))) for k in ['P','Q']}
 track['pass']=track['P']<=2000 and track['Q']<=10000
 m=(s['t']>onset)&(s['t']<=end+1e-12);track['PWM_Pmean_max_abs_error_W']=float(np.max(abs(s['Pmean'][m]-s['Pcmdmean'][m])));track['PWM_Qmean_max_abs_error_var']=float(np.max(abs(s['Qmean'][m]-s['Qcmdmean'][m])))
 recovery_cost=costs(s,h,ss,hs,end,deadline);post_cost=costs(s,h,ss,hs,deadline,finish);total_cost=costs(s,h,ss,hs,onset,finish);service_cost=costs(s,h,ss,hs,onset,end);pre_onset_cost=costs(s,h,ss,hs,2,onset);checkpoint_total_cost=costs(s,h,ss,hs,2,finish)
 m=(s['t']>end)&(s['t']<=deadline+1e-12);cpmax=float(np.max(abs(s['cp'][m]-h['cp'][m])));ubmax=float(np.max(abs(s['ub'][m])));recovery_cost['max_abs_incremental_cP_W']=cpmax;recovery_cost['max_abs_inventory_correction_W']=ubmax
 budget=cpmax<=5000+1e-9 and all(recovery_cost[k]<=1000+1e-9 for k in ['absolute_net_incremental_grid_J','positive_incremental_grid_J','absolute_integral_incremental_grid_J'])
 health_dense={'W_cycle_sample_mean_error_J':float(np.mean(hd['W'])-21600),'W_ripple_peak_to_peak_J':float(np.ptp(hd['W'])),'Vmin':float(np.sqrt(2*np.min(hd['W'])/.03)),'Vmax':float(np.sqrt(2*np.max(hd['W'])/.03))}
 recovery_pass=diff['W']<=2 and diff['B']<=2 and max(diff[k] for k in ['ia','ib','ic'])<=2
 warm=periodic(read('warmup_'+('h1' if dt==1e-6 else 'h05')),2);health=periodic(h,deadline)
 initial_same=all(ss[k][0]==hs[k][0] for k in ss);initial_cpfile='checkpoint_'+('h1' if dt==1e-6 else 'h05')+'.csv'
 preserved=np.all(np.equal(s['cp'][(s['t']>2)&(s['t']<=end+1e-12)],s['cp'][0])) and np.max(abs(s['ub'][(s['t']>2)&(s['t']<=end+1e-12)]))==0
 return {'tag':tag,'actual_tau_s':tau,'actual_ramp_W_per_s':ramp,'offset_s':offset,'dt_s':dt,'checkpoint_file':initial_cpfile,'checkpoint_sha256':hashlib.sha256((R/initial_cpfile).read_bytes()).hexdigest(),'identical_complete_initial_snapshot':initial_same,'held_service_cp_and_disabled_inventory_verified':bool(preserved),'warmup_health':warm,'final_healthy_periodicity':health,'final_healthy_dense_physical':health_dense,'physical_hard_bound_checks':physical,'physical_all_pass':all(physical.values()),'tracking':track,'last_100ms_dense_max_abs_differences':diff,'physical_recovery_pass':recovery_pass,'recovery_cost':recovery_cost,'budget_pass':budget,'service_cost':service_cost,'pre_onset_cost':pre_onset_cost,'checkpoint_total_cost':checkpoint_total_cost,'post_deadline_cost':post_cost,'whole_observation_cost':total_cost,'snapshots':terminal,'extrema':j,'energy_closure_quality_pass':bool(j['all']['closure']<=.1),'pass':bool(all(physical.values()) and track['pass'] and recovery_pass and budget and warm['qualified'] and health['qualified'] and initial_same and preserved)}

def main():
 results=[]
 for dt in [1e-6,.5e-6]:
  d='h1' if dt==1e-6 else 'h05';tag='nominal_'+d
  if (R/(tag+'_s1.npz')).exists():results.append(assess(tag,.005,30e6,0,dt))
 for tau,ramp,offset,dt in itertools.product([.004,.006],[25e6,35e6],[37e-6,73e-6],[1e-6,.5e-6]):
  d='h1' if dt==1e-6 else 'h05';tag=f'tau{tau*1000:.0f}_r{ramp/1e6:.0f}_o{offset*1e6:.0f}_{d}'
  if (R/(tag+'_s1.npz')).exists():results.append(assess(tag,tau,ramp,offset,dt))
 conv=[]
 for x in results:
  if x['dt_s']!=1e-6:continue
  ft=x['tag'][:-2]+'h05' if x['tag'].endswith('h1') else ''
  if not(R/(ft+'_s1.npz')).exists():continue
  a,b=read(x['tag']+'_s1'),read(ft+'_s1');fields=['W','B','b','ia','ib','ic','cp','Pmean','Qmean']
  conv.append({'coarse':x['tag'],'fine':ft,'max_abs_difference':{k:float(np.max(abs(a[k]-b[k]))) for k in fields},'terminal_difference':{k:float(a[k][-1]-b[k][-1]) for k in fields}})
 old=json.loads((R/'ORIGINAL_SHA256_BEFORE.json').read_text());changed=[f for f,h in old.items() if hashlib.sha256((R.parent/f).read_bytes()).hexdigest()!=h]
 summary={'authoritative_protocol':'PROTOCOL_V1A.json','cases':results,'convergence':conv,'original_files_checked':len(old),'original_files_changed':changed,'all_cases_pass':all(x['pass'] for x in results),'case_count':len(results)}
 (R/'SUMMARY_V1A.json').write_text(json.dumps(summary,indent=2)+'\n')
 for x in results:print(x['tag'],'PASS',x['pass'],'physical',x['physical_all_pass'],'tracking',x['tracking']['pass'],'recovery',x['physical_recovery_pass'],'budget',x['budget_pass'],'diffWB',x['last_100ms_dense_max_abs_differences']['W'],x['last_100ms_dense_max_abs_differences']['B'],'energy',x['recovery_cost']['signed_incremental_grid_J'],x['recovery_cost']['absolute_integral_incremental_grid_J'])
 print('changed originals',changed)
if __name__=='__main__':main()
