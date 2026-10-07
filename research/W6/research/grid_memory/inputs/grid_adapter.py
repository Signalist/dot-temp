"""Reproducible supplemental constant-power ports; official ANDES cases untouched.
Units: t[s], positive P[MW]/Q[Mvar] = added consumption, base = case MVA.
Original PQ loads retain ANDES default constant-impedance dynamic conversion.
"""
import os,pathlib,hashlib,json
from collections import OrderedDict
ROOT=pathlib.Path(__file__).resolve().parent
os.environ['HOME']=str(ROOT/'home');os.environ['MPLCONFIGDIR']=str(ROOT/'home/mpl')
import andes,numpy as np
from andes.shared import matrix
from scipy import sparse
from scipy.sparse.linalg import splu
from scipy.linalg import solve
CASES={'kundur':'kundur/kundur_full.xlsx','npcc':'npcc/npcc.xlsx','wecc':'wecc/wecc_full.xlsx','wecc_gencls':'wecc/wecc_gencls.xlsx'}
DEFAULT_BUSES={'kundur':[7,8],'npcc':[6,11],'wecc':[1,4],'wecc_gencls':[1,4]}

def build(slug,buses=None,dt=.01,tf=10.,baseline_MW=None,baseline_Mvar=None):
 buses=DEFAULT_BUSES[slug] if buses is None else list(buses)
 path=pathlib.Path(andes.get_case(CASES[slug]));s=andes.load(str(path),setup=False,no_output=True,default_config=True)
 orig_events={name:m.as_df().to_dict(orient='records') for name,m in s.models.items() if name in ('Toggle','Fault','Alter') and m.n}
 orig={name:m.as_df().copy() for name,m in s.models.items() if m.n}
 S=float(s.config.mva);basep=np.zeros(len(buses)) if baseline_MW is None else np.asarray(baseline_MW);baseq=np.zeros(len(buses)) if baseline_Mvar is None else np.asarray(baseline_Mvar)
 ports=[]
 for j,bus in enumerate(buses):
  uid=s.Bus.idx2uid(bus);pq=f'TRANSFER_PQ_{j}';z=f'TRANSFER_ZIP_{j}'
  s.add('PQ',dict(idx=pq,bus=bus,Vn=s.Bus.Vn.v[uid],p0=basep[j]/S,q0=baseq[j]/S))
  s.add('ZIP',dict(idx=z,pq=pq,kpp=100,kpi=0,kpz=0,kqp=100,kqi=0,kqz=0));ports.append(z)
 s.setup()
 for name in ('Toggle','Fault','Alter'):
  m=getattr(s,name)
  if m.n:
   m.u.v[:]=0
   if hasattr(m,'t'):m.t.v[:]=1e6
 s.PFlow.config.tol=1e-11
 if not s.PFlow.run():raise RuntimeError('Power flow failed')
 s.TDS.config.tol=1e-10;s.TDS.config.reset_tiny=0;s.TDS.config.no_tqdm=1;s.TDS.config.tstep=dt;s.TDS.config.tf=tf;s.TDS.config.fixt=1;s.TDS.config.shrinkt=1
 s.TDS.init()
 if not s.TDS.test_ok:raise RuntimeError('TDS initialization failed')
 s._transfer_ports=np.array(s.ZIP.idx2uid(ports));s._transfer_buses=buses;s._transfer_x0=s.dae.x.copy();s._transfer_y0=s.dae.y.copy();s._transfer_basep=basep;s._transfer_baseq=baseq
 s._transfer_metadata={'andes_version':andes.__version__,'source_case':CASES[slug],'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'variant':'original-parameters_no-demo-events_supplemental-ZIP-constant-PQ-ports','disabled_original_events':orig_events,'port_buses':buses,'base_MVA':S,'frequency_Hz':float(s.config.freq),'baseline_port_MW':basep.tolist(),'baseline_port_Mvar':baseq.tolist(),'original_PQ_TDS_conversion':{k:getattr(s.PQ.config,k) for k in ('p2p','p2i','p2z','q2q','q2i','q2z')},'port_original_PQ_status_after_dynamic_replacement':[float(s.PQ.u.v[s.PQ.idx2uid(f'TRANSFER_PQ_{j}')]) for j in range(len(buses))],'initial_f_max':float(max(abs(s.dae.f))),'initial_g_max':float(max(abs(s.dae.g))),'original_model_parameters_modified':False,'local_original_P_MW':[float(sum(p for p,b in zip(orig['PQ'].p0,orig['PQ'].bus) if b==bus)*S) for bus in buses]}
 return s

def descriptor(s):
 s.j_update(s.exist.pflow_tds);d=s.dae;n=d.n
 K=sparse.bmat([[np.asarray(matrix(d.fx)),np.asarray(matrix(d.fy))],[np.asarray(matrix(d.gx)),np.asarray(matrix(d.gy))]],format='csc')
 mass=np.r_[d.Tf,np.zeros(d.m)];G=np.zeros((n+d.m,2*len(s._transfer_buses)))
 for j,bus in enumerate(s._transfer_buses):
  uid=s.Bus.idx2uid(bus);G[n+s.Bus.a.a[uid],2*j]=1/s.config.mva;G[n+s.Bus.v.a[uid],2*j+1]=1/s.config.mva
 return K,mass,G

def schedule_value(schedule,t):
 # Rows [time, P0, Q0, P1, Q1, ...], additional MW/Mvar above port baseline.
 i=np.searchsorted(schedule[:,0],float(t)+1e-10,side='right')-1
 return schedule[max(i,0),1:]

def install_schedule(s,schedule,event_epsilon=0.):
 schedule=np.asarray(schedule,float)
 if schedule.ndim!=2 or schedule.shape[1]!=1+2*len(s._transfer_ports):raise ValueError('Expected columns time,P0,Q0,...')
 if schedule[0,0]!=0 or np.any(np.diff(schedule[:,0])<=0):raise ValueError('Schedule must begin at 0 and increase strictly')
 if np.any(schedule[0,1:]!=0):raise ValueError('Initial perturbation must be zero; use baseline_MW/Mvar in build for nonzero steady load')
 # Register exact integration breakpoints, without changing a network device.
 for tt in schedule[1:,0]:
  s.switch_dict[float(tt)]={}
  if event_epsilon>0:
   for off in [-event_epsilon,event_epsilon]:
    if tt+off>0:s.switch_dict[float(tt+off)]={}
 s.switch_dict=OrderedDict(sorted(s.switch_dict.items()));s.switch_times=np.asarray(list(s.switch_dict));s.n_switches=len(s.switch_times)
 def perturb(t,system):
  vals=schedule_value(schedule,t).reshape(-1,2);p=system._transfer_ports
  system.ZIP.pp0.v[p]=(system._transfer_basep+vals[:,0])/system.config.mva
  system.ZIP.qp0.v[p]=(system._transfer_baseq+vals[:,1])/system.config.mva
 s.TDS.callpert=perturb
 return schedule

def extract(s):
 t=s.dae.ts.t;x=s.dae.ts.x;y=s.dae.ts.y
 generators=[m for m in (s.GENROU,s.GENCLS) if m.n];om=np.concatenate([m.omega.a for m in generators]);de=np.concatenate([m.delta.a for m in generators]);weights=np.concatenate([m.M.v for m in generators]);weights/=sum(weights)
 freq=(x[:,om]-1)*s.config.freq;delta=x[:,de]-s._transfer_x0[de];coi=freq@weights
 l=s.Line;v1=y[:,l.v1.a];v2=y[:,l.v2.a];a=y[:,l.a1.a]-y[:,l.a2.a]-l.phi.v
 # Exact active/reactive expression used by installed ANDES Line model.
 p1=l.ue.v*(v1*v1*(l.gh.v+l.ghk.v)*l.itap2.v-v1*v2*(l.ghk.v*np.cos(a)+l.bhk.v*np.sin(a))*l.itap.v)*s.config.mva
 q1=l.ue.v*(-v1*v1*(l.bh.v+l.bhk.v)*l.itap2.v-v1*v2*(l.ghk.v*np.sin(a)-l.bhk.v*np.cos(a))*l.itap.v)*s.config.mva
 out={'t':t,'frequency_deviation_Hz':freq,'coi_frequency_deviation_Hz':coi,'generator_delta_deviation_rad':delta,'relative_delta_rad':delta-delta[:,:1],'bus_voltage_pu':y[:,s.Bus.v.a],'branch_P_from_MW':p1,'branch_Q_from_Mvar':q1,'x_deviation':x-s._transfer_x0,'y_deviation':y-s._transfer_y0,'generator_ids':np.asarray([str(i) for m in generators for i in m.idx.v]),'bus_ids':np.asarray(s.Bus.idx.v),'branch_ids':np.asarray(s.Line.idx.v),'coi_weights':weights}
 return out

def linear_descriptor_trace(K,mass,G,t,schedule):
 # Match ANDES trapezoidal residual: all x rows, including Tf=0, use trapezoid;
 # original algebraic rows g are imposed at the new instant.
 # Derive n from number of rows with mass metadata separately via K/G convention.
 raise NotImplementedError('Use linear_trace(system,...)')

def linear_trace(s,K,mass,G,t,schedule):
 n=s.dae.n;N=len(mass);z=np.zeros(N);out=np.zeros((len(t),N));cache={};nports=G.shape[1]
 Md=sparse.diags(mass);wnew=np.r_[np.full(n,.5),np.ones(s.dae.m)];wold=np.r_[np.full(n,.5),np.zeros(s.dae.m)]
 Wn=sparse.diags(wnew);Wo=sparse.diags(wold)
 for k in range(1,len(t)):
  h=float(t[k]-t[k-1]);key=round(h,12)
  if h<1e-11:out[k]=z;continue
  if key not in cache:
   L=Md-h*Wn@K;R=Md+h*Wo@K;cache[key]=(splu(L.tocsc()),R)
  lu,R=cache[key];un=schedule_value(schedule,t[k]);uo=schedule_value(schedule,t[k-1]);rhs=R@z+h*(wnew*(G@un)+wold*(G@uo));z=lu.solve(rhs);out[k]=z
 return out

def export_kundur_reduced(s,path):
 """Remove uniform rotor-angle gauge only. No machine/controller truncation."""
 if s.dae.n!=52 or np.any(s.dae.Tf==0):raise ValueError('This export is qualified for Kundur full only')
 K,mass,G=descriptor(s);n=s.dae.n;kk=K.toarray();Yx=-solve(kk[n:,n:],kk[n:,:n]);Yu=-solve(kk[n:,n:],G[n:]);A=(kk[:n,:n]+kk[:n,n:]@Yx)/mass[:n,None];B=(G[:n]+kk[:n,n:]@Yu)/mass[:n,None]
 ref=int(s.GENROU.delta.a[-1]);keep=np.delete(np.arange(n),ref);R=np.eye(n)[keep];V=np.eye(n)[:,keep]
 for row,i in enumerate(keep):
  if i in s.GENROU.delta.a:R[row,ref]=-1
 Ar=R@A@V;Br=R@B;C=np.eye(n)[s.GENROU.omega.a]*s.config.freq;Cv=Yx[s.Bus.v.a];Dv=Yu[s.Bus.v.a]
 np.savez_compressed(path,A=Ar,B=Br,C_frequency_Hz=C@V,C_voltage_pu=Cv@V,D_voltage_pu=Dv,coi_weights=s.GENROU.M.v/sum(s.GENROU.M.v),full_A=A,full_B=B,R=R,V=V,state_names=np.asarray(s.dae.x_name)[keep],input_names=np.asarray([f'{q}@bus{b}' for b in s._transfer_buses for q in ('P_MW','Q_Mvar')]),generator_ids=np.asarray(s.GENROU.idx.v),bus_ids=np.asarray(s.Bus.idx.v))
 return {'removed_gauge_state':s.dae.x_name[ref],'dimension':len(keep),'max_real_eigenvalue':float(np.max(np.linalg.eigvals(Ar).real)),'quotient_invariance_residual':float(np.max(abs(R@A-Ar@R)))}

def descriptor_verified(s):
 """Exact chain-rule completion of ESST3A VE VarService for ANALYSIS ONLY.
 Does not modify any ANDES equations, parameters, states, or nonlinear solver.
 See chainrule_audit.json for independent central-difference checks.
 """
 K,mass,G=descriptor(s)
 if s.ESST3A.n:
  e=s.ESST3A;n=s.dae.n;J=K.tolil()
  zz=e.KPC.v*(e.vd.v+1j*e.vq.v)+1j*(e.KI.v+e.KPC.v*e.XL.v)*(e.Id.v+1j*e.Iq.v)
  dz=[e.KPC.v,1j*e.KPC.v,1j*(e.KI.v+e.KPC.v*e.XL.v),-(e.KI.v+e.KPC.v*e.XL.v)]
  for a,d in zip([e.vd.a,e.vq.a,e.Id.a,e.Iq.a],dz):
   dve=np.real(np.conj(zz)*d)/abs(zz)
   for j,col in enumerate(a):
    J[n+e.VB_x.a[j],n+col]+=e.FEX_y.v[j]*dve[j]
    J[n+e.IN.a[j],n+col]+=-e.ue.v[j]*e.IN.v[j]*dve[j]
  K=J.tocsc()
 return K,mass,G

def install_it_zoh_bess_pwl(s,it_rows,bess_rows,event_epsilon=0.):
 """Separate IT right-continuous ZOH and realized BESS PWL injection.
 Both arrays have columns [seconds,P0_MW,Q0_Mvar,...]. BESS sign is positive
 injection, so the supplemental grid demand is IT minus BESS. This wrapper
 contains no PCS/energy equations; those must be verified by its producer.
 """
 it=np.asarray(it_rows,float);be=np.asarray(bess_rows,float);nc=1+2*len(s._transfer_ports)
 for rows in [it,be]:
  if rows.ndim!=2 or rows.shape[1]!=nc or rows[0,0]!=0 or np.any(np.diff(rows[:,0])<=0):raise ValueError('Both schedules require strict increasing timestamps, first0, and correct port count')
  if np.any(rows[0,1:]!=0):raise ValueError('Initial increments must be zero')
 for tt in np.unique(np.r_[it[1:,0],be[1:,0]]):s.switch_dict[float(tt)]={}
 if event_epsilon>0:
  for tt in it[1:,0]:
   for off in [-event_epsilon,event_epsilon]:
    if tt+off>0:s.switch_dict[float(tt+off)]={}
 s.switch_dict=OrderedDict(sorted(s.switch_dict.items()));s.switch_times=np.asarray(list(s.switch_dict));s.n_switches=len(s.switch_times)
 def perturb(t,system):
  ti=float(t);itv=schedule_value(it,ti);bev=np.array([np.interp(ti,be[:,0],be[:,k]) for k in range(1,nc)]);net=(itv-bev).reshape(-1,2);ports=system._transfer_ports
  system.ZIP.pp0.v[ports]=(system._transfer_basep+net[:,0])/system.config.mva
  system.ZIP.qp0.v[ports]=(system._transfer_baseq+net[:,1])/system.config.mva
 s.TDS.callpert=perturb
 return {'it_zoh':it,'bess_realized_pwl':be}
