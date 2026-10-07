from pathlib import Path
import json,itertools
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments'
cases=[('development',.85,.7),('holdout_low_memory',.6,.7),('holdout_high_memory',.95,.7),('holdout_rational',.85,np.pi/4),('holdout_irrational',.85,np.pi*(np.sqrt(5)-1)/2)]
rows=[];checks=[]
for name,r,theta in cases:
 k=np.arange(1024);v=r**k[:,None]*np.column_stack([np.cos(k*theta),-np.sin(k*theta)]);c=abs(v).sum(axis=0)
 for j,t in enumerate(np.linspace(0,1,41)):
  a=np.array([t,1-t]);w=v*a;fixed=abs(w.sum(axis=1)).sum();indep=abs(w).sum();dyn=np.maximum.reduce([abs(w[:,0]),abs(w[:,1]),abs(w.sum(axis=1))]).sum();static=max(fixed,*(c*a));tail=np.linalg.norm(a)*r**1024/(1-r)
  checks.append({'case':name,'ray':j,'identity_error':abs(dyn-(fixed+indep)/2)})
  rows.append({'case':name,'ray':j,'a':a.tolist(),'committed_support':float(fixed),'fixed_optional_support':float(static),'dynamic_optional_support':float(dyn),'independent_sign_support':float(indep),'tail_upper':float(tail),'dynamic_optional_total_amplitude_capacity':float(1/dyn),'coupling_information_capacity_gain_percent':float(100*(indep/dyn-1))})
 # Exhaustive hexagon-vertex sum at N=6, independently enumerated 6^6.
 a=np.array([.4,.6]);V=v[:6];verts=np.array([[a[0],a[1]],[a[0],0],[0,a[1]],[-a[0],-a[1]],[-a[0],0],[0,-a[1]]])
 brute=max(sum(V[k]@verts[s] for k,s in enumerate(ss)) for ss in itertools.product(range(6),repeat=6))
 exact=np.max(V@verts.T,axis=1).sum();checks.append({'case':name,'enumeration_N6_error':float(abs(brute-exact))})
(OUT/'DYNAMIC_OPTIONAL_RESULTS.json').write_text(json.dumps({'rows':rows,'checks':checks},indent=2));print(json.dumps({'max_identity_error':max(x.get('identity_error',0) for x in checks),'max_hexagon_enumeration_error':max(x.get('enumeration_N6_error',0) for x in checks),'equal_rays':[x for x in rows if x['ray']==20]},indent=2))
