"""Independent rotating-nominal-dq averaged GFL benchmark. SI, no state projection.
GATE_A_LOCKED_V1 has the authoritative resource/control contract.
"""
from pathlib import Path
import json, math, hashlib
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import root
ROOT=Path(__file__).resolve().parents[1]
PARAM=ROOT/'protocol/GATE_A_LOCKED_V1_1.json'

def load(): return json.loads(PARAM.read_text())
def cnormclip(x,lim): return x*min(1.,lim/max(abs(x),1e-30))
def source_bus(p,d): return d['eta_dc_dc']*p if p>=0 else p/d['eta_dc_dc']
def battery_draw(p,d): return p/d['eta_discharge_energy'] if p>=0 else d['eta_charge_energy']*p
def inv_loss(i,d): return d['inverter_loss_constant_W']+d['inverter_loss_current_squared_W_at_1pu']*(abs(i)/d['I_phase_peak_base_A'])**2

def initial(d,c):
    w=d['omega_base_rad_s']; eg=d['V_phase_peak_base_V']; rg=d['grid_R_ohm']; lg=d['grid_L_H']; rf=d['filter_R_ohm']; lf=d['filter_L_H']
    target=complex(c['P_req_W'],c['Q_req_var'])
    def residual(x):
        i=complex(*x); v=eg+complex(rg,w*lg)*i; err=1.5*v*np.conj(i)-target
        return [err.real,err.imag]
    sol=root(residual,[c['P_req_W']/(1.5*eg),-c['Q_req_var']/(1.5*eg)],tol=1e-12)
    assert sol.success or np.linalg.norm(residual(sol.x))<1e-6
    i=complex(*sol.x); v=eg+complex(rg,w*lg)*i; u=eg+complex(rg+rf,w*(lg+lf))*i
    pinv=1.5*np.real(u*np.conj(i)); need=pinv+inv_loss(i,d); pb=need/d['eta_dc_dc'] if need>=0 else need*d['eta_dc_dc']
    W0=.5*d['C_dc_F']*d['V_dc_initial_V']**2
    # i_d, i_q, Wdc, Pb, delta E_b, integral P_source, integral losses
    y=np.array([i.real,i.imag,W0,pb,0.,0.,0.])
    ctl=dict(theta=float(np.angle(v)),zpll=0.,omega=w,zi=rf*i*np.exp(-1j*np.angle(v)),applied=u/d['V_dc_initial_V'],queued=u/d['V_dc_initial_V'],pb_command=pb)
    assert abs(ctl['applied']) <= d['svpwm_linear_voltage_derating']/np.sqrt(3)
    return y,ctl,dict(i0=[i.real,i.imag],v_pcc0=[v.real,v.imag],u_inv0=[u.real,u.imag],p_b0=pb,Wdc0=W0,WL0=.75*(lf+lg)*abs(i)**2,initial_power_residual_W=np.linalg.norm(residual(sol.x)))

def signals(t,y,ctl,d,vs):
    i=complex(y[0],y[1]); W=y[2]
    if W<=0: raise ValueError('nonpositive physical DC energy')
    vdc=np.sqrt(2*W/d['C_dc_F']); u=ctl['applied']*vdc*np.exp(-1j*d['omega_base_rad_s']*t)
    e=d['V_phase_peak_base_V']*vs
    lf=d['filter_L_H'];lg=d['grid_L_H'];rf=d['filter_R_ohm'];rg=d['grid_R_ohm']
    vp=(lg*(u-rf*i)+lf*(e+rg*i))/(lf+lg)
    pinv=1.5*np.real(u*np.conj(i)); spcc=1.5*vp*np.conj(i); psrc=1.5*np.real(e*np.conj(i))
    return i,vdc,u,vp,pinv,spcc,psrc

def controller(t,y,ctl,d,c,vs):
    i,vdc,u,vp,pinv,spcc,psrc=signals(t,y,ctl,d,vs)
    # Sample old hold before queue promotion. The PLL frame is separate from plant dq.
    rot=np.exp(1j*(d['omega_base_rad_s']*t-ctl['theta'])); ic=i*rot; vc=vp*rot; V=abs(vc)
    e=vc.imag/max(V,d['pll_normalization_floor_pu']*d['V_phase_peak_base_V'])
    wu=d['omega_base_rad_s']+d['pll_Kp_per_s']*e+ctl['zpll']
    wn=float(np.clip(wu,2*np.pi*d['pll_frequency_min_Hz'],2*np.pi*d['pll_frequency_max_Hz']))
    Ts=d['control_sample_s']
    if V>=d['pll_normalization_floor_pu']*d['V_phase_peak_base_V']:
        znew=ctl['zpll']+Ts*(d['pll_Ki_per_s2']*e+d['pll_Kaw_per_s']*(wn-wu))
    else: znew=ctl['zpll'];wn=ctl['omega']
    pref=np.clip(c['P_req_W'],-d['converter_active_service_limit_W'],d['converter_active_service_limit_W']);qref=c['Q_req_var']
    Imax=d['current_reference_limit_pu']*d['I_phase_peak_base_A'];vnorm=max(V,d['pll_normalization_floor_pu']*d['V_phase_peak_base_V'])
    a=pref/(1.5*vnorm);b=qref/(1.5*vnorm)
    b=np.clip(b,-Imax,Imax);a=np.clip(a,-np.sqrt(max(0,Imax**2-b**2)),np.sqrt(max(0,Imax**2-b**2)))
    ir=(a-1j*b)*vc/max(V,1e-30)
    err=ir-ic
    uu=vc+1j*wn*d['filter_L_H']*ic+d['current_Kp_ohm']*err+ctl['zi']
    us=cnormclip(uu,d['svpwm_linear_voltage_derating']*vdc/np.sqrt(3))
    zinew=ctl['zi']+Ts*(d['current_Ki_ohm_per_s']*err+d['current_Kaw_per_s']*(us-uu))
    mnew=us*np.exp(1j*ctl['theta'])/vdc
    need=pinv+inv_loss(i,d);pff=need/d['eta_dc_dc'] if need>=0 else need*d['eta_dc_dc']
    pbnew=np.clip(pff+d['dc_energy_feedback_gain_per_s']*(.5*d['C_dc_F']*d['V_dc_initial_V']**2-y[2]),d['battery_terminal_power_min_W'],d['battery_terminal_power_max_W'])
    ctl.update(zpll=znew,omega=wn,zi=zinew,applied=ctl['queued'],queued=mnew,pb_command=float(pbnew))
    return [t,abs(ir)/d['I_phase_peak_base_A'],abs(us)/max(abs(uu),1e-30),wn/(2*np.pi),float(pbnew),a,b,abs(mnew)]

def rhs(t,y,ctl,d,vs):
    i,vdc,u,vp,pinv,spcc,psrc=signals(t,y,ctl,d,vs)
    Lt=d['filter_L_H']+d['grid_L_H'];Rt=d['filter_R_ohm']+d['grid_R_ohm'];e=d['V_phase_peak_base_V']*vs
    di=(u-e-Rt*i)/Lt-1j*d['omega_base_rad_s']*i
    pb=y[3];pbus=source_bus(pb,d);loss_inv=inv_loss(i,d);draw=battery_draw(pb,d)
    dpb=np.clip((ctl['pb_command']-pb)/d['battery_source_tau_s'],-d['battery_source_ramp_down_W_per_s'],d['battery_source_ramp_up_W_per_s'])
    total_losses=(draw-pb)+(pb-pbus)+loss_inv+1.5*Rt*abs(i)**2
    return [di.real,di.imag,pbus-pinv-loss_inv,dpb,-draw,psrc,total_losses]

def run(case_id,max_step=1e-5,outdir=None):
    d=load();c=next(x for x in d['case_registry'] if x['id']==case_id);y,ctl,init=initial(d,c);y0=y.copy();Ts=d['control_sample_s'];ev=c['event'];duration=c['duration_s']
    def vs_at(t): return ev['retained_voltage_pu'] if ev and ev['start_s']<=t<ev['end_s'] else c['source_voltage_pu']
    def emergency_i(t,y):return d['current_emergency_stop_pu']**2*d['I_phase_peak_base_A']**2-y[0]**2-y[1]**2
    def lowdc(t,y):return y[2]-.5*d['C_dc_F']*(d['V_dc_min_pu']*d['V_dc_initial_V'])**2
    def highdc(t,y):return .5*d['C_dc_F']*(d['V_dc_max_pu']*d['V_dc_initial_V'])**2-y[2]
    def current_limit(t,y):return d['I_phase_peak_base_A']**2-y[0]**2-y[1]**2
    for f in [emergency_i,lowdc,highdc]:f.terminal=True;f.direction=-1
    current_limit.terminal=False;current_limit.direction=-1
    rows=[];controls=[];crossings=[];reason='completed';t=0.;stop=False
    def record(tt,yy,vv):
        i,vdc,u,vp,pinv,spcc,psrc=signals(tt,yy,ctl,d,vv)
        WL=.75*(d['filter_L_H']+d['grid_L_H'])*abs(i)**2
        energy_res=(yy[4]+yy[2]-y0[2]+WL-init['WL0']+yy[5]+yy[6])
        rows.append([tt,*yy,abs(i)/d['I_phase_peak_base_A'],vdc/d['V_dc_initial_V'],spcc.real,spcc.imag,abs(vp)/d['V_phase_peak_base_V'],pinv,psrc,WL,energy_res,u.real,u.imag,vp.real,vp.imag,vv])
    record(0,y,vs_at(0))
    for k in range(int(round(duration/Ts))):
        t=k*Ts;tend=(k+1)*Ts
        controls.append(controller(t,y,ctl,d,c,vs_at(t)))
        cuts=[t,tend]
        if ev:
            cuts += [z for z in [ev['start_s'],ev['end_s']] if t+1e-14<z<tend-1e-14]
        cuts=sorted(cuts)
        for a,b in zip(cuts[:-1],cuts[1:]):
            vv=vs_at((a+b)/2)
            sol=solve_ivp(lambda tt,yy:rhs(tt,yy,ctl,d,vv),(a,b),y,method='DOP853',rtol=1e-10,atol=1e-8,max_step=max_step,events=[emergency_i,lowdc,highdc,current_limit])
            for tt,yy in zip(sol.t[1:],sol.y.T[1:]):record(tt,yy,vv)
            crossings.extend(sol.t_events[3].tolist());y=sol.y[:,-1]
            if sol.status==1:
                reason=['actual_current_emergency','dc_low','dc_high'][next(i for i in range(3) if len(sol.t_events[i]))];stop=True;break
            if not sol.success: reason='solver_failure';stop=True;break
        ctl['theta']+=ctl['omega']*(sol.t[-1]-t)
        if stop: break
    a=np.array(rows);ct=np.array(controls);I=a[:,8];Vdc=a[:,9];S=np.hypot(a[:,10],a[:,11]);Ebase=d['battery_energy_MWh']*3.6e9;soc=d['soc_initial']+a[:,5]/Ebase
    summary=dict(case=case_id,representation='nominal-rotating-dq',parameter_sha256=hashlib.sha256(PARAM.read_bytes()).hexdigest(),max_step_s=max_step,stop_reason=reason,final_time_s=float(a[-1,0]),initial=init,
        max_actual_current_pu=float(max(I)),max_reference_current_pu=float(max(ct[:,1])),first_current_limit_crossing_s=crossings[0] if crossings else None,
        min_dc_pu=float(min(Vdc)),max_dc_pu=float(max(Vdc)),max_abs_battery_terminal_power_W=float(max(abs(a[:,4]))),min_soc=float(min(soc)),max_soc=float(max(soc)),
        max_pcc_apparent_VA=float(max(S)),max_abs_energy_conservation_residual_J=float(max(abs(a[:,16]))),max_modulation_norm=float(max(ct[:,7])),
        mean_last_20ms_pcc_P_W=float(np.mean(a[a[:,0]>a[-1,0]-.02,10])),mean_last_20ms_pcc_Q_var=float(np.mean(a[a[:,0]>a[-1,0]-.02,11])),
        gate_hard_safe=bool(reason=='completed' and max(I)<=1.+1e-8 and min(Vdc)>=d['V_dc_min_pu'] and max(Vdc)<=d['V_dc_max_pu'] and max(S)<=d['S_base_VA']*(1+1e-8)),samples=len(a))
    if outdir:
        out=Path(outdir);out.mkdir(parents=True,exist_ok=True);tag=f'{case_id}_{max_step:g}'
        np.savez_compressed(out/f'{tag}.npz',trace=a,control=ct,trace_columns=np.array(['t','id','iq','Wdc','Pb','deltaEb','intPsource','intLoss','Ipu','Vdcpu','Ppcc','Qpcc','Vpccpu','Pinv','Psource','WL','energy_residual','ud','uq','vd','vq','Vs']),control_columns=np.array(['t','Irefpu','voltage_sat_factor','PLL_Hz','Pb_cmd','ip_ref','iq_req_positiveQ','mnorm']))
        (out/f'{tag}.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--case',default='all');ap.add_argument('--max-step',type=float,default=1e-5);args=ap.parse_args()
    cases=[c['id'] for c in load()['case_registry']] if args.case=='all' else [args.case]
    for c in cases: print(json.dumps(run(c,args.max_step,ROOT/'gate_a/dq_results'),indent=2),flush=True)
