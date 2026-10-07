"""Plot existing stopped fault records and compare the two fixed integration grids."""
from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','.cache/g3_mpl_cache');os.environ.setdefault('XDG_CACHE_HOME','.cache/g3_xdg_cache')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path(__file__).resolve().parent;O=R/'results';ids=['C50-slow','C50-fast','C1-slow','C1-fast'];f,axes=plt.subplots(3,2,figsize=(12,9),constrained_layout=True);ref=[]
for cid,col,ls in zip(ids,['tab:blue','tab:orange','tab:green','tab:red'],['-','-','--','--']):
 d=json.loads((O/f'{cid}_h1e-05.json').read_text());d5=json.loads((O/f'{cid}_h5e-06.json').read_text());z=np.load(O/d['trace_file']);a=z['dense_trace'];ct=z['control'];on=d['event']['start_s'];t=(a[:,0]-on)*1000;label=cid
 for ax,yy in [(axes[0,0],a[:,14]),(axes[0,1],a[:,15]),(axes[1,0],a[:,16]/1000),(axes[1,1],a[:,17]/1000),(axes[2,0],a[:,4]/1000)]:ax.plot(t,yy,color=col,ls=ls,lw=1.3,label=label)
 axes[2,1].plot((ct[:,0]-on)*1000,ct[:,-1],color=col,ls=ls,lw=1.3,label=label)
 ref.append({'case':cid,'stop_reason_10us':d['stop_reason'],'stop_reason_5us':d5['stop_reason'],'root_time_10us_s':d['final_time_s'],'root_time_5us_s':d5['final_time_s'],'root_time_difference_s':d5['final_time_s']-d['final_time_s'],'I_peak_10us':d['metrics']['I_peak_pu'],'I_peak_5us':d5['metrics']['I_peak_pu'],'I_peak_difference_pu':d5['metrics']['I_peak_pu']-d['metrics']['I_peak_pu'],'clearance_observed':False})
for ax,title,unit,line in [(axes[0,0],'Actual current until DC stop','pu',1),(axes[0,1],'DC link: all curves end at upper bound','pu',1.1),(axes[1,0],'PCC active power','kW',800),(axes[1,1],'PCC reactive power','kvar',700),(axes[2,0],'Synthetic DC-port terminal power','kW',None),(axes[2,1],'New modulation change from original PI','norm',None)]:
 ax.set_title(title);ax.set_ylabel(unit);ax.set_xlabel('Time since fault onset (ms)');ax.grid(alpha=.25);ax.legend(fontsize=8)
 if line is not None:ax.axhline(line,color='black',ls=':',lw=.9)
f.suptitle('Four frozen fault cases: current remained below 1 pu only until DC termination\nNo clearance or recovery observed; curves do not extend beyond the numerical stop',fontsize=12)
f.savefig(R/'GATE1_FAULTS_UNTIL_DC_STOP.png',dpi=150)
q={'same_physical_conditions_only':True,'controller_clock_s':.0001,'retuned':False,'rows':ref,'maximum_absolute_root_time_difference_s':max(abs(x['root_time_difference_s']) for x in ref),'maximum_absolute_I_peak_difference_pu':max(abs(x['I_peak_difference_pu']) for x in ref),'interpretation':'Integration step stability of these fixed-parameter offline model records, not parameter uncertainty or hardware verification.'}
(R/'REFINEMENT_COMPARISON.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))
