"""Independent checks of conservation, physical signs, and convergence."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R=Path(__file__).resolve().parent
data=json.loads((R/'REFERENCE_RESULTS.json').read_text())
tests=[]
def check(name,ok,detail):
    tests.append(dict(name=name,passed=bool(ok),detail=detail))

for run in data['runs']:
    a=np.genfromtxt(R/run['trace'],delimiter=',',names=True)
    name=run['trace']
    check(name+':total_energy_conservation',run['energy_closure_max_J']<.1,run['energy_closure_max_J'])
    check(name+':balanced_abc',run['abc_current_sum_max_A']<1e-7,run['abc_current_sum_max_A'])
    check(name+':DC_bridge_energy',np.max(np.abs(a['W']-19600-a['bridge_energy']+a['load_energy']-a['battery_energy']))<1e-5,'W-W0=bridge input-load+battery discharge')
    check(name+':storage_energy',np.max(np.abs(a['B']-100000+a['battery_energy']))<1e-5,'B-B0=-integral b')
    check(name+':positive_compute_load',np.min(a['dmean'])>0,float(np.min(a['dmean'])))
    check(name+':modulation_no_clipping',np.max(a['clipped'])==0,float(np.max(a['modulation'])))
    wave=np.genfromtxt(R/run['waveform'],delimiter=',',names=True)
    sw=np.column_stack([wave[x] for x in ['sa','sb','sc']]);i=np.column_stack([wave[x] for x in ['ia','ib','ic']]);e=np.column_stack([wave[x] for x in ['ea','eb','ec']])
    if run['mode']=='pwm':check(name+':genuine_binary_switches',np.all((sw==0)|(sw==1)),list(np.unique(sw)))
    check(name+':instantaneous_bridge_power',np.max(np.abs(np.sum(e*i,axis=1)-wave['pdc']))<1e-5,'sum e_k*i_k is bridge DC input power')
    check(name+':DC_current_switch_identity',np.max(np.abs(wave['pdc']/wave['Vdc']-np.sum(sw*i,axis=1)))<1e-7,'i_dc=sum(s_k*i_k); grid->DC sign')
    th=2*np.pi*50*wave['t'];v=np.sqrt(2/3)*690*np.cos(th[:,None]-2*np.pi*np.arange(3)/3)
    p=np.sum(v*i,axis=1)
    q=((v[:,2]-v[:,1])*i[:,0]+(v[:,0]-v[:,2])*i[:,1]+(v[:,1]-v[:,0])*i[:,2])/np.sqrt(3)
    check(name+':abc_power_signs',max(np.max(np.abs(p-wave['P'])),np.max(np.abs(q-wave['Q'])))<1e-5,'Qsupport computed independently from abc cross products')

for case in ['constant','smooth_service']:
    halving=[x for x in data['convergence'] if x['case']==case and x['comparison']=='time_step_halving']
    check(case+':time_step_convergence',halving[1]['W_max_abs_difference']<halving[0]['W_max_abs_difference']/2,[x['W_max_abs_difference'] for x in halving])
    avg=[x for x in data['convergence'] if x['case']==case and x['comparison']=='pwm_vs_average']
    for key in ['W_rms_difference','Pmean_rms_difference','Qmean_rms_difference']:
        values=[x[key] for x in avg]
        check(case+':frequency_convergence:'+key,all(b<a/2 for a,b in zip(values,values[1:])),values)

pwm=np.genfromtxt(R/'smooth_service_pwm_f10000_h1e-06.csv',delimiter=',',names=True)
avg=np.genfromtxt(R/'smooth_service_avg_f10000_h1e-06.csv',delimiter=',',names=True)
wave=np.genfromtxt(R/'smooth_service_pwm_f10000_h1e-06_waveform.csv',delimiter=',',names=True)
fig,axs=plt.subplots(3,2,figsize=(12,10),constrained_layout=True)
for ax,key,cmd,label in [(axs[0,0],'Pmean','Pcmd','Grid import (kW)'),(axs[0,1],'Qmean','Qcmd','Reactive support (kvar)')]:
    ax.plot(pwm['t']*1000,pwm[cmd]/1000,'k--',label='command')
    ax.plot(pwm['t']*1000,pwm[key]/1000,label='10 kHz PWM cycle average');ax.set_ylabel(label);ax.legend()
axs[1,0].plot(pwm['t']*1000,np.sqrt(2*pwm['W']/.02),label='PWM endpoint')
axs[1,0].plot(avg['t']*1000,np.sqrt(2*avg['W']/.02),'--',label='averaged endpoint');axs[1,0].set_ylabel('DC voltage (V)');axs[1,0].legend()
axs[1,1].plot(pwm['t']*1000,pwm['b']/1000,label='actual finite-response b')
axs[1,1].plot(pwm['t']*1000,pwm['umean']/1000,'--',label='u command');axs[1,1].set_ylabel('Battery discharge (kW)');axs[1,1].legend()
axs[2,0].plot(wave['t']*1000,wave['ia'],label='i_a');axs[2,0].plot(wave['t']*1000,wave['ib'],label='i_b');axs[2,0].plot(wave['t']*1000,wave['ic'],label='i_c');axs[2,0].set_ylabel('Actual switched currents (A)');axs[2,0].legend()
axs[2,1].plot(pwm['t']*1000,pwm['energy_closure']*1000);axs[2,1].set_ylabel('Total-energy residual (mJ)')
for ax in axs.flat:ax.set_xlabel('Time (ms)');ax.grid(alpha=.25)
fig.suptitle('Independent abc PWM rectifier: frozen smooth service test\nSynthetic software model, not hardware validation')
fig.savefig(R/'reference_validation.png',dpi=160);plt.close(fig)
results={'passed':all(x['passed'] for x in tests),'tests':tests,'test_count':len(tests)}
(R/'REFERENCE_AUDIT.json').write_text(json.dumps(results,indent=2)+'\n')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(R.iterdir()) if p.is_file() and p.name not in ['REFERENCE_SHA256.json','reference_test.log']}
(R/'REFERENCE_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:results[k] for k in ['passed','test_count']}))
assert results['passed'],[x for x in tests if not x['passed']]
