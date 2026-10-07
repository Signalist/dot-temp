import pathlib,json,numpy as np
from scipy.integrate import solve_ivp
R=pathlib.Path(__file__).resolve().parent
eta=.95;alpha=12/(1+eta*eta);tau=.01;r=.2
# Independent scalar implementation, no import from witness producer.
def v(t,j):
 k=min(int(t),5);s=t-k
 if s<r:f=np.sin(np.pi*s/(2*r))**2/(1-r);df=np.pi*np.sin(np.pi*s/r)/(2*r*(1-r))
 elif s<=1-r:f=1/(1-r);df=0
 else:f=np.sin(np.pi*(1-s)/(2*r))**2/(1-r);df=-np.pi*np.sin(np.pi*(1-s)/r)/(2*r*(1-r))
 c=(12 if k==j else 0)-(alpha if k in[1,2] else 0)
 return 6+(12*f if k==j else 0),6+(alpha*f if k in[1,2] else 0),c*f,c*(f+tau*df)
rows=[];traces=[]
for maxstep in [.01,.005]:
 for j in[1,2]:
  def rhs(t,z):
   d,p,bd,u=v(t,j);b,e=z
   return [(u-b)/tau,(-b/eta if b>=0 else -eta*b)]
  tt=np.linspace(0,6,12001);sol=solve_ivp(rhs,[0,6],[0,9],method='DOP853',rtol=1e-10,atol=1e-11,max_step=maxstep,t_eval=tt)
  assert sol.success
  vals=np.array([v(t,j) for t in tt]);actualP=vals[:,0]-sol.y[0];pccerr=max(abs(actualP-vals[:,1]));berr=max(abs(sol.y[0]-vals[:,2]));end=float(sol.y[1,-1]-9)
  rows.append({'max_step':maxstep,'high_slot':j+1,'max_PCC_error':float(pccerr),'max_buffer_error':float(berr),'terminal_SOC_error':end,'SOC_min':float(sol.y[1].min()),'SOC_max':float(sol.y[1].max())});traces.append(actualP)
res={'scope':'independent differential-equation integration of lossy smooth DAG pair, no analytic energy trajectory substituted','rows':rows,'max_world_difference_fine':float(max(abs(traces[-1]-traces[-2]))),'all_pass':all(x['max_PCC_error']<1e-7 and abs(x['terminal_SOC_error'])<1e-7 and x['SOC_min']>0 and x['SOC_max']<18 for x in rows)}
(R/'SMOOTH_ODE_CHECK.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2));assert res['all_pass']
