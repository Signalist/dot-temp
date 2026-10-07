"""Cross-artifact scientific QA; assertions never replace analytical proofs."""
from pathlib import Path
import json,hashlib,mpmath as mp
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parent/'round2_20261003';mp.iv.dps=50;mp.mp.dps=70
checks=[]
def ck(name,truth,detail=None):
 checks.append(dict(name=name,pass_=bool(truth),detail=detail));assert truth,(name,detail)
lower=json.loads((ROOT/'raw/interval_lower_certificate.json').read_text());L=mp.mpf(lower['certified_energy_lower']);ck('new_prefix_lower_above_045561533',L>mp.mpf('.45561533'))
rows=json.loads((ROOT/'raw/interval_summary.json').read_text());rounded={'robust_policy.json':('.350694','.353911'),'frequency_policy_eta_0.005.json':('.351327','.354550'),'frequency_policy_eta_0.01.json':('.353820','.357066'),'frequency_policy_eta_0.02.json':('.358564','.361854'),'frequency_policy_eta_0.05.json':('.369018','.372404'),'no_feedback_policy.json':('.468265','.472561')}
for r in rows:
 name=r['policy'];ck(name+'_all_histories',r['all_histories_feasible']);ck(name+'_frequency',mp.mpf(r['frequency_upper'])<mp.mpf('.6'));ck(name+'_power',mp.mpf(r['power_upper'])<mp.mpf('.5'))
 ds=json.loads((ROOT/'raw'/('interval_'+name)).read_text())['histories'];e0,E=map(mp.mpf,rounded[name])
 for row in ds:
  ck(name+f"_p{row['p0']}_h{row['history']}_empty_soc",e0>=mp.mpf(row['zmax_upper']))
  ck(name+f"_p{row['p0']}_h{row['history']}_full_soc",E>=e0-mp.mpf(row['zmin_lower']))
for eta,tau in [('.005','.0101015272'),('.01','.0204124441'),('.02','.0417034085'),('.05','.1118325592')]:
 t=mp.iv.mpf(tau);value=t*mp.iv.exp(-t)-2*mp.iv.mpf(eta);ck('tau_outward_'+eta,mp.mpf(value._mpi_[0])>=0);ck('detect_before_second_edge_'+eta,mp.mpf(tau)+mp.mpf('.1')<1)
ck('strict_P_resource_separation',L>mp.mpf('.353911'));ck('strict_frequency_resource_separation',L>mp.mpf('.372404'))
ck('post20_tail',1/mp.e+20*mp.exp(-20)<mp.mpf('.6'))
# Frozen authoritative hashes, not freshly invented pre-work hashes.
old=json.loads((BASE/'manuscript_phase/writer_manifest.json').read_text())['source_files']
for name,record in old.items():
 path=BASE/name
 if path.exists():ck('round2_final_preserved_'+name,hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256'])
old=json.loads((BASE/'classical_feedback/MANIFEST.json').read_text())['files']
for name,h in old.items():ck('round2_classical_preserved_'+name,hashlib.sha256((BASE/'classical_feedback'/name).read_bytes()).hexdigest()==h)
summary=dict(checks=len(checks),failed=sum(not c['pass_'] for c in checks),lower=str(L),opacity_threshold=str(1/(2*mp.e)),P_universal_gap_fraction=str(1-mp.mpf('.353911')/L),frequency005_universal_gap_fraction=str(1-mp.mpf('.372404')/L),checks_detail=checks)
(ROOT/'CORE_QA.json').write_text(json.dumps(summary,indent=2));print(json.dumps({k:v for k,v in summary.items() if k!='checks_detail'},indent=2))
