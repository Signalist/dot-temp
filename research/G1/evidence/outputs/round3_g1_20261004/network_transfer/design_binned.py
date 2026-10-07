from design_controller import *
# One midpoint per information-equivalence bin. Sampling boundaries are separate
# in the later sensitivity certificate; this solve alone is not continuum robust.
phases=np.arange(.05,5.,.1)
result=[]
for fb in [True,False]:
 for hi in [False,True]:
  tag=f'binned_{"feedback" if fb else "openloop"}_{"high" if hi else "low"}'
  r,theta=solve(hi,fb,phases,band=.0915,dt=.5);r['tag']=tag
  (OUT/(tag+'.json')).write_text(json.dumps(r,indent=2));result.append(r)
  if theta is not None:np.savez_compressed(OUT/(tag+'.npz'),theta=theta,nodes=nodes,initial_high=hi,feedback=fb,phases=phases,band=.0915)
(OUT/'BINNED_DESIGN_RESULTS.json').write_text(json.dumps(result,indent=2))
