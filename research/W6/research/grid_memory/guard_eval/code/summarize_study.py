from guard_study import *
import csv,datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140})
protocol=json.loads((ROOT/'PROTOCOL.json').read_text());configs=protocol['design']+protocol['confirmation'];rows=[json.loads((ROOT/f"raw/{c['id']}.json").read_text()) for c in configs];aligned=json.loads((ROOT/'raw/ALIGNED_RESULTS.json').read_text());assert len(aligned)==9
exe=json.loads((ROOT/'raw/EXECUTOR_RESULTS.json').read_text());assert len(exe)==72
amap={r['id']:r for r in aligned};table=[]
for row in rows:
 for lab,p in row['policies'].items():
  table.append({'id':row['id'],'split':row['split'],'controller':lab,'mesh':'frozen_uniform256','beta':row['config']['beta'],'R':row['config']['R'],'mode_Hz':row['config']['mode_Hz'],'pcap':p['pcap'],**p['parts'],'frequency_nominal_Hz':p['frequency_nominal']['peak_Hz'],'frequency_transfer_Hz':p['frequency_transfer_worst']['peak_Hz'],'peak_phase':p['frequency_nominal']['phase'],'worst_W':p['frequency_nominal']['W'],'gain_vs_target_percent':p.get('weighted_objective_gain_vs_target_percent'),'mesh_relative_change':p.get('mesh_128_256_relative_difference')})
 for lab,p in amap[row['id']]['policies'].items():
  table.append({'id':row['id'],'split':row['split'],'controller':lab,'mesh':'supplementary_knee_aligned256','beta':row['config']['beta'],'R':row['config']['R'],'mode_Hz':row['config']['mode_Hz'],'pcap':p['pcap'],**p['parts'],'frequency_nominal_Hz':p['frequency_nominal']['peak_Hz'],'frequency_transfer_Hz':p['frequency_transfer_worst']['peak_Hz'],'peak_phase':p['frequency_nominal']['phase'],'worst_W':p['frequency_nominal']['W'],'gain_vs_target_percent':p['gain_vs_global_target_percent'],'mesh_relative_change':p['refinement_relative_difference']})
with open(ROOT/'raw/POLICY_SUMMARY.csv','w') as f:
 writer=csv.DictWriter(f,fieldnames=list(table[0]));writer.writeheader();writer.writerows(table)
fields=['id','controller','execution','EOS_delay_s','expected_objective','expected_dynamic_energy','expected_powercycle_time','expected_true_service_time','worst_dense_EOS_peak_Hz','mean_useful_work','expected_wasted_potential_service','objective_excess_percent_vs_event_instant','objective_513_1025_relative_difference','pathwise_delay_excess_max','pure_delay_bound','bound_holds_float']
with open(ROOT/'raw/EXECUTOR_SUMMARY.csv','w') as f:
 writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows([{k:r.get(k) for k in fields} for r in exe])
# Independent floating QA, source immutability and physical feasibility.
qa={'source_unchanged':{},'protocol_hash_verified':hashlib.sha256((ROOT/'PROTOCOL.json').read_bytes()).hexdigest()==(ROOT/'PROTOCOL.sha256').read_text().split()[0],'case_count':len(rows),'aligned_case_count':len(aligned),'executor_case_count':len(exe),'failures':[]}
for p,h in protocol['source_sha256'].items():qa['source_unchanged'][p]=hashlib.sha256((Path(p) if Path(p).exists() else ORIGINAL/Path(p).name).read_bytes()).hexdigest()==h
for row in rows:
 for r in sum(row['solvers'].values(),[]):
  if not r['success']:qa['failures'].append({'id':row['id'],'type':'SLSQP_failure','message':r['message']})
 for label,p in row['policies'].items():
  if p['physical_max_abs_slew']>row['config']['R']+1e-9:qa['failures'].append({'id':row['id'],'type':'slew','policy':label})
  if p['actual_max_power']>p['pcap']+1e-10:qa['failures'].append({'id':row['id'],'type':'cap','policy':label})
for r in aligned:
 for rr in r['solvers'].values():
  for x in rr:
   if not x['success']:qa['failures'].append({'id':r['id'],'type':'aligned_solver_failure','message':x['message']})
for r in exe:
 if r.get('bound_holds_float') is False:qa['failures'].append({'id':r['id'],'type':'pure_delay_bound'})
 if r['work_accounting_max_error']>1e-10:qa['failures'].append({'id':r['id'],'type':'work_ledger'})
qa['max_original_bellman_quadrature_disagreement']=max(v['quadrature_disagreement'] for r in rows for l in r['bellman'].values() for v in l)
qa['max_aligned_refinement_relative_change']=max(p['refinement_relative_difference'] for r in aligned for p in r['policies'].values())
qa['max_uniform_refinement_relative_change']=max(p['mesh_128_256_relative_difference'] for r in rows for p in r['policies'].values() if 'mesh_128_256_relative_difference' in p)
qa['max_aligned_finite_mesh_gap']=max(v['finite_mesh_linearization_gap'] for r in aligned for rr in r['solvers'].values() for v in rr)
qa['max_executor_quadrature_relative_change']=max(r['objective_513_1025_relative_difference'] for r in exe)
qa['all_confirmations_counted']=len([r for r in rows if r['split']=='confirmation'])==8
qa['not_interval_certificate']=True
(ROOT/'raw/QA.json').write_text(json.dumps(qa,indent=2))
# Design policy and EOS robustness curves.
design=rows[0];fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
labels={'nominal_optimal':'Nominal guard, convex','nominal_target':'Nominal guard, target','robust_optimal':'Robust guard, convex','unguarded_optimal':'No guard diagnostic'}
colors=['#1675a9','#ef8d24','#25875b','#8d62b5']
for (lab,display),color in zip(labels.items(),colors):
 p=design['policies'][lab];path=np.loadtxt(ROOT/p['control_path'],delimiter=',',skiprows=1);axs[0].plot(path[:,0],path[:,2],label=display,color=color,lw=1.8)
 dat=np.load(ROOT/p['curve_path']);axs[1].plot(dat['W'],dat['nominal'],label=display,color=color,lw=1.8)
axs[0].set(xlabel='Completed work x',ylabel='Actual dynamic power p',title='Design profiles: same physical slew and cycle ledger')
axs[1].axhline(.05,color='#a92828',ls='--',lw=1,label='Study budget .05 Hz');axs[1].set(xlabel='EOS work W',ylabel='All-future peak |f| [Hz]',title='Continuous EOS grid + analytic infinite tail');axs[0].legend(fontsize=8);axs[1].legend(fontsize=8)
fig.savefig(ROOT/'plots/design_policy_and_eos.png');plt.close(fig)
# All fixed confirmation outcomes, with diagnostic only comparator.
conf=rows[1:];names=[f"β={r['config']['beta']}, R={r['config']['R']}, f={r['config']['mode_Hz']}" for r in conf];y=np.arange(8)
fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained')
for offset,lab,color,label in [(-.24,'unguarded_optimal','#999999','No guard diagnostic'),(0,'nominal_optimal','#1675a9','Nominal guard'),(.24,'robust_optimal','#25875b','Robust guard')]:
 axs[0].barh(y+offset,[r['policies'][lab]['frequency_transfer_worst']['peak_Hz'] for r in conf],height=.23,color=color,label=label)
axs[0].axvline(.05,color='#a92828',ls='--');axs[0].set(yticks=y,yticklabels=names,xlabel='Worst tested uncertain all-future peak [Hz]',title='Guard transfer is conservative');axs[0].legend(fontsize=8)
for offset,lab,color,label in [(-.15,'nominal_aligned_optimal','#1675a9','Nominal guard'),(.15,'robust_aligned_optimal','#25875b','Robust guard')]:
 axs[1].barh(y+offset,[amap[r['id']]['policies'][lab]['gain_vs_global_target_percent'] for r in conf],height=.28,color=color,label=label)
axs[1].set(yticks=y,yticklabels=names,xlabel='Weighted full-cycle cost gain vs same-cap target [%]',title='Supplementary knee-aligned gains are often tiny');axs[1].legend(fontsize=8)
fig.savefig(ROOT/'plots/confirmation_peaks_and_cost.png');plt.close(fig)
# An example whose true maximum lies after power return.
r=conf[0];pr=r['policies']['nominal_optimal'];dat=np.loadtxt(ROOT/pr['control_path'],delimiter=',',skiprows=1);pol=Policy(r['config']['beta'],r['config']['R'],dat[:,0],dat[:,1]);g=Grid(r['config']['mode_Hz'],r['config']['zeta']);ev=FrequencyEvaluator(pol,g);ww=pr['frequency_nominal']['W'];detail=ev.evaluate(ww,True);i=min(np.searchsorted(pol.x,ww,side='right')-1,len(pol.slope)-1);dt=pol.duration(i,ww);te=pol.t[i]+dt;pe=(pol.K*max(0,pol.z[i]+pol.slope[i]*(ww-pol.x[i])))**(1/pol.K);tr=te+pe/pol.R;end=g.value(g.value(ev.states[i],pol.slope[i],dt),-pol.R,pe/pol.R);tt=np.linspace(0,tr+3/g.mode,3000);ff=[];pp=[]
for t in tt:
 if t<=te:
  j=min(np.searchsorted(pol.t,t,side='right')-1,i);delta=t-pol.t[j];ff.append(g.value(ev.states[j],pol.slope[j],delta)[0]);pp.append(pol.p[j]+pol.slope[j]*delta)
 elif t<=tr:
  delta=t-te;ff.append(g.value(g.value(ev.states[i],pol.slope[i],dt),-pol.R,delta)[0]);pp.append(pe-pol.R*delta)
 else:ff.append(g.value(end,0.,t-tr)[0]);pp.append(0.)
fig,axs=plt.subplots(2,1,figsize=(9,5),sharex=True,layout='constrained');axs[0].plot(tt,pp,color='#1675a9');axs[0].set(ylabel='Actual dynamic p',title=f'Grid memory persists after power return: W={ww:.5f}')
axs[1].plot(tt,ff,color='#25875b');axs[1].scatter([detail['peak_time_s']],[-detail['peak_Hz'] if np.interp(detail['peak_time_s'],tt,ff)<0 else detail['peak_Hz']],color='#a92828',zorder=3,label='Analytic all-future maximum')
for ax in axs:
 ax.axvline(te,color='#777777',ls=':',label='True EOS' if ax==axs[0] else None);ax.axvline(tr,color='#a92828',ls='--',label='Power returns to zero' if ax==axs[0] else None)
axs[0].legend(fontsize=8);axs[1].legend(fontsize=8);axs[1].set(xlabel='Time [s]',ylabel='Frequency deviation f [Hz]');fig.savefig(ROOT/'plots/post_return_grid_memory.png');plt.close(fig)
np.savetxt(ROOT/'curves/post_return_grid_memory.csv',np.column_stack([tt,pp,ff]),delimiter=',',header='time,power,f_Hz',comments='')
# Executor delay effects separate from pure sampling effects.
fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
for lab,color in [('nominal_optimal','#1675a9'),('robust_optimal','#25875b')]:
 for mode,style in [('event','-'),('sampled','--')]:
  rr=[x for x in exe if x['id']=='design' and x['controller']==lab and x['execution']==mode];axs[0].plot([x['EOS_delay_s'] for x in rr],[x['objective_excess_percent_vs_event_instant'] for x in rr],style,marker='o',color=color,label=lab.replace('_optimal','')+' '+mode)
  axs[1].plot([x['EOS_delay_s'] for x in rr],[x['worst_dense_EOS_peak_Hz'] for x in rr],style,marker='o',color=color)
axs[0].set(xlabel='EOS observation delay [s]',ylabel='Expected cost excess [%]',title='Delay cost dominates .01 s sampling effect');axs[0].legend(fontsize=8);axs[1].set(xlabel='EOS observation delay [s]',ylabel='Worst dense-EOS all-future peak [Hz]',title='Hard amplitude guard survives executor delay');axs[1].axhline(.05,color='#a92828',ls=':');fig.savefig(ROOT/'plots/executor_delay_tradeoff.png');plt.close(fig)
# Concise machine summary for parent paper integration.
summary={'protocol_sha256':(ROOT/'PROTOCOL.sha256').read_text().split()[0],'amendment_sha256':(ROOT/'AMENDMENT_KNEE_ALIGNMENT.sha256').read_text().split()[0],'confirmation_nominal_guard_peak_range':[min(r['policies']['nominal_optimal']['frequency_nominal']['peak_Hz'] for r in conf),max(r['policies']['nominal_optimal']['frequency_nominal']['peak_Hz'] for r in conf)],'confirmation_nominal_guard_transfer_peak_range':[min(r['policies']['nominal_optimal']['frequency_transfer_worst']['peak_Hz'] for r in conf),max(r['policies']['nominal_optimal']['frequency_transfer_worst']['peak_Hz'] for r in conf)],'nominal_peak_after_return_count':sum(r['policies']['nominal_optimal']['frequency_nominal']['phase']=='zero_input_tail' for r in conf),'unguarded_nominal_violations':sum(r['policies']['unguarded_optimal']['frequency_nominal']['peak_Hz']>.05 for r in conf),'unguarded_uncertain_violations':sum(r['policies']['unguarded_optimal']['frequency_transfer_worst']['peak_Hz']>.05 for r in conf),'aligned_nominal_gain_range_percent':[min(amap[r['id']]['policies']['nominal_aligned_optimal']['gain_vs_global_target_percent'] for r in conf),max(amap[r['id']]['policies']['nominal_aligned_optimal']['gain_vs_global_target_percent'] for r in conf)],'aligned_robust_gain_range_percent':[min(amap[r['id']]['policies']['robust_aligned_optimal']['gain_vs_global_target_percent'] for r in conf),max(amap[r['id']]['policies']['robust_aligned_optimal']['gain_vs_global_target_percent'] for r in conf)],'executor_max_peak_Hz':max(r['worst_dense_EOS_peak_Hz'] for r in exe),'executor_delay_bounds_all_hold':all(r.get('bound_holds_float',True) for r in exe),'executor_sampling_only_cost_change_range_percent':[min(r['objective_excess_percent_vs_event_instant'] for r in exe if r['execution']=='sampled' and r['EOS_delay_s']==0),max(r['objective_excess_percent_vs_event_instant'] for r in exe if r['execution']=='sampled' and r['EOS_delay_s']==0)],'QA':qa}
(ROOT/'raw/STUDY_SUMMARY.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
