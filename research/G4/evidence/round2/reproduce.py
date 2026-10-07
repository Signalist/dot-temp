#!/usr/bin/env python3
"""Verify the public package and rerun unchanged scientific scripts in a new copy."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--verify-only',action='store_true',help='Verify package hashes without running experiments')
p.add_argument('--include-grid',action='store_true',help='Also rerun current G4 grid transfer with bundled locked inputs')
p.add_argument('--figures',action='store_true',help='Regenerate figures; requires Matplotlib')
p.add_argument('--destination',default='rerun_workspace',help='New output directory, relative to package root unless absolute')
a=p.parse_args();root=Path(__file__).resolve().parent
manifest=json.loads((root/'PUBLIC_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
for r in manifest['files']:
 f=root/r['public_path']
 if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=r['public_sha256']:
  raise SystemExit('Package hash mismatch: '+r['public_path'])
print('Package payload hashes verified.')
if a.verify_only:raise SystemExit(0)
work=root/a.destination
if work.exists():raise SystemExit('Destination already exists; choose a new --destination to avoid overwriting any evidence.')
work.mkdir(parents=True);shutil.copytree(root/'outputs',work/'outputs')
R=Path('outputs/round2_g4_identifiability_20261003')
scripts=[
'experiments/recovery_frontier.py','experiments/causal_horizon_design.py','experiments/fixed_initial_compare.py',
'experiments/dag_equivalence.py','experiments/smooth_dag_pair.py','experiments/timing_ablation.py',
'experiments/measurement_ablation.py','experiments/heldout_transfer.py','experiments/two_site_measurement_design.py',
'experiments/grid_service_decision.py','validation/exact_dual_certificate.py','validation/exact_feasible_witness.py',
'validation/integrate_smooth_witness.py']
if a.include_grid:scripts+=['experiments/grid_transfer/run_transfer_study.py','experiments/grid_transfer/validate_and_witness.py']
scripts+=['theory/independent_theory_checks.py','theory/check_fixed_initial_schedules.py','theory/check_smooth_physical_witness.py','theory/check_service_decision.py']
if a.figures:scripts+=['report/make_figures.py','report/make_service_figure.py']
env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
logs=work/'run_logs';logs.mkdir();failed=[]
for script in scripts:
 print('Running '+script,flush=True)
 result=subprocess.run([sys.executable,str(R/script)],cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 (logs/(Path(script).stem+'.log')).write_text(result.stdout,encoding='utf-8')
 if result.returncode:failed.append({'script':script,'exit_code':result.returncode})
summary={'commands':len(scripts),'all_exit_codes_zero':not failed,'failures':failed,'note':'Run outputs are in a separate copy; the packaged frozen evidence is unchanged. This launcher checks exit codes, not cross-version numerical equivalence.'}
(work/'RUN_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
raise SystemExit(1 if failed else 0)
