from pathlib import Path
import hashlib,json,subprocess,itertools,datetime
import numpy as np
R=Path(__file__).resolve().parent

def run(mode,tag,dt,cp,tau=.005,ramp=30e6,offset=0,service=1):
    args=[str(R/'recovery'),mode,str(R/'original_input.csv'),str(R/tag),str(dt),str(R/cp)]
    if mode=='case':args+=list(map(str,[tau,ramp,offset,service]))
    a=subprocess.run(args,check=True,capture_output=True,text=True)
    j=json.loads(a.stdout);j['command']=args;(R/(tag+'.json')).write_text(json.dumps(j,indent=2)+'\n')
    # Lossless CSV-to-NPZ compact evidence. No original output is overwritten.
    for suff in ['','_dense','_snapshots','_bins']:
        f=R/(tag+suff+'.csv');z=np.genfromtxt(f,delimiter=',',names=True)
        np.savez_compressed(R/(tag+suff+'.npz'),**{k:np.atleast_1d(z[k]) for k in z.dtype.names})
        # Dense redundant text removed only from new recovery workspace after verified array save.
        if suff=='_dense':
            check=np.load(R/(tag+suff+'.npz'));assert all(np.array_equal(check[k],np.atleast_1d(z[k]),equal_nan=True) for k in z.dtype.names);f.unlink()
    return j

def main():
    stage=__import__('sys').argv[1]
    if stage=='warmup':
      for dt in [1e-6,.5e-6]:
        d='h1' if dt==1e-6 else 'h05';run('warmup','warmup_'+d,dt,'checkpoint_'+d+'.csv')
      # Common-clock no-service fork identity is checked before any service run.
      for i in [1,2]:run('case','identity_'+str(i),1e-6,'checkpoint_h1.csv',service=0)
      equal=all((R/('identity_1'+s)).read_bytes()==(R/('identity_2'+s)).read_bytes() for s in ['.csv','_snapshots.csv','_bins.csv'])
      a=np.load(R/'identity_1_dense.npz');b=np.load(R/'identity_2_dense.npz');equal=equal and all(np.array_equal(a[k],b[k]) for k in a.files)
      (R/'COMMON_CLOCK_IDENTITY.json').write_text(json.dumps({'bitwise_identical_healthy_forks':bool(equal),'method':'Same full nominal checkpoint, actual parameters, absolute clock, controller and service-clock gates; independent process runs'},indent=2)+'\n');assert equal
    elif stage=='nominal':
      for dt in [1e-6,.5e-6]:
        d='h1' if dt==1e-6 else 'h05'
        for service in [0,1]:run('case',f'nominal_{d}_s{service}',dt,'checkpoint_'+d+'.csv',service=service)
    elif stage in ['regression','confirmation']:
      ts,rs,os=([.004,.006],[25e6,35e6],[37e-6,73e-6]) if stage=='regression' else ([.0045,.0055],[27e6,33e6],[19e-6,61e-6])
      for tau,ramp,offset,dt in itertools.product(ts,rs,os,[1e-6,.5e-6]):
        d='h1' if dt==1e-6 else 'h05';tag=f'tau{tau*1000:g}_r{ramp/1e6:.0f}_o{offset*1e6:.0f}_{d}'
        for service in [0,1]:run('case',tag+f'_s{service}',dt,'checkpoint_'+d+'.csv',tau,ramp,offset,service)
        print(tag,flush=True)
    else:raise ValueError(stage)
if __name__=='__main__':main()
