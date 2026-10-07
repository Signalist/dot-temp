"""Plot existing constructive fault evidence only, without extrapolating early stops."""
from pathlib import Path
import os,json
os.environ.setdefault('MPLCONFIGDIR','.cache/g3_mpl_cache');os.environ.setdefault('XDG_CACHE_HOME','.cache/g3_xdg_cache')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path(__file__).resolve().parent;O=R/'results';fig,axes=plt.subplots(3,2,figsize=(12,9),constrained_layout=True);found=[]
for cid,col in [('P50-fast','tab:blue'),('R50-fast','tab:orange')]:
 p=O/f'{cid}_h1e-05.json'
 if not p.exists():continue
 d=json.loads(p.read_text());z=np.load(O/d['trace_file']);a=z['dense_trace'];a=a[(a[:,0]-.60005)<=.20000001];ct=z['control'];ct=ct[(ct[:,0]-.60005)<=.20000001];label=f"{cid}: {d['stop_reason']}";t=(a[:,0]-.60005)*1000;found.append(cid)
 for ax,y in [(axes[0,0],a[:,14]),(axes[0,1],a[:,15]),(axes[1,0],a[:,16]/1000),(axes[1,1],a[:,17]/1000),(axes[2,0],a[:,4]/1000)]:ax.plot(t,y,color=col,lw=1.,label=label)
 if len(ct):axes[2,1].plot((ct[:,0]-.60005)*1000,ct[:,-1],color=col,lw=1.,label=label)
for ax,title,unit,line in [(axes[0,0],'Actual current','pu',1),(axes[0,1],'DC link','pu',1.1),(axes[1,0],'PCC active power','kW',800),(axes[1,1],'PCC reactive power','kvar',700),(axes[2,0],'Synthetic DC-port terminal power','kW',None),(axes[2,1],'Modulation change from original nominal PI','norm',None)]:
 ax.set_title(title);ax.set_ylabel(unit);ax.set_xlabel('Time since declared onset (ms)');ax.grid(alpha=.25);ax.legend(fontsize=8);ax.axvline(150,color='gray',ls=':',lw=.8)
 if line is not None:ax.axhline(line,color='black',ls='--',lw=.8)
fig.suptitle('Standard P-priority / radial references with the identical fixed MPSC layer\nSame hypothetical fast port; curves end at observed stop; dotted time marks scheduled clearance',fontsize=12)
if not found:raise RuntimeError('No completed fault record available')
fig.savefig(R/'CONSTRUCTIVE_FAULT_RESPONSE.png',dpi=150)
print(json.dumps({'plotted':found,'file':'CONSTRUCTIVE_FAULT_RESPONSE.png'}))
