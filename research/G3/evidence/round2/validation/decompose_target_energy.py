"""Independent polynomial integration of ideal energy flows and measured gaps."""
from pathlib import Path
import json
import numpy as np
from run_target_witness import ideal

R=Path(__file__).resolve().parent
def exact_requested_integrals(z,params,tf):
    t=np.r_[z['t'],max(float(z['t'][-1])+.1,tf)]
    p=np.r_[z['p'],z['p'][-1]]*1000;q=np.r_[z['q'],z['q'][-1]]*1000;d=np.r_[z['d'],z['d'][-1]]*1000
    vp=params['Vrms']*np.sqrt(2/3);losscoef=params['R']/(1.5*vp**2)
    vals=dict(grid_energy=0.,loss_energy=0.,load_energy=0.)
    for k in range(len(t)-1):
        h=t[k+1]-t[k];x=np.clip((tf-t[k])/h,0,1)
        if x==0:continue
        pp=p[k];dp=p[k+1]-pp;qq=q[k];dq=q[k+1]-qq;dd=d[k];ddelta=d[k+1]-dd
        vals['grid_energy']+=h*(pp*x+dp*x*x/2)
        vals['load_energy']+=h*(dd*x+ddelta*x*x/2)
        vals['loss_energy']+=losscoef*h*((pp*pp+qq*qq)*x+(pp*dp+qq*dq)*x*x+(dp*dp+dq*dq)*x**3/3)
    vals['filter_energy']=params['L']/(3*vp**2)*(np.interp(tf,t,p)**2+np.interp(tf,t,q)**2)
    vals['battery_energy']=params['B0']-float(ideal(np.array([tf]),z,'B')[0])
    return vals

def main():
    records=[]
    for f in sorted(R.glob('*_TARGET_RESULTS.json')):
        source=json.loads(f.read_text());z=dict(np.load(source['source']));params=source['parameters'];case=f.stem.replace('_TARGET_RESULTS','')
        T=float(z['t'][-1]);out={'case':case,'service_horizon_s':T,'continued_horizon_s':T+.1,'sign_convention':'Each signed contribution sums to W_actual-W_ideal; numerical residual retained','runs':[]}
        for run in source['runs']:
            a=np.genfromtxt(R/run['trace'],delimiter=',',names=True)
            row={'mode':run['mode'],'dt':run['dt'],'fs':run['fs'],'checkpoints':[]}
            for tf in [T,T+.1]:
                k=int(np.argmin(np.abs(a['t']-tf)));ref=exact_requested_integrals(z,params,tf)
                terms={
                    'grid_tracking_J':float(a['grid_energy'][k]-ref['grid_energy']),
                    'negative_incremental_copper_J':float(ref['loss_energy']-a['loss_energy'][k]),
                    'negative_filter_endpoint_difference_J':float(ref['filter_energy']-a['filter_energy'][k]),
                    'battery_discharge_difference_J':float(a['battery_energy'][k]-ref['battery_energy']),
                    'negative_load_integration_difference_J':float(ref['load_energy']-a['load_energy'][k]),
                    'numerical_total_energy_residual_J':float(a['energy_closure'][k])}
                actual_gap=float(a['W'][k]-ideal(np.array([tf]),z,'W')[0])
                row['checkpoints'].append({'t':tf,'actual_minus_ideal_W_J':actual_gap,'signed_contributions':terms,'sum_J':sum(terms.values()),'decomposition_error_J':sum(terms.values())-actual_gap,'actual_flows_J':{key:float(a[key][k]) for key in ref},'ideal_flows_J':ref})
            row['baseline_continuation']={'start_s':T,'end_s':T+.1,'W_change_J':float(a['W'][-1]-a['W'][np.argmin(np.abs(a['t']-T))]),'average_W_decline_power_W':float((a['W'][-1]-a['W'][np.argmin(np.abs(a['t']-T))])/.1)}
            if abs(T-.2)<1e-10:row['baseline_0p2_to_0p3']=row['baseline_continuation']
            out['runs'].append(row)
        (R/f'{case}_ENERGY_DECOMPOSITION.json').write_text(json.dumps(out,indent=2)+'\n');records.append(out)
    maxerr=max(abs(x['decomposition_error_J']) for o in records for r in o['runs'] for x in r['checkpoints'])
    print('max decomposition error J',maxerr)
    assert maxerr<1e-6
    for o in records:
        for r in o['runs']:
            if r['mode']=='pwm' and r['fs']==10000 and r['dt']==1e-6:print(o['case'],json.dumps(r,indent=2))
if __name__=='__main__':main()
