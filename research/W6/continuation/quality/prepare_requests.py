"""Compile frozen inference requests only. No GPU, network, model import or launch."""
import argparse,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--split',choices=['development','calibration','heldout'],default='development');p.add_argument('--phase',choices=['Q_quality','R_paired'],default='Q_quality');p.add_argument('--freeze-id',default='');p.add_argument('--out',required=True);args=p.parse_args()
raw=(ROOT/'benchmark.json').read_bytes();pool=json.loads(raw);freeze=json.loads((ROOT/'BENCHMARK_FREEZE.json').read_text())
assert hashlib.sha256(raw).hexdigest()==freeze['benchmark_sha256'],'Pool changed; preregistration must be revised'
if args.split=='heldout' and (args.phase!='R_paired' or not args.freeze_id):p.error('Heldout is reserved for the frozen paired phase: use R_paired and an actual reviewed protocol/candidate freeze id')
rows=[]
for t in pool['tasks']:
    if t['split']!=args.split:continue
    rows.append({'task_id':t['id'],'domain':t['domain'],'source_family_id':t['family'],'split_role':t['split'],'prompt':t['prompt'],'prompt_sha256':hashlib.sha256(t['prompt'].encode()).hexdigest(),'task_contract_sha256':freeze['task_hashes'][t['id']],'pool_sha256':freeze['benchmark_sha256'],'phase':args.phase,'protocol_candidate_freeze_id':args.freeze_id or None,'sampling':{'temperature':0,'seed':17,'ignore_eos':False,'max_tokens':1536,'stop':None},'new_gpu_run':False})
out=pathlib.Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in rows));print(json.dumps({'compiled_requests':len(rows),'path':str(out),'gpu_launched':False}))
