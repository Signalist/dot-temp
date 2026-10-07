from pathlib import Path
import json,hashlib,zipfile,datetime
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=R.parent/'G3_GateA_with_extension_20261002.zip';basehash='0d23d57e94eb17407570be7c7a336a703240e68232195af62e40e610c3c53ab5';assert sha(base)==basehash
baseman=json.loads((R/'DELIVERY_MANIFEST_GATE_A_EXTENSION.json').read_text());basepaths={e['path'] for e in baseman['files']}
for e in baseman['files']:assert sha(R/e['path'])==e['sha256'],e['path']
readme='''# G3 源速度/静态分配/独立abc 增量包

此包不是独立全量包。请先恢复已保存的 **G3完整v2**，再将本包按相对路径展开到相同G3根目录。所有本包文件均为新增文件，不替换v2原文件。

基础包：`G3_GateA_with_extension_20261002.zip`，211,699,716 bytes，SHA256 `0d23d57e94eb17407570be7c7a336a703240e68232195af62e40e610c3c53ab5`。

主入口：`G3_PORT_AND_CURRENT_AUDIT_REPORT_ZH.md`；机器摘要：`G3_PORT_AND_CURRENT_AUDIT_SUMMARY.json`。原始失败、未观察到清除/恢复、微小越流、参考请求误差与配对参照差均保留。当前paper_ready=false。

`INCREMENT_PORT_CURRENT_MANIFEST.json` 将“本包新增文件及哈希”与“依赖基础v2的原文件及哈希”分开列出。两类不得混为恢复原件。`source_speed_ablation/verify_increment_dependencies.py` 可在叠加后只读核对。

本包仅有自行编写的源码、图表、实验结果、研究摘要及公开来源链接。没有下载的论文/厂家PDF原件，没有wheel、venv或第三方代码副本。使用NumPy/SciPy/Matplotlib等依赖仍遵循基础包的来源记录，二进制与安装环境不随包复制。独立abc为自行实现的公开方程复核，直接调用的原自行实现代码由基础v2提供。

包含已完成的DC拓扑适用性更正、解析源包络及文献/波形证据摘要；这些摘要中的未来开发实例均标记为尚未仿真。**不包含**下一动态电流guard提案及其来源文件，亦没有实现该guard。

重现注意：现有实验脚本使用固定结果目录。若另行复验，先复制到新的版本化工作目录，避免覆盖本包原始记录。读取和校验无需重跑。
'''
(R/'INCREMENT_PORT_CURRENT_README.md').write_text(readme)
verify='''from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'INCREMENT_PORT_CURRENT_MANIFEST.json').read_text())
for group in ['new_files','base_v2_dependencies']:
 for f in m[group]:
  p=R/f['path']
  assert p.exists(), f"Missing {group}: {p}; restore the base G3 v2 before using this increment"
  assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],f"Hash mismatch: {p}"
print('All new files and base-v2 dependencies verified; no simulation executed')
'''
(R/'source_speed_ablation/verify_increment_dependencies.py').write_text(verify)
files=[R/'G3_PORT_AND_CURRENT_AUDIT_REPORT_ZH.md',R/'G3_PORT_AND_CURRENT_AUDIT_SUMMARY.json',R/'INCREMENT_PORT_CURRENT_README.md']
for folder in ['source_speed_ablation','baseline_allocation','model_audit/p_priority_abc']:
 files.extend(p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.zip','.pdf','.whl'))
for name in ['GATE_A_SOURCE_SPEED_V1.json','GATE_A_SOURCE_SPEED_V1.sha256','GATE_A_ALLOCATION_BASELINES_V1.json','GATE_A_ALLOCATION_BASELINES_V1.sha256']:
 files.append(R/'protocol'/name)
files.extend(p for p in (R/'protocol/phase_mechanism').iterdir() if p.is_file() and p.name not in ['dynamic_current_baseline_proposal.md','current_guard_sources.json'] and p.suffix in ('.py','.json','.md'))
files=sorted(set(files));newpaths={p.relative_to(R).as_posix() for p in files};assert not newpaths&basepaths
external={'protocol/GATE_A_LOCKED_V1_1.json','protocol/GATE_A_LOCKED_V2_1.json','gate_a/dq_bench.py','gate_a/dq_preconditioned.py','gate_a/preconditioned_dq/h1e-05_checkpoint.json','gate_a/preconditioned_dq/h1e-05.json','gate_a/preconditioned_dq/h1e-05.npz','protocol/DC_BOUND_GATE_A_V2_1_REVALIDATED.json','protocol/DC_BOUND_GATE_A_V2_1_REVALIDATED.md','gate_a_extension/results/signed_periodic_h1e-05.npz','GATE_A_EXTENSION_REPORT_ZH.md','model_audit/abc_reference/reference_abc.py','model_audit/abc_reference/preconditioned_abc.py'}
abc=json.loads((R/'model_audit/p_priority_abc/MANIFEST.json').read_text())
external.update(k for k in abc['input_sha256'] if k not in newpaths)
assert all((R/q).exists() for q in external),external
m={'package_type':'increment_only_requires_G3_complete_v2','created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_archive':{'filename':base.name,'bytes':base.stat().st_size,'sha256':basehash,'version_label':'G3 complete v2'},'main_report':'G3_PORT_AND_CURRENT_AUDIT_REPORT_ZH.md','paper_ready':False,'all_new_files_nonoverlapping_with_base_v2':True,'excluded':['guard proposal/current_guard_sources','all downloaded third-party PDF originals','all dependency wheels/virtualenvs','bytecode caches','base v2 raw data duplicated into increment'],'new_files':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'evidence_role':'new diagnostic, authored analysis/code, or research summary as marked in file'} for p in files],'base_v2_dependencies':[{'path':q,'bytes':(R/q).stat().st_size,'sha256':sha(R/q),'role':'Required unchanged base-v2 evidence/code; NOT included in this increment'} for q in sorted(external)]}
mp=R/'INCREMENT_PORT_CURRENT_MANIFEST.json';mp.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n');files.append(mp)
zpath=R.parent/'G3_PORT_CURRENT_INCREMENT_20261002.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None
 for f in m['new_files']:assert hashlib.sha256(z.read(f['path'])).hexdigest()==f['sha256']
identity={'path':str(zpath),'bytes':zpath.stat().st_size,'sha256':sha(zpath),'files':len(files),'new_manifest_members':len(m['new_files']),'base_dependency_count':len(m['base_v2_dependencies']),'is_increment_not_full':True,'base_archive_sha256':basehash,'crc_and_all_new_hashes_verified':True,'base_v2_hashes_unchanged':True,'guard_proposal_included':False}
(R.parent/'G3_PORT_CURRENT_INCREMENT_IDENTITY.json').write_text(json.dumps(identity,indent=2)+'\n');print(json.dumps(identity,indent=2))
