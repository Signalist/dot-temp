"""Standard Kelley supporting-cut LP for exact actuator cells.
All supporting cuts are mathematical outer relaxations; floats are not directed intervals.
"""
import sys,time,json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from model import Params,grid,poly_segments
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'theory'))
from exact_cell import Actuator,cell_bounds,reachability

def solve_exact_outer(alpha,beta,n=80,par=Params(),tighten=False,max_iter=100,save=None):
    tm=time.perf_counter(); t=grid(par,n); m=poly_segments(t,alpha,beta,par); N=m['n']; h=m['h']; baseV=2*(N+1)+1; sidx=baseV-1; V=baseV+2*N+1
    cur=par.imax**2-np.max(np.sum(m['i']**2,axis=1))
    if cur<-1e-10:return dict(status='current_infeasible',alpha=alpha,beta=beta,n=n)
    bp=np.arange(N+1); cp=np.arange(N+1)+N+1
    rows=[]; rhs=[]
    def add(pairs,value):
        z=np.zeros(V)
        for j,a in pairs:z[j]+=a
        rows.append(z);rhs.append(float(value))
    A=np.r_[m['offset'][0,0],np.sum(m['offset'],axis=1)]
    # Curvature allowances differ per physical slack. Max |Woffset''| in real time.
    awpp=np.maximum(np.abs(2*m['offset'][:,2]),np.abs(2*m['offset'][:,2]+6*m['offset'][:,3]))/h**2
    modpp=np.maximum(np.abs(2*(m['offset'][:,2]-m['modfloor'][:,2])),np.abs(2*(m['offset'][:,2]-m['modfloor'][:,2])+6*m['offset'][:,3]))/h**2
    mw=(par.ramp+awpp)*h*h/8 if tighten else np.zeros(N)
    mm=(par.ramp+modpp)*h*h/8 if tighten else np.zeros(N)
    mb=par.ramp*h*h/8 if tighten else np.zeros(N)
    for k in range(N):
        for j,x in [(k,0),(k+1,1)]:
            aa=A[j]; mf=np.polynomial.polynomial.polyval(x,m['modfloor'][k])
            add([(cp[j],-1),(sidx,1)],par.W0+aa-par.Wmin-mw[k])
            add([(cp[j],1),(sidx,1)],par.Wmax-par.W0-aa-mw[k])
            add([(cp[j],-1),(sidx,1)],par.W0+aa-mf-mm[k])
            add([(cp[j],1)],par.B0-par.Bmin-mb[k]);add([(cp[j],-1)],par.Bmax-par.B0-mb[k])
        add([(bp[k+1],1),(bp[k],-1)],par.ramp*h[k]);add([(bp[k+1],-1),(bp[k],1)],par.ramp*h[k])
        add([(bp[k+1],par.tau),(bp[k],-par.tau),(cp[k+1],1),(cp[k],-1)],par.umax*h[k])
        add([(bp[k+1],-par.tau),(bp[k],par.tau),(cp[k+1],-1),(cp[k],1)],par.umax*h[k])
        add([(cp[k+1],1),(cp[k],-1),(bp[k],-h[k]/2),(bp[k+1],-h[k]/2)],par.ramp*h[k]**2/4)
        add([(cp[k+1],-1),(cp[k],1),(bp[k],h[k]/2),(bp[k+1],h[k]/2)],par.ramp*h[k]**2/4)
    av=np.arange(N+1)+baseV; tv=np.arange(N)+baseV+N+1
    for k in range(N+1):
        add([(bp[k],1),(av[k],-1)],0);add([(bp[k],-1),(av[k],-1)],0)
    for k in range(N):
        add([(bp[k+1],1),(bp[k],-1),(tv[k],-1)],0);add([(bp[k+1],-1),(bp[k],1),(tv[k],-1)],0)
    bounds=[(-par.bmax,par.bmax)]*(N+1)+[(par.B0-par.Bmax,par.B0-par.Bmin)]*(N+1)+[(None,None)]+[(0,None)]*(2*N+1)
    for j in np.where(t<=par.delay+1e-12)[0]:bounds[bp[j]]=(0,0);bounds[cp[j]]=(0,0)
    bounds[bp[-1]]=(0,0);bounds[cp[-1]]=(0,0)
    obj=np.zeros(V);obj[sidx]=-1
    secondary=np.zeros(V);secondary[av]=.01/(N+1);secondary[tv]=1/N
    act=Actuator(-par.umax,par.umax,par.tau,par.ramp,par.ramp)
    history=[]
    for it in range(max_iter):
        used_rhs=np.array(rhs); used_rows=np.array(rows)
        res=linprog(obj,A_ub=used_rows,b_ub=used_rhs,bounds=bounds,method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
        if not res.success:return dict(status='lp_'+res.message,alpha=alpha,beta=beta,n=n,iterations=it)
        primary=res; sigupper=float(primary.x[sidx])
        sr=np.zeros(V);sr[sidx]=-1
        res2=linprog(secondary,A_ub=np.vstack([used_rows,sr]),b_ub=np.r_[used_rhs,-sigupper+1e-7],bounds=bounds,method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
        if res2.success:res=res2
        b=res.x[bp]; C=res.x[cp]; count=0; errpow=0.; errarea=0.
        for k in range(N):
            br=cell_bounds(float(np.clip(b[k],-par.umax,par.umax)),float(np.clip(b[k+1],-par.umax,par.umax)),h[k],act,anchor_unreachable=True)
            x0=br['anchor_b0'];x1=br['anchor_b1'];dc=C[k+1]-C[k]
            ep=max(br['b1_min']-b[k+1],b[k+1]-br['b1_max'],0);errpow=max(errpow,ep)
            if b[k+1]>br['b1_max']+1e-7:
                g=br['grad_b1_max'];add([(bp[k+1],1),(bp[k],-g)],br['b1_max']-g*x0+1e-10);count+=1
            if b[k+1]<br['b1_min']-1e-7:
                g=br['grad_b1_min'];add([(bp[k+1],-1),(bp[k],g)],-br['b1_min']+g*x0+1e-10);count+=1
            g0,g1=br['grad_max'];bound=br['Imax']+g0*(b[k]-x0)+g1*(b[k+1]-x1)
            ea=max(dc-bound,0);errarea=max(errarea,ea)
            if ea>1e-9:
                add([(cp[k+1],1),(cp[k],-1),(bp[k],-g0),(bp[k+1],-g1)],br['Imax']-g0*x0-g1*x1+1e-11);count+=1
            g0,g1=br['grad_min'];bound=br['Imin']+g0*(b[k]-x0)+g1*(b[k+1]-x1)
            ea=max(bound-dc,0);errarea=max(errarea,ea)
            if ea>1e-9:
                add([(cp[k+1],-1),(cp[k],1),(bp[k],g0),(bp[k+1],g1)],-br['Imin']+g0*x0+g1*x1+1e-11);count+=1
        history.append(dict(iteration=it,upper_margin=float(sigupper),new_cuts=count,max_reach_error_kW=errpow,max_area_error_kJ=errarea))
        if count==0:break
    out=dict(status='converged' if count==0 else 'iteration_limit',alpha=alpha,beta=beta,n=n,intervals=N,margin_kJ=float(sigupper),iterations=it+1,cuts=len(rows),runtime_s=time.perf_counter()-tm,tightened=bool(tighten),max_nodal_margin_tightening_kJ=float(max(np.max(mw),np.max(mm))),history=history,
             max_linear_violation=float(max(0,np.max(np.array(rows)@res.x-np.array(rhs)))),duality_gap=float(abs(primary.fun-(np.dot(primary.ineqlin.marginals,used_rhs)+sum((lo or 0)*x for (lo,hi),x in zip(bounds,primary.lower.marginals))+sum((hi or 0)*x for (lo,hi),x in zip(bounds,primary.upper.marginals))))))
    if save:
        np.savez_compressed(save,t=t,b=b,charge=C,alpha=alpha,beta=beta,par_json=json.dumps(par.dict()),history=json.dumps(history),tightened=tighten,lp_A=np.array(rows),lp_rhs=np.array(rhs),lp_x=res.x,lp_duals=primary.ineqlin.marginals)
    return out
if __name__=='__main__':
 for nn in [40,80,160]:
  for tight in [False,True]:print(json.dumps(solve_exact_outer(100,600,nn,tighten=tight),indent=2))
