from pathlib import Path
import os,json,hashlib
os.environ.setdefault('MPLCONFIGDIR','cache/g6-matplotlib');os.environ.setdefault('XDG_CACHE_HOME','cache/g6-cache')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'figures'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight'})
paths=[];labels=[];lti=[];nl=[]
for slug,display in [('kundur','Original Kundur'),('wecc','Original WECC')]:
 for contract,short in [('committed','Fixed'),('dynamic_optional','Variable')]:
  p=ROOT/f'nonlinear/{slug}_{contract}_inner_dt128.json';x=json.loads(p.read_text());assert x['complete'];paths.append(p);labels.append(f'{display}\n{short} amplitude');lti.append(x['metrics']['exact_LTI_peak_any_generator_Hz']);nl.append(x['metrics']['nonlinear_peak_any_generator_Hz'])
for contract,short,dt in [('committed','Fixed',128),('dynamic_optional','Variable',256)]:
 p=ROOT/f'positive_workpoint/{contract}_inner_dt{dt}.json';x=json.loads(p.read_text());assert x['complete'];paths.append(p);labels.append(f'Positive Kundur\n{short} amplitude');lti.append(x['metrics']['exact_LTI_peak_Hz']);nl.append(x['metrics']['nonlinear_peak_Hz'])
fig,ax=plt.subplots(figsize=(11.2,4.5));ix=np.arange(len(labels));ax.bar(ix-.18,lti,width=.36,label='Exact same-input LTI',color='#628BA7');ax.bar(ix+.18,nl,width=.36,label='Original nonlinear model',color=['#D27032' if z>.05 else '#446873' for z in nl]);ax.axhline(.05,color='#A93431',linestyle='--',lw=1.4,label='Frequency limit 0.05 Hz');ax.set_xticks(ix,labels,fontsize=8.5);ax.set(ylabel='Peak absolute generator frequency deviation (Hz)',title='A linear inner-bound witness can fail nonlinear transfer',ylim=(0,.059));ax.legend(frameon=False,loc='upper center',bbox_to_anchor=(.5,1.12),ncol=3,fontsize=9);ax.set_title('A linear inner-bound witness can fail nonlinear transfer',pad=44);ax.grid(axis='y',alpha=.15);fig.text(.5,-.02,'Each input is 0.98 times its LTI inner amplitude. Original cases are signed probes; positive Kundur has 50 MW compute per port. Finite trajectories only.',ha='center',fontsize=8.5);fig.tight_layout();fig.savefig(OUT/'nonlinear_inner_transfer.png',dpi=170);fig.savefig(OUT/'nonlinear_inner_transfer.pdf');plt.close(fig)
(OUT/'FINAL_FIGURE_PROVENANCE.json').write_text(json.dumps({'source_files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'scope':'Finest predeclared completed nonlinear traces, no new data or re-selection'},indent=2))
