"""Read-only existing-data + algebraic diagnostic. No converter ODE, policy, or tuning.
The development harmonic surrogate is NOT a validated plant orbit/certificate.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from scipy.optimize import brentq, minimize_scalar
ROOT = Path(__file__).resolve().parents[2]
D = json.loads((ROOT/'protocol/GATE_A_LOCKED_V2_1.json').read_text())
S=D['S_base_VA']; eta=D['eta_dc_dc']; R=D['battery_source_ramp_up_W_per_s']; tau=D['battery_source_tau_s']; K=D['dc_energy_feedback_gain_per_s']
Wref=.5*D['C_dc_F']*D['V_dc_initial_V']**2
Wmin=Wref*D['V_dc_min_pu']**2; Wmax=Wref*D['V_dc_max_pu']**2
I=D['I_phase_peak_base_A']; E=D['V_phase_peak_base_V']; L=D['filter_L_H']+D['grid_L_H']; Rt=D['filter_R_ohm']+D['grid_R_ohm']
WLmax=.75*L*I**2; lossmin=D['inverter_loss_constant_W']; lossmax=lossmin+D['inverter_loss_current_squared_W_at_1pu']+1.5*Rt*I**2
Pmin=D['battery_terminal_power_min_W']; Pmax=D['battery_terminal_power_max_W']
def h(p): return np.where(np.asarray(p)>=0,eta*np.asarray(p),np.asarray(p)/eta)
def hinv(q): return np.where(np.asarray(q)>=0,np.asarray(q)/eta,eta*np.asarray(q))
def H(p): return np.where(np.asarray(p)>=0,.5*eta*np.asarray(p)**2,.5*np.asarray(p)**2/eta)
def ramp_integral(p,t,up):
    p=np.asarray(p);t=np.asarray(t); limit=Pmax if up else Pmin; sg=1 if up else -1
    t1=np.minimum(t,np.maximum(0,(limit-p)/(sg*R))); q=p+sg*R*t1
    return (H(q)-H(p))/(sg*R)+(t-t1)*h(limit)
def margins(p,w,wl,rho,T=.15):
    p=np.asarray(p); w=np.asarray(w); wl=np.asarray(wl)
    bp=rho*S+lossmax; bm=-rho*S+lossmin
    tp=np.clip((p-hinv(bp))/R,0,T);tm=np.clip((hinv(bm)-p)/R,0,T)
    F=ramp_integral(p,tp,False)-bp*tp; G=bm*tm-ramp_integral(p,tm,True)
    return F-(Wmax+WLmax-w-wl), G-(w+wl-Wmin),tp,tm

def equilibrium(P,Q):
    P=np.asarray(P); rg=D['grid_R_ohm'];rf=D['filter_R_ohm']; xg=D['omega_base_rad_s']*D['grid_L_H']; xt=D['omega_base_rad_s']*L
    aa=rg**2+xg**2;bb=E**2+(2/1.5)*(rg*P+xg*Q);cc=(P**2+Q**2)/2.25
    disc=bb**2-4*aa*cc
    if np.any(disc<0): raise ValueError('No low-current nominal equilibrium')
    j=2*cc/(bb+np.sqrt(disc));ip=(P/1.5-rg*j)/E+1j*(xg*j-Q/1.5)/E;u=E+(Rt+1j*xt)*ip
    q=P+1.5*rf*j+lossmin+D['inverter_loss_current_squared_W_at_1pu']*j/I**2
    jp=((2/1.5)*rg*j-2*P/2.25)/(2*aa*j-bb)
    qp=1+(1.5*rf+D['inverter_loss_current_squared_W_at_1pu']/I**2)*jp
    dp=np.where(q>=0,qp/eta,eta*qp)
    return np.sqrt(j)/I,hinv(q),abs(u)/(D['svpwm_linear_voltage_derating']*D['V_dc_initial_V']/np.sqrt(3)),dp

# These engineering margins/grids are declared before any controller comparison.
rule={'bias_interval_W':[-50000,0], 'Q_grid_var':[0,300000,700000], 'amplitude_grid_W':list(range(100000,1000001,100000)),
      'nominal_I_design_limit_pu':.90,'nominal_Pb_design_limit_W':.90*Pmax,
      'frequency_grid_Hz':[.1,.25,.5,1.0], 'omega_tau_limit':.10,'source_equilibrium_slew_fraction_of_hard_R':.60,
      'status':'Algebraic preregistration candidate; numerical screening, not validated dynamic feasibility'}
audit=[]
for A in rule['amplitude_grid_W']:
    p=np.linspace(-A-50000,A,20001); rows=[]
    for Q in rule['Q_grid_var']:
        i,pb,m,dp=equilibrium(p,Q)
        rows.append({'Q_var':Q,'max_I_pu':float(max(i)),'max_abs_Pb_W':float(max(abs(pb))),'max_modulation_use_at_1400V':float(max(m)),'max_abs_d_Pbeq_d_Ppcc':float(max(abs(dp))), 'max_abs_Spcc_VA':float(max(np.hypot(p,Q)))})
    passed=bool(A+50000<=D['converter_active_service_limit_W'] and max(x['max_I_pu'] for x in rows)<=.90 and max(x['max_abs_Pb_W'] for x in rows)<=.90*Pmax and max(x['max_modulation_use_at_1400V'] for x in rows)<=1 and max(x['max_abs_Spcc_VA'] for x in rows)<=S)
    audit.append({'A_W':A,'nominal_screen_pass':passed,'Q_results':rows})
selected=max(x['A_W'] for x in audit if x['nominal_screen_pass'])
dpmax=max(x['max_abs_d_Pbeq_d_Ppcc'] for x in next(x for x in audit if x['A_W']==selected)['Q_results'])
faudit=[{'f_Hz':f,'omega_tau':2*np.pi*f*tau,'max_equilibrium_source_slew_bound_W_per_s':2*np.pi*f*selected*dpmax,'pass':bool(2*np.pi*f*tau<=.1 and 2*np.pi*f*selected*dpmax<=.6*R)} for f in rule['frequency_grid_Hz']]
fsel=max(x['f_Hz'] for x in faudit if x['pass'])

# Existing final frozen-bias cycle only; no new ODE or trajectory interpolation.
pf=ROOT/'gate_a_extension/results/signed_periodic_h1e-05.npz'; z=np.load(pf)
a=z['endpoint_trace'];c=z['endpoint_columns'].tolist(); a=a[(a[:,0]>=9.6-1e-10)&(a[:,0]<=10.6+1e-10)]
x=z['interval_extrema'];xc=z['interval_columns'].tolist();x=x[(x[:,0]>=9.6-1e-10)&(x[:,1]<=10.6+1e-10)]
old={'phase_sampling':'Existing 100 us endpoints, final cycle [9.6,10.6] s; interval-extrema bounds also reported; no new converter integration',
     'endpoint_Pb_W':[float(a[:,c.index('Pb')].min()),float(a[:,c.index('Pb')].max())],
     'endpoint_Wdc_J':[float(a[:,c.index('Wdc')].min()),float(a[:,c.index('Wdc')].max())],
     'interval_max_abs_Pb_W':float(x[:,xc.index('Pb_absmax')].max()),
     'interval_Wdc_bounds_J':[float(Wref*x[:,xc.index('Vdcmin')].min()**2),float(Wref*x[:,xc.index('Vdcmax')].max()**2)],
     'rho_results':[]}
for rho in [.85,.75,.475,.4]:
    mp,mm,tp,tm=margins(a[:,c.index('Pb')],a[:,c.index('Wdc')],a[:,c.index('WL')],rho)
    pbabs=old['interval_max_abs_Pb_W']
    # These initial derivative signs, plus monotonic source envelopes, establish zero prefix maxima at every recorded-cycle continuous phase, conditional on supplied extrema.
    upper_initial_derivative_bound=float(h(pbabs)-rho*S-lossmax)
    lower_initial_derivative_bound=float(-rho*S+lossmin-h(-pbabs))
    old['rho_results'].append({'rho':rho,'endpoint_max_upper_margin_J':float(max(mp)),'endpoint_max_lower_margin_J':float(max(mm)), 'all_continuous_phases_prefix_maxima_zero_from_extrema':bool(upper_initial_derivative_bound<0 and lower_initial_derivative_bound<0), 'upper_Fprime_global_upper_W':upper_initial_derivative_bound,'lower_Gprime_global_upper_W':lower_initial_derivative_bound})

# Branch-local harmonic proxy, NOT a full nonlinear signed orbit. No losses/bias in q=A sin(phi), ideal source-side current estimate for WL. Used only to derive falsifiable direction/scale.
A=float(selected); omega=2*np.pi*fsel
def state(phi):
    phi=np.asarray(phi);g=np.where(np.sin(phi)>=0,eta,1/eta);den=g*K-tau*omega**2+1j*omega
    gain=-1j*tau*omega/den
    w=A*(gain.real*np.sin(phi)+gain.imag*np.cos(phi)); dw=A*(gain.real*np.cos(phi)-gain.imag*np.sin(phi))
    pb=(A*np.sin(phi)+omega*dw)/g
    wl=WLmax*(A*np.sin(phi)/S)**2
    return pb,Wref+w,wl
phis=np.linspace(0,2*np.pi,16385)
def peak(rho,side):
    vals=margins(*state(phis),rho)[side];j=int(np.argmax(vals));step=2*np.pi/16384
    opt=minimize_scalar(lambda ph:-float(margins(*state(ph),rho)[side]),bounds=(phis[j]-step,phis[j]+step),method='bounded',options={'xatol':1e-13})
    return float(opt.x%(2*np.pi)),float(-opt.fun)
def intervals(rho,side):
    vals=margins(*state(phis),rho)[side];roots=[]
    for j in np.flatnonzero(vals[:-1]*vals[1:]<0):roots.append(float(brentq(lambda ph:float(margins(*state(ph),rho)[side]),phis[j],phis[j+1])))
    cuts=[0,*roots,2*np.pi];return [[a*180/np.pi,b*180/np.pi] for a,b in zip(cuts[:-1],cuts[1:]) if float(margins(*state((a+b)/2),rho)[side])>0]
crit=[float(brentq(lambda rho:peak(rho,s)[1],.05,.85)) for s in [0,1]]
near=float(np.ceil(1000*max(crit))/1000)
proxy={'warning':'Branch-local harmonic algebra only; no signed-branch crossing validity, loss/bias fit, full-state orbit, or plant feasibility claim','A_W':A,'f_Hz':fsel,'Q_var':0,'bias_W':0,
       'upper_critical_rho_surrogate':crit[0],'lower_critical_rho_surrogate':crit[1], 'near_rho_rule':'ceil(1000*max(rho_critical_upper,rho_critical_lower))/1000, from surrogate before controllers','near_rho':near,'cases':[]}
for rho in [.75,near,.4]:
    pp,pm=peak(rho,0);np_,nm=peak(rho,1)
    proxy['cases'].append({'rho':rho,'upper_peak_phi_deg':pp*180/np.pi,'upper_peak_margin_J':pm,'upper_margin_at_positive_request_peak_J':float(margins(*state(np.pi/2),rho)[0]),'upper_gain_over_request_peak_J':float(pm-margins(*state(np.pi/2),rho)[0]),'upper_shift_from_request_peak_deg':pp*180/np.pi-90,'upper_excluded_intervals_deg':intervals(rho,0),'lower_peak_phi_deg':np_*180/np.pi,'lower_peak_margin_J':nm,'lower_margin_at_negative_request_peak_J':float(margins(*state(3*np.pi/2),rho)[1]),'lower_gain_over_request_peak_J':float(nm-margins(*state(3*np.pi/2),rho)[1]),'lower_shift_from_request_peak_deg':np_*180/np.pi-270,'lower_excluded_intervals_deg':intervals(rho,1)})
# If F/G is everywhere maximized at t=0, a headroom-only minimum is not an energy-obstruction phase peak.
for case in proxy['cases']:
    for prefix,side in [('upper',0),('lower',1)]:
        phi=case[prefix+'_peak_phi_deg']*np.pi/180
        active=float(margins(*state(phi),case['rho'])[2+side])>0
        case[prefix+'_positive_prefix_active']=active
        if not active:
            for suffix in ['peak_phi_deg','shift_from_request_peak_deg','gain_over_request_peak_J']:
                case[prefix+'_'+suffix]=None
proxy['fixed_same_request_pairs_at_rho_04']=[]
for angles in [(60,120),(75,105),(240,300),(255,285)]:
    side=0 if angles[0]<180 else 1
    states=[state(x*np.pi/180) for x in angles]
    proxy['fixed_same_request_pairs_at_rho_04'].append({'phases_deg':angles,'side':['upper','lower'][side],'q_W':[float(A*np.sin(x*np.pi/180)) for x in angles], 'Wdc_J':[float(s[1]) for s in states], 'Pb_W':[float(s[0]) for s in states], 'margin_J':[float(margins(*s,.4)[side]) for s in states]})
checks={}
for p,t in [(815639.6755381202,.02),(-400000,.15),(300000,.15)]:
    from scipy.integrate import quad
    for up in [False,True]:
        expected=quad(lambda tt:float(h(np.clip(p+(R if up else -R)*tt,Pmin,Pmax))),0,t,epsabs=1e-7,points=[v for v in [-p/(R if up else -R)] if 0<v<t])[0]
        checks[f'integral_{p}_{t}_{up}']=abs(float(ramp_integral(p,t,up))-expected)
assert max(checks.values())<1e-4

# Primary phase metric: greatest retained voltage excluded by the necessary certificate.
def rho_crit_formula(phi,side):
    pb,w,wl=state(phi);g=eta if side==0 else 1/eta
    head=(Wmax+WLmax-w-wl) if side==0 else (w+wl-Wmin)
    return ((g*pb-lossmax-np.sqrt(2*g*R*head)) if side==0 else (-g*pb+lossmin-np.sqrt(2*g*R*head)))/S
critical_phase=[]
for side in [0,1]:
    ppeak=(.5+side)*np.pi
    opt=minimize_scalar(lambda ph:-float(rho_crit_formula(ph,side)),bounds=(ppeak-.5,ppeak+.5),method='bounded',options={'xatol':1e-13})
    phi=float(opt.x);rc=float(-opt.fun);rcpeak=float(rho_crit_formula(ppeak,side));st=state(phi);g=eta if side==0 else 1/eta;head=float(Wmax+WLmax-st[1]-st[2] if side==0 else st[1]+st[2]-Wmin)
    tstar=float(np.sqrt(2*head/(g*R)))
    critical_phase.append({'side':['upper','lower'][side],'phase_deg':phi*180/np.pi,'shift_from_request_extremum_deg':(phi-ppeak)*180/np.pi,'rho_critical':rc,'rho_critical_at_request_extremum':rcpeak,'gain_rho_pu':rc-rcpeak,'critical_prefix_s':tstar,'equivalent_J_first_order':(rc-rcpeak)*S*tstar,'margin_J_at_request_extremum_when_rho_equals_phasewise_max':float(margins(*state(ppeak),rc)[side])})
proxy['primary_critical_voltage_phase_metric']=critical_phase

# Exact source-command/lag/ramp envelope; no new plant trajectory.
def env_time(p,target,rr,tt,up):
    p=np.asarray(p);target=np.asarray(target);sg=1 if up else -1;u=Pmax if up else Pmin
    gap=sg*(u-p);tr=np.maximum(0,(gap-rr*tt)/rr);qtr=p+sg*rr*tr;distance=sg*(target-p)
    lin=distance/rr
    ratio=np.maximum(1e-300,(u-target)/(u-qtr))
    expo=tr-tt*np.log(ratio)
    return np.maximum(0,np.where(distance<=rr*tr,lin,expo))
def env_pint(p,t,rr,tt,up):
    p=np.asarray(p);t=np.asarray(t);sg=1 if up else -1;u=Pmax if up else Pmin
    gap=sg*(u-p);tr=np.maximum(0,(gap-rr*tt)/rr);t1=np.minimum(t,tr);gaptr=np.minimum(gap,rr*tt);v=np.maximum(0,t-tr)
    return p*t1+.5*sg*rr*t1*t1+u*v-sg*gaptr*tt*(-np.expm1(-v/tt))
def env_p(p,t,rr,tt,up):
    p=np.asarray(p);t=np.asarray(t);sg=1 if up else -1;u=Pmax if up else Pmin
    gap=sg*(u-p);tr=np.maximum(0,(gap-rr*tt)/rr)
    return np.where(t<=tr,p+sg*rr*t,u-sg*np.minimum(gap,rr*tt)*np.exp(-np.maximum(0,t-tr)/tt))
def env_busint(p,t,rr,tt,up):
    p=np.asarray(p);t=np.asarray(t);pf=env_p(p,t,rr,tt,up);integ=env_pint(p,t,rr,tt,up)
    first=np.where(p>=0,eta,1/eta);last=np.where(pf>=0,eta,1/eta)
    tz=np.minimum(t,env_time(p,0,rr,tt,up));iz=env_pint(p,tz,rr,tt,up)
    return np.where(first==last,first*integ,first*iz+last*(integ-iz))
def exact_margins(p,w,wl,rho,rr,tt,T=.15):
    p=np.asarray(p);bp=rho*S+lossmax;bm=-rho*S+lossmin
    tp=np.where(h(p)>bp,np.minimum(T,env_time(p,hinv(bp),rr,tt,False)),0)
    tm=np.where(h(p)<bm,np.minimum(T,env_time(p,hinv(bm),rr,tt,True)),0)
    F=env_busint(p,tp,rr,tt,False)-bp*tp;G=bm*tm-env_busint(p,tm,rr,tt,True)
    return F-(Wmax+WLmax-w-wl),G-(w+wl-Wmin),tp,tm
sens=[];oldcert=json.loads((ROOT/'protocol/DC_BOUND_GATE_A_V2_1_REVALIDATED.json').read_text())['checkpoint']
for rr in [5e6,50e6,500e6]:
    for tt in [.02,.002,.0002]:
        p=phis;g=np.where(np.sin(p)>=0,eta,1/eta);gain=-1j*tt*omega/(g*K-tt*omega**2+1j*omega)
        w=A*(gain.real*np.sin(p)+gain.imag*np.cos(p));dw=A*(gain.real*np.cos(p)-gain.imag*np.sin(p));pb=(A*np.sin(p)+omega*dw)/g;wl=WLmax*(A*np.sin(p)/S)**2
        mo=exact_margins(oldcert['Pb'],oldcert['Wdc'],oldcert['WL'],.4,rr,tt)
        mf=exact_margins(*state(phis),.4,rr,tt);mr=exact_margins(pb,Wref+w,wl,.4,rr,tt)
        sens.append({'R_W_per_s':rr,'tau_s':tt,'old_04_fixed_initial_state_upper_margin_J':float(mo[0]),'old_04_upper_prefix_s':float(mo[2]),'proxy_04_fixed_original_healthy_states_upper_max_J':float(max(mf[0])),'proxy_04_fixed_original_healthy_states_lower_max_J':float(max(mf[1])),'proxy_04_recomputed_harmonic_healthy_states_upper_max_J':float(max(mr[0])),'proxy_04_recomputed_harmonic_healthy_states_lower_max_J':float(max(mr[1])),'proxy_recomputed_either_side_excluded':bool(max(mr[0])>0 or max(mr[1])>0)})
for rr,tt,p,t,up in [(50e6,.02,815639.6755381202,.08,False),(500e6,.02,-815639,.15,True),(5e6,.0002,300000,.15,False)]:
    expected=quad(lambda x:float(h(env_p(p,x,rr,tt,up))),0,t,epsabs=1e-5,points=[float(env_time(p,0,rr,tt,up))] if 0<float(env_time(p,0,rr,tt,up))<t else None)[0]
    checks[f'exact_envelope_{rr}_{tt}_{p}_{up}']=abs(float(env_busint(p,t,rr,tt,up))-expected)
assert max(checks.values())<1e-3


checkpoint_path=ROOT/'gate_a/preconditioned_dq/h1e-05_checkpoint.json';checkpoint=json.loads(checkpoint_path.read_text())
checkpointstate=dict(Pb=checkpoint['plant_state'][3],Wdc=checkpoint['plant_state'][2],WL=.75*L*(checkpoint['plant_state'][0]**2+checkpoint['plant_state'][1]**2))
minimal_gate=[]
for label,st in [('historical_checkpoint_0p6s',checkpointstate),('historical_actual_fault_onset_0p60005s',oldcert)]:
    for name,rr,tt in [('locked_original_synthetic_controlled_DC_port',5e6,.02),('hypothetical_fast_synthetic_controlled_DC_port',50e6,.002)]:
        mp,mm,tp,tm=exact_margins(st['Pb'],st['Wdc'],st['WL'],.4,rr,tt)
        hp=Wmax+WLmax-st['Wdc']-st['WL'];hm=st['Wdc']+st['WL']-Wmin
        minimal_gate.append({'state_source':label,'port':name,'R_W_per_s':rr,'tau_s':tt,'initial_Pb_W':st['Pb'],'initial_Wdc_J':st['Wdc'],'initial_WL_J':st['WL'],'upper_headroom_J':hp,'lower_headroom_J':hm,'upper_max_prefix_gain_J':float(mp+hp),'lower_max_prefix_deficit_J':float(mm+hm),'upper_margin_J':float(mp),'lower_margin_J':float(mm),'upper_optimal_prefix_s':float(tp),'lower_optimal_prefix_s':float(tm)})

out={'status':'THEORY_ONLY_NO_GATE_B_NO_NEW_CONVERTER_INTEGRATION','constants':{'Wref_J':Wref,'Wmin_J':Wmin,'Wmax_J':Wmax,'WLmax_J':WLmax,'lossmin_W':lossmin,'lossmax_W':lossmax},'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'protocol/GATE_A_LOCKED_V2_1.json',ROOT/'gate_a/dq_bench.py',pf,ROOT/'protocol/DC_BOUND_GATE_A_V2_1_REVALIDATED.json',checkpoint_path]},'existing_300kW_negative_control':old,'development_selection_rule':rule,'nominal_algebraic_screen':audit,'selected_candidate_A_W':selected,'selected_candidate_f_Hz':fsel,'frequency_screen':faudit,'harmonic_proxy':proxy,'minimal_source_speed_gate':{'status':'PRIORITY_NEXT_GATE_THEORY_ONLY','warning':'Same historical states, changed reachable source envelope only; no claim these are new fast-port equilibria. Any future fast-port run from 0.6s must record its own actual 0.60005s state before recomputing the certificate.','rho':.4,'T_s':.15,'cases':minimal_gate},'source_response_sensitivity':{'warning':'Synthetic sensitivity only, not literature-calibrated hardware or a directly paralleled battery model. Instant extreme commands relax sample holding.','rho':.4,'cases':sens},'selfchecks_absolute_integral_errors_J':checks}
path=Path(__file__).with_suffix('.json');path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'selected_A_W':selected,'selected_f_Hz':fsel,'frequency_screen':faudit,'existing_cycle':old,'proxy':proxy,'source_response_sensitivity':sens,'minimal_source_speed_gate':minimal_gate},indent=2))
