from pathlib import Path
import json, csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]; O=R/'figures';O.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':160})
cert=json.loads((R/'experiments/EXACT_RATIONAL_PARAMETER_CERTIFICATE.json').read_text())['rows']
fig,ax=plt.subplots(figsize=(7.2,4.6));x=[q['intervals'] for q in cert]
ax.loglog(x,[float(q['first_order_error_upper']) for q in cert],'o-',label='First-order Lipschitz bound',color='#64748b')
ax.loglog(x,[float(q['second_order_error_upper']) for q in cert],'s-',label='Kink-safe second-order bound',color='#047857')
ax.set(xlabel='Angle intervals (same mesh)',ylabel='Certified support error',title='Finite angle uncertainty: rigorous error without arithmetic classification');ax.legend(frameon=False);ax.grid(alpha=.15)
fig.text(.12,.025,'Exact rational enclosure: r=17/20, theta in [11/20,17/20], a=(1/2,1/2), N=512\nThe 138.4x error reduction is not a measured runtime or capacity gain',fontsize=8,color='#475569');fig.tight_layout(rect=(0,.1,1,1));fig.savefig(O/'finite_parameter_certificate.png');plt.close(fig)
rows=list(csv.DictReader((R/'contracts/contract_amplitude_brackets.csv').open()))
fig,axs=plt.subplots(1,2,figsize=(9,4.7))
for ax,name,title in zip(axs,['positive','wecc'],['Positive Kundur','WECC incremental model']):
 rs=[q for q in rows if q['source']==name and q['ray_index']=='0']; x=np.array([int(q['B']) for q in rs]);lo=np.array([float(q['inner_amplitude_MW']) for q in rs]);hi=np.array([float(q['outer_amplitude_MW']) for q in rs]);mid=(lo+hi)/2
 ax.errorbar(x,mid,yerr=[mid-lo,hi-mid],fmt='o-',capsize=4,color='#075985',label='All-phase amplitude bracket')
 ax.axhline(mid[-1],color='#64748b',ls='--',label='Independent signs / average-only')
 ax.set(xlabel='Allowed mismatches per 8-block window',ylabel='Total fluctuation amplitude (MW)',title=title,xticks=x);ax.grid(alpha=.15);ax.legend(frameon=False,fontsize=8)
fig.suptitle('Imperfect coordination changes the contract, not the optimizer',fontsize=13)
fig.text(.09,.02,'Equal allocation. Conditional LTI frequency limit 0.05 Hz; ordinary floating evaluation of analytic bounds\nKundur nominal voltages 0.945/0.949 pu. WECC has no positive compute baseline; old nonlinear inner failed',fontsize=8,color='#475569');fig.tight_layout(rect=(0,.09,1,.94));fig.savefig(O/'mismatch_contract_amplitudes.png');plt.close(fig)
rows=json.loads((R/'experiments/ORIENTATION_CROSSOVER.json').read_text())['rows']
fig,ax=plt.subplots(figsize=(7.2,4.6))
for d,c in zip([.001,.01,.1],['#94a3b8','#0284c7','#7c3aed']):
 rs=[q for q in rows if q['orientation_halfwidth_rad']==d];ax.loglog([q['gauge_tolerance'] for q in rs],[q['safe_constructed_pieces'] for q in rs],'o-',color=c,label=f'Orientation halfwidth {d:g} rad')
ax.invert_xaxis();ax.set(xlabel='Gauge tolerance (finer to the right)',ylabel='Constructed safe affine pieces',title='Robust circle-sector complexity has a finite-tolerance crossover');ax.legend(frameon=False);ax.grid(alpha=.15)
fig.text(.11,.025,'Exact normalized circle-sector illustration; not measured grid geometry\nDirect planar pieces only. The same circle arc has a constant-size SOC description',fontsize=8,color='#475569');fig.tight_layout(rect=(0,.1,1,1));fig.savefig(O/'orientation_finite_tolerance.png');plt.close(fig)
