"""Mature conic certificates. Exact polynomial nonnegativity uses Markov-Lukacs."""
import os,sys,time,json
import numpy as np
import cvxpy as cp
from model import Params,grid,poly_segments

def positive_cubic(coeff,cons,name=''):
    n=coeff.shape[0]
    q=cp.Variable((n,3),name=name+'Q'); r=cp.Variable((n,3),name=name+'R')
    cons.extend([coeff[:,0]==r[:,0],coeff[:,1]==q[:,0]+2*r[:,1]-r[:,0],
                 coeff[:,2]==2*q[:,1]+r[:,2]-2*r[:,1],coeff[:,3]==q[:,2]-r[:,2],
                 cp.SOC(q[:,0]+q[:,2],cp.vstack([2*q[:,1],q[:,0]-q[:,2]]),axis=0),
                 cp.SOC(r[:,0]+r[:,2],cp.vstack([2*r[:,1],r[:,0]-r[:,2]]),axis=0)])

def constant_poly(vec,n):
    return cp.hstack([cp.reshape(vec,(n,1),order='C'),np.zeros((n,3))])

def polynomial_min(coefs):
    a=np.asarray(coefs); out=[]
    for p in a:
        roots=np.polynomial.polynomial.polyroots(np.arange(1,4)*p[1:])
        xs=[0.,1.]+[float(z.real) for z in roots if abs(z.imag)<1e-8 and 0<z.real<1]
        out.append(min(np.polynomial.polynomial.polyval(x,p) for x in xs))
    return np.array(out)

def solve_inner(alpha,beta,n=80,par=Params(),inventory=True,modulation=True,solver='CLARABEL',save=None,restore_orbit=True):
    t=grid(par,n); m=poly_segments(t,alpha,beta,par); h=m['h']; N=m['n']; tm=time.perf_counter()
    current_margin=float(par.imax**2-np.max(np.sum(m['i']**2,axis=1)))
    if current_margin < -1e-10:
        return {'status':'current_infeasible','alpha':alpha,'beta':beta,'n':n,'current_squared_margin':current_margin}
    # b(x)=b0+a*x+c*x^2, C(x)=C0+h*b0*x+h*a*x^2/2+h*c*x^3/3.
    b=cp.Variable(N+1); a=cp.Variable(N); c=cp.Variable(N); C=cp.Variable(N+1)
    sigma=cp.Variable()
    Cpoly=cp.hstack([cp.reshape(C[:-1],(N,1),order='C'),cp.reshape(cp.multiply(h,b[:-1]),(N,1),order='C'),
                    cp.reshape(cp.multiply(h/2,a),(N,1),order='C'),cp.reshape(cp.multiply(h/3,c),(N,1),order='C')])
    bpoly=cp.hstack([cp.reshape(b[:-1],(N,1),order='C'),cp.reshape(a,(N,1),order='C'),cp.reshape(c,(N,1),order='C'),np.zeros((N,1))])
    deriv=cp.hstack([cp.reshape(cp.multiply(1/h,a),(N,1),order='C'),cp.reshape(cp.multiply(2/h,c),(N,1),order='C'),np.zeros((N,2))])
    upoly=bpoly+par.tau*deriv
    Wpoly=m['offset']+Cpoly+constant_poly(np.full(N,par.W0),N)
    Bpoly=constant_poly(np.full(N,par.B0),N)-Cpoly
    con=[b[0]==0,b[-1]==0,C[0]==0,b[1:]==b[:-1]+a+c,
         C[1:]==C[:-1]+cp.multiply(h,b[:-1]+a/2+c/3),sigma>=-100]
    if inventory: con.extend([C[-1]==0])
    # All-time DC orbit restoration is always retained; for this task exact loss compensation makes C(T)=0 necessary.
    if restore_orbit: con.extend([par.W0+m['final_A']+C[-1]==par.W0])
    fixed=np.where(t[1:]<=par.delay+1e-12)[0]
    if len(fixed): con.extend([b[fixed]==0,a[fixed]==0,c[fixed]==0])
    polynomials={
        'W_lower':Wpoly-constant_poly(np.full(N,par.Wmin),N)-constant_poly(cp.multiply(np.ones(N),sigma),N),
        'W_upper':constant_poly(np.full(N,par.Wmax),N)-Wpoly-constant_poly(cp.multiply(np.ones(N),sigma),N),
        'B_lower':Bpoly-constant_poly(np.full(N,par.Bmin),N),
        'B_upper':constant_poly(np.full(N,par.Bmax),N)-Bpoly,
        'b_lower':bpoly+constant_poly(np.full(N,par.bmax),N),
        'b_upper':constant_poly(np.full(N,par.bmax),N)-bpoly,
        'u_lower':upoly+constant_poly(np.full(N,par.umax),N),
        'u_upper':constant_poly(np.full(N,par.umax),N)-upoly,
        'ramp_lower':deriv+constant_poly(np.full(N,par.ramp),N),
        'ramp_upper':constant_poly(np.full(N,par.ramp),N)-deriv}
    if modulation:
        polynomials['modulation']=Wpoly-m['modfloor']-constant_poly(cp.multiply(np.ones(N),sigma),N)
    for name,p in polynomials.items():
        scale = par.ramp if name.startswith("ramp") else par.umax if name.startswith(("u_","b_")) else par.B0 if name.startswith("B_") else par.W0
        positive_cubic(p/scale,con,name)
    prob=cp.Problem(cp.Maximize(sigma-1e-8*cp.sum_squares(b/par.bmax)),con)
    try: prob.solve(solver=solver,tol_gap_abs=1e-6,tol_feas=1e-7,tol_gap_rel=1e-6,max_iter=300)
    except Exception as ex:
        try: prob.solve(solver='CLARABEL',tol_gap_abs=1e-5,tol_feas=1e-6,tol_gap_rel=1e-5,max_iter=500,static_regularization_constant=1e-7)
        except Exception as ex2: return {'status':'solver_error','error':str(ex2),'alpha':alpha,'beta':beta,'n':n}
    out={'status':prob.status,'alpha':alpha,'beta':beta,'n':n,'intervals':N,'current_squared_margin':current_margin,'runtime_s':time.perf_counter()-tm,'gamma_kW':m['profiles']['gamma'],'energy_residual_kJ':m['energy_residual']}
    if b.value is not None:
        mins={k:float(np.min(polynomial_min(v.value))) for k,v in polynomials.items()}
        out.update(margin_kJ=float(sigma.value),polynomial_residual_min=mins,certified_numeric_inner=bool(sigma.value>1e-5 and min(mins.values())>-1e-5))
        if save:
            np.savez_compressed(save,t=t,b=b.value,a=a.value,c=c.value,charge=C.value,Wpoly=Wpoly.value,Bpoly=Bpoly.value,upoly=upoly.value,par_json=json.dumps(par.dict()),alpha=alpha,beta=beta,p=m['profiles']['p'],q=m['profiles']['q'],d=m['profiles']['d'],sigma=float(sigma.value))
    return out

def solve_outer(alpha,beta,n=80,par=Params(),modulation=True):
    """Necessary relaxation for ALL absolutely continuous physical b, not spline-only."""
    t=grid(par,n); m=poly_segments(t,alpha,beta,par); h=m['h']; N=m['n']; tm=time.perf_counter()
    cur=float(par.imax**2-np.max(np.sum(m['i']**2,axis=1)))
    if cur < -1e-10: return {'status':'current_infeasible','alpha':alpha,'beta':beta,'n':n,'current_squared_margin':cur}
    b=cp.Variable(N+1); C=cp.Variable(N+1); sig=cp.Variable()
    db=b[1:]-b[:-1]; dc=C[1:]-C[:-1]; areaerr=dc-cp.multiply(h/2,b[:-1]+b[1:])
    # Sharp integral envelopes for any R-Lipschitz function with given endpoint values.
    slack=par.ramp*h*h/4-cp.square(db)/(4*par.ramp)
    con=[b[0]==0,b[-1]==0,C[0]==0,C[-1]==0,b<=par.bmax,b>=-par.bmax,
         db<=par.ramp*h,db>=-par.ramp*h,areaerr<=slack,-areaerr<=slack,
         par.tau*db+dc<=par.umax*h,par.tau*db+dc>=-par.umax*h]
    A=np.r_[m['offset'][0,0],np.sum(m['offset'],axis=1)]; W=par.W0+A+C
    con.extend([W>=par.Wmin+sig,W<=par.Wmax-sig,C<=par.B0-par.Bmin,C>=par.B0-par.Bmax])
    if modulation:
        # Both one-sided requested converter voltages at electrical knots.
        ml=m['modfloor'][:,0]; mr=np.sum(m['modfloor'],axis=1)
        con.extend([W[:-1]>=ml+sig,W[1:]>=mr+sig])
    fixed=np.where(t<=par.delay+1e-12)[0]
    con.extend([b[fixed]==0,C[fixed]==0])
    prob=cp.Problem(cp.Maximize(sig),con)
    try: prob.solve(solver='CLARABEL',tol_gap_abs=1e-9,tol_feas=1e-9,tol_gap_rel=1e-9,max_iter=300)
    except Exception as ex:return {'status':'solver_error','error':str(ex),'alpha':alpha,'beta':beta,'n':n}
    out={'status':prob.status,'alpha':alpha,'beta':beta,'n':n,'intervals':N,'runtime_s':time.perf_counter()-tm,'current_squared_margin':cur}
    if sig.value is not None:out.update(outer_margin_kJ=float(sig.value),numerically_excluded=bool(sig.value < -1e-5),max_constraint_violation=max(float(np.max(np.asarray(z.violation()))) for z in con))
    return out

if __name__=='__main__':
    p=Params()
    for alpha,beta in [(0,0),(100,600),(200,900),(300,1200),(300,900)]:
        print('INNER',solve_inner(alpha,beta,40,p))
        print('OUTER',solve_outer(alpha,beta,40,p))
