"""Floating W6 isolated-cycle model study; original files imported read-only."""
from pathlib import Path
import sys,json,math,hashlib,itertools,time,traceback
import numpy as np
from scipy.optimize import brentq,minimize_scalar
from scipy.linalg import expm
from scipy.integrate import quad
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/'code/vendor_original'
if not ORIGINAL.exists(): ORIGINAL=ROOT.parents[1]/'full_cycle/code'
sys.path.insert(0,str(ORIGINAL))
from cycle_model import Case,Mesh,solve,power_int
from global_bellman import uniform_edge
M=2.;C=1.;F=.05;MH=2*4*1000/60
class CappedCase(Case):
 def __init__(self,beta,R,c,pcap):
  super().__init__(beta=beta,R=R,c=c);object.__setattr__(self,'pcap',pcap)
 def cap(self,x):return np.minimum(super().cap(x),self.A(self.pcap))
class Grid:
 def __init__(self,mode,zeta,gain=20.):
  self.mode=mode;self.zeta=zeta;self.gain=gain;self.omega=2*np.pi*mode
  self.a=zeta*self.omega;self.w=self.omega*np.sqrt(1-zeta*zeta);self.b=gain/MH
 def G(self):
  k=self.zeta/np.sqrt(1-self.zeta**2)
  return self.b/self.omega*np.exp(-k*np.arccos(self.zeta))/(-np.expm1(-np.pi*k))
 def slew_norm(self):return self.b/self.omega**2/np.tanh(np.pi*self.zeta/(2*np.sqrt(1-self.zeta**2)))
 def value(self,state,slope,t):
  f,q=state;ss=-self.b*slope/self.omega**2;c=f-ss;d=(q+self.a*c)/self.w
  co=np.cos(self.w*t);si=np.sin(self.w*t);e=np.exp(-self.a*t)
  return np.array([ss+e*(c*co+d*si),e*((-self.a*c+self.w*d)*co+(-self.a*d-self.w*c)*si)])
 def extrema(self,state,slope,dt=np.inf):
  f,q=state;ss=-self.b*slope/self.omega**2;c=f-ss;d=(q+self.a*c)/self.w
  U=-self.a*c+self.w*d;V=-self.a*d-self.w*c;cand=[0.]
  if np.isfinite(dt):cand.append(float(dt))
  if abs(U)+abs(V)>1e-300:
   first=(math.atan2(-U,V)%np.pi)/self.w
   if first<1e-12:first+=np.pi/self.w
   if np.isfinite(dt):
    if first<=dt:cand.extend(first+np.arange(int((dt-first)*self.w/np.pi)+1)*np.pi/self.w)
   else:
    if slope!=0:raise ValueError('Infinite tail requires zero forcing')
    cand.append(first)
  vals=np.abs([self.value(state,slope,t)[0] for t in cand]);i=int(np.argmax(vals))
  return float(vals[i]),float(cand[i])
 def asdict(self):return {'mode_Hz':self.mode,'zeta':self.zeta,'gain_MW_per_p':self.gain,'G_Hz_per_p':self.G(),'slew_kernel_L1':self.slew_norm()}
class Policy:
 def __init__(self,beta,R,x,z):
  self.beta=beta;self.R=R;self.x=np.asarray(x);self.z=np.asarray(z);self.K=1+beta
  self.p=(self.K*self.z)**(1/self.K);self.slope=np.diff(self.z)/np.diff(self.x)
  self.dt=np.array([self.duration(i,self.x[i+1]) for i in range(len(self.x)-1)]);self.t=np.r_[0,np.cumsum(self.dt)]
 def duration(self,i,w):
  dx=w-self.x[i]
  if dx<=0:return 0.
  zz=max(0.,float(self.z[i]+self.slope[i]*dx))
  return self.K**(-self.beta/self.K)*power_int(float(self.z[i]),zz,-self.beta/self.K,dx)
 def sample(self,n=2001):
  tt=np.linspace(0,self.t[-1],n);ii=np.minimum(np.searchsorted(self.t,tt,side='right')-1,len(self.slope)-1)
  return tt,self.p[ii]+self.slope[ii]*(tt-self.t[ii])
class FrequencyEvaluator:
 def __init__(self,policy,grid):
  self.p=policy;self.g=grid;states=[np.array([0.,0.])];prefix=[0.];peaktimes=[0.]
  for i,(v,dt) in enumerate(zip(policy.slope,policy.dt)):
   pk,tm=grid.extrema(states[-1],v,dt)
   if pk>prefix[-1]:prefix.append(pk);peaktimes.append(policy.t[i]+tm)
   else:prefix.append(prefix[-1]);peaktimes.append(peaktimes[-1])
   states.append(grid.value(states[-1],v,dt))
  self.states=np.array(states);self.prefix=np.array(prefix);self.peaktimes=np.array(peaktimes)
 def evaluate(self,w,details=False):
  p=self.p;g=self.g
  if w<=0:return {'peak_Hz':0.,'peak_time_s':0.,'phase':'zero_work','W':0.} if details else 0.
  i=min(int(np.searchsorted(p.x,w,side='right')-1),len(p.slope)-1);dt=p.duration(i,w)
  state=g.value(self.states[i],p.slope[i],dt);z=max(0.,p.z[i]+p.slope[i]*(w-p.x[i]));power=(p.K*z)**(1/p.K)
  task=p.t[i]+dt;recovery=power/p.R;pk0=self.prefix[i];tm0=self.peaktimes[i]
  pk1,tm1=g.extrema(self.states[i],p.slope[i],dt);pk2,tm2=g.extrema(state,-p.R,recovery)
  end=g.value(state,-p.R,recovery);pk3,tm3=g.extrema(end,0.,np.inf)
  vals=[pk0,pk1,pk2,pk3];k=int(np.argmax(vals))
  if not details:return float(vals[k])
  return {'W':float(w),'peak_Hz':float(vals[k]),'peak_time_s':float([tm0,p.t[i]+tm1,task+tm2,task+recovery+tm3][k]),'phase':['productive_prefix','productive_partial','recovery','zero_input_tail'][k],'service_time_s':float(task),'recovery_time_s':float(recovery),'powercycle_time_s':float(task+recovery),'grid_f_at_power_return_Hz':float(end[0]),'grid_fdot_at_power_return_Hz_per_s':float(end[1]),'eos_power':float(power)}
 def worst(self,n=2049):
  ws=np.linspace(0,M,n);ys=np.array([self.evaluate(w) for w in ws]);cands=[0,n-1]+[i for i in range(1,n-1) if ys[i]>=ys[i-1] and ys[i]>=ys[i+1] and (ys[i]>ys[i-1] or ys[i]>ys[i+1])]
  refined=[(ys[i],ws[i]) for i in cands];local=[]
  for i in cands:
   if 0<i<n-1:
    res=minimize_scalar(lambda w:-self.evaluate(w),bounds=(ws[i-1],ws[i+1]),method='bounded',options={'xatol':1e-11})
    local.append({'W':float(res.x),'peak_Hz':float(-res.fun),'success':bool(res.success)});refined.append((-res.fun,res.x))
  _,w=max(refined);out=self.evaluate(w,True);out.update({'dense_points':n,'dense_peak_Hz':float(ys.max()),'refined_candidate_count':len(local),'local_refinements':local,'grid':self.g.asdict(),'empirical_maximum_not_universal_certificate':True})
  return out,ws,ys

def safe_solver(beta,R,pcap,N,initial=None):
 c=CappedCase(beta,R*M,C,pcap);row=solve(c,N,initial=initial);rawz=np.array(row['z'])
 scale=min(1.,c.R/N/max(np.max(np.abs(np.diff(rawz))),1e-300),float(c.A(pcap))/max(rawz.max(),1e-300))*(1-1e-12)
 z=rawz*scale;z[0]=z[-1]=0;row['raw_z']=row.pop('z');row['z']=z.tolist();row['inward_scale']=float(scale)
 row['parts']={k:v*M for k,v in Mesh(c,N,96).evaluate(z,parts=True).items()}
 row['physical_max_slew']=float(np.max(np.abs(np.diff(z)))*N/M);row['actual_peak_power']=float(c.P(z.max()));row['physical_pcap']=float(pcap);row['mesh_objective']*=M
 if row['finite_mesh_linearization_gap'] is not None:row['finite_mesh_linearization_gap']*=M
 return row

def target(beta,R,pcap):
 c=Case(beta,R*M,C);b=beta;K=1+b
 pc=brentq(lambda p:(1-b)*p+2/c.R*p**(1+b)*(p+C)-b*C,0,c.critical)
 p=min(pc,float(c.P(c.R/2)),pcap);q=float(c.A(p));a=q/c.R;m=1-2*a
 earlyE=(K*c.R)**(2/K)*a**(1+2/K)/(c.R*(1+2/K));earlyT=2*(K*c.R)**(1/K)*a**(1+1/K)/(c.R*(1+1/K))
 energy=earlyE+(1-a)*p*p/c.R+.5*p**(1-b)*m;cycle=earlyT+(1-a)*2*p/c.R+.5*p**(-b)*m;tail=earlyT+m*p/c.R
 parts={k:float(v*M) for k,v in {'dynamic_energy':energy,'task_time':cycle-tail,'recovery_time':tail,'cycle_time':cycle,'objective':energy+C*cycle}.items()}
 return {'target':p,'unconstrained_stationary_target':pc,'parts':parts,'x':[0.,a*M,(1-a)*M,M],'z':[0.,q,q,0.],'global_target_method':'unique monotone stationary root clipped by reachable peak and guard cap'}

def bellman_cap(beta,R,pcap,N,sub):
 start=time.perf_counter();c=Case(beta,R*M,C);h=1/N;dz=c.R*h/sub;cap=min(float(c.A(c.critical)),float(c.A(pcap)),c.R/2)
 z=np.unique(np.r_[np.arange(int(np.floor(cap/dz))+1)*dz,cap]);V=np.full(len(z),np.inf);V[0]=0.;pol=np.full((N,len(z)),-1,dtype=int);expansions=0
 for i in range(N-1,-1,-1):
  cur=np.full(len(z),np.inf);x=i*h
  for j,a in enumerate(z):
   if a>min(c.R*x,c.R*(1-x),cap)+1e-12:continue
   lo=np.searchsorted(z,a-c.R*h-1e-12);hi=np.searchsorted(z,a+c.R*h+1e-12,side='right')
   for k in range(lo,hi):
    if not np.isfinite(V[k]):continue
    v=uniform_edge(c,x,h,a,z[k])+V[k];expansions+=1
    if v<cur[j]:cur[j]=v;pol[i,j]=k
  V=cur
 inds=[0]
 for i in range(N):
  k=pol[i,inds[-1]]
  if k<0:raise RuntimeError('Bellman failed reconstructing feasible path')
  inds.append(int(k))
 zz=z[inds];parts={k:v*M for k,v in Mesh(c,N,96).evaluate(zz,parts=True).items()}
 return {'N':N,'sub':sub,'z':zz.tolist(),'objective':float(V[0]*M),'independent_quadrature_objective':parts['objective'],'parts':parts,'quadrature_disagreement':float(abs(V[0]*M-parts['objective'])),'states':len(z),'expansions':expansions,'seconds':time.perf_counter()-start,'scope':'global finite-state restricted feasible optimum, same uniform EOS; not continuous lower certificate','pcap':pcap}

def verify_design():
 g=Grid(.4,.1);a=g.a;w=g.w;b=g.b;h=lambda t:-b*np.exp(-a*t)*(np.cos(w*t)-a/w*np.sin(w*t));horizon=100/a
 cuts=np.r_[0.,np.arange(np.arccos(g.zeta)/w,horizon,np.pi/w),horizon];plus=minus=0.
 for l,r in zip(cuts[:-1],cuts[1:]):
  v=quad(h,l,r,epsabs=1e-13)[0];plus+=max(v,0);minus+=max(-v,0)
 tail=b*np.sqrt(1+(a/w)**2)*np.exp(-a*horizon)/a
 A=np.array([[0,2*np.pi],[-g.omega**2/(2*np.pi),-2*a]]);B=np.array([0.,-b]);aug=np.zeros((4,4));aug[:2,:2]=A;aug[:2,2]=B;aug[2,3]=1
 v=.7;dt=1.234;initial=np.array([.01,-.007,.11,v]);end=expm(aug*dt)@initial
 f0=initial[1];q0=(A@initial[:2]+B*initial[2])[1];closed=g.value((f0,q0),v,dt)
 residual=max(abs(closed[0]-end[1]),abs(closed[1]-(A@end[:2]+B*end[2])[1]))
 result={'closed_form_G':g.G(),'floating_positive_integral':plus,'floating_negative_integral':minus,'quadrature_tail_envelope':tail,'integral_horizon_s':horizon,'closed_vs_matrix_propagation_max_error':float(residual),'not_interval_certified':True}
 (ROOT/'raw/DESIGN_VERIFICATION.json').write_text(json.dumps(result,indent=2));assert abs(plus-g.G())<1e-10 and abs(minus-g.G())<1e-10 and residual<1e-12
 return result

def evaluate_policy(row,label,pol,g,cap):
 record=row['policies'][label];id=row['id'];worst,ws,ys=FrequencyEvaluator(pol,g).worst();record['frequency_nominal']=worst
 cases=[Grid(g.mode*m,g.zeta*z,20*gain) for gain,m,z in itertools.product([1.,1.1],[.9,1.1],[.8,1.])];transfer=[];curveall={'W':ws,'nominal':ys}
 for i,grid in enumerate(cases):
  result,_,y=FrequencyEvaluator(pol,grid).worst();transfer.append(result);curveall['corner_'+str(i)]=y
 record['frequency_transfer_corners']=transfer;record['frequency_transfer_worst']=max(transfer,key=lambda r:r['peak_Hz'])
 record['nominal_analytic_amplitude_bound_Hz']=cap*g.G();record['nominal_analytic_slew_bound_Hz']=pol.R*g.slew_norm();record['nominal_combined_bound_Hz']=min(cap*g.G(),pol.R*g.slew_norm())
 rg=Grid(g.mode*.9,g.zeta*.8,22.);record['box_analytic_amplitude_bound_Hz']=cap*rg.G()
 record['analytic_guard_status']='guaranteed on specified whole box under stated model' if cap*rg.G()<=F*(1+1e-12) else ('guaranteed nominal model only' if cap*g.G()<=F*(1+1e-12) else 'no guard guarantee')
 record['physical_max_abs_slew']=float(np.max(abs(pol.slope)));record['actual_max_power']=float(pol.p.max());record['hard_endpoint_work_completion_time']=float(pol.t[-1])
 np.savez_compressed(ROOT/f'curves/{id}_{label}_eos.npz',**curveall)
 np.savetxt(ROOT/f'curves/{id}_{label}_path.csv',np.column_stack([pol.x,pol.z,pol.p,pol.t]),delimiter=',',header='work,z,power,time',comments='')
 record['curve_path']=f'curves/{id}_{label}_eos.npz';record['control_path']=f'curves/{id}_{label}_path.csv'

def run_case(config,protocolhash):
 id=config['id'];b=config['beta'];R=config['R'];g=Grid(config['mode_Hz'],config['zeta']);rg=Grid(g.mode*.9,g.zeta*.8,22.)
 caps={'nominal':F/g.G(),'robust':F/rg.G(),'unguarded':b*C/(1-b)}
 row={'id':id,'split':'design' if id=='design' else 'confirmation','config':config,'protocol_sha256':protocolhash,'nominal_grid':g.asdict(),'robust_worst_grid':rg.asdict(),'caps':caps,'solvers':{},'policies':{},'bellman':{},'failures':[]};pth=ROOT/f'raw/{id}.json'
 def checkpoint():pth.write_text(json.dumps(row,indent=2,allow_nan=False))
 for label,cap in caps.items():
  rr=[];initial=None
  for N in [64,128,256]:
   try:
    r=safe_solver(b,R,cap,N,initial);rr.append(r);initial=r['z']
    if not r['success']:row['failures'].append({'controller':label,'N':N,'message':r['message']})
   except Exception as e:
    row['failures'].append({'controller':label,'N':N,'error':str(e),'traceback':traceback.format_exc()});checkpoint();raise
  row['solvers'][label]=rr;checkpoint();main=rr[-1];pol=Policy(b,R,np.linspace(0,M,len(main['z'])),main['z'])
  row['policies'][label+'_optimal']={'parts':main['parts'],'mesh_N':256,'pcap':cap,'mesh_128_256_relative_difference':abs(rr[-2]['parts']['objective']-main['parts']['objective'])/main['parts']['objective'],'physical_peak_power':main['actual_peak_power']}
  evaluate_policy(row,label+'_optimal',pol,g,cap);checkpoint()
  if label!='unguarded':
   base=target(b,R,cap);pol=Policy(b,R,base['x'],base['z']);row['policies'][label+'_target']=base;row['policies'][label+'_target']['pcap']=cap;evaluate_policy(row,label+'_target',pol,g,cap);checkpoint()
   row['bellman'][label]=[bellman_cap(b,R,cap,N,sub) for N,sub in [(64,4),(128,8)]];checkpoint()
 for lab in ['nominal','robust']:
  opt=row['policies'][lab+'_optimal'];base=row['policies'][lab+'_target'];opt['weighted_objective_gain_vs_target_percent']=100*(base['parts']['objective']-opt['parts']['objective'])/base['parts']['objective'];opt['bellman_128_excess_percent']=100*(row['bellman'][lab][-1]['objective']-opt['parts']['objective'])/opt['parts']['objective']
 checkpoint();print('DONE',id,'gain',row['policies']['nominal_optimal']['weighted_objective_gain_vs_target_percent'],'peak',row['policies']['nominal_optimal']['frequency_nominal']['peak_Hz'],'uncertain',row['policies']['nominal_optimal']['frequency_transfer_worst']['peak_Hz'],flush=True)
 return row

def main():
 p=ROOT/'PROTOCOL.json';h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==(ROOT/'PROTOCOL.sha256').read_text().split()[0];protocol=json.loads(p.read_text());verify_design();requested=sys.argv[1:] or ['all'];cases=protocol['design']+protocol['confirmation']
 if requested!=['all']:cases=[c for c in cases if c['id'] in requested or ('confirmation' in requested and c['id']!='design')]
 for case in cases:run_case(case,h)
if __name__=='__main__':main()
