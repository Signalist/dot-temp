#!/usr/bin/env python3
"""Reproducible synthetic workload-contract study. No measured traces or real hardware."""
import json, csv, hashlib, platform, sys, time
from pathlib import Path
from functools import lru_cache
from fractions import Fraction as F
import numpy as np
from scipy.optimize import linprog
import scipy
import sympy as sp
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'experiments';OUT.mkdir(exist_ok=True)
L,H=6.,18.

def dag_data(labels,edges):
 n=len(labels);pre=[0]*n
 for u,v in edges:pre[v]|=1<<u
 full=(1<<n)-1
 @lru_cache(None)
 def suffix(mask):
  if mask==full:return {()}
  result=set()
  for j in range(n):
   if not(mask>>j&1) and pre[j]&mask==pre[j]:
    result.update((labels[j],)+s for s in suffix(mask|1<<j))
  return result
 pats=sorted(suffix(0));sw=set();amin=[n+1]*(n+1);bmax=[-1]*(n+1)
 for mask in range(1<<n):
  if any((mask>>j&1) and pre[j]&mask!=pre[j] for j in range(n)):continue
  t=mask.bit_count();k=sum(labels[j] for j in range(n) if mask>>j&1);amin[t]=min(amin[t],k);bmax[t]=max(bmax[t],k)
  ready=[j for j in range(n) if not(mask>>j&1) and pre[j]&mask==pre[j]]
  if {labels[j] for j in ready}=={0,1}:sw.add(t)
 return pats,sorted(sw),amin,bmax

def matrices(pats,eta=.95,sw=None,ideal=False,finite=1):
 n=len(pats[0]);a=[];b=[];ae=[];be=[]
 # finite horizon uses independent public block vectors, lower/upper endpoint envelopes
 if finite!=1:return finite_matrices(pats,eta,finite)
 for pat in pats:
  aa=np.where(np.array(pat)==0,eta,1/eta);cc=np.where(np.array(pat)==0,-eta*L,-H/eta)
  for k in range(n+1):
   v=np.zeros(n+2);v[:k]=aa[:k];v[n]=1;a.append(-v);b.append(sum(cc[:k]));v=v.copy();v[-1]=-1;a.append(v);b.append(-sum(cc[:k]))
  if sw is None or pat==pats[0]:ae.append(np.r_[aa,0,0]);be.append(-sum(cc))
 if sw is not None:
  for t in sw:
   v=np.zeros(n+2);v[t]=1;v[t+1]=-1;ae.append(v);be.append(0)
 return np.r_[np.zeros(n+1),1],np.array(a),np.array(b),np.array(ae),np.array(be),[(L,H)]*n+[(0,None)]*2

def solve_model(model):
 c,a,b,ae,be,bounds=model
 return linprog(c,A_ub=a,b_ub=b,A_eq=ae if len(ae) else None,b_eq=be if len(be) else None,bounds=bounds,method='highs')

def finite_matrices(pats,eta,K):
 n=len(pats[0]); # vars p[K*n], lower[K+1],upper[K+1], B
 nn=K*n+2*(K+1)+1;lo=K*n;up=lo+K+1;ib=nn-1;a=[];b=[];ae=[];be=[]
 v=np.zeros(nn);v[lo]=1;v[up]=-1;ae.append(v);be.append(0)
 for block in range(K):
  for pat in pats:
   aa=np.where(np.array(pat)==0,eta,1/eta);cc=np.where(np.array(pat)==0,-eta*L,-H/eta)
   for t in range(n+1):
    v=np.zeros(nn);v[block*n:block*n+t]=-aa[:t];v[lo+block]=-1;a.append(v);b.append(sum(cc[:t]))
    v=np.zeros(nn);v[block*n:block*n+t]=aa[:t];v[up+block]=1;v[ib]=-1;a.append(v);b.append(-sum(cc[:t]))
   v=np.zeros(nn);v[lo+block+1]=1;v[lo+block]=-1;v[block*n:(block+1)*n]=-aa;a.append(v);b.append(sum(cc))
   v=np.zeros(nn);v[up+block+1]=-1;v[up+block]=1;v[block*n:(block+1)*n]=aa;a.append(v);b.append(-sum(cc))
 c=np.zeros(nn);c[ib]=1
 return c,np.array(a),np.array(b),np.array(ae),np.array(be),[(L,H)]*(K*n)+[(0,None)]*(2*(K+1)+1)

def leakage_matrices(pats,eta,rho):
 n=len(pats[0]);nn=n+3;lo=n;up=n+1;ib=n+2;a=[];b=[]
 v=np.zeros(nn);v[lo]=1;v[up]=-1;a.append(v);b.append(0)
 for pat in pats:
  aa=np.where(np.array(pat)==0,eta,1/eta);cc=np.where(np.array(pat)==0,-eta*L,-H/eta)
  for t in range(n+1):
   weights=rho**np.arange(t-1,-1,-1);v=np.zeros(nn);v[:t]=-weights*aa[:t];v[lo]=-rho**t;a.append(v);b.append(float(weights@cc[:t]))
   v=np.zeros(nn);v[:t]=weights*aa[:t];v[up]=rho**t;v[ib]=-1;a.append(v);b.append(float(-weights@cc[:t]))
  weights=rho**np.arange(n-1,-1,-1);v=np.zeros(nn);v[:n]=-weights*aa;v[lo]=1-rho**n;a.append(v);b.append(float(weights@cc))
  v=np.zeros(nn);v[:n]=weights*aa;v[up]=rho**n-1;a.append(v);b.append(float(-weights@cc))
 c=np.zeros(nn);c[ib]=1
 return c,np.array(a),np.array(b),np.zeros((0,nn)),np.array([]),[(L,H)]*n+[(0,None)]*3

def rational_check(model,r):
 c,a,b,ae,be,bounds=model
 conv=lambda x:F(float(x)).limit_denominator(10**7)
 x=list(map(conv,r.x));yy=list(map(conv,r.ineqlin.marginals));zz=list(map(conv,r.eqlin.marginals));ll=list(map(conv,r.lower.marginals));uu=list(map(conv,r.upper.marginals))
 aa=[[conv(t) for t in row] for row in a];bb=list(map(conv,b));ee=[[conv(t) for t in row] for row in ae];ff=list(map(conv,be));cc=list(map(conv,c))
 # Recover exact primal from the numerically selected active face.
 def exact_solution(rows,rhs,approx):
  if not rows:return approx
  syms=sp.symbols('z:'+str(len(approx)));sols=sp.linsolve((sp.Matrix(rows),sp.Matrix(rhs)),syms)
  if sols is sp.EmptySet or not sols:return approx
  vals=list(next(iter(sols)));free=set().union(*(v.free_symbols for v in vals));sub={z:sp.Rational(approx[i].numerator,approx[i].denominator) for i,z in enumerate(syms) if z in free}
  return [F(str(v.subs(sub))) for v in vals]
 active=ee.copy();rhs=ff.copy()
 for row,rr,afr in zip(a,b,aa):
  if abs(float(row@r.x-rr))<1e-7:active.append(afr);rhs.append(conv(rr))
 for j,(lb,ub) in enumerate(bounds):
  for bound in [lb,ub]:
   if bound is not None and abs(r.x[j]-bound)<1e-7:
    unit=[F(0)]*len(x);unit[j]=F(1);active.append(unit);rhs.append(conv(bound))
 x=exact_solution(active,rhs,x)
 # Recover exact dual on the solver's nonzero support; verify signs afterwards.
 cols=[];orig=[];loc=[]
 for kind,rows,mult in [('ineq',aa,yy),('eq',ee,zz)]:
  for i,y in enumerate(mult):
   if abs(float(y))>1e-9:cols.append(rows[i]);orig.append(y);loc.append((kind,i))
 for kind,mult in [('lower',ll),('upper',uu)]:
  for i,y in enumerate(mult):
   if abs(float(y))>1e-9:
    unit=[F(0)]*len(x);unit[i]=F(1);cols.append(unit);orig.append(y);loc.append((kind,i))
 dm=exact_solution(list(map(list,zip(*cols))),cc,orig)
 yy=[F(0)]*len(yy);zz=[F(0)]*len(zz);ll=[F(0)]*len(ll);uu=[F(0)]*len(uu)
 for (kind,i),v in zip(loc,dm):{'ineq':yy,'eq':zz,'lower':ll,'upper':uu}[kind][i]=v
 dot=lambda u,v:sum((s*t for s,t in zip(u,v)),F(0))
 primal=all(dot(row,x)<=rhs for row,rhs in zip(aa,bb)) and all(dot(row,x)==rhs for row,rhs in zip(ee,ff))
 primal &= all((lb is None or xx>=conv(lb)) and (ub is None or xx<=conv(ub)) for xx,(lb,ub) in zip(x,bounds))
 dual=all(y<=0 for y in yy) and all(y>=0 for y in ll) and all(y<=0 for y in uu)
 for j in range(len(x)):
  dual &= sum((row[j]*y for row,y in zip(aa,yy)),F(0))+sum((row[j]*y for row,y in zip(ee,zz)),F(0))+ll[j]+uu[j]==cc[j]
  if bounds[j][0] is None:dual &= ll[j]==0
  if bounds[j][1] is None:dual &= uu[j]==0
 pobj=dot(cc,x);dobj=dot(bb,yy)+dot(ff,zz)
 for j,(lb,ub) in enumerate(bounds):
  if lb is not None:dobj+=conv(lb)*ll[j]
  if ub is not None:dobj+=conv(ub)*uu[j]
 return {'exact_primal':bool(primal),'exact_dual':bool(dual),'exact_zero_gap':pobj==dobj,'capacity_fraction':str(pobj),'dual_fraction':str(dobj),'x_fraction':list(map(str,x)),'dual_nonzero':{kind:[[i,str(y)] for i,y in enumerate(mult) if y] for kind,mult in [('ineq',yy),('eq',zz),('lower',ll),('upper',uu)]}}

def record(name,labels,edges,eta=.95,split='worked'):
 pats,sw,amin,bmax=dag_data(labels,edges);t=time.time();m=matrices(pats,eta);r=solve_model(m);m2=matrices(pats,eta,sw=sw);r2=solve_model(m2)
 assert r.success and r2.success
 n=len(labels);k=sum(labels);q=(k*H+eta**2*(n-k)*L)/(k+eta**2*(n-k));c=eta*(q-L);h=(H-q)/eta
 gup=[c*t-(c+h)*amin[t] for t in range(n+1)];glo=[c*t-(c+h)*bmax[t] for t in range(n+1)];flat=max(gup)-min(glo)
 ideal=(H-L)*max(b-a for a,b in zip(amin,bmax));full=2*(n-k)*c
 return {'name':name,'split':split,'labels':labels,'edges':edges,'eta':eta,'word_count':len(pats),'swap_boundaries_zero_based':sw,'slot_graph_connected':len(sw)==n-1,'scenario_B':float(r.fun),'graph_B':float(r2.fun),'matched_difference':abs(r.fun-r2.fun),'full_permutation_B':full,'flat_DAG_B':flat,'ideal_B':ideal,'output':r.x[:n].tolist(),'initial':float(r.x[n]),'prefix_high_min':amin,'prefix_high_max':bmax,'exact_certificate':rational_check(m,r),'seconds':time.time()-t},pats,r

def main():
 rows=[]
 configs=[('antichain_6',[1,0,0,0,1,0],[]),('connected_restricted_6',[1,0,0,0,1,0],[(1,3),(2,5),(3,4),(4,5)]),('barriers_3plus3',[1,0,0,1,0,0],[(i,j) for i in range(3) for j in range(3,6)]),('heterogeneous_barriers',[1,0,0,0,1,1,0,0],[(i,j) for i in range(4) for j in range(4,8)]),('alternating_pipelines_8',[1,0,1,0,0,1,0,1],[(i,i+1) for i in [0,1,2,4,5,6]])]
 for name,labs,edges in configs:
  for eta in [.8,.95,.999]:rows.append(record(name,labs,edges,eta)[0])
 rng=np.random.default_rng(41004)
 for n in range(4,9):
  for j in range(12):
   labs=rng.integers(0,2,n).tolist()
   if sum(labs) in [0,n]:labs[0]=0;labs[-1]=1
   prob=[.1,.25,.5][j%3];edges=[(u,v) for u in range(n) for v in range(u+1,n) if rng.random()<prob]
   rows.append(record(f'random_n{n}_{j:02}',labs,edges,split='transfer_seeded')[0])
 for nstage in [3,4]:
  n=3*nstage;labs=[x for _ in range(nstage) for x in [1,0,0]];edges=[(i,j) for s in range(nstage-1) for i in range(3*s,3*s+3) for j in range(3*s+3,3*s+6)]
  rows.append(record(f'transfer_barriers_{nstage}',labs,edges,split='transfer_structure')[0])
 # Finite arbitrary block traces with no final recovery, illustrating convergence to T1 limit.
 horizons=[]
 for name,labs,edges in configs[:3]:
  pats,*_=dag_data(labs,edges)
  for K in [1,2,4,8,16,32,64]:
   r=solve_model(finite_matrices(pats,.95,K));assert r.success
   horizons.append({'name':name,'blocks':K,'capacity':float(r.fun),'infinite_capacity':next(z['scenario_B'] for z in rows if z['name']==name and z['eta']==.95)})
 # Loss plus self-discharge ablation, identical word family and output constraints.
 leaky=[]
 for name,labs,edges in configs[:3]:
  pats,*_=dag_data(labs,edges);n=len(labs)
  for rho in [.999,.99,.9]:
   r=solve_model(leakage_matrices(pats,.95,rho));assert r.success
   p=r.x[:n];res=[]
   for pat in pats:
    d=np.where(np.array(pat),H,L);inc=np.where(p>=d,.95*(p-d),(p-d)/.95);res.append(float((rho**np.arange(n-1,-1,-1))@inc))
   expected=(max(res)-min(res))/(1-rho**n)
   leaky.append({'name':name,'rho':rho,'B':float(r.fun),'output':p.tolist(),'spread':float(np.ptp(p)),'endpoint_width':float(r.x[n+1]-r.x[n]),'formula_width':expected,'interval':[float(r.x[n]),float(r.x[n+1])],'common_initial':float((r.x[n]+r.x[n+1])/2),'extra_PCC_energy_above_task':float(sum(p)-sum(np.where(np.array(labs),H,L)))})
 summary={'model':'synthetic normalized positive task powers L=6,H=18,delta=1; energy arbitrary consistent units','seed':41004,'dag_cases':len(rows),'matched_baseline_max_difference':max(z['matched_difference'] for z in rows),'all_exact_primal_dual_pass':all(z['exact_certificate']['exact_primal'] and z['exact_certificate']['exact_dual'] and z['exact_certificate']['exact_zero_gap'] for z in rows),'exact_primal_dual_pass_count':sum(z['exact_certificate']['exact_primal'] and z['exact_certificate']['exact_dual'] and z['exact_certificate']['exact_zero_gap'] for z in rows),'connected_cases':sum(z['slot_graph_connected'] for z in rows),'connected_formula_max_difference':max(abs(z['flat_DAG_B']-z['scenario_B']) for z in rows if z['slot_graph_connected']),'leakage_formula_max_difference':max(abs(z['endpoint_width']-z['formula_width']) for z in leaky),'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__}
 for fn,value in [('dag_results.json',rows),('finite_horizons.json',horizons),('leakage_results.json',leaky),('SUMMARY.json',summary)]: (OUT/fn).write_text(json.dumps(value,indent=2)+'\n')
 fields=['name','split','eta','word_count','slot_graph_connected','scenario_B','graph_B','matched_difference','full_permutation_B','flat_DAG_B','ideal_B']
 with (OUT/'dag_results.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
 print(json.dumps(summary,indent=2))
 for row in rows:
  if row['split']=='worked' and row['eta']==.95:print(row['name'],row['scenario_B'],row['exact_certificate'],row['output'])
 print('LEAKY',json.dumps(leaky,indent=2))
if __name__=='__main__':main()
