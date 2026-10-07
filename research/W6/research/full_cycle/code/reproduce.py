"""Portable verifier. --full additionally regenerates optimization experiments (~minutes).
Run from any cwd using an environment with numpy/scipy/mpmath/matplotlib.
"""
from pathlib import Path
import argparse,subprocess,sys,json,hashlib,os,time,csv
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');args=p.parse_args();start=time.perf_counter()
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',MPLCONFIGDIR='/tmp/w6_mpl_cache',XDG_CACHE_HOME='/tmp/w6_cache')
def run(rel):
 r=subprocess.run([sys.executable,str(ROOT/rel)],env=env,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(rel+'\n'+r.stdout+'\n'+r.stderr)
 return {'script':rel,'success':True,'stdout_last':r.stdout[-1200:]}
logs=[]
if args.full:
 for f in ['run_primary.py','continuous_dual.py','transfer_and_initial.py','check_initial_global.py','atomic_bellman.py','trace_driven.py','inward_feasible_paths.py','matched_cycle_frontier.py','summarize_and_plot.py']:logs.append(run('code/'+f))
for f in ['check_full_cycle_witnesses.py','independent_numerical_audit.py','audit_transfer_and_repairs.py','audit_final_baselines_trace.py','audit_safe_inner_paths.py']:
 logs.append(run('audit/'+f))
# Recompute optimization/global chains in addition to independent saved-path verification.
from cycle_model import Case,solve
from atomic_bellman import dp
primary=json.load(open(ROOT/'results/PRIMARY_MESHES.json'));old=next(r for r in primary if r['N']==64);fresh=solve(Case(**old['case']),64)
errs={'fresh_convex64_objective':abs(fresh['parts']['objective']-old['parts']['objective'])}
a=json.load(open(ROOT/'results/ATOMIC_GLOBAL_BOUNDS.json'))[0];c=Case(**a['case']);lo,_=dp(c,a['work'],a['probabilities'],128,True);hi,_=dp(c,a['work'],a['probabilities'],128,False)
errs['fresh_atomic128_lower']=abs(lo-a['refinements'][0]['lower']);errs['fresh_atomic128_upper']=abs(hi-a['refinements'][0]['upper'])
raw=list(csv.DictReader(open(ROOT/'literature/data_candidate/empirical_output_length_pmf.csv')));w=np.array([int(r['generated_tokens'])/1000 for r in raw]);pr=np.array([float(r['probability']) for r in raw]);pr/=pr.sum();t=json.load(open(ROOT/'results/TRACE_DRIVEN_GLOBAL.json'))[0];c=Case(**t['case']);lo,_=dp(c,w,pr,128,True);hi,_=dp(c,w,pr,128,False)
errs['fresh_trace623_atoms_lower128']=abs(lo-t['refinements'][0]['lower']);errs['fresh_trace623_atoms_upper128']=abs(hi-t['refinements'][0]['upper'])
passed=max(errs.values())<1e-9
out={'status':'PASS' if passed else 'FAIL','portable_root':str(ROOT),'full_regeneration':args.full,'elapsed_seconds':time.perf_counter()-start,'independent_audits':logs,'fresh_reoptimization_differences':errs,'tolerance':1e-9,'formal_outward_rounding':False}
(ROOT/'audit/PORTABLE_REPLAY.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if not passed:raise SystemExit(1)
