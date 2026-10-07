"""Global constant-target comparison for an atomic EOS distribution, by exact breakpoints.
This fixes the flat unreachable-target region in a generic bounded scalar search.
"""
import numpy as np
from scipy.optimize import brentq

def global_target(c,work,prob):
 work=np.asarray(work);prob=np.asarray(prob);R=c.R;b=c.beta;K=1+b
 cap=min(float(c.A(c.critical)),R/2)
 cuts=np.unique(np.r_[0.,cap,R*work,R*(1-work)]);cuts=cuts[(cuts>=0)&(cuts<=cap)];candidates=list(cuts[cuts>0])
 def objective(q):
  P=float(c.P(q));a=q/R;end=1-a;early=work<=a;late=work>=end;middle=~early&~late
  v=np.empty(len(work));v[early]=2*c.H(R*work[early]);v[middle]=2*c.H(q)+(work[middle]-a)*c.G(q);v[late]=2*c.H(q)+(1-2*a)*c.G(q)
  return float(prob@v)
 roots=[]
 for q0,q1 in zip(cuts[:-1],cuts[1:]):
  mid=(q0+q1)/2;middle=(work>mid/R)&(work<1-mid/R);late=work>=1-mid/R
  m=float(prob[middle].sum());C=float(prob[middle]@work[middle]+prob[late].sum());D=float(m+2*prob[late].sum())
  def deriv(p):
   q=p**K/K;return m*(p+c.c)*p**K+(R*C-D*q)*((1-b)*p-b*c.c)
  p0=float(c.P(q0));p1=float(c.P(q1));v0=deriv(p0);v1=deriv(p1)
  if v0*v1<0:
   p=brentq(deriv,p0,p1,xtol=1e-14);q=float(c.A(p));candidates.append(q);roots.append(q)
 vals=[objective(q) for q in candidates];j=int(np.argmin(vals));q=candidates[j]
 return {'target':float(c.P(q)),'target_z':q,'objective':vals[j],'method':'All EOS branch breakpoints plus the unique stationary root on each smooth interval','breakpoint_count':len(cuts),'stationary_roots':roots,'evaluated_candidates':len(candidates),'global_within_constant_target_class':True}
