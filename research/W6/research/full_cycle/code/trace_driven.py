from pathlib import Path
import csv,json,time
import numpy as np
from scipy.optimize import minimize_scalar
from cycle_model import Case,power_int
from atomic_bellman import dp,physical,segments
ROOT=Path(__file__).resolve().parents[1]
from atomic_target_baseline import global_target as constant_target

def run():
 raw=list(csv.DictReader(open(ROOT/'literature/data_candidate/empirical_output_length_pmf.csv')));work=np.array([int(x['generated_tokens'])/1000 for x in raw]);prob=np.array([float(x['probability']) for x in raw]);prob=prob/prob.sum();out=[]
 for ca in [Case(.5,4.,1.),Case(.8,.5,1.)]:
  row={'case':ca.__dict__,'requests':19366,'support_atoms':len(work),'work_normalization':'generated_tokens /1000; empirical observed support, not prospective guarantee','measured_service_curve':False,'refinements':[]}
  for n in (128,512,1024,2048):
   st=time.perf_counter();lo,_=dp(ca,work,prob,n,True);hi,z=dp(ca,work,prob,n,False)
   row['refinements'].append({'n':n,'lower':lo,'upper':hi,'relative_gap':(hi-lo)/hi,'seconds':time.perf_counter()-st,'z':z})
   (ROOT/'results/TRACE_DRIVEN_GLOBAL.json').write_text(json.dumps(out+[row],indent=2));print(ca,n,lo,hi,(hi-lo)/hi,flush=True)
  row['constant_target']=constant_target(ca,work,prob);row['physical']=physical(ca,work.tolist(),prob.tolist(),z)
  for path in row['physical']['paths']:path.pop('segments')
  row['shared_bridge_segments']=segments(ca,work,z)
  row['ledger_gap']=abs(row['physical']['mean_objective']-hi);out.append(row);(ROOT/'results/TRACE_DRIVEN_GLOBAL.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':run()
