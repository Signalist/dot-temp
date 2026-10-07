"""Portable replay from compact frozen kernels, with no simulator/network access.
Creates a disposable sibling layout in --scratch (must not exist), regenerates
coefficient tensors, runs the unchanged primary contract producer, and compares
all primary numeric brackets against the archived reference. About 300MB scratch.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','4')
from pathlib import Path
import argparse,shutil,json,hashlib,csv,subprocess,sys
import numpy as np
HERE=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--scratch',required=True);args=p.parse_args();scratch=Path(args.scratch).resolve()
if scratch.exists():raise SystemExit('Refusing existing scratch path; choose a new directory')
scratch.mkdir(parents=True)
old=scratch/'round2_g6_joint_admission_20261003';dst=scratch/'round3_g6_20261004'/'contracts';dst.mkdir(parents=True)
for name in ['run_contracts.py','window_dp.cpp']:shutil.copy2(HERE/'contracts'/name,dst/name)
T=2.;QS=np.array([[1,1],[1,-1],[-1,-1],[-1,1]],float);N=256;M=2048
def ki(lam,tau):
 out=np.zeros((len(lam),2),complex)
 for j,q in enumerate(QS):
  lo=j*T/4;hi=min((j+1)*T/4,tau)
  if hi<=lo:continue
  d=hi-lo;z=np.empty_like(lam);m=abs(lam)>1e-12;z[m]=np.expm1(lam[m]*d)/lam[m];z[~m]=d
  out+=(np.exp(lam*(tau-hi))*z)[:,None]*q
 return out
hashes=[]
for name,sub in [('positive','positive_workpoint'),('wecc','transfer')]:
 target=old/sub;target.mkdir(parents=True)
 for suffix in ['kernel.npz','bound_components.npz','support_arrays.npz']:
  src=HERE/'inputs'/sub/f'{name}_{suffix}';shutil.copy2(src,target/src.name)
  hashes.append({'fixture':str(src.relative_to(HERE)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
 k=np.load(target/f'{name}_kernel.npz');lam=k['lam'];R=k['R'];rb=R*ki(lam,T)[None,:,:];powers=np.exp(lam[:,None]*T*np.arange(N)[None,:]);phase=np.linspace(0,T,M+1)
 W=np.lib.format.open_memmap(target/f'{name}_coefficients.npy',mode='w+',dtype=np.float64,shape=(R.shape[0],M+1,2,N+1))
 for st in range(0,M+1,64):
  ts=phase[st:st+64];integ=np.stack([ki(lam,t) for t in ts]);expo=np.exp(ts[:,None]*lam[None,:]);cur=np.einsum('omi,pmi->opi',R,integ,optimize=True);hist=np.einsum('omi,pm,mn->opin',rb,expo,powers,optimize=True)
  W[:,st:st+len(ts)]=np.concatenate((cur.real[:,:,:,None],hist.real),axis=-1)
 W.flush();del W
with (scratch/'producer.log').open('w') as f:subprocess.run([sys.executable,str(dst/'run_contracts.py')],stdout=f,stderr=subprocess.STDOUT,check=True)
ref=list(csv.DictReader((HERE/'contracts/contract_amplitude_brackets.csv').open()));actual=list(csv.DictReader((dst/'contract_amplitude_brackets.csv').open()));assert len(ref)==len(actual)==30
columns=['peak_lower_Hz_per_MW','peak_upper_Hz_per_MW','inner_amplitude_MW','outer_amplitude_MW'];errs={k:max(abs(float(a[k])-float(b[k])) for a,b in zip(ref,actual)) for k in columns}
for k,e in errs.items():assert e<1e-9,(k,e)
result={'pass':True,'primary_rows_replayed':30,'maximum_absolute_differences':errs,'kernel_fixtures':hashes,'generated_scratch_bytes':sum(p.stat().st_size for p in scratch.rglob('*') if p.is_file()),'scope':'regenerated numerical kernels, ordinary double; no simulator, no old-source-model qualification or nonlinear rerun','scratch':str(scratch)}
(scratch/'REPLAY_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
