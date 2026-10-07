#!/usr/bin/env python3
"""Regression gates on retained scientific claims, using only the standard library."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];R2=ROOT/'evidence/round2_g6_joint_admission_20261003';R3=ROOT/'evidence/round3_g6_20261004'
a=json.loads((R2/'nonlinear/wecc_dynamic_optional_inner_dt128.json').read_text())
peak=a['metrics']['nonlinear_peak_any_generator_Hz']
assert abs(peak-0.0530995503416376)<1e-14 and peak>0.05
b=json.loads((R3/'experiments/JOB_DAG_REALIZATION.json').read_text())
assert b['checks_count']==128 and b['all_checks_pass']
assert b['counterexample']['plus_feasible'] and not b['counterexample']['minus_feasible']
c=json.loads((R3/'experiments/EXACT_RATIONAL_PARAMETER_CERTIFICATE.json').read_text())
assert c['N']==512 and c['r']=='17/20'
r=c['rows'][-1]
assert r['intervals']==128 and float(r['prefix_lower'])>2.862363672458 and float(r['robust_upper'])<2.862589894265
print(json.dumps({'pass':True,'retained_WECC_violation_Hz':peak,'DAG_checks':128,'rational_certificate_grid':128,'scope':'archived scientific regression assertions; no new physical test'}))
