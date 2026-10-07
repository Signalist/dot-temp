from pathlib import Path
import json
from cycle_model import Case
from global_bellman import bellman
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for r in json.load(open(ROOT/'results/NONZERO_INITIAL.json')):
 c=Case(**r['case']);free=r['label']=='prepaid_all';b=bellman(c,144,4,recovery=not free,critical=not free)
 row={'case':r['case'],'label':r['label'],'convex_or_exact_cost':r['precise_parts']['objective'],'bellman':b,'bellman_excess':b['objective']-r['precise_parts']['objective']};rows.append(row)
 (ROOT/'results/NONZERO_GLOBAL_COMPARISON.json').write_text(json.dumps(rows,indent=2));print(r['label'],row['bellman_excess'],flush=True)
