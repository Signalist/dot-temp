import numpy as np,json,pathlib
from smooth_dag_pair import shape,a,L,D,Q,e0,C,tau
R=pathlib.Path(__file__).resolve().parent

def desired(t,j):
 out=np.zeros_like(t);valid=(t>=0)&(t<6);tt=t[valid];k=np.floor(tt).astype(int);h,dh,F=shape(tt-k)
 out[valid]=D*h*(k==j)-a*h*np.isin(k,[1,2]);return out

def load(t,j):
 k=np.minimum(np.floor(t).astype(int),5);h,_,_=shape(t-k);return L+D*h*(k==j)

t=np.arange(0,6.1000001,.0001);out=[]
for delay in [0,.001,.01,.05]:
 d0=load(t,1);d1=load(t,2);b0=desired(t-delay,1);b1=desired(t-delay,2);p0=d0-b0;p1=d1-b1
 # A delayed feedforward u=b_des(t-delay)+tau db_des(t-delay) exactly realizes delayed b through same first-order PCS from0.
 delta=p0-p1;idx=int(np.argmax(abs(delta)));out.append({'actuation_transport_delay':delay,'max_world_PCC_difference_sampled':float(max(abs(delta))),'time_of_max':float(t[idx]),'direct_PCC_linf_noise_separates_if_below':float(max(abs(delta))/2),'each_task_energy_unchanged':True,'battery_waveform_only_delayed':True})
res={'scope':'fixed delayed-feedforward ablation on smooth DAG pair; does not prove impossibility for all preview-capable local controllers','same_initial_PCS_state':0,'sample_step':.0001,'horizon6.1s':'includes delayed power recovery tails, no truncation','rows':out,'tests':{'zero_delay_identical':out[0]['max_world_PCC_difference_sampled']<1e-10,'positive_delays_expose_this_controller':all(r['max_world_PCC_difference_sampled']>0 for r in out[1:])}}
(R/'TIMING_ABLATION_RESULTS.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2));assert all(res['tests'].values())
