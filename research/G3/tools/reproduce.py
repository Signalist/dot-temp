#!/usr/bin/env python3
"""Run the preserved G3 research in a new copy; never alter frozen evidence."""
from pathlib import Path
import argparse,json,os,shutil,subprocess,sys,time,importlib.metadata,hashlib
sys.dont_write_bytecode=True
from verify_handoff import verify
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--mode',choices=['exact','full'],default='exact')
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();out=a.output.resolve()
if out.exists() or out==ROOT or ROOT in out.parents:p.error('Output must be new and outside the handoff')
count=verify();out.mkdir(parents=True);work=out/'round3';shutil.copytree(ROOT/'evidence/round3',work)
commands=['review/check_exact_zoh_certificate.py','review/check_profile_rationals.py','review/check_interval_export.py','src/verify_package.py']
if a.mode=='full':commands=['src/zoh_inner.py','src/certify_zoh_inner.py','src/certify_matched_baseline.py','src/certify_prefix_interval.py','src/account_and_ablate.py','src/check_lag_counterexample.py','review/independent_coupled_numeric.py','review/check_interval_export.py','review/check_zoh_inner.py','review/check_exact_zoh_certificate.py','review/check_profile_rationals.py','src/make_figures.py','src/verify_package.py']
versions={}
for name in ['numpy','scipy','cvxpy','clarabel','mpmath','matplotlib']:
 try:versions[name]=importlib.metadata.version(name)
 except importlib.metadata.PackageNotFoundError:versions[name]=None
res={'mode':a.mode,'python':sys.version.split()[0],'packages':versions,'files_verified_before':count,'stages':[],'note':'Exact certificates and source assertions are checked; full optimizer coordinates need not be byte-identical. No hardware claim.'}
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','MPLCONFIGDIR':str(out/'mpl'),'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
for i,cmd in enumerate(commands):
 log=out/f'{i+1:02d}_{Path(cmd).stem}.log';t=time.monotonic()
 with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(work/cmd)],cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT)
 res['stages'].append({'script':cmd,'exit_code':r.returncode,'seconds':round(time.monotonic()-t,3),'log':log.name,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
 res['all_passed']=all(x['exit_code']==0 for x in res['stages']);(out/'REPLAY_RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(cmd+': '+str(r.returncode),flush=True)
 if r.returncode:raise SystemExit(r.returncode)
res['files_verified_after']=verify();(out/'REPLAY_RESULT.json').write_text(json.dumps(res,indent=2)+'\n')
