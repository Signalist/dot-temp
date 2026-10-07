"""Recompute stored observations and case bookkeeping; no new integration."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from g6_model import Model,MODELS
name=sys.argv[1];m=Model(next(c for c in MODELS if c['name']==name));cp=ROOT/'raw'/f'{name}_challenge_cases.json';cases=json.loads(cp.read_text());meta=json.loads((ROOT/'results'/f'{name}_challenge_metadata.json').read_text());trials=pd.read_csv(ROOT/'results'/f'{name}_challenge_trials.csv',float_precision='round_trip').set_index('id')
rec={'model':name,'case_count':len(cases),'case_hash_matches_metadata':hashlib.sha256(cp.read_bytes()).hexdigest()==meta['scenario_file_sha256'],'chunks':[],'all_finite':True,'all_peak_arrays_match':True,'max_peak_csv_discrepancy':0.,'max_saved_load_reconstruction_error':0.,'case_ids':[]}
for p in sorted((ROOT/'raw').glob(f'{name}_traces_[0-9]*.npz')):
 d=np.load(p);x=d['x'];t=d['t'];loads=d['pcc_P_MW'];ids=d['case_ids'];B=len(ids);kap=np.array([cases[i]['kappa'] for i in ids]);peaks=np.max(np.abs(x[:,:,m.n:])/.05,axis=(0,2))
 for a,b,k in m.edges:peaks=np.maximum(peaks,np.max(np.abs(kap[None,:]*k*np.sin(x[:,:,a]-x[:,:,b]))/15,axis=0))
 rec['all_finite'] &= bool(all(np.isfinite(d[k]).all() for k in d.files));rec['all_peak_arrays_match'] &= bool(np.array_equal(peaks,d['peak_ratio']));rec['max_peak_csv_discrepancy']=max(rec['max_peak_csv_discrepancy'],float(np.max(abs(peaks-trials.loc[ids,'peak_ratio'].to_numpy()))));rec['case_ids']+=ids.tolist()
 for it in [0,len(t)//3,2*len(t)//3,len(t)-1]:
  for local,i in enumerate(ids):
   c=cases[i];fs=np.array(c['fs']);ph=np.array(c['phases']);a=np.array(c['amps']);off=np.array(c.get('harmonic_offsets',np.zeros((2,3))));dr=np.array(c.get('drift_amplitudes',[0,0]));th=2*np.pi*fs*t[it]+ph+dr*35*(1-np.cos(2*np.pi*t[it]/35));pcalc=a*np.sum(np.sin(th[:,None]*m.hs[None,:]+off)/m.hs[None,:],axis=1);rec['max_saved_load_reconstruction_error']=max(rec['max_saved_load_reconstruction_error'],float(np.max(abs(pcalc-loads[it,local]))))
 rec['chunks'].append({'filename':p.name,'cases':B,'samples':len(t),'state_shape':list(x.shape),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
rec['exact_case_coverage']=sorted(rec['case_ids'])==list(range(len(cases)));del rec['case_ids']
rec['coarse_summary_violation_counts_match']=True
summary=pd.read_csv(ROOT/'results'/f'{name}_challenge_summary.csv',float_precision='round_trip')
for _,row in summary.iterrows():
 q=trials[(trials.method==row.method)&(trials.condition==row.condition)];rec['coarse_summary_violation_counts_match'] &= bool(len(q)==row.n and int((q.peak_ratio>1+1e-9).sum())==row.sampled_violations)
(ROOT/'review'/f'{name}_trace_artifact_audit.json').write_text(json.dumps(rec,indent=2));print(json.dumps({k:v for k,v in rec.items() if k!='chunks'},indent=2))
