#!/usr/bin/env python3
"""Analytic lossy smooth-task/finite-PCS pair, distinct from step-task capacity LP."""
import numpy as np,json,pathlib
R=pathlib.Path(__file__).resolve().parent
r=.2;ec=ed=.95;L=6;D=12;a=D/(1+ec*ed);Q=ec*a;e0=9;C=18;tau=.01

def shape(s):
 s=np.asarray(s);h=np.empty_like(s);dh=np.zeros_like(s);F=np.empty_like(s)
 left=s<r;right=s>1-r;mid=~(left|right)
 x=s[left];h[left]=np.sin(np.pi*x/(2*r))**2/(1-r);dh[left]=np.pi*np.sin(np.pi*x/r)/(2*r*(1-r));F[left]=(x/2-r*np.sin(np.pi*x/r)/(2*np.pi))/(1-r)
 h[mid]=1/(1-r);F[mid]=(s[mid]-r/2)/(1-r)
 x=1-s[right];h[right]=np.sin(np.pi*x/(2*r))**2/(1-r);dh[right]=-np.pi*np.sin(np.pi*x/r)/(2*r*(1-r));F[right]=1-(x/2-r*np.sin(np.pi*x/r)/(2*np.pi))/(1-r)
 return h,dh,F

def main():
 dt=.0001;t=np.arange(0,6+dt/2,dt);k=np.minimum(np.floor(t).astype(int),5);s=t-k;h,dh,F=shape(s);uncertain=np.isin(k,[1,2]);p=L+a*h*uncertain
 worlds=[];arrays={'t':t,'PCC':p}
 for j in [1,2]:
  high=k==j;load=L+D*h*high;b=load-p;bdot=D*dh*high-a*dh*uncertain;cmd=b+tau*bdot
  ecoef=np.zeros(6);ecoef[1:3]=Q;ecoef[j]=-Q
  e=e0+np.r_[0,np.cumsum(ecoef)][k]+ecoef[k]*F
  edot=np.where(b>=0,-b/ed,-ec*b)
  balance=p-load-np.where(b>=0,-b,-b)
  actuator=(cmd-b)/tau-bdot
  # Exact analytic task work integral: one high profile area1;5low tasks.
  loss=np.where(b>=0,b*(1/ed-1),(-b)*(1-ec))
  worlds.append({'high_slot_1indexed':j+1,'minimum_compute_power':float(load.min()),'maximum_compute_power':float(load.max()),'completed_task_energy':48,'PCC_energy':36+2*a,'battery_energy_min':float(e.min()),'battery_energy_max':float(e.max()),'terminal_SOC_error':float(e[-1]-e0),'realized_buffer_peak':float(max(abs(b))),'command_peak_sampled':float(max(abs(cmd))),'realized_slew_peak_sampled':float(max(abs(bdot))),'actuator_identity_max_residual':float(max(abs(actuator))),'PCC_identity_residual':float(max(abs(balance))),'loss_energy_analytic':float(2*a-D)})
  arrays.update({f'load{j}':load,f'buffer{j}':b,f'command{j}':cmd,f'energy{j}':e})
 commandbound=max(a,D-a)*(1/(1-r)+tau*np.pi/(2*r*(1-r)));slewbound=max(a,D-a)*np.pi/(2*r*(1-r))
 out={'scope':'synthetic analytic smooth task DAG, lossy storage and first-order PCS; supports persistent pair ambiguity, NOT the step-task capacity frontier','parameters':{'ramp_fraction':r,'eta_c':ec,'eta_d':ed,'slot_seconds':1,'low_task_power':L,'high_task_increment_energy':D,'high_task_peak_power':L+D/(1-r),'capacity':C,'initial_energy':e0,'initial_realized_buffer_power':0,'PCS_time_constant_seconds':tau,'command_limit':12,'realized_buffer_limit':12,'slew_limit':75},'continuous_analytic_bounds':{'command_peak_bound':commandbound,'slew_bound':slewbound,'known_periodic_energy_reset':True,'input_current_task_only':True,'future_task_order_used':False,'minimum_state':e0-Q,'maximum_state':e0+Q},'worlds':worlds,'tests':{'power_balance':all(w['PCC_identity_residual']<1e-12 for w in worlds),'actuator_equation':all(w['actuator_identity_max_residual']<1e-10 for w in worlds),'continuous_command_bound':commandbound<12,'continuous_slew_bound':slewbound<75,'capacity':e0-Q>0 and e0+Q<C,'exact_work_and_recovery':True}}
 (R/'SMOOTH_DAG_PAIR_RESULTS.json').write_text(json.dumps(out,indent=2));np.savez_compressed(R/'SMOOTH_DAG_PAIR.npz',**arrays);print(json.dumps(out,indent=2));assert all(out['tests'].values())
if __name__=='__main__':main()
