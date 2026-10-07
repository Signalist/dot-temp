#!/usr/bin/env python3
"""Exact task-DAG equivalence and a targeted SOC measurement certificate.
All quantities synthetic; task power is an abstract work-energy contract.
"""
import json,itertools,pathlib
import numpy as np
R=pathlib.Path(__file__).resolve().parent
NAMES=['A','B','H','D','E','F'];POWER={x:(18 if x=='H' else 6) for x in NAMES}
DAGS={'all_orders':[], 'wide_partial_order':[('A','H'),('H','F')], 'diamond':[('A','B'),('A','H'),('B','D'),('H','D'),('D','E'),('E','F')], 'fully_serial':list(zip(NAMES[:-1],NAMES[1:]))}

def topological(edges):
 return [p for p in itertools.permutations(NAMES) if all(p.index(a)<p.index(b) for a,b in edges)]
def phi(z,ec=.95,ed=.95):return np.where(z>=0,ec*z,z/ed)
def main():
 ec=ed=.95;C=18;e0=9;rho=ec*ed;L=6;H=18;Rmax=12
 q=(H+rho*L)/(1+rho);Q=ec*(q-L)
 p=np.array([6,q,q,6,6,6]);dag=[]
 for name,edges in DAGS.items():
  orders=topological(edges);powerseq=sorted(set(tuple(POWER[t] for t in o) for o in orders))
  entries=[]
  for d in powerseq:
   d=np.array(d);e=e0+np.r_[0,np.cumsum(phi(p-d))]
   entries.append({'high_slot_1indexed':int(np.argmax(d)+1),'task_power':d.tolist(),'state':e.tolist(),'recovery_error':float(e[-1]-e0),'within_capacity':bool(e.min()>=0 and e.max()<=C),'battery_ac_peak':float(max(abs(p-d))),'consistent_exact_recovery':bool(abs(e[-1]-e0)<1e-9 and e.min()>=0 and e.max()<=C)})
  dag.append({'name':name,'edges':edges,'number_topological_task_orders':len(orders),'number_distinct_power_orders':len(powerseq),'task_orders':[list(z) for z in orders] if len(orders)<=6 else None,'power_worlds':entries,'residual_power_equivalence_class':[x['high_slot_1indexed'] for x in entries if x['consistent_exact_recovery']]})
 orders=topological(DAGS['diamond']);ds=sorted([np.array([POWER[t] for t in o]) for o in orders],key=lambda d:int(np.argmax(d)))
 one=[e0+np.r_[0,np.cumsum(phi(p-d))] for d in ds]
 # Repeat actual increments 1000 times, never set e=e0 at block edges.
 reps=[]
 for d in ds:
  state=e0+np.r_[0,np.cumsum(np.tile(phi(p-d),1000))]
  reps.append({'min':float(state.min()),'max':float(state.max()),'max_checkpoint_error':float(max(abs(state[::6]-e0))),'completed_jobs':6000,'compute_task_energy':48000.,'grid_energy':float(1000*sum(p))})
 # Two sites swap the two DAG-admissible orders. Site-labelled PCCs stay equal.
 ea,eb=one;Eobs1=[float(ea[2]),float(eb[2])];Eobs2=Eobs1[::-1]
 epsE=.1;clock=.01;totalEerror=epsE+max(abs(phi(p-ds[0])).max(),abs(phi(p-ds[1])).max())*clock
 out={'scope':'abstract positive-work DAG and two-world source-of-high-task label; NOT exposed-PCC-source label or AI label','contract':{'task_energy':POWER,'task_duration_seconds':1,'task_count':6,'task_work_energy_total':48,'all_tasks_completed_within_seconds':6,'eta_c':ec,'eta_d':ed,'capacity':C,'known_initial_energy':e0,'ac_charge_and_discharge_limit':Rmax,'PCC_schedule':p.tolist(),'qpair':q,'Qpair':Q,'controller':'p is public clock schedule; local realized battery observes current load and uses p-d; no future private task order','grid_worlds':'same physical grid, initial state, all nodal P/Q histories and measurement kernels; task order only swaps at two candidate sites'},'dags':dag,'continuous_1000block_check':reps,'source_label':{'world1':'site A high task at slot2','world2':'site B high task at slot2','PCC_source_label_both_worlds':'same two site-resolved PCC traces; no different exposed electrical source','same_total_task_work':True},'measurement_increment':{'identical_complete_labelled_PCC':True,'identical_total_buffer_energy_trace':bool(np.max(abs((ea+eb)-2*e0))<1e-9),'identical_block_end_SOC':True,'siteA_SOC_after_slot2_worlds':[Eobs1[0],Eobs2[0]],'SOC_threshold':e0,'energy_sensor_error':epsE,'time_error_seconds':clock,'total_energy_error_allowance':float(totalEerror),'robust_bit_margin':float(Q-totalEerror),'site_label_required':True,'cost_superiority_claim':False},'equivalence_size_under_exact_recovery':{'single_block_all_order_observer':2,'K_blocks':'2^K distinct task power histories remain compatible with the complete PCC trace','two_site_swapped_label':'two physically different source-of-high-task worlds remain compatible forever'},'tests':{}}
 tests={'diamond_has2_orders':len(orders)==2,'all_work_positive':all(min(d)>0 for d in ds),'same_work_energy':all(sum(d)==48 for d in ds),'power_limit':all(max(abs(p-d))<=Rmax for d in ds),'1000block_soc':all(x['min']>=0 and x['max']<=C and x['max_checkpoint_error']<1e-8 for x in reps),'same_aggregate_energy':out['measurement_increment']['identical_total_buffer_energy_trace'],'SOC_bit_robust':Q>totalEerror,'allorder_residual_exact_class_2':len(dag[0]['residual_power_equivalence_class'])==2}
 tests={k:bool(v) for k,v in tests.items()};out['tests']=tests;(R/'DAG_EQUIVALENCE_RESULTS.json').write_text(json.dumps(out,indent=2));np.savez_compressed(R/'DAG_PAIR_WITNESS.npz',p=p,d0=ds[0],d1=ds[1],energy0=ea,energy1=eb)
 print(json.dumps({'tests':tests,'q':q,'Q':Q,'dags':[(d['name'],d['number_topological_task_orders'],d['number_distinct_power_orders'],d['residual_power_equivalence_class']) for d in dag],'measurement':out['measurement_increment']},indent=2));assert all(tests.values())
if __name__=='__main__':main()
