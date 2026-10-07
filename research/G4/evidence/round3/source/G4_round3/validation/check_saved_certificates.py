#!/usr/bin/env python3
"""Read-only exact saved-certificate check; does not invoke optimization."""
import json,sys,hashlib
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from run_workload_study import dag_data,matrices
BASE=Path(__file__).resolve().parents[1]
rows=json.loads((BASE/'experiments/dag_results.json').read_text())
boundary=json.loads((BASE/'experiments/boundary_results.json').read_text())
rows+=boundary['public_pattern_transfer']
checks=[]
for row in rows:
 pats,*_=dag_data(row['labels'],row['edges']);c,A,b,E,f,bounds=matrices(pats,row['eta']);rat=lambda v:F(float(v)).limit_denominator(10**7)
 c=list(map(rat,c));A=[[rat(t) for t in aa] for aa in A];b=list(map(rat,b));E=[[rat(t) for t in aa] for aa in E];f=list(map(rat,f));cert=row['exact_certificate'];x=list(map(F,cert['x_fraction']));dot=lambda a,b:sum((aa*bb for aa,bb in zip(a,b)),F(0))
 dual={k:{i:F(v) for i,v in vals} for k,vals in cert['dual_nonzero'].items()};get=lambda k,i:dual[k].get(i,F(0))
 primal=all(dot(a,x)<=bb for a,bb in zip(A,b)) and all(dot(a,x)==bb for a,bb in zip(E,f))
 primal &= all((lo is None or xx>=rat(lo)) and (up is None or xx<=rat(up)) for xx,(lo,up) in zip(x,bounds))
 signs=all(y<=0 for y in dual['ineq'].values()) and all(y>=0 for y in dual['lower'].values()) and all(y<=0 for y in dual['upper'].values())
 equal=all(sum((aa[j]*get('ineq',i) for i,aa in enumerate(A)),F(0))+sum((aa[j]*get('eq',i) for i,aa in enumerate(E)),F(0))+get('lower',j)+get('upper',j)==c[j] for j in range(len(c)))
 objective=sum((bb*get('ineq',i) for i,bb in enumerate(b)),F(0))+sum((bb*get('eq',i) for i,bb in enumerate(f)),F(0))
 for j,(lo,up) in enumerate(bounds):
  if lo is not None:objective+=rat(lo)*get('lower',j)
  else:assert get('lower',j)==0
  if up is not None:objective+=rat(up)*get('upper',j)
  else:assert get('upper',j)==0
 checks.append({'name':row['name'],'eta':row['eta'],'primal':primal,'dual':signs and equal,'zero_gap':objective==dot(c,x)})
old=BASE.parent/'round2_g4_identifiability_20261003';manifest=json.loads((old/'SCIENCE_MANIFEST.json').read_text());mismatch=[]
for record in manifest['files']:
 p=old/record['path']
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=record['sha256']:mismatch.append(record['path'])
result={'optimization_invoked':False,'cases':len(checks),'all_pass':all(z['primal'] and z['dual'] and z['zero_gap'] for z in checks),'checks':checks,'old_manifest_files_checked':len(manifest['files']),'old_manifest_mismatches':mismatch}
(BASE/'validation/SAVED_CERTIFICATE_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='checks'});assert result['all_pass'];assert not mismatch
