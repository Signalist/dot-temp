"""Nonintegrating sign/coordinate/energy checks independent of parent dq code."""
from pathlib import Path
import hashlib,json,math,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'model_audit/abc_reference'))
from reference_abc import abc_from_complex,complex_from_abc

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pfile=ROOT/'protocol/GATE_A_LOCKED_V2_1.json';p=json.loads(pfile.read_text())
R=p['filter_R_ohm']+p['grid_R_ohm'];L=p['filter_L_H']+p['grid_L_H'];w=p['omega_base_rad_s'];Ip=p['I_phase_peak_base_A'];Vp=p['V_phase_peak_base_V'];eta=p['eta_dc_dc']
rows=[]
for phase in [0.0,0.7]:
 for idpu in [-0.3,0.3]:
  for iqpu in [-0.2,0.2]:
   for Pb in [-300000.0,0.0,300000.0]:
    t=0.1234;theta=w*t+phase;wh=w+0.3
    i=complex(idpu,iqpu)*Ip;edq=0.85*Vp*np.exp(-1j*phase)
    # Chosen applied voltage is a finite actuator output; points need not be equilibria.
    udq=(edq+(R+1j*w*L)*i)*0.98
    iabc=abc_from_complex(i*np.exp(1j*theta));eabc=abc_from_complex(edq*np.exp(1j*theta));uabc=abc_from_complex(udq*np.exp(1j*theta))
    diabc=(uabc-eabc-R*iabc)/L
    didq_from_abc=complex_from_abc(diabc)*np.exp(-1j*theta)-1j*wh*i
    didq=(udq-edq-R*i)/L-1j*wh*i
    Pidq=1.5*(udq*i.conjugate()).real;Piabc=float(uabc@iabc);Psdq=1.5*(edq*i.conjugate()).real;Psabc=float(eabc@iabc)
    Prdq=1.5*R*abs(i)**2;Prabc=R*float(iabc@iabc)
    Pl=p['inverter_loss_constant_W']+p['inverter_loss_current_squared_W_at_1pu']*(abs(i)/Ip)**2
    Pbus=eta*Pb if Pb>=0 else Pb/eta
    Pdep=Pb/p['eta_discharge_energy'] if Pb>=0 else p['eta_charge_energy']*Pb
    dWabc=Pbus-Piabc-Pl-p['auxiliary_power_W'];dWdq=Pbus-Pidq-Pl-p['auxiliary_power_W']
    dWLabc=L*float(iabc@diabc);dWLdq=1.5*L*(i.conjugate()*didq).real
    loss_dc=Pb-Pbus;loss_batt=Pdep-Pb
    total_residual=(-Pdep+dWabc+dWLabc)-(-Psabc-Prabc-Pl-p['auxiliary_power_W']-loss_dc-loss_batt)
    row={'phase_rad':phase,'id_pu':idpu,'iq_pu':iqpu,'Pbat_W':Pb,'Q_source_var':float(1.5*(edq*i.conjugate()).imag),'Pbus_W':Pbus,'Pdeplete_W':Pdep,'battery_energy_derivative_W':-Pdep,'dc_conversion_loss_W':loss_dc,'battery_conversion_loss_W':loss_batt,'dq_current_derivative_error_A_per_s':abs(didq_from_abc-didq),'converter_power_error_W':abs(Pidq-Piabc),'source_power_error_W':abs(Psdq-Psabc),'copper_error_W':abs(Prdq-Prabc),'DC_energy_derivative_error_W':abs(dWabc-dWdq),'inductor_energy_derivative_error_W':abs(dWLabc-dWLdq),'whole_storage_conservation_residual_W':abs(total_residual),'zero_sequence_current_A':abs(float(iabc.sum()))}
    row['pass']=bool(max(row[k] for k in row if k.endswith('_error_W') or k.endswith('_error_A_per_s') or k=='whole_storage_conservation_residual_W')<1e-6 and loss_dc>=0 and loss_batt>=0 and np.sign(-Pdep)==-np.sign(Pb))
    rows.append(row)
eps=1e-6
h=lambda P:eta*P if P>=0 else P/eta
g=lambda P:P/p['eta_discharge_energy'] if P>=0 else p['eta_charge_energy']*P
zero={'epsilon_W':eps,'dc_left_W':h(-eps),'dc_zero_W':h(0.),'dc_right_W':h(eps),'depletion_left_W':g(-eps),'depletion_zero_W':g(0.),'depletion_right_W':g(eps),'interpretation':'Continuous at zero, with distinct physically lossy one-sided slopes; nondifferentiability is intentional.'}
out={'status':'pass' if all(x['pass'] for x in rows) else 'fail','integration_performed':False,'cases':len(rows),'results':rows,'zero_branch_check':zero,'maxima':{k:max(x[k] for x in rows) for k in rows[0] if k.endswith('_error_W') or k.endswith('_error_A_per_s') or k=='whole_storage_conservation_residual_W'},'provenance':{'protocol_sha256':sha(pfile),'script_sha256':sha(__file__),'abc_transform_source_sha256':sha(ROOT/'model_audit/abc_reference/reference_abc.py')},'coverage':'Algebraic coordinate and signed DC/battery energy identities only; no full signed trajectory, BMS or hardware validation.'}
path=Path(__file__).with_name('signed_rhs_check.json');path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2))
assert out['status']=='pass'
