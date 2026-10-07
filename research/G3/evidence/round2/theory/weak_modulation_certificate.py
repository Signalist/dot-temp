"""All-allocation weak-form modulation exclusion for a declared positive-slack family.

Only computes a sufficient analytic upper-envelope certificate. It does not
solve a free P/Q optimization and is not an interval-arithmetic verification.
"""
from pathlib import Path
import sys,json
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from model import Params,grid,poly_segments,profiles
from envelope import up

def certificate(epsilon,alpha=100.,beta=900.,left=.008,right=.030,par=Params()):
    # Reference cap differs from the frozen energy-tight cap only in its
    # recharge tail, to permit exactly epsilon kJ total net-energy slack.
    c=par.R/(1500*par.v**2); k=par.L/(3000*par.v**2)
    R1=.045; R2=.040+2*.005/3; Sg=.030+2*.005/3; Ss=2*Sg
    mu0=1-2*c*par.p0; demand=c*(alpha**2*Ss+beta**2*Sg)+epsilon
    discr=(R1*mu0)**2-4*c*R2*demand
    if discr<=0:raise ValueError('Reference recharge cap has no increasing-branch root')
    gamma=2*demand/(R1*mu0+np.sqrt(discr))
    Pmax=par.p0+max(alpha,gamma); mu=1-2*c*Pmax
    cap_lip=max(alpha,gamma)/.005
    current_lip=(par.v+(par.R+abs(par.omega)*par.L)*par.imax+par.vdcmax/np.sqrt(3))/par.L
    K=cap_lip+1500*par.v*current_lip
    if epsilon==0:Hdef=0.
    else:
        # Stronger mixed tent inequality, not merely sqrt(K epsilon/mu).
        Hdef=brentq(lambda x:mu*x*x/K+2*c*x**3/(3*K)-epsilon,0,np.sqrt(K*epsilon/mu),xtol=1e-12)
    rho_global=2*k*Pmax*Hdef
    m=poly_segments(grid(par,40),alpha,beta,par)
    def H(t):
        ix=min(m['n']-1,max(0,int(np.searchsorted(m['t'],t,side='right')-1)))
        x=(t-m['t'][ix])/m['h'][ix]
        return par.W0+np.polynomial.polynomial.polyval(x,m['offset'][ix])+up(t,par)[1]
    width=right-left
    if not (.005<=left<right<=.035):raise ValueError('Use a window within first constant-current plateau')
    mid=.5*(left+right); pval=profiles(mid,alpha,beta,par)
    id0=pval['p']/(1500*par.v); iq0=pval['q']/(1500*par.v)
    ed=par.v-par.R*id0+par.omega*par.L*iq0
    # For 0<=deltaP<=Pbar, the exact favorable inductive reduction
    # k*deltaP*(2Pbar-deltaP) saturates at the active-current energy.
    local_def=min(float(pval['p']),Hdef)
    rho=k*local_def*(2*float(pval['p'])-local_def)
    Mbar=ed*width/2
    # psi=(sin²(pi x),0). Its q error coefficient is omega L psi_d>=0,
    # so Q>=Qmin cannot reduce the weak voltage integral.
    adplus=np.sqrt((par.L*np.pi/width)**2+(par.R/2)**2)-par.R/2
    Epsi=epsilon*adplus/(mu*1500*par.v)
    kappa=1/np.sqrt(1500*par.Cdc)
    rhs=kappa*quad(lambda t:np.sin(np.pi*(t-left)/width)**2*np.sqrt(min(par.Wmax,H(t)+rho)),left,right,
                   epsabs=1e-13,epsrel=1e-12,points=[x for x in m['t'] if left<x<right],limit=200)[0]
    return dict(alpha_kW=alpha,beta_kvar=beta,epsilon_kJ=epsilon,gamma_kW=float(gamma),Pmax_kW=float(Pmax),
                mu=float(mu),K_kW_per_s=float(K),deficit_amplitude_bound_kW=float(Hdef),rho_kJ=float(rho),rho_coarse_kJ=float(rho_global),
                window_s=[left,right],Mbar_kV_s=float(Mbar),error_kV_s=float(Epsi),rhs_kV_s=float(rhs),
                margin_kV_s=float(Mbar-Epsi-rhs),excluded=bool(Mbar-Epsi-rhs>1e-10))

if __name__=='__main__':
    # Freeze the window before computing its positive-slack limit.
    left,right=.008,.030
    zero=certificate(0,left=left,right=right)
    limit=brentq(lambda eps:certificate(eps,left=left,right=right)['margin_kV_s'],0,10,xtol=1e-11)
    checks=[certificate(eps,left=left,right=right) for eps in [0,.001,.005,.01,.05,.1,limit]]
    result={'scope':'Same physical device, fixed workload; P<=reference cap and Q>=reference floor; full W,B,current recovery; recharge cap expanded to allow epsilon kJ net-energy slack.',
      'test_function':'psi=(sin²(pi(t-.008)/.022),0) on [.008,.030]s; zero elsewhere',
      'zero_slack_margin':zero,'positive_slack_exclusion_limit_kJ':limit,'checks':checks,
      'warning':'Analytic sufficient bound evaluated in floating point; no interval-arithmetic claim. Numerical non-exclusion above this limit is not feasibility.'}
    Path(__file__).with_name('weak_modulation_results.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
