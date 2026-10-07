"""Independent numerical checks + algebraic continuing-load cyclic witness."""
from pathlib import Path
import json,hashlib,platform
import numpy as np, scipy
from scipy.linalg import solve,expm
from scipy.integrate import simpson
D=Path(__file__).resolve().parent;S=D.parents[2]/'round2_20261003'/'grid_transfer'
r=json.loads((D/'results.json').read_text());z=np.load(S/'kundur_reduced51.npz');h=np.load(D/'harmonic_transfer_arrays.npz');cl=np.load(D/'causal_lockin_arrays.npz')
A=z['A'];B=z['B'];C=np.vstack([z['C_voltage_pu'][[6,7]],z['C_frequency_Hz'][[0,3]]]);DD=np.vstack([z['D_voltage_pu'][[6,7]],np.zeros((2,4))]);scales=h['sensor_scales']
# Independent sampled analytic trajectory and Simpson quadrature at one frozen f.
f=.2;w=2*np.pi*f;T=20/f;dt=.01;t=np.arange(0,T+dt/2,dt);Z=solve(1j*w*np.eye(len(A))-A,B);H=C@Z+DD
step=expm(A*dt);trans=Z.copy();out=np.empty((len(t),4,4),complex)
for j,tt in enumerate(t):
 out[j]=H*np.exp(1j*w*tt)-C@trans
 trans=step@trans
mcos=2/T*simpson(out.real*np.exp(-1j*w*t[:,None,None]),x=t,axis=0)
msin=2/T*simpson(out.imag*np.exp(-1j*w*t[:,None,None]),x=t,axis=0)
si=[0,1];F=[]
for port in [0,2]:
 q=[mcos[si,port]/scales[si],msin[si,port]/scales[si]]
 F.append(np.column_stack([np.r_[v.real,v.imag] for v in q]))
num=np.stack(F);analytic=cl['causal_0.2_V_pair'];error=float(np.linalg.norm(num-analytic)/np.linalg.norm(analytic))
assert error<1e-8,error
single=[x for x in r['harmonic'] if x['channel_count']==1];pair=[x for x in r['harmonic'] if x['channel_count']==2]
assert len(single)==24 and all(x['residual_is_numerically_zero'] for x in single)
assert len(pair)==36 and all(x['sin_principal_angle']>1e-5 for x in pair)
assert all(x['both_fill_observation_space'] for x in r['PQ_nuisance'])
assert max(x['relative_output_equilibration_difference'] for x in r['descriptor_numerical_audits'])<1e-10
assert max(x.get('reduced_descriptor_output_relative_difference',0) for x in r['descriptor_numerical_audits'])<1e-10
assert r['causal_single_sensor_alias']['max_voltage_alias_difference_pu']<1e-14
# Lossless finite-PCS same-PCC witness. Two possible internal phases; all initial
# grid, energy and realized PCS states agree. Commands are causal clock signals.
a=1.;period=10.;w=2*np.pi/period;base=10.;tau=.05;E0=.01;Ecap=.02
Tw=np.arange(0,3*period+.0005,.001);u=a*np.sin(w*Tw);b=np.stack([u,-u],axis=1);load=base+b;pcc=load-b
E=np.column_stack([E0+a/w*(np.cos(w*Tw)-1)/3600,E0-a/w*(np.cos(w*Tw)-1)/3600])
bdot=np.column_stack([a*w*np.cos(w*Tw),-a*w*np.cos(w*Tw)]);cmd=b+tau*bdot
witness={'classification':'Exact boundary-equivalence construction; explicitly synthetic and lossless. No grid replay or hardware validation.', 'period_s':period,'continuing_load_baseline_MW':base,'internal_peak_to_peak_MW':2*a,'efficiencies_charge_discharge':[1.,1.],'buffer_realized_power_limit_MW':1.,'buffer_command_limit_MW':1.1,'buffer_slew_limit_MW_per_s':1.,'PCS_tau_s':tau,'E0_MWh':E0,'capacity_MWh':Ecap,'max_PCC_world_difference_MW':float(np.max(abs(pcc[:,0]-pcc[:,1]))),'max_PCC_deviation_from_constant_MW':float(np.max(abs(pcc-base))),'min_load_MW':float(np.min(load)),'SOC_minmax_MWh':[float(E.min()),float(E.max())],'cycle_boundary_energy_errors_MWh':[float(max(abs(E[i]-E0))) for i in [0,10000,20000,30000]],'max_command_MW':float(np.max(abs(cmd))),'max_slew_MW_per_s':float(np.max(abs(bdot))),'same_initial_realized_buffer_MW':b[0].tolist(),'same_initial_energy_MWh':E[0].tolist(),'meaning':'Distinct internal phase histories remain invisible even to exact direct PCC sensing when P/Q at every nodal boundary coincide. To turn this into hidden location at paired buses, assign one oscillation/buffer pair to bus1 of the configured pair in world1 and bus2 in world2, keeping identical positive baseline aggregates at both buses. This is a conceptual internal decomposition, not a newly calibrated benchmark load model. First-order PCS feasibility is analytic: command=b+tau*db/dt. Losses would require extra recharge; this witness does not apply unchanged with efficiency below1.'}
assert np.max(abs(pcc-base))<1e-12 and E.min()>0 and E.max()<Ecap
assert np.max(abs(cmd))<1.1 and np.max(abs(bdot))<1.
np.savez_compressed(D/'cyclic_continuing_load_same_PCC.npz',t_s=Tw,load_MW=load,buffer_injection_MW=b,pcc_MW=pcc,buffer_energy_MWh=E,command_MW=cmd)
(D/'cyclic_continuing_load_witness.json').write_text(json.dumps(witness,indent=2)+'\n')
v={'passed':True,'checks':{'harmonic_single_channel_exact_aliases':len(single),'harmonic_two_channel_noncollinear_P_only':len(pair),'PQ_nuisance_full_observation_spaces':len(r['PQ_nuisance']),'causal_lockin_independent_quadrature_relative_error':error,'causal_cascade_machine_precision_identity':True,'same_PCC_cyclic_continuing_load_identity':True,'source_files_unchanged':json.loads((D/'input_integrity_after.json').read_text())['all_input_hashes_unchanged']},'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'limitations':'Algebraic identities are mathematical; tolerance checks are floating-point audit evidence, not interval-arithmetic certificates.'}
(D/'validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2));print(json.dumps(witness,indent=2))
