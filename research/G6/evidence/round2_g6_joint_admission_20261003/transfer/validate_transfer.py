"""Independent numerical checks: original Kundur state replay, small-word
exhaustion, refined modal tails, and direct formula agreement.
"""
from pathlib import Path
import json,itertools,sys
import numpy as np
from scipy.linalg import expm
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));from run_transfer import kernel_integral,QS,T,N,RAYS,FMAX

def main(name):
 k=np.load(ROOT/f'{name}_kernel.npz');lam=k['lam'];R=k['R'];q=np.load(ROOT/f'{name}_witnesses.npz');W=np.load(ROOT/f'{name}_coefficients.npy',mmap_mode='r');b=np.load(ROOT/f'{name}_bound_components.npz');s=np.load(ROOT/f'{name}_support_arrays.npz')
 out={'network':name,'checks':{}};word_errors=[];dynamic_errors=[];tails=[]
 for j in [0,10,20,30,40]:
  o,p,_=q['committed_argmax'][j];g=W[o,p].T;a=RAYS[j];w=g[:12]@a
  exact=max(np.dot(w,word) for word in itertools.product([-1,1],repeat=12));word_errors.append(abs(exact-abs(w).sum()))
  # All optional two-port per-block vertices, four blocks, brute force 7^4.
  choices=np.array([[0,0],[a[0],0],[0,a[1]],a,[-a[0],0],[0,-a[1]],-a]);terms=g[:4]@choices.T;best=max(sum(terms[i,c] for i,c in enumerate(word)) for word in itertools.product(range(7),repeat=4));x=g[:4,0]*a[0];y=g[:4,1]*a[1];formula=.5*(abs(x+y)+abs(x)+abs(y)).sum();dynamic_errors.append(abs(best-formula))
 for tau in np.linspace(0,T,17):
  tmpl=kernel_integral(lam,T);pows=np.exp(lam[:,None]*T*np.arange(N,2*N)[None,:]);hist=np.einsum('omi,mi,mn,m->oin',R,tmpl,pows,np.exp(lam*tau),optimize=True).real
  ratio=np.divide(abs(hist).sum(axis=-1),b['tail'],out=np.zeros_like(b['tail']),where=b['tail']>0);tails.append(float(ratio.max()))
 out['checks']['finite_common_sign_exhaustive_2power12_max_error']=float(max(word_errors));out['checks']['finite_dynamic_optional_exhaustive_7power4_max_error']=float(max(dynamic_errors));out['checks']['sampled_Nto2N_actual_tail_over_analytic_bound_max']=max(tails)
 if name=='kundur':
  A=k['A'];B=k['B'];C=k['C'];dim=len(A)
  # Augmented expm obtains exact ZOH without diagonalization or A inverse.
  aug=np.zeros((dim+2,dim+2));aug[:dim,:dim]=A;aug[:dim,dim:]=B
  step=expm(.5*aug);Phi=step[:dim,:dim];Gamma=step[:dim,dim:]
  replay=[];cached={}
  for contract in ['committed','dynamic_optional','independent_ports']:
   for j in range(41):
    o,p,_=q[contract+'_argmax'][j];tau=float(q['phase_grid'][p]);word=q[contract+'_input_MW_per_total_MW'][j];x=np.zeros(dim)
    for u in word[:0:-1]:
     for seg in QS:x=Phi@x+Gamma@(u*seg)
    for segidx in range(4):
     duration=min(.5,max(0,tau-.5*segidx))
     if duration<=0:continue
     if duration not in cached:
      em=expm(duration*aug);cached[duration]=(em[:dim,:dim],em[:dim,dim:])
     ph,ga=cached[duration];x=ph@x+ga@(word[0]*QS[segidx])
    y=float(C[o]@x);target=float(q[contract+'_output'][j]);replay.append({'contract':contract,'ray_index':j,'Hz_per_MW_state_replay':y,'Hz_per_MW_modal_witness':target,'absolute_error':abs(y-target),'relative_error':abs(y-target)/max(abs(target),1e-30)})
  out['checks']['original_state_expm_replay_max_abs_error']=max(x['absolute_error'] for x in replay);out['checks']['original_state_expm_replay_max_relative_error']=max(x['relative_error'] for x in replay)
  (ROOT/'kundur_original_state_replays.json').write_text(json.dumps(replay,indent=2))
 # Add labelled invalid-screen counterexample decisions, keeping primary results.
 import csv
 rows=list(csv.DictReader((ROOT/f'{name}_rays.csv').open()));old=json.loads((ROOT/f'{name}_decisions.json').read_text());base=[d for d in old if not d['comparison'].startswith('invalid_')]
 for j,row in enumerate(rows):
  for screen in ['reset','single_sign_periodic']:
   admitted=float(row[screen+'_capacity_lower_MW']);rejected=float(row['committed_capacity_upper_MW'])
   if admitted>rejected:
    amp=(admitted+rejected)/2;base.append({'ray_index':j,'comparison':'invalid_'+screen+'_screen','total_fluctuation_amplitude_MW':amp,'allocation_MW':(RAYS[j]*amp).tolist(),'screened_contract':screen,'screened_output_upper_Hz':amp*float(row[screen+'_peak_upper_Hz_per_MW']),'actual_contract':'committed','actual_finite_witness_Hz':amp*float(row['committed_peak_lower_Hz_per_MW']),'violation_above_005_Hz':amp*float(row['committed_peak_lower_Hz_per_MW'])-.05})
 (ROOT/f'{name}_decisions.json').write_text(json.dumps(base,indent=2));out['checks']['invalid_reset_decisions']=sum(d['comparison']=='invalid_reset_screen' for d in base);out['checks']['invalid_periodic_decisions']=sum(d['comparison']=='invalid_single_sign_periodic_screen' for d in base)
 out['pass']=bool(max(word_errors)<1e-12 and max(dynamic_errors)<1e-12 and max(tails)<=1+1e-10 and (name!='kundur' or out['checks']['original_state_expm_replay_max_relative_error']<1e-9));out['scope']='Floating arithmetic validation, no interval or nonlinear certificate. Exhaustive tests independently check finite support identities; tail ratio samples supplement the analytic bound, not replace it.'
 (ROOT/f'{name}_validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':
 for name in sys.argv[1:] or ['kundur','wecc']:main(name)
