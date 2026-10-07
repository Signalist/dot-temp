"""Independent scalar extreme actuator envelope and continuous necessary bound."""
import numpy as np
from scipy.optimize import minimize_scalar
from model import Params,grid,poly_segments

def up(t,par=Params()):
    t=np.maximum(np.asarray(t)-par.delay,0)
    r=par.ramp; u=par.umax; tau=par.tau
    if tau==0:
        tr=u/r; s=np.minimum(t,tr); b=np.minimum(r*t,u); C=.5*r*s*s+u*np.maximum(t-tr,0)
    else:
        tr=max((u-r*tau)/r,0)
        s=np.minimum(t,tr); w=np.maximum(t-tr,0)
        b=np.where(t<=tr,r*t,u-(u-r*tr)*np.exp(-w/tau))
        C=.5*r*s*s+u*w-(u-r*tr)*tau*(-np.expm1(-w/tau))
    return b,C

def prefix_outer(alpha,beta,par=Params()):
    m=poly_segments(grid(par,40),alpha,beta,par); best=(np.inf,None,None)
    for k,h in enumerate(m['h']):
        for tag,bound in [('dc',np.array([par.Wmin,0,0,0])),('mod',m['modfloor'][k])]:
            co=np.r_[par.W0,0,0,0]+m['offset'][k]-bound
            f=lambda x:np.polynomial.polynomial.polyval(x,co)+up(m['t'][k]+h*x,par)[1]
            r=minimize_scalar(f,bounds=(0,1),method='bounded',options={'xatol':1e-13})
            v,x=min([(f(0),0),(f(1),1),(r.fun,r.x)])
            if v<best[0]:best=(float(v),float(m['t'][k]+h*x),tag)
    return {'minimum_margin_kJ':best[0],'time_s':best[1],'constraint':best[2],'excluded':best[0]<-1e-6,'scope':'necessary prefix max-port envelope; favorable relaxation omits other-state and terminal constraints'}
if __name__=='__main__':
 for a,q in [(0,0),(100,0),(100,600),(100,900),(200,0),(200,900)]:print(a,q,prefix_outer(a,q))
