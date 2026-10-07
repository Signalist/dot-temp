"""Same-condition diagnostic display from saved arrays only."""
from pathlib import Path
import os
os.environ.setdefault("MPLCONFIGDIR", ".cache/p_priority_abc_mpl")
os.environ.setdefault("XDG_CACHE_HOME", ".cache/p_priority_abc_cache")
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
a=np.load(r/'fast_p_priority_abc_h1e-05.npz');b=np.load(r/'dq_saved_state_diagnostics.npz');d=a['control'];D=b['diagnostics'];tr=a['trace'];t=(d[:,0]-.60005)*1000;tt=(tr[:,0]-.60005)*1000
fig,axs=plt.subplots(3,2,figsize=(11,10),layout='constrained');color='#007991'
for ax in axs.flat:
 ax.grid(alpha=.18);ax.set_xlabel('Time from sag onset (ms)');ax.axvline(0,color='0.6',lw=.7)
ax=axs[0,0];ax.plot(tt,tr[:,16],label='Actual abc',color=color);ax.step(t,d[:,13],where='post',label='Reference',color='#c65b29');ax.axhline(1,color='black',ls='--',label='Actual hard constraint');ax.axhline(1.1,color='0.5',ls=':',label='Numerical stop only');ax.set_ylabel('Current (pu)');ax.legend(fontsize=8)
ax=axs[0,1];ax.plot(tt,tr[:,17],color=color);ax.axhline(1.1,color='0.5',ls=':');ax.set_ylabel('DC voltage (pu)');ax.set_ylim(.995,1.105)
ax=axs[1,0];ax.plot(t,d[:,7],label='a raw');ax.plot(t,d[:,8],label='b raw');ax.step(t,d[:,9],where='post',label='a limited');ax.step(t,d[:,10],where='post',label='b limited');ax.set_ylabel('Current basis coefficients (A)');ax.legend(fontsize=8)
ax=axs[1,1];ax.step(t,d[:,6]/(2*np.pi),where='post',color=color,label='PLL frequency');ax.axhline(75,color='0.5',ls=':');ax.set_ylabel('PLL frequency (Hz)');ax2=ax.twinx();ax2.plot(t,d[:,4],color='#c65b29',ls='--',label='Normalized vq error');ax2.set_ylabel('PLL normalized error',color='#c65b29')
ax=axs[2,0];ax.plot(t,np.hypot(d[:,18],d[:,19]),color=color,label='|uu|');ax.plot(t,np.hypot(d[:,20],d[:,21]),color='#c65b29',ls='--',label='|us|');ax.set_ylabel('PI voltage command (V)');ax.legend(fontsize=8);ax.text(.04,.06,'Voltage limiter inactive; current AW term = 0',transform=ax.transAxes,fontsize=8)
ax=axs[2,1];pre=a['sample_before'][:,-10:];post=a['sample_after'][:,-10:];ax.plot(t,pre[:,3],label='zi d before');ax.plot(t,post[:,3],'--',label='zi d after');ax.plot(t,pre[:,4],label='zi q before');ax.plot(t,post[:,4],'--',label='zi q after');ax.set_ylabel('Current PI integrator (V)');ax.legend(fontsize=8)
fig.suptitle('Single fast P-priority condition: independent abc diagnostic window\nSame averaged synthetic-port model; no hardware protection claim',fontsize=13)
fig.savefig(r/'diagnostic_window.png',dpi=160);plt.close(fig)
