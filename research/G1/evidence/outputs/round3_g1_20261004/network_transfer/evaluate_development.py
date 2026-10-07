from design_controller import *
T=np.arange(0,HORIZON+.01,.02);K=kernel(T)
# A fine public phase sweep diagnoses initial sparse-training undercoverage only.
rows=[]
for fb in [True,False]:
 for hi in [False,True]:
  tag=f'{"feedback" if fb else "openloop"}_{"high" if hi else "low"}_b0.093_dr0.5';theta=np.load(OUT/(tag+'.npz'))['theta']
  worst=(0,None);me=0;mc=0
  for r in np.r_[.0001,np.arange(.025,5.00001,.025)]:
   M,D=mapping(r,hi,fb);p=M@theta;y=loadtrace(T,r,hi)-((K@p[1:-1]).reshape(-1,4));pk=float(np.max(abs(y)));m=metrics(p)
   rows.append(dict(controller=tag,r=float(r),peak_Hz=pk,**m))
   if pk>worst[0]:worst=(pk,float(r))
   me=max(me,m['E_MWs']);mc=max(mc,m['max_command_MW'])
  print(tag,dict(worst=worst,max_E=me,max_command=mc),flush=True)
(OUT/'DEVELOPMENT_PHASE_SWEEP.json').write_text(json.dumps(rows,indent=2))
