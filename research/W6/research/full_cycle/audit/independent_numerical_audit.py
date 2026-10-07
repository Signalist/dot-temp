"""Independent recomputation. Does not import any production model or integration function."""
import json, hashlib, math, time
from pathlib import Path
import numpy as np
import mpmath as mp
from scipy.integrate import quad
from scipy.optimize import brentq
mp.mp.dps=60
Q=lambda x:mp.mpf(str(x))
ROOT=Path(__file__).resolve().parents[1]

def moment(a,b,q):
 if a==b:return a**q,a**q/2
 I=(b**(q+1)-a**(q+1))/((q+1)*(b-a))
 I1=(b**(q+2)-a**(q+2))/((q+2)*(b-a))
 U=(I1-a*I)/(b-a)
 return I,U

def uniform_parts(case,z):
 b=Q(case['beta']);R=Q(case['R']);c=Q(case['c']);K=1+b;n=len(z)-1
 vals=[mp.mpf(0)]*4
 for i in range(n):
  a,d=Q(z[i]),Q(z[i+1]);dx=mp.mpf(1)/n;x=mp.mpf(i)/n
  for j,q in enumerate([(1-b)/K,-b/K,2/K,1/K]):
   I,U=moment(a,d,q)
   coef=K**q
   if j==2:coef/=2*R
   if j==3:coef/=R
   vals[j]+=coef*dx*((1-x)*I-dx*U if j<2 else I)
 E=vals[0]+vals[2];T=vals[1]+vals[3]
 return {"dynamic_energy":float(E),"task_time":float(vals[1]),"recovery_time":float(vals[3]),"cycle_time":float(T),"objective":float(E+c*T)}

def check_physical(case,path,atomic=False):
 beta=Q(case['beta']);R=Q(case['R']);c=Q(case['c']);K=1+beta
 dt=mp.mpf(0);energy=mp.mpf(0);work=mp.mpf(0)
 residual={'segment_time':0.,'segment_energy':0.,'physical_slew':0.,'power_continuity':0.}
 lastp=None
 for s in path['segments']:
  xa,xb=Q(s['x0']),Q(s['x1']);dx=xb-xa
  if atomic:
   za,zb=Q(s['z0']),Q(s['z1']);stored_dt=s['time'];pa,pb=(K*za)**(1/K),(K*zb)**(1/K)
  else:
   # Recover z from each stored physical power; independent physical linear-ramp integration.
   pa,pb=Q(s['p0']),Q(s['p1']);stored_dt=s['t1']-s['t0'];za,zb=pa**K/K,pb**K/K
  if pa==pb:
   dtime=dx/pa**beta;de=pa*dtime
  else:
   # Direct physical-time integration: useful work determines slope, not production power_int.
   v=(pb**K-pa**K)/(K*dx)
   dtime=(pb-pa)/v;de=(pb*pb-pa*pa)/(2*v)
  slew=(pb-pa)/dtime
  residual['segment_time']=max(residual['segment_time'],abs(float(dtime)-stored_dt))
  residual['segment_energy']=max(residual['segment_energy'],abs(float(de)-s['energy']))
  residual['physical_slew']=max(residual['physical_slew'],max(0,float(abs(slew)-R)))
  if lastp is not None:residual['power_continuity']=max(residual['power_continuity'],abs(float(pa-lastp)))
  lastp=pb;dt+=dtime;energy+=de;work+=dx
 pend=lastp;tail=pend/R;burn=pend**2/(2*R)
 recalced={'task_time':float(dt),'cycle_time':float(dt+tail),'dynamic_energy':float(energy+burn),'burn_energy':float(burn),'objective':float(energy+burn+c*(dt+tail))}
 residual['path_cost']=max(abs(path[k]-v) for k,v in recalced.items())
 residual['work']=abs(float(work)-path['W'])
 return residual,recalced

def independent_dual(row):
 c=row['case'];beta=c['beta'];R=c['R'];ct=c['c'];p0=c['p0'];K=1+beta
 z0=p0**K/K;zc=(beta*ct/(1-beta))**K/K
 xx=row['dual_x'];yy=row['dual_y'];value=-yy[0]*z0;err=0
 for i in range(len(xx)-1):
  lo,hi=xx[i],xx[i+1];slope=(yy[i+1]-yy[i])/(hi-lo)
  def fun(x):
   zzmax=min(z0+R*x,R*(1-x),max(zc,z0-R*x));pmax=(K*zzmax)**(1/K)
   zmin=max(0,z0-R*x);pmin=(K*zmin)**(1/K)
   S=1-x;f=1.
   # Derivative in power multiplied by p^(beta+1); independent from Fz implementation.
   def station(p):return S*((1-beta)*p-beta*ct)+f*(p+ct)*p**(beta+1)/R-slope*p**(2*beta+1)
   if station(pmax)<=0:p=pmax
   elif pmin>0 and station(pmin)>=0:p=pmin
   else:p=brentq(station,pmin,pmax,xtol=5e-15,rtol=1e-14)
   z=p**K/K;y=yy[i]+slope*(x-lo)
   F=S*(p+ct)/p**beta+(p*p/2+ct*p)/R
   return F-slope*z-R*abs(y)
  points=[]
  if yy[i]*yy[i+1]<0:points=[lo-yy[i]/slope]
  v,e=quad(fun,lo,hi,epsabs=2e-11,epsrel=2e-11,limit=150,points=points or None)
  value+=v;err+=e
 return value,err

files=['PRIMARY_MESHES.json','PHYSICAL_PATHS.json','CONTINUOUS_DUAL.json','ATOMIC_GLOBAL_BOUNDS.json','BASELINES.json','DOMINANCE_ABLATION.json']
rows=json.loads((ROOT/'results/PRIMARY_MESHES.json').read_text());out={"precision_digits":60,"scope":"Independent exact weighted-moment uniform objective, direct physical linear-ramp ledgers, and adaptive-quadrature power-coordinate dual; floating, not interval certificate.","primary":[],"physical":{},"atomic":[],"duals":[]}
for r in rows:
 p=uniform_parts(r['case'],r['z']);difference=max(abs(p[k]-r['parts'][k]) for k in p)
 z=np.array(r['z']);x=np.linspace(0,1,len(z));cc=r['case'];b=cc['beta'];R=cc['R'];ct=cc['c'];zc=(b*ct/(1-b))**(1+b)/(1+b)
 out['primary'].append({'case':cc,'N':r['N'],'max_component_difference':difference,'objective_recomputed':p['objective'],'slew_excess':float(max(0,np.max(abs(np.diff(z)))*(len(z)-1)-R)),'cone_excess':float(max(0,np.max(z-R*(1-x)))),'critical_excess':float(max(0,np.max(z-zc)))})
physical=json.loads((ROOT/'results/PHYSICAL_PATHS.json').read_text());maxres={};counts={'paths':0,'segments':0}
for row in physical:
 for p in row['paths']:
  residual,_=check_physical(row['case'],p)
  for k,v in residual.items():maxres[k]=max(maxres.get(k,0),v)
  counts['paths']+=1;counts['segments']+=len(p['segments'])
out['physical']={'counts':counts,'max_residuals':maxres}
for row in json.loads((ROOT/'results/ATOMIC_GLOBAL_BOUNDS.json').read_text()):
 res={};mean=0
 for p in row['physical']['paths']:
  r,cost=check_physical(row['case'],p,True)
  for k,v in r.items():res[k]=max(res.get(k,0),v)
  mean+=p['probability']*cost['objective']
 refs=row['refinements'];out['atomic'].append({'case':row['case'],'probabilities':row['probabilities'],'max_residuals':res,'objective_recomputed':mean,'upper_difference':abs(mean-refs[-1]['upper']),'lower_refinement_monotone':all(refs[i+1]['lower']>=refs[i]['lower']-1e-13 for i in range(len(refs)-1)),'upper_refinement_monotone':all(refs[i+1]['upper']<=refs[i]['upper']+1e-13 for i in range(len(refs)-1)),'relative_global_numeric_gap':refs[-1]['relative_gap']})
for row in json.loads((ROOT/'results/CONTINUOUS_DUAL.json').read_text()):
 v,e=independent_dual(row);out['duals'].append({'case':row['case'],'dual_recomputed':v,'saved_dual_difference':v-row['continuous_dual_numerical'],'quad_error_estimate':e,'independent_relative_gap':(row['primal_feasible_numerical']-v)/row['primal_feasible_numerical']})
# Re-evaluate independent Bellman comparators with high precision moments.
comp=[]
for row in json.loads((ROOT/'results/BASELINES.json').read_text()):
 for name in ['bellman_sub2','bellman_sub4']:
  r=row[name];p=uniform_parts(r['case'],r['z']);comp.append({'case':r['case'],'name':name,'objective_difference':p['objective']-r['objective']})
out['bellman_comparator_recomputation']=comp
out['source_sha256']={str((ROOT/'results'/f).relative_to(ROOT)):hashlib.sha256((ROOT/'results'/f).read_bytes()).hexdigest() for f in files}
out['source_sha256'].update({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'code').glob('*.py'))})
out['summary']={'max_primary_component_difference':max(r['max_component_difference'] for r in out['primary']),'max_dual_numeric_difference':max(abs(r['saved_dual_difference']) for r in out['duals']),'max_atomic_upper_difference':max(r['upper_difference'] for r in out['atomic']),'max_comparator_difference':max(abs(r['objective_difference']) for r in comp)}
(ROOT/'audit/INDEPENDENT_NUMERICAL_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out['summary'],indent=2));print(json.dumps(out['physical'],indent=2));print('Dual gap range',min(r['independent_relative_gap'] for r in out['duals']),max(r['independent_relative_gap'] for r in out['duals']))
