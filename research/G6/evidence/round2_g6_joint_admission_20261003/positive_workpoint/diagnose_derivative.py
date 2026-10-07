import sys,os;sys.dont_write_bytecode=True;os.environ['OPENBLAS_NUM_THREADS']='1'
from grid_adapter import *
s=build('kundur',buses=[7,8],dt=1/128,tf=10,baseline_MW=[50,50],baseline_Mvar=[0,0]);K,mass,G=descriptor(s);n=s.dae.n;x0=s.dae.x.copy();y0=s.dae.y.copy();rng=np.random.default_rng(2601003);z=rng.normal(size=len(mass));z/=np.linalg.norm(z)
def fg(a):
 s.dae.x[:]=x0+a*z[:n];s.dae.y[:]=y0+a*z[n:];s.vars_to_models();s.TDS.fg_update(s.exist.pflow_tds);return s.dae.fg.copy()
c=(fg(1e-6)-fg(-1e-6))/(2e-6);ex=K@z;err=c-ex;names=s.dae.x_name+s.dae.y_name
for i in np.argsort(abs(err))[-20:][::-1]:print(i,names[i],c[i],ex[i],err[i])
for m in ['Slack','PV','GENROU']:
 mm=getattr(s,m);print(m,[(k,np.asarray(v.v).tolist()) for k,v in mm.services.items() if k in ['p0','q0','Pe0','Qe0']]);print('P',[(k,v.v.tolist()) for k,v in mm.cache.all_vars.items() if k.lower() in ['p','q','pe','qe','tm']])
