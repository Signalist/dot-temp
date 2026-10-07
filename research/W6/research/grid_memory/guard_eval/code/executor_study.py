"""Sampled ideal actual-power executors; not a hardware implementation."""
from guard_study import ROOT,Policy,Grid,M,C,F
import json,hashlib,numpy as np

def work_integral(p,v,t,b):
 if abs(v)<1e-14:return p**b*t
 end=max(0.,p+v*t)
 return (end**(1+b)-p**(1+b))/(v*(1+b))
def time_for_work(p,v,w,b):
 if w<=0:return 0.
 if abs(v)<1e-14:return w/p**b
 end=max(0.,p**(1+b)+(1+b)*v*w)**(1/(1+b))
 return (end-p)/v
class Wave:
 def __init__(self,beta,R,t,p,x):
  self.beta=beta;self.R=R;self.t=np.array(t);self.p=np.array(p);self.x=np.array(x)
  self.dt=np.diff(self.t);self.v=np.diff(self.p)/self.dt
  self.energy=np.r_[0.,np.cumsum((self.p[:-1]+self.p[1:])/2*self.dt)]
 def eos_time(self,w):
  if w<=0:return 0.
  i=min(int(np.searchsorted(self.x,w,side='left')-1),len(self.v)-1);i=max(0,i)
  return float(self.t[i]+time_for_work(self.p[i],self.v[i],w-self.x[i],self.beta))
 def observed(self,w,delay,grid,cache):
  true=self.eos_time(w);detect=min(true+delay,self.t[-1]);i=min(int(np.searchsorted(self.t,detect,side='right')-1),len(self.v)-1);dt=detect-self.t[i]
  p=max(0.,self.p[i]+self.v[i]*dt);energy=self.energy[i]+(self.p[i]+p)/2*dt+p*p/(2*self.R);cycle=detect+p/self.R
  state=grid.value(cache['states'][i],self.v[i],dt)
  pk1=grid.extrema(cache['states'][i],self.v[i],dt)[0];pk2=grid.extrema(state,-self.R,p/self.R)[0];end=grid.value(state,-self.R,p/self.R);tail=grid.extrema(end,0.)[0]
  peak=max(cache['prefix'][i],pk1,pk2,tail)
  # Potential service beyond true EOS is explicitly not useful work.
  ghost=min(M,self.x[i]+work_integral(self.p[i],self.v[i],dt,self.beta))
  return [energy+C*cycle,energy,cycle,true,peak,ghost-w,w,p]
 def grid_cache(self,g):
  states=[np.zeros(2)];prefix=[0.]
  for v,dt in zip(self.v,self.dt):
   prefix.append(max(prefix[-1],g.extrema(states[-1],v,dt)[0]));states.append(g.value(states[-1],v,dt))
  return {'states':states,'prefix':prefix}

def event_wave(pol):return Wave(pol.beta,pol.R,pol.t,pol.p,pol.x)

def sampled_wave(pol,cap,dt=.01):
 b=pol.beta;R=pol.R;x=0.;p=0.;t=0.;T=[0.];P=[0.];X=[0.];clamps=0;ticks=0
 while x<M-1e-12:
  if t>1000:raise RuntimeError('sampled controller did not finish by 1000 s')
  i=min(int(np.searchsorted(pol.x,x,side='right')-1),len(pol.slope)-1);pref=float(((1+b)*np.interp(x,pol.x,pol.z))**(1/(1+b)))
  u=float(np.clip(pol.slope[i]+(pref-p)/dt,-R,R));remaining=dt;ticks+=1
  while remaining>1e-13:
   actual=u
   if (p>=cap-1e-12 and actual>0) or (p<=1e-12 and actual<0):actual=0.
   dur=remaining
   if actual>0:dur=min(dur,max(0.,(cap-p)/actual))
   elif actual<0:dur=min(dur,max(0.,-p/actual))
   if dur<1e-13:actual=0.;dur=remaining;clamps+=1
   dx=work_integral(p,actual,dur,b)
   if x+dx>=M:
    dur=time_for_work(p,actual,M-x,b);dx=M-x;remaining=0.
   else:remaining-=dur
   p=max(0.,min(cap,p+actual*dur));x=min(M,x+dx);t+=dur
   if dur>1e-14:T.append(t);P.append(p);X.append(x)
   if x>=M-1e-12:break
 if p>1e-12:T.append(t+p/R);P.append(0.);X.append(M)
 wave=Wave(b,R,T,P,X)
 return wave,{'ticks':ticks,'clamp_events':clamps,'completed_work':x,'time_to_max_work':t,'max_power':max(P),'max_abs_slew':float(np.max(abs(wave.v))),'segments':len(wave.v)}

def run():
 proto=ROOT/'EXECUTOR_PROTOCOL.json';digest=hashlib.sha256(proto.read_bytes()).hexdigest();expected=(ROOT/'EXECUTOR_PROTOCOL.sha256').read_text().split()[0];assert digest==expected
 protocol=json.loads(proto.read_text());allrows=[]
 for cid in protocol['case_ids']:
  source=ROOT/f'raw/{cid}.json'
  if not source.exists():continue
  row=json.loads(source.read_text())
  if any(label not in row['policies'] or 'control_path' not in row['policies'][label] for label in protocol['controllers']):continue
  cfg=row['config'];g=Grid(cfg['mode_Hz'],cfg['zeta']);ws=np.linspace(0,M,1025)
  for label in protocol['controllers']:
   record=row['policies'][label];data=np.loadtxt(ROOT/record['control_path'],delimiter=',',skiprows=1)
   pol=Policy(cfg['beta'],cfg['R'],data[:,0],data[:,1]);cap=record['pcap'];wave0=event_wave(pol)
   wave1,diagnostic=sampled_wave(pol,cap);curves={};refs={}
   for name,wave in [('event',wave0),('sampled',wave1)]:
    cache=wave.grid_cache(g);np.savetxt(ROOT/f'curves/{cid}_{label}_{name}_executor.csv',np.column_stack([wave.t,wave.p,wave.x,wave.energy]),delimiter=',',header='time,power,ghost_work,energy',comments='')
    for delay in protocol['EOS_delays_s']:
     vals=np.array([wave.observed(w,delay,g,cache) for w in ws]);mean=np.trapezoid(vals,ws,axis=0)/M;coarse=np.trapezoid(vals[::2],ws[::2],axis=0)/M
     key=f'{name}_delay{delay}';curves[key]=vals
     result={'id':cid,'controller':label,'execution':name,'EOS_delay_s':delay,'protocol_sha256':digest,'expected_objective':float(mean[0]),'expected_dynamic_energy':float(mean[1]),'expected_powercycle_time':float(mean[2]),'expected_true_service_time':float(mean[3]),'worst_dense_EOS_peak_Hz':float(vals[:,4].max()),'worst_peak_W':float(ws[np.argmax(vals[:,4])]),'expected_wasted_potential_service':float(mean[5]),'mean_useful_work':float(mean[6]),'work_accounting_max_error':float(np.max(abs(vals[:,6]-ws))),'objective_513_1025_relative_difference':float(abs(mean[0]-coarse[0])/mean[0]),'pcap':cap,'analytic_nominal_guard_bound_Hz':cap*g.G(),'sampled_diagnostics':diagnostic if name=='sampled' else None,'cycle_duration_includes_no_zero_input_grid_tail':True}
     refs[key]=result
   baseline=refs['event_delay0.0']['expected_objective']
   for key,result in refs.items():
    result['objective_excess_vs_event_instant']=result['expected_objective']-baseline;result['objective_excess_percent_vs_event_instant']=100*(result['expected_objective']/baseline-1)
    if result['execution']=='event':
     bound=2*(cap+C)*result['EOS_delay_s'];result['pure_delay_bound']=bound;result['pathwise_delay_excess_max']=float(np.max(curves[key][:,0]-curves['event_delay0.0'][:,0]));result['bound_holds_float']=result['pathwise_delay_excess_max']<=bound+1e-10
    allrows.append(result)
   np.savez_compressed(ROOT/f'curves/{cid}_{label}_executor_EOS.npz',W=ws,**curves)
   (ROOT/'raw/EXECUTOR_RESULTS.json').write_text(json.dumps(allrows,indent=2));print('EXECUTOR',cid,label,diagnostic,flush=True)
 return allrows
if __name__=='__main__':run()
