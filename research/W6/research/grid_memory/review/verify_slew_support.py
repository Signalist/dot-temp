"""Independent analytic-hat and one-LP check, using Gaussian interval quadrature."""
from pathlib import Path
import sys,json,subprocess
from datetime import datetime,timezone
import numpy as np
from scipy.special import roots_legendre
from scipy.optimize import linprog
from scipy.sparse import diags,vstack
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
from slew_support import Swing
rows=json.loads((ROOT/'results/SLEW_SUPPORT_RESULTS.json').read_text())
checks=[]
for row in rows:
 model=Swing(**row['model']);hz=model.mode_hz;z=model.zeta;cap=row['pcap'];R=row['R']
 # Filenames carry requested dt, while the JSON carries its uniform-grid adjusted value.
 requested=min([.05,.025,.0125],key=lambda x:abs(x-row['dt']))
 p=ROOT/f'results/support_f{hz}_z{z}_cap{cap}_R{R}_dt{requested}.npz'
 d=np.load(p);t=d['lag_time'];v=d['lag_power'];w=model.hats(t);h=np.diff(t)
 nodes,weights=roots_legendre(12);local=(nodes+1)/2;tt=t[:-1,None]+h[:,None]*local
 f=model.impulse(tt);ints=h[:,None]/2*weights*f
 wg=np.zeros(len(t));wg[:-1]+=(ints*(1-local)).sum(axis=1);wg[1:]+=(ints*local).sum(axis=1)
 observed=row['sign']*wg@v
 record={'mode_hz':hz,'zeta':z,'cap':cap,'R':R,'requested_dt':requested,'max_hat_weight_error':float(max(abs(w-wg))),'gauss_recomputed_selected_objective':float(observed),'recorded_LP_support':row['LP_support'],'objective_difference':float(abs(observed-row['LP_support'])),'actual_slew_excess':float(max(0,max(abs(np.diff(v))/h)-R)),'cap_excess':float(max(0,max(v)-cap)),'lower_bound_recomputed':float(max(0,observed-row['tail_remainder'])),'upper_bound_recomputed':float(min(cap*model.area(),R*model.slew_norm(),row['LP_dual_weak_upper']+row['tail_remainder']+row['interpolation_remainder']))}
 if len(checks)==0:
  N=len(t)-1;dd=diags([-np.ones(N),np.ones(N)],[0,1],shape=(N,N+1),format='csr');A=vstack([dd,-dd]);rhs=np.r_[R*h,R*h]
  vals=[]
  for sign in [-1,1]:
   res=linprog(-sign*wg,A_ub=A,b_ub=rhs,bounds=(0,cap),method='highs');assert res.success;vals.append(float(-res.fun))
  record['independent_LP_support']=max(vals);record['independent_LP_error']=abs(max(vals)-row['raw_LP_support'])
 record['upper_reconstruction_error']=abs(record['upper_bound_recomputed']-row['support_upper'])
 record['lower_reconstruction_error']=abs(record['lower_bound_recomputed']-row['support_lower'])
 record['upper_source']='row LP_dual_weak_upper + tail + interpolation, intersected with analytic amplitude/slew guards'
 record['independent_LP_comparison_source']='raw_LP_support, not inward-scaled feasible-witness objective'
 checks.append(record)
out={'status':'ordinary-float independent checks; no outward-rounded or machine interval certificate','method':'12-node Gauss-Legendre interval integrals independently produce nodal hats; one LP solved with those weights; all archived optimizer paths checked','checks':checks,'summary':{'max_hat_weight_error':max(q['max_hat_weight_error'] for q in checks),'max_selected_objective_error':max(q['objective_difference'] for q in checks),'max_slew_excess':max(q['actual_slew_excess'] for q in checks),'max_cap_excess':max(q['cap_excess'] for q in checks),'independent_one_LP_error':checks[0]['independent_LP_error']}}
out['review_version']='repaired_witness_and_weak_dual_v2'
out['reviewed_utc']=datetime.now(timezone.utc).isoformat()
out['exact_constraint_and_dual_audit']='verify_slew_support_repair.py, invoked automatically below'
path=ROOT/'review/SLEW_SUPPORT_REVIEW.json'
previous=json.loads(path.read_text()) if path.exists() else {}
if previous and previous.get('review_version') != out['review_version']:
    historic={key:previous[key] for key in ('status','method','checks','summary') if key in previous}
    previous.setdefault('historical_reviews',[]).append({'label':'pre-repair review; superseded for current witnesses, retained as evidence', 'review':historic})
combined={**previous,**out}
path.write_text(json.dumps(combined,indent=2)+'\n')
print(json.dumps(out['summary'],indent=2))
# Keep exact Fraction feasibility and an independently rerun weak-dual branch
# review in the default standalone reproduction, without erasing past findings.
subprocess.run([sys.executable,str(ROOT/'review/verify_slew_support_repair.py')],check=True)

