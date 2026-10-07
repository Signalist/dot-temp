from g6_model import *
import pandas as pd
import json,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]
def verify(cfg):
 m=Model(cfg);name=cfg['name'];cases=json.loads((ROOT/'raw'/f'{name}_challenge_cases.json').read_text());df=pd.read_csv(ROOT/'results'/f'{name}_challenge_trials.csv').set_index('id');seen=[];max_error=0.;load_error=0.;files=[]
 for p in sorted((ROOT/'raw').glob(f'{name}_traces_*.npz')):
  z=np.load(p);x=z['x'];tt=z['t'];ids=z['case_ids'];assert x.dtype==np.float64;assert x.shape==(4501,len(ids),2*m.n);assert np.isfinite(x).all();seen+=ids.tolist()
  for local,i in enumerate(ids):
   c=cases[i];xx=x[:,local];outs=[np.max(abs(xx[:,m.n:])/.05)]
   for u,v,k in m.edges:outs.append(float(np.max(abs(c['kappa']*k*np.sin(xx[:,u]-xx[:,v]))/15)))
   mx=max(outs);err=abs(mx-df.loc[i,'peak_ratio']);max_error=max(max_error,err);assert err<1e-12
   f=np.array(c['fs']);drift=np.array(c.get('drift_amplitudes',[0,0]));phase=np.array(c['phases']);off=np.array(c.get('harmonic_offsets',np.zeros((2,3))))
   th=2*np.pi*tt[:,None]*f[None,:]+phase[None,:]+drift[None,:]*35*(1-np.cos(2*np.pi*tt[:,None]/35))
   pp=np.array(c['amps'])[None,:]*np.sum(np.sin(th[:,:,None]*m.hs[None,None,:]+off[None,:,:])/m.hs[None,None,:],axis=2)
   ee=float(np.max(abs(pp-z['pcc_P_MW'][:,local])));load_error=max(load_error,ee);assert ee<1e-8
  files.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 assert sorted(seen)==list(range(len(cases)));assert len(set(seen))==len(cases)
 r={'model':name,'case_count':len(cases),'base_paired_scenarios':40,'base_method_runs':160,'contract_break_variants':36,'complete_case_coverage':True,'peak_recompute_max_error':max_error,'pcc_recompute_max_error_MW':load_error,'files':files}
 (ROOT/'results'/f'{name}_raw_replay.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='files'}),flush=True)
if __name__=='__main__':
 for cfg in MODELS:
  if len(sys.argv)>1 and cfg['name'] not in sys.argv[1:]:continue
  verify(cfg)
