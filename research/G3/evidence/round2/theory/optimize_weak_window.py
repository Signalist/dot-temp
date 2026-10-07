"""Deterministic predeclared d-axis sine-window grid for a sharper sufficient bound.
Every selected window is re-evaluated by the independent-form quad certificate.
"""
from pathlib import Path
import json,sys
import numpy as np
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss
from weak_modulation_certificate import certificate
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from model import Params
from envelope import up
p=Params();alpha=100.;c=p.R/(1500*p.v**2);k=p.L/(3000*p.v**2)
Pmax=p.p0+alpha;mu=1-2*c*Pmax
K=alpha/.005+1500*p.v*(p.v+(p.R+abs(p.omega)*p.L)*p.imax+p.vdcmax/np.sqrt(3))/p.L
nodes,weights=leggauss(160)
# Declared grid: 16 left endpoints, 25 right endpoints; only width>=5ms.
windows=[(a,b) for a in np.linspace(.005,.020,16) for b in np.linspace(.011,.035,25) if b-a>=.005-1e-12]
result=[]
for eps in [0,.001,.01,.1,1.]:
    hdef=0 if eps==0 else brentq(lambda x:mu*x*x/K+2*c*x**3/(3*K)-eps,0,np.sqrt(K*eps/mu))
    d=min(p.p0-alpha,hdef);rho=k*d*(2*(p.p0-alpha)-d)
    best=None
    for left,right in windows:
        w=right-left;t=left+(nodes+1)*w/2;weight=weights*w/2
        shape=np.sin(np.pi*(t-left)/w)**2
        C=up(t,p)[1]
        E=eps/(mu*1500*p.v)*(np.sqrt((p.L*np.pi/w)**2+(p.R/2)**2)-p.R/2)
        def margin(beta):
            ramp=.005*(-(alpha+p.Aload)/2+c*p.p0*alpha-c*(alpha**2+beta**2)/3)
            slope=-alpha-p.Aload+2*c*p.p0*alpha-c*alpha**2-c*beta**2
            A=ramp+(t-.005)*slope-k*((p.p0-alpha)**2+beta**2-p.p0**2)
            H=p.W0+A+C+rho
            ed=p.v-p.R*(p.p0-alpha)/(1500*p.v)+p.omega*p.L*beta/(1500*p.v)
            return ed*w/2-E-np.sum(weight*shape*np.sqrt(np.minimum(p.Wmax,H)))/np.sqrt(1500*p.Cdc)
        if margin(700)>=0: threshold=700.
        elif margin(1100)<=0: continue
        else: threshold=brentq(margin,700,1100,xtol=1e-8)
        if best is None or threshold<best[0]:best=(threshold,left,right)
    beta,left,right=best
    exact=certificate(eps,alpha,beta,left,right,p)
    # Add tiny margin to create an excluded value rather than report the root
    # itself as strict exclusion; the threshold remains a numerical boundary.
    check=certificate(eps,alpha,beta+.01,left,right,p)
    result.append({'epsilon_kJ':eps,'selected_window_s':[left,right],
       'upper_threshold_beta_kvar':beta,'quad_margin_at_threshold_kV_s':exact['margin_kV_s'],
       'verified_excluded_beta_kvar':beta+.01,'verified_margin_kV_s':check['margin_kV_s']})
output={'alpha_kW':alpha,'grid_windows':len(windows),'left_grid':'0.005:0.001:0.020',
 'right_grid':'0.011:0.001:0.035','minimum_width_s':.005,'Gauss_Legendre_order':160,
 'scope':'Valid sufficient weak-form all-allocation outer cuts; optimizing the chosen test does not establish exact capacity.',
 'results':result}
Path(__file__).with_name('optimized_weak_windows.json').write_text(json.dumps(output,indent=2))
print(json.dumps(output,indent=2))
