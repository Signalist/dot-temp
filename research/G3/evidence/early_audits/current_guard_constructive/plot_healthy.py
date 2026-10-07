"""Plot saved frozen model evidence only. No integration or optimization."""
from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','.cache/g3_mpl_cache');os.environ.setdefault('XDG_CACHE_HOME','.cache/g3_xdg_cache')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path(__file__).resolve().parent;out=R/'results'
fig,axes=plt.subplots(3,2,figsize=(12,10),constrained_layout=True)
loaded=[]
for cid,color in [('P0-fast','tab:blue'),('R0-fast','tab:orange')]:
 p=out/f'{cid}_h1e-05.json'
 if not p.exists():continue
 s=json.loads(p.read_text());z=np.load(out/s['trace_file']);a=z['endpoint_trace'];de=z['dense_trace'];ct=z['control'];data=np.vstack([a,de]) if len(de) else a;data=data[np.argsort(data[:,0],kind='stable')];t=data[:,0]-.6;label=f"{cid}: {s['stop_reason']}";loaded.append(cid)
 for ax,ys in [(axes[0,0],data[:,14]),(axes[0,1],data[:,15]),(axes[1,0],data[:,16]/1000),(axes[1,1],data[:,17]/1000),(axes[2,1],data[:,25])]:ax.plot(t,ys,color=color,lw=1.1,label=label)
 if len(ct):axes[2,0].plot(ct[:,0]-.6,ct[:,-1],color=color,lw=1.1,label=label)
for ax,y,title,unit in [(axes[0,0],1,'Actual current','pu'),(axes[0,1],1.1,'DC link','pu'),(axes[1,0],800,'PCC active power','kW'),(axes[1,1],700,'PCC reactive power','kvar'),(axes[2,1],60,'PLL frequency','Hz')]:
 ax.axhline(y,color='black',ls='--',lw=.8,label='hard limit' if title in ['Actual current','DC link'] else 'nominal request/reference');ax.set_title(title);ax.set_ylabel(unit)
axes[0,1].axhline(.8,color='black',ls='--',lw=.8)
axes[2,0].set_title('New modulation change from original PI');axes[2,0].set_ylabel('norm (dimensionless)')
for ax in axes.flat:ax.set_xlabel('Time since fixed checkpoint (s)');ax.grid(alpha=.25);ax.legend(fontsize=7)
fig.suptitle('Standard allocations plus the same guard: healthy response and service cost\nSame hypothetical fast DC port; offline clock; no real-time or joint-invariance certification\nAfter first 5 ms: 100-us endpoint snapshots; reported means use continuous quadratures',fontsize=11)
if not loaded:raise RuntimeError('No completed model record available')
fig.savefig(R/'CONSTRUCTIVE_HEALTHY_RESPONSE.png',dpi=150)
fig2,axs=plt.subplots(2,2,figsize=(11,7),constrained_layout=True)
for cid,color in [('P0-fast','tab:blue'),('R0-fast','tab:orange')]:
 p=out/f'{cid}_h1e-05.json'
 if not p.exists():continue
 s=json.loads(p.read_text());z=np.load(out/s['trace_file']);a=z['dense_trace'];a=a[(a[:,0]>=.6)&(a[:,0]<=.605+1e-12)]
 for ax,y in [(axs[0,0],a[:,14]),(axs[0,1],a[:,15]),(axs[1,0],a[:,16]/1000),(axs[1,1],a[:,17]/1000)]:ax.plot((a[:,0]-.6)*1000,y,lw=1.3,color=color,label=cid)
for ax,title,unit,line in [(axs[0,0],'Actual current','pu',1),(axs[0,1],'DC link','pu',1.1),(axs[1,0],'PCC active power','kW',800),(axs[1,1],'PCC reactive power','kvar',700)]:ax.set_title(title);ax.set_ylabel(unit);ax.set_xlabel('First 5 ms after fixed checkpoint');ax.axhline(line,color='black',ls='--',lw=.8);ax.grid(alpha=.25);ax.legend()
fig2.suptitle('Healthy insertion transient; initial modulation change 0.214580692 retained',fontsize=12)
fig2.savefig(R/'CONSTRUCTIVE_INSERTION_TRANSIENT.png',dpi=150)
print(json.dumps({'plotted_cases':loaded,'files':['CONSTRUCTIVE_HEALTHY_RESPONSE.png','CONSTRUCTIVE_INSERTION_TRANSIENT.png']}))
