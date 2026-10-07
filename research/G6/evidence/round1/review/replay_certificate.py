"""Replay existing saved certificate, never recompute an optimization or modify it."""
from pathlib import Path
import sys, json, hashlib, time
import numpy as np
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import g6_model as g
name=sys.argv[1] if len(sys.argv)>1 else 'design4'
path=ROOT/'raw'/f'{name}_certificate.npz'; data=np.load(path)
boxes=data['boxes']; saved=data['leaf_upper'];lb=data['lower'];ub=data['upper'];witness=data['witness']
rec={'model':name,'artifact_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'model_source_sha256':hashlib.sha256((ROOT/'src/g6_model.py').read_bytes()).hexdigest(),'leaf_count':len(boxes),'finite_arrays':all(np.isfinite(data[k]).all() for k in data.files)}
meta=json.loads((ROOT/'results'/f'{name}_certificate.json').read_text())
rec['reported_tightness']={k:meta[k] for k in ['relative_tolerance','max_relative_gap','tolerance_met','evaluated_boxes','maxboxes']}
root=[float(g.down(.08)),float(g.up(.75)),float(g.down(.85)),float(g.up(1.15))]
events={}
for idx,(a,b,c,d) in enumerate(boxes):
 assert root[0]<=a<b<=root[1] and root[2]<=c<d<=root[3]
 events.setdefault(a,[]).append((1,idx,c,d));events.setdefault(b,[]).append((-1,idx,c,d))
active={};xs=sorted(events); assert xs[0]==root[0] and xs[-1]==root[1]
for z,x in enumerate(xs):
 for op,idx,c,d in events[x]:
  if op==1:active[idx]=(c,d)
  else:del active[idx]
 if z<len(xs)-1:
  end=root[2]
  for c,d in sorted(active.values()):assert c==end,(x,c,end);end=d
  assert end==root[3]
assert not active
rec['exact_binary_endpoint_partition_check']=True
rec['upper_equals_leaf_max']=bool(np.array_equal(saved.max(axis=0),ub))
m=g.Model(next(c for c in g.MODELS if c['name']==name));rec['witness_lower_match']=True;rec['witness_nominal_domain_feasible']=True
for ind in np.ndindex(lb.shape):
 f,k=witness[ind];rec['witness_nominal_domain_feasible'] &= bool(mp.mpf('0.08')<=mp.mpf(float(f))<=mp.mpf('0.75') and mp.mpf('0.85')<=mp.mpf(float(k))<=mp.mpf('1.15'))
 low,_=m.bounds([f,f,k,k]);rec['witness_lower_match'] &= bool(low[ind]==lb[ind])
start=time.time();rec['replay_upper_mismatch_count']=0;rec['max_replay_minus_saved']=0.
for idx,b in enumerate(boxes):
 _,u=m.bounds(b)
 if not np.array_equal(u,saved[idx]):rec['replay_upper_mismatch_count']+=1
 rec['max_replay_minus_saved']=max(rec['max_replay_minus_saved'],float(np.max(u-saved[idx])))
rec['replay_seconds']=time.time()-start
rec['source_changed_during_replay']=rec['model_source_sha256']!=hashlib.sha256((ROOT/'src/g6_model.py').read_bytes()).hexdigest()
(ROOT/'review'/f'{name}_certificate_replay.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec,indent=2))
