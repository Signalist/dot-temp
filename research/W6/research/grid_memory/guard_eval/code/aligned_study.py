from guard_study import *
from numpy.polynomial.legendre import leggauss
from scipy.optimize import minimize,linprog
class GeneralMesh:
 def __init__(self,c,x,order):
  self.c=c;self.xx=x;self.h=np.diff(x)[:,None];N=len(x)-1;u,w=leggauss(order);u=(u+1)/2;w=w/2
  self.u=np.broadcast_to(u,(N,order)).copy();self.w=np.broadcast_to(w,(N,order)).copy();self.u[0]=u**6;self.w[0]=w*6*u**5;self.u[-1]=1-u**3;self.w[-1]=w*3*u**2;self.x=x[:-1,None]+self.h*self.u
 def evaluate(self,z,gradient=False,parts=False):
  c=self.c;u=self.u;ww=self.h*self.w;zz=z[:-1,None]*(1-u)+z[1:,None]*u
  if np.any(zz<=0):return (1e100,np.zeros(len(z))) if gradient else 1e100
  p=c.P(zz);S=c.S(self.x);f=c.f(self.x);energy=np.sum(ww*(S*p**(1-c.beta)+f*p*p/(2*c.R)));task=np.sum(ww*S/p**c.beta);tail=np.sum(ww*f*p/c.R);val=energy+c.c*(task+tail)
  if parts:return {'dynamic_energy':float(energy),'task_time':float(task),'recovery_time':float(tail),'cycle_time':float(task+tail),'objective':float(val)}
  if gradient:
   gz=ww*c.Fz(self.x,zz);g=np.zeros(len(z));g[:-1]+=np.sum(gz*(1-u),axis=1);g[1:]+=np.sum(gz*u,axis=1);return float(val),g
  return float(val)
def aligned(beta,R,cap,N):
 c=CappedCase(beta,R*M,C,cap);q=min(c.A(cap),c.A(c.critical),c.R/2);base=target(beta,R,cap);qb=float(c.A(base['target']));x=np.unique(np.r_[np.linspace(0,1,N+1),q/c.R,1-q/c.R,qb/c.R,1-qb/c.R]);h=np.diff(x)
 up=np.minimum(c.R*x,c.cap(x));free=np.arange(1,len(x)-1);D=np.diff(np.eye(len(x)),axis=0);Af=D[:,free];lb=np.full(len(free),1e-14);ub=up[free];mesh=GeneralMesh(c,x,32)
 z0=np.minimum(np.minimum(c.R*x,qb),c.R*(1-x));v=z0[free]
 def expand(v):return np.r_[0.,v,0.]
 def fun(v):val,g=mesh.evaluate(expand(v),True);return val,g[free]
 cons={'type':'ineq','fun':lambda v:np.r_[c.R*h-Af@v,c.R*h+Af@v],'jac':lambda v:np.r_[-Af,Af]}
 res=minimize(fun,v,jac=True,method='SLSQP',bounds=list(zip(lb,ub)),constraints=cons,options={'ftol':2e-12,'maxiter':1200});z=expand(res.x);val,g=fun(res.x)
 lp=linprog(g,A_ub=np.r_[Af,-Af],b_ub=np.r_[c.R*h,c.R*h],bounds=list(zip(lb,ub)),method='highs')
 gap=float(g@res.x-lp.fun)*M if lp.success else None
 scale=min(1.,np.min(c.R*h/np.maximum(abs(np.diff(z)),1e-300)),float(c.A(cap))/max(z.max(),1e-300))*(1-1e-12);z*=scale
 parts={k:v*M for k,v in GeneralMesh(c,x,96).evaluate(z,parts=True).items()}
 return {'N_uniform_component':N,'actual_intervals':len(x)-1,'x':(x*M).tolist(),'z':z.tolist(),'parts':parts,'success':bool(res.success),'message':res.message,'iterations':int(res.nit),'finite_mesh_linearization_gap':gap,'inward_scale':float(scale),'quadrature_difference':abs(parts['objective']-val*M),'max_physical_slew':float(np.max(abs(np.diff(z)/h))/M),'pcap':cap,'global_target_objective':base['parts']['objective'],'gain_vs_global_target_percent':100*(base['parts']['objective']-parts['objective'])/base['parts']['objective']}
def run():
 manifest=json.loads((ROOT/'PROTOCOL.json').read_text());h=hashlib.sha256((ROOT/'AMENDMENT_KNEE_ALIGNMENT.json').read_bytes()).hexdigest();assert h==(ROOT/'AMENDMENT_KNEE_ALIGNMENT.sha256').read_text().split()[0]
 out=[]
 for cfg in manifest['design']+manifest['confirmation']:
  source=json.loads((ROOT/f"raw/{cfg['id']}.json").read_text());r={'id':cfg['id'],'config':cfg,'amendment_sha256':h,'solvers':{},'policies':{}}
  g=Grid(cfg['mode_Hz'],cfg['zeta'])
  for label in ['nominal','robust']:
   cap=source['caps'][label];rows=[aligned(cfg['beta'],cfg['R'],cap,N) for N in [128,256]];r['solvers'][label]=rows;v=rows[-1]
   r['policies'][label+'_aligned_optimal']={'parts':v['parts'],'pcap':cap,'refinement_relative_difference':abs(rows[0]['parts']['objective']-v['parts']['objective'])/v['parts']['objective'],'gain_vs_global_target_percent':v['gain_vs_global_target_percent']}
   pol=Policy(cfg['beta'],cfg['R'],v['x'],v['z']);evaluate_policy(r,label+'_aligned_optimal',pol,g,cap)
  out.append(r);(ROOT/'raw/ALIGNED_RESULTS.json').write_text(json.dumps(out,indent=2));print('ALIGNED',cfg['id'],[(k,v[-1]['gain_vs_global_target_percent']) for k,v in r['solvers'].items()],flush=True)
 return out
if __name__=='__main__':run()
