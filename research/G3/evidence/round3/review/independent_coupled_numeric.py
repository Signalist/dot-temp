"""Independent nested adaptive-quadrature check of the proposed prefix certificate.
No imports from the new implementation; constants and identities are explicit.
Floating-point verification only. Outputs stay in review/.
"""
from pathlib import Path
import json
import math
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

OUT=Path(__file__).resolve().parent
V=math.sqrt(2/3)*.690
R=.005
L=.0003
omega=2*math.pi*50
C=.03
Gp=1500*V
c=R/(1500*V*V)
k=L/(3000*V*V)
K_v=math.sqrt(1500*C)
D0=650.
P0=2*D0/(1+math.sqrt(1-4*c*D0))
alpha=100.
P=P0-alpha
m=1-2*c*P
W0=500*C*1.2**2
left=.011292608356252797
right=.023925376064810815
angle=-.10163040739497287
nd=math.cos(angle)
nq=math.sin(angle)
width=right-left

def certificate(beta, lam=0., epsilon=.1):
    # Integral(g)=t-.0025 and integral(g^2)=t-.010/3 on the plateau.
    A=-alpha-300+2*c*P0*alpha
    B=-c*(alpha*alpha+beta*beta)
    def H(t):
        v=t-.011
        Cup=1.5+450*v-.75*(-math.expm1(-v/.005))
        return W0+A*(t-.0025)+B*(t-.010/3)-k*(P*P+beta*beta-P0*P0)+Cup
    def h(t): return math.sin(math.pi*(t-left)/width)**2
    def hp(t): return math.pi/width*math.sin(2*math.pi*(t-left)/width)
    def z(t): return h(t)/(2*K_v*math.sqrt(H(t)))
    def r(t):
        return quad(z,t,right,epsabs=1e-19,epsrel=2e-12,limit=100)[0]
    def coeff(t):
        ht=h(t); hpt=hp(t); zt=z(t); rt=r(t)
        l_d=(L*nd*hpt-(R*nd+omega*L*nq)*ht)/Gp
        l_q=-(L*nq*hpt-(R*nq-omega*L*nd)*ht)/Gp
        return (l_d+2*k*zt*P-rt*m,
                l_q-2*k*zt*beta-rt*2*c*beta,
                k*zt+rt*c)
    def support(t):
        ad,aq,b=coeff(t)
        numer=max(ad-lam*m,0.)**2+max(aq-lam*2*c*beta,0.)**2
        denom=4*(b+lam*c)
        if denom==0:
            return 0. if numer==0 else math.inf
        return numer/denom
    pts=np.linspace(left,right,1501)
    active_intervals=[]
    roots=[]
    for axis in [0,1]:
        vals=[coeff(t)[axis]-lam*(m if axis==0 else 2*c*beta) for t in pts]
        axisroots=[]
        for lo,hi,flo,fhi in zip(pts[:-1],pts[1:],vals[:-1],vals[1:]):
            if flo*fhi<0:
                root=brentq(lambda t:coeff(t)[axis]-lam*(m if axis==0 else 2*c*beta),lo,hi,xtol=1e-15)
                roots.append(root);axisroots.append(root)
        active_intervals.append(axisroots)
    E,Eerr=quad(support,left,right,epsabs=1e-17,epsrel=3e-11,points=sorted(set(roots)),limit=300)
    E+=lam*epsilon
    rhs,rhserr=quad(lambda t:h(t)*math.sqrt(H(t))/K_v,left,right,epsabs=1e-16,epsrel=3e-13,limit=200)
    ed=V-R*P/Gp+omega*L*beta/Gp
    eq=-R*beta/Gp-omega*L*P/Gp
    M=(nd*ed+nq*eq)*width/2
    return dict(beta_kvar=beta,lambda_value=lam,epsilon_kJ=epsilon,
                Mbar_kV_s=M,rhs_kV_s=rhs,support_kV_s=E,
                margin_kV_s=M-rhs-E,
                estimated_rhs_quad_error=rhserr,estimated_support_quad_error=Eerr,
                coefficient_zeroes_s=active_intervals,Hmin_grid_kJ=min(H(t) for t in pts),
                scope='Nested adaptive floating-point quadrature; no interval enclosure')

if __name__=='__main__':
    rows=[certificate(q,lam) for q in [812.2689440942253,812.5,813.] for lam in [0.,1e-10]]
    result=dict(window_s=[left,right],angle_rad=angle,results=rows)
    (OUT/'independent_coupled_numeric.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
