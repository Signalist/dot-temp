from pathlib import Path
import os,json,numpy as np
OUT=Path(__file__).resolve().parent;os.environ['MPLCONFIGDIR']=str(OUT/'mplcache');os.environ['XDG_CACHE_HOME']=str(OUT/'xdgcache')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
blue='#1976a3';orange='#d4822d';red='#b83939';green='#46865b'
fig,axs=plt.subplots(2,2,figsize=(12,8),layout='constrained')
ax=axs[0,0];vals=[94.26493675271104,127.13453434593212]
ax.bar(['Delayed sampled P','Initial P only'],vals,color=[blue,orange],width=.6)
ax.axhline(64.61624655317877,color='0.25',ls='--',lw=1.5,label='Unrestricted OL lower: 64.62')
for i,v in enumerate(vals):ax.text(i,v+2,f'{v:.2f}',ha='center',fontweight='bold')
ax.set_ylim(0,151);ax.set_ylabel('Usable SOC excursion (MWs)');ax.set_title('(a) Conventional family: 25.85% less energy',loc='left');ax.legend(frameon=False,fontsize=9,loc='upper left')
ax.text(.5,.05,'50 MW command cap; exact SOC recovery by 60 s',ha='center',transform=ax.transAxes,fontsize=9)
ax=axs[0,1]
for kind,color in [('feedback',blue),('openloop',orange)]:
 for hi,ls in [('low','-'),('high','--')]:
  d=json.loads((OUT/f'binned93_{kind}_{hi}_certificate.json').read_text());rows=d['bin_midpoint_certificates'];r=np.array([x['r'] for x in rows]);y=np.array([x['continuous_finite_peak_upper_Hz'] for x in rows]);ax.plot(r,y,color=color,ls=ls,lw=1.6,label=f'{kind}, {hi} start')
ax.axhline(.1,color=red,ls=':',lw=1.5);ax.text(4.92,.10025,'Research band',color=red,fontsize=9,ha='right')
ax.set_ylim(.085,.102);ax.set_xlim(0,5);ax.set_xlabel('Representative remaining first-stage time (s)');ax.set_ylabel('Continuous LTI peak bound (Hz)');ax.set_title('(b) Full-state LTI, all 50 information bins',loc='left');ax.legend(frameon=False,fontsize=8,loc='lower right')
ax.text(.04,.96,'Add 4.436 mHz to cover every phase\nAll-future upper <= 97.458 mHz',va='top',transform=ax.transAxes,fontsize=9,bbox={'facecolor':'white','alpha':.85,'edgecolor':'none'})
ax=axs[1,0]
for kind,color in [('fb',blue),('ol',orange)]:
 d=np.load(OUT/'nonlinear_replay'/f'{kind}_low_r2.347_s1_ramp0.npz');t=d['t']-1;f=d['frequency_deviation_Hz'];ax.plot(t,np.min(f,axis=1),color=color,lw=1.5,label=('Sampled P' if kind=='fb' else 'Initial P only'))
ax.axhline(-.1,color=red,ls=':',lw=1.5);ax.set_xlim(0,30);ax.set_ylim(-.105,.015);ax.set_xlabel('Time after reconnection (s)');ax.set_ylabel('Lowest generator frequency deviation (Hz)');ax.set_title('(c) Unseen r=2.347 s, low start: unchanged ANDES',loc='left');ax.legend(frameon=False,fontsize=9,loc='lower right')
ax=axs[1,1];xs=[0,5,10];ys=[]
for scale in [1.,1.05,1.1]:
 path=OUT/'nonlinear_replay'/f'fb_high_r4.927_s{scale:g}_ramp0.json';d=json.loads(path.read_text());ys.append(d['window']['peak_abs_any_generator_Hz'])
ax.plot(xs,ys,'o-',color=blue,lw=1.8);ax.axhline(.1,color=red,ls=':',lw=1.5)
for x,y in zip(xs,ys):ax.annotate(f'{y:.5f}',(x,y),xytext=(0,-18 if x==5 else 8),textcoords='offset points',ha='center')
ax.set_xticks(xs);ax.set_xlabel('Out-of-contract amplitude increase (%)');ax.set_ylabel('Nonlinear peak, any generator (Hz)');ax.set_ylim(.086,max(ys)+.006);ax.set_title('(d) High-start amplitude fragility, fixed policy',loc='left');ax.text(.03,.06,'+10% is a separately frozen, outcome-informed\nchallenge; no controller redesign',transform=ax.transAxes,fontsize=9)
fig.suptitle('Kundur information-contract transfer: conventional control, qualified evidence',fontsize=14,fontweight='bold')
fig.savefig(OUT/'figure_network_transfer.png',dpi=190);fig.savefig(OUT/'figure_network_transfer.svg')
print('Saved figure_network_transfer.png/.svg')
