"""Original complete257-block positive-compute ANDES nonlinear witness replays."""
from pathlib import Path
import sys,os,json,hashlib,time,logging,gc,importlib.util,csv
sys.dont_write_bytecode=True;os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
from grid_adapter import *
ROOT=Path(__file__).resolve().parent;QS=np.array([[1,1],[1,-1],[-1,-1],[-1,1.]])
helper=ROOT.parent/'nonlinear/run_g6_nonlinear.py';spec=importlib.util.spec_from_file_location('nl_original',helper);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
logging.basicConfig(level=logging.ERROR)
def save(p,o):Path(p).write_text(json.dumps(o,indent=2,allow_nan=False))
def sha(a):return hashlib.sha256(np.asarray(a,dtype=np.float64).tobytes()).hexdigest()
def freeze():
 p=ROOT/'POSITIVE_NONLINEAR_CASES.json'
 if p.exists():return json.loads(p.read_text())
 assert json.loads((ROOT/'QUALIFICATION.json').read_text())['qualification_pass']
 r=json.loads((ROOT/'positive_summary.json').read_text())['equal_split'];w=np.load(ROOT/'positive_witnesses.npz');cases=[]
 for contract in ['committed','dynamic_optional','independent_ports']:
  for side,factor,key in [('inner',.98,'lower'),('outer',1.02,'upper')]:
   nominal=factor*r[f'{contract}_capacity_{key}_MW'];amp=min(nominal,100.);cases.append({'label':f'{contract}_{side}','contract':contract,'side':side,'factor':factor,'nominal_total_amplitude_MW':nominal,'total_amplitude_MW':amp,'physical_cap_applied':nominal>100.,'claimed_outside_uncapped_test':side=='outer' and nominal<=100.,'source_capacity_key':f'{contract}_capacity_{key}_MW'})
 nominal=.98*r['reset_capacity_lower_MW'];amp=.98*min(r['reset_capacity_lower_MW'],100.);cases.append({'label':'reset_false_admission','contract':'committed','side':'reset','factor':.98,'nominal_total_amplitude_MW':nominal,'total_amplitude_MW':amp,'physical_cap_applied':r['reset_capacity_lower_MW']>100.,'claimed_outside_uncapped_test':False,'source_capacity_key':'reset_capacity_lower_MW'})
 for c in cases:
  contract=c['contract'];amp=c['total_amplitude_MW'];word=w[contract+'_input_MW_per_total_MW'][20].copy();sc=m.schedules(word,amp);oi,pi,_=w[contract+'_argmax'][20];c.update({'target_output_zero_based':int(oi),'target_phase_s':float(w['phase_grid'][pi]),'target_time_s':513+float(w['phase_grid'][pi]),'full_LTI_target_Hz':amp*float(w[contract+'_output'][20]),'proper_contract_upper_Hz':amp*r[contract+'_peak_upper_Hz_per_MW'],'reset_screen_upper_Hz':amp*r['reset_peak_upper_Hz_per_MW'] if c['side']=='reset' else None,'tf_s':535.,'baseline_MW':[50.,50.],'per_port_amplitude_MW':[amp/2,amp/2],'schedule_sha256':sha(sc),'word_sha256':sha(word),'actual_compute_min_MW':np.min(50+sc[:,[1,3]],axis=0).tolist(),'zero_block_integral_max_MWs':float(abs((amp*word[:,:,None]*QS.T[None,:,:]).sum(axis=2)*.5).max())});assert min(c['actual_compute_min_MW'])>=0 and c['zero_block_integral_max_MWs']==0
  np.savez_compressed(ROOT/f"{c['label']}_input.npz",word_current_to_oldest=word,schedule=sc,total_compute_MW=50+sc[:,[1,3]],q=QS,total_amplitude_MW=amp)
  np.savetxt(ROOT/f"{c['label']}_schedule.csv",np.c_[sc,50+sc[:,[1,3]]],delimiter=',',header='time_s,deltaP7_MW,deltaQ7_Mvar,deltaP8_MW,deltaQ8_Mvar,computeP7_MW,computeP8_MW',comments='')
 conf={'freeze_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'predeclared_rule_source':'POSITIVE_WORKPOINT_FREEZE.json','support_inputs_hashes':{x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in ['positive_summary.json','positive_witnesses.npz','positive_kernel.npz']},'cases':cases,'start_s':1.,'full_blocks':257,'ringdown_s':20.,'event_epsilon_s':1e-4,'primary_dt_s':1/128,'refine_dt_s':1/256,'refine_labels':['dynamic_optional_inner','dynamic_optional_outer','reset_false_admission'],'scope':'Finite nonlinear checks of selected full witness words at genuinely positive compute baselines, not whole-family safety. Explicit affine-work law only.'};save(p,conf);return conf

def run(c,dt,conf):
 label=f"{c['label']}_dt{round(1/dt)}";out=ROOT/(label+'.json')
 if out.exists():
  old=json.loads(out.read_text())
  if old.get('complete'):return old
 start=time.perf_counter();print('START',label,flush=True);sc=np.load(ROOT/f"{c['label']}_input.npz")['schedule'];assert sha(sc)==c['schedule_sha256'];s=build('kundur',buses=[7,8],dt=dt,tf=c['tf_s'],baseline_MW=[50,50],baseline_Mvar=[0,0]);meta=s._transfer_metadata;install_schedule(s,sc,event_epsilon=conf['event_epsilon_s']);target=c['target_time_s'];s.switch_dict[target]={};s.switch_dict=OrderedDict(sorted(s.switch_dict.items()));s.switch_times=np.asarray(list(s.switch_dict));s.n_switches=len(s.switch_times);om=s.GENROU.omega.a.copy();bv=s.Bus.v.a.copy();genids=[str(i) for i in s.GENROU.idx.v];s.dae.store();ok=bool(s.TDS.run());t=s.dae.ts.t;freq=(s.dae.ts.x[:,om]-1)*60;v=s.dae.ts.y[:,bv];u=np.stack([schedule_value(sc,tt)[[0,2]] for tt in t]);k=np.load(ROOT/'positive_kernel.npz');lf=m.exact_lti(k['lam'],k['R'],t,sc);actual=50+u;ix=np.unravel_index(np.argmax(abs(freq)),freq.shape);il=np.unravel_index(np.argmax(abs(lf)),lf.shape);it=int(np.argmin(abs(t-target)));io=c['target_output_zero_based'];tail=t>=sc[-1,0];err=freq-lf
 r={'label':label,'case':c,'dt_s':dt,'event_epsilon_s':conf['event_epsilon_s'],'complete':bool(ok and abs(float(t[-1])-c['tf_s'])<1e-8),'tds_return':ok,'busted':bool(s.TDS.busted),'err_msg':s.TDS.err_msg,'end_time_s':float(t[-1]),'samples':len(t),'initial_x_sha256':sha(s._transfer_x0),'initial_y_sha256':sha(s._transfer_y0),'metadata':meta,'no_state_reset':True,'actual_compute_min_MW':np.min(actual,axis=0).tolist(),'actual_compute_max_MW':np.max(actual,axis=0).tolist(),'actual_compute_nonnegative':bool(np.all(actual>=0)),'metrics':{'nonlinear_peak_Hz':float(abs(freq[ix])),'nonlinear_peak_time_s':float(t[ix[0]]),'nonlinear_peak_generator':genids[ix[1]],'exact_LTI_peak_Hz':float(abs(lf[il])),'exact_LTI_peak_time_s':float(t[il[0]]),'exact_LTI_peak_generator':genids[il[1]],'nonlinear_target_Hz':float(freq[it,io]),'exact_LTI_target_Hz':float(lf[it,io]),'analytic_witness_target_error_Hz':float(abs(lf[it,io]-c['full_LTI_target_Hz'])),'target_time_error_s':float(abs(t[it]-target)),'max_NL_LTI_difference_Hz':float(abs(err).max()),'rms_NL_LTI_difference_Hz':float(np.sqrt(np.mean(err**2))),'frequency_limit_margin_Hz':float(.05-abs(freq).max()),'ringdown_peak_Hz':float(abs(freq[tail]).max()),'min_bus_voltage_pu':float(v.min()),'max_bus_voltage_pu':float(v.max())},'elapsed_s':time.perf_counter()-start,'scope':'Full finite nonlinear witness replay, not whole-family proof. Positive compute contract only under explicitly assumed affine power-work law.'}
 np.savez_compressed(ROOT/(label+'.npz'),t=t,frequency_Hz=freq,exact_LTI_frequency_Hz=lf,bus_voltage_pu=v,deltaP_MW=u,total_compute_MW=actual,schedule=sc);save(out,r);print('DONE',label,json.dumps(r['metrics']),flush=True);del s;gc.collect();return r
if __name__=='__main__':
 conf=freeze()
 if '--freeze-only' not in sys.argv:
  mode=sys.argv[1] if len(sys.argv)>1 else 'primary';dt=conf['primary_dt_s'] if mode=='primary' else conf['refine_dt_s'];cases=conf['cases'] if mode=='primary' else [c for c in conf['cases'] if c['label'] in conf['refine_labels']];results=[]
  for c in cases:
   results.append(run(c,dt,conf));save(ROOT/f'POSITIVE_NONLINEAR_{mode.upper()}.json',results)
