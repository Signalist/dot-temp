"""Package an explicit Gate0 increment. No old archive is changed or rerun."""
from pathlib import Path
import json,hashlib,zipfile,datetime
R=Path(__file__).resolve().parents[1];P=R.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
archives=[('G3_GateA_with_extension_20261002.zip','0d23d57e94eb17407570be7c7a336a703240e68232195af62e40e610c3c53ab5'),('G3_PORT_CURRENT_INCREMENT_20261002.zip','8b783534e189f75952ec98d73f74925e304ce31924f147a38b17233e5c631a02'),('G3_DYNAMIC_CURRENT_GUARD_PROPOSAL_20261002.zip','80fe75515f5cadbc2bb37f4f6b163afa72e7b09bd6329000765ca9c937f00712')]
old={}
for name,h in archives:
 assert sha(P/name)==h,(name,'archive hash mismatch')
 with zipfile.ZipFile(P/name) as z:
  for n in z.namelist():
   if not n.endswith('/'):old[n]=(name,hashlib.sha256(z.read(n)).hexdigest())
files=[p for p in (R/'current_guard_gate0').iterdir() if p.is_file()]
files += [R/p for p in ['GATE0_MPSC_REPORT_ZH.md','GATE1_MPSC_SIX_MODELS_CHECKLIST_ZH.md','INCREMENT_GATE0_README.md','protocol/GATE0_MPSC_DESIGN_V1.json','protocol/GATE0_MPSC_DESIGN_V1.sha256','protocol/GATE1_MPSC_SIX_MODELS_V1.json','protocol/GATE1_MPSC_SIX_MODELS_V1.sha256']]
files=sorted(files)
assert not any(str(p.relative_to(R)) in old for p in files)
assert all(p.suffix in ['.py','.json','.md','.sha256','.log','.png'] for p in files)
deps=['protocol/GATE_A_LOCKED_V2_1.json','gate_a/preconditioned_dq/h1e-05_checkpoint.json','model_audit/p_priority_abc/fast_p_priority_abc_h1e-05.npz','gate_a/dq_bench.py','protocol/DC_BOUND_GATE_A_V2_1_REVALIDATED.json','protocol/phase_mechanism/dynamic_current_baseline_proposal.md','protocol/phase_mechanism/current_guard_sources.json','protocol/phase_mechanism/CURRENT_GUARD_PROPOSAL_MANIFEST.json']
prior=[]
for name in deps:
 origin,h=old[name];assert sha(R/name)==h,(name,'prior dependency modified')
 prior.append({'path':name,'sha256':h,'bytes':(R/name).stat().st_size,'available_in_prior_archive':origin,'included_in_this_increment':False})
manifest={'kind':'G3 Gate0 increment, not a standalone full archive','created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Completed analytical/one-point offline Gate0 and independent audit; six-model checklist frozen before subsequent execution approval, no closed-loop results in this archive','status_at_freeze':{'current_guard_qualified':False,'paper_ready':False,'closed_loop_runs':0},'new_files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files],'prior_dependencies':prior,'prior_archives':[{'filename':n,'sha256':h} for n,h in archives],'exclusions':['raw third-party papers/manuals','third-party source copies','wheel','venv','all closed-loop guard results'],'provenance':'Gate0 is newly executed offline algebra/optimization; prior reconstructed_then_rerun trajectory provenance remains unchanged. No historical raw file is represented as recovered through this package.'}
m=R/'INCREMENT_GATE0_MANIFEST.json';m.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n');files.append(m)
out=P/'G3_GATE0_MPSC_INCREMENT_20261002.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:z.write(p,str(p.relative_to(R)))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(files)
 for p in files:assert hashlib.sha256(z.read(str(p.relative_to(R)))).hexdigest()==sha(p)
identity={'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'archive_files':len(files),'new_manifest_members':len(manifest['new_files']),'prior_dependency_files':len(prior),'all_new_members_hash_verified':True,'zip_crc_verified':True,'prior_archives_unchanged_verified':True,'prior_dependency_hashes_verified':True,'is_standalone_full_archive':False}
(P/'G3_GATE0_MPSC_INCREMENT_IDENTITY.json').write_text(json.dumps(identity,indent=2)+'\n');print(json.dumps(identity,indent=2))
