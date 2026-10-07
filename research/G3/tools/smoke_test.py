#!/usr/bin/env python3
"""Small non-mutating source and frozen-result checks; not full reproduction."""
from pathlib import Path
from decimal import Decimal
from fractions import Fraction
import json
ROOT=Path(__file__).resolve().parents[1]
files=sorted(ROOT.rglob('*.py'))
for p in files:
 if '.venv' not in p.parts:compile(p.read_text(),str(p.relative_to(ROOT)),'exec')
checks=[]
def add(name,value):
 assert value,name
 checks.append(name)
R=ROOT/'evidence/round3'
outer=json.loads((R/'results/outward_prefix_certificates.json').read_text())
x=next(x for x in outer if Decimal(x['beta_kvar'])==Decimal('812.5'))
add('812.5_prefix_excluded',x['strict_exclusion'] and x['prefix_only_without_recovery_budget'] and Decimal(x['gap_interval_kV_s'][0])>0)
i=json.loads((R/'results/outward_zoh_inner.json').read_text())
add('808_inner',i['beta_kvar']==808 and i['strict_all_constraints_pass'])
add('strict_all_time_margins',all(Decimal(v[0])>0 for v in i['all_time_interval_lower_bounds'].values()))
p=json.loads((R/'results/zoh_q808_exact_payload.json').read_text())
add('3200_exact_commands',len(p['base_commands_decimal_kW'])==3200 and len(p['times_decimal'])==3201)
add('rational_base',all(Fraction(v).denominator>0 for v in p['base_commands_decimal_kW']))
add('failed_grids_retained',[x['critical_hold_us'] for x in json.loads((R/'results/zoh_inner_results.json').read_text()) if not x['feasible_with_margin']]==[50,100])
print(json.dumps({'python_sources_compiled':len(files),'checks':checks,'all_passed':True},indent=2))
