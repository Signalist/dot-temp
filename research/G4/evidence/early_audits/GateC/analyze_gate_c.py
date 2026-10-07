from pathlib import Path
import json,numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).parent;d=pd.read_csv(P/'per_cycle_harmonics.csv')
fig,axs=plt.subplots(1,3,figsize=(12,3.8),layout='constrained')
for a,cr in zip(axs,[.5,2,20]):
 q=d[d['case']==f'f0.5_cap{cr:g}'];a.plot(q.cycle+1,q.low_start_harmonic_MW,label='Low initial energy',color='#B6523E');a.plot(q.cycle+1,q.high_start_harmonic_MW,label='High initial energy',color='#227A8F')
 a.axhline(.5,color='#333333',ls='--',lw=1,label='0.5 MW class threshold');a.set_xscale('log');a.set_title(f'Capacity / cycle energy = {cr:g}');a.set_xlabel('Cycle number (log scale)');a.set_ylabel('PCC fundamental peak (MW)');a.grid(alpha=.2)
axs[0].legend(fontsize=8);fig.suptitle('Initial energy changes finite-window source classes; persistent separation is not supported',fontsize=12)
fig.savefig(P/'gate_c_source_classes.png',dpi=170)
q=np.load(P/'traces'/'f0.5_cap20.npz');mask=q['time_s']<=10;t=q['time_s'][mask];E=q['energy_MWs'][mask];v=q['PCC_MW'][mask];u=q['load_MW'][mask];y=q['PMU_Hz'][mask];yb=q['PMU_swapped_Hz'][mask]
meta=next(m for m in json.loads((P/'GATE_C_RESULTS.json').read_text())['physical_cases'] if m['frequency_Hz']==.5 and m['cap_ratio']==20)
fig,axs=plt.subplots(3,1,figsize=(10,7.2),layout='constrained',sharex=True)
axs[0].plot(t,u,'--',color='#999999',lw=1,label='Same job load at both sites');axs[0].plot(t,v[:,0],color='#B6523E',label='Low-energy site');axs[0].plot(t,v[:,1],color='#227A8F',label='High-energy site');axs[0].set_ylabel('Power (MW)');axs[0].legend(ncol=3,fontsize=8)
axs[1].plot(t,E[:,0]/meta['capacity_MWs'],color='#B6523E');axs[1].plot(t,E[:,1]/meta['capacity_MWs'],color='#227A8F');axs[1].axhline(.1,color='#333333',ls='--',lw=1);axs[1].set_ylabel('Energy / capacity');axs[1].text(.02,.86,'States evolve continuously; no cycle resets',transform=axs[1].transAxes,fontsize=9)
axs[2].plot(t,y[:,0]*1000,color='#222222',label='World A, PMU 0');axs[2].plot(t,yb[:,0]*1000,'--',color='#DAAA39',label='Swapped initial states, PMU 0');axs[2].set_ylabel('Frequency deviation (mHz)');axs[2].set_xlabel('Time (s)');axs[2].legend(fontsize=8)
for a in axs:a.grid(alpha=.2)
fig.suptitle('Continuous two-site witness: different PCC exposure, indistinguishable remote measurements',fontsize=12)
fig.savefig(P/'gate_c_continuous_witness.png',dpi=170)
# Compute energy-gap accounting with a stated quadrature error, preserving all cases.
rows=[]
for m in json.loads((P/'GATE_C_RESULTS.json').read_text())['physical_cases']:
 tag=f"f{m['frequency_Hz']:g}_cap{m['cap_ratio']:g}";q=np.load(P/'traces'/(tag+'.npz'));t=q['time_s'];delta=q['PCC_MW'][:,0]-q['PCC_MW'][:,1]
 rows.append(dict(case=tag,pcc_difference_L1_MWs=float(np.trapezoid(abs(delta),t)),initial_energy_gap_bound_MWs=m['state_gap_initial_MWs']/.95,
  max_negative_PCC_order_violation_MW=float(min(0,delta.min()))))
pd.DataFrame(rows).to_csv(P/'energy_gap_accounting.csv',index=False)
