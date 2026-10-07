from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150})
BLUE='#176c9c';ORANGE='#c15419';GREEN='#19836c'

def ramp_response(t,alpha,beta):
 t=np.maximum(t,0);return (1-np.exp(-alpha*t)*(np.cos(beta*t)+alpha/beta*np.sin(beta*t)))/(alpha*alpha+beta*beta)
def signal(t,knots,power,alpha,beta,gain=1):
 slopes=np.diff(power)/np.diff(knots);changes=np.r_[slopes[0],np.diff(slopes),-slopes[-1]]
 return gain*sum(c*ramp_response(t-k,alpha,beta)*(t>=k) for c,k in zip(changes,knots))
a=4*np.pi/3;R=.01;t=np.linspace(0,22,5000)
k1=np.array([0,a,1.5*a,2.5*a]);p1=np.array([0,R*a,R*a,0]);k2=np.array([0,a,2*a]);p2=np.array([0,R*a,0])
f1=signal(t,k1,p1,.01,1);f2=signal(t,k2,p2,.01,1)
fig,axs=plt.subplots(1,2,figsize=(11,3.5),layout='constrained')
axs[0].plot(t,np.interp(t,k1,p1,right=0),color=BLUE,label='Original: ramp, hold, return');axs[0].plot(t,np.interp(t,k2,p2,right=0),color=ORANGE,label='Recovery projection')
axs[0].set(xlabel='Physical time (normalized)',ylabel='Actual dynamic power',title='Less draw at every physical time');axs[0].legend(fontsize=8)
axs[1].plot(t,f1,color=BLUE,label='Original');axs[1].plot(t,f2,color=ORANGE,label='Projection')
for b in [-.025,.025]:axs[1].axhline(b,color='#555555',ls='--',lw=1)
axs[1].axvspan(2*a,22,color=ORANGE,alpha=.05);axs[1].set(xlabel='Physical time (normalized)',ylabel='Frequency-deficit output',title='The same signed-grid budget fails')
axs[1].legend(fontsize=8);fig.savefig(ROOT/'figures/PROJECTION_SIGNED_GRID.png');fig.savefig(ROOT/'figures/PROJECTION_SIGNED_GRID.pdf');plt.close(fig)

d=json.loads((ROOT/'review/CONVEXITY_INDEPENDENT_VERIFIED.json').read_text())['rounded_three_decimals_gain36_8'];omega=2*np.pi*.4;alpha=.08*omega;beta=omega*np.sqrt(1-.08**2);gain=-36.8/(400/3)
t=np.linspace(0,12,5000);fig,axs=plt.subplots(1,2,figsize=(11,3.5),layout='constrained')
for key,label,color,ls in [('z1','Feasible profile 1',BLUE,'-'),('z2','Feasible profile 2',GREEN,'-'),('midpoint','Work-profile midpoint',ORANGE,'--')]:
 z=np.array(d[key]['work_nodes'],float);knots=np.array(d[key]['physical_time_knots'],float);power=(1.5*z)**(2/3)
 axs[0].plot(np.linspace(0,2,len(z)),z,color=color,ls=ls,label=label)
 axs[1].plot(t,abs(signal(t,knots,power,alpha,beta,gain)),color=color,ls=ls,label=label)
axs[0].set(xlabel='Completed work',ylabel='Work-state z',title='Two exactly feasible reduced profiles');axs[0].legend(fontsize=8)
axs[1].axhline(.05,color='#555555',ls=':',lw=1.3,label='Common 0.05 Hz budget');axs[1].set(xlabel='Physical time (s)',ylabel='Absolute modal frequency (Hz)',title='Grid-memory feasible set is nonconvex',xlim=(2.5,6),ylim=(.04,.051))
axs[1].legend(fontsize=8,loc='lower right');fig.savefig(ROOT/'figures/NONCONVEX_GRID_SET.png');fig.savefig(ROOT/'figures/NONCONVEX_GRID_SET.pdf');plt.close(fig)

rr=json.loads((ROOT/'results/SLEW_SUPPORT_RESULTS.json').read_text());fine=[r for r in rr if r['dt']<.013]
fig,ax=plt.subplots(figsize=(8,3.5),layout='constrained');xx=np.arange(len(fine))
amp=np.array([r['amplitude_only_bound'] for r in fine]);lo=np.array([r['support_lower'] for r in fine]);up=np.array([r['support_upper'] for r in fine])
ax.bar(xx-.18,amp,.32,color=BLUE,label='Amplitude-only bound');ax.bar(xx+.18,up,.32,color=GREEN,label='Joint amplitude/slew upper bound');ax.errorbar(xx+.18,(lo+up)/2,yerr=(up-lo)/2,fmt='none',ecolor='black',capsize=4)
ax.set_xticks(xx,[f"{r['model']['mode_hz']} Hz\nP={r['pcap']}, R={r['R']}" for r in fine]);ax.set(ylabel='All-history frequency support (Hz)',title='A tighter safe class without exact-grid convexity');ax.legend(fontsize=8);fig.savefig(ROOT/'figures/SLEW_SUPPORT_BOUNDS.png');fig.savefig(ROOT/'figures/SLEW_SUPPORT_BOUNDS.pdf')
print('Saved three boundary figures and PDF counterparts')
