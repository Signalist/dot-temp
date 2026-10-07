"""Outward feasible same-workload no-service comparator, no optimization claim."""
from pathlib import Path
import json
from certify_zoh_inner import iv,I,enc,v,Gp,R,L,Cdc,om,cc,kk,p0
ROOT=Path(__file__).resolve().parents[1]
d=iv.mpf(['350','950']);dd=iv.mpf(['-60000','60000'])
PL=2*d/(1+iv.sqrt(1-4*cc*d));Pdot=dd/iv.sqrt(1-4*cc*d)
i=PL/Gp;ip=Pdot/Gp;ed=v-R*i-L*ip;eq=-om*L*i
W=I('21.6')-kk*(PL*PL-p0*p0);M=1500*Cdc*(ed*ed+eq*eq)
res={'definition':'P_L=2d/(1+sqrt(1-4cd)),Q_L=0,b_L=u_L=0,B_L=B0,W_L=W0-k(P_L²-p0²); exact pointwise common d','bounds_over_all_piecewise_affine_workload_segments':{'W_kJ':enc(W),'modulation_floor_kJ':enc(M),'current_kA':enc(i),'W_minus_modulation_floor_kJ':enc(W-M)},'pass':bool(W.a>I('17.496').b and W.b<I('26.136').a and (W-M).a>0 and i.b<I('1.5').a),'endpoint_exact':'d(0)=d(T)=650 impliesP_L=p0,Q=0,W_L=W0,B_L=B0,b_L=0; continuous nominal continuation','scope':'Feasible explicit policy, not minimum-energy no-service optimizer; no service P/Q cap imposed on L'}
(ROOT/'results'/'outward_matched_baseline.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
