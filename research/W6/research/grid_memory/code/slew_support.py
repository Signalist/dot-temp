"""Reconstructed after filesystem reset; rerun rather than recalled results.
All-history frequency support: ordinary-float LP plus analytic remainder budgets.
"""
import json,math,hashlib,time
from datetime import datetime,timezone
from dataclasses import dataclass,asdict
from fractions import Fraction
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import diags,vstack

@dataclass(frozen=True)
class Swing:
 mode_hz:float=.4
 zeta:float=.1
 gain_MW:float=20.
 inertia:float=400/3
 @property
 def omega(self):return 2*np.pi*self.mode_hz
 @property
 def a(self):return self.zeta*self.omega
 @property
 def wd(self):return self.omega*np.sqrt(1-self.zeta**2)
 @property
 def b(self):return self.gain_MW/self.inertia
 def impulse(self,t):return -self.b*np.exp(-self.a*np.asarray(t))*(np.cos(self.wd*np.asarray(t))-self.a/self.wd*np.sin(self.wd*np.asarray(t)))
 def step(self,t):return -self.b/self.wd*np.exp(-self.a*np.asarray(t))*np.sin(self.wd*np.asarray(t))
 def area(self):
  z=self.zeta;q=np.sqrt(1-z*z)
  return self.b/self.omega*np.exp(-z*np.arccos(z)/q)/(-np.expm1(-np.pi*z/q))
 def slew_norm(self):return self.b/self.omega**2/np.tanh(np.pi*self.zeta/(2*np.sqrt(1-self.zeta**2)))
 def tail_bound(self,T):return self.b*np.sqrt(1+(self.a/self.wd)**2)*np.exp(-self.a*T)/self.a
 def hats(self,t):
  lam=-self.a+1j*self.wd;c=1+1j*self.a/self.wd
  F=-self.b*np.real(c*np.exp(lam*t)/lam);F1=-self.b*np.real(c*np.exp(lam*t)*(t/lam-1/lam**2))
  ints=np.diff(F);firsts=np.diff(F1);right=(firsts-t[:-1]*ints)/np.diff(t)
  w=np.zeros(len(t));w[:-1]+=ints-right;w[1:]+=right;return w

def support(model,pcap,R,dt=.025,exponents=14):
 T=exponents/model.a;N=math.ceil(T/dt);t=np.linspace(0,T,N+1);step=T/N;w=model.hats(t)
 D=diags([-np.ones(N),np.ones(N)],[0,1],shape=(N,N+1),format='csr');A=vstack([D,-D]);rhs=np.r_[R*np.diff(t),R*np.diff(t)]
 sols=[];start=time.perf_counter()
 for sign in [-1.,1.]:
  res=linprog(-sign*w,A_ub=A,b_ub=rhs,bounds=(0,pcap),method='highs')
  if not res.success:raise RuntimeError(res.message)
  # Analytic weak upper bound with nonnegative inequality multipliers and
  # explicit residual maximization over the box; no perfect dual solve needed.
  dual=np.maximum(0.,-res.ineqlin.marginals)
  upper=float(dual@rhs+pcap*np.maximum(sign*w-A.T@dual,0).sum())
  raw=res.x.copy();delta=abs(np.diff(raw));mask=delta>0
  scale=min(1.,float(np.min(R*np.diff(t)[mask]/delta[mask]))) if np.any(mask) else 1.
  path=raw*scale*(1-1e-9)
  # Use exact differences of the serialized IEEE values, not rounded differences.
  exact=all(abs(Fraction(float(path[i+1]))-Fraction(float(path[i])))<=Fraction(float(R))*(Fraction(float(t[i+1]))-Fraction(float(t[i]))) for i in range(N))
  exact=exact and all(Fraction(0)<=Fraction(float(v))<=Fraction(float(pcap)) for v in path)
  assert exact
  sols.append({'raw_value':float(-res.fun),'value':float(sign*w@path),'path':path,'sign':sign,'dual_upper':upper,'exact_feasible':exact,'raw_excess':max(0.,float(max(abs(np.diff(raw))/np.diff(t))-R))})
 winner=max(sols,key=lambda z:z['value']);value=winner['value'];path=winner['path'];sign=winner['sign'];dualupper=max(s['dual_upper'] for s in sols)
 tail=pcap*model.tail_bound(T);interp=R*max(np.diff(t))*model.area()
 row={'model':asdict(model),'pcap':pcap,'R':R,'dt':step,'horizon':T,'nodes':N+1,'LP_support':float(value),
 'support_lower':max(0.,float(value-tail)),'support_upper':min(pcap*model.area(),R*model.slew_norm(),float(dualupper+tail+interp)),
 'LP_dual_weak_upper':dualupper,'raw_LP_support':max(s['raw_value'] for s in sols),'raw_slew_excess_max':max(s['raw_excess'] for s in sols),'exact_serialized_witness_constraints_pass':all(s['exact_feasible'] for s in sols),'inward_relative_reserve':1e-9,
 'interpolation_remainder':interp,'tail_remainder':tail,'amplitude_only_bound':pcap*model.area(),'slew_only_bound':R*model.slew_norm(),
 'max_slew_excess':max(0.,float(max(abs(np.diff(path)))/step-R)),'seconds':time.perf_counter()-start,
 'sign':sign,'numeric_status':'ordinary_float_analytic_remainders_not_outward_rounded'}
 return row,t,path

def main():
 root=Path(__file__).resolve().parents[1];out=root/'results';out.mkdir(exist_ok=True)
 protocol={'fresh_freeze_utc':datetime.now(timezone.utc).isoformat(),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  'status':'auxiliary exploratory support-bound convergence; postreset fresh rerun, not independent samples',
  'cases':[(.4,.1,.5,1.),(.25,.08,.5,.5),(.7,.08,1.,2.),(.4,.1,1.,.1)],'steps':[.05,.025,.0125],'tail_exponents':14,
 'reset':'pre-reset raw results vanished; this code was reconstructed and all reported outputs newly run',
 'repair':'pre_inward_repair retains raw LP witnesses with tiny floating slew excess; new witnesses inwardscaled and exact rational constraints checked; upper uses dual residual formula, kernel/cost remain ordinary float'}
 (out/'SLEW_SUPPORT_PROTOCOL.json').write_text(json.dumps(protocol,indent=2));rows=[]
 for hz,z,cap,R in protocol['cases']:
  for dt in protocol['steps']:
   row,t,p=support(Swing(hz,z),cap,R,dt,protocol['tail_exponents']);rows.append(row)
   name=f'support_f{hz}_z{z}_cap{cap}_R{R}_dt{dt}';np.savez_compressed(out/(name+'.npz'),lag_time=t,lag_power=p)
   print(name,row['support_lower'],row['support_upper'],flush=True)
 (out/'SLEW_SUPPORT_RESULTS.json').write_text(json.dumps(rows,indent=2))
if __name__=='__main__':main()
