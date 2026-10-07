from pathlib import Path
import json,hashlib,math
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1];checks=[]
def add(name,ok,detail=None):checks.append({'name':name,'pass':bool(ok),'detail':detail})
def read(name):return json.loads((ROOT/name).read_text())
p=read('results/outward_prefix_certificates.json')
for r in p:add('strict_outer_'+r['beta_kvar'],r['strict_exclusion'] and Decimal(r['gap_interval_kV_s'][0])>0 and r['lambda']=='0')
i=read('results/outward_zoh_inner.json')
for key,bnd in i['all_time_interval_lower_bounds'].items():add('inner_'+key,Decimal(bnd[0])>0)
for key in ['terminal_b_interval_kW','terminal_C_interval_kJ','total_net_grid_minus_load_interval_kJ']:
 a,b=map(Decimal,i[key]);add(key,a<=0<=b and max(abs(a),abs(b))<Decimal('1e-30'))
pay=read('results/zoh_q808_exact_payload.json');add('complete_payload',len(pay['times_decimal'])==3201 and len(pay['base_commands_decimal_kW'])==3200)
z=read('results/zoh_inner_results.json');add('failed_grids_retained',[r['critical_hold_us'] for r in z if not r['feasible_with_margin']]==[50,100])
ledger=read('results/same_workload_energy_ledger.json')
for r in ledger['windows']:
 add('signed_ledger_'+r['window'],abs(r['energy_closure_residual_J'])<1e-7)
 add('positive_absolute_identity_'+r['window'],abs(r['absolute_AC_increment_J']-(2*r['positive_AC_increment_J']-r['signed_AC_increment_J']))<1e-6)
 add('full_states_'+r['window'],all(k in r['states_at_start'] and k in r['states_at_end'] for k in ['W_S_kJ','W_L_kJ','B_S_kJ','B_L_kJ','Z_S_kJ','Z_L_kJ']))
add('common_task130kJ',next(r['common_workload_J'] for r in ledger['windows'] if r['window']=='whole_task')==130000)
add('matched_baseline_physical',read('results/outward_matched_baseline.json')['pass'])
comp=read('results/mature_socp_comparator.json');add('mature_baseline_reproduced',abs(comp['margin_kJ']-.0071382825773217765)<1e-10)
rev=read('review/exact_zoh_certificate_audit.json')
for k in ['all_decimal_exports_outward','event_alignment','strictly_increasing_grid','queue_command_exactly_zero','grid_critical_holds_correct','grid_later_holds_correct','exact_payload_matches_parent','strict_all_constraints_pass']:add('review_'+k,rev[k])
add('profile9603',read('review/profile_rational_audit.json')['all_enclose_exact_rational_time_reference'] and read('review/profile_rational_audit.json')['comparisons']==9603)
add('outer_export_audit',read('review/interval_export_audit.json')['all_decimal_exports_outward'])
freeze=read('HISTORICAL_SOURCE_FREEZE.json')['files'];base=ROOT.parents[1];exists=all((base/k).is_file() for k in freeze)
preservation={'available':exists,'count':len(freeze),'changed':[]}
if exists:
 for name,rec in freeze.items():
  if hashlib.sha256((base/name).read_bytes()).hexdigest()!=rec['sha256']:preservation['changed'].append(name)
 add('historical_sources_unchanged',not preservation['changed'])
# Copied prior source provenance remains exact when the historical sibling exists.
old=ROOT.parent/'round2_g3_port_20261003'
if old.exists():
 for f in (ROOT/'prior_core').rglob('*'):
  if f.is_file() and '__pycache__' not in f.parts:
   rel=f.relative_to(ROOT/'prior_core');add('prior_copy_'+str(rel),f.read_bytes()==(old/rel).read_bytes())
for f in ROOT.rglob('*.json'):
 if '__pycache__' not in f.parts:
  try:json.loads(f.read_text());ok=True
  except Exception:ok=False
  add('json_readable_'+str(f.relative_to(ROOT)),ok)
out={'all_pass':all(x['pass'] for x in checks),'check_count':len(checks),'checks':checks,'historical_preservation':preservation,'independent_checks_are_not_sample_size':True}
(ROOT/'QA.json').write_text(json.dumps(out,indent=2));print(json.dumps({'all_pass':out['all_pass'],'check_count':len(checks),'historical_preservation':preservation},indent=2))
if not out['all_pass']:raise SystemExit(1)
