"""Post-primary, explicitly exploratory equal-ratio window-shape ablation.
Chosen only after primary L=8 results: compare (L,B)=(4,1) with (8,2).
No claim of pre-outcome freezing or held-out confirmation.
"""
from pathlib import Path
import ctypes,json,csv
import numpy as np
from scipy.optimize import linprog
R=Path(__file__).resolve().parent;OLD=R.parents[1]/'round2_g6_joint_admission_20261003';primary=json.loads((R/'SUMMARY.json').read_text())
lib=ctypes.CDLL(str(R/'window_dp.so'));ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS');lib.window_dp.argtypes=[ptr,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ptr]
L=4;B=1;M=2048;N=256;T=2.;a=np.array([.5,.5]);rows=[];words=[]
for name,sub in [('positive','positive_workpoint'),('wecc','transfer')]:
 src=OLD/sub;W=np.load(src/f'{name}_coefficients.npy',mmap_mode='r');supp=np.load(src/f'{name}_support_arrays.npz');p=np.array(W[:,:,0,:])*.5;q=np.array(W[:,:,1,:])*.5;r0=abs(p+q);d=np.ascontiguousarray(abs(p-q)-r0);out=np.empty(d.shape[0]*d.shape[1]);lib.window_dp(d.reshape(-1,N+1),len(out),N+1,L,B,out);support=r0.sum(-1)+out.reshape(d.shape[:2]);o,phase=np.unravel_index(support.argmax(),support.shape);peak=float(support[o,phase]);error=float(supp['tail'][20]+supp['phase_error'][20]);inner=.05/(peak+error);outer=.05/peak
 # Independent LP with the *four*-block constraint; normalized objective.
 dd=d[o,phase];scale=float(abs(dd).max());A=np.zeros((N+2-L,N+1))
 for k in range(len(A)):A[k,k:k+L]=1
 lp=linprog(-dd/scale,A_ub=A,b_ub=np.ones(len(A)),bounds=(0,1),method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9});assert lp.success
 lpz=np.rint(lp.x).astype(int);assert np.max(abs(lpz-lp.x))<1e-6 and np.max(A@lpz)<=B
 scores={0:0.};backs=[]
 for gain in dd:
  nxt={};back={}
  for state,v in scores.items():
   for bit in [0,1]:
    if state.bit_count()+bit>B:continue
    dest=((state<<1)|bit)&((1<<(L-1))-1);value=v+gain*bit
    if dest not in nxt or value>nxt[dest]:nxt[dest]=value;back[dest]=(state,bit)
  scores=nxt;backs.append(back)
 state=max(scores,key=scores.get);z=[]
 for back in reversed(backs):state,bit=back[state];z.append(bit)
 z=np.array(z[::-1]);assert np.max(A@z)<=B
 lp_gap=float(abs(dd@z+lp.fun*scale));assert lp_gap<1e-10
 ss=np.where(p[o,phase]+(1-2*z)*q[o,phase]>=0,1,-1);u=np.column_stack((ss*.5,ss*(1-2*z)*.5));direct=float(np.sum(W[o,phase].T*u));gap=abs(direct-peak);assert gap<1e-10
 base=next(r for r in primary['brackets'] if r['source']==name and r['ray_index']==0 and r['B']==2)
 row={'source':name,'status':'post-primary secondary exploratory ablation','ray_a1':.5,'ray_a2':.5,'L':L,'B':B,'B_over_L':B/L,'phase_intervals':M,'N_past':N,'peak_lower_Hz_per_MW':peak,'peak_upper_Hz_per_MW':peak+error,'inner_amplitude_MW':inner,'outer_amplitude_MW':outer,'comparison_L':8,'comparison_B':2,'comparison_inner_MW':base['inner_amplitude_MW'],'comparison_outer_MW':base['outer_amplitude_MW'],'window_shape_gain_lower_fraction':inner/base['outer_amplitude_MW']-1,'window_shape_gain_upper_fraction':outer/base['inner_amplitude_MW']-1,'LP_objective_gap_Hz_per_MW':lp_gap,'max_word_direct_sum_gap_Hz_per_MW':gap,'output_index':int(o),'phase_seconds':float(phase*T/M)};rows.append(row)
 words.append({'source':name,'status':row['status'],'L':L,'B':B,'chronological_z':z[::-1].tolist(),'chronological_common_sign':ss[::-1].tolist(),'unit_amplitude_chronological_port_values':u[::-1].tolist(),'probe_phase_seconds':float(phase*T/M),'probe_output_index':int(o),'DP_peak_Hz_per_MW':peak,'independent_DP_word_direct_probe_Hz_per_MW':direct,'note':'Separate Python DP reconstructed maximizing word; independent LP objective agrees to the saved floating numerical tolerance'})
 np.savez_compressed(R/f'{name}_secondary_L4_B1_support.npz',support=support,phase_grid=np.linspace(0,T,M+1))
with (R/'secondary_window_shape.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(R/'SECONDARY_WINDOW_SHAPE.json').write_text(json.dumps({'selection':'Requested after the primary results were available; not frozen primary or held-out evidence','same_allowance_ratio':.25,'hypothesis':'A local four-block burst envelope can improve peak robustness compared with an eight-block window at the same nominal ratio','rows':rows,'words':words},indent=2))
text='''# Secondary window-shape ablation (explicitly post-primary)

This additional comparison was selected after inspecting the frozen primary L=8 outcomes. It is exploratory/analytical evidence, not a held-out or predeclared confirmation. Only the equal ray (0.5,0.5) is added, with (L,B)=(4,1), compared against the existing (8,2). No L=16 sweep was undertaken.

Both contracts have B/L=1/4, but the four-block contract forbids two nearby mismatches that the eight-block contract permits. Every eight-block window is two disjoint four-block windows, so K(4,1) is a subset of K(8,2); the difference tests local burst shape rather than asymptotic rate. Each envelope retains 256 past blocks, 2048 phase intervals and the inherited full continuous-phase/tail error.

| Source | (4,1) bracket MW | (8,2) bracket MW | Bracket-separated window-shape gain |
|---|---:|---:|---:|
'''
for r in rows:text+=f"| {r['source']} | {r['inner_amplitude_MW']:.6f}–{r['outer_amplitude_MW']:.6f} | {r['comparison_inner_MW']:.6f}–{r['comparison_outer_MW']:.6f} | {100*r['window_shape_gain_lower_fraction']:.3f}% |\n"
text+='''
The same-information four-window LP independently checks each maximizing phase/output row, with direct-word discrepancies saved in SECONDARY_WINDOW_SHAPE.json. Raw complete phase supports are retained. Numerical uncertainty, physical/source scope, affine work assumptions, and old nonlinear/voltage limitations are exactly those in REPORT.md; no new nonlinear run was made. The primary protocol and primary result files are unchanged by this secondary calculation.
'''
(R/'SECONDARY_WINDOW_SHAPE.md').write_text(text)
print(json.dumps(rows,indent=2))
