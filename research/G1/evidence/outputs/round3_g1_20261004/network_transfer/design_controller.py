"""Conventional robust affine sampled-disturbance-feedback LP.
Only the last received P class enters the targets; exact phase never enters.
Recovery is a fixed trapezoid scaled by measured/applied-power energy debt.
"""
from pathlib import Path
import numpy as np,json,time,hashlib,argparse
from scipy.optimize import linprog
from scipy.sparse import csr_matrix,vstack
OUT=Path(__file__).resolve().parent
SRC=OUT.parents[1]/'round2_20261003/grid_transfer/kundur_reduced51.npz'
d=np.load(SRC);A=d['A'];B=d['B'][:,2];C=d['C_frequency_Hz'];lam,V=np.linalg.eig(A);bm=np.linalg.solve(V,B);CV=C@V
ETA=.95;TAU=.05;POWER=50.;BAND=.093;HORIZON=100.
# First target at .05 is determined at reconnect from known initial class.
# Target at .15 is based on sample0; target at .25 on sample .1 received .15.
SUPPORT=12.15
nodes=np.r_[0,np.arange(.05,SUPPORT-.00001,.1),SUPPORT,20.,21.,59.,60.]
ns=len(nodes)-5 # index of final zero support knot, =122
nfree=ns-1
areaweights=(nodes[2:ns+1]-nodes[:ns-1])/2
RECOVERY_AREA=39.

def response(tt,ramp=False):
 tt=np.asarray(tt);flat=tt.ravel();p=np.maximum(flat,0);z=p[:,None]*lam
 tab=((np.expm1(z)-z)@(CV*(bm/lam**2)).T).real if ramp else (np.expm1(z)@(CV*(bm/lam)).T).real
 tab[flat<0]=0
 return tab.reshape(*tt.shape,4)

def loadtrace(t,r,high,scale=1.,ramp=0.):
 t=np.asarray(t);y=scale*(100 if high else 50)*response(t)
 for k,at in enumerate(np.arange(r,max(t)+5,5.)):
  delta=50*(-1 if high else 1)*(-1)**k*scale
  if ramp<=0:y+=delta*response(t-at)
  else:y+=delta*(response(t-at,True)-response(t-at-ramp,True))/ramp
 return y

def kernel(t):
 a=nodes[:-2];b=nodes[1:-1];c=nodes[2:];h0=b-a;h1=c-b
 return (response(t[:,None]-a,True)/h0[None,:,None]-response(t[:,None]-b,True)*(1/h0+1/h1)[None,:,None]+response(t[:,None]-c,True)/h1[None,:,None]).transpose(0,2,1).reshape(-1,len(b))

def p_class(t,r,high):
 t=np.asarray(t);flips=np.where(t<r,0,1+np.floor((t-r)/5.+1e-10)).astype(int)
 return np.logical_xor(high,flips%2).astype(int)

def mapping(r,high,feedback=True):
 # pfree vector internal support nodes; deterministic functions of received samples.
 nv=nfree*(2 if feedback else 1)
 M=np.zeros((len(nodes),nv))
 for j in range(nfree):
  # Segment ending at nodes[j+1] began at nodes[j]. At its start the
  # most recent newly delivered sample was floor((t-.05)/.1)*.1.
  received_sample=max(0.,round(nodes[j]-.05,10))
  cls=int(p_class(received_sample,r,high)) if j>=2 else int(high)
  M[j+1,j*(2 if feedback else 1)+(cls if feedback else 0)]=1
 D=areaweights@M[1:ns]
 M[-3]=-D/(ETA**2*RECOVERY_AREA);M[-2]=M[-3]
 return M,D

def metrics(p):
 h=np.diff(nodes);areas=h*(p[:-1]+p[1:])/2
 deplete=np.where(areas>=0,areas/ETA,areas*ETA);soc=np.r_[0,-np.cumsum(deplete)]
 sl=np.diff(p)/h;v0=p[:-1]+TAU*sl;v1=p[1:]+TAU*sl
 return {'E_MWs':float(np.ptp(soc)),'return_error_MWs':float(soc[-1]),'discharge_MWs':float(areas[areas>0].sum()),'charge_MWs':float(-areas[areas<0].sum()),'max_power_MW':float(max(abs(p))),'max_command_MW':float(max(np.max(abs(v0)),np.max(abs(v1)))),'max_slew_MW_s':float(max(abs(sl))),'crossing_segments':int(sum(p[:-1]*p[1:]<-1e-10))}

def solve(high,feedback,phases,band=BAND,dt=.2):
 started=time.time();nv=nfree*(2 if feedback else 1);N=nv+1
 t=np.arange(0,HORIZON+dt/2,dt);K=kernel(t);Ks=[];ys=[];Ms=[];ds=[]
 rows=[];rhs=[]
 for r in phases:
  M,D=mapping(r,high,feedback);Ms.append(M);ds.append(D)
  Q=K@M[1:-1];y=loadtrace(t,r,high).ravel();Ks.append(Q);ys.append(y)
  rows.extend([csr_matrix(np.c_[-Q,np.zeros(len(Q))]),csr_matrix(np.c_[Q,np.zeros(len(Q))])]);rhs.extend([band-y,band+y])
  rows.append(csr_matrix(np.r_[D/ETA,-1][None,:]));rhs.append([0.])
  slopes=np.diff(M,axis=0)/np.diff(nodes)[:,None]
  for W,cap in [(M,POWER),(slopes,10*POWER),(M[:-1]+TAU*slopes,POWER),(M[1:]+TAU*slopes,POWER)]:
   aug=csr_matrix(np.c_[W,np.zeros(len(W))]);rows.extend([aug,-aug]);rhs.extend([np.full(len(W),cap)]*2)
 c=np.r_[np.full(nv,1e-8),1.];bounds=[(0,POWER)]*nv+[(0,None)]
 iters=[]
 for iteration in range(9):
  tic=time.time();res=linprog(c,A_ub=vstack(rows,format='csr'),b_ub=np.concatenate(rhs),bounds=bounds,method='highs',options={'dual_feasibility_tolerance':1e-8,'primal_feasibility_tolerance':1e-8})
  rec={'iteration':iteration,'success':bool(res.success),'status':res.message,'seconds':time.time()-tic,'n_constraints':sum(q.shape[0] for q in rows)}
  if not res.success:iters.append(rec);break
  fine=np.arange(0,HORIZON+.01,.02);Kfine=kernel(fine) if iteration==0 else Kfine
  peak=0.;nnew=0
  for r,M in zip(phases,Ms):
   yy=loadtrace(fine,r,high).ravel();qq=Kfine@M[1:-1];f=yy-qq@res.x[:nv];peak=max(peak,max(abs(f)))
   bad=np.where(abs(f)>band+2e-7)[0]
   if len(bad):
    # All newly violated rows; keep exact sign.
    sign=np.sign(f[bad]);rows.append(csr_matrix(np.c_[-qq[bad]*sign[:,None],np.zeros(len(bad))]));rhs.append(band-sign*yy[bad]);nnew+=len(bad)
  rec.update(E_MWs=float(res.x[-1]),fine_peak_Hz=float(peak),new_violations=nnew);iters.append(rec);print(high,feedback,rec,flush=True)
  if nnew==0:break
 summary={'initial_high':bool(high),'feedback':bool(feedback),'phases_r_s':list(map(float,phases)),'band_Hz':band,'P_MW':POWER,'tau_s':TAU,'eta':ETA,'support_end_s':SUPPORT,'recovery_end_s':60.,'iterations':iters,'seconds':time.time()-started,'success':bool(res.success)}
 if res.success:
  theta=res.x[:nv];summary['E_MWs']=float(res.x[-1]);summary['phase_metrics']=[dict(r=float(r),**metrics(M@theta)) for r,M in zip(phases,Ms)]
  return summary,theta
 return summary,None

if __name__=='__main__':
 pa=argparse.ArgumentParser();pa.add_argument('--band',type=float,default=BAND);pa.add_argument('--spacing',type=float,default=.5);pa.add_argument('--kind',choices=['feedback','openloop','both'],default='both');a=pa.parse_args()
 phases=np.r_[.0001,np.arange(a.spacing,5.00001,a.spacing)]
 result=[]
 for fb in ([True,False] if a.kind=='both' else [a.kind=='feedback']):
  for hi in [False,True]:
   name=f'{"feedback" if fb else "openloop"}_{"high" if hi else "low"}_b{a.band:g}_dr{a.spacing:g}'
   r,theta=solve(hi,fb,phases,a.band);(OUT/(name+'.json')).write_text(json.dumps(r,indent=2));result.append(r)
   if theta is not None:np.savez_compressed(OUT/(name+'.npz'),theta=theta,nodes=nodes,initial_high=hi,feedback=fb,phases=phases,band=a.band)
 (OUT/'DESIGN_RESULTS.json').write_text(json.dumps(result,indent=2))
