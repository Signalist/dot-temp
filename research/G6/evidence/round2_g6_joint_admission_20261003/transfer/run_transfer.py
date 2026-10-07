"""Original numerical G6 two-port continuous-block support experiment.
Only numpy/scipy and frozen public-model data. No installed grid code executes.
"""
from pathlib import Path
import os,sys,json,hashlib,time,csv
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np
from scipy import linalg,sparse
from scipy.sparse.linalg import splu
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parents[1]/'round2_20261003'/'grid_transfer'
T=2.; QS=np.array([[1,1],[1,-1],[-1,-1],[-1,1]],float)
N=256; FMAX=.05; RAYS=np.array([(j/40,1-j/40) for j in range(41)])
def savej(p,x): p.write_text(json.dumps(x,indent=2,allow_nan=False))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def kernel_integral(lam,tau):
 out=np.zeros((len(lam),2),complex)
 for j,q in enumerate(QS):
  lo=j*T/4;hi=min((j+1)*T/4,tau)
  if hi<=lo:continue
  d=hi-lo;z=np.empty_like(lam);m=abs(lam)>1e-12
  z[m]=np.expm1(lam[m]*d)/lam[m];z[~m]=d
  out += (np.exp(lam*(tau-hi))*z)[:,None]*q
 return out

def qualify_kundur():
 p=SOURCE/'kundur_reduced51.npz';d=np.load(p);A=d['A'];B=d['B'][:,[0,2]];C=d['C_frequency_Hz']
 lam,V=linalg.eig(A);be=linalg.solve(V,B);R=np.einsum('om,mi->omi',C@V,be)
 err=[]
 for s in [.01+.1j,.1+.5j,1+2j,10+10j,100+100j,1000+100j]:
  a=np.einsum('omi,m->oi',R,1/(s-lam));b=C@linalg.solve(s*np.eye(len(A))-A,B)
  err.append(float(np.linalg.norm(a-b)/max(np.linalg.norm(b),1e-30)))
 np.savez_compressed(ROOT/'kundur_kernel.npz',lam=lam,R=R,A=A,B=B,C=C)
 stat={'source':str(p),'source_sha256':sha(p),'state_dimension':51,'outputs':4,'ports':['P_MW@bus7','P_MW@bus8'],'max_eigenvalue_real':float(lam.real.max()),'eigenvector_condition':float(np.linalg.cond(V)),'max_resolvent_relative_error':max(err),'qualification_pass':bool(max(err)<1e-8 and lam.real.max()<0)}
 savej(ROOT/'kundur_qualification.json',stat);return lam,R,stat

def qualify_wecc():
 kp=SOURCE/'wecc_verified_descriptor_K.npz';ap=SOURCE/'wecc_descriptor_aux.npz';K=sparse.load_npz(kp);d=np.load(ap);mass=d['mass'];G=d['G'][:,[0,2]];n=len(d['x_names'])
 oi=np.array([i for i,s in enumerate(d['x_names']) if s.startswith('omega GENROU ')])
 Cf=np.eye(n)[oi]*60;lu=splu(K[n:,n:].tocsc());Y=-lu.solve(K[n:,:n].toarray());U=-lu.solve(G[n:]);F=K[:n,:n].toarray()+K[:n,n:]@Y;B=G[:n]+K[:n,n:]@U;E=np.diag(mass[:n])
 w,L,V=linalg.eig(F,E,left=True,right=True,homogeneous_eigvals=True);finite=abs(w[1])>1e-9;lam=w[0,finite]/w[1,finite];V=V[:,finite];L=L[:,finite]
 unused=set(range(len(lam)));groups=[]
 while unused:
  j=min(unused);ids=[i for i in unused if abs(lam[i]-lam[j])<1e-7*max(1,abs(lam[j]))];unused.difference_update(ids);groups.append(ids)
 rs=[];ls=[];conds=[];res=[]
 for ids in groups:
  v=V[:,ids];ll=L[:,ids];gram=ll.conj().T@E@v;conds.append(float(np.linalg.cond(gram)));weight=linalg.solve(gram,ll.conj().T@B);rs.append(Cf@v@weight);ls.append(np.mean(lam[ids]))
 lam=np.array(ls);R=np.stack(rs,axis=1);gauge=abs(lam)<1e-7
 # The only removed root is the analytically known uniform-angle gauge.
 gauge_R=float(abs(R[:,gauge,:]).max(initial=0));raw_lam=lam.copy();raw_R=R.copy();lam=lam[~gauge];R=R[:,~gauge,:]
 Cfull=np.zeros((len(oi),len(mass)));Cfull[:,oi]=60*np.eye(len(oi))
 checks=[]
 for s in [.001+.003j,.01+.1j,.1+.5j,1+2j,10+10j,100+100j,1000+100j,1e4+1e4j,1e5+1e4j]:
  exact=Cfull@splu((s*sparse.diags(mass)-K).astype(complex).tocsc()).solve(G.astype(complex));approx=np.einsum('omi,m->oi',R,1/(s-lam));checks.append({'s':[s.real,s.imag],'absolute_error':float(abs(exact-approx).max()),'relative_error':float(np.linalg.norm(exact-approx)/max(np.linalg.norm(exact),1e-30))})
 s=1e6+2e5j;hf=Cfull@splu((s*sparse.diags(mass)-K).astype(complex).tocsc()).solve(G.astype(complex));remainder=hf-np.einsum('omi,m->oi',R,1/(s-lam))
 stat={'sources':{str(p):sha(p) for p in [kp,ap]},'method':'Original verified descriptor, algebraic elimination then generalized finite residues with repeated-eigenvalue block biorthogonalization. Not the rejected ordinary QZ model. Two real P input columns independently checked.','ports':['P_MW@bus1','P_MW@bus4'],'original_descriptor_dimension':len(mass),'differential_named_variables':n,'generator_outputs':len(oi),'finite_eigenvalues':int(finite.sum()),'finite_groups_before_gauge':len(raw_lam),'uniform_angle_gauge_roots_removed':int(gauge.sum()),'gauge_eigenvalues':[[z.real,z.imag] for z in raw_lam[gauge]],'max_gauge_frequency_residue':gauge_R,'max_biorthogonal_group_condition':max(conds),'max_stable_eigenvalue_real':float(lam.real.max()),'high_frequency_polynomial_remainder':float(abs(remainder).max()),'resolvent_checks':checks,'qualification_pass':bool(gauge.sum()==1 and gauge_R<1e-10 and lam.real.max()<0 and max(x['relative_error'] for x in checks)<1e-6 and abs(remainder).max()<1e-9),'limitations':['Floating eigensystem and resolvent checks, no directed rounding','Gauge exclusion is structural unobservability plus a numerical residual check','Original pencil is ill conditioned; tests do not prove nonlinear fidelity at admission amplitudes']}
 savej(ROOT/'wecc_qualification.json',stat);np.savez_compressed(ROOT/'wecc_kernel.npz',lam=lam,R=R,raw_lam=raw_lam,raw_R=raw_R,omega_indices=oi,group_conditions=conds)
 if not stat['qualification_pass']:raise RuntimeError('WECC two-input transfer not qualified')
 return lam,R,stat

def run(name,lam,R,qual):
 print(name,'begin',flush=True)
 rr=np.exp(T*lam.real);tmpl=kernel_integral(lam,T);Rblock=R*tmpl[None,:,:];powers=np.exp(lam[:,None]*T*np.arange(N)[None,:]);n_o=R.shape[0]
 tail=np.einsum('omi,m->oi',abs(Rblock),rr**N/(1-rr))
 dtail=np.einsum('omi,m->oi',abs(Rblock*lam[None,:,None]),rr**N/(1-rr))
 integabs=-np.expm1(lam.real*T)/(-lam.real)
 L1=(abs(R*lam[None,:,None])*integabs[None,:,None]).sum(axis=1)+(abs(Rblock*lam[None,:,None])/(1-rr)[None,:,None]).sum(axis=1)+abs(R.sum(axis=1))
 L2=(abs(R*lam[None,:,None]**2)*integabs[None,:,None]).sum(axis=1)+(abs(Rblock*lam[None,:,None]**2)/(1-rr)[None,:,None]).sum(axis=1)+abs((R*lam[None,:,None]).sum(axis=1))
 np.savez_compressed(ROOT/f'{name}_bound_components.npz',tail=tail,derivative_tail=dtail,global_L1=L1,global_L2=L2,template_integral=tmpl)
 refinements=[]
 for M in [2048,4096,8192,16384]:
  phase=np.linspace(0,T,M+1);h=T/M
  shape=(n_o,M+1,2,N+1);W=np.lib.format.open_memmap(ROOT/f'{name}_coefficients.npy',mode='w+',dtype=np.float64,shape=shape)
  peaks={k:np.zeros(41) for k in ['committed','dynamic_optional','fixed_optional','independent_ports','reset','single_sign_periodic']};where={k:np.zeros((41,3),int) for k in peaks}
  dpeak=np.zeros(41);direct_max=np.zeros((n_o,2));baseline_gap=0.;imaginary=0.
  for st in range(0,M+1,64):
   ts=phase[st:st+64];integ=np.stack([kernel_integral(lam,t) for t in ts]);expo=np.exp(ts[:,None]*lam[None,:]);cur=np.einsum('omi,pmi->opi',R,integ,optimize=True)
   hist=np.einsum('omi,pm,mn->opin',Rblock,expo,powers,optimize=True)
   imaginary=max(imaginary,float(abs(cur.imag).max()),float(abs(hist.imag).max()))
   wc=np.concatenate((cur.real[:,:,:,None],hist.real),axis=-1);W[:,st:st+len(ts)]=wc
   dh=np.einsum('omi,pm,mn->opin',Rblock*lam[None,:,None],expo,powers,optimize=True).real
   dc=np.einsum('omi,pmi->opi',R*lam[None,:,None],integ,optimize=True).real
   qright=QS[np.minimum((ts/(T/4)).astype(int),3)];qleft=QS[np.maximum(np.ceil(ts/(T/4)).astype(int)-1,0)]
   H0=R.sum(axis=1).real;dcmax=np.maximum(abs(dc+H0[:,None,:]*qright[None,:,:]),abs(dc+H0[:,None,:]*qleft[None,:,:]))
   dcoeff=dcmax+abs(dh).sum(axis=-1)
   individual=abs(wc).sum(axis=-1)
   for j,a in enumerate(RAYS):
    u=wc[:,:,0,:]*a[0];v=wc[:,:,1,:]*a[1];z=u+v
    committed=abs(z).sum(axis=-1);independent=np.einsum('opi,i->op',individual,a);dynamic=.5*(committed+independent)
    classical=np.maximum(np.maximum(abs(u),abs(v)),abs(z)).sum(axis=-1)
    baseline_gap=max(baseline_gap,float(abs(dynamic-classical).max()))
    vals={'committed':committed,'dynamic_optional':dynamic,'fixed_optional':np.maximum(committed,np.maximum(individual[:,:,0]*a[0],individual[:,:,1]*a[1])),'independent_ports':independent,'reset':abs(z[:,:,0]),'single_sign_periodic':abs(np.cumsum(z,axis=-1)).max(axis=-1)}
    for k,s in vals.items():
     idx=np.unravel_index(np.argmax(s),s.shape);val=s[idx]
     if val>peaks[k][j]:
      peaks[k][j]=val;where[k][j]=[idx[0],st+idx[1],int(np.argmax(abs(np.cumsum(z[idx],axis=-1)))) if k=='single_sign_periodic' else N]
    dpeak[j]=max(dpeak[j],float(np.einsum('opi,i->op',dcoeff,a).max()))
  W.flush()
  tails=np.max(tail@RAYS.T,axis=0);dtails=np.max(dtail@RAYS.T,axis=0);l1s=np.max(L1@RAYS.T,axis=0);l2s=np.max(L2@RAYS.T,axis=0)
  L=np.minimum(l1s,dpeak+dtails+h/2*l2s);phase_error=h/2*L;error=tails+phase_error
  relative=float(np.max(error/peaks['committed']));refinements.append({'phase_intervals':M,'max_relative_error_committed':relative,'max_modal_imaginary_residual':imaginary,'same_information_dynamic_baseline_max_abs_difference':baseline_gap});print(name,refinements[-1],flush=True)
  if relative<=.02 or M==16384:break
 # Reset/periodic use the same conservative error envelope: valid but deliberately not optimized.
 rows=[]
 for j,a in enumerate(RAYS):
  row={'ray_index':j,'a1_share':a[0],'a2_share':a[1],'tail_error_Hz_per_MW':tails[j],'phase_error_Hz_per_MW':phase_error[j]}
  for k in peaks:row.update({k+'_peak_lower_Hz_per_MW':peaks[k][j],k+'_peak_upper_Hz_per_MW':peaks[k][j]+error[j],k+'_capacity_lower_MW':FMAX/(peaks[k][j]+error[j]),k+'_capacity_upper_MW':FMAX/peaks[k][j]})
  row['common_vs_independent_capacity_gain_lower']=row['committed_capacity_lower_MW']/row['independent_ports_capacity_upper_MW']-1
  row['dynamic_vs_independent_capacity_gain_lower']=row['dynamic_optional_capacity_lower_MW']/row['independent_ports_capacity_upper_MW']-1
  row['dynamic_loss_vs_committed_lower']=1-row['dynamic_optional_capacity_upper_MW']/row['committed_capacity_lower_MW']
  rows.append(row)
 with (ROOT/f'{name}_rays.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 # Every-ray exact maximizing finite words, ordered current block then newest past to oldest.
 witnesses={};word_meta=[]
 for k in ['committed','dynamic_optional','independent_ports']:
  us=np.zeros((41,N+1,2));ys=np.zeros(41)
  for j,a in enumerate(RAYS):
   o,p,_=where[k][j];g=W[o,p].T;v=g*a
   if k=='committed':us[j]=np.sign(v.sum(axis=1))[:,None]*a
   elif k=='independent_ports':us[j]=np.sign(g)*a
   else:
    choices=np.array([[0,0],[a[0],0],[0,a[1]],a,[-a[0],0],[0,-a[1]],-a]);ix=np.argmax(g@choices.T,axis=1);us[j]=choices[ix]
   ys[j]=np.sum(g*us[j]);word_meta.append({'contract':k,'ray_index':j,'output_index':int(o),'phase_seconds':float(phase[p]),'prefix_past_blocks':N,'finite_witness_output_Hz_per_total_MW':ys[j],'support_match_error':float(abs(ys[j]-peaks[k][j]))})
  witnesses[k+'_input_MW_per_total_MW']=us;witnesses[k+'_output']=ys;witnesses[k+'_argmax']=where[k]
 np.savez_compressed(ROOT/f'{name}_witnesses.npz',rays=RAYS,phase_grid=phase,**witnesses)
 savej(ROOT/f'{name}_witness_metadata.json',word_meta)
 np.savez_compressed(ROOT/f'{name}_support_arrays.npz',rays=RAYS,phase_grid=phase,tail=tails,phase_error=phase_error,**{k+'_peak':v for k,v in peaks.items()},**{k+'_argmax':v for k,v in where.items()})
 # Predeclared all-ray decision rule: midpoint between strongest rigorously separated capacity brackets.
 decisions=[]
 for j,row in enumerate(rows):
  for strong,weak,label in [('committed','independent_ports','common_information_vs_independent_relaxation'),('dynamic_optional','independent_ports','dynamic_optional_vs_independent_relaxation'),('committed','dynamic_optional','fixed_cohort_not_optional_capacity')]:
   lo=row[strong+'_capacity_lower_MW'];hi=row[weak+'_capacity_upper_MW']
   if lo>hi:
    amp=(lo+hi)/2;decisions.append({'ray_index':j,'comparison':label,'total_amplitude_MW':amp,'allocation_MW':(RAYS[j]*amp).tolist(),'accepted_contract':strong,'accepted_output_upper_Hz':amp*row[strong+'_peak_upper_Hz_per_MW'],'rejected_contract':weak,'rejected_finite_witness_Hz':amp*row[weak+'_peak_lower_Hz_per_MW'],'gap_Hz':amp*(row[weak+'_peak_lower_Hz_per_MW']-row[strong+'_peak_upper_Hz_per_MW'])})
 savej(ROOT/f'{name}_decisions.json',decisions)
 summary={'network':name,'qualification':qual,'phase_refinements':refinements,'N_past_blocks':N,'frequency_limit_Hz':FMAX,'all_time_interpretation':'Unrestricted-sign and optional supports are nondecreasing in available history, so infinite support dominates every zero-state startup prefix. Single-sign comparator explicitly maximizes every startup prefix.','float_numerical_bound_not_interval_proof':True,'same_information_committed_baseline':'Identical classical support sum by derivation; no solver gain','same_information_dynamic_baseline_max_abs_gap':baseline_gap,'equal_split':rows[20],'maximum_common_vs_independent_capacity_gain_lower':max(r['common_vs_independent_capacity_gain_lower'] for r in rows),'maximum_dynamic_vs_independent_capacity_gain_lower':max(r['dynamic_vs_independent_capacity_gain_lower'] for r in rows),'maximum_dynamic_capacity_loss_vs_committed_lower':max(r['dynamic_loss_vs_committed_lower'] for r in rows),'decision_counts':{k:sum(d['comparison']==k for d in decisions) for k in sorted(set(d['comparison'] for d in decisions))},'raw_coefficients_shape':list(shape),'raw_coefficients_file':f'{name}_coefficients.npy','coefficient_order':'output,phase,port,[current,lag0,...,lag255]','phase_bound':'h/2 times min(global analytic first-derivative bound, maximum sampled sum-absolute first derivatives plus exact derivative modal tail plus h/2 global second-derivative bound). Each segment endpoint uses both one-sided derivatives.'}
 savej(ROOT/f'{name}_summary.json',summary);print(name,'COMPLETE',json.dumps({k:summary[k] for k in ['maximum_common_vs_independent_capacity_gain_lower','maximum_dynamic_vs_independent_capacity_gain_lower','maximum_dynamic_capacity_loss_vs_committed_lower','decision_counts']}),flush=True)
 return summary

if __name__=='__main__':
 which=sys.argv[1:];summaries=[]
 for name,fn in [('kundur',qualify_kundur),('wecc',qualify_wecc)]:
  if which and name not in which:continue
  lam,R,qual=fn();print(name,'qualified',flush=True);summaries.append(run(name,lam,R,qual))
 savej(ROOT/'latest_run_summary.json',summaries)
