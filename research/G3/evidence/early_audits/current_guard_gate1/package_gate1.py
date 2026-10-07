"""Freeze only completed Gate1 evidence, excluding next unexecuted proposals."""
from pathlib import Path
import json,hashlib,zipfile,datetime
R=Path(__file__).resolve().parents[1];P=R.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
archives=[('G3_GateA_with_extension_20261002.zip','0d23d57e94eb17407570be7c7a336a703240e68232195af62e40e610c3c53ab5'),('G3_PORT_CURRENT_INCREMENT_20261002.zip','8b783534e189f75952ec98d73f74925e304ce31924f147a38b17233e5c631a02'),('G3_DYNAMIC_CURRENT_GUARD_PROPOSAL_20261002.zip','80fe75515f5cadbc2bb37f4f6b163afa72e7b09bd6329000765ca9c937f00712'),('G3_GATE0_MPSC_INCREMENT_20261002.zip','549d872d2dd6f64ab05bdddedb73abd2130eb4ae25f7520a20f08cdd4c072d2f')]
old={}
for name,h in archives:
 assert sha(P/name)==h,(name,'archive hash mismatch')
 with zipfile.ZipFile(P/name) as z:
  for n in z.namelist():
   if not n.endswith('/'):old[n]=(name,hashlib.sha256(z.read(n)).hexdigest())
files=sorted(p for p in (R/'current_guard_gate1').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files += [R/'GATE1_MPSC_MODEL_REPORT_ZH.md',R/'INCREMENT_GATE1_README.md']
assert not any(str(p.relative_to(R)) in old for p in files)
assert all(p.suffix in ['.py','.json','.md','.log','.png','.npz','.gz'] for p in files)
deps=['protocol/GATE_A_LOCKED_V2_1.json','gate_a/preconditioned_dq/h1e-05_checkpoint.json','gate_a/dq_bench.py','gate_a/dq_preconditioned.py','gate_a_extension/results/matched_no_fault_reference_v2.npz','source_speed_ablation/results/fast_reference_h1e-05.npz','protocol/GATE0_MPSC_DESIGN_V1.json','protocol/GATE1_MPSC_SIX_MODELS_V1.json','current_guard_gate0/GATE0_RESULTS.json','current_guard_gate0/INDEPENDENT_MATH_REVIEW.md','protocol/phase_mechanism/dynamic_current_baseline_proposal.md','protocol/phase_mechanism/current_guard_sources.json']
prior=[]
for name in deps:
 origin,h=old[name];assert sha(R/name)==h,(name,'prior dependency modified')
 prior.append({'path':name,'sha256':h,'bytes':(R/name).stat().st_size,'available_in_prior_archive':origin,'included_in_this_increment':False})
for cid in ['C0-slow','C0-fast','C50-slow','C50-fast','C1-slow','C1-fast']:
 d=json.loads((R/f'current_guard_gate1/results/{cid}_h1e-05.json').read_text())
 assert d['guard_source_sha256']==sha(R/'current_guard_gate1/common_guard.py')
 assert d['controller_source_sha256']==sha(R/'current_guard_gate1/guarded_controller.py')
 assert d['runner_source_sha256']==sha(R/'current_guard_gate1/run_models.py')
manifest={'kind':'G3 common-MPSC six-model Gate1 increment, not standalone full archive','created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Six primary conditions plus four same-condition5us boundary refinements; no new allocator or workload strategy experiment','new_files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files],'prior_dependencies':prior,'prior_archives':[{'filename':n,'sha256':h} for n,h in archives],'status':{'primary_conditions_executed':6,'same_condition_refinements':4,'no_fault_finite_physical_passes':2,'faults_terminated_DC_before_clearance':4,'current_guard_qualified':False,'paper_ready':False,'joint_DC_SOC_invariance':False,'machine_interval_certificate':False,'real_time_qualified':False},'audit':'Independent algebra/interface and all ten raw/NPZ/summary records reconciled; no postrun change of three executed code hashes','provenance':'New authorized Gate1 averaged-model trajectories, using prior reconstructed_then_rerun physical protocol/checkpoint. No historical raw recovery claim.','exclusions':['next_constructive pending proposal/ledger','third-party PDFs/manuals/source copies','wheel/venv','previous large archives']}
m=R/'INCREMENT_GATE1_MANIFEST.json';m.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n');files.append(m)
out=P/'G3_GATE1_MPSC_SIX_MODELS_INCREMENT_20261002.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:z.write(p,str(p.relative_to(R)))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for p in files:assert hashlib.sha256(z.read(str(p.relative_to(R)))).hexdigest()==sha(p)
identity={'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'archive_files':len(files),'new_manifest_members':len(manifest['new_files']),'prior_dependency_files':len(prior),'all_new_members_hash_verified':True,'zip_crc_verified':True,'prior_archives_unchanged_verified':True,'prior_dependency_hashes_verified':True,'is_standalone_full_archive':False}
(P/'G3_GATE1_MPSC_SIX_MODELS_INCREMENT_IDENTITY.json').write_text(json.dumps(identity,indent=2)+'\n');print(json.dumps(identity,indent=2))
