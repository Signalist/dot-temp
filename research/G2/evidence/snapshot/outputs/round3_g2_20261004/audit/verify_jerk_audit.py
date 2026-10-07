#!/usr/bin/env python3
"""Independent ordinary-floating-point checks; not a proof or interval certificate."""
import json, math, pathlib
import numpy as np
from scipy.integrate import quad
from scipy.optimize import linprog
A=.01; J=.25; l=.9; twopi=2*math.pi; d0=6*twopi**3
Qb=[4,6*math.pi,16*math.pi**2,48*math.pi**3]
K={1:54*math.exp(-3),2:24,3:48,4:90}
records=[(1,3,0,0,0,3),(-2,2,1,0,0,2),(3,2,0,1,0,4),(1,1,2,0,0,1),(-2,1,1,1,0,3),(3,1,0,2,0,5),(-1,1,0,0,1,4)]
drecords=[]
for c,r,s,p,q,d in records:
    drecords += [(-c,r+1,s,p,q,d+1),(c,r,s+1,p,q,d),(-c*d,r,s,p+1,q,d+2)]
    if p: drecords += [(c*p,r,s,p-1,q+1,d+1)]
Ccont=sum(abs(c)*Qb[s]*K[r]*J**q*l**(1-d) for c,r,s,p,q,d in drecords)
C2=sum(abs(c)*Qb[s]*K[r]*J**q*l**(1-d) for c,r,s,p,q,d in records)
S=3*4/l**4; B0=6*4/l**3; C0=B0+Ccont; I0=2/(9*math.e)
G1=7*Qb[0]+3*Qb[1]; G3=Qb[0]*K[4]+3*Qb[1]*K[3]+3*Qb[2]*K[2]+Qb[3]*K[1]
CR=8/(math.e*d0*d0)*(twopi*Qb[0]+2*Qb[1]+Qb[2]/twopi)
Cstar=G3/twopi**4+J*(5*G1/d0+2*Qb[1]/(math.pi*d0*math.e))+J*J*CR
N0=math.ceil(2*d0*Cstar/(J*I0)); alpha=math.pi*I0/(24*S); beta=C0/(2*J*S); gamma=A*J*I0/(4*d0)
def Q(x,n=0):
    if n==0:return 1.5-2*math.cos(twopi*x)+.5*math.cos(2*twopi*x)
    return -2*twopi**n*math.cos(twopi*x+n*math.pi/2)+.5*(2*twopi)**n*math.cos(2*twopi*x+n*math.pi/2)
def h(s,n=0):
    coeff={0:[0,0,0,1],1:[0,0,3,-1],2:[0,6,-6,1],3:[6,-18,9,-1],4:[-24,36,-12,1]}[n]
    return math.exp(-s)*sum(c*s**r for r,c in enumerate(coeff))
def P(x,N):return -A/(twopi*N)*Q(x)*math.sin(twopi*N*x)
def P1(x,N):return -A*(Q(x)*math.cos(twopi*N*x)+Q(x,1)*math.sin(twopi*N*x)/(twopi*N))
a0=(1-1/math.sqrt(2))/2
nodes=np.array([0,a0,.5,1-a0,1]); jumps=np.array([J,-2*J,2*J,-2*J,J])
def state(t):
    if t>=1:return t,1.,0.,0.
    z=np.maximum(t-nodes,0)
    return t+float(jumps@z**3)/6,1+float(jumps@z**2)/2,float(jumps@z),float(jumps@(t>=nodes))
def integrate(f,tau,N):
    breaks=sorted(set([0,tau]+[float(s) for s in nodes if 0<s<tau]+[i/(4*N) for i in range(1,int(4*N*tau)+1) if i/(4*N)<tau]))
    return sum(quad(f,s,t,epsabs=1e-14,epsrel=5e-12)[0] for s,t in zip(breaks,breaks[1:]))
def value_records(t,tau,rs):
    x,v,a,j=state(t)
    return sum(c*h(tau-t,r)*Q(x,s)*a**p*j**q*v**(-d) for c,r,s,p,q,d in rs)
checks=[]
for N in [1,2,7,19]:
  for tau in [.08,.4,.999,1,1.17,2.6,5.8]:
    original=integrate(lambda t:h(tau-t)*P1(state(t)[0],N)*state(t)[1],tau,N)
    primitive=integrate(lambda t:h(tau-t,1)*P(state(t)[0],N),tau,N)
    cont=integrate(lambda t: math.cos(twopi*N*state(t)[0])*value_records(t,tau,drecords)*state(t)[1],tau,N)
    atoms=0
    for s,dj in zip(nodes[1:],jumps[1:]):
      if s<tau:
        x,v,a,j=state(float(s))
        atoms += math.cos(twopi*N*x)*(-dj*h(tau-s,1)*Q(x)/v**4)
    x,v,a,j=state(tau); boundary=-6*Q(x)/v**3*math.cos(twopi*N*x)
    bv=A/(twopi*N)**4*(boundary+cont+atoms)
    bound=A/(twopi*N)**4*(2*J*3*S+C0)
    checks.append(dict(N=N,tau=tau,original=original,primitive=primitive,bv=bv,bound=bound,bv_boundary=A/(twopi*N)**4*boundary))
I=quad(lambda t:h(1-t,1)*Q(t),0,1,epsabs=1e-14)[0]
witness=[]
for N in [1,2,3,4,8,16,32,64,128]:
    def yt(t):
        eta=J*Q(N*t)/(d0*N**3)
        return h(1-t,1)*P(t+eta,N)
    y=integrate(yt,1,N)
    lead=A*J*I/(d0*N**3)
    witness.append(dict(N=N,y=y,N3_y=N**3*y,leading=lead,error=abs(y-lead),error_bound=A*Cstar/N**4))
# Independent finite LP checks of the phase envelope on a 200-cell acceleration grid.
n=200; ds=1/n; left=np.arange(n)*ds
Aeq=np.array([np.full(n,ds),(1-left)*ds-ds*ds/2])
phasechecks=[]
def phaseplus(t):
    return t+(t*t/2-max(t-.25,0)**2+max(t-.75,0)**2)
for t in [.05,.15,.25,.35,.5,.65,.75,.85,.95]:
    coeff=(np.maximum(t-left,0)**2-np.maximum(t-left-ds,0)**2)/2
    opt=linprog(-coeff,A_eq=Aeq,b_eq=[0,0],bounds=[(-1,1)]*n,method='highs')
    phasechecks.append(dict(t=t,lp=t-opt.fun,envelope=phaseplus(t),success=bool(opt.success)))
out={"status":"ordinary floating point diagnostics only", "constants":dict(Ccont=Ccont,C2=C2,S=S,B0=B0,C0=C0,I0=I0,I=I,G1=G1,G3=G3,CR=CR,Cstar=Cstar,N0=N0,alpha=alpha,beta=beta,gamma=gamma,asymptotic_N3_y=A*J*I/d0),"identity_checks":checks,"max_original_primitive_error":max(abs(c['original']-c['primitive']) for c in checks),"max_original_bv_error":max(abs(c['original']-c['bv']) for c in checks),"witness_checks":witness,"phase_envelope_lp_checks":phasechecks}
assert max(abs(c['original']-c['primitive']) for c in checks)<1e-10
assert max(abs(c['original']-c['bv']) for c in checks)<1e-10
assert all(c['error']<=c['error_bound'] for c in witness)
assert all(abs(c['lp']-c['envelope'])<1e-8 for c in phasechecks)
path=pathlib.Path(__file__).with_name('JERK_AUDIT_DIAGNOSTICS.json'); path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['identity_checks','witness_checks','phase_envelope_lp_checks']},indent=2))
print('All checked identities, conservative inequalities, and phase-envelope LP values pass.')
