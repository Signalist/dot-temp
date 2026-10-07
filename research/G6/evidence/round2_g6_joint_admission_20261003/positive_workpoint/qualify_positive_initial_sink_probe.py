"""Original positive-compute operating point qualification; prior files read-only."""
from pathlib import Path
import os,sys,json,hashlib,logging,time
os.environ['OPENBLAS_NUM_THREADS']='1';sys.dont_write_bytecode=True
from grid_adapter import *
from scipy import linalg
logging.basicConfig(level=logging.WARNING)
OUT=Path(__file__).resolve().parent

def save(name,x): (OUT/name).write_text(json.dumps(x,indent=2,default=lambda y:y.tolist() if hasattr(y,'tolist') else str(y),allow_nan=False))
def arr(s,m,ks):
 z=getattr(s,m);return {k:np.asarray(getattr(z,k).v).tolist() for k in ks if hasattr(z,k)}
def workpoint(s):
 return {'Slack':arr(s,'Slack',['idx','bus','p0','q0','p','q','v0']),'PV':arr(s,'PV',['idx','bus','p0','q0','p','q','v0']),'GENROU':arr(s,'GENROU',['idx','bus','M','p0','q0','Pe','Qe','tm','Sn']),'TGOV1':arr(s,'TGOV1',['idx','pref0','paux0','pout']),'Bus':arr(s,'Bus',['idx','a','v']),'PQ':arr(s,'PQ',['idx','bus','p0','q0','u']),'ZIP':arr(s,'ZIP',['idx','pq','pp0','qp0','kpp','kqp'])}

def main():
 base=build('kundur',buses=[7,8],dt=1/128,tf=10,baseline_MW=[0,0],baseline_Mvar=[0,0]);old=workpoint(base);del base
 s=build('kundur',buses=[7,8],dt=1/128,tf=10,baseline_MW=[50,50],baseline_Mvar=[0,0]);d={'freeze_sha256':hashlib.sha256((OUT/'POSITIVE_WORKPOINT_FREEZE.json').read_bytes()).hexdigest(),'metadata':s._transfer_metadata,'old_zero_compute_workpoint':old,'positive_compute_workpoint':workpoint(s),'powerflow_converged':bool(s.PFlow.converged),'tds_initialized':bool(s.TDS.test_ok),'dimensions':[s.dae.n,s.dae.m]}
 save('qualification_in_progress.json',d)
 K,mass,G=descriptor(s);n=s.dae.n; sparse.save_npz(OUT/'positive_descriptor_K.npz',K);np.savez_compressed(OUT/'positive_descriptor_aux.npz',mass=mass,G=G,x0=s._transfer_x0,y0=s._transfer_y0,x_names=np.asarray(s.dae.x_name),y_names=np.asarray(s.dae.y_name))
 d['new_reduced_export']=export_kundur_reduced(s,OUT/'positive_reduced51.npz')
 new=np.load(OUT/'positive_reduced51.npz');prev=np.load(OUT.parents[1]/'round2_20261003/grid_transfer/kundur_reduced51.npz');d['changed_model_check']={'max_abs_A_change':float(abs(new['A']-prev['A']).max()),'relative_Frobenius_A_change':float(np.linalg.norm(new['A']-prev['A'])/np.linalg.norm(prev['A'])),'max_abs_B_change':float(abs(new['B']-prev['B']).max()),'A_sha256':hashlib.sha256(new['A'].tobytes()).hexdigest(),'old_A_sha256':hashlib.sha256(prev['A'].tobytes()).hexdigest()}
 x0=s.dae.x.copy();y0=s.dae.y.copy();rng=np.random.default_rng(2601003);z=rng.normal(size=len(mass));z/=np.linalg.norm(z);u=np.array([1.,0.,-0.7,0.]);d['central_difference_checks']=[]
 def fg(dx,dy,pu):
  s.dae.x[:]=x0+dx;s.dae.y[:]=y0+dy;s.vars_to_models();s.ZIP.pp0.v[s._transfer_ports]=(np.array([50.,50.])+pu[::2])/s.config.mva;s.ZIP.qp0.v[s._transfer_ports]=pu[1::2]/s.config.mva;s.TDS.fg_update(s.exist.pflow_tds);return s.dae.fg.copy()
 for tag,zz,uu in [('mixed_state',z,np.zeros(4)),('P_bus7',z*0,np.array([1.,0,0,0])),('P_bus8',z*0,np.array([0.,0,1.,0])),('mixed_state_and_P',z,u)]:
  for h in [1e-5,1e-6,1e-7]:
   central=(fg(h*zz[:n],h*zz[n:],h*uu)-fg(-h*zz[:n],-h*zz[n:],-h*uu))/(2*h);exact=K@zz+G@uu;d['central_difference_checks'].append({'direction':tag,'step':h,'max_abs_error':float(abs(central-exact).max()),'relative_L2_error':float(np.linalg.norm(central-exact)/np.linalg.norm(exact))})
 fg(np.zeros(n),np.zeros(len(mass)-n),np.zeros(4));s.j_update(s.exist.pflow_tds)
 ok=bool(s.TDS.run());o=extract(s);d['stationarity']={'run_return':ok,'busted':bool(s.TDS.busted),'end_time_s':float(s.dae.t),'max_abs_dx':float(abs(o['x_deviation']).max()),'max_abs_dy':float(abs(o['y_deviation']).max()),'max_abs_frequency_Hz':float(abs(o['frequency_deviation_Hz']).max()),'bus_voltage_range_pu':[float(o['bus_voltage_pu'].min()),float(o['bus_voltage_pu'].max())]};np.savez_compressed(OUT/'positive_stationarity.npz',**o)
 A=new['A'];B=new['B'][:,[0,2]];C=new['C_frequency_Hz'];lam,V=linalg.eig(A);be=linalg.solve(V,B);R=np.einsum('om,mi->omi',C@V,be);checks=[]
 for zz in [.01+.1j,.1+.5j,1+2j,10+10j,100+100j,1000+100j]:
  aa=np.einsum('omi,m->oi',R,1/(zz-lam));bb=C@linalg.solve(zz*np.eye(len(A))-A,B);checks.append(float(np.linalg.norm(aa-bb)/np.linalg.norm(bb)))
 d['transfer']={'max_eigenvalue_real':float(lam.real.max()),'eigenvector_condition':float(np.linalg.cond(V)),'max_resolvent_relative_error':max(checks),'frequency_direct_feedthrough':0,'fresh_linearization':True};np.savez_compressed(OUT/'positive_kernel.npz',lam=lam,R=R,A=A,B=B,C=C)
 save('qualification_in_progress.json',d)
 d['small_P_pulse_checks']=[]
 for port in [0,1]:
  for amp in [.1,.05]:
   s=build('kundur',buses=[7,8],dt=1/128,tf=6,baseline_MW=[50,50],baseline_Mvar=[0,0]);sc=np.zeros((3,5));sc[:,0]=[0,1,2];sc[1,1+2*port]=amp;install_schedule(s,sc,event_epsilon=1e-4);ok=bool(s.TDS.run());o=extract(s);z=linear_trace(s,K,mass,G,o['t'],sc);lf=z[:,s.GENROU.omega.a]*s.config.freq;freq=o['frequency_deviation_Hz'];lv=z[:,n+s.Bus.v.a];vol=o['bus_voltage_pu']-s._transfer_y0[s.Bus.v.a];r={'bus':[7,8][port],'amplitude_MW':amp,'tds_return':ok,'end_time_s':float(s.dae.t),'frequency_peak_Hz':float(abs(freq).max()),'frequency_Linf_error_Hz':float(abs(freq-lf).max()),'frequency_relative_L2_error':float(np.linalg.norm(freq-lf)/np.linalg.norm(lf)),'voltage_relative_L2_error':float(np.linalg.norm(vol-lv)/np.linalg.norm(lv))};d['small_P_pulse_checks'].append(r);np.savez_compressed(OUT/f'pulse_bus{r["bus"]}_{amp}.npz',t=o['t'],frequency_Hz=freq,linear_frequency_Hz=lf,voltage_deviation_pu=vol,linear_voltage_deviation_pu=lv,schedule=sc);print('PULSE',r,flush=True)
 d['qualification_pass']=bool(d['powerflow_converged'] and d['tds_initialized'] and max(d['metadata']['initial_f_max'],d['metadata']['initial_g_max'])<1e-8 and d['stationarity']['max_abs_dx']<1e-8 and d['stationarity']['max_abs_dy']<1e-8 and lam.real.max()<0 and max(checks)<1e-8 and max(x['relative_L2_error'] for x in d['central_difference_checks'])<1e-4 and max(x['frequency_relative_L2_error'] for x in d['small_P_pulse_checks'])<.01)
 save('QUALIFICATION.json',d);print('QUALIFICATION_PASS',d['qualification_pass'],d['transfer'],d['stationarity'],flush=True)
 if not d['qualification_pass']:raise RuntimeError('Positive operating point did not pass frozen qualification; no retune')
if __name__=='__main__':main()
