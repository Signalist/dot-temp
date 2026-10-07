"""Frozen-protocol matched-information endpoint experiment, ordinary float.
All baselines use identical p=e(theta)*theta_dot and fixed work/speed moments.
Only two explicit ablations relax those promises. No runtime claim.
"""
from pathlib import Path
import json,time,hashlib
import numpy as np
from numpy.polynomial import Polynomial as Poly
from numpy.polynomial.legendre import leggauss
from scipy.optimize import linprog,root,brentq

ROOT=Path(__file__).resolve().parent
A=.01; RHO=.05
H=np.array([1.,0.,-1.,0.])/np.e
G=np.array([1.2,-.3,-1.,.1])/np.e

class Functional:
 def __init__(self,N,eps,port=None):
  self.N=N;self.eps=eps;self.k=2*np.pi*N
  terms=[]
  if port is None:
   terms=[(1.,2*eps*G),(1+1j*self.k,-A*H/2),(1-1j*self.k,-A*H/2)]
  else:
   sign=1 if port==1 else -1;P=sign*H+eps*G
   terms=[(1.,P),(1+1j*self.k,-sign*A*P/4),(1-1j*self.k,-sign*A*P/4)]
  self.terms=[]
  for z,P in terms:
   p=Poly(P.astype(complex));r=Poly([0j])
   for j in range(len(P)): r+=(-1)**j*(j+1)*p.deriv(j)/z**(j+2)
   h1=np.exp(z)*r(1.);dh1=np.exp(z)*(z*r(1.)+r.deriv()(1.))
   self.terms.append((z,r,h1,dh1))
 def F(self,t):
  t=np.asarray(t);v=np.zeros_like(t,dtype=complex)
  for z,r,h1,dh1 in self.terms:v+=np.exp(z*t)*r(t)-h1-(t-1)*dh1
  return v.real

def integrate(fun,edges,order=24):
 q,w=leggauss(order);edges=np.unique(np.asarray(edges));l=edges[:-1];r=edges[1:]
 x=((l+r)[:,None]/2+(r-l)[:,None]*q/2).ravel();ww=((r-l)[:,None]*w/2).ravel()
 return float(ww@fun(x))

def cells(F,M):
 e=np.linspace(0,1,M+1);q,w=leggauss(32);t=(e[:-1,None]+e[1:,None])/2+np.diff(e)[:,None]*q/2
 return (F.F(t)*w[None,:]*np.diff(e)[:,None]/2).sum(axis=1)

def lp(F,M):
 c=cells(F,M);e=np.linspace(0,1,M+1);mom=np.array([np.diff(e),np.diff(e**2)/2])
 sol=linprog(-c,A_eq=mom,b_eq=[0.,0.],bounds=[(-1,1)]*M,method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
 assert sol.success,sol.message
 return e,sol.x,float(c@sol.x),-sol.eqlin.marginals

def sign_roots(F,lam):
 e=np.linspace(0,1,max(2049,256*F.N+1));v=F.F(e)-lam[0]-lam[1]*e
 roots=[]
 for i in np.flatnonzero(v[:-1]*v[1:]<0):roots.append(brentq(lambda t:float(F.F(t)-lam[0]-lam[1]*t),e[i],e[i+1],xtol=2e-15))
 return np.r_[0.,roots,1.]

def signs_and_moments(F,lam):
 e=sign_roots(F,lam);a=np.sign(F.F((e[:-1]+e[1:])/2)-lam[0]-lam[1]*(e[:-1]+e[1:])/2)
 return e,a,np.array([np.diff(e)@a,np.diff(e**2)@a/2])

def free_knot(F):
 _,_,_,lam=lp(F,max(512,64*F.N))
 # The exact sign-moment equations refine the discrete dual; no knot cap.
 scale=max(np.max(np.abs(F.F(np.linspace(0,1,1001)))) ,1e-15)
 sol=root(lambda z:signs_and_moments(F,z*scale)[2],lam/scale,tol=1e-11)
 lam=sol.x*scale;e,a,mom=signs_and_moments(F,lam)
 dual=integrate(lambda t:np.abs(F.F(t)-lam[0]-lam[1]*t),e,40)
 val=sum(a[i]*integrate(F.F,e[i:i+2],40) for i in range(len(a)))
 refined=integrate(lambda t:np.abs(F.F(t)-lam[0]-lam[1]*t),e,64)
 assert max(abs(mom))<1e-9,(F.N,F.eps,sol.message,mom)
 assert abs(val-dual)<1e-10
 return e,a,dict(value=val,dual=dual,primal_dual_gap=dual-val,moment_residual=mom.tolist(),switches=len(a)-1,lambda_=lam.tolist(),root_status=bool(sol.success),quadrature_refinement=refined-dual)

def clock(e,a,t):
 d=np.diff(e);v=np.r_[0.,np.cumsum(a*d)];eta=np.r_[0.,np.cumsum(v[:-1]*d+a*d*d/2)]
 j=np.clip(np.searchsorted(e,t,side='right')-1,0,len(a)-1);dt=np.asarray(t)-e[j]
 return np.asarray(t)+RHO*(eta[j]+v[j]*dt+a[j]*dt*dt/2),1+RHO*(v[j]+a[j]*dt)

def h(s):return s*s*np.exp(-s)
def hp(s):return (2*s-s*s)*np.exp(-s)
def g(s):return (s*s+.1*s**3)*np.exp(-s)
def gp(s):return (2*s-.7*s*s-.1*s**3)*np.exp(-s)
def exact_y(N,eps,e,a,order=32):
 k=2*np.pi*N;edges=np.unique(np.r_[e,np.arange(4*N+1)/(4*N)])
 # Energy primitive representation, valid at fixed theta(1)=1.
 def fun(t):
  th,_=clock(e,a,t)
  return -A/k*hp(1-t)*np.sin(k*th)+2*eps*gp(1-t)*th
 return integrate(fun,edges,order) # h1(0)=h2(0)=0 and primitives zero at start

def envelope(t):
 return np.where(t<=.25,t*t/2,np.where(t<=.75,-t*t/2+t/2-1/16,(1-t)**2/2))

def run():
 result=[]
 for N in [8,2,32]:
  for eps in [0.,.0025,.01]:
   t0=time.perf_counter();F=Functional(N,eps);e,a,ref=free_knot(F)
   nominal=exact_y(N,eps,np.array([0.,1.]),np.array([0.]));refy=exact_y(N,eps,e,a);refy2=exact_y(N,eps,e,a,48)
   # Taylor: derivative of aggregate integrand wrt theta is -A*k*hp*sin;
   # common mode is exactly affine in theta, so only oscillation contributes.
   remainder=A*(2*np.pi*N)*RHO**2/2*integrate(lambda t:abs(hp(1-t))*envelope(t)**2,np.linspace(0,1,129),40)
   methods=[]
   for M in [4,8,16,32,64,128]:
    ee,aa,val,_=lp(F,M);y=exact_y(N,eps,ee,aa)
    phase,speed=clock(ee,aa,np.linspace(0,1,4097))
    methods.append(dict(method='uniform_PWC_LP',M=M,linear_value=val,linear_loss=ref['value']-val,exact_nonlinear_endpoint=y,nonlinear_remainder_observed=y-nominal-RHO*val,speed_min=float(speed.min()),speed_max=float(speed.max()),switches=int(np.count_nonzero(np.abs(np.diff(aa))>1e-8))))
   eb=np.array([0.,.25,.75,1.]);ab=np.array([1.,-1.,1.]);bv=sum(ab[i]*integrate(F.F,eb[i:i+2],40) for i in range(3));by=exact_y(N,eps,eb,ab)
   ablate_unconstrained=integrate(lambda t:abs(F.F(t)),np.arange(16*N+1)/(16*N),40)
   independent=[]
   for port in [1,2]:
    _,_,pr=free_knot(Functional(N,eps,port));independent.append(pr['value'])
   ref.update(exact_nonlinear_endpoint=refy,nonlinear_quadrature_change=refy2-refy,nonlinear_remainder_observed=refy-nominal-RHO*ref['value'],knot_times=e.tolist(),arc_accelerations=(RHO*a).tolist())
   assert abs(refy2-refy)<1e-10
   assert abs(ref['nonlinear_remainder_observed'])<=remainder+1e-12
   assert all(abs(m['nonlinear_remainder_observed'])<=remainder+1e-12 for m in methods)
   if eps==.01: assert abs(ref['value']-bv)<1e-10
   row=dict(N=N,epsilon=eps,nominal_endpoint=nominal,continuous_linearized_support=ref,uniform_remainder=remainder,nonlinear_global_max_interval=[refy,nominal+RHO*ref['dual']+remainder],uniform_methods=methods,envelope=dict(linear_value=bv,exact_nonlinear_endpoint=by,linear_loss=ref['value']-bv,nonlinear_exact_max_proven=bool(eps>=A/2)),ablations=dict(no_endpoint_moments=ablate_unconstrained,independent_port_clocks=sum(independent),correct_shared_clock=ref['value']),seconds=time.perf_counter()-t0)
   result.append(row)
   print(json.dumps({'N':N,'epsilon':eps,'switches':ref['switches'],'support':ref['value'],'envelope_loss':ref['value']-bv,'seconds':row['seconds']}),flush=True)
   (ROOT/'matched_support_results.json').write_text(json.dumps(dict(status='running',rows=result),indent=2))
 out=dict(status='passed',arithmetic='ordinary float; exact supporting proofs separate',scope='linearized endpoint global support and nonlinear endpoint witnesses/remainder, not full-future peak',rows=result)
 (ROOT/'matched_support_results.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':run()
