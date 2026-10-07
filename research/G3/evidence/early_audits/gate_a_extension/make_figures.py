from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','.cache/g3_mpl_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'gate_a_extension/results';FIG=ROOT/'gate_a_extension/figures';FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.grid':True,'grid.alpha':.25,'figure.dpi':140})
fig,axs=plt.subplots(3,2,figsize=(10,8),constrained_layout=True)
for row,c in enumerate(['sag085','sag075','sag0475']):
 s=json.loads((OUT/f'{c}_h1e-05.json').read_text());z=np.load(OUT/f'{c}_h1e-05.npz');a=z['dense_trace'];x=(a[:,0]-s['event_start_s'])*1000
 axs[row,0].plot(x,a[:,12],lw=1,label='Actual current');axs[row,0].axhline(1,color='crimson',ls='--',label='1.0 pu hard bound')
 axs[row,1].plot(x,a[:,13],lw=1,color='#9467bd',label='DC voltage');axs[row,1].axhline(1.1,color='crimson',ls='--',label='1.1 pu hard bound')
 for col in range(2):
  axs[row,col].axvspan(0,min(150,max(x)),color='#f2b450',alpha=.12);axs[row,col].set_xlabel('Time from sag onset (ms)');axs[row,col].set_ylabel('pu');axs[row,col].set_title(f"{c}: {'completed electrical recovery' if s['stop_reason']=='completed' else 'DC boundary stop; no recovery observed'}");axs[row,col].legend(fontsize=8,loc='best')
fig.suptitle('Fixed preselected sags: balanced averaged synthetic converter',fontsize=14);fig.savefig(FIG/'sag_physical_limits.png');plt.close(fig)
pp=OUT/'signed_periodic_h1e-05.json'
if pp.exists():
 s=json.loads(pp.read_text());z=np.load(pp.with_suffix('.npz'));a=z['endpoint_trace'];tend=s['final_time_s'];a=a[a[:,0]>=tend-3-1e-12]
 fig,axs=plt.subplots(3,1,figsize=(10,8),sharex=True,constrained_layout=True);x=a[:,0]-(tend-3)
 axs[0].plot(x,a[:,14]/1000,label='Actual PCC P');axs[0].plot(x,(s['frozen_bias_W']+300000*np.sin(2*np.pi*(a[:,0]-s['event_start_s'])))/1000,ls='--',lw=.8,label='Sampled command waveform');axs[0].set_ylabel('P (kW)');axs[0].legend()
 axs[1].plot(x,a[:,13],label='DC voltage',color='#9467bd');axs[1].set_ylabel('Vdc (pu)');axs[1].legend()
 eb=(a[:,5]-a[0,5])/1000;axs[2].plot(x,eb,label='Stored battery energy relative to cycle boundary',color='#1f8a70');axs[2].set_ylabel('Energy change (kJ)');axs[2].set_xlabel('Final three fixed-bias confirmation cycles (s)');axs[2].legend(fontsize=9)
 fig.suptitle(f"Signed 1 Hz service: fixed bias {s['frozen_bias_W']/1000:.6f} kW; dq-only numerical orbit",fontsize=13);fig.savefig(FIG/'signed_periodic_confirmation.png');plt.close(fig)
print('Figures written:',', '.join(p.name for p in FIG.glob('*.png')))
