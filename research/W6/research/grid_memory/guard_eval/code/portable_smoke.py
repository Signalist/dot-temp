"""Run from any extraction location; no network or original archive required."""
from guard_study import *
start=time.perf_counter();checks=[]
for name,h in json.loads((ROOT/'PROTOCOL.json').read_text())['source_sha256'].items():
 ok=hashlib.sha256((ORIGINAL/Path(name).name).read_bytes()).hexdigest()==h;assert ok;checks.append({'source':Path(name).name,'sha256_agrees':ok})
g=Grid(.4,.1);assert abs(g.G()-.1901466801229238)<1e-14
r=safe_solver(.5,1.,.05/g.G(),32);assert r['success'] and r['actual_peak_power']<=.05/g.G()+1e-12
p=Policy(.5,1.,np.linspace(0,2,len(r['z'])),r['z']);peak=FrequencyEvaluator(p,g).worst(n=129)[0];assert peak['peak_Hz']<.05
result={'source':checks,'N32_design_objective':r['parts']['objective'],'N129_EOS_design_peak':peak['peak_Hz'],'seconds':time.perf_counter()-start,'scope':'portable smoke only, not replacement of frozen primary or confirmation outputs'}
(ROOT/'raw/PORTABLE_SMOKE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
