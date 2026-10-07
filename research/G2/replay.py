#!/usr/bin/env python3
"""Portable, copy-on-run replay. Scientific computations are unchanged; public paths and package integrity are adapted.
Standard library suffices for --mode verify. Full replay uses requirements.txt.
"""
import argparse,datetime,hashlib,json,math,os,platform,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
R3=Path('outputs/round3_g2_20261004')
STAGES=[
 ('prior_art','literature/verify_reductions.py','literature/REDUCTION_DIAGNOSTICS.json'),
 ('matched_support','experiments/matched_support_baselines.py','experiments/matched_support_results.json'),
 ('matched_arc_budget','experiments/matched_arc_budget.py','experiments/matched_arc_budget_results.json'),
 ('matched_audit','audit/verify_matched_support.py','audit/MATCHED_SUPPORT_QA.json'),
 ('jerk_compression','experiments/jerk_compression.py','experiments/jerk_compression_results.json'),
 ('theory_diagnostics','theory_worker/verify_theory.py','theory_worker/THEORY_DIAGNOSTICS.json'),
 ('jerk_audit','audit/verify_jerk_audit.py','audit/JERK_AUDIT_DIAGNOSTICS.json'),
 ('network_structure','experiments/network_structure_transfer.py','experiments/network_structure_results.json'),
]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
from verify import verify_manifest
def saved_assertions(base):
 r=base/R3
 for f in ['experiments/matched_support_results.json','experiments/jerk_compression_results.json','experiments/network_structure_results.json','audit/MATCHED_SUPPORT_QA.json','literature/REDUCTION_DIAGNOSTICS.json']:
  assert load(r/f)['status']=='passed',f
 t=load(r/'theory_worker/THEORY_DIAGNOSTICS.json');assert t['all_sampled_bounds_hold']
 assert t['max_identity_error']<1e-12 and t['max_refinement_error']<1e-12
 for f in ['EXPERIMENT_CODE_SHA256.txt','JERK_COMPRESSION_CODE_SHA256.txt']:
  expected,rel=(r/'protocol'/f).read_text().strip().split(maxsplit=1);assert sha(base/rel)==expected
 for c in load(r/'report/CLAIM_LEDGER.json'):assert (r/c['evidence']).is_file()
 net=load(r/'experiments/network_structure_results.json');assert sha(base/net['source'])==net['source_sha256']
 prior={};available=[] # Full historical corpus intentionally not published or reverified.
 mat=load(r/'experiments/matched_support_results.json')['rows'];comp=load(r/'experiments/jerk_compression_results.json')['rows'];qa=load(r/'audit/MATCHED_SUPPORT_QA.json')['checks'];arc=load(r/'experiments/matched_arc_budget_results.json')
 assert len(mat)==9 and sum(len(x['uniform_methods']) for x in mat)==54
 assert len(comp)==10 and sum(len(x['observations']) for x in comp)==2570
 assert len(qa)==9 and len(arc)==3 and len(t['identity_rows'])==45
 assert t['analytic_constants']['N0']==1734133
 ja=load(r/'audit/JERK_AUDIT_DIAGNOSTICS.json')
 assert ja['max_original_primitive_error']<1e-10 and ja['max_original_bv_error']<1e-10
 assert len(ja['identity_checks'])==28 and len(ja['witness_checks'])==9 and len(ja['phase_envelope_lp_checks'])==9
 assert all(x['error']<=x['error_bound'] for x in ja['witness_checks'])
 assert all(x['success'] and abs(x['lp']-x['envelope'])<1e-8 for x in ja['phase_envelope_lp_checks'])
 return {'status':'passed','matched_cases':9,'matched_grid_witnesses':54,'same_arc_cases':3,'compression_cases':10,'compression_observations':2570,'theory_formula_cases':45,'independent_jerk_identity_cases':28,'independent_jerk_witness_cases':9,'independent_phase_LP_cases':9,'prior_corpus_entries':896,'included_prior_files_checked':0,'omitted_prior_files_not_checked':896,'full_historical_verifier_executed':False,'scope':'Assertions on stored or freshly regenerated results; this is not a proof or interval certificate'}
def compare_json(a,b):
 mismatches=[];numbers=0;max_abs=0.;ignored=[]
 def walk(a,b,p='$'):
  nonlocal numbers,max_abs
  if isinstance(a,dict) and isinstance(b,dict):
   if set(a)!=set(b):mismatches.append(p+': key sets differ');return
   for k in a:
    if k=='seconds':ignored.append(p+'.seconds');continue
    walk(a[k],b[k],p+'.'+k)
  elif isinstance(a,list) and isinstance(b,list):
   if len(a)!=len(b):mismatches.append(p+': lengths differ');return
   for i,(x,y) in enumerate(zip(a,b)):walk(x,y,p+f'[{i}]')
  elif isinstance(a,(float,int)) and not isinstance(a,bool) and isinstance(b,(float,int)) and not isinstance(b,bool):
   numbers+=1;delta=abs(a-b);max_abs=max(max_abs,delta)
   if isinstance(a,int) and isinstance(b,int):ok=(a==b)
   else:ok=math.isfinite(a) and math.isfinite(b) and math.isclose(a,b,rel_tol=1e-7,abs_tol=1e-12)
   if not ok:mismatches.append(f'{p}: {a!r} != {b!r}')
  elif a!=b:mismatches.append(p+': non-numeric values differ')
 walk(a,b)
 return {'status':'passed' if not mismatches else 'failed','numeric_values_checked':numbers,'max_absolute_difference':max_abs,'rtol':1e-7,'atol':1e-12,'ignored_wall_time_fields':len(ignored),'mismatches':mismatches[:30],'scope':'Regression comparison, not a guarantee of relative accuracy near zero; script assertions remain essential'}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mode',choices=['verify','diagnostics','full'],default='verify');p.add_argument('--work-dir',type=Path);args=p.parse_args()
 integrity=verify_manifest();print(json.dumps({'manifest':integrity}),flush=True)
 if args.mode=='verify':print(json.dumps({'saved_results':saved_assertions(ROOT/'evidence/snapshot')},indent=2));return
 work=(args.work_dir or ROOT/'replay_work').resolve()
 if work.exists():p.error('Work directory already exists. Choose a new empty/nonexistent directory; nothing was overwritten.')
 if work==ROOT/'evidence/snapshot' or ROOT/'evidence/snapshot' in work.parents:p.error('Work directory cannot be inside immutable snapshot')
 work.mkdir(parents=True);shutil.copytree(ROOT/'evidence/snapshot/outputs',work/'outputs');(work/'logs').mkdir()
 import numpy,scipy,sympy,mpmath
 report={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':args.mode,'status':'running','manifest_before':integrity,'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'dependencies':{x.__name__:x.__version__ for x in [numpy,scipy,sympy,mpmath]},'fresh_environment_install_tested':False,'stages':[],'historical_896_file_check_rerun':False,'boundary':'Replays round-3 scripts from supplied matrix; does not regenerate ANDES matrices or rerun round-2 grid simulations'}
 env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONPATH']=''
 selected=STAGES if args.mode=='full' else [s for s in STAGES if s[0] in ['prior_art','matched_audit','theory_diagnostics','jerk_audit','network_structure']]
 try:
  for name,script,result in selected:
   t=time.perf_counter();cmd=[sys.executable,str(R3/script)]
   with (work/'logs'/f'{name}.log').open('w') as log:r=subprocess.run(cmd,cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT)
   stage={'name':name,'command':cmd,'cwd':'replay work directory','exit_code':r.returncode,'seconds':time.perf_counter()-t,'log':f'logs/{name}.log','source_sha256':sha(work/R3/script)}
   report['stages'].append(stage);assert r.returncode==0,f'{name} failed; see {stage["log"]}'
   stage['comparison_to_archived']=compare_json(load(ROOT/'evidence/snapshot'/R3/result),load(work/R3/result));assert stage['comparison_to_archived']['status']=='passed',name+' regression mismatch'
   if name=='network_structure':
    old=numpy.load(ROOT/'evidence/snapshot'/R3/'experiments/network_structure_kernels.npz',allow_pickle=False);new=numpy.load(work/R3/'experiments/network_structure_kernels.npz',allow_pickle=False)
    arrays=[]
    assert old.files==new.files
    for key in old.files:
     assert old[key].shape==new[key].shape and old[key].dtype==new[key].dtype
     err=float(numpy.max(numpy.abs(old[key]-new[key])));assert numpy.allclose(old[key],new[key],rtol=1e-7,atol=1e-12)
     arrays.append({'name':key,'shape':list(old[key].shape),'max_absolute_difference':err})
    stage['array_regression']={'status':'passed','arrays':arrays,'rtol':1e-7,'atol':1e-12}
   print(json.dumps({'stage':name,'seconds':stage['seconds'],'status':'passed'}),flush=True)
  report['result_assertions']=saved_assertions(work);report['manifest_after']=verify_manifest();report['status']='passed'
 except Exception as e:report['status']='failed';report['error']=str(e);raise
 finally:
  report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(work/'replay_report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'status':report['status'],'report':str(work/'replay_report.json'),'stages_completed':len(report['stages'])}),flush=True)
if __name__=='__main__':main()
