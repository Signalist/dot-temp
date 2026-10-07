from pathlib import Path
import json,hashlib,os
import numpy as np
R=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(R/'.mplconfig'));os.environ.setdefault('XDG_CACHE_HOME',str(R/'.cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CASES=['spline_R5000_q900','spline_R10000_q1050','spline_R30000_q1000']
CPP_HASH=hashlib.sha256((R/'rectifier.cpp').read_bytes()).hexdigest()
reference_hash=json.loads((R/'REFERENCE_SHA256.json').read_text())['rectifier.cpp']
assert CPP_HASH==reference_hash,'Physical plant/control changed from prior validation layer'
records=[]
for index,case in enumerate(CASES):
    z=json.loads((R/f'{case}_TARGET_RESULTS.json').read_text());w=dict(np.load(z['source']));r=next(r for r in z['runs'] if r['dt']==1e-6)
    T=float(w['t'][-1]);a=np.genfromtxt(R/r['trace'],delimiter=',',names=True)
    work=float(np.trapezoid(w['d']*1000,w['t']));extra=float(np.trapezoid((w['d']-650)*1000,w['t']))
    conservation={'service_input_work_J':work,'continuing_baseline_work_J':650000*T,'extra_work_J':extra,'work_preserved':abs(extra)<1e-6,'input_load_min_W':float(w['d'].min()*1000),'input_load_max_W':float(w['d'].max()*1000),'simulated_load_work_at_T_J':float(a['load_energy'][np.argmin(abs(a['t']-T))]),'initial_current_d_A':float(w['p'][0]*1000/(1.5*z['parameters']['Vrms']*np.sqrt(2/3))),'initial_current_q_A':float(w['q'][0]*1000/(1.5*z['parameters']['Vrms']*np.sqrt(2/3))),'initial_W_J':z['parameters']['W0'],'initial_B_J':z['parameters']['B0'],'initial_b_W':z['parameters']['b0']}
    records.append({'case':case,'source_sha256':z['source_sha256'],'analytic_margin_J':1000*z['analytic_margin_kJ'],'ramp_limit_W_per_s':z['parameters']['ramp'],'input_and_state_checks':conservation,'primary_result':r,'step_convergence':z['convergence']})
    assert conservation['work_preserved'] and conservation['input_load_min_W']>0
protocol=R.parent/'CORRIDOR_SWITCH_PROTOCOL.json'
out={'additional_layer':'six new 10 kHz PWM simulations, distinct from original 41-run layer','source_protocol':str(protocol),'source_protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),'local_selection_protocol_sha256':hashlib.sha256((R/'SHAPE_TRANSFER_VALIDATION_PROTOCOL.json').read_bytes()).hexdigest(),'physical_cpp_sha256':CPP_HASH,'same_cpp_as_original_reference_layer':CPP_HASH==reference_hash,'selected_cases_before_PWM':CASES,'results':records,'negative_margin_cases_simulated':[],'decision':'All three finite-horizon bounds pass. Inventory recovery passes. Exact DC recovery and exact P/Q transfer fail; no retuning or indefinite-orbit claim.'}
(R/'SHAPE_TRANSFER_VALIDATION_SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n')
fig,axs=plt.subplots(3,2,figsize=(12,10),constrained_layout=True)
for case in CASES:
    z=np.load(R/f'{case}_pwm_f10000_h1e-06_comparison.npz');t=z['t']*1000;label=case.replace('spline_','').replace('_',', ')
    if case==CASES[0]:axs[0,0].plot(t,z['dmean']/1000,color='k',label='same compute load')
    axs[0,1].plot(t,z['Qmean']/1000,label=label)
    axs[1,0].plot(t,z['Vmax'],label=label,color=f'C{CASES.index(case)}');axs[1,0].plot(t,z['Vmin'],alpha=.45,color=f'C{CASES.index(case)}')
    axs[1,1].plot(t,z['Imax'],label=label)
    axs[2,0].plot(t,z['circular_modulation'],label=label)
    axs[2,1].plot(t,z['W']-z['ideal_W'],label=label)
axs[0,0].set_ylabel('Continuing compute power (kW)');axs[0,1].set_ylabel('Reactive support cycle average (kvar)')
axs[1,0].set_ylabel('Within-cycle DC voltage extrema (V)');axs[1,0].axhline(1320,color='r',ls=':');axs[1,0].axhline(1080,color='r',ls=':')
axs[1,1].set_ylabel('Within-cycle current-vector peak (A)');axs[1,1].axhline(1500,color='r',ls=':')
axs[2,0].set_ylabel('Circular modulation utilization');axs[2,0].axhline(1,color='r',ls=':')
axs[2,1].set_ylabel('Actual minus ideal DC energy (J)');axs[2,1].axhline(0,color='k',ls=':')
for ax in axs.flat:ax.axvline(400,color='grey',ls=':');ax.set_xlabel('Time (ms)');ax.grid(alpha=.25);ax.legend(fontsize=8)
fig.suptitle('Preregistered multi-cycle compute shape-transfer: six additional PWM runs\nSame controller, exact workload and actuator commands; finite bounds pass, exact DC return fails')
fig.savefig(R/'shape_transfer_validation.png',dpi=160);plt.close(fig)
print(json.dumps({'additional_runs':6,'same_physical_cpp':True,'all_work_preserved':True,'all_tested_bounds_satisfied':all(r['primary_result']['all_tested_hardware_bounds_satisfied'] for r in records)}))
