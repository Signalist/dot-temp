"""Frozen Gate0 algebra/one-point optimization. No closed-loop simulation.
All disturbance/terminal conclusions are conditional on stated physical domains.
"""
from pathlib import Path
import json,hashlib,time
import numpy as np
from scipy.optimize import minimize,LinearConstraint,NonlinearConstraint
RDIR=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
FP=RDIR/'protocol/GATE0_MPSC_DESIGN_V1.json';F=json.loads(FP.read_text());D=json.loads((RDIR/F['base_protocol']).read_text());cp=json.loads((RDIR/F['checkpoint']).read_text())
Ts=1e-4;N=10;Lf=D['filter_L_H'];Lg=D['grid_L_H'];L=Lf+Lg;Rf=D['filter_R_ohm'];Rg=D['grid_R_ohm'];R=Rf+Rg;lam=R/L;omega=D['omega_base_rad_s'];Ibase=D['I_phase_peak_base_A'];Ebase=D['V_phase_peak_base_V'];Cdc=D['C_dc_F'];Vbar=1400.;Vlo=1120.;Vhi=1540.;mmax=.95/np.sqrt(3);num=1e-8

def vv(z):return np.array([np.real(z),np.imag(z)],float)
def cc(x):return complex(*x)
def rot(a):return np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]])
def aof(t):return np.exp(-lam*t)
def bof(t):return -np.expm1(-lam*t)/R
def cof(t):return Vbar*bof(t)/Ibase
def je(t):return (np.exp(1j*omega*t)-np.exp(-lam*t))/(R+1j*omega*L)
a=aof(Ts);b=bof(Ts);c=cof(Ts);Rot=rot(-omega*Ts);Ki=-a*a/c;Kq=-a;K=np.block([Ki*np.eye(2),Kq*np.eye(2)]);A=np.zeros((4,4));A[:2,:2]=a*Rot;A[:2,2:]=c*Rot;B=np.zeros((4,2));B[2:]=Rot;Acl=A+B@K
# Current measurements are read only at the first saved pre-update point.
# This independently recorded abc point is an exact transform of the mandated dq checkpoint.
p0file=RDIR/'model_audit/p_priority_abc/fast_p_priority_abc_h1e-05.npz';zz=np.load(p0file);rr=zz['trace'][0];names=zz['trace_columns'].tolist();get=lambda k:rr[names.index(k)]
ia=np.array([get('ia'),get('ib'),get('ic')]);i_meas=(2/3)*np.dot(ia,np.exp(-1j*np.array([0,-2*np.pi/3,2*np.pi/3])));W0=get('Wdc');pb0=get('Pbat');vdc0=np.sqrt(2*W0/Cdc);m_applied=complex(*cp['controller']['applied']);m_queued=complex(*cp['controller']['queued']);Smeas=complex(get('Ppcc_W'),get('Qpcc_var'));vp_meas=Smeas/(1.5*np.conj(i_meas));u_meas=vdc0*m_applied
e_est=(L/Lf)*vp_meas-(Lg/Lf)*(u_meas-Rf*i_meas)-Rg*i_meas;theta=float(np.angle(e_est));rotation=np.exp(-1j*theta);ip=i_meas*rotation;qp=m_queued*rotation;s0=np.r_[vv(ip/Ibase),vv(qp)]
post=zz['sample_after'][0];postcols=zz['sample_state_columns'].tolist();mn=complex(post[postcols.index('queued_re')],post[postcols.index('queued_im')])*rotation;pb_cmd=float(post[postcols.index('source_command')]);mnom=vv(mn)
assert abs(get('t')-.6)<1e-12
assert abs(abs(i_meas)-np.hypot(cp['plant_state'][0],cp['plant_state'][1]))<1e-7
assert zz['control'][0,zz['control_columns'].tolist().index('iref_pu')]<.95

# Same-state immutable first hold: first-exit DC bounds, no future sampled trajectory.
def source_held(p,u,t,tau,rate):
 sg=np.sign(u-p);gap=abs(u-p);tr=max(0.,(gap-rate*tau)/rate)
 return p+sg*rate*t if t<=tr else u-sg*min(gap,rate*tau)*np.exp(-(t-tr)/tau)
def bus(p):return .99*p if p>=0 else p/.99
holds=[]
for label,tau,rate in [('slow',.02,5e6),('hypothetical_fast',.002,50e6)]:
 pend=source_held(pb0,pb_cmd,Ts,tau,rate);buslo=min(bus(pb0),bus(pend));bushi=max(bus(pb0),bus(pend));mhold=abs(qp)
 wdotlo=buslo-1.5*Vhi*mhold*Ibase-7200.;wdothi=bushi+1.5*Vhi*mhold*Ibase-1200.
 def vbox(t):return np.sqrt(2*(W0+min(0.,wdotlo)*t)/Cdc),np.sqrt(2*(W0+max(0.,wdothi)*t)/Cdc)
 grid=np.linspace(0,Ts,101);upper=[];lo_witness=[];n=ip/abs(ip);nq=float(np.real(np.conj(n)*qp));eps=1e-6
 for t in grid:
  vl,vh=vbox(t);vm=(vl+vh)/2;dv=(vh-vl)/2;center=aof(t)*ip+qp*vm*bof(t)-.7*Ebase*je(t)
  rx=.3*Ebase*max(0.,np.real(je(t)));ry=.3*Ebase*max(0.,np.imag(je(t)))
  vals=[abs(center+sv*qp*dv*bof(t)+sx*rx+1j*sy*ry) for sv in [-1,1] for sx in [-1,1] for sy in [-1,1]]
  upper.append(max(vals)/Ibase)
  # Allowed only by broad_circle: reverse source phase180deg just1us after sample.
  prefix=min(t,eps);e_integral=(-Ebase*je(t)+2*Ebase*np.exp(-lam*(t-prefix))*je(prefix)) if t>eps else Ebase*je(t)
  projection=aof(t)*abs(ip)+nq*(vl if nq>=0 else vh)*bof(t)-np.real(np.conj(n)*e_integral)
  lo_witness.append(projection/Ibase)
 M_I=(Vhi*mhold+Ebase+R*Ibase)/(L*Ibase);upper_cert=max(upper)+M_I*1e-6+num
 vl,vh=vbox(Ts);assert vl>Vlo and vh<Vhi
 holds.append({'port':label,'tau_s':tau,'ramp_W_per_s':rate,'known_updated_source_command_W':pb_cmd,'source_power_end_bound_W':pend,'Wdot_domain_lower_W':wdotlo,'Wdot_domain_upper_W':wdothi,'Vdc_dynamic_box_end_V':[float(vl),float(vh)],'W_domain_closure':True,'structured_peak_node_current_outer_bound_pu':float(max(upper)),'intersample_padding_pu':M_I*1e-6+num,'structured_first_hold_certified_upper_pu':float(upper_cert),'structured_first_hold_admitted':bool(upper_cert<1),'broad_circle180deg_reversal_at1us_projection_lower_at100us_pu':float(lo_witness[-1]),'broad_circle_counterexample_certified':bool(lo_witness[-1]>1+num),'argument':'Both current and W domain are assumed only until first exit. DC bounds cannot exit in100us. Structured current outer bound closes the first-exit argument; broad-circle projection>1 contradicts current safety for an allowed phase reversal. No conclusion about impossibility of the narrower amplitude-only class.','time_grid_s':grid.tolist(),'structured_node_bounds_pu':upper,'broad_witness_projection_lower_pu':lo_witness})

results=[]
for name,contract in F['contracts'].items():
 tic=time.monotonic();Ec=contract['source_center_pu']*Ebase;Er=contract['source_uncertainty_radius_pu']*Ebase
 r=b*(max(abs(Vlo-Vbar),abs(Vhi-Vbar))*mmax+Er)/Ibase
 epsI=(1+a)*r;umargin=abs(Ki)*r;utight=mmax-umargin
 qbar=Ec*je(Ts)/(Vbar*b);mbar=np.exp(1j*omega*Ts)*qbar;sbar=np.r_[np.zeros(2),vv(qbar)];d=np.r_[-Rot@vv(Ec*je(Ts)/Ibase),np.zeros(2)]
 Tomega=np.zeros((4,4));Tomega[:2,:2]=np.eye(2);Tomega[:,2:]=Acl[:,:2]
 center_eq=float(np.max(abs(A@sbar+B@vv(mbar)+d-sbar)))
 # Uniform tube radius at every hold fraction follows a closed algebraic identity.
 sig=np.linspace(0,Ts,101);radii=np.array([(aof(t)+abs(aof(t)*a+cof(t)*Ki))*r+(bof(t)/b)*r for t in sig]);radius_res=float(np.max(abs(radii-epsI)))
 # Unconditional nominal-state box over one hold for the chord-error estimate.
 mu_domain=1+(Vbar*max(utight,0)+Ec)*b/Ibase
 d1=(Vbar*max(utight,0)+Ec+R*Ibase*mu_domain)/(L*Ibase)
 d2=lam*d1+omega*Ec/(L*Ibase);hnode=Ts/4;chord=d2*hnode*hnode/8;itight=1-epsI-chord-num
 terminal_node=max(abs(cof(t)*qbar-Ec*je(t)/Ibase) for t in np.linspace(0,Ts,5));terminal_current_bound=terminal_node+chord+epsI+num
 terminal_mod_bound=abs(mbar)+umargin+num
 terminal_ok=terminal_current_bound<=1 and terminal_mod_bound<=mmax and utight>0 and itight>0
 # Parametric lifted nominal state from Omega witnesses and nominal controls.
 nx=4+2*N;P0=np.zeros((4,nx));P0[:,:4]=-Tomega;J=[P0];v=[s0.copy()]
 for j in range(N):
  pj=A@J[-1];pj[:,4+2*j:6+2*j]+=B;J.append(pj);v.append(A@v[-1]+d)
 E=J[-1];eb=v[-1]-sbar
 norms=[]
 def add(M,off,rad,label):norms.append((np.array(M),np.array(off),float(rad),label))
 for j in [0,1]:
  M=np.zeros((2,nx));M[:,2*j:2*j+2]=np.eye(2);add(M,np.zeros(2),r,'initial_Omega_w'+str(j))
 for j in range(N):
  M=np.zeros((2,nx));M[:,4+2*j:6+2*j]=np.eye(2);add(M,np.zeros(2),utight,'nominal_input_'+str(j))
 for j in range(N+1):add(J[j][2:],v[j][2:],utight,'nominal_queue_'+str(j))
 for j in range(N):
  for k,t in enumerate(np.linspace(0,Ts,5)):
   Cflow=np.block([aof(t)*np.eye(2),cof(t)*np.eye(2)]);add(Cflow@J[j],Cflow@v[j]-vv(Ec*je(t)/Ibase),itight,'current_'+str(j)+'_'+str(k))
 Cfirst=np.zeros((2,nx));Cfirst[:,4:6]=np.eye(2);Cfirst[:,:4]+=K@Tomega
 def obj(x):e=Cfirst@x-mnom;return float(e@e)
 def grad(x):return 2*Cfirst.T@(Cfirst@x-mnom)
 def g(x):return np.array([rad*rad-np.sum((M@x+off)**2) for M,off,rad,_ in norms])
 def gj(x):return np.array([-2*(M@x+off)@M for M,off,rad,_ in norms])
 xstart=np.linalg.lstsq(E,-eb,rcond=None)[0]
 sol=minimize(obj,xstart,jac=grad,method='SLSQP',constraints=[LinearConstraint(E,-eb,-eb),NonlinearConstraint(g,0,np.inf,jac=gj)],options={'ftol':1e-12,'maxiter':500,'disp':False})
 x=sol.x;eq_res=float(np.max(abs(E@x+eb)));norm_violations=[float(np.linalg.norm(M@x+off)-rad) for M,off,rad,_ in norms];primal=max(0.,max(norm_violations),eq_res);plan_ok=primal<=1e-8 and terminal_ok
 z=np.array([Jj@x+vj for Jj,vj in zip(J,v)]);u=x[4:].reshape(N,2);u0=Cfirst@x
 active=[{'constraint':norms[j][3],'norm_residual':norm_violations[j]} for j in np.argsort(norm_violations)[-5:]]
 # No dual-infeasibility certificate is asserted for SLSQP.
 result={'contract':name,'state_frame':'Causal initial measured source-phase frame, rotating thereafter at the declared60Hz; every equation includes Rot(-omega Ts) and the affine center-source integral','A':A.tolist(),'B':B.tolist(),'affine_center_d':d.tolist(),'K':K.tolist(),'Acl':Acl.tolist(),'Acl_squared_norm_inf':float(np.linalg.norm(Acl@Acl,np.inf)),'disturbance_radius_current_pu':r,'Omega_current_radius_pu':epsI,'Omega_queue_radius':umargin,'K_Omega_input_radius':umargin,'tightened_nominal_input_radius':utight,'tightened_nominal_current_node_radius':itight,'hold_current_tube_radius_identity_residual':radius_res,'nominal_second_derivative_bound_pu_per_s2':d2,'nominal_chord_padding_pu':chord,'terminal_center_sbar':sbar.tolist(),'terminal_nominal_input_mbar':vv(mbar).tolist(),'terminal_center_affine_residual':center_eq,'terminal_current_continuous_bound_pu':float(terminal_current_bound),'terminal_modulation_bound':float(terminal_mod_bound),'terminal_set_nonempty_and_constraint_compatible_conditional':bool(terminal_ok),'backup':'m=mbar+K(s-sbar); phase-consistent, delayed modulation state preserved; conditional on declared voltage domains','solver':{'name':'SciPy SLSQP','success_flag':bool(sol.success),'status':int(sol.status),'message':str(sol.message),'iterations':int(sol.nit),'objective':float(sol.fun),'terminal_equality_residual_inf':eq_res,'max_norm_constraint_violation':max(norm_violations),'max_primal_residual':primal,'verified_one_point_primal_feasible':bool(plan_ok),'dual_infeasibility_certificate':False,'worst_constraints':active},'first_nominal_PI_modulation':mnom.tolist(),'first_certified_plan_input_candidate':u0.tolist(),'first_input_difference_norm':float(np.linalg.norm(u0-mnom)),'nominal_states':z.tolist(),'nominal_inputs':u.tolist(),'initial_Omega_witnesses':x[:4].reshape(2,2).tolist(),'wall_time_s':time.monotonic()-tic,'qualification':'Analytical ideal-real-arithmetic construction plus double-precision residual checks. Not machine-verified interval arithmetic, not a joint DC invariant set, not closed-loop or100us real-time validation.'}
 results.append(result)
out={'status':'GATE0_ONLY_NO_CLOSED_LOOP_RUN','protocol_sha256':hashlib.sha256(FP.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'constants':{'Ts':Ts,'N':N,'L_H':L,'R_ohm':R,'a':a,'b_per_ohm':b,'c_pu_per_modulation':c,'mmax':mmax,'Ibase_A_peak':Ibase,'Vdc_domain':[Vlo,Vhi],'Vbar':Vbar,'omega':omega},'observation_interface':{'data_source':str(p0file.relative_to(RDIR)),'data_source_sha256':hashlib.sha256(p0file.read_bytes()).hexdigest(),'only_first_preupdate_measurement_and_same_sample_nominal_controller_output_used':True,'blocked_fields_not_used':['source_pu','event objects','future rows','future fault/clearance timing'],'i_alpha_beta_A':vv(i_meas).tolist(),'Vdc_V':vdc0,'PCC_voltage_alpha_beta_V':vv(vp_meas).tolist(),'source_phasor_reconstructed_from_current_measurements_V':vv(e_est).tolist(),'source_magnitude_V':abs(e_est),'measured_source_phase_rad':theta,'aligned_initial_s0':s0.tolist(),'nominal_input_aligned_mnom':mnom.tolist(),'sensor_scope':'Exact synthetic-model observations; no commercial interface or noise robustness validated.'},'first_hold':holds,'contracts':results,'proof_gaps':['DC/SoC not included in the invariant state; current and modulation conclusions are conditional on Vdc staying in the declared physical interval','No hardware sensor/parameter uncertainty or grid frequency/phase-jump coverage under structured contract','Double precision residual checks are not a machine-verified transcendental interval proof','No closed-loop implementation, backup timing test,100us runtime deployment test or six model scenarios executed','SLSQP failure alone is not an emptiness or physical-impossibility proof']}
(OUT/'GATE0_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'first_hold':[{k:v for k,v in r.items() if k not in ['time_grid_s','structured_node_bounds_pu','broad_witness_projection_lower_pu']} for r in holds],'contracts':[{k:r[k] for k in ['contract','disturbance_radius_current_pu','Omega_current_radius_pu','tightened_nominal_input_radius','terminal_set_nonempty_and_constraint_compatible_conditional','terminal_current_continuous_bound_pu','terminal_modulation_bound','solver','first_input_difference_norm','wall_time_s']} for r in results]},indent=2))
