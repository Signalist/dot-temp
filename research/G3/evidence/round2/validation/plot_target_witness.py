from pathlib import Path
import os
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.mplconfig'))
os.environ.setdefault('XDG_CACHE_HOME',str(ROOT/'.cache'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

name='witness_a100_q600_n160'
z=dict(np.load(ROOT/f'{name}_pwm_f10000_h1e-06_comparison.npz'))
t=z['t']*1000
fig,axs=plt.subplots(3,2,figsize=(12,10),constrained_layout=True)
ax=axs[0,0];ax.plot(t,z['Pcmd']/1000,'k--',label='grid command');ax.plot(t,z['Pmean']/1000,label='PWM grid cycle mean');ax.plot(t,z['dmean']/1000,alpha=.7,label='continuing compute load');ax.set_ylabel('Active power (kW)');ax.legend()
ax=axs[0,1];ax.plot(t,z['Qcmd']/1000,'k--',label='support command');ax.plot(t,z['Qmean']/1000,label='PWM support cycle mean');ax.set_ylabel('Reactive support (kvar)');ax.legend()
ax=axs[1,0];ax.fill_between(t,z['Vmin'],z['Vmax'],alpha=.6,label='within-cycle voltage range');ax.plot(t,np.sqrt(2*z['ideal_W']/.03),'k--',label='ideal witness');ax.axhline(1080,color='r',ls=':');ax.axhline(1320,color='r',ls=':');ax.set_ylabel('DC voltage (V)');ax.legend()
ax=axs[1,1];ax.plot(t,z['B']/1000,label='actual');ax.plot(t,z['ideal_B']/1000,'k--',label='ideal witness');ax.axhline(50,color='grey',ls=':');ax.set_ylabel('Battery inventory (kJ)');ax.legend()
ax=axs[2,0];ax.plot(t,z['b']/1000,label='actual battery power');ax.plot(t,z['umean']/1000,'--',alpha=.7,label='u command');ax.axhline(450,color='r',ls=':');ax.axhline(-450,color='r',ls=':');ax.set_ylabel('Battery power (kW)');ax.legend()
ax=axs[2,1];ax.plot(t,z['W']-z['ideal_W'],label='actual W minus ideal W');ax.axhline(0,color='k',ls=':');ax.set_ylabel('DC-energy discrepancy (J)');ax.legend()
for ax in axs.flat:ax.axvline(200,color='grey',ls=':');ax.set_xlabel('Time (ms)');ax.grid(alpha=.25)
fig.suptitle('Same analytical command applied to independent 10 kHz PWM plant\nFinite-horizon bounds pass; exact DC-energy recovery fails (no retuning)')
fig.savefig(ROOT/'target_a100_q600_validation.png',dpi=160);plt.close(fig)

fig,axs=plt.subplots(2,2,figsize=(12,7),constrained_layout=True)
axs[0,0].plot(t,z['Imax']);axs[0,0].axhline(1500,color='r',ls=':');axs[0,0].set_ylabel('Actual phase-vector peak per cycle (A)')
axs[0,1].plot(t,z['modulation']);axs[0,1].axhline(1,color='r',ls=':');axs[0,1].set_ylabel('PWM duty-span utilization')
wave=np.genfromtxt(ROOT/f'{name}_pwm_f10000_h1e-06_waveform.csv',delimiter=',',names=True)
for key in ['ia','ib','ic']:axs[1,0].plot(wave['t']*1000,wave[key],label=key)
axs[1,0].set_ylabel('Switched phase current (A)');axs[1,0].legend()
mask=wave['t']>=.2997;axs[1,1].step(wave['t'][mask]*1000,wave['sa'][mask],where='mid',label='leg a');axs[1,1].set_ylabel('Actual binary switching state');axs[1,1].legend()
for ax in axs.flat:ax.set_xlabel('Time (ms)');ax.grid(alpha=.25)
fig.suptitle('Physical switched-current, modulation and binary-leg evidence\nSynthetic ideal semiconductor model, no real hardware claims')
fig.savefig(ROOT/'target_a100_q600_switching.png',dpi=160);plt.close(fig)
