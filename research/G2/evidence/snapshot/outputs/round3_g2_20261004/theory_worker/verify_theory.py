#!/usr/bin/env python3
"""Deterministic diagnostics for the frozen protocol; no validated numerics claims."""
from pathlib import Path
import json, math, hashlib
import numpy as np
from numpy.polynomial.legendre import leggauss
import sympy as sp

ROOT=Path(__file__).resolve().parent
protocol=json.loads((ROOT/'DIAGNOSTIC_PROTOCOL.json').read_text())
J=protocol['J']; A=protocol['A']; w=2*np.pi; d0=6*w**3; l=.9
Qb=np.array([4.,6*np.pi,16*np.pi**2,48*np.pi**3])
Kb={1:54*np.exp(-3),2:24.,3:48.,4:90.}
base=[(1,3,0,0,0,3),(-2,2,1,0,0,2),(3,2,0,1,0,4),(1,1,2,0,0,1),(-2,1,1,1,0,3),(3,1,0,2,0,5),(-1,1,0,0,1,4)]
third=[]
for c,r,s,p,q,d in base:
    third += [(-c,r+1,s,p,q,d+1),(c,r,s+1,p,q,d),(-c*d,r,s,p+1,q,d+2)]
    if p: third += [(c*p,r,s,p-1,q+1,d+1)]
Ccont=sum(abs(c)*Qb[s]*Kb[r]*J**q*l**(1-d) for c,r,s,p,q,d in third)
C2=sum(abs(c)*Qb[s]*Kb[r]*J**q*l**(1-d) for c,r,s,p,q,d in base)
S=3*Qb[0]/l**4; B0=6*Qb[0]/l**3; C0=B0+Ccont
I0=2/(9*np.e)
G1=7*Qb[0]+3*Qb[1]
G3=Qb[0]*Kb[4]+3*Qb[1]*Kb[3]+3*Qb[2]*Kb[2]+Qb[3]*Kb[1]
CR=8/(np.e*d0**2)*(w*Qb[0]+2*Qb[1]+Qb[2]/w)
Cs=G3/w**4+J*(5*G1/d0+2*Qb[1]/(np.pi*d0*np.e))+J**2*CR
N0=math.ceil(2*d0*Cs/(J*I0)); alpha=np.pi*I0/(24*S); beta=C0/(2*J*S); gamma=A*J*I0/(4*d0)

def Q(x, r=0):
    z=w*np.asarray(x)
    if r==0: return (1-np.cos(z))**2
    if r==1: return w*(2*np.sin(z)-np.sin(2*z))
    if r==2: return w**2*(2*np.cos(z)-2*np.cos(2*z))
    if r==3: return w**3*(-2*np.sin(z)+4*np.sin(2*z))
    raise ValueError(r)

def H(t, r=0):
    t=np.asarray(t); e=np.exp(-t)
    return e*([t**3,3*t**2-t**3,6*t-6*t**2+t**3,6-18*t+9*t**2-t**3,-24+36*t-12*t**2+t**3][r])

def P(x,N, r=0):
    k=w*N
    if r==0: return -A/k*Q(x)*np.sin(k*x)
    return -A*(Q(x)*np.cos(k*x)+Q(x,1)*np.sin(k*x)/k)

knots=np.array([(2-np.sqrt(2))/4,.5,(2+np.sqrt(2))/4])
def clock(t, label, N=1):
    t=np.asarray(t); active=t<1
    if label=='nominal': return t, np.ones_like(t), np.zeros_like(t), np.zeros_like(t)
    if label=='witness':
        eta=J*Q(N*t)/(d0*N**3); dv=J*Q(N*t,1)/(d0*N**2)
        a=J*Q(N*t,2)/(d0*N); j=J*Q(N*t,3)/d0
    else:
        M=1 if label=='universal_plus_one_cell' else 2
        sig=1 if M==1 else -1
        z=np.mod(M*t,1.)
        eta=z**3/6; dv=z**2/2; a=z.copy(); j=np.ones_like(t)
        for knot,delta in zip(knots,[-2.,2.,-2.]):
            pos=np.maximum(z-knot,0)
            eta+=delta*pos**3/6; dv+=delta*pos**2/2; a+=delta*pos; j+=delta*(z>knot)
        eta*=sig*J/M**3; dv*=sig*J/M**2; a*=sig*J/M; j*=sig*J
    return t+np.where(active,eta,0),1+np.where(active,dv,0),np.where(active,a,0),np.where(active,j,0)

def events(label):
    if label=='nominal': return []
    M=1 if label=='universal_plus_one_cell' else 2
    sig=1 if M==1 else -1
    out=[]
    for cell in range(M):
        out += [((cell+z)/M,sig*J*d) for z,d in zip(knots,[-2.,2.,-2.])]
        if cell<M-1: out += [((cell+1)/M,2*sig*J)]
    return sorted(out)

def quadrature(tau,N,order,label='nominal'):
    panels=max(1,math.ceil(protocol['panels_per_nominal_workload_cycle']*N*tau))
    splits=list(np.linspace(0,tau,panels+1))+[t for t,d in events(label) if 0<t<tau]
    if tau>1: splits+=[1.]
    splits=np.unique(splits); left=splits[:-1]; right=splits[1:]
    x,weights=leggauss(order)
    ts=((left+right)[:,None]/2+(right-left)[:,None]*x/2).ravel()
    ws=((right-left)[:,None]*weights/2).ravel()
    return ts,ws

def integrate(tau,N,label,order,kind):
    ts,ws=quadrature(tau,N,order,label if label!='witness' else 'nominal')
    theta,v,a,j=clock(ts,label,N); k=w*N
    if kind=='power': return float(ws@(H(tau-ts)*P(theta,N,1)*v))
    if kind=='phase': return float(ws@(H(tau-ts,1)*P(theta,N)))
    if kind=='bv':
        f3=np.zeros_like(ts)
        for c,r,s,p,q,d in third:
            f3+=c*H(tau-ts,r)*Q(theta,s)*a**p*j**q*v**(-d)
        cont=float(ws@(f3*np.cos(k*theta)*v)); atom=0.
        for ti,delta in events(label):
            if ti<tau:
                xi,vi,ai,ji=clock(np.array([ti]),label,N)
                atom+=float(-delta*H(tau-ti,1)*Q(xi[0])/vi[0]**4*np.cos(k*xi[0]))
        xb,vb,ab,jb=clock(np.array([tau]),label,N)
        boundary=-6*Q(xb[0])/vb[0]**3*np.cos(k*xb[0])
        return float(A/k**4*(boundary+cont+atom)),float(A/k**4*boundary),float(A/k**4*atom)
    raise ValueError(kind)

# Symbolic monomial differentiation, independent expression differential operator.
a,j,v=sp.symbols('a j v', nonzero=True)
HH=sp.symbols('H0:6'); QQ=sp.symbols('Q0:5')
expr=HH[1]*QQ[0]/v
D=lambda f: sp.expand(sum(-sp.diff(f,HH[r])*HH[r+1]/v for r in range(5))+sum(sp.diff(f,QQ[s])*QQ[s+1] for s in range(4))+sp.diff(f,v)*a/v+sp.diff(f,a)*j/v)
f2=sum(c*HH[r]*QQ[s]*a**p*j**q*v**(-d) for c,r,s,p,q,d in base)
f3=sum(c*HH[r]*QQ[s]*a**p*j**q*v**(-d) for c,r,s,p,q,d in third)
assert sp.simplify(D(D(expr))-f2)==0
assert sp.simplify(D(f2)-f3)==0
x=sp.symbols('x',real=True); rt=sp.sqrt(2); kk=[(2-rt)/4,sp.Rational(1,2),(2+rt)/4]
bounds=[0]+kk+[1]
mom=[sp.simplify(sum((-1)**z*(bounds[z+1]**(r+1)-bounds[z]**(r+1))/(r+1) for z in range(4))) for r in range(3)]
assert mom==[0,0,0]
mean=sp.integrate((1-sp.cos(2*sp.pi*x))**2*sp.cos(2*sp.pi*x),(x,0,1)); assert mean==-1

rows=[]
for N in protocol['identity_N']:
    for label in protocol['identity_clocks']:
        for tau in protocol['observation_times']:
            vals={}
            for order in protocol['quadrature_orders']:
                yp=integrate(tau,N,label,order,'power'); ye=integrate(tau,N,label,order,'phase')
                yb,bterm,atoms=integrate(tau,N,label,order,'bv')
                vals[str(order)]={'power':yp,'phase':ye,'bv':yb,'boundary':bterm,'atoms':atoms}
            a16=vals['16']; a32=vals['32']
            jumps=len(events(label)); upper=A/(w*N)**4*(2*J*jumps*S+C0)
            row={'N':N,'clock':label,'tau':tau,'values':vals,'identity_error':max(abs(a32['power']-a32['phase']),abs(a32['power']-a32['bv'])),'refinement_error':max(abs(a32[key]-a16[key]) for key in ['power','phase','bv']),'upper':upper,'bound_holds':abs(a32['power'])<=upper}
            rows.append(row)
# High-witness asymptotic, fixed endpoint integral.
ts,ws=quadrature(1,1,64)
I=float(ws@(H(1-ts,1)*Q(ts))); lead=A*J*I/d0
witness=[]
for N in protocol['witness_N']:
    y16=integrate(1,N,'witness',16,'phase'); y32=integrate(1,N,'witness',32,'phase'); yp=integrate(1,N,'witness',32,'power')
    ts=np.linspace(0,1,10001); th,vv,aa,jj=clock(ts,'witness',N)
    rem=abs(y32-lead/N**3); err_bound=A*Cs/N**4
    witness.append({'N':N,'y':y32,'N3_y':N**3*y32,'asymptotic_limit':lead,'scaled_relative_error':abs(N**3*y32/lead-1),'power_phase_error':abs(yp-y32),'refinement_error':abs(y32-y16),'remainder':rem,'remainder_upper':err_bound,'remainder_bound_holds':rem<=err_bound,'sampled_v_range':[float(vv.min()),float(vv.max())],'sampled_abs_acceleration':float(abs(aa).max()),'sampled_abs_jerk':float(abs(jj).max())})
summary={'protocol_sha256':hashlib.sha256((ROOT/'DIAGNOSTIC_PROTOCOL.json').read_bytes()).hexdigest(),'interpretation':protocol['interpretation'],'symbolic_checks':{'F_second_derivative':True,'F_third_derivative':True,'universal_jerk_moments':[str(z) for z in mom],'witness_fourier_mean':str(mean)},'analytic_constants':{'Q_bounds':Qb.tolist(),'kernel_L1_bounds':Kb,'J':J,'A':A,'d0':d0,'C_cont':Ccont,'C2':C2,'S':S,'B0':B0,'C0':C0,'I0':I0,'G1':G1,'G3':G3,'C_R':CR,'C_star':Cs,'N0':N0,'alpha':alpha,'beta':beta,'gamma':gamma,'upper_B':135*np.exp(-3)},'quadrature_I':I,'asymptotic_leading_constant':lead,'max_identity_error':max(r['identity_error'] for r in rows),'max_refinement_error':max(r['refinement_error'] for r in rows),'largest_boundary_magnitude':max(abs(r['values']['32']['boundary']) for r in rows),'largest_atom_magnitude':max(abs(r['values']['32']['atoms']) for r in rows),'all_sampled_bounds_hold':all(r['bound_holds'] for r in rows) and all(r['remainder_bound_holds'] for r in witness),'identity_rows':rows,'witness_rows':witness}
assert summary['max_identity_error']<2e-12
assert summary['max_refinement_error']<2e-12
assert summary['all_sampled_bounds_hold']
(ROOT/'THEORY_DIAGNOSTICS.json').write_text(json.dumps(summary,indent=2,default=lambda x: x.item() if isinstance(x,np.generic) else str(x)))
print(json.dumps({k:v for k,v in summary.items() if k not in ('identity_rows','witness_rows')},indent=2))
print('witness rows:')
for row in witness: print(json.dumps(row,default=lambda x: x.item() if isinstance(x,np.generic) else str(x)))
