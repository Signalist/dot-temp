from pathlib import Path
import json,hashlib,subprocess,sys
import numpy as np
R=Path(__file__).resolve().parent
OLD=R.parent/'recovery_phase2'/'V2'

def run(tag,dt,tau,ramp,offset,branch):
 h='h1' if dt==1e-6 else 'h05';args=[str(R/'rectifier_load_match'),'case',str(R/'original_input.csv'),str(R/tag),str(dt),str(R/f'checkpoint_{h}.csv'),str(tau),str(ramp),str(offset),str(branch)]
 res=subprocess.run(args,check=True,text=True,capture_output=True);j=json.loads(res.stdout);j['command']=args;(R/(tag+'.json')).write_text(json.dumps(j,indent=2)+'\n')
 for suffix in ['','_dense','_snapshots','_bins']:
  path=R/(tag+suffix+'.csv');a=np.genfromtxt(path,delimiter=',',names=True);data={k:np.atleast_1d(a[k]) for k in a.dtype.names};np.savez_compressed(R/(tag+suffix+'.npz'),**data)
  if suffix=='_dense':
   b=np.load(R/(tag+suffix+'.npz'));assert all(np.array_equal(data[k],b[k]) for k in data);path.unlink()
 return j

def main():
 configs=json.loads((R/'PROTOCOL_PHASE3.json').read_text())['configurations'];identity=[]
 for c in configs[:2]:
  tag=c['tag'];j=run('replay_'+tag+'_S',c['dt_s'],c['tau_s'],c['ramp_W_per_s'],c['offset_s'],1);original=json.loads((OLD/(tag+'_s1.json')).read_text());metrics_equal={k:j[k]==original[k] for k in ['steps','clipped_cycles','all','service','recovery']}
  exact={suffix:(R/('replay_'+tag+'_S'+suffix)).read_bytes()==(OLD/(tag+'_s1'+suffix)).read_bytes() for suffix in ['.csv','_snapshots.csv','_bins.csv']}
  a=np.load(R/('replay_'+tag+'_S_dense.npz'));b=np.load(OLD/(tag+'_s1_dense.npz'));exact['dense_npz_arrays']=all(np.array_equal(a[k],b[k]) for k in a.files)
  row={'case':tag,'metrics_bitwise_equal':metrics_equal,'outputs_byte_or_array_bitwise_equal':exact,'pass':all(metrics_equal.values()) and all(exact.values())};identity.append(row)
  (R/'SERVICE_REPLAY_IDENTITY.json').write_text(json.dumps(identity,indent=2)+'\n');assert row['pass'],'Extended command mode changed old S dynamics; stop without changing frozen code'
 print('Both old nominal service cases reproduced exactly',flush=True)
 for c in configs:
  run(c['tag']+'_L',c['dt_s'],c['tau_s'],c['ramp_W_per_s'],c['offset_s'],2);print(c['tag'],flush=True)
if __name__=='__main__':main()
