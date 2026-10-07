from research_lp import *
ps=[(h,float(r),float(r)) for h in [True,False] for r in np.r_[1e-6,np.arange(.25,5.000001,.25)]]
br=[(list(range(21)),5.),(list(range(21,42)),5.)]
x=build_solve('nofeedback_test',ps,br,dt=.01);print(x,flush=True)
