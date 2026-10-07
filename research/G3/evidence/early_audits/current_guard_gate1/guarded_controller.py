"""Original Q-priority sampler plus only new-queue guard/consistent antiwindup.
No physical state clipping or queue overwrite before its scheduled promotion.
"""
from pathlib import Path
import sys,copy
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'gate_a'))
from dq_bench import controller as original_controller,signals
from common_guard import GuardFailure,v2

def guarded_controller(t,y,ctl,d,request,vs,guard):
    # Driver/sensor adapter produces present electrical alpha-beta observations.
    # The guard never receives vs, event objects, or the plant's true source angle.
    old=copy.deepcopy(ctl);nominal=copy.deepcopy(ctl)
    i,vdc,u,vp,pinv,spcc,psrc=signals(t,y,old,d,vs)
    sensor_rotation=np.exp(1j*d['omega_base_rad_s']*t)
    observation={'i_ab':i*sensor_rotation,'vp_ab':vp*sensor_rotation,'vdc':vdc,'applied_ab':old['applied'],'queued_ab':old['queued']}
    cc=original_controller(t,y,nominal,d,request,vs);mnom=nominal['queued']
    # All original updates remain provisional until a new guard command is admitted.
    k=int(round((t-.6)/d['control_sample_s']))
    msafe,log=guard.command(t,k,observation,mnom)
    # nom zi already contains original us-uu. Replace only the actual new voltage
    # term with msafe; same measuredVdc, sampledPLL frame and originalKaw.
    delta_aw=d['control_sample_s']*d['current_Kaw_per_s']*vdc*(msafe-mnom)*np.exp(-1j*old['theta'])
    nominal['zi']+=delta_aw;nominal['queued']=msafe
    assert nominal['applied']==old['queued']
    ctl.update(nominal)
    log.update(antiwindup_delta_zi=v2(delta_aw).tolist(),original_nominal_voltage_saturation_factor=float(cc[2]),new_modulation_norm=float(abs(msafe)),old_applied_ab=v2(old['applied']).tolist(),old_queued_ab=v2(old['queued']).tolist(),promoted_applied_ab=v2(ctl['applied']).tolist(),sample_theta_PLL_rad=float(old['theta']),nominal_integrator_after=v2(nominal['zi']-delta_aw).tolist(),guarded_integrator_after=v2(nominal['zi']).tolist())
    cc[7]=float(abs(msafe))
    return cc,log
