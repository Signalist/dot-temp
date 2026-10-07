"""Score retained output records; writes diagnostics, never runs model code."""
import argparse,hashlib,json,pathlib
from validator import score
ROOT=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('input_jsonl');p.add_argument('--out',required=True);a=p.parse_args()
freeze=json.loads((ROOT/'BENCHMARK_FREEZE.json').read_text())
assert hashlib.sha256((ROOT/'benchmark.json').read_bytes()).hexdigest()==freeze['benchmark_sha256'],'Pool hash mismatch'
tasks={t['id']:t for t in json.loads((ROOT/'benchmark.json').read_text())['tasks']};rows=[]
for i,line in enumerate(pathlib.Path(a.input_jsonl).read_text().splitlines(),1):
    r=json.loads(line)
    if r['task_id'] not in tasks:raise ValueError('Unknown task on line '+str(i))
    rows.append({'task_id':r['task_id'],'run_id':r.get('run_id'),'family':tasks[r['task_id']]['family'],'split':tasks[r['task_id']]['split'],'synthetic_fixture':r.get('synthetic_fixture',False),**score(tasks[r['task_id']],r['output_text'],r.get('terminal'))})
for r in rows:
    r['validation_gate_eligible']=r.pop('eligible_quality_matched_claim')
    r['model_evidence_eligible']=False
    r['reason_claim_not_assessed']='Record-level diagnostics only: expected-denominator, identity, frozen protocol, provenance and quality matching not checked'
pathlib.Path(a.out).write_text(json.dumps({'report_scope':'RECORD_LEVEL_DIAGNOSTICS_NOT_EXPERIMENT_CLAIM','pool_sha256':freeze['benchmark_sha256'],'records':rows,'note':'Synthetic fixtures do not establish model quality. Writing needs blinded human review. Unsupported code is unknown, never silently dropped.'},indent=2)+'\n')
print(json.dumps({'records':len(rows),'out':a.out}))
