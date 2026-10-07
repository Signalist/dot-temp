import json,pathlib,itertools,numpy as np
R=pathlib.Path(__file__).resolve().parent;cases=json.load(open(R.parent/'TRANSFER_FREEZE.json'))['cases'];rows=[]
for c in cases:
 N,k,L,H,dt,ec,ed=[c[x] for x in ['N','k','L','H','delta','ec','ed']];rho=ec*ed;kap=1/ed-ec
 q=(k*H+rho*(N-k)*L)/(k+rho*(N-k));Q=dt*(N-k)*ec*(q-L);per=[]
 for high in itertools.combinations(range(N),k):
  d=np.full(N,L,dtype=float);d[list(high)]=H;per.append(d)
 def increments(p,d):return dt*np.where(p-d>=0,ec*(p-d),(p-d)/ed)
 states=np.array([Q+np.r_[0,np.cumsum(increments(q,d))] for d in per])
 # Nonflat public schedules chosen before outcomes; not tuned to minimize uncertainty.
 p=np.linspace(L+.2*(H-L),H-.2*(H-L),N)
 residual=np.array([sum(increments(p,d)) for d in per]);rangeformula=dt*kap*(sum(sorted(p)[-k:])-sum(sorted(p)[:k]))
 # A second public block reverses schedule: same task uncertainty, not cancelled.
 residual2=np.array([sum(increments(p[::-1],d)) for d in per]);allends=np.array([a+b for a in residual for b in residual2]);width2=float(np.ptp(allends))
 rows.append({**c,'power_orders':len(per),'q':q,'Q':Q,'capacity':2*Q,'state_min':float(states.min()),'state_max':float(states.max()),'max_reset_error':float(max(abs(states[:,-1]-Q))),'residual_range':float(np.ptp(residual)),'range_formula':rangeformula,'two_block_uncertainty_width':width2,'sum_oneblock_widths':float(np.ptp(residual)+np.ptp(residual2)),'task_total_work_energy':dt*(k*H+(N-k)*L),'grid_total_energy':N*dt*q,'peak_task_power':H,'tests':{'reset':bool(max(abs(states[:,-1]-Q))<1e-10),'sharp_capacity':bool(abs(states.min())<1e-10 and abs(states.max()-2*Q)<1e-10),'assignment_range':bool(abs(np.ptp(residual)-rangeformula)<1e-10),'no_cancellation_by_reversing_public_schedule':bool(abs(width2-(np.ptp(residual)+np.ptp(residual2)))<1e-10)}})
# Scaling invariance is exact algebra: multiply powers by a and time by b -> energies scaleab.
base=rows[0];scaled=cases[0].copy();scaleP=3.7;scaleT=.4;rho=scaled['ec']*scaled['ed'];qq=scaleP*base['q'];Qs=(scaled['delta']*scaleT)*(scaled['N']-scaled['k'])*scaled['ec']*(qq-scaled['L']*scaleP)
out={'scope':'heldout synthetic parameter/contract transfer, not external device validation','cases':rows,'scaling':{'power_factor':scaleP,'time_factor':scaleT,'capacity_scaled':2*Qs,'expected':base['capacity']*scaleP*scaleT,'residual':2*Qs-base['capacity']*scaleP*scaleT},'all_pass':all(all(r['tests'].values()) for r in rows)}
(R/'HELDOUT_TRANSFER_RESULTS.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['all_pass']
