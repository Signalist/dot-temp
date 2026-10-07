#!/usr/bin/env python3
"""Copy-on-run G6 scientific source replay. No network/download or simulator by default."""
from pathlib import Path
import argparse,json,os,shutil,subprocess,sys,time,importlib.metadata
from verify import verify_manifest
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--mode',choices=['verify','quick','synthetic','network','round2'],default='verify')
p.add_argument('--work-dir',type=Path)
a=p.parse_args();integrity=verify_manifest()
if a.mode=='verify':print(json.dumps(integrity,indent=2));raise SystemExit
if a.work_dir is None:p.error('--work-dir is required')
w=a.work_dir.resolve()
if w.exists():p.error('Refusing existing work directory')
if w==ROOT or ROOT in w.parents:p.error('Use a work directory outside the handoff')
w.mkdir(parents=True);shutil.copytree(ROOT/'evidence',w/'evidence');(w/'logs').mkdir()
r3=w/'evidence/round3_g6_20261004';r2=w/'evidence/round2_g6_joint_admission_20261003'
if a.mode=='quick':
 cmds=[(ROOT/'tests/test_window_dp.py',[]),(w/'evidence/round1/src/test_g6.py',[]),(r2/'theory_review/check_theory.py',[]),(r3/'src/run_orientation_and_jobs.py',[])]
elif a.mode=='synthetic':cmds=[(r3/'src/run_finite_uncertainty.py',[]),(r3/'src/run_orientation_and_jobs.py',[])]
elif a.mode=='network':cmds=[(r3/'src/reproduce_network_contracts.py',['--scratch',str(w/'network')])]
else:cmds=[(r2/s,[]) for s in ['src/run_structural.py','src/run_dynamic_optional.py','src/run_shared_parameter.py','src/run_face_budget.py','theory_review/check_theory.py','audit/independent_checks.py','stochastic/verify_stochastic.py']]
env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='2',MPLCONFIGDIR=str(w/'mpl'),XDG_CACHE_HOME=str(w/'cache'))
record={'mode':a.mode,'python':sys.version.split()[0],'versions':{n:importlib.metadata.version(n) for n in ['numpy','scipy','mpmath','matplotlib']},'checks':[],'scope':'Reexecutes specified scientific source; quick is partial, network conditional floating LTI only; no new nonlinear integration'}
for i,(script,args) in enumerate(cmds):
 t=time.perf_counter()
 with (w/'logs'/f'{i:02d}_{script.stem}.log').open('w') as log:r=subprocess.run([sys.executable,str(script),*args],cwd=w,env=env,stdout=log,stderr=subprocess.STDOUT)
 record['checks'].append({'script':str(script.relative_to(w)) if w in script.parents else 'tests/'+script.name,'returncode':r.returncode,'seconds':time.perf_counter()-t})
 print(json.dumps(record['checks'][-1]),flush=True)
 if r.returncode:break
record['all_passed']=len(record['checks'])==len(cmds) and all(x['returncode']==0 for x in record['checks'])
if record['all_passed'] and a.mode in ['quick','synthetic']:
 files=['ORIENTATION_CROSSOVER.json','JOB_DAG_REALIZATION.json','orientation_crossover.csv']
 if a.mode=='synthetic':files+=['EXACT_RATIONAL_PARAMETER_CERTIFICATE.json','EXACT_RATIONAL_GRID_RAW.json','finite_uncertainty.csv']
 comparison={f:(ROOT/'evidence/round3_g6_20261004/experiments'/f).read_bytes()==(r3/'experiments'/f).read_bytes() for f in files}
 record['archived_result_byte_comparison']=comparison
 record['all_passed']=all(comparison.values())
(w/'REPLAY_RESULT.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'all_passed':record['all_passed'],'report':'REPLAY_RESULT.json in requested work directory'}))
raise SystemExit(0 if record['all_passed'] else 1)
