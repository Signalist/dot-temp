"""Exact frozen controller with standard allocation block replacement only."""
import numpy as np
from dq_bench import signals,cnormclip,inv_loss

def controller(t,y,ctl,d,c,vs,policy):
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
    if policy=='p_priority':
        a=np.clip(a,-Imax,Imax)
        b=np.clip(b,-np.sqrt(max(0,Imax**2-a**2)),np.sqrt(max(0,Imax**2-a**2)))
    elif policy=='radial':
        scale=min(1.,Imax/max(np.hypot(a,b),1e-30));a=a*scale;b=b*scale
    elif policy=='q_priority':
        b=np.clip(b,-Imax,Imax);a=np.clip(a,-np.sqrt(max(0,Imax**2-b**2)),np.sqrt(max(0,Imax**2-b**2)))
    else:raise ValueError(policy)
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
