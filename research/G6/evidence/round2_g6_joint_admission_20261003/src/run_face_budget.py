"""Analytic-bound face budgets for the narrow structural theorem.

Ordinary floating evaluation of exact analytic bounds, not rounded proof.
Truncation, folding and greedy chord approximation are all classical methods.
The prospective contribution is a representation lower bound, not a solver.
"""
from pathlib import Path
import json,math,datetime
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments'
TMIN=.25;TMAX=4.;M=np.hypot(1,TMAX)
cases=[('golden_r085',.85,np.pi*(np.sqrt(5)-1)/2),('golden_r060',.6,np.pi*(np.sqrt(5)-1)/2),('golden_r095',.95,np.pi*(np.sqrt(5)-1)/2),('rational_pi4',.85,np.pi/4),('near_rational_diagnostic',.85,np.pi/7+np.sqrt(2)*1e-10)]
epss=10.**(-np.arange(2,11))
if not (ROOT/'protocol/FACE_BUDGET_FREEZE.json').exists():
 (ROOT/'protocol/FACE_BUDGET_FREEZE.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'slope_interval':[TMIN,TMAX],'absolute_gauge_tolerances':epss.tolist(),'cases':[{'name':n,'r':r,'theta_float':t} for n,r,t in cases],'near_rational':'post-theorem mechanism diagnostic, not a heldout and not proof of beta=infinity','comparators':['geometric-tail truncation','classical exact-knot greedy chord polygon','return folding with same angle information'],'novelty':'none asserted for algorithms'},indent=2))
rows=[]
for name,r,theta in cases:
 Nref=int(np.ceil(np.log(1e-14*(1-r)/M)/np.log(r)))
 k=np.arange(Nref);co=np.cos(k*theta);si=np.sin(k*theta);rw=r**k
 roots=co[np.abs(si)>1e-13]/si[np.abs(si)>1e-13]
 knots=np.unique(np.r_[TMIN,roots[(roots>TMIN)&(roots<TMAX)],TMAX])
 values=(rw[:,None]*abs(co[:,None]-si[:,None]*knots)).sum(axis=0)
 tailref=M*r**Nref/(1-r)
 for eps in epss:
  N=int(np.ceil(np.log(eps*(1-r)/M)/np.log(r)))
  ks=np.arange(N);s=np.sin(ks*theta);c=np.cos(ks*theta);rr=c[abs(s)>1e-13]/s[abs(s)>1e-13]
  truncpieces=1+len(np.unique(np.round(rr[(rr>TMIN)&(rr<TMAX)],13)))
  # A chord through true finite-series endpoints majorizes the convex finite
  # series. Its maximum error occurs at a kink, tested exhaustively here.
  seg=[(0,len(knots)-1)]
  while True:
   worst=(-1,None,None)
   for idx,(l,h) in enumerate(seg):
    xx=knots[l:h+1]
    yy=values[l]+(values[h]-values[l])*(xx-knots[l])/(knots[h]-knots[l])
    gap=yy-values[l:h+1];j=int(gap.argmax());g=float(gap[j])
    if g>worst[0]:worst=(g,idx,l+j)
   if worst[0]+tailref<=eps:break
   g,idx,j=worst;l,h=seg.pop(idx)
   assert l<j<h
   seg.extend([(l,j),(j,h)])
  # Search q only for comparable information; no unknown angle is snapped.
  folds=[]
  for q in range(1,min(N,2048)+1):
   delta=abs(q*theta-np.rint(q*theta/np.pi)*np.pi)
   err=M*delta*r**q/((1-r)*(1-r**q))
   if err<=eps:folds.append((q,err))
  rows.append({'case':name,'r':r,'theta_float':theta,'epsilon':float(eps),'truncation_terms':N,'truncation_pieces':truncpieces,'truncation_error_bound':M*r**N/(1-r),'adaptive_chord_pieces':len(seg),'chord_error_bound':worst[0]+tailref,'reference_terms':Nref,'reference_tail':tailref,'fold_exactness_scope':'rational pi/4 reduction is symbolic; numerical zero alone is not proof' if name=='rational_pi4' else 'ordinary floating return residual','best_found_fold_q':folds[0][0] if folds else None,'fold_error_bound':float(folds[0][1]) if folds else None})
(OUT/'FACE_BUDGET_RESULTS.json').write_text(json.dumps({'metric':'uniform absolute error of convex gauge F(1,t), t in [.25,4]; inverse gauges correspond to polygon radial error','rounding_scope':'analytic truncation/folding/chord error formulas evaluated with ordinary doubles','rows':rows},indent=2))
print(json.dumps([x for x in rows if x['epsilon'] in [1e-4,1e-8,1e-10]],indent=2))
