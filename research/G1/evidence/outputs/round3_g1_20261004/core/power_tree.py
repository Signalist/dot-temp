"""Exact continuum-phase robust LP, power sampling with bounded-noise decoding."""
from research_lp import *
import sys
SRC=Path('outputs/round2_20261003/phase_reconnection/causal_phase_tree.py')
# Load original under fresh unique module namespace, never execute main / write frozen folder.
import importlib.util
spec=importlib.util.spec_from_file_location('frozen_r2_tree',SRC);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)

def solve(name='power_delay005',P=.5,dt=.01,dr=.1,delay=.05,H=20.,b=.6):
 assert abs(delay/dt-round(delay/dt))<1e-9 and abs(dr/dt-round(dr/dt))<1e-9, "Observation delivery must align with control cells"
 old.HGLOBAL=H
 n=round(H/dt);ntr=round((5+delay)/dt);nb=round(5/dr);t=np.arange(n+1)*dt
 phases=[(high,j*dr,(j+1)*dr) for high in [True,False] for j in range(nb)]
 ns=len(phases);bs=4*n+3;tr=ns*bs;EI=tr+2*ntr;E0=EI+1;nv=E0+1
 ai=np.exp(-dt);Ad=np.array([[1+dt,dt],[-dt,1-dt]])*ai;Bd=np.array([1-(1+dt)*ai,dt*ai])
 inter=(2+P)*(4+6/np.e)*dt*dt/8+dt/4
 er=[];ec=[];ev=[];rhs=[];ir=[];ic=[];iv=[];bub=[];bounds=[(None,None)]*nv
 def eq(cols,vals,v=0.):
  row=len(rhs);er.extend([row]*len(cols));ec.extend(cols);ev.extend(vals);rhs.append(v)
 def ine(cols,vals,v=0.):
  row=len(bub);ir.extend([row]*len(cols));ic.extend(cols);iv.extend(vals);bub.append(v)
 for j,(high,lo,hi) in enumerate(phases):
  X=j*bs;Y=X+n+1;S=Y+n+1;U=S+n+1;ymin,ymax=old.phase_envelope(t,lo,hi,high)
  for k in range(n+1):
   bounds[Y+k]=(ymax[k]-b+inter,ymin[k]+b-inter);bounds[S+k]=(0,None);ine([S+k,EI],[1,-1])
  bounds[X]=(0,0);bounds[Y]=(0,0);bounds[X+n]=(0,0);bounds[Y+n]=(0,0)
  eq([S,E0],[1,-1]);eq([S+n,E0],[1,-1])
  for k in range(n):
   bounds[U+k]=(-P,P);eq([X+k+1,X+k,Y+k,U+k],[1,-Ad[0,0],-Ad[0,1],-Bd[0]]);eq([Y+k+1,X+k,Y+k,U+k],[1,-Ad[1,0],-Ad[1,1],-Bd[1]]);eq([S+k+1,S+k,U+k],[1,-1,dt])
  branch=round((hi+delay)/dt);grp=0 if high else 1
  for k in range(branch):eq([U+k,tr+grp*ntr+k],[1,-1])
 for i in range(tr,EI):bounds[i]=(-P,P)
 bounds[EI]=(0,None);bounds[E0]=(0,None);ine([E0,EI],[1,-1]);c=np.zeros(nv);c[EI]=1
 ae=coo_matrix((ev,(er,ec)),shape=(len(rhs),nv)).tocsr();au=coo_matrix((iv,(ir,ic)),shape=(len(bub),nv)).tocsr()
 print(json.dumps(dict(stage='built',name=name,variables=nv,equalities=len(rhs))),flush=True)
 st=time.time();res=linprog(c,A_ub=au,b_ub=bub,A_eq=ae,b_eq=rhs,bounds=bounds,method='highs',options={'primal_feasibility_tolerance':1e-8,'dual_feasibility_tolerance':1e-8})
 out=dict(name=name,P=P,b=b,dt=dt,sample=dr,delay=delay,power_noise_bound=.1,noise_threshold_guarantee='any bound strictly less than .5',H=H,seconds=time.time()-st,success=res.success,message=res.message,initial_class=True,phase_bins=ns,continuous_phase=True,intersample_margin=inter)
 if res.success:
  out.update(E=float(res.fun),e0=float(res.x[E0]),max_eq=float(max(abs(res.eqlin.residual))),min_ineq=float(min(res.ineqlin.residual)))
  np.savez_compressed(ROOT/'raw'/f'{name}.npz',t=t,phases=phases,u=np.array([res.x[j*bs+3*(n+1):j*bs+3*(n+1)+n] for j in range(ns)]),soc=np.array([res.x[j*bs+2*(n+1):j*bs+3*(n+1)] for j in range(ns)]),x=np.array([res.x[j*bs:j*bs+n+1] for j in range(ns)]),y_control=np.array([res.x[j*bs+n+1:j*bs+2*(n+1)] for j in range(ns)]),E=res.fun,e0=res.x[E0])
 (ROOT/'raw'/f'{name}.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True);return out
if __name__=='__main__':
 import argparse
 pa=argparse.ArgumentParser();pa.add_argument('--delay',type=float,default=.05);pa.add_argument('--dt',type=float,default=.02);pa.add_argument('--dr',type=float,default=.1);a=pa.parse_args()
 solve(name=f'power_delay{a.delay:g}_dt{a.dt:g}_dr{a.dr:g}',dt=a.dt,dr=a.dr,delay=a.delay)
