"""Independent physical-power quadrature for distribution transfer and repaired artifacts."""
import json,math,hashlib
from pathlib import Path
import numpy as np
import mpmath as mp
from scipy.integrate import quad
mp.mp.dps=60
Q=lambda x:mp.mpf(str(x))
ROOT=Path(__file__).resolve().parents[1]
def load(f):return json.loads((ROOT/'results'/f).read_text())
def parts(c,z,xnodes=None):
 b=c['beta'];R=c['R'];K=1+b;n=len(z)-1
 xx=np.linspace(0,1,n+1) if xnodes is None else np.asarray(xnodes)
 out=np.zeros(4);err=0.
 for i in range(n):
  a,d=Q(z[i]),Q(z[i+1]);dx=Q(xx[i+1])-Q(xx[i]);pa=(Q(K)*a)**(1/Q(K));pb=(Q(K)*d)**(1/Q(K));dp=pb-pa
  if a==d:dt=dx/pa**Q(b)
  else:dt=dx*dp/(d-a)
  pa,pb,dt=float(pa),float(pb),float(dt);dp=pb-pa;dx=float(dx)
  def evaluate(u,j):
   p=pa+dp*u
   if dp==0:frac=u;rem=1-xx[i]-dx*u
   elif pa==0:frac=u**K;rem=1-xx[i]-dx*frac
   elif pb==0:rem=1-xx[i+1]+dx*(1-u)**K
   else:
    frac=math.expm1(K*math.log1p(dp*u/pa))/math.expm1(K*math.log1p(dp/pa));rem=1-xx[i]-dx*frac
   rem=max(rem,1e-300)
   dist=c['dist']
   if dist=='uniform':S,f=rem,1.
   elif dist=='power':S,f=rem**c['alpha'],c['alpha']*rem**(c['alpha']-1)
   elif dist=='truncexp':
    rate=c['rate'];den=-math.expm1(-rate);S=math.exp(-rate)*math.expm1(rate*rem)/den;f=rate*math.exp(-rate*(1-rem))/den
   elif dist=='endatom':S,f=c['atom']+(1-c['atom'])*rem,1-c['atom']
   return dt*[S*p,S,f*p*p/(2*R)*p**b,f*p/R*p**b][j]
  for j in range(4):
   value,e=quad(lambda u:evaluate(u,j),0,1,epsabs=1e-12,epsrel=1e-12,limit=120);out[j]+=value;err+=e
 if c['dist']=='endatom':
  pend=((1+b)*z[-1])**(1/(1+b));out[2]+=c['atom']*pend**2/(2*R);out[3]+=c['atom']*pend/R
 E=out[0]+out[2];T=out[1]+out[3]
 return {'dynamic_energy':E,'task_time':out[1],'tail_time':out[3],'cycle_time':T,'objective':E+c['c']*T,'error_estimate':err}
def diff(a,b):return max(abs(a[k]-b[k]) for k in ['dynamic_energy','task_time','cycle_time','objective'])
def key(c):return tuple(c[k] for k in ['beta','R','c'])
primary=load('PRIMARY_MESHES.json');sources={key(r['case']):r for r in primary if r['N']==128}
out={'scope':'Independent quadrature in physical linear-power time, not production work-coordinate quadrature; no interval arithmetic.','transfer':[],'initial':[],'refinement':[],'accounting':[],'nonzero_bellman':[]}
for row in load('DISTRIBUTION_TRANSFER.json'):
 c=row['target_case'];src=parts(c,sources[key(c)]['z']);oracle=parts(c,row['target_oracle']['z']);kappa=(1+2*c['beta'])/(1+c['beta'])
 hazardmax=c['alpha'] if c['dist']=='power' else (c['rate']/(-math.expm1(-c['rate'])) if c['dist']=='truncexp' else 1-c['atom'])
 out['transfer'].append({'case':c,'source_component_difference':diff(src,row['source_uniform_parts']),'oracle_component_difference':diff(oracle,row['target_oracle']['precise_parts']),'recomputed_excess_fraction':src['objective']/oracle['objective']-1,'hazard_bound':hazardmax,'kappa':kappa,'within_convex_class':hazardmax<=kappa+1e-14})
for row in load('NONZERO_INITIAL.json'):
 c=row['case'];z=np.array(row['z']);n=len(z)-1;x=np.linspace(0,1,n+1);R=c['R'];b=c['beta'];ct=c['c'];z0=c['p0']**(1+b)/(1+b);zc=(b*ct/(1-b))**(1+b)/(1+b)
 p=parts(c,z);physical_excess=max(0,float(np.max(abs(np.diff(z)))*n-R));reserve=(c['p0']**2/2+ct*c['p0'])/R
 cap=np.maximum(zc,z0-R*x)
 record={'case':c,'label':row['label'],'component_difference':diff(p,row['precise_parts']),'slew_excess':physical_excess,'critical_envelope_excess':max(0,float(np.max(z-cap))),'initial_state_difference':abs(z[0]-z0),'objective_recomputed':p['objective'],'reserve_lower_bound':reserve}
 if row['label']=='prepaid_all':record['reserve_equality_difference']=abs(p['objective']-reserve)
 else:record['recovery_cone_excess']=max(0,float(np.max(z-R*(1-x))))
 out['initial'].append(record)
for row in load('REFINEMENTS_256.json'):
 p=parts(row['case'],row['z']);out['refinement'].append({'case':row['case'],'component_difference':diff(p,row['precise_parts']),'objective_recomputed':p['objective'],'128_to_256_improvement':sources[key(row['case'])]['parts']['objective']-p['objective']})
old=json.loads((ROOT/'prior/round2_saved_source_nodes.json').read_text())
for row in load('ACCOUNTING_ABLATION.json'):
 c=row['case'];r=next(r for r in old if r['N']==128 and r['beta']==c['beta'] and r['R']==c['R'] and r['lambda']==c['c']);z=np.array(r['z_nodes'])/(1+c['beta']);n=len(z)-1;x=np.linspace(0,1,n+1)
 # Independently locate the unique crossing by linear interpolation of z - recovery cone.
 d=z-c['R']*(1-x);newx=list(x)
 for i in range(n):
  if d[i]<0<d[i+1]:newx.append(x[i]+(x[i+1]-x[i])*(-d[i])/(d[i+1]-d[i]))
 newx=np.array(sorted(newx));newz=np.minimum(np.interp(newx,x,z),c['R']*(1-newx))
 original=parts(c,z);clipped=parts(c,newz,newx)
 out['accounting'].append({'case':c,'original_component_difference':diff(original,row['task_time_only_policy_full_cycle']),'exact_clip_component_difference':diff(clipped,row['same_policy_after_recovery_dominance']),'crossings_inserted':len(newx)-len(x),'objective_dominance_improvement':original['objective']-clipped['objective']})
for row in load('NONZERO_GLOBAL_COMPARISON.json'):
 if 'bellman' not in row:continue
 d=row['bellman'];p=parts(d['case'],d['z']);out['nonzero_bellman'].append({'case':d['case'],'label':row['label'],'recomputed_difference':p['objective']-d['objective']})
files=['DISTRIBUTION_TRANSFER.json','NONZERO_INITIAL.json','ACCOUNTING_ABLATION.json','REFINEMENTS_256.json','NONZERO_GLOBAL_COMPARISON.json']
out['source_sha256']={str((ROOT/'results'/f).relative_to(ROOT)):hashlib.sha256((ROOT/'results'/f).read_bytes()).hexdigest() for f in files}
out['source_sha256'].update({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'code').glob('*.py'))})
out['summary']={'max_transfer_component_difference':max(max(r['source_component_difference'],r['oracle_component_difference']) for r in out['transfer']),'max_initial_component_difference':max(r['component_difference'] for r in out['initial']),'max_refinement_component_difference':max(r['component_difference'] for r in out['refinement']),'max_accounting_component_difference':max(max(r['original_component_difference'],r['exact_clip_component_difference']) for r in out['accounting']),'max_nonzero_bellman_difference':max(abs(r['recomputed_difference']) for r in out['nonzero_bellman'])}
(ROOT/'audit/TRANSFER_REPAIR_INDEPENDENT_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['summary'],indent=2));print(out['initial'])
