"""Vector sine-bump weak cut with a joint one-sided energy-budget dual.
On the constant positive-Q floor plateau, error is O(epsilon), not a separate
L2 Q penalty: the same energy budget pays for both active and reactive errors.
"""
from pathlib import Path
import sys,json
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from model import Params
from envelope import up
p=Params();alpha=100.;c=p.R/(1500*p.v**2);k=p.L/(3000*p.v**2);Gp=1500*p.v
Pfirst=p.p0-alpha;Pmax=p.p0+alpha;mu=1-2*c*Pmax;mu_local=1-2*c*Pfirst
K=alpha/.005+Gp*(p.v+(p.R+abs(p.omega)*p.L)*p.imax+p.vdcmax/np.sqrt(3))/p.L
nodes,weights=leggauss(160)
def values(eps,beta,left,right,angle,use_quad=False):
    w=right-left;nd=np.cos(angle);nq=np.sin(angle)
    hdef=0 if eps==0 else brentq(lambda x:mu*x*x/K+2*c*x**3/(3*K)-eps,0,np.sqrt(K*eps/mu))
    delta=min(Pfirst,hdef);rho=k*delta*(2*Pfirst-delta)
    dd=p.R*nd+p.omega*p.L*nq;dq=p.R*nq-p.omega*p.L*nd
    adplus=-dd/2+np.sqrt((p.L*np.pi*nd/w)**2+(dd/2)**2)
    aqminus=dq/2+np.sqrt((p.L*np.pi*nq/w)**2+(dq/2)**2)
    active_ratio=adplus/mu_local;reactive_ratio=aqminus/(2*c*beta)
    E=eps/Gp*max(active_ratio,reactive_ratio)
    ed=p.v-p.R*Pfirst/Gp+p.omega*p.L*beta/Gp
    eq=-p.R*beta/Gp-p.omega*p.L*Pfirst/Gp
    M=(nd*ed+nq*eq)*w/2
    ramp=.005*(-(alpha+p.Aload)/2+c*p.p0*alpha-c*(alpha**2+beta**2)/3)
    slope=-alpha-p.Aload+2*c*p.p0*alpha-c*alpha**2-c*beta**2
    def H(t): return p.W0+ramp+(t-.005)*slope-k*(Pfirst**2+beta**2-p.p0**2)+up(t,p)[1]+rho
    if use_quad:
        rhs=quad(lambda t:np.sin(np.pi*(t-left)/w)**2*np.sqrt(min(p.Wmax,H(t))),left,right,
                 epsabs=1e-13,epsrel=1e-12,points=[q for q in [.011] if left<q<right],limit=200)[0]/np.sqrt(1500*p.Cdc)
    else:
        t=left+(nodes+1)*w/2
        rhs=np.sum(weights*w/2*np.sin(np.pi*(t-left)/w)**2*np.sqrt(np.minimum(p.Wmax,H(t))))/np.sqrt(1500*p.Cdc)
    return dict(margin_kV_s=float(M-E-rhs),Mbar_kV_s=float(M),error_kV_s=float(E),rhs_kV_s=float(rhs),
                active_error_ratio=float(active_ratio),reactive_error_ratio=float(reactive_ratio),rho_kJ=float(rho))
if __name__=='__main__':
    # Finite declared family, not a claim of optimality over all weak tests.
    windows=[(a,b) for a in np.linspace(.005,.020,16) for b in np.linspace(.011,.035,25) if b-a>=.005-1e-12]
    angles=np.linspace(-.18,0,19)
    out=[]
    for eps in [0,.001,.01,.1,1.]:
        best=None
        for a,b in windows:
            for angle in angles:
                f=lambda beta:values(eps,beta,a,b,angle)['margin_kV_s']
                if f(1100)<=0:continue
                threshold=brentq(f,700,1100,xtol=1e-7)
                if best is None or threshold<best[0]:best=(threshold,a,b,float(angle))
        beta,a,b,angle=best
        out.append(dict(epsilon_kJ=eps,upper_threshold_beta_kvar=float(beta),window_s=[a,b],angle_rad=angle,
                        quad_at_threshold=values(eps,beta,a,b,angle,True),
                        verified_excluded_beta_kvar=float(beta+.01),quad_exclusion=values(eps,beta+.01,a,b,angle,True)))
    result=dict(alpha_kW=alpha,windows=len(windows),angles=len(angles),angle_range_rad=[-.18,0],angle_step_rad=.01,
       assumption='First-event positive Q floor; reference gamma stays below100kW for the reported beta/epsilon range, so Pmax and cap Lipschitz constants are valid.',
       scope='Optimized within a finite weak-test family only; exact all-allocation sufficient exclusion, numerically evaluated.',results=out)
    Path(__file__).with_name('vector_weak_results.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
