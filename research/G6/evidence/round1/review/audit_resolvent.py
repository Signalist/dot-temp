"""Independent fresh-seed nonzero-width tests of the resolvent enclosure.
Finite diagnostics only: no production edits, new optimizer, or safety inference.
"""
from pathlib import Path
import sys, json, hashlib
import numpy as np
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import g6_model as g
mp.mp.dps=140;rng=np.random.default_rng(6022027)
rec={'seed':6022027,'source_sha256':hashlib.sha256((ROOT/'src/g6_model.py').read_bytes()).hexdigest(),'models':[]}
for cfg in g.MODELS:
 m=g.Model(cfg); r={'name':cfg['name'],'box_harmonic_evaluations':0,'refinement_changed_enclosure':0,'empty_intervals':0,'scalar_components_checked':0,'containment_failures':[],'enlarged_vs_original':0,'max_width_ratio_refined_original':0.}
 for bid in range(20):
  fc=float(rng.uniform(.081,.749));kc=float(rng.uniform(.851,1.149));df=10.**rng.uniform(-5,-1.);dk=10.**rng.uniform(-5,-.65)
  box=[max(.08,fc-df),min(.75,fc+df),max(.85,kc-dk),min(1.15,kc+dk)]
  for h in [1,3,5]:
   a,b,c,d=box;a=float(g.down(h*a));b=float(g.up(h*b));r['box_harmonic_evaluations']+=1
   rr,ii=m.transfer_interval(a,b,c,d);ro,io=m.transfer_interval(a,b,c,d,_refine=False)
   if not all(np.array_equal(v,w) for v,w in zip(rr+ii,ro+io)):r['refinement_changed_enclosure']+=1
   for new,old in [(rr,ro),(ii,io)]:
    r['empty_intervals']+=int(np.count_nonzero(new[0]>new[1]));r['enlarged_vs_original']+=int(np.count_nonzero((new[0]<old[0])|(new[1]>old[1])))
    ow=old[1]-old[0];nw=new[1]-new[0];r['max_width_ratio_refined_original']=max(r['max_width_ratio_refined_original'],float(np.max(nw/ow)))
   pts=[(a,c),(a,d),(b,c),(b,d),((a+b)/2,(c+d)/2)]
   for f,k in pts:
    om=2*mp.pi*mp.mpf(f);kap=mp.mpf(k)
    den=[kap*int(l)-mp.mpf(m.M)*om**2/(2*mp.pi)+1j*mp.mpf(m.D)*om/(2*mp.pi) for l in m.lam]
    for j in range(m.J):
     for i in range(2):
      val=sum(mp.mpf(float(m.res[j,t,i]))/den[t] for t in range(m.n))
      val*= -1j*om/(2*mp.pi)/mp.mpf('0.05') if j<m.n else -kap*int(m.kedge[j-m.n])/15
      for name,iv,v in [('real',rr,mp.re(val)),('imag',ii,mp.im(val))]:
       r['scalar_components_checked']+=1
       if not mp.mpf(float(iv[0][j,i]))<=v<=mp.mpf(float(iv[1][j,i])):r['containment_failures'].append([bid,h,f,k,j,i,name])
 rec['models'].append(r)
rec['source_changed_during_audit']=rec['source_sha256']!=hashlib.sha256((ROOT/'src/g6_model.py').read_bytes()).hexdigest()
(ROOT/'review/resolvent_diagnostics.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec,indent=2))
