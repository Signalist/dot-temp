"""Exact sampled/held buffer-port LP; no Euler dynamics and no frozen PWM claim."""
from pathlib import Path
import sys,json,time
import numpy as np
from scipy.optimize import linprog,brentq
from scipy.sparse import lil_matrix
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'prior_core'
sys.path.insert(0,str(OLD/'src'))
from model import Params,poly_segments,base_knots
p=Params()

def run(critical_us=25,beta=808):
 hcrit=critical_us*1e-6
 t=np.unique(np.round(np.r_[np.arange(0,.04+hcrit/2,hcrit),np.arange(.04,.2+.00005,.0001),base_knots(p)],12))
 mod=poly_segments(t,100,beta,p);N=len(t)-1;h=np.diff(t);ee=np.exp(-h/p.tau);ah=p.tau*(-np.expm1(-h/p.tau));uh=h-ah
 # Variables b[0:N+1], C[0:N+1], u[0:N], sigma.
 bi=np.arange(N+1);ci=bi+N+1;ui=np.arange(N)+2*(N+1);si=3*N+2;nv=si+1
 eq=lil_matrix((2*N+4,nv));rhs=np.zeros(2*N+4)
 for j in range(N):
  eq[2*j,[bi[j+1],bi[j],ui[j]]]=[1,-ee[j],-(1-ee[j])]
  eq[2*j+1,[ci[j+1],ci[j],bi[j],ui[j]]]=[1,-1,-ah[j],-uh[j]]
 eq[-4,bi[0]]=1;eq[-3,bi[-1]]=1;eq[-2,ci[0]]=1;eq[-1,ci[-1]]=1
 # Cell endpoint state tube M h²/8; curvature of A and modulation exactly bounded from polynomials.
 rows=[];bounds=[]
 def le(vals,r): rows.append(vals);bounds.append(r)
 for j in range(N):
  le({int(ui[j]):1,int(bi[j]):-1},p.tau*p.ramp);le({int(ui[j]):-1,int(bi[j]):1},p.tau*p.ramp)
  A=mod['offset'][j];M=mod['modfloor'][j]
  A2=np.array([2*A[2],2*A[2]+6*A[3]])/h[j]**2;M2=2*M[2]/h[j]**2
  curves=[max(0,A2.max()+p.ramp),max(0,-A2.min()+p.ramp),max(0,(A2-M2).max()+p.ramp)]
  for idx,x in [(j,0),(j+1,1)]:
   av=float(np.polynomial.polynomial.polyval(x,A));mv=float(np.polynomial.polynomial.polyval(x,M))
   le({int(ci[idx]):-1,si:1},p.W0+av-p.Wmin-curves[0]*h[j]**2/8)
   le({int(ci[idx]):1,si:1},p.Wmax-p.W0-av-curves[1]*h[j]**2/8)
   le({int(ci[idx]):-1,si:1},p.W0+av-mv-curves[2]*h[j]**2/8)
   le({int(ci[idx]):1},p.B0-p.Bmin-p.ramp*h[j]**2/8)
   le({int(ci[idx]):-1},p.Bmax-p.B0-p.ramp*h[j]**2/8)
 Aub=lil_matrix((len(rows),nv))
 for rr,d in enumerate(rows):
  for col,val in d.items():Aub[rr,col]=val
 vb=[(-p.bmax,p.bmax)]*(N+1)+[(None,None)]*(N+1)+[(-p.umax,p.umax)]*N+[(-100,100)]
 for j in range(N):
  if t[j+1]<=p.delay+1e-12:vb[ui[j]]=(0,0)
 obj=np.zeros(nv);obj[si]=-1
 st=time.perf_counter();res=linprog(obj,A_ub=Aub.tocsr(),b_ub=np.array(bounds),A_eq=eq.tocsr(),b_eq=rhs,bounds=vb,method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9,'ipm_optimality_tolerance':1e-10});dt=time.perf_counter()-st
 out={'beta_kvar':beta,'critical_hold_us':critical_us,'later_hold_us':100,'intervals':N,'success':bool(res.success),'status':res.message,'runtime_s':dt}
 if res.success:
  v=res.x;b=v[bi];C=v[ci];u=v[ui];sig=v[si]
  out.update(sigma_kJ=float(sig),feasible_with_margin=bool(sig>1e-5),eq_residual=float(np.max(np.abs(eq@v-rhs))),inequality_residual=float(np.max(Aub@v-np.array(bounds))),b_end_kW=float(b[-1]),C_end_kJ=float(C[-1]),current_margin_kA2=float(p.imax**2-np.max(np.sum(mod['i']**2,axis=1))),gamma_kW=mod['profiles']['gamma'],grid_net_energy_residual_kJ=mod['energy_residual'])
  np.savez_compressed(ROOT/'results'/f'zoh_q{beta}_h{critical_us}.npz',t=t,b=b,charge=C,u=u,A=mod['offset'],M=mod['modfloor'],p=mod['profiles']['p'],q=mod['profiles']['q'],d=mod['profiles']['d'],sigma=sig,par_json=json.dumps(p.dict()))
 return out
if __name__=='__main__':
 rows=[]
 for h in [25,50,100]:
  o=run(h);rows.append(o);print(json.dumps(o),flush=True)
 (ROOT/'results'/'zoh_inner_results.json').write_text(json.dumps(rows,indent=2))
