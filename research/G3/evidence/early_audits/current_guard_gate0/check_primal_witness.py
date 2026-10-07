"""Independent algebraic residual/KKT/tail-error postcheck; no solver rerun."""
from pathlib import Path
import json,numpy as np
from scipy.optimize import nnls
R=Path(__file__).resolve().parent;s=json.loads((R/'GATE0_RESULTS.json').read_text());r=next(x for x in s['contracts'] if x['contract']=='structured_amplitude');c=s['constants'];a=c['a'];b=c['b_per_ohm'];cv=c['c_pu_per_modulation'];w=c['omega'];Ts=c['Ts'];N=c['N'];L=c['L_H'];ohm=c['R_ohm'];Ib=c['Ibase_A_peak'];lam=ohm/L
A=np.array(r['A']);B=np.array(r['B']);K=np.array(r['K']);Acl=np.array(r['Acl']);s0=np.array(s['observation_interface']['aligned_initial_s0']);sb=np.array(r['terminal_center_sbar']);aff=np.array(r['affine_center_d']);mnom=np.array(r['first_nominal_PI_modulation']);d=json.loads((R.parents[0]/'protocol/GATE_A_LOCKED_V2_1.json').read_text());Ec=.7*d['V_phase_peak_base_V']
rr=r['disturbance_radius_current_pu'];ulim=r['tightened_nominal_input_radius'];ilim=r['tightened_nominal_current_node_radius'];nx=4+2*N
T=np.zeros((4,4));T[:2,:2]=np.eye(2);T[:,2:]=Acl[:,:2];p0=np.zeros((4,nx));p0[:,:4]=-T;J=[p0];v=[s0]
for j in range(N):
 p=A@J[-1];p[:,4+2*j:6+2*j]+=B;J.append(p);v.append(A@v[-1]+aff)
def aof(t):return np.exp(-lam*t)
def bof(t):return -np.expm1(-lam*t)/ohm
def je(t):return (np.exp(1j*w*t)-np.exp(-lam*t))/(ohm+1j*w*L)
def v2(z):return np.array([z.real,z.imag])
cons=[]
def add(M,z,d,label):cons.append((M,z,d,label))
for j in [0,1]:
 M=np.zeros((2,nx));M[:,2*j:2*j+2]=np.eye(2);add(M,np.zeros(2),rr,'Omega'+str(j))
for j in range(N):
 M=np.zeros((2,nx));M[:,4+2*j:6+2*j]=np.eye(2);add(M,np.zeros(2),ulim,'input'+str(j))
for j in range(N+1):add(J[j][2:],v[j][2:],ulim,'queue'+str(j))
for j in range(N):
 for k,t in enumerate(np.linspace(0,Ts,5)):
  C=np.block([aof(t)*np.eye(2),1400*bof(t)/Ib*np.eye(2)]);add(C@J[j],C@v[j]-v2(Ec*je(t)/Ib),ilim,'current'+str(j)+'_'+str(k))
x=np.r_[np.array(r['initial_Omega_witnesses']).ravel(),np.array(r['nominal_inputs']).ravel()];E=J[-1];eb=v[-1]-sb
Cfirst=np.zeros((2,nx));Cfirst[:,4:6]=np.eye(2);Cfirst[:,:4]+=K@T
qval=np.array([radius*radius-np.dot(M@x+off,M@x+off) for M,off,radius,_ in cons]);nres=np.array([np.linalg.norm(M@x+off)-radius for M,off,radius,_ in cons]);G=np.array([-2*(M@x+off)@M for M,off,_,_ in cons]);grad=2*Cfirst.T@(Cfirst@x-mnom)
active=np.flatnonzero(nres>=-1e-8);proj=np.eye(nx)-E.T@np.linalg.solve(E@E.T,E);lam_ineq,res=nnls(proj@G[active].T,proj@grad);lam_eq=np.linalg.solve(E@E.T,E@(G[active].T@lam_ineq-grad));stationary=grad+E.T@lam_eq-G[active].T@lam_ineq
# Mathematical terminal repair uses only the final two nominal inputs.
err=E@x+eb;delta=np.linalg.solve(E[:,-4:],-err);xc=x.copy();xc[-4:]+=delta
changes=np.array([np.linalg.norm(M@(xc-x)) for M,_,_,_ in cons]);tail_slacks=[]
for k,(M,off,radius,label) in enumerate(cons):
 if np.any(abs(M[:,-4:])>1e-14):tail_slacks.append({'name':label,'old_norm_slack':float(-nres[k]),'change_norm_bound':float(changes[k])})
out={'status':'READ_ONLY_OFFLINE_PRIMAL_POSTCHECK_NO_CLOSED_LOOP','active_tolerance_norm':1e-8,'primal_max_norm_violation':float(max(nres)),'terminal_equality_inf':float(max(abs(err))),'active_constraint_names':[cons[k][3] for k in active],'nonnegative_inequality_multipliers':lam_ineq.tolist(),'equality_multipliers':lam_eq.tolist(),'stationarity_inf':float(max(abs(stationary))),'complementarity_max_abs':float(max(abs(lam_ineq*qval[active]))),'dual_feasibility_min_multiplier':float(min(lam_ineq)),'interpretation':'Numerical KKT consistency for a convex QCQP; not a machine-verified optimality certificate. No gain,N,threshold or solver plan search was repeated.','terminal_tail_repair':{'ideal_formula':'delta_tail = -[A B, B]^{-1} (z_N-sbar), only last2 nominal inputs; exact real arithmetic removes terminal equality residue. No physical state is projected.','stored_plan_kept_unchanged':True,'delta_tail':delta.tolist(),'max_abs_delta':float(max(abs(delta))),'candidate_repaired_terminal_residual_inf':float(max(abs(E@xc+eb))),'first_modulation_change_due_to_repair':float(np.linalg.norm(Cfirst@(xc-x))),'affected_constraints':tail_slacks,'minimum_affected_constraint_slack':min(v['old_norm_slack'] for v in tail_slacks),'max_constraint_change_bound':max(v['change_norm_bound'] for v in tail_slacks),'limit':'Finite-precision/transcendental outward enclosure still not implemented. This bounds a tail-equality issue, not every implementation error.'}}
(R/'PRIMAL_POSTCHECK.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
