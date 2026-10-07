"""Synthetic import-side compute buffer model. kW, kJ, kA, kV, seconds."""
from dataclasses import dataclass,asdict
import numpy as np
from numpy.polynomial import polynomial as P
from scipy.integrate import quad
@dataclass(frozen=True)
class Params:
    v:float=np.sqrt(2/3)*.690
    omega:float=2*np.pi*50
    L:float=.0003
    R:float=.005
    Cdc:float=.03
    vdc0:float=1.2
    vdcmin:float=1.08
    vdcmax:float=1.32
    imax:float=1.5
    D0:float=650.
    Aload:float=300.
    bmax:float=450.
    umax:float=450.
    ramp:float=30000.
    tau:float=.005
    delay:float=.001
    B0:float=50.
    Bmin:float=0.
    Bmax:float=100.
    T:float=.2
    @property
    def W0(self): return 500*self.Cdc*self.vdc0**2
    @property
    def Wmin(self): return 500*self.Cdc*self.vdcmin**2
    @property
    def Wmax(self): return 500*self.Cdc*self.vdcmax**2
    @property
    def losscoef(self): return self.R/(1500*self.v**2)
    @property
    def p0(self):
        c=self.losscoef
        return 2*self.D0/(1+np.sqrt(1-4*c*self.D0))
    def dict(self): return asdict(self)

def pulse(t,start=0):
    return np.interp(np.asarray(t)-start,[0,.005,.035,.040],[0,1,1,0],left=0,right=0)
def recovery(t):
    return np.interp(np.asarray(t),[.125,.130,.170,.175],[0,1,1,0],left=0,right=0)
def base_knots(par):
    return np.unique([0,par.delay,.005,.035,.040,.070,.075,.105,.110,.125,.130,.170,.175,par.T])
def grid(par,n):
    return np.unique(np.round(np.r_[np.linspace(0,par.T,n+1),base_knots(par)],12))
def profiles(t,alpha,beta,par=Params()):
    t=np.asarray(t)
    g=pulse(t); gm=pulse(t,.070); s=gm-g; r=recovery(t)
    # Integrals of the fixed linear shapes: each 35ms pulse has 100/3? ms square.
    g2=.030+2*.005/3
    s2=2*g2; ra=.045; r2=.040+2*.005/3
    c=par.losscoef
    a=c*r2; bb=-ra*(1-2*c*par.p0); cc=c*(alpha**2*s2+beta**2*g2)
    gamma=0. if cc==0 else 2*cc/(-bb+np.sqrt(bb*bb-4*a*cc))
    return {'p':par.p0+alpha*s+gamma*r,'q':beta*g,'d':par.D0+par.Aload*(g-gm),'gamma':float(gamma)}

def poly_segments(t,alpha,beta,par=Params()):
    vals=profiles(t,alpha,beta,par)
    h=np.diff(t); n=len(h); i=np.stack([vals['p'],vals['q']],axis=1)/(1500*par.v)
    Woffset=np.zeros((n,4)); emod=np.zeros((n,4)); Z=np.zeros((n,4)); loss=np.zeros((n,3))
    A=0.; zinitial=750*par.L*np.sum(i[0]**2)
    integrated=0.
    for k in range(n):
        ik=i[k]; di=i[k+1]-ik
        norm=np.array([ik@ik,2*ik@di,di@di])
        z=750*par.L*norm; ls=1500*par.R*norm
        e0=np.array([par.v,0])-par.R*ik-par.L*di/h[k]-par.omega*par.L*np.array([-ik[1],ik[0]])
        de=-par.R*di-par.omega*par.L*np.array([-di[1],di[0]])
        esq=np.array([e0@e0,2*e0@de,de@de])
        pd=np.array([vals['p'][k]-vals['d'][k],vals['p'][k+1]-vals['p'][k]-(vals['d'][k+1]-vals['d'][k]),0])-ls
        ap=np.r_[integrated,h[k]*pd/np.arange(1,4)]
        ap[:3]-=z; ap[0]+=zinitial
        Woffset[k]=ap; emod[k,:3]=1500*par.Cdc*esq; Z[k,:3]=z; loss[k]=ls
        integrated+=h[k]*np.sum(pd/np.arange(1,4))
    return dict(t=t,h=h,n=n,i=i,offset=Woffset,modfloor=emod,z=Z,loss=loss,profiles=vals,
                energy_residual=float(integrated),final_A=float(np.sum(Woffset[-1])))
