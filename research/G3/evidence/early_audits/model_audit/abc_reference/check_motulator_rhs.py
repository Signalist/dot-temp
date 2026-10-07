"""Static, independent public-component RHS consistency checks; no dynamic cases."""
import hashlib,importlib.metadata,inspect,json,math
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from motulator.grid import model
from reference_abc import abc_from_complex,complex_from_abc
p=json.loads((Path(__file__).parents[2]/'protocol'/'GATE_A_LOCKED_V1.json').read_text())
rf,lf,rg,lg=[p[x] for x in ['filter_R_ohm','filter_L_H','grid_R_ohm','grid_L_H']]
lflt=model.LFilter(L_f=lf,R_f=rf,L_g=lg,R_g=rg)
C=p['C_dc_F'];Vdc=p['V_dc_initial_V'];dc=model.CapacitiveDCBusConverter(u_dc=Vdc,C_dc=C)
rows=[]
for phase in [0.0,.7]:
 for loading in [.3,-.4]:
  for sag in [1.0,.4]:
   rot=np.exp(1j*phase)
   i=p['I_phase_peak_base_A']*(loading-.2j)*rot
   u=p['V_phase_peak_base_V']*(1.0+.1j)*rot
   eg=p['V_phase_peak_base_V']*sag*rot
   ia,ua,ea=[abc_from_complex(x) for x in [i,u,eg]]
   didt_abc=(ua-ea-(rf+rg)*ia)/(lf+lg)
   vabc=(lg*(ua-rf*ia)+lf*(ea+rg*ia))/(lf+lg)
   lflt.state.i_c_ab=i;lflt.inp.u_c_ab=u;lflt.inp.e_g_ab=eg
   public_rhs=lflt.rhs(0.0)[0];public_v=lflt.pcc_voltage(lflt.state,lflt.inp)
   Pbus=450000.0 if loading>0 else -350000.0;Ploss=5000.0
   dc.inp.i_dc=(Pbus-Ploss)/Vdc;dc.inp.q_c_ab=u/Vdc;dc.inp.i_c_ab=i
   public_dW=C*Vdc*dc.rhs(0.0)[0]
   our_dW=Pbus-Ploss-float(ua@ia)
   rows.append({'phase_rad':phase,'loading':loading,'retained_source':sag,
     'current_rhs_error_A_per_s':abs(public_rhs-complex_from_abc(didt_abc)),
     'pcc_voltage_error_V':abs(public_v-complex_from_abc(vabc)),
     'dc_energy_rhs_error_W':abs(public_dW-our_dW)})
files={}
for cls in [model.LFilter,model.CapacitiveDCBusConverter]:
 f=Path(inspect.getfile(cls));files[str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
r={'motulator_installed_version':importlib.metadata.version('motulator'),'component_source_sha256':files,
 'method':'8 deterministic algebraic points, not new trajectory experiments; official LFilter RHS/PCC and ideal capacitive converter RHS evaluated directly against independent abc circuit algebra. Loss is placed as external bus current for DC check; battery actuator/control not externally validated.',
 'rows':rows,'max_current_rhs_error_A_per_s':max(x['current_rhs_error_A_per_s'] for x in rows),
 'max_pcc_voltage_error_V':max(x['pcc_voltage_error_V'] for x in rows),
 'max_dc_energy_rhs_error_W':max(x['dc_energy_rhs_error_W'] for x in rows)}
r['pass']=bool(r['max_current_rhs_error_A_per_s']<1e-8 and r['max_pcc_voltage_error_V']<1e-10 and r['max_dc_energy_rhs_error_W']<1e-8)
out=Path(__file__).with_name('MOTULATOR_RHS_CHECK.json');out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
