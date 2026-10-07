"""Additional exactly feasible rational stored-node policies, preserving raw solver outputs.
Only linear constraints/critical cap are rationally proved. Costs remain floating evaluations.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,numpy as np
from cycle_model import Case,Mesh,reconstruct
ROOT=Path(__file__).resolve().parents[1]
raw=[r for r in json.load(open(ROOT/'results/PRIMARY_MESHES.json')) if r['N']==128];duals=json.load(open(ROOT/'results/CONTINUOUS_DUAL.json'));out=[]
for r,d in zip(raw,duals):
 c=Case(**r['case']);N=r['N'];z=np.array(r['z'])*(1-1e-7);parts=Mesh(c,N,96).evaluate(z,parts=True)
 zz=[Q.from_float(float(v)) for v in z];R=Q(str(c.R));beta=Q(str(c.beta));cw=Q(str(c.c));K=1+beta;pc=beta*cw/(1-beta)
 slew=all(abs(N*(b-a))<=R for a,b in zip(zz[:-1],zz[1:]));recovery=all(v<=R*(1-Q(i,N)) for i,v in enumerate(zz));start=all(v<=R*Q(i,N) for i,v in enumerate(zz));positive=all(v>0 for v in zz[1:-1])
 critical=all((K*v)**beta.denominator<=pc**(beta.numerator+beta.denominator) for v in zz)
 endpoints=zz[0]==zz[-1]==0
 gap=parts['objective']-d['continuous_dual_numerical'];margin=min(float(R-abs(N*(b-a))) for a,b in zip(zz[:-1],zz[1:]))
 out.append({'case':r['case'],'N':N,'z':z.tolist(),'parts':parts,'raw_to_inner_objective_change':parts['objective']-r['parts']['objective'],'continuous_dual_numerical':d['continuous_dual_numerical'],'relative_gap':gap/parts['objective'],'exact_rational_checks':{'slew':slew,'recovery_cone':recovery,'startup_cone':start,'critical_cap':critical,'endpoints':endpoints,'positive_interior':positive},'minimum_slew_margin':margin,'worst_supported_cycle_time_numerical':reconstruct(c,z,1.)['cycle_time'],'objective_directed_rounding':False})
assert all(all(r['exact_rational_checks'].values()) for r in out)
(ROOT/'results/SAFE_PRIMARY_PATHS.json').write_text(json.dumps(out,indent=2));print('all exact rational checks PASS; minimum margin',min(r['minimum_slew_margin'] for r in out));print('safe gap range',min(r['relative_gap'] for r in out),max(r['relative_gap'] for r in out))
