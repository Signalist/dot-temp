from pathlib import Path
import hashlib,json,numpy as np
from scipy.linalg import eig,expm
P=Path('outputs/round2_20261003/grid_transfer/kundur_reduced51.npz');x=np.load(P);A=x['A'];B=x['B'][:,[0,2]];C=x['C_frequency_Hz'];lam,V=eig(A);Vi=np.linalg.inv(V);t=np.linspace(0,48,9601)
R=np.einsum('ik,kj->ikj',C@V,Vi@B);h=np.real(np.einsum('tk,ikj->tij',np.exp(t[:,None]*lam),R));hp=np.real(np.einsum('tk,ikj->tij',np.exp(t[:,None]*lam),R*lam[None,:,None]));M=[(C@np.linalg.matrix_power(A,k)@B).tolist() for k in range(4)];rows=[]
for i in range(4):
 a=h[:,i,0];b=h[:,i,1];coef=max(0.,-float(a@b)/(b@b));res=np.linalg.norm(a+coef*b)/np.linalg.norm(a)
 changes=[]
 for j in range(2):
  z=hp[:,i,j];ii=np.flatnonzero(z[:-1]*z[1:]<0);changes.append(dict(port=str(x['input_names'][[0,2][j]]),min=float(z.min()),max=float(z.max()),sign_changes=int(len(ii)),first_brackets=[[float(t[k]),float(t[k+1])] for k in ii[:6]]))
 rows.append(dict(generator=int(x['generator_ids'][i]),h0=M[0][i],relative_degree_four_hypothesis=False,opposite_positive_scale=coef,opposite_fit_relative_L2=float(res),kernel_correlation=float(a@b/(np.linalg.norm(a)*np.linalg.norm(b))),derivative_signs=changes))
checks=[]
for tau in [0,.015,.7,1.,4.,16.,48.]:
 exact=C@expm(A*tau)@B;modal=np.real(np.einsum('k,ikj->ij',np.exp(lam*tau),R));checks.append(dict(tau=tau,max_error=float(abs(exact-modal).max())))
assert max(r['max_error'] for r in checks)<1e-10
out=dict(status='passed',source=str(P),source_sha256=hashlib.sha256(P.read_bytes()).hexdigest(),ports=x['input_names'][[0,2]].tolist(),Markov_coefficients=M,rows=rows,expm_checks=checks,scope='Qualifying structural nontransfer evidence only; sampled signs are not interval certificates. Existing model inputs unchanged.')
O=Path(__file__).resolve().parent;(O/'network_structure_results.json').write_text(json.dumps(out,indent=2));np.savez_compressed(O/'network_structure_kernels.npz',t=t,h=h,hp=hp);print(json.dumps(out,indent=2))
