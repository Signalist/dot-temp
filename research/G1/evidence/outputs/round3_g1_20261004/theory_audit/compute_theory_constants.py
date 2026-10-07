"""Independent real-arithmetic formulas for G1 input-free robust CBF.
No imports from frozen producer/reviewer code. Float evaluations are not interval arithmetic.
"""
from pathlib import Path
import json, numpy as np
from scipy.optimize import brentq
from scipy.linalg import expm
OUT=Path(__file__).resolve().parent
alpha=5.;h=.6;M=.003;h0=h-2*M/alpha
F=lambda t:1-(1+t)*np.exp(-t)
g=lambda t:t*np.exp(-t)

def constants(hh):
 K=(alpha-1)**2/alpha
 ta=brentq(lambda t:2*(1+(alpha-1)*t)*np.exp(-t)-alpha*hh,0,(alpha-2)/(alpha-1))
 ya=2*g(ta);d=hh-ya
 peak_t=np.log(alpha*K*d/hh)/alpha
 duration=brentq(lambda t:K*d*(-np.expm1(-alpha*t))-hh*t,1e-8,4)
 U=K*d*(-np.expm1(-alpha*peak_t))-hh*peak_t
 D=K*d*(duration+np.expm1(-alpha*duration)/alpha)-hh*duration**2/2
 tb=brentq(lambda t:F(t)-(2-2*hh),0,5)
 tau=2*np.log(alpha-1)/alpha
 yinv=brentq(lambda t:g(t)-hh/2,0,1)
 checks={
  'initial_inactive':alpha*hh-2,
  'pure_low_inactive_margin':-(1-alpha*hh+(alpha-1)*np.exp(-(alpha-2)/(alpha-1))),
  'entry_monotonicity_margin':alpha-2-yinv/(1-yinv),
  'down_exit_margin':-(1-2*hh+2/alpha-(hh-1/alpha)*tau),
  'episode_before_next_up_margin':5-tb-tau,
  'later_reactivation_exclusion_margin':F(5)-D/np.e-(2-2*hh),
  'unit_power_margin':1-U,
 }
 return dict(h=hh,alpha=alpha,entry_time=ta,entry_y=ya,peak_time=peak_t,active_duration=duration,peak_power=U,discharge=D,tb=tb,tau=tau,support_upper=tb+tau,positive_checks=checks)
lo=constants(h0);hi=constants(h)
A=np.array([[0.,1.],[-1.,-2.]])
B=np.array([0.,-1.]);cuts=[10.,11.,19.,20.]
C=np.vstack([np.diff(cuts),np.array([expm(A*(20-b))@np.linalg.solve(A,(expm(A*(b-a))-np.eye(2)))@B for a,b in zip(cuts[:-1],cuts[1:])]).T])
CI=np.linalg.inv(C)
ABC=np.column_stack([-CI[:,0],np.exp(-20)*(20*CI[:,1]-19*CI[:,2]),np.exp(-20)*(-CI[:,1]+CI[:,2])])
S=5.
def ranges(row):
 c,a,b=row;pts=[0.,S]
 if b and 0<-a/b-1<S:pts.append(-a/b-1)
 vals=[c+np.exp(t)*(a+b*t) for t in pts]
 return [min(vals),max(vals)]
cr=np.array([ranges(row) for row in ABC]);zr=np.array([ranges(row) for row in np.vstack([[1.,0.,0.],np.array([1.,0.,0.])+np.cumsum(np.diff(cuts)[:,None]*ABC,axis=0)])])
D=lo['discharge'];rec_power=D*np.max(abs(cr),axis=1);cap=D*(1-min(zr[:,0]));prefix_power=lo['peak_power']+2*M*(alpha-2)*lo['active_duration']
state={'sampling':.001,'delay':.0005,'epsilon_x':1e-4,'epsilon_y':1e-4};a=state['sampling']+state['delay'];state['barrier_error_bound']=(1+(alpha-1)*a)*state['epsilon_x']+(alpha-2)*state['epsilon_y']+.5*(alpha-2)*a
freq={'sampling':.0002,'delay':.0002,'epsilon_y':1e-5,'integration_horizon':10.};freq['epsilon_x']=10*(freq['epsilon_y']+freq['sampling']);a=freq['sampling']+freq['delay'];freq['barrier_error_bound']=(1+(alpha-1)*a)*freq['epsilon_x']+(alpha-2)*freq['epsilon_y']+.5*(alpha-2)*a
result={'model':'xdot=y; ydot=p-2y-x-u; edot=-u; p alternates1/2 every5 with all initial phases; exact model and known applied u','alpha':alpha,'h':h,'barrier_error_budget':M,'tight_nominal':lo,'loose_nominal':hi,'robust_prefix_power_upper':prefix_power,'robust_e0':D,'robust_capacity':cap,'prefix_support_end':S,'prefix_cutoff_margin':F(S)-D/np.e-(2-2*h+2*M),'recovery_matrix':C.tolist(),'unit_recovery_coefficient_ranges':cr.tolist(),'unit_cumulative_recovery_ranges':zr.tolist(),'recovery_power_bounds':rec_power.tolist(),'post10_frequency_upper':1/np.e+10*np.exp(-10)+D*(9-S)*np.exp(-(10-S))+sum(rec_power)/np.e,'state_sensor_contract':state,'frequency_only_contract':freq,'full_family_opacity_noise_threshold':1/(2*np.e),'frozen_no_feedback_lower':.442710930662431,'resource_separation_float_gap':.442710930662431-cap,'qualification':'Proof formulas evaluated in ordinary floating point. No outward-rounded numerical certification, ZOH actuation, actuator/model uncertainty or physical-unit calibration claim.'}
assert all(v>0 for c in [lo,hi] for v in c['positive_checks'].values())
assert prefix_power<.5 and max(rec_power)<.5 and result['post10_frequency_upper']<h
assert result['prefix_cutoff_margin']>0 and state['barrier_error_bound']<M and freq['barrier_error_bound']<M
assert cap<result['frozen_no_feedback_lower']
(OUT/'theory_constants.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
