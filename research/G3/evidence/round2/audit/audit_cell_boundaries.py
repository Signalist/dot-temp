from pathlib import Path
import sys,json,numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'theory'))
from exact_cell import *
rng=np.random.default_rng(2026100310);rows=[];worst=0;errors=[]
# Test command-domain corners, finite-reachability boundary curves, ramp/lag transition initial points.
for h in [.00005,.0005,.005,.025]:
 for ru,rd in [(30000,30000),(10000,70000),(90000,10000)]:
  p=Actuator(-450,450,.005,ru,rd)
  for b0 in sorted(set([-450.,450.,0.,max(-450,p.upper-p.tau*ru),min(450,p.lower+p.tau*rd)])):
   rr=reachability(b0,h,p)
   for b1 in [rr['b1_min'],rr['b1_max']]:
    try: a=cell_bounds(b0,b1,h,p)
    except Exception as e:errors.append({'h':h,'b0':b0,'b1':b1,'error':str(e)});continue
    local=0.
    for j in range(100):
     y0=float(rng.uniform(-450,450));yr=reachability(y0,h,p);y1=float(rng.uniform(yr['b1_min'],yr['b1_max']));b=cell_bounds(y0,y1,h,p)
     delta=np.array([y0-b0,y1-b1]);v=max(b['Imax']-a['Imax']-np.dot(a['grad_max'],delta),a['Imin']+np.dot(a['grad_min'],delta)-b['Imin'])
     local=max(local,v)
    worst=max(worst,local);rows.append({'h':h,'ru':ru,'rd':rd,'b0':b0,'b1':b1,'max_tangent_violation':local})
res={'boundary_anchors':len(rows),'tangent_checks':len(rows)*100*2,'max_global_tangent_violation':worst,'errors':errors,'cases':rows}
(ROOT/'audit/EXACT_CELL_BOUNDARY_AUDIT.json').write_text(json.dumps(res,indent=2));print({k:v for k,v in res.items() if k!='cases'})
