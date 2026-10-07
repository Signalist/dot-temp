"""Independent weak-form all-allocation exclusion, no src/theory imports.
Build the first plateau's energy offset directly by integrating its affine ramp.
"""
from pathlib import Path
import json,numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq,minimize_scalar
ROOT=Path(__file__).resolve().parents[1]
z=np.load(ROOT/'results/witness_a100_q900_n160.npz');p=json.loads(str(z['par_json']))
V=p['v'];R=p['R'];L=p['L'];tau=p['tau'];r=p['ramp'];U=p['umax'];omega=p['omega'];W0=500*p['Cdc']*p['vdc0']**2;Wmax=500*p['Cdc']*p['vdcmax']**2
S=1500*V;c=R/(1500*V*V);k=L/(3000*V*V)
P0=brentq(lambda x:x-c*x*x-p['D0'],650,1000)
a=100.;q=900.;left=.008;right=.030;width=right-left;Pl=P0-a;Ql=q
Z0=k*P0*P0;Zl=k*(Pl*Pl+Ql*Ql)
# Workload coefficient is fixed +300 kW on the first plateau.
ramp_integral=.005*((-a-p['Aload']+2*c*P0*a)/2-c*(a*a+q*q)/3)
plateau_net=Pl-p['D0']-p['Aload']-c*(Pl*Pl+Ql*Ql)

def charge(t):
 s=max(0,t-p['delay']);switch=U/r-tau
 if s<=switch:return .5*r*s*s
 d=s-switch
 return .5*r*switch*switch+U*d-tau*tau*r*(1-np.exp(-d/tau))

def H(t):return W0+ramp_integral+plateau_net*(t-.005)-Zl+Z0+charge(t)
def psi(t):return np.sin(np.pi*(t-left)/width)**2
def psip(t):return np.pi/width*np.sin(2*np.pi*(t-left)/width)
# Directly optimize coefficient; do not use closed-form trigonometric amplitude.
aa=minimize_scalar(lambda t:-(L*psip(t)-R*psi(t)),bounds=(left,right),method='bounded',options={'xatol':1e-15})
admax=max(0,-aa.fun);ed=V-R*Pl/S+omega*L*Ql/S
Mbar=quad(lambda t:psi(t)*ed,left,right,epsabs=1e-14,epsrel=1e-14)[0]

def gamma(eps):
 # Independent scalar net-energy equality; exact shape moments from elementary integration.
 req=c*(a*a*(2*.03+4*.005/3)+q*q*(.03+2*.005/3))+eps
 return brentq(lambda g:.045*g*(1-2*c*P0)-c*(.04+2*.005/3)*g*g-req,0,1000,xtol=1e-12)
def result(eps):
 gam=gamma(eps);Pmax=P0+max(a,gam);mu=1-2*c*Pmax
 current_slew=(V+(R+omega*L)*p['imax']+p['vdcmax']/np.sqrt(3))/L
 K=max(a,gam)/.005+S*current_slew
 h=0 if eps==0 else brentq(lambda h:mu*h*h/K+2*c*h*h*h/(3*K)-eps,0,np.sqrt(K*eps/mu),xtol=1e-12)
 delta=min(Pl,h);rho=k*delta*(2*Pl-delta)
 error=admax*eps/(S*mu)
 rhs=quad(lambda t:psi(t)*np.sqrt(min(Wmax,H(t)+rho)/(1500*p['Cdc'])),left,right,points=[.011],epsabs=1e-14,epsrel=1e-13)[0]
 return {'epsilon_kJ':eps,'gamma_kW':gam,'Pmax_kW':Pmax,'mu':mu,'K_kW_per_s':K,'deficit_amplitude_bound_kW':h,'rho_kJ':rho,'Mbar_kV_s':Mbar,'error_kV_s':error,'rhs_kV_s':rhs,'margin_kV_s':Mbar-error-rhs}
rs=[result(e) for e in [0,.001,.005,.01,.05,.1,1.0]];root=brentq(lambda e:result(e)['margin_kV_s'],.1,2,xtol=1e-12)
target=json.loads((ROOT/'theory/weak_modulation_results.json').read_text());diff={}
for want in target['checks']:
 got=result(want['epsilon_kJ'])
 for key in got:
  if key in want:diff[key]=max(diff.get(key,0),abs(got[key]-want[key]))
# Early prefix-only all-slack witness for alpha=200, Qfloor=0.
a2=200.;t2=.03561073948454363
# Direct quadrature of first-pulse profile through a fixed time, independent of energy offset.
def g(t):return max(0,min(1,t/.005,(.04-t)/.005))
def net2(t):
 P=P0-a2*g(t);d=p['D0']+p['Aload']*g(t)
 return P-d-c*P*P
netint=quad(net2,0,t2,points=[.005,.035],epsabs=1e-12,epsrel=1e-12)[0]
# Grant arbitrary release of ALL current magnetic energy by dropping Zactual>=0.
ceiling=W0+Z0+netint+charge(t2);Wmin=500*p['Cdc']*p['vdcmin']**2
out={'independence':'No model/admission/theory modules imported. Plateau offset derived from first-ramp integral, cap gamma from an independent scalar balance, weak coefficient from direct scalar maximization, RHS from separate quadrature.','independent_checks':rs,'independent_positive_slack_limit_kJ':root,'max_difference_from_target':diff,'alpha200_q0_all_late_slack_prefix_witness':{'time_s':t2,'W_ceiling_after_granting_all_inductor_release_kJ':ceiling,'Wmin_kJ':Wmin,'upper_ceiling_minus_Wmin_kJ':ceiling-Wmin,'scope':'Any early-time 0<=P<=the same alpha200 cap and Q>=0, same initial state/workload/battery. Arbitrary late recovery slack cannot alter this earlier necessary bound. No exact terminal recovery is needed for this prefix obstruction.'}}
(ROOT/'audit/WEAK_MODULATION_AUDIT.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
