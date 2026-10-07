"""Independent final review of repaired exact baselines, matched-time claims, empirical bridges."""
import csv,json,math,hashlib,collections
from pathlib import Path
import numpy as np
import mpmath as mp
from scipy.optimize import brentq
mp.mp.dps=60;Q=lambda x:mp.mpf(str(x))
ROOT=Path(__file__).resolve().parents[1]
def load(n):return json.loads((ROOT/'results'/n).read_text())
def uniform(c,p):
 p=Q(p);b=Q(c['beta']);R=Q(c['R']);ct=Q(c['c']);K=1+b;q=p**K/K
 # Reserve-integral formula independent of production early/middle/late expression.
 E=p*p/R-2*p**(b+3)/(R*R*K*(b+3))+(mp.mpf('.5')-q/R)*p**(1-b)
 T=2*p/R-2*p**(b+2)/(R*R*K*(b+2))+(mp.mpf('.5')-q/R)*p**(-b)
 tail=2*p**(b+2)/(R*R*(b+2))+(1-2*q/R)*p/R
 return {'dynamic_energy':float(E),'cycle_time':float(T),'recovery_time':float(tail),'task_time':float(T-tail),'objective':float(E+ct*T)}
out={'scope':'Independent final numeric audit. Exact model bounds are evaluated in ordinary floating arithmetic, never called outward-rounded certificates.','uniform_targets':[],'matched_time':[],'trace':[]}
for row in load('BASELINES.json'):
 c=row['case'];saved=row['constant_target_with_recovery'];p=saved['target'];v=uniform(c,p);b=c['beta'];R=c['R'];ct=c['c'];root=brentq(lambda p:(1-b)*p+2/R*p**(1+b)*(p+ct)-b*ct,0,b*ct/(1-b),xtol=1e-14)
 pstar=min(root,((1+b)*R/2)**(1/(1+b)))
 out['uniform_targets'].append({'case':c,'target_difference':p-pstar,'max_component_difference':max(abs(v[k]-saved['parts'][k]) for k in v),'relative_weighted_improvement':1-row['convex_objective']/v['objective']})
for row in load('MATCHED_CYCLE_FRONTIER.json'):
 c=row['case'];b=c['beta'];R=c['R'];pt=(b*R/2)**(1/(1+b));pmin=uniform(c,pt);v={'case':c,'minimum_time_difference':pmin['cycle_time']-row['constant_target_min_cycle_time'],'feasibility_flag_consistent':row['target_feasible_at_requested_cycle_time']==(row['proposed_cycle_time']>=pmin['cycle_time']-1e-10)}
 if row['target_feasible_at_requested_cycle_time']:
  m=uniform(c,row['matched_target_power']);v.update({'matched_time_difference':m['cycle_time']-row['proposed_cycle_time'],'energy_difference':m['dynamic_energy']-row['matched_target_dynamic_energy'],'energy_minimal_branch':row['matched_target_power']<=pt+1e-13,'relative_dynamic_energy_saving':1-row['proposed_dynamic_energy']/m['dynamic_energy'],'relative_allocated_energy_saving':1-row['proposed_allocated_facility_energy']/(m['dynamic_energy']+row['facility_idle_per_cycle']*m['cycle_time'])})
 out['matched_time'].append(v)
raw=list(csv.DictReader(open(ROOT/'literature/data_candidate/empirical_output_length_pmf.csv')));work=np.array([int(r['generated_tokens'])/1000 for r in raw]);counts=np.array([int(r['count']) for r in raw]);prob=counts/counts.sum()
out['empirical_pmf']={'atoms':len(work),'requests':int(counts.sum()),'strictly_increasing':bool(np.all(np.diff(work)>0)),'all_positive':bool(np.all(prob>0)),'max_work':float(work[-1]),'probability_sum':float(prob.sum()),'max_csv_probability_difference':float(max(abs(prob-np.array([float(r['probability']) for r in raw]))))}
raw_file=ROOT/'literature/data_candidate/AzureLLMInferenceTrace_conv.csv'
raw_rows=list(csv.DictReader(raw_file.open()))
observed=collections.Counter(int(r['GeneratedTokens']) for r in raw_rows)
out['empirical_pmf']['raw_csv_count_match']=observed=={int(r['generated_tokens']):int(r['count']) for r in raw}
out['empirical_pmf']['raw_csv_rows']=len(raw_rows)
out['empirical_pmf']['raw_csv_sha256']=hashlib.sha256(raw_file.read_bytes()).hexdigest()
def H(z,c):
 p=((1+c['beta'])*z)**(1/(1+c['beta']));return (p*p/2+c['c']*p)/c['R']
def independent_box_dp(c,n,boxes):
 b=c['beta'];R=c['R'];zc=(b*c['c']/(1-b))**(1+b)/(1+b);gcrit=((b*c['c']/(1-b))+c['c'])/(b*c['c']/(1-b))**b
 xs=np.r_[0.,work];caps=np.minimum(np.minimum(R*xs,R*(1-xs)),zc);vl=vh=np.array([0.]);cost=np.array([0.])
 for i in range(len(work)):
  vertices=np.linspace(0,caps[i+1],n+1) if caps[i+1]>0 else np.array([0.])
  if boxes and len(vertices)>1:bl,bh=vertices[:-1],vertices[1:]
  else:bl=bh=vertices
  dx=xs[i+1]-xs[i];a=np.minimum(vh[:,None],bh[None,:]+R*dx);d=np.minimum(bh[None,:],vh[:,None]+R*dx)
  peak=np.minimum((a+d+R*dx)/2,zc);plateau=np.maximum(0,dx-(2*peak-a-d)/R)
  bridge=2*H(peak,c)-H(a,c)-H(d,c)+plateau*gcrit
  valid=(vl[:,None]<=bh[None,:]+R*dx+1e-14)&(bl[None,:]<=vh[:,None]+R*dx+1e-14)
  S=prob[i:].sum();V=cost[:,None]+S*bridge+prob[i]*H(bl[None,:],c);cost=np.min(np.where(valid,V,np.inf),axis=0);vl,vh=bl,bh
 return float(cost[0])
for row in load('TRACE_DRIVEN_GLOBAL.json'):
 c=row['case'];b=Q(c['beta']);R=Q(c['R']);ct=Q(c['c']);K=1+b;segs=row['shared_bridge_segments'];cumulative_t=[];cumulative_e=[];ends=[];power=[];T=mp.mpf(0);E=mp.mpf(0);slewmax=mp.mpf(0);continuity=0.;lastx=0.;lastz=0.
 for xx0,xx1,aa,bb in segs:
  a=Q(aa);d=Q(bb);dx=Q(xx1)-Q(xx0);pa=(K*a)**(1/K);pb=(K*d)**(1/K)
  if a==d:dt=dx/pa**b;de=pa*dt
  else:v=(d-a)/dx;dt=(pb-pa)/v;de=(pb*pb-pa*pa)/(2*v);slewmax=max(slewmax,abs(v)-R)
  continuity=max(continuity,abs(xx0-lastx),abs(aa-lastz));lastx=xx1;lastz=bb;T+=dt;E+=de;ends.append(xx1);power.append(pb);cumulative_t.append(T);cumulative_e.append(E)
 ends=np.array(ends);pathmax=0.;means=[mp.mpf(0)]*3
 for W,pr,saved in zip(work,prob,row['physical']['paths']):
  j=int(np.argmin(abs(ends-W)));assert abs(ends[j]-W)<1e-12
  p=power[j];tt=cumulative_t[j];ee=cumulative_e[j];cycle=tt+p/R;dynamic=ee+p*p/(2*R);objective=dynamic+ct*cycle
  vals={'task_time':tt,'cycle_time':cycle,'dynamic_energy':dynamic,'burn_energy':p*p/(2*R),'objective':objective};pathmax=max(pathmax,max(abs(float(v)-saved[k]) for k,v in vals.items()));pr=Q(pr)
  means[0]+=pr*objective;means[1]+=pr*cycle;means[2]+=pr*dynamic
 # Recompute target cost via physical ramps for every possible W.
 target=Q(row['constant_target']['target']);q=target**K/K;a=q/R;targetcost=mp.mpf(0)
 for W,nc in zip(work,counts):
  w=Q(W)
  if w<=a:
   pend=(K*R*w)**(1/K);task=pend/R;energy=pend*pend/(2*R)
  elif w<1-a:
   pend=target;task=target/R+(w-a)/target**b;energy=target*target/(2*R)+(w-a)*target**(1-b)
  else:
   pend=(K*R*(1-w))**(1/K);task=(2*target-pend)/R+(1-2*a)/target**b;energy=(2*target*target-pend*pend)/(2*R)+(1-2*a)*target**(1-b)
  targetcost+=Q(int(nc))/Q(int(counts.sum()))*(energy+pend*pend/(2*R)+ct*(task+pend/R))
 low=independent_box_dp(c,128,True);hi=independent_box_dp(c,128,False);saved128=next(r for r in row['refinements'] if r['n']==128)
 out['trace'].append({'case':c,'paths':len(work),'shared_segments':len(segs),'max_physical_path_difference':pathmax,'raw_slew_excess':float(max(0,slewmax)),'max_shared_continuity_difference':continuity,'mean_objective_recomputed':float(means[0]),'upper_difference':float(means[0])-row['refinements'][-1]['upper'],'target_objective_recomputed':float(targetcost),'target_difference':float(targetcost)-row['constant_target']['objective'],'weighted_improvement_fraction':1-float(means[0]/targetcost),'independent_box128_lower_difference':low-saved128['lower'],'independent_grid128_upper_difference':hi-saved128['upper'],'refinement_lower_monotone':all(row['refinements'][i+1]['lower']>=row['refinements'][i]['lower']-1e-12 for i in range(len(row['refinements'])-1)),'refinement_upper_monotone':all(row['refinements'][i+1]['upper']<=row['refinements'][i]['upper']+1e-12 for i in range(len(row['refinements'])-1))})
files=['BASELINES.json','MATCHED_CYCLE_FRONTIER.json','TRACE_DRIVEN_GLOBAL.json']
out['source_sha256']={str((ROOT/'results'/f).relative_to(ROOT)):hashlib.sha256((ROOT/'results'/f).read_bytes()).hexdigest() for f in files}
out['source_sha256'].update({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'code').glob('*.py'))})
(ROOT/'audit/FINAL_BASELINE_TRACE_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['empirical_pmf'],indent=2));print(json.dumps(out['trace'],indent=2));print('uniform max',max(r['max_component_difference'] for r in out['uniform_targets']));print('matched flags',all(r['feasibility_flag_consistent'] for r in out['matched_time']))
