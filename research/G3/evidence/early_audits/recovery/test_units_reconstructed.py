"""New post-reconstruction tests, not recreation of old test logs."""
from pathlib import Path
import json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];p=R/'protocol/GATE_A_LOCKED_V2_1.json';d=json.loads(p.read_text())
rng=np.random.default_rng(2026100203);errs=[]
for n in range(128):
 theta=rng.uniform(-np.pi,np.pi);v=(rng.normal()+1j*rng.normal())*d['V_phase_peak_base_V'];i=(rng.normal()+1j*rng.normal())*.5*d['I_phase_peak_base_A'];angles=theta-2*np.pi*np.arange(3)/3
 va=v.real*np.cos(angles)-v.imag*np.sin(angles);ia=i.real*np.cos(angles)-i.imag*np.sin(angles)
 vr=(2/3)*np.sum(va*np.exp(-1j*angles));ir=(2/3)*np.sum(ia*np.exp(-1j*angles))
 pabc=va@ia;qabc=((va[1]-va[2])*ia[0]+(va[2]-va[0])*ia[1]+(va[0]-va[1])*ia[2])/np.sqrt(3)
 sdq=1.5*v*np.conj(i);L=d['filter_L_H']+d['grid_L_H'];Wabc=.5*L*(ia@ia);Wdq=.75*L*abs(i)**2
 errs.append([abs(vr-v),abs(ir-i),abs(pabc-sdq.real),abs(qabc-sdq.imag),abs(Wabc-Wdq)])
m=np.max(errs,axis=0);base=1.5*d['V_phase_peak_base_V']*d['I_phase_peak_base_A'];power_base_error=abs(base-d['S_base_VA'])
result={'status':'reconstructed_then_rerun','test_origin':'New coordinate/base algebra tests after exact parameter reconstruction; not copied historical output','seed':2026100203,'points':128,'parameter_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'maximum_errors':dict(zip(['V_roundtrip_V','I_roundtrip_A','P_abc_vs_dq_W','Q_abc_vs_dq_var','inductor_energy_J'],m.tolist())),'three_phase_power_base_error_VA':power_base_error,'positive_Q_requires_negative_iq_when_vq_zero':bool((1.5*(1+0j)*np.conj(0-1j)).imag>0),'passed':bool(m[0]<1e-9 and m[1]<1e-9 and m[2]<1e-7 and m[3]<1e-7 and m[4]<1e-8 and power_base_error<1e-8)}
(R/'recovery/UNITS_REVALIDATED.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['passed']
