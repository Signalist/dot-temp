from pathlib import Path
import json,numpy as np
from scipy.integrate import quad
from cycle_model import *
ROOT=Path(__file__).resolve().parents[1]
def precise(c,z,xnodes=None):
 N=len(z)-1;totals=np.zeros(4);errs=np.zeros(4)
 if xnodes is None:xnodes=np.linspace(0,1,N+1)
 for i in range(N):
  lo=xnodes[i];hi=xnodes[i+1]
  def fn(x,j):
   zz=z[i]+(z[i+1]-z[i])*(x-lo)/(hi-lo);p=c.P(max(zz,1e-300));S=c.S(x);f=c.f(x)
   return [S*p**(1-c.beta),S/p**c.beta,f*p*p/(2*c.R),f*p/c.R][j]
  for j in range(4):
   v,e=quad(lambda x:fn(x,j),lo,hi,epsabs=1e-11,epsrel=1e-11,limit=200);totals[j]+=v;errs[j]+=e
 if c.dist=='endatom':
  p=c.P(z[-1]);totals[2]+=c.atom*p*p/(2*c.R);totals[3]+=c.atom*p/c.R
 E=totals[0]+totals[2];T=totals[1]+totals[3]
 return {'dynamic_energy':E,'cycle_time':T,'task_time':totals[1],'tail_time':totals[3],'objective':E+c.c*T,'quad_error_estimate_sum':float(sum(errs))}
def exact_recovery_clip(c,z):
 N=len(z)-1;xx=[0.]
 for i in range(N):
  x0=i/N;x1=(i+1)/N;slope=(z[i+1]-z[i])*N
  if abs(slope+c.R)>1e-14:
   cross=(c.R-z[i]+slope*x0)/(slope+c.R)
   if x0+1e-14<cross<x1-1e-14:xx.append(cross)
  xx.append(x1)
 xx=np.array(xx);zz=np.minimum(np.interp(xx,np.linspace(0,1,N+1),z),c.R*(1-xx))
 return xx,zz
def run():
 primary=[r for r in json.load(open(ROOT/'results/PRIMARY_MESHES.json')) if r['N']==128];rows=[]
 for beta,R,cost in [(.5,4.,.25),(.5,.5,1.),(.8,4.,1.)]:
  source=next(r for r in primary if [r['case'][k] for k in ['beta','R','c']]==[beta,R,cost])
  for dist,kw in [('power',{'alpha':.5}),('power',{'alpha':(1+2*beta)/(1+beta)}),('truncexp',{'rate':.3}),('endatom',{'atom':.2})]:
   c=Case(beta,R,cost,dist=dist,**kw);oracle=solve(c,128,source['z']);oracle['precise_parts']=precise(c,oracle['z']);src=precise(c,source['z'])
   rows.append({'target_case':c.__dict__,'source_uniform_parts':src,'target_oracle':oracle,'source_excess_fraction':src['objective']/oracle['precise_parts']['objective']-1});(ROOT/'results/DISTRIBUTION_TRANSFER.json').write_text(json.dumps(rows,indent=2));print('transfer',c,rows[-1]['source_excess_fraction'],flush=True)
 # Historical saved policies: use primitive-scaled saved nodes, never old physical ledgers.
 old=json.load(open(ROOT/'prior/round2_saved_source_nodes.json'));abl=[]
 for r in primary:
  ca=Case(**r['case'])
  if ca.R!=4:continue
  v=next(v for v in old if v['N']==128 and v['beta']==ca.beta and v['R']==ca.R and v['lambda']==ca.c)
  z=np.array(v['z_nodes'])/(1+ca.beta);clipped=np.minimum(z,ca.R*(1-np.linspace(0,1,len(z))))
  a=precise(ca,z)
  xx,zz=exact_recovery_clip(ca,z);b=precise(ca,zz,xx)
  abl.append({'case':ca.__dict__,'source':'round2 saved work-state nodes, independent stable reevaluation; canonical erratum physical ledger retained','task_time_only_policy_full_cycle':a,'same_policy_after_recovery_dominance':b,'new_full_cycle_oracle':r['parts'],'old_objective_excess_fraction':a['objective']/r['parts']['objective']-1,'dominance_improvement_fraction':1-b['objective']/a['objective']})
 (ROOT/'results/ACCOUNTING_ABLATION.json').write_text(json.dumps(abl,indent=2))
 # Prefix boundaries grid aligned to avoid incorrectly linear-interpolating a convex high-state envelope.
 initial=[]
 for beta,R,cost in [(.5,.5,.25),(.8,4.,.25)]:
  ca=Case(beta,R,cost);crit=float(ca.A(ca.critical))
  for label,z0 in [('below_critical',crit/2),('forced_prefix',crit+R*.25),('prepaid_all',R*1.25)]:
   c=Case(beta,R,cost,p0=float(ca.P(z0)));r=solve(c,128);r['label']=label;r['precise_parts']=precise(c,r['z']);r['paths']=[reconstruct(c,r['z'],w) for w in [.1,.5,1.]];initial.append(r)
 (ROOT/'results/NONZERO_INITIAL.json').write_text(json.dumps(initial,indent=2))
 # Mesh refinement must not be counted as new independent models.
 refinements=[]
 for r in primary:
  c=Case(**r['case']);rr=solve(c,256,r['z']);rr['precise_parts']=precise(c,rr['z']);refinements.append(rr)
 (ROOT/'results/REFINEMENTS_256.json').write_text(json.dumps(refinements,indent=2))
if __name__=='__main__':run()
