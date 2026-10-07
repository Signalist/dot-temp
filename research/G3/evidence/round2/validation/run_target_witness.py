"""Apply stored analytic command polynomials to independent physical plant.

No admission solver/model is imported. All values derive from the NPZ witness.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess
import numpy as np
from run_reference_tests import run,ROOT

def convert(path,extension=.1):
    z=dict(np.load(path));par=json.loads(str(z['par_json']));t=z['t'];name=path.stem
    horizon=t[-1]+extension
    up=np.vstack([z['upoly'],np.zeros((2,4))])*1000
    data=np.c_[np.r_[t,horizon],np.r_[z['p'],z['p'][-1]]*1000,np.r_[z['q'],z['q'][-1]]*1000,np.r_[z['d'],z['d'][-1]]*1000,up]
    np.savetxt(ROOT/f'{name}_input.csv',data,delimiter=',',header='t,p_grid,q_support,d,u,uc1,uc2,uc3',comments='',fmt='%.17g')
    pp=dict(Vrms=par['v']*1000*np.sqrt(1.5),f=par['omega']/(2*np.pi),L=par['L'],R=par['R'],C=par['Cdc'],W0=.5*par['Cdc']*(par['vdc0']*1000)**2,B0=par['B0']*1000,b0=0.,tau=par['tau'],umax=par['umax']*1000,ramp=par['ramp']*1000,alpha=2000.)
    return name,z,par,pp

def ideal(t,z,key):
    knots=z['t'];k=np.clip(np.searchsorted(knots,t,side='right')-1,0,len(knots)-2)
    s=(t-knots[k])/(knots[k+1]-knots[k]);s=np.clip(s,0,1)
    if key=='b':co=np.c_[z['b'][:-1],z['a'],z['c'],np.zeros(len(z['c']))]
    else:co=z[key+'poly']
    v=np.sum(co[k]*s[:,None]**np.arange(4),axis=1)*1000
    if key=='b':v=np.where(t>knots[-1],0,v)
    return v

def main():
    parser=argparse.ArgumentParser();parser.add_argument('witness',type=Path);parser.add_argument('--suite',choices=['full','boundary','shape'],default='full');args=parser.parse_args()
    path=args.witness.resolve();name,z,par,params=convert(path)
    subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra','-o',str(ROOT/'rectifier'),str(ROOT/'rectifier.cpp')],check=True)
    result={'source':str(path),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'model':'independent abc RL filter, ideal two-level bridge, event-aligned PWM','parameters':params,'limits':{k:par[k] for k in ['vdcmin','vdcmax','imax','bmax','umax','ramp','Bmin','Bmax']},'case_alpha_kW':float(z['alpha']),'case_beta_kvar':float(z['beta']),'analytic_margin_kJ':float(z['sigma']),'service_horizon_s':par['T'],'continued_horizon_s':par['T']+.1,'extension':f"After {par['T']}s hold p=p0,q=0,d=650kW,u=0 through {par['T']+.1}s, no state reset",'runs':[]}
    traces={}
    suite=[('avg',1e-6,10000),('pwm',2e-6,10000),('pwm',1e-6,10000),('pwm',.5e-6,10000),('avg',.5e-6,20000),('pwm',.5e-6,20000)]
    if args.suite in ['boundary','shape']:
        suite=[('pwm',1e-6,10000),('pwm',.5e-6,10000)]
        if args.suite=='boundary' and float(z['beta'])==800:suite=[('avg',1e-6,10000)]+suite
    result['suite']=args.suite
    for mode,dt,fs in suite:
        a,r=run(name,mode,dt,fs,params);traces[(mode,dt,fs)]=a
        t=a['t'];active=t<=par['T']+1e-12
        expected={key:ideal(t,z,key) for key in ['W','B','b']}
        for key in expected:
            r[key+'_max_abs_analytic_difference_initial_horizon']=float(np.max(np.abs(a[key][active]-expected[key][active])))
        for tv in [par['T'],par['T']+.1]:
            k=int(np.argmin(np.abs(t-tv)));r[f'state_at_{tv:.3f}s']={key:float(a[key][k]) for key in ['W','B','b','id','iq','filter_energy','energy_closure']}
            r[f'state_at_{tv:.3f}s']['W_error_J']=float(a['W'][k]-params['W0']);r[f'state_at_{tv:.3f}s']['B_error_J']=float(a['B'][k]-params['B0'])
        r['margins_full_horizon']={
            'V_lower_V':float(np.min(a['Vmin'])-par['vdcmin']*1000),
            'V_upper_V':float(par['vdcmax']*1000-np.max(a['Vmax'])),
            'instant_current_amplitude_A':float(par['imax']*1000-np.max(a['Imax'])),
            'B_lower_J':float(np.min(a['B'])-par['Bmin']*1000),
            'B_upper_J':float(par['Bmax']*1000-np.max(a['B'])),
            'b_peak_W':float(par['bmax']*1000-np.max(np.abs(a['b']))),
            'PWM_duty_utilization':float(1-np.max(a['modulation'])),
            'circular_modulation_utilization':float(1-np.max(a['circular_modulation']))}
        r['margins_full_horizon']['b_ramp_W_per_s']=float(par['ramp']*1000-r['actual_bdot_peak_W_per_s'])
        r['margins_full_horizon']['requested_u_W']=float(par['umax']*1000-r['requested_u_peak_W'])
        r['all_tested_hardware_bounds_satisfied']=all(v>=-1e-6 for v in r['margins_full_horizon'].values())
        r['tracking_service_horizon']={key+'_rms_error':float(np.sqrt(np.mean((a[key][active]-a[cmd][active])**2))) for key,cmd in [('Pmean','Pcmd'),('Qmean','Qcmd')]}
        if abs(par['T']-.2)<1e-10:
            r['margins_all_0p3s']=r['margins_full_horizon'];r['tracking_horizon_0p2s']=r['tracking_service_horizon']
        np.savez_compressed(ROOT/(r['trace'].replace('.csv','_comparison.npz')),**{key:a[key] for key in a.dtype.names},**{'ideal_'+key:v for key,v in expected.items()})
        result['runs'].append(r)
    result['convergence']=[]
    for dt in [2e-6,1e-6]:
        if ('pwm',dt,10000) not in traces or ('pwm',dt/2,10000) not in traces:continue
        aa=traces[('pwm',dt,10000)];bb=traces[('pwm',dt/2,10000)]
        result['convergence'].append(dict(coarse_step=dt,fine_step=dt/2,**{key+'_max_abs_difference':float(np.max(np.abs(aa[key]-bb[key]))) for key in ['W','B','b','Pmean','Qmean','Imax']}))
    (ROOT/f'{name}_TARGET_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
