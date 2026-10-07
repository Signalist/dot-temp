"""Freeze the four standard-allocation records and bounded research closure."""
from pathlib import Path
import json,hashlib,zipfile,datetime
R=Path(__file__).resolve().parents[1];P=R.parent;B=R/'current_guard_constructive'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
archives=[('G3_GateA_with_extension_20261002.zip','0d23d57e94eb17407570be7c7a336a703240e68232195af62e40e610c3c53ab5'),('G3_PORT_CURRENT_INCREMENT_20261002.zip','8b783534e189f75952ec98d73f74925e304ce31924f147a38b17233e5c631a02'),('G3_DYNAMIC_CURRENT_GUARD_PROPOSAL_20261002.zip','80fe75515f5cadbc2bb37f4f6b163afa72e7b09bd6329000765ca9c937f00712'),('G3_GATE0_MPSC_INCREMENT_20261002.zip','549d872d2dd6f64ab05bdddedb73abd2130eb4ae25f7520a20f08cdd4c072d2f'),('G3_GATE1_MPSC_SIX_MODELS_INCREMENT_20261002.zip','06cbba5897d99651261866bbd82c8e8ad25e8aaa560f05615086e7eed181ac5b')]
old={}
for name,h in archives:
 assert sha(P/name)==h,(name,'archive hash mismatch')
 with zipfile.ZipFile(P/name) as z:
  for n in z.namelist():
   if not n.endswith('/'):old[n]=(name,hashlib.sha256(z.read(n)).hexdigest())
def select_files():
 files=sorted(p for parent in [B,R/'protocol/next_constructive'] for p in parent.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 return files+[R/'G3_CONSTRUCTIVE_AND_CLOSURE_REPORT_ZH.md',R/'INCREMENT_CONSTRUCTIVE_README.md']
files=select_files();raw=[p for p in files if p.suffix=='.npz' or p.name.endswith('.jsonl.gz')]
index=B/'LIGHT_ADDITIONS_INDEX.json'
index.write_text(json.dumps({'kind':'Light code/report additions, not a full-data backup','included_paths':sorted(set([str(p.relative_to(R)) for p in files if p not in raw]+[str(index.relative_to(R)),'INCREMENT_CONSTRUCTIVE_MANIFEST.json'])),'excluded_raw_data':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in raw],'full_raw_archive':'G3_CONSTRUCTIVE_CLOSURE_INCREMENT_20261002.zip','merge_instruction':'Append to the existing light artifact under the same Library identity; deduplicate identical proposal paths; retain all old members. No raw-data completeness claim for this light ZIP.'},indent=2)+'\n')
files=select_files();assert not any(str(p.relative_to(R)) in old for p in files)
assert all(p.suffix in ['.py','.json','.md','.log','.png','.npz','.gz','.patch','.sha256'] for p in files)
deps=['protocol/GATE_A_LOCKED_V2_1.json','gate_a/preconditioned_dq/h1e-05_checkpoint.json','gate_a/dq_bench.py','gate_a/dq_preconditioned.py','baseline_allocation/allocators.py','protocol/GATE0_MPSC_DESIGN_V1.json','protocol/GATE1_MPSC_SIX_MODELS_V1.json','current_guard_gate0/GATE0_RESULTS.json','current_guard_gate0/INDEPENDENT_MATH_REVIEW.md','current_guard_gate1/common_guard.py','current_guard_gate1/run_models.py','current_guard_gate1/audit_interface_tests.py','current_guard_gate1/audit_runner_checks.py','current_guard_gate1/results/C0-fast_h1e-05.json','current_guard_gate1/results/C50-fast_h1e-05.json','protocol/phase_mechanism/dynamic_current_baseline_proposal.md','protocol/phase_mechanism/current_guard_sources.json','protocol/phase_mechanism/literature_collision.md','protocol/phase_mechanism/sources.json','protocol/phase_mechanism/theory_proposal.md','protocol/phase_mechanism/dc_topology_scope.md','protocol/phase_mechanism/dc_topology_sources.json','protocol/phase_mechanism/exogenous_waveform_scope.md','protocol/phase_mechanism/waveform_sources.json']
prior=[]
for name in deps:
 origin,h=old[name];assert sha(R/name)==h,(name,'prior dependency modified')
 prior.append({'path':name,'sha256':h,'bytes':(R/name).stat().st_size,'available_in_prior_archive':origin,'included_in_this_increment':False})
for cid in ['P0-fast','R0-fast','P50-fast','R50-fast']:
 d=json.loads((B/f'results/{cid}_h1e-05.json').read_text())
 assert d['guard_source_sha256']==sha(R/'current_guard_gate1/common_guard.py')
 assert d['controller_source_sha256']==sha(B/'guarded_allocator_controller.py')
 assert d['runner_source_sha256']==sha(B/'run_constructive.py')
 assert d['complete_hard_safe'] and not d['numerical_refinement_indicated']
manifest={'kind':'G3 four constructive standard-allocation cases and bounded closure increment, not standalone full archive','created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files],'prior_dependencies':prior,'prior_archives':[{'filename':n,'sha256':h} for n,h in archives],'status':{'primary_conditions_executed':4,'same_condition_refinements':0,'finite_hard_safe_fault_witnesses':2,'full_original_PQ_service_success':False,'frozen_formal_recovery_success':False,'healthy_target_guard_compatibility_issue_observed':True,'engineering_evidence':'finite numerical construction under locked synthetic averaged topology only','current_guard_qualified':False,'paper_ready':False,'compute_load_specificity':False,'hardware_transfer':False,'real_time_qualified':False,'new_search_planned':False},'audit':'All86004samples/plans independently reconciled; all four completed; original scoring unchanged; current guard code reused unchanged','provenance':'New authorized four-condition standard-baseline runs; old six-case hypothesis ledger retained, post-four update separate; no invented missing observation','exclusions':['old large archives','third-party PDFs/manuals/source copies','wheel/venv','new unapproved scenarios']}
m=R/'INCREMENT_CONSTRUCTIVE_MANIFEST.json';m.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n');files.append(m)
outputs=[]
for name,items in [('G3_CONSTRUCTIVE_CLOSURE_INCREMENT_20261002.zip',files),('G3_CONSTRUCTIVE_CODE_LIGHT_ADDITIONS_20261002.zip',[p for p in files if not(p.suffix=='.npz' or p.name.endswith('.jsonl.gz'))])]:
 out=P/name
 with zipfile.ZipFile(out,'w') as z:
  for p in items:z.write(p,str(p.relative_to(R)),compress_type=zipfile.ZIP_STORED if p.suffix in ['.npz','.gz'] else zipfile.ZIP_DEFLATED,compresslevel=None if p.suffix in ['.npz','.gz'] else 9)
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
  assert len(set(z.namelist()))==len(z.namelist())==len(items)
  for p in items:assert hashlib.sha256(z.read(str(p.relative_to(R)))).hexdigest()==sha(p)
 outputs.append({'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'archive_files':len(items),'all_members_hash_verified':True,'zip_crc_verified':True})
identity={'archives':outputs,'new_manifest_members':len(manifest['new_files']),'prior_dependency_files':len(prior),'prior_archives_unchanged_verified':True,'prior_dependency_hashes_verified':True,'full_increment_raw_files':len(raw),'is_standalone_full_archive':False}
(P/'G3_CONSTRUCTIVE_CLOSURE_IDENTITY.json').write_text(json.dumps(identity,indent=2)+'\n');print(json.dumps(identity,indent=2))
