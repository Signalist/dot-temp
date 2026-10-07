from pathlib import Path
import sys,json
import numpy as np
from scipy.integrate import quad,simpson
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'prior_core';sys.path.insert(0,str(OLD/'src'));sys.path.insert(0,str(OLD/'theory'))
from model import Params,profiles,base_knots
from admission import solve_inner
from vector_weak_certificate import values as oldvalues
from explore_coupled import values
p=Params();c=p.losscoef;k=p.L/(3000*p.v*p.v);Gp=1500*p.v

def ledger():
 def pair(t):
  z=profiles(t,100,808,p);d=float(z['d']);pl=2*d/(1+np.sqrt(1-4*c*d));return float(z['p']),pl,d,float(z['q'])
 knots=base_knots(p);rows=[]
 for name,a,b in [('critical_prefix',0,.0239),('early_service',0,.11),('loss_compensation_tail',.125,.175),('whole_task',0,.2),('continuing_nominal',.2,.3)]:
  points=[x for x in knots if a<x<b]
  integrate=lambda f:quad(f,a,b,points=points,epsabs=1e-10,epsrel=1e-12,limit=500)[0]
  diff=lambda t:pair(t)[0]-pair(t)[1]
  E=integrate(diff);positive=integrate(lambda t:max(diff(t),0));absolute=integrate(lambda t:abs(diff(t)))
  rows.append(dict(window=name,start_s=a,end_s=b,signed_AC_increment_J=1000*E,positive_AC_increment_J=1000*positive,absolute_AC_increment_J=1000*absolute,service_grid_J=1000*integrate(lambda t:pair(t)[0]),no_service_grid_J=1000*integrate(lambda t:pair(t)[1]),common_workload_J=1000*integrate(lambda t:pair(t)[2]),extra_copper_J=1000*integrate(lambda t:c*(pair(t)[0]**2+pair(t)[3]**2-pair(t)[1]**2))))
 # Every window keeps separate DC, buffer, and inductor endpoint increments.
 tr=np.loadtxt(ROOT/'results'/'zoh_certified_trace.csv',delimiter=',',skiprows=1)
 tr=np.vstack([[0,0,0,p.W0],tr])
 def states(t):
  ps,pl,dd,qs=pair(t)
  if t>=.2:ws=p.W0;bs=p.B0
  else:
   jj=int(np.argmin(abs(tr[:,0]-t)));assert abs(tr[jj,0]-t)<1e-10
   ws=tr[jj,3];bs=p.B0-tr[jj,2]
  zl=k*pl*pl;zs=k*(ps*ps+qs*qs);wl=p.W0-zl+k*p.p0*p.p0
  return {'W_S_kJ':ws,'W_L_kJ':wl,'B_S_kJ':bs,'B_L_kJ':p.B0,'Z_S_kJ':zs,'Z_L_kJ':zl,'b_S_kW':0. if t>=.2 else tr[jj,1]}
 for row in rows:
  ss=states(row['start_s']);ee=states(row['end_s']);row['states_at_start']=ss;row['states_at_end']=ee
  dc={name:1000*((ee[name+'_S_kJ']-ee[name+'_L_kJ'])-(ss[name+'_S_kJ']-ss[name+'_L_kJ'])) for name in ['W','B','Z']}
  row['paired_state_change_J']=dc;row['energy_closure_residual_J']=row['signed_AC_increment_J']-row['extra_copper_J']-sum(dc.values())
 # frozen .1kJ cap slack chooses a larger allowed late tail, not necessarily actual import.
 z=profiles(0,100,808,p);gamma=z['gamma'];r1=.045;r2=.040+2*.005/3;rhs=c*(10000*(2*(.030+.010/3))+808**2*(.030+.010/3))+.1
 gamma_cap=2*rhs/(r1*(1-2*c*p.p0)+np.sqrt((r1*(1-2*c*p.p0))**2-4*c*r2*rhs))
 out={'comparison':'S uses original fixed recoverable P/Q with certified ZOH buffer; L is exact net-load following P_L=(1-sqrt(1-4cd))/(2c), Q_L=b_L=u_L=0; d_L=d_S pointwise','windows':rows,'actual_gamma_kW':gamma,'allowed_gamma_at_epsilon100J_kW':gamma_cap,'epsilon_meaning':'Reference-cap net delivery minus same compute workload over0-.2s is100J; it is neither total recovery import nor absolute service energy','endpoint_states':'Both W(T)=W0, B(T)=B0, i(T)=i0; S b(T)=0 by exact correction; L b identically0; thereafter both exact averaged nominal orbit','baseline_optimality_claim':False}
 (ROOT/'results'/'same_workload_energy_ledger.json').write_text(json.dumps(out,indent=2));return out

if __name__=='__main__':
 out=ledger();print(json.dumps(out,indent=2),flush=True)
 rows=[]
 for q in [808,812.5,834.414530875619]:
  for mode in ['coupled','no_prefix']:
   r=values(.1,q,.0113,.0239,float(np.arctan(-.102)),N=20001,mode=mode);r['ablation']=mode;rows.append(r)
  rr=oldvalues(.1,q,.009,.027,-.1,True);rows.append({'beta':q,'ablation':'old_uniform_release_joint_linear_budget','old_values':rr})
 (ROOT/'results'/'ablation_results.json').write_text(json.dumps(rows,indent=2))
 z=solve_inner(100,808,n=320,save=ROOT/'results'/'mature_socp_q808.npz');(ROOT/'results'/'mature_socp_comparator.json').write_text(json.dumps(z,indent=2));print('SOCP',z)
