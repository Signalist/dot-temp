"""Frozen, read-only benchmark inputs -> synthetic source-identifiability audits.
No ANDES imports and no existing adapter/cache modifications are needed.
"""
from pathlib import Path
import json,hashlib,datetime,csv
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
from scipy.linalg import solve,expm,svdvals,orth,subspace_angles
from scipy.signal import lsim
D=Path(__file__).resolve().parent
P=json.loads((D/'PROTOCOL_FREEZE.json').read_text())
S=D.parents[2]/'round2_20261003'/'grid_transfer'
assert hashlib.sha256((D/'PROTOCOL_FREEZE.json').read_bytes()).hexdigest()==(D/'PROTOCOL_FREEZE.sha256').read_text().split()[0]
for f,h in P['input_sha256'].items():assert hashlib.sha256((S/f).read_bytes()).hexdigest()==h,f
freq=np.array(P['frequencies_Hz'])
sets={'V_first':[0],'F_first':[2],'V_pair':[0,1],'F_pair':[2,3],'V_first_F_first':[0,2]}
scales=np.array([P['noise']['voltage_scale_pu']]*2+[P['noise']['frequency_scale_Hz']]*2)
k=np.load(S/'kundur_reduced51.npz',allow_pickle=False)
A=k['A'];B=k['B'];C=np.vstack([k['C_voltage_pu'][[6,7]],k['C_frequency_Hz'][[0,3]]]);Du=np.vstack([k['D_voltage_pu'][[6,7]],np.zeros((2,4))])

def realvec(z):return np.r_[np.real(z),np.imag(z)]
def finite(x):return float(x) if np.isfinite(x) else None

def cm(h):
 n=np.linalg.norm(h,axis=0)
 if min(n)<=1e-15:return {'degenerate_zero_column':True,'norms_per_MW':n.tolist()}
 U=h/n
 rho=min(1.,abs(np.vdot(U[:,0],U[:,1])))
 # Orthogonal residual avoids catastrophic cancellation in sqrt(1-rho^2).
 r0=h[:,0]-h[:,1]*(np.vdot(h[:,1],h[:,0])/n[1]**2)
 r1=h[:,1]-h[:,0]*(np.vdot(h[:,0],h[:,1])/n[0]**2)
 d=np.array([np.linalg.norm(r0),np.linalg.norm(r1)])
 ss=svdvals(U)
 sin=float(d[0]/n[0]);condition=float(ss[0]/ss[-1]) if len(ss)>1 and ss[-1]>1e-14 else np.inf
 return {'degenerate_zero_column':False,'norms_per_MW':n.tolist(),'correlation':float(rho),'sin_principal_angle':sin,'normalized_column_condition':finite(condition),'residual_per_MW':d.tolist(),'critical_amplitude_MW':[float(2/x) if x>1e-12 else None for x in d],'complex_alias_source2_over_source1':[float((np.vdot(h[:,1],h[:,0])/n[1]**2).real),float((np.vdot(h[:,1],h[:,0])/n[1]**2).imag)],'residual_is_numerically_zero':bool(max(d)<1e-12)}

raw={};rows=[];solve_audits=[];nuisance=[];causal=[];causal_raw={}
for case in ['kundur','wecc']:
 aux=np.load(S/(case+'_descriptor_aux.npz'),allow_pickle=False)
 K=sparse.load_npz(S/(case+('_verified' if case=='wecc' else '')+'_descriptor_K.npz')).astype(complex)
 mass=aux['mass'];G=aux['G'];nx=len(aux['x0'])
 vn=aux['y_names'].tolist();xn=aux['x_names'].tolist()
 cfg=P['models'][case]
 idx=[nx+vn.index('v Bus '+str(b)) for b in cfg['voltage_buses']]+[xn.index('omega GENROU '+str(g)) for g in cfg['frequency_generator_ids']]
 fac=np.array([1,1,60,60]);Hs=[]
 for f in freq:
  w=2*np.pi*f;J=1j*w*sparse.diags(mass)-K;lu=splu(J.tocsc());Z=lu.solve(G)
  res=G-J@Z;cor=lu.solve(res);Zr=Z+cor
  rscale=1/np.maximum(abs(J).max(axis=1).toarray().ravel(),1e-30)
  Jr=sparse.diags(rscale)@J
  cscale=1/np.maximum(abs(Jr).max(axis=0).toarray().ravel(),1e-30)
  Je=(Jr@sparse.diags(cscale)).tocsc();Ze=cscale[:,None]*splu(Je).solve(rscale[:,None]*G)
  Hd=fac[:,None]*Zr[idx];He=fac[:,None]*Ze[idx]
  bwd=float(np.linalg.norm(G-J@Zr)/(np.linalg.norm(G)+sparse.linalg.norm(J)*np.linalg.norm(Zr)))
  sensitivity=float(np.linalg.norm(Hd-He)/max(np.linalg.norm(Hd),1e-30))
  rec={'case':case,'frequency_Hz':float(f),'descriptor_backward_relative_residual':bwd,'relative_output_refinement':float(np.linalg.norm(fac[:,None]*cor[idx])/max(np.linalg.norm(Hd),1e-30)),'relative_output_equilibration_difference':sensitivity}
  if case=='kundur':
   ZZ=solve(1j*w*np.eye(len(A))-A,B)
   H=C@ZZ+Du
   rec['reduced_descriptor_output_relative_difference']=float(np.linalg.norm(H-Hd)/np.linalg.norm(H))
   T=20/f
   Jint=solve(A-1j*w*np.eye(len(A)),expm(A*T)-np.eye(len(A)))
   Mcos=H-2/T*C@Jint@ZZ.real
   Msin=-1j*H-2/T*C@Jint@ZZ.imag
   causal_raw[str(f)]={'M_cos':Mcos,'M_sin':Msin}
  else:H=Hd
  rec['numerical_warning']=bool(bwd>1e-9 or sensitivity>1e-7 or rec['relative_output_refinement']>1e-7)
  solve_audits.append(rec);Hs.append(H)
  for name,si in sets.items():
   W=H[si]/scales[si,None]
   metric=cm(W[:,[0,2]])
   rows.append({'case':case,'frequency_Hz':float(f),'sensors':name,'channel_count':len(si),**metric})
   Rp=[W[:,[0,1]],W[:,[2,3]]]
   nuisance.append({'case':case,'frequency_Hz':float(f),'sensors':name,'complex_channel_count':len(si),'PQ_complex_ranks':[int(np.linalg.matrix_rank(r)) for r in Rp],'PQ_block_singular_values':[svdvals(r).tolist() for r in Rp],'both_fill_observation_space':bool(all(np.linalg.matrix_rank(r)==len(si) for r in Rp))})
   if case=='kundur':
    F=[np.column_stack([realvec(Mcos[si,j]/scales[si]),realvec(Msin[si,j]/scales[si])]) for j in [0,2]]
    Q=[orth(g) for g in F];residual=[];crit=[]
    for j in range(2):
     R=F[j]-Q[1-j]@(Q[1-j].T@F[j]);ss=svdvals(R);v=float(min(ss));residual.append(v);crit.append(float(2/v) if v>1e-10 else None)
    b2=np.linalg.lstsq(F[1],F[0][:,0],rcond=None)[0]
    ckey=f'causal_{f}_{name}';causal_raw[ckey]=np.stack(F)
    causal.append({'case':case,'frequency_Hz':float(f),'sensors':name,'horizon_s':float(T),'zero_initial_state':True,'real_source_subspace_ranks':[q.shape[1] for q in Q],'principal_angles_degrees':np.degrees(subspace_angles(*Q)).tolist(),'worst_phase_residual_per_MW':residual,'critical_worst_phase_amplitude_MW':crit,'source2_cos_sin_matching_source1_cos':b2.tolist(),'source1_cos_alias_residual':float(np.linalg.norm(F[0][:,0]-F[1]@b2))})
 raw[case+'_H_voltage_frequency_per_MW_Mvar']=np.array(Hs)

# Exact commutation example with two causal SISO filters at the same voltage sensor.
# Each world uses the same grid A,C and zero initial state, but a different port.
# u1=g2*v, u2=g1*v => y1=g1*g2*v=y2=g2*g1*v by causal LTI convolution commutativity.
n=len(A);c=C[0:1];b1=B[:,0:1];b2=B[:,2:3];d1=Du[0,0];d2=Du[0,2]
# Two source-generator filters and two grid responses in a single augmented ODE.
AA=np.zeros((4*n,4*n));BB=np.zeros((4*n,1))
for j in range(4):AA[j*n:(j+1)*n,j*n:(j+1)*n]=A
BB[:n]=b2;BB[n:2*n]=b1
AA[2*n:3*n,:n]=b1@c;BB[2*n:3*n]=b1*d2
AA[3*n:,n:2*n]=b2@c;BB[3*n:]=b2*d1
CC=np.zeros((4,4*n));DD=np.zeros((4,1))
CC[0,:n]=c;DD[0]=d2;CC[1,n:2*n]=c;DD[1]=d1
CC[2,:n]=d1*c;CC[2,2*n:3*n]=c;DD[2]=d1*d2
CC[3,n:2*n]=d2*c;CC[3,3*n:]=c;DD[3]=d2*d1
T=np.arange(0,40+0.005,0.01);v=np.where(T<=20,np.sin(2*np.pi*0.2*T),0)
_,Y,_=lsim((AA,BB,CC,DD),v,T,interp=True)
scale=1/np.max(np.abs(Y[:,:2]));Y*=scale;v*=scale
cascade={'case':'kundur','sensor':'V bus7','same_zero_grid_state':True,'source_generator_states_zero':True,'drive_scale':float(scale),'max_source_MW':np.max(np.abs(Y[:,:2]),axis=0).tolist(),'max_voltage_alias_difference_pu':float(np.max(abs(Y[:,2]-Y[:,3]))),'relative_voltage_alias_L2_difference':float(np.linalg.norm(Y[:,2]-Y[:,3])/np.linalg.norm(Y[:,2])),'distinct_source_trace_L2':float(np.linalg.norm(Y[:,0]-Y[:,1])),'source_tail_at_40s_MW':Y[-1,:2].tolist(),'input_interpretation':'Continuous piecewise-linear interpolation of the sampled drive; equality theorem holds for any common admissible causal drive. 40s truncates reported arrays, not the filter evolution. Incremental signals may be signed about a common positive background.'}
np.savez_compressed(D/'causal_single_sensor_alias.npz',t_s=T,common_drive=v,source1_at_bus7_MW=Y[:,0],source2_at_bus8_MW=Y[:,1],world1_voltage7_pu=Y[:,2],world2_voltage7_pu=Y[:,3])
np.savez_compressed(D/'harmonic_transfer_arrays.npz',frequency_Hz=freq,sensor_scales=scales,sensor_order=np.array(['V_first','V_second','F_first','F_second']),**raw)
np.savez_compressed(D/'causal_lockin_arrays.npz',**{key:val for key,val in causal_raw.items() if not isinstance(val,dict)})
results={'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':hashlib.sha256((D/'PROTOCOL_FREEZE.json').read_bytes()).hexdigest(),'harmonic':rows,'descriptor_numerical_audits':solve_audits,'causal_lockin_kundur':causal,'PQ_nuisance':nuisance,'causal_single_sensor_alias':cascade,'direct_PCC':{'resolved_two_port_P':cm(np.eye(2)/P['noise']['direct_PCC_scale_MW']),'one_aggregate_P':cm(np.ones((1,2))/P['noise']['direct_PCC_scale_MW'])}}
(D/'results.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
with (D/'harmonic_summary.csv').open('w') as o:
 fields=['case','frequency_Hz','sensors','channel_count','correlation','sin_principal_angle','normalized_column_condition','critical_MW_source1','critical_MW_source2'];writer=csv.DictWriter(o,fields);writer.writeheader()
 for row in rows:writer.writerow({**{key:row[key] for key in fields[:-2]},'critical_MW_source1':row['critical_amplitude_MW'][0],'critical_MW_source2':row['critical_amplitude_MW'][1]})
print(json.dumps({'harmonic_records':len(rows),'causal_lockin_records':len(causal),'numeric_warnings':sum(r['numerical_warning'] for r in solve_audits),'cascade':cascade,'representative':[r for r in rows if r['frequency_Hz']==0.2]},indent=2))
# Read-only integrity is checked both before and after every calculation.
assert all(hashlib.sha256((S/f).read_bytes()).hexdigest()==h for f,h in P['input_sha256'].items())
(D/'input_integrity_after.json').write_text(json.dumps({'all_input_hashes_unchanged':True,'sha256':P['input_sha256']},indent=2)+'\n')
