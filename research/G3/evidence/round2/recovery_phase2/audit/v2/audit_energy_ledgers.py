from pathlib import Path
import json,csv,numpy as np,math
A=Path(__file__).resolve().parent;R=A.parent.parent/'V2';J=json.loads((A/'INDEPENDENT_RESULTS.json').read_text())
def load(t,s=''):return dict(np.load(R/(t+s+'.npz')))
def at(z,t):
 i=np.argmin(abs(z['t']-t));assert abs(z['t'][i]-t)<1e-10
 return {k:float(v[i]) for k,v in z.items()}
def flows(a,b):
 d={k:b[k]-a[k] for k in ['W','B','filter_energy','grid_energy','loss_energy','load_energy','battery_energy','bridge_energy']}
 d['grid_after_copper']=d['grid_energy']-d['loss_energy'];d['full_conservation_residual']=d['W']+d['B']+d['filter_energy']-d['grid_energy']+d['loss_energy']+d['load_energy'];d['bridge_balance_residual']=d['W']-d['bridge_energy']+d['load_energy']-d['battery_energy'];d['inventory_balance_residual']=d['B']+d['battery_energy'];return d
rows=[];diag=[];warm=[]
for x in J['cases']:
 tag=x['tag'];onset=2+x['offset_s'];service_end=onset+.2;deadline=onset+.7;finish=onset+.9;s=load(tag+'_s1');h=load(tag+'_s0');ss=load(tag+'_s1','_snapshots');hs=load(tag+'_s0','_snapshots');sd=load(tag+'_s1','_dense');hd=load(tag+'_s0','_dense');zmax={}
 for w,lo,hi in [('recovery',service_end,deadline),('final',deadline-.1,deadline),('postdeadline',deadline,finish)]:
  m=(s['t']>=lo-1e-10)&(s['t']<=hi+1e-10);zmax[w+'_PWM_boundary_J']=float(np.max(abs(s['filter_energy'][m]-h['filter_energy'][m])))
 zmax['final_common_1us_J']=float(np.max(abs(sd['filter_energy']-hd['filter_energy'])))
 eformula=max(float(np.max(abs(v['filter_energy']-.00015*(v['ia']**2+v['ib']**2+v['ic']**2)))) for v in [s,h,sd,hd])
 normsum=np.sqrt((sd['ia']+hd['ia'])**2+(sd['ib']+hd['ib'])**2+(sd['ic']+hd['ic'])**2);normdiff=np.sqrt((sd['ia']-hd['ia'])**2+(sd['ib']-hd['ib'])**2+(sd['ic']-hd['ic'])**2)
 point_bound=.00015*normsum*normdiff;defect=float(np.max(abs(sd['filter_energy']-hd['filter_energy'])-point_bound))
 per={k:float(np.max(abs(hd[k][20000:]-hd[k][:-20000]))) for k in ['W','B','ia','ib','ic']}
 diag.append({'tag':tag,'Z_sampled_maxima':zmax,'Z_formula_max_error_J':eformula,'Cauchy_bound_max_defect_J':defect,'hard_limit_derived_bound_J':.0003*1500*2*math.sqrt(4.5),'healthy_dense_periodicity':per,'healthy_dense_periodic_pass':per['W']<=.1 and per['B']<=.1 and max(per[k] for k in ['ia','ib','ic'])<=.2,'healthy_dense_W_mean_offset_J':float(hd['W'].mean()-21600),'healthy_dense_W_ripple_J':float(np.ptp(hd['W']))})
 for window,ta,tb in [('preonset',2,onset),('service',onset,service_end),('recovery',service_end,deadline),('postdeadline',deadline,finish),('onset_through_observation',onset,finish),('checkpoint_through_observation',2,finish)]:
  fs=flows(at(ss,ta),at(ss,tb));fh=flows(at(hs,ta),at(hs,tb));row={'case':tag,'window':window,'start_s':ta,'end_s':tb}
  for k in fs:row['service_'+k+'_J']=fs[k];row['healthy_'+k+'_J']=fh[k];row['incremental_'+k+'_J']=fs[k]-fh[k]
  row['service_grid_minus_model_baseline_J']=fs['grid_energy']-654498.7248565304*(tb-ta);row['healthy_grid_minus_model_baseline_J']=fh['grid_energy']-654498.7248565304*(tb-ta);row['service_after_copper_minus_model_net_baseline_J']=fs['grid_after_copper']-650000*(tb-ta);row['healthy_after_copper_minus_model_net_baseline_J']=fh['grid_after_copper']-650000*(tb-ta);rows.append(row)
for dt in ['h1','h05']:
 s=load('warmup_'+dt,'_snapshots');v=flows(at(s,0),at(s,2));v['tag']='warmup_'+dt;v['grid_minus_model_baseline_J']=v['grid_energy']-2*654498.7248565304;warm.append(v)
with (A/'FULL_ENERGY_LEDGER.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
(A/'FILTER_ENERGY_AUDIT.json').write_text(json.dumps({'exact_identity':'d(W+B)/dt = Pgrid - copper_loss - load - dZ/dt, Z=(L/2)*sum(iabc^2)','analytic_terminal_bound_J':.0003*1500*2*math.sqrt(4.5),'bound_scope':'At any instant where all three current differences <=2A and each branch space-vector current<=1500A. Numerical traces establish these premises only at sampled times.','cases':diag,'warmup':warm},indent=2)+'\n')
print(json.dumps({'ledger_rows':len(rows),'Zmax':{k:max(d['Z_sampled_maxima'][k] for d in diag) for k in diag[0]['Z_sampled_maxima']},'max_Z_formula_error_J':max(d['Z_formula_max_error_J'] for d in diag),'max_bound_defect_J':max(d['Cauchy_bound_max_defect_J'] for d in diag),'all_healthy_dense_periodic':all(d['healthy_dense_periodic_pass'] for d in diag),'max_pair_conservation_residual_J':max(abs(d['incremental_full_conservation_residual_J']) for d in rows)},indent=2))
