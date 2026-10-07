from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
MODELS=['design4','interior4','transfer8_cube','transfer8_mesh']
STYLE={'classic_shared_grid_template_safe':('Verified template inner','#147D92','-'), 'phase_free_harmonic_shared_grid_safe':('Phase-free harmonic inner','#DA8B26','--'),'classic_shared_grid_template_sample_outer':('Template outer','#4779B6',':'),'sparse_3x9_template_UNCERTIFIED':('Sparse mesh (not certified)','#BD4B45','-.')}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
fig,axes=plt.subplots(2,2,figsize=(10,8),constrained_layout=True)
for name,ax in zip(MODELS,axes.flat):
    p=ROOT/'results'/f'{name}_polygons.json'
    if not p.exists():ax.axis('off');continue
    polys=json.loads(p.read_text())
    for method,(label,col,ls) in STYLE.items():
        q=np.array(polys[method]);q=np.vstack([q,q[0]])
        ax.plot(q[:,0],q[:,1],label=label,color=col,linestyle=ls,linewidth=1.8)
    ax.set_title(name);ax.set_xlabel('Site 1 fundamental amplitude [MW]');ax.set_ylabel('Site 2 fundamental amplitude [MW]');ax.set_xlim(left=0);ax.set_ylim(bottom=0);ax.grid(alpha=.18)
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=2,frameon=False)
fig.suptitle('G6 conditional steady-state amplitude envelopes\nSynthetic networks; no installed-MW or nonlinear safety claim',fontsize=13)
fig.savefig(OUT/'joint_envelopes.png');plt.close(fig)
fig,axes=plt.subplots(2,2,figsize=(10,7),constrained_layout=True)
for name,ax in zip(MODELS,axes.flat):
    p=ROOT/'results'/f'{name}_challenge_trials.csv'
    if not p.exists():ax.axis('off');continue
    d=pd.read_csv(p);d=d[d.condition=='fixed_template']
    for method,(label,col,ls) in STYLE.items():
        if method=='classic_shared_grid_template_sample_outer':continue
        s=d[d.method==method].sort_values('scenario')
        ax.plot(s.scenario,s.peak_ratio,color=col,ls=ls,label=label,linewidth=1.4)
    ax.axhline(1,color='black',lw=1);ax.axvline(19.5,color='gray',lw=.8,ls=':');ax.set_title(name);ax.set_xlabel('Paired scenario (0–19 random; 20–39 peak targets)');ax.set_ylabel('Sampled nonlinear peak / limit');ax.grid(alpha=.18)
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=2,frameon=False)
fig.suptitle('Nonlinear stress tests do not extend the linear certificate',fontsize=13);fig.savefig(OUT/'nonlinear_stress_tests.png');plt.close(fig)
