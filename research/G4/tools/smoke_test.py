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
R=ROOT/'evidence/round3/source/G4_round3'
s=json.loads((R/'FINAL_SCIENTIFIC_STATUS.json').read_text())
x=json.loads((R/'validation/independent_saved_certificate_check.json').read_text())
add('89_saved_exact_checks',x['records_checked']==89 and x['all_passed'])
add('same_information_baseline_equal',s['matched_baseline']['cases']==89 and 'No optimizer advantage' in s['matched_baseline']['advantage'])
y=s['decisive_same_multiset_examples']
add('full_capacity',Fraction(y['full_order_B'])==Fraction(6080,187))
add('DAG_capacity',Fraction(y['connected_DAG_B'])==Fraction(3800,187))
add('barrier_capacity',Fraction(y['barrier_DAG_B'])==Fraction(3040,187))
print(json.dumps({'python_sources_compiled':len(files),'checks':checks,'all_passed':True},indent=2))
