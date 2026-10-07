#!/usr/bin/env python3
import sys,pathlib,json
import numpy as np
import sympy as S
R=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'experiments'))
from causal_horizon_design import design
out,raw=design(5,initial_fraction=.5,audit=True)
A=raw['A'];rhs=raw['rhs'];eq=raw['Aeq'];res=raw['res'];obj=raw['objective'];bounds=raw['bounds'];nv=len(obj)
rat=lambda x:S.Rational(float(x)).limit_denominator(100000)
cols=[];weights=[];kinds=[];orig=[]
for i,v in enumerate(res.ineqlin.marginals):
 if abs(v)>1e-9:cols.append([rat(x) for x in A.getrow(i).toarray()[0]]);weights.append(rat(rhs[i]));kinds.append('le_nonpositive');orig.append(['ineq',i,float(v)])
for i,v in enumerate(res.eqlin.marginals):
 if abs(v)>1e-9:cols.append([rat(x) for x in eq.getrow(i).toarray()[0]]);weights.append(S.Integer(0));kinds.append('eq_free');orig.append(['eq',i,float(v)])
for field,sign in [('lower','ge_nonnegative'),('upper','le_nonpositive')]:
 for i,v in enumerate(getattr(res,field).marginals):
  if abs(v)>1e-9:
   col=[S.Integer(0)]*nv;col[i]=1;cols.append(col);weights.append(rat(bounds[i][0 if field=='lower' else 1]));kinds.append(sign);orig.append([field,i,float(v)])
Mat=S.Matrix(cols).T;target=S.Matrix([rat(x) for x in obj]);sol=next(iter(S.linsolve((Mat,target))))
free=set().union(*(z.free_symbols for z in sol));assert not free,free
assert Mat*S.Matrix(sol)==target
assert all((v<=0 if kind=='le_nonpositive' else v>=0 if kind=='ge_nonnegative' else True) for v,kind in zip(sol,kinds))
value=sum(v*w for v,w in zip(sol,weights))
cert={'scope':'exact rational LP dual lower bound for common-PCC all-task-order hiding, K5, eta19/20, tau1/2, half initial SOC, R12, p within6..18','dual_stationarity_exact':True,'dual_signs_exact':True,'lower_bound_fraction':str(value),'lower_bound_float':float(value),'strictly_exceeds18_exact':bool(value>18),'margin_above18_fraction':str(value-18),'multipliers':[{'row_kind':x[0],'row_index':x[1],'value':str(v),'bound':str(w)} for x,v,w in zip(orig,sol,weights)],'dimension':nv,'nonzero_multipliers':len(sol),'parent_lp_capacity_float':out['capacity']}
(R/'EXACT_DUAL_K5_CERTIFICATE.json').write_text(json.dumps(cert,indent=2))
print(json.dumps({k:v for k,v in cert.items() if k!='multipliers'},indent=2));assert value>18
