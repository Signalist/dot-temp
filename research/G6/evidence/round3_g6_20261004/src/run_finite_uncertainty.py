"""Finite fixed-angle uncertainty experiments; no arithmetic-type estimation.
Ordinary floats for broad sensitivity study; independent rational enclosures for
one predeclared support certificate. No third-party interval arithmetic required.
"""
from pathlib import Path
from fractions import Fraction as Q
import json, math, time, hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments'; OUT.mkdir(exist_ok=True)

def support(theta,r,a,N=512):
    k=np.arange(N); p=r**k
    return (np.abs(a[0]*np.cos(np.asarray(theta)[...,None]*k)-a[1]*np.sin(np.asarray(theta)[...,None]*k))*p).sum(axis=-1)

rows=[]; start=time.perf_counter()
for r in [.6,.85,.95]:
 for delta in [.001,.01,.1]:
  lo,hi=.7-delta,.7+delta
  for a in [np.array([.25,.75]),np.array([.5,.5]),np.array([.75,.25])]:
   dense=support(np.linspace(lo,hi,32769),r,a)
   norm=np.linalg.norm(a); tail=norm*r**512/(1-r)
   for M in [8,16,32,64,128]:
    grid=support(np.linspace(lo,hi,M+1),r,a); h=(hi-lo)/M
    e1=norm*r/(1-r)**2*h/2+tail
    e2=norm*r*(1+r)/(1-r)**3*h*h/8+tail
    rows.append({'r':r,'theta_halfwidth':delta,'a1':a[0],'a2':a[1],'intervals':M,'grid_lower':float(grid.max()),'dense_diagnostic':float(dense.max()),'first_order_error':e1,'second_order_error':e2,'second_order_upper':float(grid.max()+e2),'dense_covered':bool(dense.max()<=grid.max()+e2+1e-13),'dense_gap':float(dense.max()-grid.max()),'tail':tail})
(OUT/'FINITE_UNCERTAINTY_FLOAT.json').write_text(json.dumps({'scope':'ordinary double; dense grid diagnostic is not ground truth; analytic formula supplies conditional upper bound','rows':rows,'seconds':time.perf_counter()-start},indent=2))
import csv
with (OUT/'finite_uncertainty.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

# Rational certificate with outward integer fixed-point intervals.
D=120; S=10**D; N=512; r=Q(17,20)
def fl(q):return q.numerator//q.denominator
def ce(q):return -((-q.numerator)//q.denominator)
def rational_to_iv(q):return (fl(q*S),ce(q*S))
def add(x,y):return (x[0]+y[0],x[1]+y[1])
def neg(x):return (-x[1],-x[0])
def mul(x,y):
 v=[x[i]*y[j] for i in [0,1] for j in [0,1]]
 return (min(v)//S,-((-max(v))//S))
def absiv(x):
 return (0 if x[0]<=0<=x[1] else min(abs(x[0]),abs(x[1])),max(abs(x[0]),abs(x[1])))
def trig_iv(x,kind):
 # Taylor polynomial through degree160, remainder bounded by |x|^161/161!.
 terms=range(0,161,2) if kind=='cos' else range(1,161,2)
 val=sum(((-1)**(n//2))*x**n/Q(math.factorial(n)) for n in terms)
 rem=abs(x)**161/Q(math.factorial(161))
 return (fl((val-rem)*S),ce((val+rem)*S))
def exact_prefix(theta):
 c,s=trig_iv(theta,'cos'),trig_iv(theta,'sin')
 co,si=(S,S),(0,0); powr=(S,S); total=(0,0)
 for k in range(N):
  # a=(1/2,1/2), F=sum r^k |(co-si)/2|.
  proj=mul(add(co,neg(si)),(S//2,S//2))
  total=add(total,mul(powr,absiv(proj)))
  co,si=add(mul(co,c),neg(mul(si,s))),add(mul(si,c),mul(co,s))
  powr=mul(powr,rational_to_iv(r))
 return total
lo,hi=Q(11,20),Q(17,20)
allv=[exact_prefix(lo+(hi-lo)*Q(j,128)) for j in range(129)]
normlo=math.isqrt(S*S//2); normhi=normlo+1
c2=sum(Q(k*k)*r**k for k in range(N));tau=r**N/(1-r)
(OUT/'EXACT_RATIONAL_GRID_RAW.json').write_text(json.dumps({'scale':str(S),'N':N,'c2_numerator':str(c2.numerator),'c2_denominator':str(c2.denominator),'tail_numerator':str(tau.numerator),'tail_denominator':str(tau.denominator),'grid':[{'j':j,'theta':str(lo+(hi-lo)*Q(j,128)),'prefix_lower_integer':str(v[0]),'prefix_upper_integer':str(v[1])} for j,v in enumerate(allv)]},indent=2))
def dec(q,places=40,upper=False):
 t=ce(q*10**places) if upper else fl(q*10**places)
 sg='-' if t<0 else '';t=abs(t)
 return sg+str(t//10**places)+'.'+str(t%10**places).zfill(places)
cert=[]
for M in [8,16,32,64,128]:
 vals=allv[::128//M]; lower=Q(max(v[0] for v in vals),S); gridup=Q(max(v[1] for v in vals),S)
 h=(hi-lo)/M
 err2=Q(normhi,S)*(c2*h*h/8+tau);err1=Q(normhi,S)*(r/(1-r)**2*h/2+tau)
 upper=gridup+err2
 cert.append({'intervals':M,'prefix_lower':dec(lower),'prefix_upper':dec(gridup,upper=True),'robust_upper':dec(upper,upper=True),'second_order_error_upper':dec(err2,upper=True),'first_order_error_upper':dec(err1,upper=True),'prefix_interval_width_upper':dec(gridup-lower,places=80,upper=True),'capacity_at_threshold_1_lower':dec(1/upper),'capacity_at_threshold_1_upper':dec(1/lower,upper=True),'support_bracket_width_float':float(upper-lower),'ratio_first_to_second_error':float(err1/err2)})
(OUT/'EXACT_RATIONAL_PARAMETER_CERTIFICATE.json').write_text(json.dumps({'arithmetic':'Python exact integer/Fraction; Taylor Lagrange enclosures and outward fixed-point multiplication; decimal strings rounded outward','proof_scope':'supports the explicitly specified rational rotation family only; does not enclose network kernels','r':'17/20','theta_interval':['11/20','17/20'],'a':['1/2','1/2'],'N':N,'scale_digits':D,'base_trig_degree':160,'rows':cert,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))
print(json.dumps({'float_rows':len(rows),'all_dense_covered':all(x['dense_covered'] for x in rows),'certificate_finest':cert[-1],'seconds':time.perf_counter()-start},indent=2))
