from design_controller import *

def advance(z,q,r,h):
 a=z+bm*q/lam+bm*r/lam**2
 return np.exp(lam*h)*a-bm*(q+r*h)/lam-bm*r/lam**2

def bound_interval(z,q,r,h,tol=1e-5,depth=0):
 z1=advance(z,q,r,h);y0=(CV@z).real;y1=(CV@z1).real
 err=abs(CV)@(abs(lam)**2*abs(z+bm*q/lam+bm*r/lam**2))*h*h/8
 low=max(np.max(abs(y0)),np.max(abs(y1)));up=low+np.max(err)
 if max(err)<=tol:return z1,float(low),float(up),1
 if depth>30:raise RuntimeError('Exceeded interval recursion depth')
 zm,l0,u0,n0=bound_interval(z,q,r,h/2,tol,depth+1)
 z1,l1,u1,n1=bound_interval(zm,q+r*h/2,r,h/2,tol,depth+1)
 return z1,max(l0,l1),max(u0,u1),n0+n1

def perstate(theta):
 aa=np.exp(lam*5);v=bm*np.expm1(lam*5)/lam;z0=v*(100*aa+50)/(1-aa*aa)
 if theta<5:return np.exp(lam*theta)*z0+100*bm*np.expm1(lam*theta)/lam
 z5=aa*z0+100*v;rr=theta-5
 return np.exp(lam*rr)*z5+50*bm*np.expm1(lam*rr)/lam

zp=perstate(0);zz,l1,u1,nn=bound_interval(zp,100,0,5);_,l2,u2,nn=bound_interval(zz,50,0,5);PER=max(u1,u2)

def certify_one(r,hi,p):
 edges=np.unique(np.round(np.r_[nodes,np.arange(r,100,5),100.],10));z=np.zeros(len(lam),complex);peak=0;up=0;cnt=0
 slopes=np.diff(p)/np.diff(nodes)
 for a,b in zip(edges[:-1],edges[1:]):
  i=np.searchsorted(nodes,a+1e-8,side='right')-1
  if a>=60-1e-8:pp=0;rr=0
  else:pp=p[i]+slopes[i]*(a-nodes[i]);rr=-slopes[i]
  load=50+50*int(p_class(a+1e-8,r,hi));z,lo,ub,n=bound_interval(z,load-pp,rr,b-a)
  peak=max(peak,lo);up=max(up,ub);cnt+=n
 theta=(5-r if hi else 10-r)%10;tail=PER+float(np.max(abs(CV)@abs(z-perstate(theta))))
 return dict(r=float(r),continuous_finite_peak_lower_Hz=peak,continuous_finite_peak_upper_Hz=up,infinite_tail_upper_from100_Hz=tail,intervals=cnt,**metrics(p))

if __name__=='__main__':
 rows=[];allow=json.loads((OUT/'PHASE_LIPSCHITZ_BOUND.json').read_text())['all_future_midpoint_phase_allowance_Hz']
 for fb in [True,False]:
  for hi in [False,True]:
   tag=f'binned93_{"feedback" if fb else "openloop"}_{"high" if hi else "low"}'
   path=OUT/(tag+'.npz')
   if not path.exists():continue
   d=np.load(path);results=[]
   for r in d['phases']:
    M,D=mapping(r,hi,fb);results.append(certify_one(r,hi,M@d['theta']))
   summary={'tag':tag,'bin_midpoint_certificates':results,'phase_allowance_Hz':allow,'continuous_all_phase_all_future_upper_Hz':max(max(x['continuous_finite_peak_upper_Hz'],x['infinite_tail_upper_from100_Hz']) for x in results)+allow,'periodic_orbit_upper_Hz':PER,'all_phase_E_MWs':max(x['E_MWs'] for x in results),'all_phase_max_command_MW':max(x['max_command_MW'] for x in results),'all_phase_max_slew_MW_s':max(x['max_slew_MW_s'] for x in results),'max_SOC_return_error_MWs':max(abs(x['return_error_MWs']) for x in results),'arithmetic':'ordinary floating-point analytic enclosures, no interval-arithmetic rounding certificate','scope':'LTI, exact two-level/sampling/actuator/efficiency model; nonlinear safety excluded'}
   (OUT/(tag+'_certificate.json')).write_text(json.dumps(summary,indent=2));rows.append(summary);print({k:v for k,v in summary.items() if k!='bin_midpoint_certificates'},flush=True)
 (OUT/'BINNED93_LTI_CERTIFICATES.json').write_text(json.dumps(rows,indent=2))
