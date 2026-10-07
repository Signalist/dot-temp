from pathlib import Path
import json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150})
fig,ax=plt.subplots(1,2,figsize=(11,4.2))
ax[0].plot([808,834.414530875619],[1,1],lw=8,color='#8ca2b5',solid_capstyle='butt',label='Previous ideal-average bracket')
ax[0].plot([808,812.5],[0,0],lw=8,color='#207e77',solid_capstyle='butt',label='New outward-checked bracket')
ax[0].scatter([808,808],[1,0],s=65,color='#145952',zorder=3)
ax[0].scatter([834.414530875619,812.5],[1,0],s=75,marker='x',color='#b34735',zorder=3)
ax[0].set(yticks=[0,1],yticklabels=['Prefix-coupled','Previous'],xlabel='Reactive floor amplitude (kvar)',xlim=(805,837),ylim=(-.7,1.6),title='Same 100 kW / 100 J averaged contract')
ax[0].text(808,-.32,'808 feasible',ha='center',fontsize=9)
ax[0].text(817.3,-.49,'812.5 and above excluded',ha='center',fontsize=9)
ax[0].text(822,.38,'83.0% narrower bound gap',ha='center')
rows=json.loads((ROOT/'results'/'zoh_inner_results.json').read_text());vals=[r['sigma_kJ']*1000 for r in rows]
ax[1].bar(['25 us','50 us','100 us'],vals,color=['#207e77','#bd6b52','#bd6b52'])
ax[1].axhline(0,color='black',lw=.8);ax[1].set_ylim(-20,4);ax[1].set(ylabel='Optimized inward energy margin (J)',title='Held battery commands at 808 kvar')
for i,v in enumerate(vals):ax[1].text(i,v+(.6 if v>0 else -.6),f'{v:.3f}',ha='center',va='bottom' if v>0 else 'top')
ax[1].text(.03,.04,'Negative bars: unsuccessful fixed-path inner attempts\nNot all-allocation impossibility',transform=ax[1].transAxes,fontsize=8)
fig.tight_layout();fig.savefig(ROOT/'figures'/'admission_and_hold_margin.png');plt.close(fig)
tr=np.loadtxt(ROOT/'results'/'zoh_certified_trace.csv',delimiter=',',skiprows=1);z=np.load(ROOT/'results'/'zoh_q808_h25.npz');t=z['t']
fig,axs=plt.subplots(3,1,figsize=(10,8),sharex=True)
axs[0].plot(t*1000,z['d'],label='Common workload d');axs[0].plot(t*1000,z['p'],label='Service grid P');axs[0].plot(t*1000,z['q'],label='Service Q');axs[0].set(ylabel='kW / kvar',title='One fixed workload and exact averaged recovery');axs[0].legend(ncol=3,frameon=False)
axs[1].plot(tr[:,0]*1000,tr[:,1],label='Buffer b');axs[1].step(t[:-1]*1000,z['u'],where='post',alpha=.55,label='Held u (raw LP, visually indistinguishable from repair)');axs[1].set(ylabel='kW');axs[1].legend(frameon=False,fontsize=8)
axs[2].plot(tr[:,0]*1000,tr[:,3],label='DC energy W');axs[2].axhline(17.496,color='#b34735',ls='--',lw=1);axs[2].axhline(26.136,color='#b34735',ls='--',lw=1);axs[2].set(xlabel='Time (ms)',ylabel='kJ');axs[2].legend(frameon=False)
for a in axs:a.grid(alpha=.2)
fig.tight_layout();fig.savefig(ROOT/'figures'/'same_contract_zoh_recovery.png');plt.close(fig)
