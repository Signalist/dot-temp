"""Original G6 nonlinear stress replay at the unchanged qualified workpoint.
No model/source mutation; no downloaded code; exact carried-state ZOH witnesses.
"""
from pathlib import Path
import os,sys,json,hashlib,time,gc,shutil,logging
sys.dont_write_bytecode=True
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;TR=BASE/'transfer';PRIOR=BASE.parent/'round2_20261003/grid_transfer'
import numpy as np
QS=np.array([[1,1],[1,-1],[-1,-1],[-1,1]],float)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,o):Path(p).write_text(json.dumps(o,indent=2,allow_nan=False))
def array_sha(a):return hashlib.sha256(np.asarray(a,dtype=np.float64).tobytes()).hexdigest()
def schedules(word,amp):
 rows=[[0.,0.,0.,0.,0.]]
 for b,ports in enumerate(word[::-1]):
  for j,q in enumerate(QS):rows.append([1+2*b+.5*j,amp*ports[0]*q[0],0.,amp*ports[1]*q[1],0.])
 rows.append([1+2*len(word),0.,0.,0.,0.]);return np.asarray(rows)
def freeze():
 p=OUT/'NONLINEAR_FREEZE.json'
 if p.exists():return json.loads(p.read_text())
 conf={'frozen_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'operating_point':'Exact original public workpoint; original PQ load law preserved, supplemental ZIP port baselines zero; no increased P0','networks':{'kundur':[7,8],'wecc':[1,4]},'allocation':[.5,.5],'T_s':2.,'q_columns':QS.tolist(),'full_past_blocks':256,'trimmed_past_blocks':64,'start_s':1.,'ringdown_s':20.,'dt_s':[1/64,1/128],'event_epsilon_s':1e-4,'limit_Hz':.05,'selection':'All equal-split committed and dynamic-optional inner .98*capacity_lower, outer 1.02*capacity_upper; reset error .98*reset capacity_lower with committed violating word. No nonlinear-outcome selection.','input_order':'Stored word current block then most recent past to oldest; replay reverses order and never resets electrical state between blocks. Entire final block retained.','claim_scope':'Finite signed constant-P injection nonlinear stress replay only. Zero-baseline probes cannot themselves realize positive compute loads. Original native total selected-bus demand audited separately. No family-wide nonlinear certificate or compute calibration.','trim_scope':'Full257-block and trimmed65-block input arrays exported; nonlinear uses trimmed word. Modal bound controls only LTI tail difference at aligned times, not nonlinear history equivalence.','cases':[],'source_hashes':{}}
 for net in conf['networks']:
  for f in [TR/f'{net}_summary.json',TR/f'{net}_witnesses.npz',TR/f'{net}_kernel.npz',TR/f'{net}_bound_components.npz']:
   conf['source_hashes'][str(f)]=sha(f)
  w=np.load(TR/f'{net}_witnesses.npz');r=json.loads((TR/f'{net}_summary.json').read_text())['equal_split'];k=np.load(TR/f'{net}_kernel.npz');b=np.load(TR/f'{net}_bound_components.npz');la=k['lam'];R=k['R'];tail=np.max(np.einsum('omi,m->oi',abs(R*b['template_integral'][None,:,:]),np.exp(2*la.real*64)/(-np.expm1(2*la.real)))@np.array([.5,.5]))
  for contract,label,factor,key in [('committed','committed_inner',.98,'committed_capacity_lower_MW'),('committed','committed_outer',1.02,'committed_capacity_upper_MW'),('dynamic_optional','dynamic_optional_inner',.98,'dynamic_optional_capacity_lower_MW'),('dynamic_optional','dynamic_optional_outer',1.02,'dynamic_optional_capacity_upper_MW'),('committed','reset_inner_error',.98,'reset_capacity_lower_MW')]:
   amp=factor*r[key];full=w[contract+'_input_MW_per_total_MW'][20].copy();trim=full[:65].copy();fullsc=schedules(full,amp);sc=schedules(trim,amp);oi,pi,_=w[contract+'_argmax'][20];tau=float(w['phase_grid'][pi]);case={'network':net,'label':label,'contract':contract,'capacity_key':key,'capacity_MW':r[key],'factor':factor,'total_amplitude_MW':amp,'allocation_MW':[amp/2,amp/2],'full_word_sha256':array_sha(full),'trim_word_sha256':array_sha(trim),'actual_schedule_sha256':array_sha(sc),'full_schedule_sha256':array_sha(fullsc),'target_output_zero_based':int(oi),'target_phase_s':tau,'target_trim_time_s':129+tau,'target_full_time_s':513+tau,'full_LTI_target_Hz':amp*float(w[contract+'_output'][20]),'LTI_trim_vs_full_tail_upper_Hz':float(amp*tail),'contract_LTI_upper_Hz':amp*r[contract+'_peak_upper_Hz_per_MW'],'invalid_reset_predicted_upper_Hz':amp*r['reset_peak_upper_Hz_per_MW'] if label=='reset_inner_error' else None,'tf_s':151.}
   stem=f'{net}_{label}';np.savez_compressed(OUT/f'{stem}_input.npz',full_word_current_to_oldest=full,trim_word_current_to_oldest=trim,full_schedule=fullsc,actual_schedule=sc,q=QS,total_amplitude_MW=amp)
   np.savetxt(OUT/f'{stem}_actual_schedule.csv',sc,delimiter=',',header='time_s,P_bus0_MW,Q_bus0_Mvar,P_bus1_MW,Q_bus1_Mvar',comments='')
   conf['cases'].append(case)
 for f in [PRIOR/'grid_adapter.py',PRIOR/'PROVENANCE_LOCK.json',PRIOR/'chainrule_audit.json',PRIOR/'kundur_reduced51.npz',PRIOR/'wecc_verified_descriptor_K.npz',PRIOR/'wecc_descriptor_aux.npz']:
  conf['source_hashes'][str(f)]=sha(f)
 dump(p,conf);return conf

def exact_lti(lam,R,t,sc):
 """Analytic exponential ZOH integration, event splitting independent of NL grid."""
 state=np.zeros((len(lam),2),complex);freq=np.zeros((len(t),R.shape[0]));at=0.;idx=0;cache={}
 def advance(end,u):
  nonlocal state,at
  h=float(end-at)
  if h<=1e-13:at=end;return
  key=round(h,12)
  if key not in cache:cache[key]=(np.exp(lam*h),np.expm1(lam*h)/lam)
  e,b=cache[key];state=e[:,None]*state+b[:,None]*u[None,:];at=end
 for j,target in enumerate(t):
  while idx+1<len(sc) and sc[idx+1,0]<=target+1e-12:
   advance(sc[idx+1,0],sc[idx,[1,3]]);idx+=1
  advance(float(target),sc[idx,[1,3]]);freq[j]=np.einsum('omi,mi->o',R,state).real
 return freq

def runone(c,dt,ga):
 stem=f"{c['network']}_{c['label']}_dt{round(1/dt)}";jp=OUT/(stem+'.json')
 if jp.exists():
  old=json.loads(jp.read_text())
  if old.get('complete'):print('SKIP',stem,flush=True);return old
 start=time.perf_counter();print('START',stem,flush=True);conf=json.loads((OUT/'NONLINEAR_FREEZE.json').read_text());net=c['network'];ports=conf['networks'][net];inp=np.load(OUT/f"{net}_{c['label']}_input.npz");sc=inp['actual_schedule'];s=ga.build(net,buses=ports,dt=dt,tf=c['tf_s']);meta=dict(s._transfer_metadata)
 ref=OUT/f'{net}_initial_state.npz'
 if not ref.exists():np.savez_compressed(ref,x0=s._transfer_x0,y0=s._transfer_y0)
 prior=np.load(ref);initdiff=max(float(abs(s._transfer_x0-prior['x0']).max()),float(abs(s._transfer_y0-prior['y0']).max()))
 om=s.GENROU.omega.a.copy();bv=s.Bus.v.a.copy();genids=[str(i) for i in s.GENROU.idx.v]
 ga.install_schedule(s,sc,event_epsilon=conf['event_epsilon_s'])
 # Force observation of the pre-selected support phase, without changing input.
 target=c['target_trim_time_s'];s.switch_dict[target]={}
 from collections import OrderedDict
 s.switch_dict=OrderedDict(sorted(s.switch_dict.items()));s.switch_times=np.asarray(list(s.switch_dict));s.n_switches=len(s.switch_times)
 s.dae.store();ok=bool(s.TDS.run());t=s.dae.ts.t;freq=(s.dae.ts.x[:,om]-1)*s.config.freq;v=s.dae.ts.y[:,bv];u=np.stack([ga.schedule_value(sc,tt)[[0,2]] for tt in t]);k=np.load(TR/f'{net}_kernel.npz');lf=exact_lti(k['lam'],k['R'],t,sc)
 backgrounds=[];ledger=[]
 for j,bus in enumerate(ports):
  uid=s.Bus.idx2uid(bus);pq=s.PQ;ii=np.array([i for i,b in enumerate(pq.bus.v) if b==bus and not str(pq.idx.v[i]).startswith('TRANSFER_')],dtype=int);V=v[:,uid]
  con=np.sum(pq.ue.v[ii]*pq.config.p2p*pq.Ppf.v[ii])*s.config.mva;lin=np.sum(pq.ue.v[ii]*pq.config.p2i*pq.Ipeq.v[ii])*s.config.mva;quad=np.sum(pq.ue.v[ii]*pq.config.p2z*pq.Req.v[ii])*s.config.mva;bg=con+lin*V+quad*V*V;backgrounds.append(bg)
  ledger.append({'bus':bus,'supplemental_port_baseline_MW':0.,'native_original_P_MW':meta['local_original_P_MW'][j],'native_dynamic_load_min_MW':float(bg.min()),'probe_input_min_MW':float(u[:,j].min()),'probe_input_max_MW':float(u[:,j].max()),'total_native_plus_probe_min_MW':float((bg+u[:,j]).min()),'total_native_plus_probe_nonnegative':bool(np.min(bg+u[:,j])>=0),'positive_compute_probe_contract_embedded':False})
 ix=np.unravel_index(np.argmax(abs(freq)),freq.shape);il=np.unravel_index(np.argmax(abs(lf)),lf.shape);it=int(np.argmin(abs(t-target)));io=c['target_output_zero_based'];tail=t>=sc[-1,0];err=abs(freq-lf)
 result={'name':stem,'case':c,'dt_s':dt,'event_epsilon_s':conf['event_epsilon_s'],'complete':bool(ok and abs(float(t[-1])-c['tf_s'])<1e-8),'tds_return':ok,'busted':bool(s.TDS.busted),'error':s.TDS.err_msg,'metadata':meta,'initial_state_max_difference':initdiff,'initial_state_sha256':array_sha(np.r_[s._transfer_x0,s._transfer_y0]),'samples':len(t),'end_time_s':float(t[-1]),'actual_max_dt_s':float(np.diff(t).max()),'actual_input_sha256':array_sha(sc),'state_reset_between_blocks':False,'metrics':{'nonlinear_peak_any_generator_Hz':float(abs(freq[ix])),'nonlinear_peak_time_s':float(t[ix[0]]),'nonlinear_peak_generator':genids[ix[1]],'exact_LTI_peak_any_generator_Hz':float(abs(lf[il])),'exact_LTI_peak_time_s':float(t[il[0]]),'exact_LTI_peak_generator':genids[il[1]],'max_linear_nonlinear_error_Hz':float(err.max()),'rms_linear_nonlinear_error_Hz':float(np.sqrt(np.mean(err**2))),'nonlinear_target_Hz':float(freq[it,io]),'exact_LTI_target_Hz':float(lf[it,io]),'target_observation_time_error_s':float(abs(t[it]-target)),'full_vs_trimmed_LTI_target_error_Hz':float(abs(lf[it,io]-c['full_LTI_target_Hz'])),'tail_after_word_peak_Hz':float(abs(freq[tail]).max()),'minimum_bus_voltage_pu':float(v.min()),'maximum_bus_voltage_pu':float(v.max()),'nonlinear_frequency_margin_Hz':float(.05-abs(freq).max()),'LTI_frequency_margin_Hz':float(.05-abs(lf).max())},'physical_ledger':ledger,'elapsed_s':time.perf_counter()-start,'scope':'Finite signed-injection nonlinear stress replay at unchanged original workpoint. Native aggregate nonnegativity does not change zero probe baseline or establish positive compute/work realization.'}
 np.savez_compressed(OUT/(stem+'.npz'),t=t,frequency_Hz=freq,exact_LTI_frequency_Hz=lf,actual_input_MW=u,actual_schedule=sc,native_background_MW=np.stack(backgrounds,axis=1),total_native_plus_probe_MW=np.stack(backgrounds,axis=1)+u,bus_voltage_pu=v,generator_ids=np.array(genids),bus_ids=np.array(s.Bus.idx.v));dump(jp,result);print('DONE',stem,json.dumps(result['metrics']),flush=True);del s;gc.collect();return result

def main():
 conf=freeze()
 if '--freeze-only' in sys.argv:print(json.dumps(conf,indent=2));return
 nets=[a for a in sys.argv[1:] if a in conf['networks']] or list(conf['networks'])
 sys.path.insert(0,str(PRIOR));import grid_adapter as ga
 os.environ['HOME']=str(OUT/'home');os.environ['MPLCONFIGDIR']=str(OUT/'home/mpl');(OUT/'home').mkdir(exist_ok=True)
 if not (OUT/'home/.andes').exists():shutil.copytree(PRIOR/'home/.andes',OUT/'home/.andes')
 logging.basicConfig(level=logging.ERROR)
 for net in nets:
  rows=[]
  for dt in conf['dt_s']:
   for c in conf['cases']:
    if c['network']==net:rows.append(runone(c,dt,ga));dump(OUT/f'{net}_RESULTS.json',rows)
  dump(OUT/f'{net}_SOURCE_INTEGRITY.json',{'all_unchanged':all(sha(p)==v for p,v in conf['source_hashes'].items()),'checks':{p:sha(p)==v for p,v in conf['source_hashes'].items()}})
if __name__=='__main__':main()
