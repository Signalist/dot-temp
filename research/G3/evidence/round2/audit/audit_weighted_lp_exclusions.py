"""Bound the LP objective from saved nonnegative inequality combinations.
No trust in solver primal objective or stationarity: residual physical-variable
coefficients are bounded over their finite boxes. Auxiliary coefficients must
be nonnegative (auxiliaries have lower bound zero). This proves a bound for the
saved finite LP; analytic tangent validity still carries normal FP caveats.
"""
from pathlib import Path
import json,math,numpy as np
from decimal import Decimal,localcontext
ROOT=Path(__file__).resolve().parents[1]
files=sorted((ROOT/'results').glob('exact_a*.npz'))+sorted((ROOT/'results/switch_corridor').glob('exact_*.npz'))
rows=[]
for path in files:
 z=np.load(path);p=json.loads(str(z['par_json']));t=z['t'];n=len(t);s=2*n
 lam=np.maximum(0,-z['lp_duals']);A=z['lp_A'][:len(lam)];rhs=z['lp_rhs'][:len(lam)]
 lo=np.r_[np.full(n,-p['bmax']),np.full(n,p['B0']-p['Bmax'])];hi=np.r_[np.full(n,p['bmax']),np.full(n,p['B0']-p['Bmin'])]
 for j in np.where(t<=p['delay']+1e-12)[0]:lo[j]=hi[j]=lo[n+j]=hi[n+j]=0
 lo[n-1]=hi[n-1]=lo[s-1]=hi[s-1]=0
 # Decimal high-precision recombination of the exact stored double constants.
 with localcontext() as ctx:
  ctx.prec=75;agg=[Decimal(0) for _ in range(A.shape[1])];right=Decimal(0)
  for row,weight,r in zip(A,lam,rhs):
   if weight==0:continue
   ww=Decimal.from_float(float(weight));right+=ww*Decimal.from_float(float(r))
   for j in np.flatnonzero(row):agg[j]+=ww*Decimal.from_float(float(row[j]))
  auxok=all(a>=0 for a in agg[s+1:]);leftmin=sum((agg[j]*Decimal.from_float(float(lo[j] if agg[j]>=0 else hi[j])) for j in range(s)),Decimal(0))
  ub=(right-leftmin)/agg[s] if auxok and agg[s]>0 else None
  rows.append({'file':str(path.relative_to(ROOT)),'nonzero_weights':int(np.sum(lam>0)),'sigma_coefficient':str(agg[s]),'auxiliary_nonnegative':auxok,'max_abs_auxiliary_coefficient':str(max(abs(v) for v in agg[s+1:])),'weighted_upper_sigma_kJ':None if ub is None else float(ub),'weighted_upper_sigma_decimal':None if ub is None else str(ub),'saved_primal_sigma_kJ':float(z['lp_x'][s]),'bound_excludes':bool(ub is not None and ub<Decimal('-0.00001')),'floating_tangent_physical_caveat':'This is an independent weighted bound on the saved linear inequalities, not directed-interval certification of the nonlinear support-oracle arithmetic.'})
out={'method':'Nonnegative inequality sum, positive sigma coefficient, and explicit finite b/C box residual correction. High-precision recombination uses stored binary64 constants. This does not depend on primal feasibility, optimality status or exact stationarity.','rows':rows,'files_checked':len(rows),'excluded_count':sum(r['bound_excludes'] for r in rows),'failed_aggregate_certificates':[r['file'] for r in rows if not r['auxiliary_nonnegative'] or r['weighted_upper_sigma_kJ'] is None]}
(ROOT/'audit/WEIGHTED_LP_BOUNDS.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['rows','method']},indent=2))
