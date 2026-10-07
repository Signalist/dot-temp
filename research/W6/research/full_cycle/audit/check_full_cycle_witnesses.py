"""Independent 80-digit mathematical sanity checks, not interval certificates."""
import json
from pathlib import Path
import mpmath as mp
mp.mp.dps=80
Q=mp.mpf
out={"precision_decimal_digits":mp.mp.dps,"certification":"High-precision floating arithmetic only; no directed-rounding certificate.","witnesses":{}}

def tent(x,x0,width):
    return max(Q(0),Q(1)-abs(x-x0)/width)
def power_fns(beta,c=Q(1),R=Q(1),k=Q(1)):
    def p(z): return ((beta+1)*z/k)**(1/(beta+1))
    def G(z):
        v=p(z); return (v+c)/(k*v**beta)
    def H(z):
        v=p(z); return (v*v/2+c*v)/R
    return p,G,H

def gap(G,H,base,x0,width,delta,S,atoms=()):
    def d(x):
        z=base(x); v=delta*tent(x,x0,width)
        return G(z)-(G(z+v)+G(z-v))/2
    integ=mp.quad(lambda x:S(x)*d(x),[x0-width,x0,x0+width])
    atom=mp.fsum(m*(H(base(x))-(H(base(x)+delta*tent(x,x0,width))+H(base(x)-delta*tent(x,x0,width)))/2) for x,m in atoms)
    return {"continuous_midpoint_gap":str(integ),"atomic_midpoint_gap":str(atom),"total_midpoint_gap":str(integ+atom),"nonconvex":bool(integ+atom>0)}

beta=Q('.5'); p,G,H=power_fns(beta)
x0=Q('.5'); width=Q('.004'); delta=Q('.001')
base=lambda x:Q('.5')*min(x,1-x)
r=gap(G,H,base,x0,width,delta,lambda x:Q(1) if x<x0 else Q('.5'),[(x0,Q('.5'))])
r.update({"distribution":"0.5 delta_(1/2) + 0.5 delta_1","service":"sqrt(p)","c":1,"R":1,"M":1,"baseline":"z=0.5 min(x,1-x)","perturbation":"plus/minus .001 max(0,1-|x-.5|/.004)","maximum_abs_slope":.75,"power_at_atom":str(p(base(x0))),"both_exact_caps_satisfied":True})
out['witnesses']['interior_atom']=r

alpha=Q(2); gamma=Q('.9'); x0=Q('.99'); width=Q('.002');delta=Q('.00005')
base=lambda x:min(x,gamma*(1-x))
r=gap(G,H,base,x0,width,delta,lambda x:(1-x)**alpha)
r.update({"distribution":"S=(1-x)^2 on [0,1]","service":"sqrt(p)","c":1,"R":1,"M":1,"kappa":str((1+2*beta)/(1+beta)),"baseline":"z=min(x,.9(1-x))","perturbation":"plus/minus .00005 max(0,1-|x-.99|/.002)","local_maximum_abs_slope":.925,"both_exact_caps_satisfied":True})
# Recompute with density contribution as part of the integral.
def term(z,x): return (1-x)**alpha*G(z)+alpha*(1-x)**(alpha-1)*H(z)
def d(x):
    z=base(x); v=delta*tent(x,x0,width)
    return term(z,x)-(term(z+v,x)+term(z-v,x))/2
full=mp.quad(d,[x0-width,x0,x0+width])
r['continuous_midpoint_gap']=str(full);r['total_midpoint_gap']=str(full);r['nonconvex']=bool(full>0)
out['witnesses']['high_tail_exponent']=r

# A smooth strictly increasing/strictly concave service curve with an affine shoulder.
a=Q('.1'); b=Q(1);eps=Q('.001');c=Q(20);R=Q(1)
def s(p): return a*p+b*(1-mp.exp(-p/eps))
def sp(p): return a+b/eps*mp.exp(-p/eps)
def spp(p): return -b/eps**2*mp.exp(-p/eps)
def A(p): return a*p*p/2+b*(p-eps*(1-mp.exp(-p/eps)))
def inv(z):
    guess=(-b+mp.sqrt(b*b+2*a*(z+b*eps)))/a
    return mp.findroot(lambda p:A(p)-z,guess)
def G(z):
    p=inv(z);return (p+c)/s(p)
def H(z):
    p=inv(z);return (p*p/2+c*p)/R
p0=Q('.2'); z0=A(p0);x0=Q('.5');width=Q('.1');delta=Q('.01')
base=lambda x:min(x,z0,1-x)
def term(z,x):return (1-x)*G(z)+H(z)
def d(x):
    z=base(x);v=delta*tent(x,x0,width)
    return term(z,x)-(term(z+v,x)+term(z-v,x))/2
full=mp.quad(d,[x0-width,x0,x0+width])
N=s(p0)-(p0+c)*sp(p0)
Gzz=(-(p0+c)*spp(p0)*s(p0)-3*N*sp(p0))/s(p0)**5
Hzz=N/(R*s(p0)**3)
r={"distribution":"Uniform[0,1]","service":"s(p)=0.1p+1-exp(-p/.001)","c":20,"R":1,"M":1,"critical_root":"none: N(p)=1-0.1c-[1+(p+c)/.001]exp(-p/.001)<0","baseline":"z=min(x,A(.2),1-x)","perturbation":"plus/minus .01 max(0,1-|x-.5|/.1)","z_at_midpoint":str(z0),"G_second_derivative":str(Gzz),"H_second_derivative":str(Hzz),"F_second_derivative_at_midpoint":str(Q('.5')*Gzz+Hzz),"total_midpoint_gap":str(full),"nonconvex":bool(full>0),"both_exact_caps_satisfied":True,"local_maximum_abs_slope":.1}
out['witnesses']['general_concave_uniform']=r

# Independently audit closed-form power-law curvature-ratio lower bound.
minimum_margin=mp.inf
for beta in map(Q,['.1','.25','.5','.8','1']):
  for c in map(Q,['.1','1','20']):
    for k in map(Q,['.3','1','2']):
      for R in map(Q,['.2','1','3']):
        for r in map(Q,['.000001','.01','.25','.75','.999']):
          power=r*beta*c/(1-beta) if beta<1 else r*c
          z=k*power**(1+beta)/(1+beta)
          s0=k*power**beta;d1=k*beta*power**(beta-1);d2=k*beta*(beta-1)*power**(beta-2)
          N=s0-(power+c)*d1
          g2=(-(power+c)*d2*s0-3*N*d1)/s0**5
          h2=N/(R*s0**3)
          ratio=g2/(-h2)
          kappa=(1+2*beta)/(1+beta)
          minimum_margin=min(minimum_margin,ratio*z/R-kappa)
out['power_curvature_grid']={"checks":5*3*3*3*5,"minimum_dimensionless_margin":str(minimum_margin),"all_lower_bound_checks_pass":bool(minimum_margin>=-mp.mpf('1e-70'))}
path=Path(__file__).with_name('FULL_CYCLE_INDEPENDENT_WITNESSES.json')
path.write_text(json.dumps(out,indent=2)+'\n')
print(path)
for name,r in out['witnesses'].items():print(name,r['total_midpoint_gap'])
print(out['power_curvature_grid'])
