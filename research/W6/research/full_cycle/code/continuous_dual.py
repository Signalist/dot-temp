"""Continuous weak-dual functional using saved feasible paths and LP-derived costates.
The formula is a theorem; all evaluated bounds remain floating (no interval enclosure).
"""
from pathlib import Path
import json,numpy as np
from scipy.optimize import linprog,brentq
from numpy.polynomial.legendre import leggauss
from cycle_model import Case,Mesh
ROOT=Path(__file__).resolve().parents[1]
def compute(row):
 c=Case(**row['case']);z=np.array(row['z']);N=len(z)-1;h=1/N;x=np.linspace(0,1,N+1)
 val,g=Mesh(c,N,64).evaluate(z,True);D=np.diff(np.eye(N+1),axis=0);A=D[:,1:-1]
 up=np.minimum(c.R*x[1:-1],c.cap(x[1:-1]));lo=np.maximum(0,c.z0-c.R*x[1:-1]);d0=D[:,0]*c.z0
 lp=linprog(g[1:-1],A_ub=np.r_[A,-A],b_ub=np.r_[c.R*h-d0,c.R*h+d0],bounds=list(zip(lo,up)),method='highs')
 y=lp.ineqlin.marginals[:N]-lp.ineqlin.marginals[N:]
 xx=np.r_[0,(np.arange(N)+.5)*h,1];yy=np.r_[y[0],y,y[-1]]
 def calculate(order):
  u,w=leggauss(order);u=(u+1)/2;w=w/2;total=-yy[0]*c.z0
  for i in range(len(xx)-1):
   U=u.copy();W=w.copy()
   if i==0:U=u**6;W=w*6*u**5
   if i==len(xx)-2:U=1-u**3;W=w*3*u**2
   width=xx[i+1]-xx[i];slope=(yy[i+1]-yy[i])/width;X=xx[i]+U*width;Y=yy[i]+U*(yy[i+1]-yy[i]);terms=[]
   for a,b in zip(X,Y):
    upper=min(c.z0+c.R*a,float(c.cap(a)));lower=max(0.,c.z0-c.R*a)
    if upper-lower<1e-13:v=max(upper,1e-300)
    elif c.Fz(a,upper)<=slope:v=upper
    elif lower>0 and c.Fz(a,lower)>=slope:v=lower
    else:v=brentq(lambda vv:c.Fz(a,vv)-slope,max(lower,upper*1e-14),upper,xtol=max(upper*1e-13,1e-16),rtol=1e-13)
    terms.append(c.F(a,v)-slope*v-c.R*abs(b))
   total+=width*np.dot(W,terms)
  return float(total)
 low=calculate(32);high=calculate(96);primal=row['parts']['objective']
 return {'case':row['case'],'N':N,'primal_feasible_numerical':primal,'continuous_dual_numerical':high,'gap':primal-high,'relative_gap':(primal-high)/primal,'quadrature_difference':abs(high-low),'dual_x':xx.tolist(),'dual_y':yy.tolist(),'lp_success':lp.success,'outward_rounded':False}
def run():
 out=[]
 for row in json.load(open(ROOT/'results/PRIMARY_MESHES.json')):
  if row['N']!=128:continue
  r=compute(row);out.append(r);(ROOT/'results/CONTINUOUS_DUAL.json').write_text(json.dumps(out,indent=2));print(row['case'],r['relative_gap'],r['quadrature_difference'],flush=True)
if __name__=='__main__':run()
