"""Frozen independent reference cases; no fitting against analytical witnesses."""
from pathlib import Path
import json, subprocess, hashlib
import numpy as np

ROOT=Path(__file__).resolve().parent
PARAMS=dict(Vrms=690.,f=50.,L=100e-6,R=.005,C=.02,Vdc0=1400.,W0=19600.,B0=100000.,b0=0.,tau=.02,umax=500000.,ramp=1e100,alpha=2000.)
def run(name,mode,dt,fs,params=PARAMS):
    stem=f'{name}_{mode}_f{fs:g}_h{dt:g}'
    p=params
    args=[str(ROOT/'rectifier'),str(ROOT/f'{name}_input.csv'),str(ROOT/stem),mode,str(dt),str(fs),str(p['W0']),str(p['B0']),str(p['b0']),str(p['tau']),str(p['umax']),str(p['ramp']),str(p['L']),str(p['R']),str(p['C']),str(p['Vrms']),str(p['alpha'])]
    proc=subprocess.run(args,check=True,text=True,capture_output=True)
    result=json.loads(proc.stdout)
    a=np.genfromtxt(ROOT/f'{stem}.csv',delimiter=',',names=True)
    result.update(case=name,mode=mode,dt=dt,fs=fs,trace=f'{stem}.csv',waveform=f'{stem}_waveform.csv',command=args)
    for key,cmd in [('Pmean','Pcmd'),('Qmean','Qcmd')]:
        error=a[key]-a[cmd]
        result[key+'_rms_error_W']=float(np.sqrt(np.mean(error**2)))
        result[key+'_max_abs_error_W']=float(np.max(np.abs(error)))
        result[key+'_rms_error_after_20ms_W']=float(np.sqrt(np.mean(error[a['t']>.02]**2)))
    result['abc_current_sum_max_A']=float(np.max(np.abs(a['ia']+a['ib']+a['ic'])))
    result['load_min_W']=float(np.min(a['dmean']))
    result['battery_peak_abs_W']=float(np.max(np.abs(a['b'])))
    result['input_sha256']=hashlib.sha256((ROOT/f'{name}_input.csv').read_bytes()).hexdigest()
    (ROOT/f'{stem}.json').write_text(json.dumps(result,indent=2)+'\n')
    return a,result

def inputs():
    t=np.linspace(0,.2,2001)
    v=np.sqrt(2/3)*690; k=.005/(1.5*v*v)
    p0=(1-np.sqrt(1-4*k*650000))/(2*k)
    h=np.where((t>=.04)&(t<=.12),np.sin(np.pi*(t-.04)/.08)**2,0.)
    for name,p,q,u in [('constant',t*0+p0,t*0,t*0),('smooth_service',p0-100000*h,200000*h,100000*h)]:
        np.savetxt(ROOT/f'{name}_input.csv',np.c_[t,p,q,t*0+650000,u],delimiter=',',header='t,p_grid,q_support,d,u',comments='',fmt='%.14g')
    return p0

def main():
    subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra','-o',str(ROOT/'rectifier'),str(ROOT/'rectifier.cpp')],check=True)
    p0=inputs()
    freeze={'timestamp_UTC':'2026-10-03T08:36:04Z','scope':'Independent abc model reference tests frozen before the admission witness','parameters':PARAMS,'baseline_import_W':p0,'case_definitions':{'constant':'d=650kW; p0 solves p0 - R*p0^2/(1.5*Vp^2)=d; q=0; u=0','smooth_service':'h=sin(pi*(t-.04)/.08)^2 on [.04,.12], otherwise 0; p=p0-100kW*h; q=200kvar*h; d=650kW; u=100kW*h'},'initialization':'iabc exactly initial reference, W0/B0/b0 fixed, controller integral zero, no warmup or state preconditioning','no_claim':'Synthetic software model only; no hardware or third-party simulator execution'}
    (ROOT/'REFERENCE_FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
    results=[];traces={}
    for case in ['constant','smooth_service']:
        for mode,dt,fs in [('avg',1e-6,10000),('pwm',2e-6,10000),('pwm',1e-6,10000),('pwm',.5e-6,10000),('avg',1e-6,5000),('pwm',1e-6,5000),('avg',1e-6,20000),('pwm',1e-6,20000),('avg',.5e-6,40000),('pwm',.5e-6,40000)]:
            a,r=run(case,mode,dt,fs);results.append(r);traces[(case,mode,dt,fs)]=a
    conv=[]
    for case in ['constant','smooth_service']:
        for dt in [2e-6,1e-6]:
            a=traces[(case,'pwm',dt,10000)];b=traces[(case,'pwm',dt/2,10000)]
            conv.append(dict(case=case,comparison='time_step_halving',h_coarse_s=dt,h_fine_s=dt/2,**{x+'_max_abs_difference':float(np.max(np.abs(a[x]-b[x]))) for x in ['W','B','b','Pmean','Qmean','id','iq','Imax']}))
        for fs in [5000,10000,20000,40000]:
            dt=.5e-6 if fs==40000 else 1e-6
            a=traces[(case,'pwm',dt,fs)];b=traces[(case,'avg',dt,fs)]
            conv.append(dict(case=case,comparison='pwm_vs_average',fs_Hz=fs,**{x+'_rms_difference':float(np.sqrt(np.mean((a[x]-b[x])**2))) for x in ['W','Pmean','Qmean','id','iq','Imax']}))
    (ROOT/'REFERENCE_RESULTS.json').write_text(json.dumps({'runs':results,'convergence':conv},indent=2)+'\n')
    print(json.dumps({'runs':len(results),'worst_energy_closure_J':max(r['energy_closure_max_J'] for r in results),'convergence':conv},indent=2))
if __name__=='__main__':main()
