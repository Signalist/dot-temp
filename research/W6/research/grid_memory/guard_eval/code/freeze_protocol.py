from pathlib import Path
import json,hashlib,datetime,itertools,platform,numpy,scipy
ROOT=Path(__file__).resolve().parents[1]
p={
 'title':'W6 isolated-cycle amplitude grid guard, uniform continuous EOS',
 'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'reset_disclosure':{'earlier_lost_protocol_sha256':'a687f28707a22891fafddf86abdb2ca4348973626449dca9544caff4cfeedef5','status':'earlier protocol vanished in filesystem reset; no original or confirmatory numerical results ran before reset; this is a newly frozen protocol, not claimed byte-identical'},
 'contract':{'work_law':'W uniform on [0,M], fixed unknown draw per isolated task','M':2.,'c':1.,'initial_power':0.,'initial_grid_state':[0.,0.],'service':'p**beta','actual_power_slew':'abs(p_dot)<=R','EOS':'instantaneous','postEOS':'fastest physical return; actual burn energy charged','objective':'E_dynamic+c*T_powercycle','grid_observation':'all future time including analytic zero-input tail; no cost after actual-power cycle return','excluded':['hardware validation','compliance threshold','empirical facility allowance','grid-reset/regenerative interpretation']},
 'grid':{'H_s':4.,'S_MW':1000.,'f0_Hz':60.,'gain_MW_per_p':20.,'budget_Hz':.05,'budget_status':'declared modeling/planning study budget only'},
 'design':[{'id':'design','beta':.5,'R':1.,'mode_Hz':.4,'zeta':.1}],
 'confirmation':[{'id':f'confirm_b{b}_R{r}_f{f}','beta':b,'R':r,'mode_Hz':f,'zeta':.08} for b,r,f in itertools.product([.5,.8],[.5,2.],[.25,.7])],
 'calibration':'only design case can inform debug choices; fixed confirmation cases are not selected on outcomes; log failures/amendments',
 'controllers':['nominal-guard convex optimal','same-cap global target+recovery','no-guard convex diagnostic','robust-guard convex optimal','same-robust-cap global target+recovery'],
 'numerics':{'meshes':[64,128,256],'primary_mesh':256,'quadrature':[32,96],'solver':'original convex SLSQP with extra z<=A(pcap)','inward_feasibility':'global scalar scaling for floating slew/cap residuals, reported','bellman':{'N':[64,128],'sub':[4,8],'cap_appended_to_state_grid':True,'scope':'global restricted finite-state uniform-EOS feasible comparator, not continuous exact certificate'},'EOS_dense_points':2049,'EOS_refinement':'bounded scalar refinement at all dense local maxima plus endpoints','grid_propagation':'closed-form exact constant-slope power segment propagation evaluated in floating arithmetic','time_peak':'analytic stationary points in each forced segment and analytic infinite zero-input tail'},
 'uncertainty':{'gain_factor':[1.,1.1],'mode_factor':[.9,1.1],'damping_factor':[.8,1.],'tests':'all 8 corners plus nominal','robust_guard':'analytic max G at gain1.1, mode0.9, damping0.8; covers full box by proven monotonicity'},
 'secondary':['separate dynamic energy/service time/recovery time/cycle time','slew-only kernel L1 guard','finite-mesh Bellman/convex agreement, no improvement claimed over exact global reference'],
 'software':{'python':platform.python_version(),'numpy':numpy.__version__,'scipy':scipy.__version__},'source_sha256':{}
}
source=ROOT.parents[1]/'full_cycle/code'
for name in ['cycle_model.py','global_bellman.py']:
 f=source/name;p['source_sha256'][str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
f=ROOT/'PROTOCOL.json'
if f.exists():raise RuntimeError('Do not overwrite a frozen protocol')
data=(json.dumps(p,indent=2,sort_keys=True)+'\n').encode();f.write_bytes(data);digest=hashlib.sha256(data).hexdigest();(ROOT/'PROTOCOL.sha256').write_text(digest+'  PROTOCOL.json\n');print(digest)
