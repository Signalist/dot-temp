from pathlib import Path
import json,hashlib,os
os.environ.setdefault("MPLCONFIGDIR","cache/g6-matplotlib")
os.environ.setdefault("XDG_CACHE_HOME","cache/g6-cache")
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':160,'savefig.bbox':'tight'})
colors=['#224E7A','#739C49','#B06426','#7F6AA5']
fig,axs=plt.subplots(1,2,figsize=(10,4.3))
for ax,(r,theta,title) in zip(axs,[(.85,.7,'A. Coupled boundary remains active'),(.9,.01,'B. Fixed adoption can hide that boundary')]):
 k=np.arange(1000);V=r**k[:,None]*np.column_stack([np.cos(k*theta),-np.sin(k*theta)]);c=abs(V).sum(axis=0)
 rays=np.column_stack([np.linspace(0,1,1001),np.linspace(1,0,1001)])
 vals=[[],[],[],[]]
 for a in rays:
  aa=a/c;F=abs(V@aa).sum();L=a.sum()
  for vv,z in zip(vals,[F,max(F,*a),.5*(F+L),L]):vv.append(a/z)
 for vv,cl,lab in zip(vals,colors,['Committed amplitude','Optional, fixed once','Optional, block-varying','Independent port signs']):
  p=np.array(vv);ax.plot(p[:,0],p[:,1],color=cl,label=lab,lw=1.8)
 ax.set(xlabel='Port 1 / its single-port limit',ylabel='Port 2 / its single-port limit',title=title,xlim=(0,1.65),ylim=(0,1.5),aspect='equal')
 ax.text(.04,.05,f'r={r}, theta={theta} rad',transform=ax.transAxes,fontsize=9)
handles,labels=axs[1].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,-.09),ncol=2,frameon=False,fontsize=9)
fig.suptitle('Different workload quantifiers produce different admission domains',fontsize=13)
fig.tight_layout();fig.savefig(OUT/'contract_domains.png');fig.savefig(OUT/'contract_domains.pdf');plt.close(fig)

face=json.loads((ROOT/'experiments/FACE_BUDGET_RESULTS.json').read_text())['rows']
fig,axs=plt.subplots(1,2,figsize=(10,4.1))
for ax,name,title in [(axs[0],'golden_r085','A. Golden-ratio angle, r=0.85'),(axs[1],'near_rational_diagnostic','B. Near-rational mechanism diagnostic')]:
 rr=[x for x in face if x['case']==name];eps=[x['epsilon'] for x in rr]
 for key,lab,col in [('truncation_pieces','Tail truncation',colors[0]),('adaptive_chord_pieces','Classical adaptive chords',colors[2])]:
  ax.plot(eps,[x[key] for x in rr],'-o',label=lab,color=col,ms=3)
 ax.set(xscale='log',xlabel='Uniform gauge error epsilon',ylabel='Affine pieces on slopes [0.25, 4]',title=title);ax.invert_xaxis();ax.grid(axis='y',alpha=.2);ax.legend(frameon=False,fontsize=9)
fig.suptitle('Representation theorem; no claim of a new or superior solver',fontsize=13)
fig.tight_layout();fig.savefig(OUT/'face_budget.png');fig.savefig(OUT/'face_budget.pdf');plt.close(fig)

fig,axs=plt.subplots(1,2,figsize=(10,4.1))
for ax,slug in zip(axs,['kundur','wecc']):
 import csv
 data=list(csv.DictReader((ROOT/f'transfer/{slug}_rays.csv').open()))
 for key,lab,col in [('committed','Committed amplitude',colors[0]),('dynamic_optional','Optional, block-varying',colors[2]),('independent_ports','Independent port signs',colors[3])]:
  rads=np.array([float(x[key+'_capacity_lower_MW']) for x in data]);share=np.array([float(x['a1_share']) for x in data]);ax.plot(rads*share,rads*(1-share),label=lab,color=col,lw=1.8)
 ax.set(xlabel='Port 1 increment amplitude (MW)',ylabel='Port 2 increment amplitude (MW)',title=slug.upper());ax.grid(alpha=.18);ax.legend(frameon=False,fontsize=8)
fig.suptitle('Frozen-point signed-injection kernels: ordinary-float inner bounds',fontsize=13)
fig.text(.5,-.025,'Supplemental port baselines are zero; these curves are not embedded nonnegative data-center hosting capacities.',ha='center',fontsize=9)
fig.tight_layout();fig.savefig(OUT/'old_point_transfer.png');fig.savefig(OUT/'old_point_transfer.pdf');plt.close(fig)

manifest={'scope':'Derived presentation only; no new heldout or changed performance endpoint','sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'experiments/FACE_BUDGET_RESULTS.json',ROOT/'transfer/kundur_rays.csv',ROOT/'transfer/wecc_rays.csv']},'contract_domains':'Original support formula evaluated with 1000 terms on 1001 display rays; exact theory in theory_review, not an independent test'}
(OUT/'FIGURE_PROVENANCE.json').write_text(json.dumps(manifest,indent=2))
