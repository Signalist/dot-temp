import tempfile
import pathlib,sys,os
os.environ['MPLCONFIGDIR']=str(pathlib.Path(tempfile.gettempdir())/'g4_matplotlib');os.environ['XDG_CACHE_HOME']=str(pathlib.Path(tempfile.gettempdir())/'g4_fontcache')
import numpy as np,matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'experiments'))
from grid_service_decision import shape,eta,a2,a3,D
z=np.load(R.parent/'experiments/GRID_SERVICE_WITNESS.npz');t=z['t'];_,_,J2=shape(t-1);_,_,J3=shape(t-2)
elow=9-float((D-a2)/eta)*J2+float(eta*a3)*J3;ehigh=9+float(eta*a2)*J2-float((D-a3)/eta)*J3
p=np.where(t<3,z['PCC_prefix'],z['PCC_service_recovery']);e=np.where(t<3,ehigh,z['energy_service_recovery'])
fig,ax=plt.subplots(2,1,figsize=(9,5.7),sharex=True,layout='constrained')
ax[0].plot(t,p,color='#286cae',label='Same observed prefix; accepted service after3s');ax[0].axhline(6,color='gray',ls=':',label='Continuing compute after3s');ax[0].axvspan(3,5,color='#86bece',alpha=.18);ax[0].set_ylabel('PCC import');ax[0].legend(fontsize=8)
ax[1].plot(t,e,label='High SOC: service + recovery',color='#286cae');mask=t<=3;ax[1].plot(t[mask],elow[mask],'--',color='#bd3f3b',label='Low SOC: cannot commit full service');ax[1].plot([3],[elow[mask][-1]],'o',color='#bd3f3b');ax[1].hlines(9.88,2.7,3.5,color='black',linestyle=':',label='Required energy9.88');ax[1].set_ylabel('Stored energy');ax[1].set_xlabel('Seconds');ax[1].legend(fontsize=8,loc='upper right');ax[1].set_ylim(0,18)
for a in ax:a.axvline(3,color='gray',ls='--',alpha=.6);a.grid(alpha=.2);a.spines['right'].set_visible(False);a.spines['top'].set_visible(False)
fig.suptitle('Identical past PCC, different safe service decision (synthetic model)',fontsize=12)
for ext in ['png','pdf']:fig.savefig(R/'figures'/f'grid_service_decision.{ext}',dpi=150)
