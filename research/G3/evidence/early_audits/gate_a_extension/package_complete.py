from pathlib import Path
import json,hashlib,zipfile,datetime,sys
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((R/'DELIVERY_MANIFEST.json').read_text())
for entry in prior['files']:
 p=R/entry['path'];assert sha(p)==entry['sha256'],f'Prior archived file changed: {p}'
ignore={'__pycache__','.git'}
files=sorted(p for p in R.rglob('*') if p.is_file() and not any(part in ignore or part.startswith('.venv') for part in p.relative_to(R).parts) and p.suffix not in ('.whl','.zip','.pyc') and p.name!='DELIVERY_MANIFEST_GATE_A_EXTENSION.json')
manifest={'package_status':'prior_reconstructed_then_rerun_plus_new_Gate_A_extension','stage':'fixed_12_condition_extension_complete','created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'main_report':'GATE_A_EXTENSION_REPORT_ZH.md','paper_ready':False,'Gate_B_run':False,'prior_manifest_verified_unchanged':True,'prior_manifest_sha256':sha(R/'DELIVERY_MANIFEST.json'),'prior_original_trajectory_binaries_recovered':False,'prior_trajectory_evidence':'Reconstructed sources rerun; four V2.1 raw hashes exactly reproduced historical retained digests','current_stage_evidence':'New diagnostic experiments, not recreated historical reports','excluded':['virtualenvs','bytecode caches','public dependency wheels','nested archives'],'files':[]}
for p in files:
 rel=p.relative_to(R).as_posix();role='new_Gate_A_extension_or_reporting_audit' if ('gate_a_extension' in rel.lower() or 'GATE_A_EXTENSION' in rel or 'GATE_A_EXTENSION_REPORT' in rel) else 'prior_reconstruction_revalidation_or_recovered_literature_preserved'
 manifest['files'].append({'path':rel,'bytes':p.stat().st_size,'sha256':sha(p),'evidence_role':role})
mp=R/'DELIVERY_MANIFEST_GATE_A_EXTENSION.json';mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n');files.append(mp)
archive=R.parent/'G3_GateA_with_extension_20261002.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for entry in manifest['files']:
  assert hashlib.sha256(z.read(entry['path'])).hexdigest()==entry['sha256'],entry['path']
identity={'path':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'files':len(files),'crc_verified':True,'every_manifest_member_sha256_verified':True,'prior_manifest_verified_unchanged':True,'main_report':'GATE_A_EXTENSION_REPORT_ZH.md','status':'complete_Gate_A_extension_no_Gate_B'}
(R.parent/'G3_GateA_EXTENSION_ARCHIVE_IDENTITY.json').write_text(json.dumps(identity,indent=2)+'\n');print(json.dumps(identity,indent=2))
