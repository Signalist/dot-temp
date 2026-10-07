from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime,timezone
import sys,json
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import diags,vstack
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
from slew_support import Swing
rows=json.loads((ROOT/'results/SLEW_SUPPORT_RESULTS.json').read_text());checks=[]
for row in rows:
 model=Swing(**row['model']);hz=model.mode_hz;z=model.zeta;P=row['pcap'];R=row['R'];requested=min([.05,.025,.0125],key=lambda x:abs(x-row['dt']))
 name=f'support_f{hz}_z{z}_cap{P}_R{R}_dt{requested}.npz';d=np.load(ROOT/'results'/name);t=d['lag_time'];v=d['lag_power'];tt=list(map(lambda x:Q(float(x)),t));vv=list(map(lambda x:Q(float(x)),v));rr=Q(float(R));pp=Q(float(P));rdecimal=Q(str(R));pdecimal=Q(str(P))
 positive_dt=all(tt[i+1]>tt[i] for i in range(len(t)-1))
 exact_ieee=positive_dt and all(abs(vv[i+1]-vv[i])<=rr*(tt[i+1]-tt[i]) for i in range(len(t)-1)) and all(Q(0)<=x<=pp for x in vv)
 exact_decimal=positive_dt and all(abs(vv[i+1]-vv[i])<=rdecimal*(tt[i+1]-tt[i]) for i in range(len(t)-1)) and all(Q(0)<=x<=pdecimal for x in vv)
 w=model.hats(t);value=row['sign']*w@v;lower=max(0,value-row['tail_remainder']);upper=min(row['amplitude_only_bound'],row['slew_only_bound'],row['LP_dual_weak_upper']+row['tail_remainder']+row['interpolation_remainder'])
 rec={'file':name,'exact_serialized_ieee_constraints_pass':exact_ieee,'exact_decimal_parameter_constraints_pass':exact_decimal,'all_time_steps_positive':positive_dt,'selected_objective_error':float(abs(value-row['LP_support'])),'lower_reconstruction_error':float(abs(lower-row['support_lower'])),'upper_reconstruction_error':float(abs(upper-row['support_upper'])),'pre_repair_artifact_retained':(ROOT/'results/pre_inward_repair'/name).exists(),'raw_to_repaired_objective_change':row['raw_LP_support']-row['LP_support']}
 if len(checks)==0:
  n=len(t)-1;D=diags([-np.ones(n),np.ones(n)],[0,1],shape=(n,n+1),format='csr');A=vstack([D,-D]);rhs=np.r_[R*np.diff(t),R*np.diff(t)];branches=[]
  # Independent LP run only for this one selected case, then independent exact
  # rational weak-dual evaluation for the represented coefficients.
  for sign in [-1,1]:
   result=linprog(-sign*w,A_ub=A,b_ub=rhs,bounds=(0,P),method='highs');assert result.success
   y=np.maximum(0,-result.ineqlin.marginals);floating=float(y@rhs+P*np.maximum(sign*w-A.T@y,0).sum())
   yp=list(map(lambda x:Q(float(x)),y[:n]));yn=list(map(lambda x:Q(float(x)),y[n:]));wc=[sign*Q(float(x)) for x in w]
   residual=wc[:];rb=Q(0)
   for i in range(n):
    u=yp[i]-yn[i];residual[i]+=u;residual[i+1]-=u
    rb+=(yp[i]+yn[i])*rr*(tt[i+1]-tt[i])
   exact_upper=rb+pp*sum(max(Q(0),v) for v in residual)
   branches.append({'sign':sign,'raw_primal_support':float(-result.fun),'floating_weak_upper':floating,'exact_represented_coefficients_weak_upper':float(exact_upper),'float_minus_rational_upper':float(Q(floating)-exact_upper),'nonnegative_multipliers':bool(np.all(y>=0))})
  rec['independent_dual_branches']=branches;rec['independent_dual_max_error']=abs(max(b['floating_weak_upper'] for b in branches)-row['LP_dual_weak_upper'])
 checks.append(rec)
repair={'reviewed_utc':datetime.now(timezone.utc).isoformat(),'status':'repair accepted; exact serialized witness feasibility verified, weak-dual formula sound; kernels/weights/upper sums still ordinary float','checks':checks,'summary':{'all_12_exact_ieee_pass':all(q['exact_serialized_ieee_constraints_pass'] for q in checks),'all_12_exact_decimal_parameters_pass':all(q['exact_decimal_parameter_constraints_pass'] for q in checks),'all_12_pre_repair_paths_retained':all(q['pre_repair_artifact_retained'] for q in checks),'maximum_repaired_objective_check_error':max(q['selected_objective_error'] for q in checks),'one_case_dual_reproduction_error':checks[0]['independent_dual_max_error']},'weak_dual_reason':'For every y>=0 and feasible 0<=v<=P, Av<=b: c^T v <=y^T b+P sum(max(c-A^T y,0)). This does not require exact stationarity or an optimal dual. Evaluate both signs and take max.','qualification':'Exact rational witness feasibility does not turn transcendental kernel weights, cost evaluation or floating weak-dual sums into an interval certificate.'}
p=ROOT/'review/SLEW_SUPPORT_REVIEW.json';previous=json.loads(p.read_text());previous.setdefault('repair_reviews',[]).append(repair);p.write_text(json.dumps(previous,indent=2)+'\n');print(json.dumps(repair['summary'],indent=2));print(json.dumps(checks[0]['independent_dual_branches'],indent=2))
