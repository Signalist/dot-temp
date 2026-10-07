"""Independent numerical audit of selected joint-budget vector weak certificates."""
from pathlib import Path
import numpy as np,json
from scipy.integrate import quad
from scipy.optimize import brentq,minimize_scalar
from independent_audit import witness_audit,replay_abc
ROOT=Path(__file__).resolve().parents[1];z=np.load(ROOT/'results/boundary_a100_q808_n320.npz');p=json.loads(str(z['par_json']))
V=p['v'];R=p['R'];L=p['L'];tau=p['tau'];r=p['ramp'];U=p['umax'];omega=p['omega'];Cdc=p['Cdc'];S=1500*V;c=R/(1500*V*V);k=L/(3000*V*V);W0=500*Cdc*p['vdc0']**2;Wmax=500*Cdc*p['vdcmax']**2
P0=brentq(lambda x:x-c*x*x-p['D0'],650,1000);a=100.;Pl=P0-a;Pmax=P0+a;mu=1-2*c*Pmax;mulocal=1-2*c*Pl
K=a/.005+S*(V+(R+omega*L)*p['imax']+p['vdcmax']/np.sqrt(3))/L

def charge(t):
 s=max(0,t-p['delay']);tr=U/r-tau
 return .5*r*s*s if s<=tr else .5*r*tr*tr+U*(s-tr)-tau*tau*r*(1-np.exp(-(s-tr)/tau))
def numerical_max(fn,left,right):
 ts=np.linspace(left,right,10001);ys=np.array([fn(t) for t in ts]);j=int(np.argmax(ys));low=ts[max(0,j-1)];high=ts[min(len(ts)-1,j+1)]
 opt=minimize_scalar(lambda t:-fn(t),bounds=(low,high),method='bounded',options={'xatol':1e-15})
 return max(0,float(ys[j]),-float(opt.fun))
def gamma(eps,beta):
 target=c*(a*a*(2*.03+4*.005/3)+beta*beta*(.03+2*.005/3))+eps
 return brentq(lambda g:.045*g*(1-2*c*P0)-c*(.04+2*.005/3)*g*g-target,0,1000,xtol=1e-12)
def calc(eps,beta,left,right,theta,coeff=None):
 width=right-left;n=np.array([np.cos(theta),np.sin(theta)]);D=np.array([[R,-omega*L],[omega*L,R]])
 def psi(t):return n*np.sin(np.pi*(t-left)/width)**2
 def psip(t):return n*np.pi/width*np.sin(2*np.pi*(t-left)/width)
 if coeff is None:
  ad=numerical_max(lambda t:(L*psip(t)-D.T@psi(t))[0],left,right)
  aq=numerical_max(lambda t:-(L*psip(t)-D.T@psi(t))[1],left,right)
 else:ad,aq=coeff
 edq=np.array([V-R*Pl/S+omega*L*beta/S,-R*beta/S-omega*L*Pl/S])
 M=quad(lambda t:psi(t)@edq,left,right,epsabs=1e-14,epsrel=1e-13)[0]
 h=0 if eps==0 else brentq(lambda h:mu*h*h/K+2*c*h*h*h/(3*K)-eps,0,np.sqrt(K*eps/mu),xtol=1e-12)
 d=min(Pl,h);rho=k*d*(2*Pl-d);E=eps/S*max(ad/mulocal,aq/(2*c*beta))
 ram=.005*((-a-p['Aload']+2*c*P0*a)/2-c*(a*a+beta*beta)/3)
 slope=Pl-p['D0']-p['Aload']-c*(Pl*Pl+beta*beta)
 def H(t):return W0+ram+slope*(t-.005)-k*(Pl*Pl+beta*beta-P0*P0)+charge(t)+rho
 rhs=quad(lambda t:np.linalg.norm(psi(t))*np.sqrt(min(Wmax,H(t))/(1500*Cdc)),left,right,points=[s for s in [.011] if left<s<right],epsabs=1e-14,epsrel=1e-13)[0]
 return {'margin_kV_s':M-E-rhs,'Mbar_kV_s':M,'error_kV_s':E,'rhs_kV_s':rhs,'active_error_ratio':ad/mulocal,'reactive_error_ratio':aq/(2*c*beta),'rho_kJ':rho,'adplus':ad,'aqminus':aq}
target=json.loads((ROOT/'theory/vector_weak_results.json').read_text());rows=[];diff={}
for case in target['results']:
 eps=case['epsilon_kJ'];beta=case['verified_excluded_beta_kvar'];left,right=case['window_s'];theta=case['angle_rad'];got=calc(eps,beta,left,right,theta)
 co=(got['adplus'],got['aqminus']);threshold=brentq(lambda b:calc(eps,b,left,right,theta,co)['margin_kV_s'],700,1100,xtol=1e-10)
 for key,v in case['quad_exclusion'].items():diff[key]=max(diff.get(key,0),abs(got[key]-v))
 rows.append({'epsilon_kJ':eps,'beta_kvar':beta,'window_s':[left,right],'angle_rad':theta,'independent_threshold_kvar':threshold,'independent_terms':got,'tail_gamma_kW':gamma(eps,beta)})
betamax=S*p['imax'];gmax=gamma(.1,betamax)
# Independently audited constructive lower witness; its zero-slack tail remains below the expanded cap.
w,data=witness_audit(ROOT/'results/boundary_a100_q808_n320.npz');w['independent_SI_abc_replay']=replay_abc(data)
row100=next(x for x in rows if x['epsilon_kJ']==.1);ub=row100['beta_kvar']
res={'selected_certificate_audits':rows,'max_difference_from_target':diff,'all_higher_beta_exclusion':{'free_allocation_current_ceiling_beta_kvar':betamax,'gamma_at_100J_and_current_ceiling_kW':gmax,'gamma_below_alpha_through_current_range':bool(gmax<a),'argument':'For fixed chosen test at epsilon=0.1, all beta from the strict upper witness to S*Imax have gamma<alpha; mu,K,rho stay fixed. Mbar increases with beta, joint error=max(const,const/beta) does not increase, H falls with beta squared. Therefore margin is increasing until a DC ceiling itself excludes. Beyond S*Imax the Q floor alone violates current.'},'constructive_808_witness':w,'capacity_bracket':{'epsilon_kJ':.1,'lower_exhibited_beta_kvar':808.,'strict_upper_excluded_beta_kvar':ub,'width_relative_to_lower_percent':100*(ub-808)/808,'lower_actual_gamma_kW':w['gamma_kW'],'lower_allowed_100J_cap_gamma_kW':gamma(.1,808),'scope':'Supremal beta over all admissible time-varying P/Q in the explicitly tail-expanded-cap, nonnegative-import, positive-reactive-floor contract family. Numerical, not directed interval, certificate.'}}
(ROOT/'audit/VECTOR_WEAK_AUDIT.json').write_text(json.dumps(res,indent=2));print(json.dumps({'max_difference_from_target':diff,'all_higher_beta_exclusion':res['all_higher_beta_exclusion'],'capacity_bracket':res['capacity_bracket'],'808_admitted':w['independent_admitted_numeric'],'808_replay':w['independent_SI_abc_replay']},indent=2))
