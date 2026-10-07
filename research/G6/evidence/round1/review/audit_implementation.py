"""Independent bounded implementation diagnostics; no production modifications.
These diagnostics complement mathematical review; passing random checks is not proof.
"""
from pathlib import Path
import hashlib, json, sys
import numpy as np
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import g6_model as g
mp.mp.dps=140
checks={}; rng=np.random.default_rng(613214)
checks['source_sha256']=hashlib.sha256((ROOT/'src/g6_model.py').read_bytes()).hexdigest()
checks['versions']={'numpy':np.__version__,'mpmath':mp.__version__}
S,C=g.exact_trig_grid()
quad_fails=[]; highprec_fails=[]
for r,h in enumerate([1,3,5]):
 for k in range(256):
  numer=h*k
  if numer%64==0:
   t=(numer//64)%4; sv=[0,1,0,-1][t]; cv=[1,0,-1,0][t]
   if not(S[0][r,k]<=sv<=S[1][r,k] and C[0][r,k]<=cv<=C[1][r,k]):quad_fails.append([h,k])
  else:
   v=2*mp.pi*h*k/256
   for name,iv,truth in [('sin',S,mp.sin(v)),('cos',C,mp.cos(v))]:
    if not mp.mpf(float(iv[0][r,k])) <= truth <= mp.mpf(float(iv[1][r,k])): highprec_fails.append([name,h,k])
checks['trig']={'quadrantal_failures':quad_fails,'nonquadrantal_highprec_failures':highprec_fails,'total_entries':1536}
models=[]
for cfg in g.MODELS:
 m=g.Model(cfg); rec={'name':cfg['name'],'transfer_entries_checked':0,'interval_transfer_failures':[],'max_direct_modal_abs_error':0.,'peak_bracket_failures':[],'max_halfwave_residual':0.}
 L=np.zeros((m.n,m.n))
 for i,j,w in m.edges:L[i,i]+=w;L[j,j]+=w;L[i,j]-=w;L[j,i]-=w
 rec['exact_laplacian_diagonalization']=bool(np.array_equal(L@m.sign,m.sign*m.lam))
 rec['nonzero_mode_min']=float(min(m.lam[1:]))
 for _ in range(20):
  f=float(rng.uniform(.08,.75)); k=float(rng.uniform(.85,1.15))
  for h in [1,3,5]:
   freq=float(h*f); rr,ii=m.transfer_interval(freq,freq,k,k); om=2*mp.pi*mp.mpf(freq); kap=mp.mpf(k)
   den=[kap*int(l)-mp.mpf(m.M)*om**2/(2*mp.pi)+1j*mp.mpf(m.D)*om/(2*mp.pi) for l in m.lam]
   for j in range(m.J):
    for i in range(2):
     val=sum(mp.mpf(float(m.res[j,r,i]))/den[r] for r in range(m.n))
     val*= -1j*om/(2*mp.pi)/mp.mpf('0.05') if j<m.n else -kap*int(m.kedge[j-m.n])/15
     rec['transfer_entries_checked']+=2
     for name,iv,v in [('real',rr,mp.re(val)),('imag',ii,mp.im(val))]:
      if not mp.mpf(float(iv[0][j,i])) <= v <= mp.mpf(float(iv[1][j,i])):rec['interval_transfer_failures'].append([f,k,h,j,i,name])
   w=2*np.pi*freq; A=k*L-m.M*w*w/(2*np.pi)*np.eye(m.n)+1j*m.D*w/(2*np.pi)*np.eye(m.n)
   theta=np.linalg.solve(A,-np.eye(m.n)[:,m.sources]); direct=np.concatenate([1j*w*theta/(2*np.pi)/.05,np.array([k*ww*(theta[a]-theta[b])/15 for a,b,ww in m.edges])]); modal=m.transfer(freq,k)
   rec['max_direct_modal_abs_error']=max(rec['max_direct_modal_abs_error'],float(np.max(np.abs(direct-modal))))
  low,upper=m.bounds([f,f,k,k]); peak,phase=m.peak_root(f,k)
  if np.any(peak<low[0]-1e-11) or np.any(peak>upper[0]+1e-11):rec['peak_bracket_failures'].append([f,k])
  H=np.array([m.transfer(h*f,k)/h for h in m.hs]);phi=float(rng.uniform(-np.pi,np.pi))
  q=lambda p: np.real(np.sum(-1j*H*np.exp(1j*m.hs[:,None,None]*p),axis=0))
  rec['max_halfwave_residual']=max(rec['max_halfwave_residual'],float(np.max(abs(q(phi)+q(phi+np.pi)))))
 models.append(rec)
checks['models']=models
checks['input_endpoints']={
 'root_covers_exact_decimal': bool(mp.mpf(float(g.down(.08)))<=mp.mpf('0.08') and mp.mpf(float(g.up(.75)))>=mp.mpf('0.75') and mp.mpf(float(g.down(.85)))<=mp.mpf('0.85') and mp.mpf(float(g.up(1.15)))>=mp.mpf('1.15')),
 'seed_lower_f_feasible':bool(mp.mpf(.08)>=mp.mpf('0.08')),
 'seed_k_low_feasible':bool(mp.mpf(float(g.up(.85)))>=mp.mpf('0.85')),
 'seed_k_high_feasible':bool(mp.mpf(float(g.down(1.15)))<=mp.mpf('1.15'))}
checks['source_changed_during_audit']=checks['source_sha256']!=hashlib.sha256((ROOT/'src/g6_model.py').read_bytes()).hexdigest()
(ROOT/'review/implementation_diagnostics.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
