"""CPU-only tests on a disposable copy. No inference, network or GPU control."""
import argparse, datetime, importlib.metadata, json, os, pathlib, shutil, subprocess, sys, tempfile, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--science',action='store_true');p.add_argument('--full-cycle-replay',action='store_true');p.add_argument('--network-replay',action='store_true');p.add_argument('--report',default='verification/RECHECK.json');args=p.parse_args()
commands=[('compileall','.',['-m','compileall','-q','.']),('quality','continuation/quality',['-m','unittest','-v','test_validators']),('legacy_compact','continuation/quality',['rescore_compact.py']),('acquisition_kit','gpu_handoff',['-m','unittest','discover','-s','tests','-v']),('parser','research/measurement/code',['read_only_schema_auditor.py']),('development_export','continuation/quality',['prepare_requests.py','--out','development_export_test.jsonl']),('payload_invariants','.',['-m','unittest','discover','-s','tests','-v'])]
if args.science or args.full_cycle_replay:
    commands += [('full_cycle_witnesses','research/full_cycle',['audit/check_full_cycle_witnesses.py']),('signed_swing','research/grid_memory',['review/verify_swing_exact.py']),('guard_smoke','research/grid_memory',['guard_eval/code/portable_smoke.py'])]
if args.full_cycle_replay:commands += [('full_cycle_replay','research/full_cycle',['code/reproduce.py'])]
if args.network_replay:commands += [('qualified_matrix','.',['scripts/check_optional_inputs.py']),('network_transfer','research/grid_memory',['review/verify_network_transfer.py'])]
rows=[];start=time.monotonic()
with tempfile.TemporaryDirectory(prefix='w6-public-checks-') as td:
    work=pathlib.Path(td)/'payload'
    shutil.copytree(ROOT,work,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.venv','scratch'))
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MPLCONFIGDIR=str(pathlib.Path(td)/'mpl'),XDG_CACHE_HOME=str(pathlib.Path(td)/'cache'))
    for name,cwd,argv in commands:
        began=time.monotonic()
        try:
            result=subprocess.run([sys.executable,*argv],cwd=work/cwd,env=env,capture_output=True,text=True,timeout=480)
            row={'check':name,'cwd':cwd,'command':['python',*argv],'returncode':result.returncode,'seconds':round(time.monotonic()-began,3),'stdout':result.stdout.replace(td,'<temporary_copy>'),'stderr':result.stderr.replace(td,'<temporary_copy>')}
        except subprocess.TimeoutExpired:
            row={'check':name,'cwd':cwd,'command':['python',*argv],'returncode':None,'seconds':round(time.monotonic()-began,3),'error':'480-second check timeout; no pass inferred'}
        rows.append(row);print(name, 'PASS' if row['returncode']==0 else 'FAIL',flush=True)
versions={}
for name in ['numpy','scipy','mpmath','matplotlib']:
    try:versions[name]=importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:versions[name]=None
out={'passed':all(r['returncode']==0 for r in rows),'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version.split()[0],'dependencies':versions,'new_gpu_runs':0,'network_requests':0,'hardware_actuations':0,'generated_model_code_executed':False,'full_scientific_regeneration':False,'original_legacy_telemetry_reverified':False,'scope':'Named checks only; compact quality replay uses public derived records. Not a new independent experiment, hardware/quality claim or interval certificate.','seconds':round(time.monotonic()-start,3),'checks':rows}
report=ROOT/args.report;report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(out,indent=2)+'\n');print('Report:',args.report)
if not out['passed']:raise SystemExit(1)
