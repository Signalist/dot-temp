"""Independent full-descriptor trapezoidal refinement for both block templates.
This is numerical evidence for the transfer, not nonlinear or interval proof.
The trapezoidal high-frequency parasitic modes are explicitly diagnosed by
refinement, and no ordinary finite-state descriptor reduction is used here.
"""
from pathlib import Path
import json,sys
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT));from run_transfer import SOURCE,kernel_integral,QS
K=sparse.load_npz(SOURCE/'wecc_verified_descriptor_K.npz');d=np.load(SOURCE/'wecc_descriptor_aux.npz');M=sparse.diags(d['mass']);G=d['G'][:,[0,2]];omega=np.array([i for i,s in enumerate(d['x_names']) if s.startswith('omega GENROU ')]);m=np.load(ROOT/'wecc_kernel.npz');lam=m['lam'];R=m['R'];checks=[]
for div in [64,128,256,512,1024]:
 dt=1/div;L=splu((M-dt/2*K).tocsc());P=(M+dt/2*K).tocsc();z=np.zeros((len(d['mass']),2));errs=[];peaks=[];last=[]
 for j in range(2*div):
  q=QS[min(int((j+.5)*dt/.5),3)];z=L.solve(P@z+dt*G*q[None,:]);t=(j+1)*dt
  y=z[omega]*60;truth=np.einsum('omi,mi->oi',R,kernel_integral(lam,t)).real;errs.append(float(abs(y-truth).max()));peaks.append(float(abs(truth).max()))
  if (j+1)%(div//4)==0:last.append({'t':t,'max_absolute_error_Hz_per_MW':errs[-1]})
 checks.append({'dt':dt,'maximum_absolute_error_Hz_per_MW':max(errs),'relative_peak_error':max(errs)/max(peaks),'quarter_second_checks':last});print(checks[-1],flush=True)
s={'method':'Original 2405x2405 descriptor trapezoidal evolution of each input template from zero, with midpoint constant forcing on each exact segment. Refinement assesses descriptor parasitic high-frequency effects and second-order time discretization.','checks':checks,'pass':checks[-1]['relative_peak_error']<1e-4 and checks[-1]['maximum_absolute_error_Hz_per_MW']<checks[0]['maximum_absolute_error_Hz_per_MW']/100,'note':'Finite-time floating linear qualification only; no nonlinear robustness or global interval guarantee.'}
(ROOT/'wecc_descriptor_time_validation.json').write_text(json.dumps(s,indent=2));print('PASS',s['pass'])
