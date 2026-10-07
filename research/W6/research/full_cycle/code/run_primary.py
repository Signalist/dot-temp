from pathlib import Path
import json,time,sys,hashlib
import numpy as np
from cycle_model import *
from global_bellman import bellman
ROOT=Path(__file__).resolve().parents[1]
def save(name,data): (ROOT/'results'/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def main():
 rows=[]
 for beta in (.5,.8):
  for R in (.5,4.):
   for c in (.25,1.,4.):
    case=Case(beta,R,c);prev=None
    for N in (64,128):
     r=solve(case,N,initial=prev);prev=r['z'];rows.append(r);save('PRIMARY_MESHES.json',rows);print(beta,R,c,N,r['success'],r['finite_mesh_linearization_gap'],r['parts']['objective'],flush=True)
 baselines=[]
 for r in rows:
  if r['N']!=128:continue
  case=Case(**r['case']);target=target_baseline(case);target.pop('z')
  d=bellman(case,N=64,sub=2);d2=bellman(case,N=64,sub=4)
  baselines.append({'case':case.__dict__,'constant_target_with_recovery':target,'bellman_sub2':d,'bellman_sub4':d2,'convex_objective':r['parts']['objective']});save('BASELINES.json',baselines);print('DP',case,d2['objective'],r['parts']['objective'],flush=True)
 # A decomposition ablation: unrestricted DP can choose any nonnegative end power.
 ablations=[]
 for beta,R,c in [(.5,.5,1.),(.5,4.,.25),(.8,4.,1.)]:
  ca=Case(beta,R,c)
  ablations.append({'case':ca.__dict__,'unrestricted':bellman(ca,64,4,False,False),'recovery_only':bellman(ca,64,4,True,False),'both_caps':bellman(ca,64,4,True,True)})
  save('DOMINANCE_ABLATION.json',ablations)
 # Saved physical paths include zero-probability endpoint and near-equal-node segments.
 paths=[]
 for r in rows:
  if r['N']!=128:continue
  ca=Case(**r['case'])
  paths.append({'case':ca.__dict__,'paths':[reconstruct(ca,r['z'],w) for w in [1e-6,.01,.1,.25,.5,.75,.99,1.-1e-6,1.]]})
 save('PHYSICAL_PATHS.json',paths)
if __name__=='__main__':main()
