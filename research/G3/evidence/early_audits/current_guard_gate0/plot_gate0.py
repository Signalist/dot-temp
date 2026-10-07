from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','.cache/g3_mpl_cache');os.environ.setdefault('XDG_CACHE_HOME','.cache/g3_xdg_cache')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path(__file__).resolve().parent;s=json.loads((R/'GATE0_RESULTS.json').read_text());h=s['first_hold'][0];t=np.array(h['time_grid_s'])*1e6;u=np.array(h['structured_node_bounds_pu'])+h['intersample_padding_pu'];l=np.array(h['broad_witness_projection_lower_pu'])
f,axs=plt.subplots(1,2,figsize=(11,4.5),constrained_layout=True)
axs[0].plot(t,u,label='Amplitude-only: ideal-model upper enclosure');axs[0].plot(t,l,label='Broad disk: reversal witness lower projection');axs[0].axhline(1,color='crimson',ls='--',label='Actual current hard limit');axs[0].set_xlabel('Immutable first hold (microseconds)');axs[0].set_ylabel('Current bound (pu)');axs[0].set_title('Different declared source contracts; not simulated traces');axs[0].legend(fontsize=8);axs[0].grid(alpha=.25)
r=s['contracts'][1];nom=np.array(r['first_nominal_PI_modulation']);cand=np.array(r['first_certified_plan_input_candidate']);theta=np.linspace(0,2*np.pi,300);mm=s['constants']['mmax'];axs[1].plot(mm*np.cos(theta),mm*np.sin(theta),color='gray',label='Physical modulation circle');axs[1].arrow(0,0,nom[0],nom[1],width=.003,length_includes_head=True,color='tab:blue');axs[1].arrow(0,0,cand[0],cand[1],width=.003,length_includes_head=True,color='tab:orange');axs[1].scatter([nom[0]],[nom[1]],label='Original PI proposal',color='tab:blue');axs[1].scatter([cand[0]],[cand[1]],label='Offline numerical candidate',color='tab:orange');axs[1].set_aspect('equal');axs[1].set_xlabel('Measured-source frame: m real');axs[1].set_ylabel('m imaginary');axs[1].set_title('Initial change norm 0.214581; no closed-loop evidence');axs[1].legend(fontsize=8);axs[1].grid(alpha=.25)
f.savefig(R/'GATE0_BOUNDS_AND_CANDIDATE.png',dpi=160)
