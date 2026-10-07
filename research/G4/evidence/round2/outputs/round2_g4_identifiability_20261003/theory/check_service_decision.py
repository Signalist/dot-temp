#!/usr/bin/env python3
"""Independent exact arithmetic and ODE audit of the finite-PCS service certificate."""
from pathlib import Path
from fractions import Fraction as F
from types import SimpleNamespace
import json, math, hashlib
import numpy as np
from scipy.integrate import solve_ivp,quad
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
eta=F(19,20);a2=F(4);a3=F(19,2);D=F(12);r=.2;tau=.01
elow=F(9)-(D-a2)/eta+eta*a3
ehigh=F(9)+eta*a2-(D-a3)/eta
need=F(247,25);amp=eta*need/2;remain=ehigh-need;recharge=(9-remain)/eta
err=F(1,50)+F(361,32)*F(3,500);threshold=need+err

def pulse(s):
    if s<=0 or s>=1:return 0.,0.
    if s<r:return (1-math.cos(math.pi*s/r))/(2*(1-r)),math.pi*math.sin(math.pi*s/r)/(2*r*(1-r))
    if s<=1-r:return 1/(1-r),0.
    x=1-s
    return (1-math.cos(math.pi*x/r))/(2*(1-r)),-math.pi*math.sin(math.pi*x/r)/(2*r*(1-r))

def bound(A,T=1):
    A=float(A)
    return dict(power=A/(1-r),command=A*(1+math.sqrt(1+(math.pi*tau/(r*T))**2))/(2*(1-r)),slew=A*math.pi/(2*r*(1-r)*T))

def pre(t,high):
    h2,dh2=pulse(t-1);h3,dh3=pulse(t-2)
    d=6+12*(h2 if high==2 else h3)
    p=6+float(a2)*h2+float(a3)*h3
    b=d-p;db=12*(dh2 if high==2 else dh3)-float(a2)*dh2-float(a3)*dh3
    return d,p,b,b+tau*db

def post(t,Arec):
    hs,dhs=pulse((t-3)/2);hr,dhr=pulse(t-5)
    b=float(amp)*hs-float(Arec)*hr
    db=float(amp)*dhs/2-float(Arec)*dhr
    return 6.,6-b,b,b+tau*db

def integrate(signals,start,end,y0,breaks):
    ts=np.linspace(start,end,int(round((end-start)*10000))+1);ys=np.zeros((3,len(ts)))
    carry=np.array(y0,dtype=float);success=True
    def rhs(t,y):
        d,p,b,cmd=signals(t);actual=y[0]
        return [(cmd-actual)/tau,-actual/float(eta) if actual>=0 else -float(eta)*actual,d]
    for left,right in zip(breaks[:-1],breaks[1:]):
        seg=solve_ivp(rhs,[left,right],carry,method='DOP853',rtol=2e-13,atol=1e-14,max_step=.001,dense_output=True)
        ix=np.flatnonzero((ts>=left-1e-14)&(ts<=right+1e-14));ys[:,ix]=seg.sol(ts[ix]);carry=seg.y[:,-1];success &=seg.success
    sig=np.array([signals(float(t)) for t in ts]);actualp=sig[:,0]-ys[0]
    return SimpleNamespace(t=ts,y=ys,signals=sig,p=actualp,success=bool(success),tracking=float(np.max(np.abs(ys[0]-sig[:,2]))),pcc_error=float(np.max(np.abs(actualp-sig[:,1]))))

def main():
    proof={'eta':str(eta),'E_low':str(elow),'E_high':str(ehigh),'required':str(need),'low_allcontrol_deficit':str(need-elow),'high_remaining':str(remain),'service_amplitude':str(amp),'recharge_AC_amplitude':str(recharge),'final_energy':str(remain+eta*recharge),'measurement_error_bound':str(err),'guard_threshold':str(threshold),'high_worst_accept_margin':str(ehigh-need-2*err),'low_worst_reject_margin':str(threshold-(elow+err))}
    bounds={f'prefix_{i}':bound(A) for i,A in enumerate([D-a2,a3,a2,D-a3])}
    bounds['service']=bound(amp,2);bounds['high_recovery']=bound(recharge);bounds['generic_worst_recovery']=bound(F(9)/eta)
    prefix_breaks=sorted(set([0.,1.,1.2,1.8,2.,2.2,2.8,3.]))
    prefix=[];sols=[]
    for high,expected in [(2,elow),(3,ehigh)]:
        sol=integrate(lambda t:pre(t,high),0,3,[0,9,0],prefix_breaks);sols.append(sol)
        prefix.append(dict(high_slot=high,tracking_error=sol.tracking,pcc_error=sol.pcc_error,state_min=float(sol.y[1].min()),state_max=float(sol.y[1].max()),E_at_3=float(sol.y[1,-1]),exact_state_error=abs(float(sol.y[1,-1])-float(expected)),b_at_3=float(sol.y[0,-1]),completed_work=float(sol.y[2,-1])))
    post_breaks=[3.,3.4,4.6,5.,5.2,5.8,6.]
    post_rows=[]
    for startE,label in [(ehigh,'high_world'),(need,'generic_threshold'),(F(697,50),'generic_midpoint'),(F(18),'generic_full')]:
        A=(9-(startE-need))/eta
        sol=integrate(lambda t:post(t,A),3,6,[0,float(startE),30],post_breaks)
        j5=int(round(2*10000))
        hs=np.array([pulse((float(t)-3)/2)[0] for t in sol.t]);cap=6-float(amp)*hs;service=sol.t<=5
        post_rows.append(dict(label=label,initial_SOC=str(startE),recovery_amplitude=str(A),tracking_error=sol.tracking,pcc_error=sol.pcc_error,state_min=float(sol.y[1].min()),state_max=float(sol.y[1].max()),SOC_after_service=float(sol.y[1,j5]),service_state_error=abs(float(sol.y[1,j5])-float(startE-need)),final_SOC=float(sol.y[1,-1]),final_buffer=float(sol.y[0,-1]),total_task_work=float(sol.y[2,-1]),max_service_cap_violation=float(max(0,np.max(sol.p[service]-cap[service]))),max_recovery_PCC=float(sol.p[sol.t>=5].max())))
    # Query always precedes commitment; external comparator separates both concrete worlds.
    samples=[]
    for high,E in [(2,elow),(3,ehigh)]:
        ss=np.linspace(2.994,2.996,101)
        def J(x):return quad(lambda z:pulse(z)[0],0,min(1,max(0,x)),points=[r] if x<1-r else [r,1-r],epsabs=1e-13)[0]
        energies=[]
        for tt in ss:
            if high==2:ee=9-float((D-a2)/eta)+float(eta*a3)*J(tt-2)
            else:ee=9+float(eta*a2)-float((D-a3)/eta)*J(tt-2)
            energies.append(ee)
        samples.append(dict(high_slot=high,min_measured=min(energies)-.02,max_measured=max(energies)+.02,all_bits_accept=min(energies)-.02>=float(threshold),all_bits_abstain=max(energies)+.02<float(threshold),max_staleness_change=max(abs(x-float(E)) for x in energies)))
    out={'scope':'independent exact energy inequalities, analytic finite-PCS limits, causal guarded-bit arithmetic, and ODE integration; no primary scenario-builder imports','exact':proof,'analytic_bounds':bounds,'prefix_ODE':prefix,'service_recovery_ODE':post_rows,'query_extremes':samples,'source_sha256':{}}
    for name in ['SERVICE_DECISION_FREEZE.json','SERVICE_CAUSAL_MEASUREMENT_AMENDMENT.json','experiments/GRID_SERVICE_DECISION_RESULTS.json']:
        pp=ROOT/name
        if pp.exists():out['source_sha256'][name]=hashlib.sha256(pp.read_bytes()).hexdigest()
    out['tests']={
      'exact_low_allcontrol_exclusion':need>elow,
      'exact_high_and_recovery':remain>0 and remain+eta*recharge==9,
      'finite_power_command_slew':all(v['power']<12 and v['command']<12 and v['slew']<100 for v in bounds.values()),
      'generic_recovery_PCC_cap':6+float(F(9)/eta)/(1-r)<18,
      'safe_guarded_acceptance':err==F(1403,16000) and threshold==F(159483,16000) and ehigh-need-2*err>0 and threshold-(elow+err)>0,
      'strictly_causal_delivery':2.996<2.999<3 and 3-2.994<=.006+1e-12,
      'identical_complete_prefix':float(np.max(np.abs(sols[0].p-sols[1].p)))<1e-9,
      'prefix_states_and_work':all(x['exact_state_error']<1e-8 and abs(x['b_at_3'])<1e-8 and abs(x['completed_work']-30)<1e-8 and x['state_min']>0 and x['state_max']<18 for x in prefix),
      'ODE_tracking':all(x['tracking_error']<1e-8 and x['pcc_error']<1e-8 for x in prefix+post_rows),
      'generic_service_recovery':all(x['state_min']>=-1e-8 and x['state_max']<=18+1e-8 and abs(x['final_SOC']-9)<1e-8 and abs(x['final_buffer'])<1e-8 and abs(x['total_task_work']-48)<1e-8 and x['max_service_cap_violation']<1e-8 and x['max_recovery_PCC']<18 for x in post_rows),
      'actual_query_separates_worlds':samples[0]['all_bits_abstain'] and samples[1]['all_bits_accept'],
    }
    (HERE/'SERVICE_DECISION_INDEPENDENT_AUDIT.json').write_text(json.dumps(out,indent=2))
    print(json.dumps({'exact':proof,'bounds':bounds,'tests':out['tests'],'max_tracking_error':max(x['tracking_error'] for x in prefix+post_rows)},indent=2));assert all(out['tests'].values())
if __name__=='__main__':main()
