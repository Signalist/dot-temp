from pathlib import Path
import json,numpy as np
from scipy.optimize import least_squares
from numpy.polynomial.legendre import leggauss
ROOT=Path(__file__).resolve().parent
J=.25;OMEGA=2*np.pi;D0=6*OMEGA**3

def src(t):
 t=np.asarray(t);Q=(1-np.cos(OMEGA*t))**2;Qp=2*OMEGA*np.sin(OMEGA*t)-OMEGA*np.sin(2*OMEGA*t);Qpp=2*OMEGA**2*(np.cos(OMEGA*t)-np.cos(2*OMEGA*t));Qppp=OMEGA**3*(-2*np.sin(OMEGA*t)+4*np.sin(2*OMEGA*t))
 return t+J*Q/D0,1+J*Qp/D0,J*Qpp/D0,J*Qppp/D0

def roots_from_z(z):
 zz=np.r_[z,0.];zz-=max(zz);w=np.exp(zz);return np.cumsum(w/w.sum())[:-1]
def moments(roots,n):
 e=np.r_[0.,roots,1.];a=(-1.)**np.arange(n+1)
 return np.array([np.diff(e**(k+1))@a/(k+1) for k in range(n)])
def saturate(left,right,n):
 x,w=leggauss(40);s=(x+1)/2;ww=w/2;target=np.array([ww@(s**k*src(left+(right-left)*s)[3]/J) for k in range(n)])
 rr=(1-np.cos(np.pi*np.arange(1,n+1)/(n+1)))/2;dd=np.diff(np.r_[0.,rr,1.]);z=np.log(dd[:-1]/dd[-1]);powers=10.**np.arange(n)
 sol=least_squares(lambda z:powers*(moments(roots_from_z(z),n)-target),z,xtol=1e-13,ftol=1e-13,gtol=1e-13,max_nfev=1000)
 rr=roots_from_z(sol.x);err=float(max(abs(moments(rr,n)-target)))
 assert err<1e-10,(left,right,n,err,sol.message)
 return np.r_[left,left+(right-left)*rr,right],J*(-1.)**np.arange(n+1),err

class Clock:
 def __init__(self,M,n):
  ed=[0.];aa=[];errs=[]
  for i in range(M):
   e,a,err=saturate(i/M,(i+1)/M,n);ed.extend(e[1:]);aa.extend(a);errs.append(err)
  self.e=np.array(ed);self.j=np.array(aa);d=np.diff(self.e);a=[0.];v=[1.];th=[0.]
  for dt,j in zip(d,self.j):
   th.append(th[-1]+v[-1]*dt+a[-1]*dt**2/2+j*dt**3/6);v.append(v[-1]+a[-1]*dt+j*dt**2/2);a.append(a[-1]+j*dt)
  self.th=np.array(th);self.v=np.array(v);self.a=np.array(a);self.err=max(errs)
 def val(self,t):
  t=np.asarray(t);ii=np.clip(np.searchsorted(self.e,t,side='right')-1,0,len(self.j)-1);dt=t-self.e[ii]
  return self.th[ii]+self.v[ii]*dt+self.a[ii]*dt**2/2+self.j[ii]*dt**3/6,self.v[ii]+self.a[ii]*dt+self.j[ii]*dt**2/2,self.a[ii]+self.j[ii]*dt

def integral(fun,edges,order=20):
 e=np.unique(edges);q,w=leggauss(order);dt=np.diff(e);x=((e[:-1]+e[1:])[:,None]/2+dt[:,None]*q/2).ravel();weights=(dt[:,None]*w/2).ravel();return float(weights@fun(x))
def E(th):return th+.2*np.sin(OMEGA*th)/OMEGA

def run():
 out=[]
 for n in [3,4]:
  for M in [2,4,8,16,32]:
   c=Clock(M,n);t=np.unique(np.r_[np.linspace(0,1,8193),c.e]);th,v,a=c.val(t);orig=src(t)[0];err=max(abs(th-orig));bound=J/(24*M**3)
   assert err<=bound+1e-11
   assert max(abs(np.array([c.th[-1]-1,c.v[-1]-1,c.a[-1]])))<1e-10
   assert min(v)>=.9 and max(v)<=1.1
   cellint=[integral(lambda t:c.val(t)[0]-src(t)[0],np.r_[i/M,c.e[(c.e>i/M)&(c.e<(i+1)/M)],(i+1)/M]) for i in range(M)]
   if n==4:assert max(abs(np.array(cellint)))<1e-11
   rows=[]
   for tau in np.linspace(0,4,257):
    end=min(tau,1.);ed=np.r_[0.,c.e[(c.e>0)&(c.e<end)],end]
    if end==0:val=0.
    else:val=integral(lambda t:(1-(tau-t))*np.exp(-(tau-t))*(E(c.val(t)[0])-E(src(t)[0])),ed)
    rows.append([float(tau),val])
   maxout=max(abs(x[1]) for x in rows)
   if n==3:theory=J*(1.2*2/np.e)/(24*M**3) # ||h'||1=2/e
   else:
    L=.2*OMEGA;M1=1.;M2=2.;C4=J/24*(1.2*M2+L*1.1*M1+1.2*M1);C6=J**2/1152*L*M1;theory=C4/M**4+C6/M**6
   assert maxout<=theory+1e-11
   row=dict(n_moments=n,M=M,jerk_arcs=len(c.j),jerk_jumps=int(np.count_nonzero(abs(np.diff(c.j))>1e-12)),max_moment_residual=c.err,phase_max_error=float(err),phase_bound=bound,endpoint_phase=float(c.th[-1]),endpoint_speed=float(c.v[-1]),endpoint_accel=float(c.a[-1]),min_speed=float(min(v)),max_speed=float(max(v)),max_cell_integral_phase_error=float(max(abs(np.array(cellint)))),sampled_output_max_error=maxout,theorem_global_bound=theory,observations=rows,edges=c.e.tolist(),jerks=c.j.tolist())
   out.append(row);print(json.dumps({k:v for k,v in row.items() if k not in ['observations','edges','jerks']}),flush=True)
   (ROOT/'jerk_compression_results.json').write_text(json.dumps(dict(status='running',rows=out),indent=2))
 (ROOT/'jerk_compression_results.json').write_text(json.dumps(dict(status='passed',scope='supplied-clock compression, not unknown optimizer or empirical sharp rate; ordinary float',rows=out),indent=2))
if __name__=='__main__':run()
