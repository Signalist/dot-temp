"""Exploratory transfer to recovered 51-state linear Kundur model.
No nonlinear run, measurement, population inference, or hardware validation.
"""
from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
import numpy as np
from scipy.linalg import eig
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'guard_eval/code'))
from guard_study import safe_solver,target,Policy
SOURCE=ROOT/'inputs/kundur_reduced51.npz'

class ModalGrid:
 def __init__(self,source,input_col,gain):
  d=np.load(source);self.A=d['A'];self.B=d['B'][:,input_col]*gain;self.C=d['C_frequency_Hz']
  self.lam,self.V=eig(self.A);self.beta=np.linalg.solve(self.V,self.B);self.res=(self.C@self.V)*self.beta
  self.condition=float(np.linalg.cond(self.V));self.maxreal=float(self.lam.real.max());self.gain=gain
  self.reconstruction=float(np.max(abs(self.V@np.diag(self.lam)@np.linalg.inv(self.V)-self.A)))
 def gains(self,T=140.,dt=.002):
  t=np.linspace(0,T,int(round(T/dt))+1);dt=t[1]-t[0]
  h=np.real(np.exp(np.outer(t,self.lam))@self.res.T)
  # Exact positive/negative integrals of the piecewise-linear interpolant.
  left=h[:-1];right=h[1:];pos=np.where((left>=0)&(right>=0),(left+right)/2*dt,0.)
  neg=np.where((left<=0)&(right<=0),-(left+right)/2*dt,0.)
  cross=left*right<0
  den=abs(left)+abs(right)
  pos+=np.where(cross,np.maximum(left,right)**2/np.maximum(den,1e-300)*dt/2,0.)
  neg+=np.where(cross,np.minimum(left,right)**2/np.maximum(den,1e-300)*dt/2,0.)
  pp=pos.sum(axis=0);nn=neg.sum(axis=0)
  tail=(abs(self.res)*np.exp(self.lam.real*T)/(-self.lam.real)).sum(axis=1)
  # Integral of interval-sup |h''| times dt²/8, geometric sum exactly.
  geom=(-np.expm1(self.lam.real*T))/(-np.expm1(self.lam.real*dt))
  interp=(abs(self.res*self.lam**2)*geom).sum(axis=1)*dt**3/8
  G=np.maximum(pp,nn);return {'positive_interpolant_area':pp.tolist(),'negative_interpolant_area':nn.tolist(),
   'interpolation_area_remainder':interp.tolist(),'tail_area_remainder':tail.tolist(),'G_lower':np.maximum(0,G-interp).tolist(),
   'G_upper':(G+interp+tail).tolist(),'horizon':T,'dt':dt,'mode_condition':self.condition,
   'max_pole_real':self.maxreal,'matrix_reconstruction_error':self.reconstruction,'numeric_status':'analytic truncation/interpolation budgets; ordinary float eigensolve and sums, not interval certificate'},t,h
 def advance(self,q,p,u,t):
  e=np.exp(self.lam*t);return e*q+p*np.expm1(self.lam*t)/self.lam+u*(np.expm1(self.lam*t)-self.lam*t)/self.lam**2
 def segment_peak(self,q,p,u,T,dt=.005):
  n=max(1,int(np.ceil(T/dt)));t=np.linspace(0,T,n+1);step=T/n
  e=np.exp(np.outer(t,self.lam));qs=e*q+p*np.expm1(np.outer(t,self.lam))/self.lam+u*(np.expm1(np.outer(t,self.lam))-np.outer(t,self.lam))/self.lam**2
  ys=np.real(qs@self.res.T);low=abs(ys).max(axis=0)
  # Every interval uses a uniform derivative upper bound, nearest sample <=dt/2.
  pmax=max(p,p+u*T,0.);qmax=abs(qs).max(axis=0)+pmax*step
  L=(abs(self.res)*(abs(self.lam)*qmax+pmax)).sum(axis=1)
  return qs[-1],low,low+step*L/2
 def replay(self,pol,w):
  q=np.zeros(len(self.lam),complex);low=np.zeros(4);upper=np.zeros(4);elapsed=0
  for i,u in enumerate(pol.slope):
   if w<=pol.x[i]:break
   dt=pol.duration(i,min(w,pol.x[i+1]));q,lo,up=self.segment_peak(q,pol.p[i],u,dt);low=np.maximum(low,lo);upper=np.maximum(upper,up);elapsed+=dt
   if w<=pol.x[i+1]:break
  power=((pol.K)*np.interp(w,pol.x,pol.z))**(1/pol.K)
  if power>0:
   q,lo,up=self.segment_peak(q,power,-pol.R,power/pol.R);low=np.maximum(low,lo);upper=np.maximum(upper,up);elapsed+=power/pol.R
  # Once this exponential envelope falls below existing lower peak, later time is settled for max purposes.
  Tend=60.;qtail=q.copy();q,lo,up=self.segment_peak(q,0.,0.,Tend,dt=.01);low=np.maximum(low,lo);upper=np.maximum(upper,up)
  omitted=(abs(self.res*qtail)*np.exp(self.lam.real*Tend)).sum(axis=1);upper=np.maximum(upper,omitted)
  return {'W':w,'powercycle_s':elapsed,'frequency_peak_lower_Hz':low.tolist(),'frequency_peak_upper_Hz':upper.tolist(),
   'tail_after_60s_bound_Hz':omitted.tolist(),'all_future_bound_status':'inter-sample derivative plus exponential tail, ordinary float',
   'sample_not_independent_run':True}

def main():
 out=ROOT/'network_transfer';out.mkdir(exist_ok=True)
 protocol={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'EXPLORATORY_NETWORK_TRANSFER_NOT_CONFIRMATORY',
  'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  'beta':.5,'R':1.,'M':2.,'c':1.,'grid_budget_Hz':.05,'input_buses':[7,8],'gain_MW_per_model_power':[20.,200.],
  'EOS_replays':[.2,.6,1.,1.6,2.],'optimization_N':128,'no_parameter_calibration':True,
  'limitations':['existing model inherited, not freshly validated','linear replay only','frequency allocation is study budget','no concurrency or physical GPU mapping']}
 (out/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2));rows=[]
 for bus,col in [(7,0),(8,2)]:
  for gain in [20.,200.]:
   grid=ModalGrid(SOURCE,col,gain);bounds,t,h=grid.gains();cap=.05/max(bounds['G_upper']);case={'bus':bus,'gain':gain,'gain_bounds':bounds,'guard_cap':cap,'policies':{}}
   np.savez_compressed(out/f'kernel_bus{bus}_gain{gain}.npz',time=t,frequency_impulse_Hz_per_model_power=h)
   for label,pcap in [('guarded',min(1.,cap)),('unguarded_diagnostic',1.)]:
    row=safe_solver(.5,1.,pcap,128);pol=Policy(.5,1.,np.linspace(0,2,129),row['z']);replays=[grid.replay(pol,w) for w in protocol['EOS_replays']]
    row['replays']=replays;row['analytic_all_work_all_time_bound_Hz']=(pcap*np.array(bounds['G_upper'])).tolist();case['policies'][label]=row
   tar=target(.5,1.,min(1.,cap));case['same_cap_global_target']=tar
   case['guarded_gain_vs_target']=1-case['policies']['guarded']['parts']['objective']/tar['parts']['objective'];rows.append(case)
   (out/'RESULTS.json').write_text(json.dumps(rows,indent=2));print(bus,gain,'cap',cap,'gain',case['guarded_gain_vs_target'],flush=True)
if __name__=='__main__':main()
