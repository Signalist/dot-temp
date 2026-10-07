from exact_observation_contract import *
from design_controller import OUT,mapping,metrics,p_class
import json,hashlib
from decimal import Decimal
from datetime import datetime,timezone
midmax=0.;online_max=0.;legacy_disagreements=0;examples=[];tested=0;maxcmd=0.;maxslew=0.;maxE={'feedback':0.,'openloop':0.}
for fb in [True,False]:
 for hi in [False,True]:
  tag=f'binned93_{"feedback" if fb else "openloop"}_{"high" if hi else "low"}';data=np.load(OUT/(tag+'.npz'));theta=data['theta']
  for j in range(1,51):
   r=(Decimal(j)-Decimal('.5'))/10;M,D=bin_mapping(j,hi,fb);old,_=mapping(float(r),hi,fb);midmax=max(midmax,float(np.max(abs(M-old))))
   m=metrics(M@theta);maxcmd=max(maxcmd,m['max_command_MW']);maxslew=max(maxslew,m['max_slew_MW_s']);maxE['feedback' if fb else 'openloop']=max(maxE['feedback' if fb else 'openloop'],m['E_MWs'])
  for j in range(1,51):
   for delta in ['-.00000001','-.00000000001','-.00000000000001','0','.00000000000001','.00000000001','.00000001']:
    r=Decimal(j)/10+Decimal(delta)
    if not 0<r<=5:continue
    first=first_edge_sample(r);M,D=bin_mapping(first,hi,fb)
    cls=np.array([class_at_sample(n,first,hi) for n in range(nfree)]);noise=np.where(np.arange(nfree)%2, -5.,5.);meas=50+50*cls+noise
    p=online_power_from_measured_samples(theta,hi,meas,fb);online_max=max(online_max,float(np.max(abs(p-M@theta))));tested+=1
    oldclasses=p_class(np.arange(nfree)/10,float(r),hi)
    bad=np.where(oldclasses!=cls)[0]
    if len(bad):
     legacy_disagreements+=1
     if len(examples)<8:examples.append(dict(r_exact=str(r),first_edge_sample=first,initial_high=hi,sample_indices=bad.tolist()))
long_tests=[];long_policy_tests=0
# Build exact 100-digit finite decimal strings using integers only. In
# particular 0.1+1e-100 must map to edge2, not round back to edge1.
N=100;den=10**N
for edge in [1,7,25,49,50]:
 for offset in [-1,0,1]:
  num=edge*10**(N-1)+offset;whole,frac=divmod(num,den);phase=f'{whole}.{frac:0{N}d}'
  if num>5*den:
   try:first_edge_sample(phase)
   except ValueError:long_tests.append({'phase':phase,'domain_rejection':True});continue
   raise AssertionError('Phase beyond5 accepted')
  expected=edge+(1 if offset>0 else 0);first=first_edge_sample(phase);assert first==expected
  long_tests.append({'phase':phase,'expected_first_edge':expected,'actual_first_edge':first})
  for fb in [True,False]:
   for hi in [False,True]:
    tag=f'binned93_{"feedback" if fb else "openloop"}_{"high" if hi else "low"}';theta=np.load(OUT/(tag+'.npz'))['theta'];M,D=bin_mapping(first,hi,fb)
    cls=np.array([class_at_sample(n,first,hi) for n in range(nfree)]);noise=np.where(np.arange(nfree)%2,-5.,5.);meas=50+50*cls+noise
    p=online_power_from_measured_samples(theta,hi,meas,fb);online_max=max(online_max,float(np.max(abs(p-M@theta))));tested+=1;long_policy_tests+=1
result={'audit_utc':datetime.now(timezone.utc).isoformat(),'exact_rule':'First edge index=ceil(10*r); subsequent edges every50 sample indices. Bin ((j-1)/10,j/10]. At a physical edge the new right-continuous class is observed. No epsilons.','near_boundary_policy_tests':tested,'very_long_phase_decimal_digits':N,'very_long_phase_parser_tests':long_tests,'very_long_phase_policy_tests':long_policy_tests,'parser':'fractions.Fraction with integer ceil(10*numerator/denominator)','frozen_midpoint_mapping_max_difference':midmax,'online_measurement_policy_vs_exact_bin_max_difference_MW':online_max,'old_helper_class_disagreement_cases':legacy_disagreements,'old_helper_examples':examples,'all_exact_bin_max_command_MW':maxcmd,'command_float_tolerance_MW':1e-9,'command_within_float_tolerance':bool(maxcmd<=50+1e-9),'all_exact_bin_max_slew_MW_s':maxslew,'exact_bin_max_E_MWs':maxE,'frozen_coefficients_or_inputs_modified':False,'certificate_effect':'All50 midpoint trajectories match exactly; analytic phase radius remains .05s and saved LTI bounds remain unchanged for the exact online policy. The frozen epsilon-tolerant load helper must not define near-boundary continuum semantics.','source_sha256':hashlib.sha256((OUT/'exact_observation_contract.py').read_bytes()).hexdigest()}
assert midmax<1e-12 and online_max<1e-12 and maxcmd<=50+1e-9
(OUT/'BOUNDARY_CONTRACT_AUDIT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
