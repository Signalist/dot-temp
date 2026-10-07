"""One-time continuation; full standalone regeneration lives in trace_driven.py."""
from pathlib import Path
import json,gzip,hashlib,time,csv
import numpy as np
from cycle_model import Case
from atomic_bellman import dp,physical,segments
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'results/TRACE_DRIVEN_GLOBAL.json';raw=p.read_bytes();rows=json.loads(raw)
archive=ROOT/'evidence/TRACE_FULL_REPEATED_LEDGERS_1024.json.gz'
with gzip.open(archive,'wb',compresslevel=6) as f:f.write(raw)
(ROOT/'evidence/TRACE_COMPACTION.json').write_text(json.dumps({'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),'gzip_path':str(archive.relative_to(ROOT)),'scope':'Identical per-EOS segment prefixes represented once as shared bridges in final output; all per-EOS totals retained'},indent=2))
for row in rows:
 for v in row.get('physical',{}).get('paths',[]):v.pop('segments',None)
p.write_text(json.dumps(rows,indent=2))
data=list(csv.DictReader(open(ROOT/'literature/data_candidate/empirical_output_length_pmf.csv')));work=np.array([int(r['generated_tokens'])/1000 for r in data]);prob=np.array([float(r['probability']) for r in data]);prob/=prob.sum()
for row in rows:
 c=Case(**row['case']);st=time.perf_counter();lower,_=dp(c,work,prob,2048,True);upper,z=dp(c,work,prob,2048,False)
 row['refinements'].append({'n':2048,'lower':lower,'upper':upper,'relative_gap':(upper-lower)/upper,'seconds':time.perf_counter()-st,'z':z})
 row['physical']=physical(c,work.tolist(),prob.tolist(),z)
 for path in row['physical']['paths']:path.pop('segments')
 row['shared_bridge_segments']=segments(c,work,z);row['ledger_gap']=abs(row['physical']['mean_objective']-upper)
 p.write_text(json.dumps(rows,indent=2));print(c,lower,upper,(upper-lower)/upper,row['ledger_gap'],flush=True)
