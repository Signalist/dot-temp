"""Prospective protocol writer; no transfer computations or result inspection."""
from pathlib import Path
import hashlib,json,datetime
D=Path(__file__).resolve().parent
S=D.parents[2]/'round2_20261003'/'grid_transfer'
files=['kundur_reduced51.npz','kundur_descriptor_K.npz','kundur_descriptor_aux.npz','wecc_verified_descriptor_K.npz','wecc_descriptor_aux.npz','grid_adapter.py','README_qualification.md','DO_NOT_USE_WECC_EIG_AS.txt','chainrule_audit.json','verified_descriptor_ports.json','PROVENANCE_LOCK.json']
p={
 'study':'G4 source-bus measurement distinguishability, synthetic qualified grid transfer',
 'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'before_results':True,
 'frequencies_Hz':[0.05,0.1,0.2,0.5,1.,2.],
 'models':{
  'kundur':{'input_source_buses':[7,8],'frequency_generator_ids':[1,4],'voltage_buses':[7,8],'interface':'qualified stable reduced51, no other truncation'},
  'wecc':{'input_source_buses':[1,4],'frequency_generator_ids':[1,29],'voltage_buses':[1,4],'interface':'verified complete descriptor resolvent; no EIG.As or QZ finite ODE'}},
 'sensor_sets':['V_first','F_first','V_pair','F_pair','V_first_F_first'],
 'primary_source_class':'Exactly one of two configured P-only incremental load ports, independent unknown nonzero amplitude and phase at every analyzed frequency; Q=0 known.',
 'source_units':'MW; positive is incremental consumption relative to common background. A frequency point is not a claim of synchronized physical data.',
 'initial_information':{'grid':'Same fixed network, parameters, equilibrium, and known zero incremental dynamic state for causal experiments.', 'steady_state_scope':'Resolvents are asymptotic harmonic signatures only, not proof of full causal time-record equivalence.', 'causal_kundur':'Zero-state sinus/cos inputs start at t=0; causal lock-in over [0,20/f] yields a two-real-column operator per source. One reported feature vector is available only at the end of that interval; raw traces are not the observer interface.'},
 'noise':{'model':'Bounded joint complex Euclidean ellipsoid: sqrt(sum_k |e_k/scale_k|^2)<=1 per observation.', 'voltage_scale_pu':0.0001,'frequency_scale_Hz':0.001,'direct_PCC_scale_MW':0.1,'origin':'Illustrative declared research errors, not sensor specifications or empirical calibration.', 'guaranteed_separation':'Distance between noiseless candidate output sets >2 normalized error units; threshold is source amplitude, not a guarantee if arbitrary amplitudes can vanish.'},
 'metrics':['complex normalized column correlation','sin principal angle','unit-column condition number','source-directed orthogonal residual per MW','critical MW for disjoint unit-error balls','finite causal real-subspace principal angles and worst-phase source-directed residual','descriptor solve backward residual and iterative correction sensitivity'],
 'numerics':{'descriptor_backward_residual_warning':1e-9,'descriptor_output_refinement_warning_relative':1e-7,'zero_norm_tolerance':1e-15},
 'controls':{'direct_resolved_PCC_pair':'Two source-resolved P measurements have identity map; same grid initial information. No superiority claim under arbitrarily unequal measurement noise.', 'direct_aggregate_PCC':'One sum-P measurement has two identical columns, hence unknown-source ambiguity.', 'PQ_nuisance':'Secondary model allows independent complex P/Q at active candidate bus. Two measured complex channels generally span C^2 for each bus and cannot localize without extra assumptions. Report ranks.', 'exact_boundary_equivalence':'Equal complete nodal P/Q histories, grid initial state, topology, and boundary controller states imply equal deterministic grid trajectories under uniqueness; no duplicate replay needed.', 'causal_single_sensor':'Kundur SISO transfer commutation yields exact same-zero-state full-trace ambiguity for unrestricted waveform sources: u7=g8*v, u8=g7*v. Provide numerical cascade audit and theorem, separate from sinusoid source class.'},
 'causal_cascade_audit':{'sensor':'V at bus7','drive':'v(t)=sin(2*pi*0.2*t) for 0<=t<=20, then0','duration_s':40,'sample_dt_s':0.01,'amplitude_normalization':'Scale common drive so maximum source increment among both worlds is1MW; no optimization.'},
 'cyclic_buffer_witness':{'concept':'Same-PCC continuing load with equal initial energy and energy-neutral zero-mean internal load/buffer differences; explicitly lossless idealization or separately accounted losses; no hardware validation.'},
 'excluded_claims':['No AI-workload label inference','No real synchronized dataset','No unknown-topology/parameter/initial-state robustness','No arbitrary nonlinear finite-amplitude localization certificate','No operational protection or sensor compliance claim'],
 'source_root_relative':str(S.relative_to(D.parents[3])),
 'input_sha256':{f:hashlib.sha256((S/f).read_bytes()).hexdigest() for f in files}
}
path=D/'PROTOCOL_FREEZE.json'
if path.exists(): raise RuntimeError('Protocol already exists; do not overwrite')
path.write_text(json.dumps(p,indent=2)+'\n')
(D/'PROTOCOL_FREEZE.sha256').write_text(hashlib.sha256(path.read_bytes()).hexdigest()+'  PROTOCOL_FREEZE.json\n')
print(path);print((D/'PROTOCOL_FREEZE.sha256').read_text())
