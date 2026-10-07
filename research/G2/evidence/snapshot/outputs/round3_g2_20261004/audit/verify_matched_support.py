"""Independent physical-convolution audit of saved free-knot witnesses."""
from pathlib import Path
import sys,json,numpy as np
from numpy.polynomial.legendre import leggauss
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
import matched_support_baselines as m
P=Path(__file__).resolve().parent
x=json.loads((P.parent/'experiments/matched_support_results.json').read_text());out=[]
for r in x['rows']:
 N=r['N'];eps=r['epsilon'];w=r['continuous_linearized_support'];e=np.array(w['knot_times']);a=np.array(w['arc_accelerations'])/m.RHO
 edges=np.unique(np.r_[e,np.arange(8*N+1)/(8*N)]);k=2*np.pi*N
 def values(t):
  th,v=m.clock(e,a,t);e1=1-m.A/2*np.cos(k*th);e2=1+m.A/2*np.cos(k*th)
  return th,v,e1,e2
 def physical(t):
  th,v,e1,e2=values(t);s=1-t
  return (m.h(s)+eps*m.g(s))*e1*v+(-m.h(s)+eps*m.g(s))*e2*v
 physical=m.integrate(physical,edges,48)
 E=[m.integrate(lambda t:values(t)[j]*values(t)[1],edges,48) for j in [2,3]]
 th,v=m.clock(e,a,np.array([0.,1.]));q=lambda t:(-m.A*m.hp(1-t)*np.cos(k*t)+2*eps*m.gp(1-t))
 F=m.Functional(N,eps);z=np.linspace(.01,.99,199);dt=2e-4
 Fpp=(-F.F(z+2*dt)+16*F.F(z+dt)-30*F.F(z)+16*F.F(z-dt)-F.F(z-2*dt))/(12*dt**2)
 # Exact support dual root sign interval check on dense nodes; no claim formal root isolation.
 lam=np.array(w['lambda_']);dense=np.linspace(0,1,65537);j=np.clip(np.searchsorted(e,dense,side='right')-1,0,len(a)-1);res=F.F(dense)-lam[0]-lam[1]*dense
 mis=float(np.max(np.maximum(-res*a[j],0)))
 row=dict(N=N,epsilon=eps,power_vs_energy_identity_error=physical-w['exact_nonlinear_endpoint'],port_total_energy=E,phase_endpoints=th.tolist(),speed_endpoints=v.tolist(),dual_sign_mismatch=mis,F_second_derivative_error=float(np.max(abs(Fpp-q(z)))))
 assert abs(row['power_vs_energy_identity_error'])<1e-11
 assert max(abs(np.array(E)-1))<1e-10
 assert max(abs(th-[0,1]))<1e-10 and max(abs(v-1))<1e-10
 assert mis<1e-12
 assert row['F_second_derivative_error']<1e-7
 out.append(row)
(P/'MATCHED_SUPPORT_QA.json').write_text(json.dumps(dict(status='passed',checks=out,limit='Floating point diagnostics; no interval root isolation'),indent=2))
print(json.dumps(out,indent=2))
