"""Replay three equal-split 512-second startup witnesses on original WECC DAE."""
from pathlib import Path
import sys,json
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT));from run_transfer import SOURCE,QS
K=sparse.load_npz(SOURCE/'wecc_verified_descriptor_K.npz');d=np.load(SOURCE/'wecc_descriptor_aux.npz');M=sparse.diags(d['mass']);G=d['G'][:,[0,2]];omega=np.array([i for i,s in enumerate(d['x_names']) if s.startswith('omega GENROU ')]);w=np.load(ROOT/'wecc_witnesses.npz');contracts=['committed','dynamic_optional','independent_ports'];words=np.stack([w[c+'_input_MW_per_total_MW'][20] for c in contracts],axis=-1);checks=[]
for div in [64,128,256]:
 dt=1/div;L=splu((M-dt/2*K).tocsc());P=(M+dt/2*K).tocsc();z=np.zeros((len(d['mass']),3))
 for b in range(256,0,-1):
  for seg in QS:
   force=dt*G@(words[b]*seg[:,None])
   for step in range(div//2):z=L.solve(P@z+force)
 trial=[]
 for j,c in enumerate(contracts):
  o,p,_=w[c+'_argmax'][20];tau=float(w['phase_grid'][p]);zz=z[:,j].copy()
  for si,seg in enumerate(QS):
   duration=min(.5,max(0,tau-.5*si));nn=int(duration/dt);u=G@(words[0,:,j]*seg)
   for step in range(nn):zz=L.solve(P@zz+dt*u)
   rest=duration-nn*dt
   if rest>1e-12:zz=splu((M-rest/2*K).tocsc()).solve((M+rest/2*K)@zz+rest*u)
  actual=float(60*zz[omega[o]]);target=float(w[c+'_output'][20]);trial.append({'contract':c,'output_generator':int(o+1),'time_seconds':512+tau,'modal_witness_Hz_per_MW':target,'original_descriptor_Hz_per_MW':actual,'absolute_error_Hz_per_MW':abs(actual-target),'relative_error':abs(actual-target)/abs(target)})
 checks.append({'dt_seconds':dt,'witnesses':trial});print(checks[-1],flush=True)
result={'network':'wecc','method':'Full original verified 2405x2405 descriptor trapezoidal integration, all 256 carried-state past blocks plus current phase, three exact stored equal-split maximizing words; no electrical reset','checks':checks,'pass':max(z['relative_error'] for z in checks[-1]['witnesses'])<1e-3,'limitations':'Finite-time floating linear replay, grid refinement only, not interval or nonlinear proof.'};(ROOT/'wecc_original_descriptor_witness_replays.json').write_text(json.dumps(result,indent=2));print('PASS',result['pass'])
