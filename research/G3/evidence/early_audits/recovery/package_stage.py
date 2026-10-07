from pathlib import Path
import json,hashlib,zipfile,sys,numpy,scipy
R=Path(__file__).resolve().parents[1]
def build(stage,files,result):
 result={'stage':stage,'status':'reconstructed_then_rerun','original_trajectory_binaries_recovered':False,**result}
 base_manifest=json.loads((R/'recovery/STAGE0_MANIFEST.json').read_text())
 files=list(dict.fromkeys([*[R/q['path'] for q in base_manifest['files']],R/'recovery/STAGE0_MANIFEST.json',*files]))
 rp=R/'recovery'/f'{stage}_RESULT.json';rp.write_text(json.dumps(result,indent=2)+'\n');files=[Path(p) for p in files]+[rp]
 manifest={'stage':stage,'status':'reconstructed_then_rerun','python':sys.version,'numpy':numpy.__version__,'scipy':scipy.__version__,'source_provenance':'Program/parameter text reconstructed from retained tool-call text; simulations rerun after reconstruction. Original NPZ files were unavailable.','files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
 mp=R/'recovery'/f'{stage}_MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2)+'\n');files.append(mp)
 z=R.parent/f'G3_{stage}_20261002.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
  for p in files:f.write(p,str(p.relative_to(R)))
 ident={'path':str(z),'bytes':z.stat().st_size,'sha256':hashlib.sha256(z.read_bytes()).hexdigest()};print(json.dumps(ident));return ident
if __name__=='__main__':
 results=[];files=[R/'gate_a/dq_bench.py',R/'protocol/GATE_A_LOCKED_V1_1.json',R/'protocol/GATE_A_LOCKED_V1_1.sha256',R/'recovery/PARAMETER_TEXT_RECONSTRUCTION.json',R/'recovery/RECOVERY_README.md',Path(__file__)]
 for h,tag in [(1e-5,'10us'),(5e-6,'5us')]:
  p=R/f'gate_a/dq_results/conservation_nominal_{h:g}.json';results.append(json.loads(p.read_text()));files +=[p,p.with_suffix('.npz'),R/f'recovery/nominal_{tag}_rerun.log']
 build('stage1_nominal_dq',files,{'cases':results,'passed':all(x['gate_hard_safe'] and x['max_abs_energy_conservation_residual_J']<1e-4 for x in results),'scope':'500kW/150kvar loss-bearing balanced average-value nominal benchmark. No sag, strategy comparison, PWM/EMT or hardware validation. Both runs hold control sample exactly100us; integration maximum step10/5us.'})
