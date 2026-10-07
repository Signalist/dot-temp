from pathlib import Path
import json
import matched_support_baselines as m
p=Path(__file__).resolve().parent;x=json.loads((p/'matched_support_results.json').read_text());out=[]
for N in [2,8,32]:
 r=next(r for r in x['rows'] if r['N']==N and r['epsilon']==0);F=m.Functional(N,0);M=2*N+1;e,a,v,_=m.lp(F,M)
 out.append(dict(N=N,arcs=M,free_knot_support=r['continuous_linearized_support']['value'],uniform_support=v,uniform_fraction=v/r['continuous_linearized_support']['value'],exact_nonlinear_endpoint=m.exact_y(N,0,e,a)))
(p/'matched_arc_budget_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
