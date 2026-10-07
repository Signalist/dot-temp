"""Outward interval audit of an exact-decimal dual for the analytic prefix LP.
All exp coefficients / phase bounds and stationarity residues enclosed with mpmath.iv.
"""
import json,time
from pathlib import Path
import numpy as np,mpmath as mp
mp.iv.dps=40;mp.mp.dps=60
I=mp.iv.mpf;ROOT=Path(__file__).resolve().parents[1]
def iv(x):return I(str(x))
def lo(x):return mp.mpf(x._mpi_[0])
def hi(x):return mp.mpf(x._mpi_[1])
def absolute(x):return max(abs(lo(x)),abs(hi(x)))
def solve(dt=.001):
 st=time.time();d=np.load(ROOT/'raw'/f'continuum_prefix_dt{dt:g}.npz');n=round(5/dt);bs=4*n+3;EI=2*bs;E0=EI+1;nv=E0+1
 dl=list(map(iv,d['lower_dual']));du=list(map(iv,d['upper_dual']));eq=list(map(iv,d['eq_dual']));mu=list(map(iv,d['ineq_dual']))
 assert all(lo(x)>=0 for x in dl) and all(hi(x)<=0 for x in du) and all(hi(x)<=0 for x in mu)
 rr=[-dl[i]-du[i] for i in range(nv)];rr[EI]+=1
 DT=iv(dt);P=iv('.5');aa=mp.iv.exp(-DT);ad00=(1+DT)*aa;ad01=DT*aa;ad10=-DT*aa;ad11=(1-DT)*aa;bd0=1-(1+DT)*aa;bd1=DT*aa;dy=P*DT*(1+2*mp.iv.exp(-2));dual=iv(0);erow=0;irow=0;box=[iv(1) for _ in range(nv)]
 def sub(cols,coefs,q):
  for j,c in zip(cols,coefs):rr[j]-=c*q
 for group,high in enumerate([True,False]):
  X=group*bs;Y=X+n+1;S=Y+n+1;U=S+n+1
  for k in range(n+1):
   sub([S+k,EI],[iv(1),iv(-1)],mu[irow]);irow+=1
   t=iv(str(k))*DT;g=t*mp.iv.exp(-t);tt=t if k*dt<=1 else iv(1);peak=tt*mp.iv.exp(-tt);base=iv(2 if high else 1)*g
   mn=base-peak if high else base;mx=base if high else base+peak
   if k:dual+=dl[Y+k]*(mx-iv('.6')-dy)+du[Y+k]*(mn+iv('.6')+dy)
   box[X+k]=P;box[Y+k]=2*P/mp.iv.exp(1)
  sub([S,E0],[iv(1),iv(-1)],eq[erow]);erow+=1
  for k in range(n):
   sub([X+k+1,X+k,Y+k,U+k],[iv(1),-ad00,-ad01,-bd0],eq[erow]);erow+=1
   sub([Y+k+1,X+k,Y+k,U+k],[iv(1),-ad10,-ad11,-bd1],eq[erow]);erow+=1
   sub([S+k+1,S+k,U+k],[iv(1),iv(-1),DT],eq[erow]);erow+=1
   dual+=P*(du[U+k]-dl[U+k]);box[U+k]=P
 sub([E0,EI],[iv(1),iv(-1)],mu[irow]);irow+=1
 assert erow==len(eq) and irow==len(mu)
 correction=iv(0)
 for r,b in zip(rr,box):correction+=iv(str(absolute(r)))*b
 lower=lo(dual-correction);out=dict(dt=dt,variables=nv,dual_interval=[str(lo(dual)),str(hi(dual))],stationarity_box_correction_upper=str(hi(correction)),certified_energy_lower=str(lower),max_stationarity_upper=str(max(absolute(r) for r in rr)),seconds=time.time()-st,scope='arbitrary measurable control cell-average image, first five units, no terminal constraints, all phases with same initial class and common e0/E; E>=1 trivial, E<1 audited box',arithmetic='mpmath.iv 40 decimal digits outward interval arithmetic; exact decimal dual entries; analytic exact phase envelopes; not proof assistant')
 (ROOT/'raw'/'interval_lower_certificate.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
if __name__=='__main__':solve()
