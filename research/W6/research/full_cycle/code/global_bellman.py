"""Matched-information global finite-state Bellman comparator, implemented independently.
Grid restricts z but never presupposes convexity. Same actual-slew and EOS objective.
Finite state optimum is an upper comparator, NOT a continuous lower bound.
"""
import numpy as np, math,time
from cycle_model import Case, power_int, Mesh

def avgpow(a,b,q):
 return power_int(a,b,q,1.)
def firstmoment(a,b,q):
 if a==0:return b**q/(q+2)
 if b==0:return a**q/((q+1)*(q+2))
 if a==b:return .5*a**q
 return (avgpow(a,b,q+1)-a*avgpow(a,b,q))/(b-a)
def uniform_edge(c,x,h,za,zb):
 if za==zb==0:return math.inf
 K=1+c.beta;qs=[(1-c.beta)/K,-c.beta/K,2/K,1/K]
 coeff=[K**qs[0],c.c*K**qs[1],K**qs[2]/(2*c.R),c.c*K**qs[3]/c.R]
 v=0.
 for k,(q,b) in enumerate(zip(qs,coeff)):
  avg=avgpow(za,zb,q)
  v+=b*h*((1-x)*avg-h*firstmoment(za,zb,q) if k<2 else avg)
 return v

def bellman(c,N=64,sub=2,recovery=True,critical=True):
 if c.dist!='uniform':raise ValueError('Independent Bellman benchmark currently uniform only')
 t0=time.perf_counter();h=1/N;dz=c.R*h/sub
 # Explicitly aligned initial values only; report mismatch instead of silently snapping.
 j0=int(round(c.z0/dz))
 if abs(j0*dz-c.z0)>1e-10:raise ValueError('Initial state not grid aligned')
 Jmax=j0+N*sub;z=np.arange(Jmax+1)*dz
 V=np.zeros(Jmax+1);policy=np.full((N,Jmax+1),-1,dtype=np.int32)
 if recovery:V[:]=np.inf;V[0]=0.
 expansions=0
 for i in range(N-1,-1,-1):
  now=np.full(Jmax+1,np.inf);x=i*h
  for j in range(max(0,j0-i*sub),min(Jmax,j0+i*sub)+1):
   if recovery and z[j]>c.R*(1-x)+1e-12:continue
   if critical and z[j]>max(c.A(c.critical),c.z0-c.R*x)+1e-12:continue
   for k in range(max(0,j-sub),min(Jmax,j+sub)+1):
    if not np.isfinite(V[k]):continue
    if critical and z[k]>max(c.A(c.critical),c.z0-c.R*(x+h))+1e-12:continue
    val=uniform_edge(c,x,h,z[j],z[k])+V[k];expansions+=1
    if val<now[j]:now[j]=val;policy[i,j]=k
  V=now
 inds=[j0]
 for i in range(N):
  k=int(policy[i,inds[-1]])
  if k<0:break
  inds.append(k)
 path=z[inds]
 return {'case':c.__dict__,'N':N,'sub':sub,'grid_dz':dz,'recovery_cap':recovery,'critical_cap':critical,'objective':float(V[j0]),'z':path.tolist(),'expansions':expansions,'seconds':time.perf_counter()-t0,'scope':'global optimum of stated finite-state piecewise-linear-z grid; not continuous lower certificate'}
