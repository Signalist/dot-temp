import json,os
os.environ.setdefault('MPLCONFIGDIR','.cache/g4_mplconfig')
os.environ.setdefault('XDG_CACHE_HOME','.cache/g4_cache')
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
B=Path(__file__).resolve().parents[1];out=B/'report/figures';out.mkdir(exist_ok=True)
r=json.loads((B/'experiments/dag_results.json').read_text());h=json.loads((B/'experiments/finite_horizons.json').read_text());l=json.loads((B/'experiments/leakage_results.json').read_text());b=json.loads((B/'experiments/boundary_results.json').read_text())
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150})
fig,ax=plt.subplots(1,2,figsize=(11,4.2),layout='constrained')
rr=[x for x in r if x['split']=='worked' and x['eta']==.95];names=['Full\norders\n6 tasks','Connected\nDAG\n6 tasks','Two\nstages\n6 tasks','Unequal\nstages\n8 tasks','Two\npipelines\n8 tasks'];x=np.arange(5)
ax[0].bar(x-.18,[z['full_permutation_B'] for z in rr],width=.36,color='#cbd5e1',label='Same multiset, all orders')
ax[0].bar(x+.18,[z['scenario_B'] for z in rr],width=.36,color='#147d92',label='Specified DAG (scenario optimum)')
ax[0].set_xticks(x,names);ax[0].set_ylabel('Usable stored energy (normalized)');ax[0].set_title('Task precedence changes the sharp capacity');ax[0].legend(frameon=False,fontsize=8)
for name,label,color in [('antichain_6','Full orders','#5363bf'),('connected_restricted_6','Connected DAG','#147d92'),('barriers_3plus3','Two stages','#ad6c1c')]:
 vals=[z for z in h if z['name']==name];ax[1].plot([z['blocks'] for z in vals],[z['capacity'] for z in vals],'o-',label=label,color=color);ax[1].axhline(vals[0]['infinite_capacity'],ls=':',color=color,alpha=.7)
ax[1].set_xscale('log',base=2);ax[1].set_xlabel('Independent blocks; no terminal recovery');ax[1].set_ylabel('Minimum capacity');ax[1].set_title('Finite horizons approach the proved limit');ax[1].legend(frameon=False,fontsize=8)
for ext in ['png','pdf']:fig.savefig(out/f'dag_capacity_and_horizon.{ext}')
plt.close(fig)
fig,ax=plt.subplots(1,2,figsize=(10,4.1),layout='constrained')
for rho,color in [(.999,'#147d92'),(.99,'#ad6c1c'),(.9,'#5363bf')]:
 row=next(z for z in l if z['name']=='antichain_6' and z['rho']==rho);ax[0].plot(np.arange(1,7),row['output'],'o-',label=f'ρ={rho:g}, B={row["B"]:.3f}',color=color)
ax[0].axhline(next(z['output'][0] for z in rr if z['name']=='antichain_6'),color='#555',ls=':',label='No leakage: flat output')
ax[0].set_xlabel('Slot');ax[0].set_ylabel('Common PCC power');ax[0].set_title('Discrete leakage permits nonflat output');ax[0].legend(fontsize=8,frameon=False)
ramps=b['PCC_step_ablation'];ax[1].plot([z['cyclic_PCC_step_limit'] for z in ramps],[z['capacity'] for z in ramps],'o-',color='#147d92');ax[1].set_xlabel('Cyclic PCC step bound (not converter slew)');ax[1].set_ylabel('Minimum capacity');ax[1].set_title('Action-class ablation: unequal stages')
for ext in ['png','pdf']:fig.savefig(out/f'leakage_and_action_boundary.{ext}')
plt.close(fig)
print(str(out))
