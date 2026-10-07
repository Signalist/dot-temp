from pathlib import Path
import json,hashlib,os
import numpy as np
R=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(R/'.mplconfig'));os.environ.setdefault('XDG_CACHE_HOME',str(R/'.cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
results=[]
for beta in [790,800,805,808]:
    f=R/f'boundary_a100_q{beta}_n320_TARGET_RESULTS.json';z=json.loads(f.read_text());r=next(r for r in z['runs'] if r['mode']=='pwm' and r['dt']==1e-6)
    results.append({key:r[key] for key in ['Vmin','Vmax','Ipeak','modulation_max','circular_modulation_max','clipped_cycles','tracking_horizon_0p2s','Pmean_max_abs_error_W','Qmean_max_abs_error_W','u_clamp_max_change_W','rate_clamp_max_change_W_per_s','all_tested_hardware_bounds_satisfied','state_at_0.200s','state_at_0.300s']}|{'beta_kvar':beta,'analytic_margin_J':1000*z['analytic_margin_kJ'],'source_sha256':z['source_sha256'],'result_file':f.name,'step_convergence':z['convergence']})
protocol=R.parent/'BOUNDARY_PROTOCOL.json';out={'preregistered_protocol':str(protocol),'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),'requested_batch_beta_kvar':[790,800,805,808,810],'all_admitted_cases_tested':[790,800,805,808],'omitted_simulation':{'beta_kvar':810,'reason':'Analytically excluded; negative-margin NPZ is not an admissible witness; the protocol excluded simulation of that non-witness'},'physical_model_unmodified':True,'no_retuning':True,'results':results,'decision':'All four admitted cases satisfy tested finite-horizon bounds, inventory recovery passes, exact DC recovery and exact P/Q transfer fail.'}
(R/'BOUNDARY_VALIDATION_SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n')
fig,axs=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
for beta in [790,800,805,808]:
    z=np.load(R/f'boundary_a100_q{beta}_n320_pwm_f10000_h1e-06_comparison.npz');t=z['t'];mask=t<.04
    axs[0,0].plot(t[mask]*1000,z['circular_modulation'][mask],label=str(beta)+' kvar')
    axs[0,1].plot(t[mask]*1000,z['modulation'][mask],label=str(beta)+' kvar')
    axs[1,0].plot(t*1000,z['W']-z['ideal_W'],label=str(beta)+' kvar')
    axs[1,1].plot(t*1000,z['Imax'],label=str(beta)+' kvar')
axs[0,0].axhline(1,color='r',ls=':');axs[0,0].set_ylim(.98,1.003);axs[0,0].set_ylabel('Circular modulation utilization')
axs[0,1].axhline(1,color='r',ls=':');axs[0,1].set_ylabel('Actual PWM duty-span utilization')
axs[1,0].axhline(0,color='k',ls=':');axs[1,0].axvline(200,color='grey',ls=':');axs[1,0].set_ylabel('Actual minus ideal DC energy (J)')
axs[1,1].axhline(1500,color='r',ls=':');axs[1,1].set_ylabel('Within-cycle current-vector maximum (A)')
for ax in axs.flat:ax.set_xlabel('Time (ms)');ax.grid(alpha=.25);ax.legend()
fig.suptitle('Entire preregistered admitted near-boundary batch, unchanged 10 kHz PWM controller\nNo clipped cases; small modulation margins survive, exact DC recovery does not')
fig.savefig(R/'boundary_validation_batch.png',dpi=160);plt.close(fig)
print(json.dumps({'cases':len(results),'clipped_cases':sum(r['clipped_cycles']>0 for r in results),'max_circle':max(r['circular_modulation_max'] for r in results)}))
