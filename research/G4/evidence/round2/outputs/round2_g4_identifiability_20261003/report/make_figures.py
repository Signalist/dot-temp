import tempfile
import json,pathlib,os,numpy as np
os.environ["MPLCONFIGDIR"]=str(pathlib.Path(tempfile.gettempdir())/"g4_matplotlib")
os.environ["XDG_CACHE_HOME"]=str(pathlib.Path(tempfile.gettempdir())/"g4_fontcache")
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=pathlib.Path(__file__).resolve().parent;E=R.parent/'experiments';plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150})
x=json.load(open(E/'FIXED_INITIAL_RESULTS.json'))
fig,ax=plt.subplots(1,2,figsize=(10,3.7),layout='constrained')
for eta in [.999,.99,.95,.8]:
 r=[z for z in x['fixed_half'] if z['ec']==eta];ax[0].plot([z['K'] for z in r],[z['capacity'] for z in r],'o-',label=f'eta={eta}')
ax[0].set_xscale('log');ax[0].set_xlabel('Independent task-order blocks K');ax[0].set_ylabel('Minimum buffer energy');ax[0].set_title('Positive recovery tolerance = 0.5');None
ax[0].legend(fontsize=8);ax[0].grid(alpha=.2)
r=x['positive_tolerance'];ax[1].plot([z['tau'] for z in r],[z['capacity'] for z in r],'o-',color='#7046b5');ax[1].axhline(20.6802721088,color='gray',ls='--',label='Infinite-horizon lower bound')
ax[1].set_xlabel('Recovery tolerance (+/- energy)');ax[1].set_ylabel('Minimum buffer energy');ax[1].set_title('10 blocks, eta=0.95, E0=B/2');ax[1].legend(fontsize=8);ax[1].grid(alpha=.2)
fig.suptitle('Synthetic all-order hiding capacity; not source-identification accuracy',fontsize=12)
for ext in ['png','pdf']:fig.savefig(R/'figures'/f'capacity_tolerance_horizon.{ext}')
a=np.load(E/'SMOOTH_DAG_PAIR.npz');fig,ax=plt.subplots(3,1,figsize=(9,7),sharex=True,layout='constrained')
ax[0].plot(a['t'],a['load1'],label='High task in slot 2');ax[0].plot(a['t'],a['load2'],'--',label='High task in slot 3');ax[0].plot(a['t'],a['PCC'],'k:',label='Identical PCC');ax[0].set_ylabel('Power');ax[0].legend(ncol=3,fontsize=8)
ax[1].plot(a['t'],a['energy1']);ax[1].plot(a['t'],a['energy2'],'--');ax[1].axhline(9,color='gray',ls=':');ax[1].set_ylabel('Stored energy');ax[1].set_ylim(0,18);ax[1].axvline(2,color='#7046b5',alpha=.4);ax[1].text(2.05,16,'Identity-bound SOC query separates')
ax[2].plot(a['t'],a['command1']);ax[2].plot(a['t'],a['command2'],'--');ax[2].set_ylabel('PCS command');ax[2].set_xlabel('Seconds');ax[2].set_ylim(-12,12)
for z in ax:z.grid(alpha=.2)
fig.suptitle('Lossy smooth DAG pair: finite actuator, same PCC, exact recovery',fontsize=12)
for ext in ['png','pdf']:fig.savefig(R/'figures'/f'smooth_dag_equivalence.{ext}')
