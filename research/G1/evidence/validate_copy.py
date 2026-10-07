"""Review-only reruns of fixed witnesses in a fresh isolated copy.
No synthesis, freeze generation, nonlinear simulation, original-path audit execution,
or package dependency installation. Never edits the package or original source.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys,time,platform
import numpy as np,scipy,mpmath
from verify_package import main as verify
SOURCE=Path(__file__).resolve().parent
R3='outputs/round3_g1_20261004'
AUDIT='outputs/round3_g1_independent_audit_20261004'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fingerprint(p):
 s=p.stat();return dict(sha256=sha(p),bytes=s.st_size,mtime_ns=s.st_mtime_ns)
def without_volatile(x):
 if isinstance(x,dict):return {k:without_volatile(v) for k,v in x.items() if k not in ['seconds','audit_utc']}
 if isinstance(x,list):return [without_volatile(v) for v in x]
 return x
def read(p):return json.loads(Path(p).read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--work-dir',required=True);a=ap.parse_args()
 work=Path(a.work_dir).resolve()
 assert not work.exists(),'Use a fresh non-existing disposable directory'
 assert work!=SOURCE and SOURCE not in work.parents and work not in SOURCE.parents,'Copy must be outside extracted evidence bundle'
 integrity=verify();scope=read(SOURCE/'PACKAGE_SCOPE.json')
 original={r['path']:fingerprint(SOURCE/r['path']) for r in scope['included']}
 work.mkdir(parents=True);shutil.copytree(SOURCE/'outputs',work/'outputs')
 for row in scope['exact_hash_duplicate_restore_map']:
  target=work/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(work/row['restore_from'],target)
  assert sha(target)==row['sha256']
 (work/'DISPOSABLE_VALIDATION_COPY.txt').write_text('Only this copy may be modified by validation. The extracted evidence package remains unchanged.\n')
 logs=work/'validation_logs';logs.mkdir();home=work/'isolated_home';home.mkdir()
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',HOME=str(home),MPLCONFIGDIR=str(home/'mpl'))
 results=[]
 def run(name,relative,expect=0):
  started=time.monotonic();r=subprocess.run([sys.executable,str(work/relative)],cwd=work,env=env,capture_output=True,text=True)
  (logs/(name+'.stdout.log')).write_text(r.stdout);(logs/(name+'.stderr.log')).write_text(r.stderr)
  assert r.returncode==expect,(name,r.returncode,r.stderr[-4000:])
  row={'name':name,'command':[sys.executable,str(work/relative)],'returncode':r.returncode,'seconds':time.monotonic()-started};results.append(row);print(name+' completed',flush=True);return r
 def compare(relative):
  assert without_volatile(read(SOURCE/relative))==without_volatile(read(work/relative)),relative
 run('interval_lower',R3+'/core/interval_lower_certificate.py');compare(R3+'/raw/interval_lower_certificate.json')
 run('interval_upper',R3+'/core/interval_validate.py');compare(R3+'/raw/interval_summary.json')
 for p in (SOURCE/R3/'raw').glob('interval_*policy*.json'):compare(str(p.relative_to(SOURCE)))
 run('feedback_seven_tests',R3+'/feedback_baseline/test_feedback.py')
 run('network_exact_boundaries',R3+'/network_transfer/audit_exact_boundaries.py');compare(R3+'/network_transfer/BOUNDARY_CONTRACT_AUDIT.json')
 net=work/R3/'network_transfer';protected=set();all_cases=[]
 for name in ['CONFIRMATION_FREEZE.json','AMPLITUDE_STRESS_ADDENDUM_FREEZE.json']:
  manifest=net/name;protected.add(manifest);m=read(manifest);all_cases+=m['cases']
  for c in m['cases']:
   for k in ['it_csv','bess_csv','observations_csv']:
    p=net/'confirmation'/Path(c[k]).name;assert sha(p)==c[k.replace('_csv','_sha256')];protected.add(p)
   p=net/(c['controller']+'.npz');assert sha(p)==c['controller_sha256'];protected.add(p)
 before={str(p):fingerprint(p) for p in protected};inventory=sorted(str(p) for p in (net/'confirmation').glob('*'))
 r=run('freeze_expected_refusal',R3+'/network_transfer/freeze_confirmation.py',expect=1)
 assert 'refusing before input generation' in r.stderr
 after={str(p):fingerprint(p) for p in protected};assert before==after and inventory==sorted(str(p) for p in (net/'confirmation').glob('*'))
 assert len(protected)==78
 csv_rows=[]
 for c in all_cases:
  be=np.loadtxt(net/'confirmation'/Path(c['bess_csv']).name,delimiter=',',skiprows=1);dt=np.diff(be[:,0]);p=be[:,1];assert np.all(dt>0)
  area=.5*(p[:-1]+p[1:])*dt;debt=np.r_[0,np.cumsum(np.where(area>=0,area/.95,area*.95))];sl=np.diff(p)/dt;cmd=max(np.max(abs(p[:-1]+.05*sl)),np.max(abs(p[1:]+.05*sl)))
  assert cmd<=50+1e-9 and abs(debt[-1])<=1e-8
  csv_rows.append({'label':c['label'],'max_command_MW':float(cmd),'terminal_depletion_MWs':float(debt[-1])})
 saved=read(SOURCE/R3/'network_transfer/SERIALIZED_INPUT_NUMERICAL_AUDIT.json')
 assert max(r['max_command_MW'] for r in csv_rows)==saved['max_serialized_command_MW']
 assert max(abs(r['terminal_depletion_MWs']) for r in csv_rows)==saved['max_abs_serialized_terminal_depletion_MWs']
 traces=[]
 for p in sorted((net/'nonlinear_replay').glob('*.npz')):
  if p.stem.endswith('_linear'):continue
  d=np.load(p,allow_pickle=False);peak=float(np.max(abs(d['frequency_deviation_Hz'][d['t']>=1-1e-12])))
  saved=read(p.with_suffix('.json'));assert peak==saved['window']['peak_abs_any_generator_Hz']
  traces.append({'label':p.stem,'peak_Hz':peak,'within_0_1_Hz':peak<=.1,'complete_to_101_s':float(d['t'][-1])==101})
 assert len(traces)==3 and sum(r['within_0_1_Hz'] for r in traces)==2 and all(r['complete_to_101_s'] for r in traces)
 audit=read(work/AUDIT/'INDEPENDENT_CHECKS.json');assert audit['checks']==592 and audit['failed']==0
 unchanged=all(fingerprint(SOURCE/p)==f for p,f in original.items());assert unchanged
 result={'passed':True,'scope':'Fresh-copy interval lower, all six interval upper policies, seven feedback tests, 1444 exact network boundary checks, non-mutating freeze refusal, all 24 saved CSV physical rechecks, and three representative raw nonlinear peak reconstructions. No new scientific experiment.','runtime':{'python':platform.python_version(),'executable':sys.executable,'numpy':np.__version__,'scipy':scipy.__version__,'mpmath':mpmath.__version__},'commands':results,'core_science_fields_exact_match_ignoring_elapsed_seconds':True,'boundary_science_fields_exact_match_ignoring_audit_timestamp':True,'protected_freeze_inputs_manifests_coefficients':len(protected),'freeze_sha256_size_mtime_unchanged':before==after,'canonical_csv_sets_verified':len(all_cases),'representative_nonlinear_traces':traces,'recorded_independent_audit_checks_not_rerun':audit['checks'],'extracted_package_source_bytes_and_mtimes_unchanged':unchanged,'package_integrity':integrity,'work_dir':str(work),'limitations':['No controller synthesis, LP reoptimization, or nonlinear replay was performed.','Full check_core_evidence.py and independent_checks.py were not executed: they require omitted prior-round/source/cache evidence and the full set of traces.','Relocated paths in public records are interpreted read-only by basename within copied confirmation/; frozen manifests are never rewritten.','This validates this local Python environment, not all operating systems or dependency versions.']}
 (work/'VALIDATION_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
