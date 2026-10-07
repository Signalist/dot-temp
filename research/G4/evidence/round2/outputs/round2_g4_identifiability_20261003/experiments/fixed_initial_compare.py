import json,pathlib
from causal_horizon_design import design
R=pathlib.Path(__file__).resolve().parent
rows=[]
for eta in [.999,.99,.95,.8]:
 for K in [1,2,5,10,20,100]:rows.append(design(K,ec=eta,ed=eta,initial_fraction=.5))
# Frozen device operation: C=18, exactly half initial SOC, deadline band+.5.
horiz=[design(K,initial_fraction=.5,capacity_value=18) for K in range(1,11)]
# Positive tolerance scale at fixed 10 blocks and fixed initial fraction.
tol=[design(10,tau=t,initial_fraction=.5) for t in [0,.01,.05,.1,.25,.5,1,2,4]]
# No fraction advantage exact theorem, hardware power rate=12 held fixed.
exact=[design(1,ec=e,ed=e,tau=0,initial_fraction=.5) for e in [1,.999,.99,.95,.8]]
allok=[r for r in rows+horiz+tol+exact if r['success']]
tests={'feasible_states':all(r['soc_min']>=-1e-7 and r['soc_max']<=r['capacity']+1e-7 for r in allok),'correct_initial_soc':all(abs(r['e0']-.5*r['capacity'])<1e-7 for r in allok),'recovery':all(r['max_recovery_error']<=r['tau']+1e-7 for r in allok),'dual_gap':all(abs(r['primal_dual_gap'])<1e-7 for r in allok)}
out={'scope':'stronger same-known-initial-SOC-fraction comparison; no SOC redesign advantage','fixed_half':rows,'fixed_hardware_horizon':horiz,'positive_tolerance':tol,'exact':exact,'tests':tests}
(R/'FIXED_INITIAL_RESULTS.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'tests':tests,'eta95':[(r['K'],r['capacity']) for r in rows if r['ec']==.95],'hardware':[(r['K'],r['success'],r.get('capacity')) for r in horiz],'tolerance':[(r['tau'],r['capacity']) for r in tol]},indent=2));assert all(tests.values())
