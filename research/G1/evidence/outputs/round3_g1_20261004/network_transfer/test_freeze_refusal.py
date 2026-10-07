"""An existing freeze must cause an early, strictly non-mutating refusal."""
from pathlib import Path
import os,sys,json,hashlib,subprocess
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent

def fingerprint(path):
 q=Path(path);return {'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'bytes':q.stat().st_size,'mtime_ns':q.stat().st_mtime_ns}

if __name__=='__main__':
 paths=set()
 for name in ['CONFIRMATION_FREEZE.json','AMPLITUDE_STRESS_ADDENDUM_FREEZE.json']:
  path=OUT/name;paths.add(path)
  for c in json.loads(path.read_text())['cases']:
   paths.update(Path(c[k]) for k in ['it_csv','bess_csv','observations_csv'])
   paths.add(OUT/(c['controller']+'.npz'))
 before={str(p):fingerprint(p) for p in sorted(paths)};inventory=sorted(str(p) for p in (OUT/'confirmation').glob('*'))
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 run=subprocess.run([sys.executable,str(OUT/'freeze_confirmation.py')],capture_output=True,text=True,env=env)
 after={str(p):fingerprint(p) for p in sorted(paths)};after_inventory=sorted(str(p) for p in (OUT/'confirmation').glob('*'))
 rows=[{'path':p,'before':b,'after':after[p],'sha256_unchanged':b['sha256']==after[p]['sha256'],'mtime_unchanged':b['mtime_ns']==after[p]['mtime_ns'],'size_unchanged':b['bytes']==after[p]['bytes']} for p,b in before.items()]
 result={'tested_utc':datetime.now(timezone.utc).isoformat(),'returncode':run.returncode,'stderr':run.stderr,'stdout':run.stdout,'n_locked_inputs_manifests_coefficients':len(paths),'expected_early_refusal':run.returncode!=0 and 'refusing before input generation' in run.stderr,'all_sha256_unchanged':all(r['sha256_unchanged'] for r in rows),'all_mtimes_unchanged':all(r['mtime_unchanged'] for r in rows),'all_sizes_unchanged':all(r['size_unchanged'] for r in rows),'confirmation_inventory_unchanged':inventory==after_inventory,'files':rows}
 assert all(result[k] for k in ['expected_early_refusal','all_sha256_unchanged','all_mtimes_unchanged','all_sizes_unchanged','confirmation_inventory_unchanged'])
 (OUT/'FREEZE_REFUSAL_REGRESSION.json').write_text(json.dumps(result,indent=2));print({k:v for k,v in result.items() if k not in ['files','stdout','stderr']})
