"""All-allocation first-event DC-underenergy witness, independent of later recharge."""
from pathlib import Path
import sys,json
import numpy as np
from scipy.optimize import minimize_scalar,brentq
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from model import Params,grid,poly_segments,profiles
from envelope import up

def evaluate(alpha=200.,beta=0.,epsilon=0.,unlimited_slack=False,par=Params()):
    c=par.R/(1500*par.v**2); k=par.L/(3000*par.v**2)
    R1=.045;R2=.040+2*.005/3;Sg=.030+2*.005/3;Ss=2*Sg
    demand=c*(alpha*alpha*Ss+beta*beta*Sg)+epsilon
    gamma=2*demand/(R1*(1-2*c*par.p0)+np.sqrt((R1*(1-2*c*par.p0))**2-4*c*R2*demand))
    Pmax=par.p0+max(alpha,gamma);mu=1-2*c*Pmax
    ilip=(par.v+(par.R+abs(par.omega)*par.L)*par.imax+par.vdcmax/np.sqrt(3))/par.L
    K=max(alpha,gamma)/.005+1500*par.v*ilip
    hdef=np.inf if unlimited_slack else (0. if epsilon==0 else brentq(lambda x:mu*x*x/K+2*c*x**3/(3*K)-epsilon,0,np.sqrt(K*epsilon/mu)))
    m=poly_segments(grid(par,40),alpha,beta,par)
    best=None
    for j,h in enumerate(m['h']):
        if m['t'][j]>=.04-1e-12:break
        def pieces(x):
            t=m['t'][j]+h*x;p=float(profiles(t,alpha,beta,par)['p'])
            A=np.polynomial.polynomial.polyval(x,m['offset'][j]); C=up(t,par)[1]
            d=min(p,hdef);rho=k*d*(2*p-d)
            fixed=par.W0+A+C-par.Wmin
            return fixed+rho,dict(time_s=float(t),fixed_margin_kJ=float(fixed),favorable_inductive_release_kJ=float(rho),
                                 all_allocation_margin_kJ=float(fixed+rho),Pcap_kW=p)
        q=minimize_scalar(lambda x:pieces(x)[0],bounds=(0,1),method='bounded',options={'xatol':1e-14})
        candidate=min([pieces(0),pieces(1),pieces(q.x)],key=lambda z:z[0])
        if best is None or candidate[0]<best[0]:best=candidate
    return dict(alpha_kW=alpha,beta_kvar=beta,epsilon_kJ=None if unlimited_slack else epsilon,
                no_late_recharge_limit_needed=unlimited_slack,gamma_kW=None if unlimited_slack else float(gamma),
                excluded=bool(best[0]<-1e-6),**best[1])
if __name__=='__main__':
    result={'scope':'Any time-varying nonnegative import P<=declared first-event cap and Q>=floor; same positive workload, physical current/modulation bounds, initial held command. Later recharge and final recovery are not needed for the unlimited-slack prefix exclusion.',
      'checks':[evaluate(epsilon=e) for e in [0,.001,.005,.01,.05,.1]]+[evaluate(unlimited_slack=True)],
      'warning':'Floating point evaluation of an analytic necessary bound; not interval-arithmetic certification.'}
    Path(__file__).with_name('dc_allocation_results.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
