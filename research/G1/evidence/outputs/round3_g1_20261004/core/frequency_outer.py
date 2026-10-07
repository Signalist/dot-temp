"""Adversarial common-history relaxation for bounded-noise sampled frequency feedback.
Noise n(phi,k)=Q(y_free(phi,t_k))-y_free(phi,t_k), |n|<=eta,
with common quantizer step2eta. Then measured y=Q(y_free)-y_control.
Shared complete quantized free-output histories imply indistinguishability by induction.
"""
from research_lp import *

def make_tree(phases,eta,sample=.1,delay=.05,H=5.,offset=.5):
 histories=[(int(h),) for h,r,_ in phases]; branches=[];ts=np.arange(0,H+.000001,sample)
 for k,st in enumerate(ts):
  if k:
   for j,(high,r,_) in enumerate(phases):
    f=float(free(np.array([st]),r,high)[0]);code=int(np.floor(f/(2*eta)+offset));histories[j]+= (code,)
  groups={}
  for j,key in enumerate(histories):groups.setdefault(key,[]).append(j)
  until=min(H,st+sample+delay)
  branches.extend((v,until) for v in groups.values() if len(v)>1)
 # Redundant ties safe but large; retain maximum end for every pair to representative.
 pairs={}
 for ids,until in branches:
  for j in ids[1:]:pairs[(ids[0],j)]=max(until,pairs.get((ids[0],j),0))
 return [([i,j],u) for (i,j),u in pairs.items()]

if __name__=='__main__':
 import argparse
 pa=argparse.ArgumentParser();pa.add_argument('--dt',type=float,default=.01);pa.add_argument('--dr',type=float,default=.25);args=pa.parse_args()
 phases=[(h,float(r),float(r)) for h in [True,False] for r in np.r_[1e-6,np.arange(args.dr,5.000001,args.dr)]];results=[]
 for eta in [.005,.02,.05,.1,.15,.19,.25]:
  br=make_tree(phases,eta)
  o=build_solve(f'freq_eta{eta:g}_dr{args.dr:g}_dt{args.dt:g}',phases,br,dt=args.dt)
  o.update(eta=eta,sample=.1,delay=.05,quantizer='floor(y_free/(2eta)+.5)',noise_contract='arbitrary bounded errors',initial_class=True)
  results.append(o);print(json.dumps(o),flush=True)
 (ROOT/'raw'/f'frequency_exploration_dr{args.dr:g}_dt{args.dt:g}.json').write_text(json.dumps(results,indent=2))
