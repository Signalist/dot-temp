from design_controller import *
from datetime import datetime,timezone
SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
CASES=OUT/'confirmation';CASES.mkdir(exist_ok=True)
plan=json.loads((OUT/'HOLDOUT_PLAN.json').read_text())

def make_it(r,high,scale=1.,ramp=0.,end=300.):
 rows=[[0.,0.,0.],[1.,scale*(100 if high else 50),0.]]
 for k,tt in enumerate(np.arange(r,end+1e-8,5.)):
  before=(100 if high else 50) if k%2==0 else (50 if high else 100);after=150-before
  if ramp:
   for delta in np.arange(.01,ramp+.00001,.01):rows.append([1+tt+delta,scale*(before+(after-before)*delta/ramp),0.])
  else:rows.append([1+tt,scale*after,0.])
 return np.array(rows)

def generate(fb,hi,r,scale=1.,ramp=0.,fine=False):
 tag=f'binned93_{"feedback" if fb else "openloop"}_{"high" if hi else "low"}'
 path=OUT/(tag+'.npz');theta=np.load(path)['theta'];it=make_it(r,hi,scale,ramp)
 samples=np.arange(0,12.100001,.1);ix=np.searchsorted(it[:,0],1+samples+1e-10,side='right')-1;actual=it[ix,1]
 noise=np.where(np.arange(len(samples))%2==0,5.,-5.);measured=actual+noise;classes=(measured>=75).astype(int)
 p=np.zeros(len(nodes));selections=[]
 for j in range(nfree):
  # At segment start, retrieve only observations whose arrival time has passed.
  # Initial class is known; no true-phase parameter is used in this policy step.
  past=np.where(samples+.05<=nodes[j]+1e-10)[0]
  cls=int(classes[past[-1]]) if len(past) else int(hi)
  p[j+1]=theta[j*(2 if fb else 1)+(cls if fb else 0)];selections.append(cls)
 discharge=float(areaweights@p[1:ns]);p[-3]=p[-2]=-discharge/(ETA**2*RECOVERY_AREA)
 be=np.c_[np.r_[0.,1+nodes],np.r_[0.,p],np.zeros(len(nodes)+1)]
 label=f'{"fb" if fb else "ol"}_{"high" if hi else "low"}_r{r:g}_s{scale:g}_ramp{ramp:g}'+('_fine' if fine else '')
 itp=CASES/(label+'_it.csv');bep=CASES/(label+'_bess.csv');obsp=CASES/(label+'_observations.csv')
 np.savetxt(itp,it,delimiter=',',header='time_s,IT_MW,IT_Mvar',comments='',fmt='%.12g');np.savetxt(bep,be,delimiter=',',header='time_s,BESS_injection_MW,BESS_Mvar',comments='',fmt='%.12g')
 np.savetxt(obsp,np.c_[samples,samples+.05,actual,noise,measured,classes],delimiter=',',header='sample_relative_s,arrival_relative_s,true_P_MW,error_MW,measured_P_MW,class_high',comments='',fmt='%.12g')
 mm=metrics(p)
 if scale==1 and ramp==0:
  Mp,D=mapping(r,hi,fb);assert np.max(abs(Mp@theta-p))<1e-8, 'Independent observed-history evaluator disagrees'
 row=dict(label=label,controller=tag,initial_high=hi,r_s=r,Pscale=scale,ramp_s=ramp,dt_s=1/(256 if fine else 128),tf_s=101.,it_csv=str(itp),bess_csv=str(bep),observations_csv=str(obsp),it_sha256=SHA(itp),bess_sha256=SHA(bep),observations_sha256=SHA(obsp),controller_sha256=SHA(path),physics=mm,scope='finite nonlinear confirmation; stress is outside exact-level contract' if scale!=1 or ramp else 'frozen unseen-phase nominal confirmation')
 return row

if __name__=='__main__':
 out=[]
 for fb in [True,False]:
  for hi in [False,True]:
   for r in plan['holdout_remaining_stage_s']:out.append(generate(fb,hi,r))
 for c in plan['stress_cases']:out.append(generate(True,c['initial_high'],c['r_s'],c['Pscale'],c['ramp_s']))
 for c in plan['fine_repeats']:out.append(generate(c['controller']=='sampled_P_feedback',c['initial_high'],c['r_s'],fine=True))
 manifest={'freeze_created_utc':datetime.now(timezone.utc).isoformat(),'holdout_plan_sha256':SHA(OUT/'HOLDOUT_PLAN.json'),'model_sha256':SHA(SRC),'analysis_source_sha256':SHA(OUT/'design_controller.py'),'freeze_source_sha256':SHA(__file__),'cases':out,'acceptance':'solver completes to stated horizon; max absolute individual-generator frequency <=0.1 Hz. Physics checked independently; no replacement by COI.','scope':'22 finite tests including repeats and stresses; not independent statistical samples or uniform nonlinear theorem'}
 path=OUT/'CONFIRMATION_FREEZE.json'
 if path.exists():raise RuntimeError('Frozen manifest already exists; do not overwrite')
 path.write_text(json.dumps(manifest,indent=2));print('Frozen',len(out),'cases',SHA(path));print('Worst physical caps',max(x['physics']['max_command_MW'] for x in out),max(x['physics']['max_slew_MW_s'] for x in out))
