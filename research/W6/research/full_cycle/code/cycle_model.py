"""Full recovery-cycle models. All units synthetic; z=int_0^p s, s=p**beta.
Uses positive quadrature and analytic endpoint limits; never subtracts nearly equal powers.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import minimize,linprog,minimize_scalar
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from dataclasses import dataclass

@dataclass(frozen=True)
class Case:
 beta:float=.5
 R:float=1.
 c:float=1.
 p0:float=0.
 dist:str='uniform'
 alpha:float=1.
 rate:float=.3
 atom:float=0.
 def S(self,x):
  x=np.asarray(x)
  if self.dist=='uniform':return 1-x
  if self.dist=='power':return (1-x)**self.alpha
  if self.dist=='truncexp':return (np.exp(-self.rate*x)-np.exp(-self.rate))/(-np.expm1(-self.rate))
  if self.dist=='endatom':return self.atom+(1-self.atom)*(1-x)
  raise ValueError(self.dist)
 def f(self,x):
  x=np.asarray(x)
  if self.dist=='uniform':return np.ones_like(x)
  if self.dist=='power':return self.alpha*(1-x)**(self.alpha-1)
  if self.dist=='truncexp':return self.rate*np.exp(-self.rate*x)/(-np.expm1(-self.rate))
  if self.dist=='endatom':return np.full_like(x,1-self.atom)
 def A(self,p):return np.asarray(p)**(1+self.beta)/(1+self.beta)
 def P(self,z):return ((1+self.beta)*np.asarray(z))**(1/(1+self.beta))
 @property
 def critical(self):return self.beta*self.c/(1-self.beta)
 @property
 def z0(self):return float(self.A(self.p0))
 def G(self,z):
  p=self.P(z);return (p+self.c)/p**self.beta
 def H(self,z):
  p=self.P(z);return (p*p/2+self.c*p)/self.R
 def F(self,x,z):return self.S(x)*self.G(z)+self.f(x)*self.H(z)
 def Fz(self,x,z):
  p=self.P(z);s=p**self.beta;N=s-(p+self.c)*self.beta*p**(self.beta-1)
  return self.S(x)*N/s**3+self.f(x)*(p+self.c)/(self.R*s)
 def Fzz(self,x,z):
  b=self.beta;p=self.P(z)
  return self.S(x)*b*((1+2*b)*self.c-2*(1-b)*p)*p**(-3*b-2)+self.f(x)*((1-b)*p-b*self.c)/(self.R*p**(2*b+1))
 def cap(self,x):return np.minimum(self.R*(1-np.asarray(x)),np.maximum(self.A(self.critical),self.z0-self.R*np.asarray(x)))

def power_int(za,zb,q,dx):
 # Independent stable log1p/expm1 version, normalized A(p) differs from prior code.
 if za==0:return dx*zb**q/(q+1)
 if zb==0:return dx*za**q/(q+1)
 d=(zb-za)/za
 if d==0:return dx*za**q
 return dx*za**q*np.expm1((q+1)*np.log1p(d))/((q+1)*d)

class Mesh:
 def __init__(self,case,N=128,order=32,ends_zero=True):
  self.c=case;self.N=N;self.h=1/N;self.order=order;self.ends_zero=ends_zero
  u,w=leggauss(order);u=(u+1)/2;w=w/2
  self.u=np.broadcast_to(u,(N,order)).copy();self.w=np.broadcast_to(w,(N,order)).copy()
  # Smooth integrable endpoint singularities before positive Gaussian quadrature.
  self.u[0]=u**6;self.w[0]=w*6*u**5
  if ends_zero:self.u[-1]=1-u**3;self.w[-1]=w*3*u**2
  self.x=(np.arange(N)[:,None]+self.u)*self.h
 def evaluate(self,z,gradient=False,parts=False):
  c=self.c;u=self.u;w=self.w;h=self.h
  zz=z[:-1,None]*(1-u)+z[1:,None]*u
  if np.any(zz<=0):
   if gradient:return 1e100,np.zeros(len(z))
   return 1e100
  p=c.P(zz);S=c.S(self.x);f=c.f(self.x)
  energy=h*np.sum(w*(S*p**(1-c.beta)+f*p*p/(2*c.R)))
  task=h*np.sum(w*S/p**c.beta);tailtime=h*np.sum(w*f*p/c.R)
  if c.dist=='endatom':
   pend=c.P(z[-1]);energy+=c.atom*pend*pend/(2*c.R);tailtime+=c.atom*pend/c.R
  val=energy+c.c*(task+tailtime)
  if parts:return {'dynamic_energy':float(energy),'task_time':float(task),'recovery_time':float(tailtime),'cycle_time':float(task+tailtime),'objective':float(val)}
  if gradient:
   gz=h*w*c.Fz(self.x,zz);g=np.zeros(len(z));g[:-1]+=np.sum(gz*(1-u),axis=1);g[1:]+=np.sum(gz*u,axis=1)
   # endpoint is fixed at zero for all endatom optimizations; avoid derivative at zero.
   return float(val),g
  return float(val)

def solve(case,N=128,initial=None,order=32,cap_recovery=True):
 import time
 start=time.perf_counter();mesh=Mesh(case,N,order,ends_zero=cap_recovery);x=np.linspace(0,1,N+1);h=1/N
 if case.z0>=case.R and cap_recovery:
  z=case.z0-case.R*x
  return {'case':case.__dict__,'N':N,'z':z.tolist(),'special':'prepaid_descent','parts':Mesh(case,N,96,False).evaluate(z,parts=True),'success':True,'seconds':time.perf_counter()-start}
 forced=max(0.,(case.z0-case.A(case.critical))/case.R)
 if forced>0 and abs(forced*N-round(forced*N))>1e-9:
  raise ValueError("Nonzero critical-prefix breakpoint must be exactly mesh aligned; insert it or choose an aligned grid")
 # A node on forced high-power prefix is fixed; all residual nodes form a convex program.
 lo=np.maximum(0.,case.z0-case.R*x);up=np.minimum(case.z0+case.R*x,case.cap(x)) if cap_recovery else np.maximum(case.A(case.critical),case.z0-case.R*x)
 lo[0]=up[0]=case.z0
 if cap_recovery:lo[-1]=up[-1]=0.
 fixed=np.isclose(lo,up,rtol=0,atol=1e-13);free=np.where(~fixed)[0];base=lo.copy();base[free]=0.;lb=np.maximum(lo[free],1e-13);ub=up[free]
 # Difference matrix maps free nodal coordinates into slopes.
 D=np.diff(np.eye(N+1),axis=0);Af=D[:,free];db=D@base
 constraint={'type':'ineq','fun':lambda v:np.r_[case.R*h-db-Af@v,case.R*h+db+Af@v],'jac':lambda v:np.r_[-Af,Af]}
 if initial is None:v=np.maximum(lb,.8*up[free]+.2*lo[free])
 else:v=np.clip(np.interp(x[free],np.linspace(0,1,len(initial)),initial),lb,ub)
 def expand(v):
  z=base.copy();z[free]=v;return z
 def fun(v):
  val,g=mesh.evaluate(expand(v),True);return val,g[free]
 res=minimize(fun,v,jac=True,method='SLSQP',bounds=list(zip(lb,ub)),constraints=constraint,options={'ftol':2e-11,'maxiter':1200})
 z=expand(res.x);val,g=fun(res.x)
 lp=linprog(g,A_ub=np.r_[Af,-Af],b_ub=np.r_[case.R*h-db,case.R*h+db],bounds=list(zip(lb,ub)),method='highs')
 gap=float(g@res.x-lp.fun) if lp.success else None
 parts=Mesh(case,N,96,cap_recovery).evaluate(z,parts=True)
 return {'case':case.__dict__,'N':N,'z':z.tolist(),'success':bool(res.success),'message':res.message,'iterations':int(res.nit),'mesh_objective':val,'parts':parts,'quadrature_difference':abs(parts['objective']-val),'finite_mesh_linearization_gap':gap,'max_slew_excess':float(max(0.,np.max(np.abs(np.diff(z)))/h-case.R)),'max_cap_excess':float(max(0.,np.max(z-up))),'seconds':time.perf_counter()-start,'forced_prefix_end_x':float(forced),'minimum_interior_power':float(min(case.P(z[1:-1])))}

def target_baseline(case,N=1024):
 from scipy.optimize import brentq
 if case.p0!=0 or case.dist!='uniform':raise ValueError('Analytically global target formula is idle/uniform only')
 b=case.beta;R=case.R;c=case.c;K=1+b
 pc=brentq(lambda p:(1-b)*p+2/R*p**(1+b)*(p+c)-b*c,0,case.critical)
 peak=float(case.P(R/2));target=min(pc,peak);q=float(case.A(target));a=q/R;m=1-2*a
 earlyE=(K*R)**(2/K)*a**(1+2/K)/(R*(1+2/K))
 earlyT=2*(K*R)**(1/K)*a**(1+1/K)/(R*(1+1/K))
 energy=earlyE+(1-a)*target**2/R+.5*target**(1-b)*m
 cycle=earlyT+(1-a)*2*target/R+.5*target**(-b)*m
 tail=earlyT+m*target/R
 parts={'dynamic_energy':float(energy),'task_time':float(cycle-tail),'recovery_time':float(tail),'cycle_time':float(cycle),'objective':float(energy+c*cycle)}
 x=np.linspace(0,1,N+1);z=np.minimum(np.minimum(R*x,q),R*(1-x))
 return {'target':float(target),'parts':parts,'z':z.tolist(),'N':N,'method':'Unique monotone stationary root capped by reachable peak; analytic whole-cycle expectation','exact_breakpoints_x':[0.,a,1-a,1.],'exact_breakpoints_z':[0.,q,q,0.]}

def reconstruct(case,z,W):
 n=len(z)-1;time=energy=work=0.;segments=[];b=case.beta;K=1+b
 for i in range(n):
  lo=i/n;hi=min((i+1)/n,W)
  if hi<=lo:break
  za=z[i];zb=za+(z[i+1]-za)*n*(hi-lo);dt=K**(-b/K)*power_int(za,zb,-b/K,hi-lo);e=K**((1-b)/K)*power_int(za,zb,(1-b)/K,hi-lo)
  pa,pb=case.P(np.array([za,zb]));slew=(zb-za)/(hi-lo)
  segments.append({'x0':lo,'x1':hi,'t0':time,'t1':time+dt,'p0':float(pa),'p1':float(pb),'slew':slew,'energy':e,'work':hi-lo});time+=dt;energy+=e;work+=hi-lo
  if hi==W:break
 p=float(case.P(np.interp(W,np.linspace(0,1,n+1),z)));tail=p/case.R;burn=p*p/(2*case.R)
 return {'W':W,'task_time':time,'tail_time':tail,'cycle_time':time+tail,'productive_energy':energy,'burn_energy':burn,'dynamic_energy':energy+burn,'objective':energy+burn+case.c*(time+tail),'work':work,'segments':segments}
