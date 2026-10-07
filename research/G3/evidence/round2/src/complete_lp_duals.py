"""Complete independently replayable floating LP dual records; not interval certificates."""
from pathlib import Path
import numpy as np,json
from scipy.optimize import linprog
root=Path(__file__).resolve().parents[1]; rows=[]
for file in list((root/'results').glob('exact_*.npz'))+list((root/'results'/'switch_corridor').glob('exact_*.npz')):
 z=dict(np.load(file));t=z['t'];N=len(t)-1;par=json.loads(str(z['par_json']));V=z['lp_A'].shape[1];sidx=2*(N+1)
 bounds=[(-par['bmax'],par['bmax'])]*(N+1)+[(par['B0']-par['Bmax'],par['B0']-par['Bmin'])]*(N+1)+[(-1000,None)]+[(0,par['bmax'])]*(N+1)+[(0,2*par['bmax'])]*N
 for j in np.where(t<=par['delay']+1e-12)[0]:bounds[j]=(0,0);bounds[N+1+j]=(0,0)
 bounds[N]=(0,0);bounds[2*N+1]=(0,0)
 obj=np.zeros(V);obj[sidx]=-1
 rr=linprog(obj,A_ub=z['lp_A'],b_ub=z['lp_rhs'],bounds=bounds,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
 if not rr.success:rows.append(dict(file=str(file.relative_to(root)),status=rr.message));continue
 lam=np.minimum(rr.ineqlin.marginals,0);dl=np.maximum(rr.lower.marginals,0);du=np.minimum(rr.upper.marginals,0)
 lo=np.array([b[0] if b[0] is not None else 0 for b in bounds]); hi=np.array([b[1] if b[1] is not None else 0 for b in bounds]);
 residual=obj-z['lp_A'].T@lam-dl-du
 # Sigma upper bound follows the first-state W_lower row; use full range <=1000.
 magnitude=np.maximum(abs(lo),abs(hi));magnitude[sidx]=1000.
 correction=float(abs(residual)@magnitude)
 dual=float(lam@z['lp_rhs']+dl@lo+du@hi)
 record=dict(file=str(file.relative_to(root)),margin_primary=float(rr.x[sidx]),dual_upper_bound_with_stationarity_correction=float(-dual+correction),stationarity_Linf=float(max(abs(residual))),correction_kJ=correction,duality_gap=float(abs(rr.fun-dual)),max_primal_violation=float(max(0,np.max(z['lp_A']@rr.x-z['lp_rhs']))),exclusion=bool(-dual+correction < -1e-5),caveat='Floating supporting-plane coefficients, not interval-arithmetic formal certification')
 z.update(lp_primary_x=rr.x,lp_objective=obj,lp_primary_fun=rr.fun,lp_lower_duals=dl,lp_upper_duals=du,lp_complete_duals=lam,lp_bounds=np.array([[np.nan if b is None else b for b in bb] for bb in bounds]),lp_dual_record=json.dumps(record))
 np.savez_compressed(file,**z);rows.append(record)
(root/'results'/'LP_DUAL_COMPLETION.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
