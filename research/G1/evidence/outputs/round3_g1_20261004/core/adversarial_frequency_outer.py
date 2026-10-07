"""Valid adversarial histories: greedily cluster free outputs within diameter 2 eta."""
from research_lp import *

def make_tree(phases,eta,sample=.1,delay=.05,H=5.):
 groups=[[j for j,p in enumerate(phases) if p[0]==h] for h in [True,False]];pairs={}; history=[]
 for k,st in enumerate(np.arange(0,H+.000001,sample)):
  new=[];f=[float(free(np.array([st]),p[1],p[0])[0]) for p in phases]
  for ids in groups:
   order=sorted(ids,key=lambda j:f[j]);chunk=[];base=0
   for j in order:
    if chunk and f[j]-base>2*eta+1e-14:new.append(chunk);chunk=[]
    if not chunk:base=f[j]
    chunk.append(j)
   if chunk:new.append(chunk)
  groups=new;until=min(H,st+sample+delay)
  for ids in groups:
   for j in ids[1:]:pairs[tuple(sorted((ids[0],j)))]=max(until,pairs.get(tuple(sorted((ids[0],j))),0))
  history.append(dict(t=float(st),groups=[dict(ids=ids,m=(min(f[j] for j in ids)+max(f[j] for j in ids))/2,max_noise=(max(f[j] for j in ids)-min(f[j] for j in ids))/2) for ids in groups]))
 return [([i,j],u) for (i,j),u in pairs.items()],history
if __name__=='__main__':
 import argparse
 pa=argparse.ArgumentParser();pa.add_argument('--dt',type=float,default=.01);pa.add_argument('--dr',type=float,default=.25);pa.add_argument('--etas',default='.02,.05,.1,.15,.19');a=pa.parse_args()
 ps=[(h,float(r),float(r)) for h in [True,False] for r in np.r_[1e-6,np.arange(a.dr,5.000001,a.dr)]];results=[]
 for eta in map(float,a.etas.split(',')):
  br,history=make_tree(ps,eta);name=f'adversarial_eta{eta:g}_dr{a.dr:g}_dt{a.dt:g}'
  o=build_solve(name,ps,br,dt=a.dt);o.update(eta=eta,sample=.1,delay=.05,max_constructed_noise=max(g['max_noise'] for h in history for g in h['groups']),phase_min=1e-6,phase_max=5.)
  (ROOT/'raw'/f'{name}_history.json').write_text(json.dumps(history));results.append(o);print(json.dumps(o),flush=True)
 (ROOT/'raw'/f'adversarial_summary_dt{a.dt:g}.json').write_text(json.dumps(results,indent=2))
