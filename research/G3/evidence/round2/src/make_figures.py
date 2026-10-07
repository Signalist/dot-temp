from pathlib import Path
import json,numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1];fig=root/'figures'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140})
rows=json.loads((root/'results/PRIMARY_CAMPAIGN.json').read_text());last=[r for r in rows if r['n']==160]
Z=np.zeros((4,5));txt=np.empty((4,5),object)
for r in last:
 i=r['alpha']//100;j=r['beta']//300;v=r['inner'].get('margin_kJ')
 Z[i,j]=0 if v is None else 1 if v>0 else -1;txt[i,j]='current' if v is None else f'{v:+.3f} kJ'
f,ax=plt.subplots(figsize=(8.5,4));im=ax.imshow(Z,origin='lower',vmin=-1,vmax=1,cmap='RdYlGn',aspect='auto')
for i in range(4):
 for j in range(5):ax.text(j,i,txt[i,j],ha='center',va='center')
ax.set(xticks=range(5),xticklabels=[0,300,600,900,1200],yticks=range(4),yticklabels=[0,100,200,300],xlabel='Requested reactive support (kvar)',ylabel='Active import curtailment (kW)',title='Same device: ideal averaged contract admission')
f.tight_layout();f.savefig(fig/'primary_admission.png');plt.close(f)
rows=json.loads((root/'results/EXACT_CELL_CAMPAIGN.json').read_text());r=[x for x in rows if x['alpha']==100 and x['beta']==600]
f,axs=plt.subplots(1,2,figsize=(10,4))
ns=np.array([40,80,160]);lo=np.array([next(x['margin_kJ'] for x in r if x['n']==n and x['tightened']) for n in ns]);up=np.array([next(x['margin_kJ'] for x in r if x['n']==n and not x['tightened']) for n in ns])
axs[0].plot(ns,lo,'o-',label='Constructive exact-cell inner');axs[0].plot(ns,up,'s-',label='Exact-cell nodal outer');axs[0].axhline(1.482889783,color='k',ls=':',label='Independent prefix ceiling');axs[0].set(xlabel='Uniform grid divisions',ylabel='Uniform safety margin (kJ)');axs[0].legend(fontsize=8)
axs[1].loglog(.2/ns,(up-lo)*1000,'o-',label='Observed bracket width');axs[1].loglog(.2/ns,3750000*(.2/ns)**2,'--',label='R h²/8');axs[1].set(xlabel='Uniform cell h (s)',ylabel='Bracket width (J)');axs[1].legend(fontsize=8)
f.suptitle('Same parameters and terminal recovery; state-tube O(h²), not a universal objective rate');f.tight_layout();f.savefig(fig/'exact_cell_convergence.png');plt.close(f)
rr=json.loads((root/'results/switch_corridor/RESULTS.json').read_text());f,ax=plt.subplots(figsize=(8,4.4))
for q,col in [(900,'#136f63'),(1000,'#d1495b'),(1050,'#4b3f72')]:
 a=[r for r in rr if r['beta']==q];xs=np.array([r['ramp']/1000 for r in a]);ys=np.array([r['inner']['margin_kJ'] for r in a]);yy=np.array([r['exact_outer']['margin_kJ'] for r in a]);ax.plot(xs,ys,'o-',color=col,label=f'{q} kvar inner');ax.plot(xs,yy,'x--',color=col,alpha=.75)
ax.axhline(0,c='k',lw=1);ax.set(xlabel='Same-case buffer slew limit (MW/s)',ylabel='Uniform safety margin (kJ)',title='Four-cycle compute demand: joint corridor decisions');ax.legend();f.tight_layout();f.savefig(fig/'compute_shape_transfer.png');plt.close(f)
rr=json.loads((root/'theory/vector_weak_results.json').read_text())['results'];old=json.loads((root/'results/ALLOCATION_SLACK_FRONTIER.json').read_text());f,ax=plt.subplots(figsize=(8,4.4));eps=np.array([r['epsilon_kJ']*1000 for r in rr]);upper=np.array([r['verified_excluded_beta_kvar'] for r in rr]);oldy=np.array([r['beta_exclusion_threshold_fixed_test_kvar'] for r in old]);ax.semilogx(eps[1:],upper[1:],'o-',label='Joint-budget vector weak upper bound');ax.semilogx(eps[1:],oldy[1:],':',color='#999999',label='Earlier d-axis weak upper bound');ax.axhline(808,c='#136f63',ls='--',label='Exhibited recoverable contract at 808 kvar');ax.fill_between(eps[1:],808,upper[1:],color='#d9e6ed',alpha=.7,label='Unresolved capacity interval');ax.set(xlabel='Extra net late-recovery allowance (J)',ylabel='Reactive contract magnitude (kvar)',title='P cap / Q floor, all time-varying allocations, same compute workload');ax.legend(fontsize=8);f.tight_layout();f.savefig(fig/'all_allocation_slack.png');plt.close(f)
print('created four figures')
