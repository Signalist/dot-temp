"""Independent exact-rational feasibility plus 60-digit objective audit of stored IEEE-node policies."""
import json,hashlib
from pathlib import Path
from fractions import Fraction
import mpmath as mp
mp.mp.dps=60
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'results/SAFE_PRIMARY_PATHS.json').read_text())
raw=json.loads((ROOT/'results/PRIMARY_MESHES.json').read_text())
matched=json.loads((ROOT/'results/MATCHED_CYCLE_FRONTIER.json').read_text())
F=Fraction;Q=lambda x:mp.mpf(str(x))
def moment(a,b,q):
 if a==b:return a**q,a**q/2
 I=(b**(q+1)-a**(q+1))/((q+1)*(b-a));U=((b**(q+2)-a**(q+2))/((q+2)*(b-a))-a*I)/(b-a)
 return I,U
out={'node_contract':'Saved JSON numbers decoded to IEEE binary64, each such value then interpreted as an exact rational coefficient; beta,R,c interpreted as exact printed decimals.','costs_outward_rounded':False,'checks':[]}
for row,match in zip(rows,matched):
 c=row['case'];n=row['N'];z=[F(float(v)) for v in row['z']];R=F(str(c['R']));b=F(str(c['beta']));ct=F(str(c['c']));K=1+b;pc=b*ct/(1-b)
 slopes=[n*(z[i+1]-z[i]) for i in range(n)];constraints={'initial_zero':z[0]==0,'terminal_zero':z[-1]==0,'positive_interior':all(v>0 for v in z[1:-1]),'slew':max(abs(v) for v in slopes)<=R,'startup':all(v<=R*F(i,n) for i,v in enumerate(z)),'recovery':all(v<=R*F(n-i,n) for i,v in enumerate(z)),'critical':all((K*v)**b.denominator<=pc**(b.numerator+b.denominator) for v in z)}
 exact=lambda v:mp.mpf(v.numerator)/v.denominator
 zz=list(map(exact,z));bm=exact(b);Rm=exact(R);Km=1+bm;cm=exact(ct);vals=[mp.mpf(0)]*4;worstT=mp.mpf(0)
 for i in range(n):
  dx=mp.mpf(1)/n;x=mp.mpf(i)/n
  for j,q in enumerate([(1-bm)/Km,-bm/Km,2/Km,1/Km]):
   I,U=moment(zz[i],zz[i+1],q);coef=Km**q
   if j==2:coef/=2*Rm
   if j==3:coef/=Rm
   vals[j]+=coef*dx*((1-x)*I-dx*U if j<2 else I)
   if j==1:worstT+=coef*dx*I
 E=vals[0]+vals[2];T=vals[1]+vals[3];J=E+cm*T
 actual={'dynamic_energy':float(E),'task_time':float(vals[1]),'recovery_time':float(vals[3]),'cycle_time':float(T),'objective':float(J)}
 diff=max(abs(actual[k]-row['parts'][k]) for k in actual)
 old=next(r for r in raw if r['N']==n and r['case']==c);ratioerr=max(abs(v-(1-1e-7)*a) for v,a in zip(row['z'],old['z']))
 out['checks'].append({'case':c,'all_exact_constraints_pass':all(constraints.values()),'constraints':constraints,'exact_minimum_slew_margin':str(min(R-abs(v) for v in slopes)),'minimum_slew_margin_float':float(min(R-abs(v) for v in slopes)),'objective_recomputed':float(J),'max_component_difference':diff,'worst_duration_difference':float(worstT)-row['worst_supported_cycle_time_numerical'],'relative_dual_gap_recomputed':(float(J)-row['continuous_dual_numerical'])/float(J),'scaling_expression_difference':ratioerr,'matched_frontier_uses_safe_values':match['proposed_cycle_time']==row['parts']['cycle_time'] and match['proposed_dynamic_energy']==row['parts']['dynamic_energy']})
assert all(r['all_exact_constraints_pass'] and r['matched_frontier_uses_safe_values'] for r in out['checks'])
out['summary']={'all_exact_constraints_pass':True,'min_exact_slew_margin':min(r['minimum_slew_margin_float'] for r in out['checks']),'max_component_difference':max(r['max_component_difference'] for r in out['checks']),'max_worst_duration_difference':max(abs(r['worst_duration_difference']) for r in out['checks']),'relative_gap_min':min(r['relative_dual_gap_recomputed'] for r in out['checks']),'relative_gap_max':max(r['relative_dual_gap_recomputed'] for r in out['checks'])}
out['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'results/SAFE_PRIMARY_PATHS.json',ROOT/'results/MATCHED_CYCLE_FRONTIER.json',ROOT/'code/inward_feasible_paths.py',ROOT/'code/matched_cycle_frontier.py']}
(ROOT/'audit/SAFE_INNER_POLICY_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['summary'],indent=2))
