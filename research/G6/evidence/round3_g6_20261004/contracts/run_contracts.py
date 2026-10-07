"""Bounded mismatched-common-sign experiment, using only frozen old kernels.
Run: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 <andes_env>/bin/python run_contracts.py
No grid simulator is imported or executed, and no old file is modified.
"""
from pathlib import Path
import csv, ctypes, hashlib, json, os, subprocess, time
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','4')
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parents[1]/'round2_g6_joint_admission_20261003'
RAYS=np.array([[.5,.5],[.25,.75],[.75,.25]])
BS=[0,1,2,4,8];L=8;N=256;F=.05;T=2.;M=2048
QS=np.array([[1,1],[1,-1],[-1,-1],[-1,1]],int)
def savej(name,x): (ROOT/name).write_text(json.dumps(x,indent=2,allow_nan=False))
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def csvwrite(name,rows):
 with (ROOT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

# Reproducible local compilation of the source accompanying this experiment.
subprocess.run(['g++','-O3','-std=c++17','-fopenmp','-shared','-fPIC',str(ROOT/'window_dp.cpp'),'-o',str(ROOT/'window_dp.so')],check=True)
lib=ctypes.CDLL(str(ROOT/'window_dp.so'))
ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
lib.window_dp.argtypes=[ptr,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ptr]
def compiled_dp(d,B):
 d=np.ascontiguousarray(d,dtype=np.float64);shape=d.shape[:-1];flat=d.reshape(-1,d.shape[-1]);out=np.empty(len(flat))
 if B==0:out.fill(0.)
 elif B==L:out[:]=np.maximum(flat,0).sum(axis=1)
 else:lib.window_dp(flat,len(flat),flat.shape[1],L,B,out)
 return out.reshape(shape)

def independent_word_dp(d,B):
 """Separate dictionary forward-edge implementation, with explicit backpointers."""
 scores={0:0.};backs=[];mask=(1<<(L-1))-1
 for gain in d:
  nxt={};back={}
  for s,v in scores.items():
   for z in (0,1):
    if s.bit_count()+z>B:continue
    t=((s<<1)|z)&mask;value=v+z*gain
    if t not in nxt or value>nxt[t]:nxt[t]=value;back[t]=(s,z)
  scores=nxt;backs.append(back)
 state=max(scores,key=scores.get);value=scores[state];word=[]
 for back in reversed(backs):state,z=back[state];word.append(z)
 return value,np.array(word[::-1],dtype=np.int8)

def valid_word(word,B):
 # Padding defines startup/end, including histories shorter than L.
 return bool(np.convolve(np.pad(word,(L-1,L-1)),np.ones(L,dtype=int),mode='valid').max(initial=0)<=B)

def baseline_lp(d,B):
 n=len(d);rows=[]
 if n<L:rows=[np.ones(n)]
 else:
  for k in range(n-L+1):
   row=np.zeros(n);row[k:k+L]=1;rows.append(row)
 # The 0/1 window matrix has consecutive ones in every column and is TU.
 r=linprog(-d,A_ub=csr_matrix(np.array(rows)),b_ub=np.full(len(rows),B),bounds=(0,1),method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
 assert r.success,r.message
 rounded=np.rint(r.x).astype(int)
 return float(-r.fun),float(abs(r.x-rounded).max(initial=0)),bool(valid_word(rounded,B)),float(d@rounded)

# Independent enumeration with no transition state for small words.
rng=np.random.default_rng(64020261004)
validation={'random_seed':64020261004,'enumeration':[],'LP':[],'witnesses':[]}
n=12;words=((np.arange(1<<n)[:,None]>>np.arange(n))&1).astype(np.int8)
for B in BS:
 legal=np.max(np.stack([words[:,k:k+L].sum(axis=1) for k in range(n-L+1)]),axis=0)<=B
 for case in range(4):
  d=rng.normal(size=n);brute=float(np.max(words[legal]@d));dp=float(compiled_dp(d[None,:],B)[0]);py,word=independent_word_dp(d,B);lp,integ,valid,direct=baseline_lp(d,B)
  err=max(abs(dp-brute),abs(py-brute),abs(lp-brute),abs(d@word-brute));assert err<1e-9
  validation['enumeration'].append({'B':B,'case':case,'length':n,'legal_words':int(legal.sum()),'enumerated_words':1<<n,'max_gap':err,'LP_integrality_gap':integ})
# Exhaust all 2^(2n) port-sign pairs for n=5. Their relative sign is the
# mismatch bit; this checks the common-sign elimination independently.
n=5;signwords=2*((np.arange(1<<n)[:,None]>>np.arange(n))&1)-1
for B in BS:
 p=rng.normal(size=n);q=rng.normal(size=n);best=-np.inf
 for s1 in signwords:
  for s2 in signwords:
   if np.sum(s1!=s2)<=B:best=max(best,float(p@s1+q@s2))
 r0=abs(p+q);d=abs(p-q)-r0;actual=float(r0.sum()+compiled_dp(d[None,:],B)[0]);assert abs(actual-best)<1e-10
 validation['enumeration'].append({'B':B,'case':'full_two_port_signs','length':n,'enumerated_words':1<<(2*n),'max_gap':abs(actual-best)})
savej('VALIDATION_in_progress.json',validation)

rows=[];convergence=[];witnesses=[];schedules=[];ledgers=[];sources=[];all_arrays={};t0=time.time()
for name,sub in [('positive','positive_workpoint'),('wecc','transfer')]:
 src=OLD/sub;W=np.load(src/f'{name}_coefficients.npy',mmap_mode='r');supp=np.load(src/f'{name}_support_arrays.npz');bounds=np.load(src/f'{name}_bound_components.npz')
 assert W.shape[1]==M+1 and W.shape[-1]==N+1
 provenance={str(src/f'{name}_{s}'):sha(src/f'{name}_{s}') for s in ['coefficients.npy','kernel.npz','support_arrays.npz','bound_components.npz']}
 sources.append({'source':name,'hashes':provenance,'coefficient_shape':list(W.shape),'P0_MW':[50,50] if name=='positive' else [0,0]})
 for ri,a in enumerate(RAYS):
  oldri=int(round(a[0]*40));assert np.max(abs(supp['rays'][oldri]-a))<1e-14
  # Reuse the inherited *valid global derivative bound*, computed from the
  # finer derivative sampling plus analytic second derivatives. Any contract
  # with fixed signed amplitudes is bounded by this port-independent L.
  Lbound=float(supp['phase_error'][oldri]/(T/M/2));tail=float(np.max(bounds['tail']@a));assert abs(tail-float(supp['tail'][oldri]))<1e-20
  p=np.array(W[:,:,0,:])*a[0];q=np.array(W[:,:,1,:])*a[1]
  r0=abs(p+q);delta=abs(p-q)-r0;base=r0.sum(axis=-1)
  for B in BS:
   begin=time.time();support=base+compiled_dp(delta,B);all_arrays[f'{name}_ray{ri}_B{B}']=support
   o,phase=np.unravel_index(np.argmax(support),support.shape);peak=float(support[o,phase]);phaseerr=T/M/2*Lbound;error=tail+phaseerr;inner=F/(peak+error);outer=F/peak
   row={'source':name,'ray_index':ri,'a1':float(a[0]),'a2':float(a[1]),'L':L,'B':B,'N_past':N,'phase_intervals':M,'peak_lower_Hz_per_MW':peak,'peak_upper_Hz_per_MW':peak+error,'tail_bound_Hz_per_MW':tail,'Lipschitz_Hz_per_MW_s':Lbound,'phase_error_Hz_per_MW':phaseerr,'inner_amplitude_MW':inner,'outer_amplitude_MW':outer,'relative_support_bracket_width':error/peak,'output_index':int(o),'phase_seconds':float(phase*T/M),'physical_amplitude_cap_MW':float(min(50/a)) if name=='positive' else 0.,'wall_seconds':time.time()-begin}
   rows.append(row)
   for coarse in [256,512,1024,2048]:
    step=M//coarse;v=float(support[:,::step].max());e=tail+T/coarse/2*Lbound
    convergence.append({'source':name,'ray_index':ri,'B':B,'phase_intervals':coarse,'peak_lower_Hz_per_MW':v,'peak_upper_Hz_per_MW':v+e,'inner_amplitude_MW':F/(v+e),'outer_amplitude_MW':F/v})
   best,z=independent_word_dp(delta[o,phase],B);s=np.where(p[o,phase]+(1-2*z)*q[o,phase]>=0,1,-1);us=np.column_stack((s*a[0],s*(1-2*z)*a[1]));g=np.array(W[o,phase]).T;direct=float(np.sum(g*us));directreward=float(np.where(z,r0[o,phase]+delta[o,phase],r0[o,phase]).sum());assert valid_word(z,B)
   assert max(abs(direct-peak),abs(directreward-peak),abs(best+base[o,phase]-peak))<1e-12
   # Selected source rows, with scale normalization to avoid absolute LP
   # stopping tolerances overwhelming the smallest frequency coefficients.
   scale=float(abs(delta[o,phase]).max(initial=0)) or 1.;lp,integ,valid,lpround=baseline_lp(delta[o,phase]/scale,B);lp*=scale;lpround*=scale
   assert abs(lp-best)<1e-10 and integ<1e-6 and valid and abs(lp-lpround)<1e-10
   validation['LP'].append({'source':name,'ray_index':ri,'B':B,'same_information':True,'length':N+1,'dp_gain':best,'LP_gain':lp,'absolute_gap':abs(lp-best),'integrality_gap':integ,'rounded_word_valid':valid})
   validation['witnesses'].append({'source':name,'ray_index':ri,'B':B,'direct_sum_gap':abs(direct-peak),'valid_chronological_word':valid_word(z[::-1],B),'valid_reversed_word':valid_word(z,B)})
   wid=f'{name}_ray{ri}_B{B}';rho=1.02*outer;uchron=us[::-1]*rho;zchron=z[::-1];p0=np.array([50.,50.]) if name=='positive' else np.zeros(2)
   witnesses.append({'id':wid,'source':name,'ray_index':ri,'B':B,'L':L,'word_order':'chronological oldest through current; current block completed after probe','mismatch_chronological':zchron.tolist(),'common_sign_chronological':s[::-1].tolist(),'unit_total_amplitude_port_values_chronological':us[::-1].tolist(),'probe_output_index':int(o),'probe_phase_seconds':float(phase*T/M),'probe_time_from_forcing_start_seconds':N*T+phase*T/M,'direct_output_Hz_per_MW':direct,'DP_support_Hz_per_MW':peak,'exported_schedule_total_amplitude_MW':rho,'finite_linear_probe_output_Hz':rho*direct,'completed_blocks':N+1,'whole_word_seconds':(N+1)*T,'physical_P0_MW':p0.tolist(),'actual_compute_nonnegative':bool(np.all(p0-rho*a>=0)),'no_new_nonlinear_replay':True})
   for k,amp in enumerate(uchron):
    for j,qsegment in enumerate(QS):
     requested=amp*qsegment;actual=p0+requested
     schedules.append({'witness_id':wid,'block':k,'segment':j,'start_seconds':k*T+j*.5,'end_seconds':k*T+(j+1)*.5,'mismatch':int(zchron[k]),'deltaP1_MW':float(requested[0]),'deltaP2_MW':float(requested[1]),'P1_MW':float(actual[0]),'P2_MW':float(actual[1])})
    for i in range(2):
     integral=float(np.sum(amp[i]*QS[:,i])*.5);assert integral==0
     ledgers.append({'witness_id':wid,'block':k,'port':i+1,'seconds':T,'delta_energy_MW_s':integral,'total_energy_MW_s':float(T*p0[i]),'total_energy_MWh':float(T*p0[i]/3600),'affine_work_wbar_coefficient':T,'affine_work_kappa_coefficient':integral,'min_P_MW':float(p0[i]-rho*a[i]),'max_P_MW':float(p0[i]+rho*a[i]),'affine_nonnegative_work_condition':f'wbar_{i+1} >= abs(kappa_{i+1}) * {rho*a[i]:.17g}'})
   print(json.dumps({k:row[k] for k in ['source','ray_index','B','inner_amplitude_MW','outer_amplitude_MW','wall_seconds']}),flush=True)
  # Consistency with old endpoint contracts is a read-only reproduction.
  for B,key in [(0,'committed_peak'),(8,'independent_ports_peak')]:
   cur=next(r for r in rows if r['source']==name and r['ray_index']==ri and r['B']==B)
   gap=abs(cur['peak_lower_Hz_per_MW']-float(supp[key][oldri]));assert gap<1e-12
   validation.setdefault('inherited_endpoint_checks',[]).append({'source':name,'ray_index':ri,'B':B,'old_contract':key,'gap':gap})
  for i in range(1,len(BS)):
   assert np.min(all_arrays[f'{name}_ray{ri}_B{BS[i]}']-all_arrays[f'{name}_ray{ri}_B{BS[i-1]}'])>-1e-12
np.savez_compressed(ROOT/'all_phase_support_arrays.npz',rays=RAYS,phase_grid=np.linspace(0,T,M+1),**all_arrays)
# Same-information LP checks at independent, reproducibly selected grid rows.
for name,sub in [('positive','positive_workpoint'),('wecc','transfer')]:
 W=np.load(OLD/sub/f'{name}_coefficients.npy',mmap_mode='r')
 for ri,a in enumerate(RAYS):
  for B in [1,2,4]:
   for trial in range(3):
    o=int(rng.integers(W.shape[0]));phase=int(rng.integers(M+1));p=W[o,phase,0]*a[0];q=W[o,phase,1]*a[1];d=abs(p-q)-abs(p+q);dp=float(compiled_dp(d[None,:],B)[0]);scale=float(abs(d).max(initial=0)) or 1.;lp,integ,valid,direct=baseline_lp(d/scale,B);lp*=scale
    assert abs(lp-dp)<1e-10 and integ<1e-6 and valid
    validation['LP'].append({'source':name,'ray_index':ri,'B':B,'trial':trial,'output_index':o,'phase_index':phase,'length':N+1,'same_information':True,'dp_gain':dp,'LP_gain':lp,'absolute_gap':abs(lp-dp),'integrality_gap':integ,'rounded_word_valid':valid})
# Comparison uses separated amplitude brackets, not unqualified point ratios.
comparisons=[]
for name in ['positive','wecc']:
 for ri in range(3):
  rs=[r for r in rows if r['source']==name and r['ray_index']==ri];common=rs[0];independent=rs[-1]
  for r in rs:
   comparisons.append({'source':name,'ray_index':ri,'B':r['B'],'benefit_vs_independent_lower_fraction':r['inner_amplitude_MW']/independent['outer_amplitude_MW']-1,'benefit_vs_independent_upper_fraction':r['outer_amplitude_MW']/independent['inner_amplitude_MW']-1,'degradation_vs_perfect_common_lower_fraction':1-r['outer_amplitude_MW']/common['inner_amplitude_MW'],'degradation_vs_perfect_common_upper_fraction':1-r['inner_amplitude_MW']/common['outer_amplitude_MW'],'average_only_any_asymptotic_rate_outer_MW':independent['outer_amplitude_MW'],'average_only_any_asymptotic_rate_inner_MW':independent['inner_amplitude_MW']})
csvwrite('contract_amplitude_brackets.csv',rows);csvwrite('phase_convergence.csv',convergence);csvwrite('comparisons.csv',comparisons);csvwrite('maximizing_word_schedules.csv',schedules);csvwrite('per_block_energy_work_ledger.csv',ledgers)
savej('maximizing_words.json',witnesses);savej('SOURCE_PROVENANCE.json',sources);savej('VALIDATION.json',validation)
summary={'elapsed_seconds':time.time()-t0,'sources':sources,'brackets':rows,'comparisons':comparisons,'max_enumeration_gap':max(r['max_gap'] for r in validation['enumeration']),'max_LP_gap':max(r['absolute_gap'] for r in validation['LP']),'max_witness_direct_sum_gap':max(r['direct_sum_gap'] for r in validation['witnesses']),'LP_cases':len(validation['LP']),'enumeration_cases':len(validation['enumeration']),'all_30_words_pass_language_and_direct_sum':True,'total_complete_blocks_per_witness':N+1,'whole_word_duration_seconds':(N+1)*T,'whole_word_affine_work_wbar_coefficient_per_port':(N+1)*T,'whole_word_affine_work_kappa_coefficient_per_port':0,'positive_whole_word_energy_MWh_per_port':50*(N+1)*T/3600,'wecc_whole_word_energy_MWh_per_port':0,'new_nonlinear_integrations':0,'claims':'Fixed-amplitude contract only; all-phase and all-startup conditional LTI envelope using floating analytic bounds; no solver novelty, no interval proof, no physical WECC compute hosting'}
savej('SUMMARY.json',summary)
print('COMPLETE',json.dumps({k:summary[k] for k in ['elapsed_seconds','max_enumeration_gap','max_LP_gap','max_witness_direct_sum_gap','LP_cases']}),flush=True)
