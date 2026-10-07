from g6_model import *
from analyze_envelopes import many_transfer
import json,time,sys,hashlib
import pandas as pd
OUT=Path(__file__).resolve().parents[1]

def generate_cases(m,env):
    rng=np.random.default_rng(6022026+MODELS.index(m.cfg)*1000);cases=[]
    methods=['candidate_independent_grid_template_safe','classic_shared_grid_template_safe','phase_free_harmonic_shared_grid_safe','sparse_3x9_template_UNCERTIFIED']
    shared=env['shared_upper'];cuts=env['kappa_cuts'];ks=env['kappa_samples'];wit=env['sample_search_seed']
    for scenario in range(40):
        w=np.array([rng.uniform(.05,.95),0]);w[1]=1-w[0]
        if scenario<20:
            k=float(rng.uniform(.85,1.15));fs=rng.uniform(.08,.75,2);phase=rng.uniform(0,2*np.pi,2);kind='random'
        else:
            score=np.einsum('kji,i->kj',shared[:,0],w);ki,j=np.unravel_index(np.argmax(score),score.shape)
            k=(cuts[ki]+cuts[ki+1])/2;kidx=np.argmin(abs(ks-k));fs=wit[kidx,j,:,0].copy();phase=np.array([m.peak_root(fs[i],k)[1][j,i] for i in range(2)]);kind='peak_witness'
        for method in methods:
            c=env[method];lam=.99/np.max(c@w)
            if method.endswith('_safe'):assert np.max(isum(mul(iv(c),iv((lam*w)[None,:])),axis=1)[1])<=1.
            cases.append({'id':len(cases),'scenario':scenario,'method':method,'condition':'fixed_template','kind':kind,'kappa':k,'fs':fs.tolist(),'phases':phase.tolist(),'amps':(lam*w).tolist(),'initial':'linear_steady','waveform_or_initial_contract_breach':False,'nonlinear_model_extension':True})
    # Predeclared contract-break tests. These do not count as failures of the fixed-period certificate.
    for condition in ['zero_state_start','frequency_drift','harmonic_phase_breach']:
        for scenario in range(12):
            base=dict(cases[(20+scenario)%40*4+1]);base['id']=len(cases);base['condition']=condition;base['waveform_or_initial_contract_breach']=True
            if condition=='zero_state_start':base['initial']='zero'
            if condition=='frequency_drift':
                base['requested_drift_amplitudes']=[.04,.035]
                ff=np.array(base['fs']);base['drift_amplitudes']=np.minimum([.04,.035],np.minimum(ff-.08,.75-ff)).tolist()
            if condition=='harmonic_phase_breach':base['harmonic_offsets']=rng.uniform(-np.pi,np.pi,(2,3)).tolist()
            cases.append(base)
    return cases

def run(m,cases,dt=.02,T=90.,keep=True):
    B=len(cases);n=m.n;kappa=np.array([c['kappa'] for c in cases]);amp=np.array([c['amps'] for c in cases]);fs=np.array([c['fs'] for c in cases]);phase=np.array([c['phases'] for c in cases]);offset=np.array([c.get('harmonic_offsets',np.zeros((2,3))) for c in cases]);drift=np.array([c.get('drift_amplitudes',[0,0]) for c in cases])
    # Bounded time-varying instantaneous frequencies for drift challenges.
    drift=np.minimum(drift,np.minimum(fs-.08,.75-fs))
    def initial_state(c):
        if c['initial']=='zero':return np.zeros(2*n)
        if 'harmonic_offsets' not in c:return m.linear_state(0,c['amps'],c['fs'],c['phases'],c['kappa'])
        z=np.zeros(2*n)
        for si,src in enumerate(m.sources):
            residues=m.sign*m.sign[src][None,:]/n
            for ih,h in enumerate(m.hs):
                w=2*np.pi*h*c['fs'][si];den=c['kappa']*m.lam-m.M*w*w/(2*np.pi)+1j*m.D*w/(2*np.pi)
                theta=-np.sum(residues/den[None,:],axis=1)*(-1j)*c['amps'][si]/h*np.exp(1j*(h*c['phases'][si]+c['harmonic_offsets'][si][ih]))
                z[:n]+=theta.real;z[n:]+=(1j*w/(2*np.pi)*theta).real
        return z
    x=np.array([initial_state(c) for c in cases]);times=np.arange(round(T/dt)+1)*dt
    states=np.empty((len(times),B,2*n),float) if keep else None;loads=np.empty((len(times),B,2),float) if keep else None;peaks=np.zeros(B);peak_t=np.zeros(B);peak_j=np.zeros(B,int)
    def power(t):
        th=2*np.pi*fs*t+phase+drift*35*(1-np.cos(2*np.pi*t/35))
        return amp*np.sum(np.sin(th[:,:,None]*m.hs[None,None,:]+offset)/m.hs[None,None,:],axis=2)
    def rhs(t,z):
        p=power(t);theta=z[:,:n];freq=z[:,n:];net=np.zeros((B,n))
        for i,j,k in m.edges:
            flow=kappa*k*np.sin(theta[:,i]-theta[:,j]);net[:,i]+=flow;net[:,j]-=flow
        load=np.zeros((B,n));load[:,m.sources]=p
        return np.concatenate([2*np.pi*freq,(-m.D*freq-net-load)/m.M],axis=1)
    def observe(it,t):
        nonlocal peaks,peak_t,peak_j
        outs=np.empty((B,m.J));outs[:,:n]=abs(x[:,n:])/.05
        for jj,(i,j,k) in enumerate(m.edges):outs[:,n+jj]=abs(kappa*k*np.sin(x[:,i]-x[:,j]))/15
        pp=outs.max(axis=1);changed=pp>peaks;peak_t[changed]=t;peak_j[changed]=outs.argmax(axis=1)[changed];peaks=np.maximum(peaks,pp)
        if keep:states[it]=x;loads[it]=power(t)
    observe(0,0.)
    for it,t in enumerate(times[:-1]):
        a=rhs(t,x);b=rhs(t+dt/2,x+a*dt/2);c=rhs(t+dt/2,x+b*dt/2);d=rhs(t+dt,x+c*dt);x+=dt*(a+2*b+2*c+d)/6
        observe(it+1,t+dt)
    return {'times':times,'states':states,'loads':loads,'peaks':peaks,'peak_time':peak_t,'peak_output':peak_j}

def main(cfg):
    start=time.time();m=Model(cfg);env=np.load(OUT/'raw'/f"{cfg['name']}_envelope_coefficients.npz");cases=generate_cases(m,env)
    # Freeze all scenario realizations before integrating.
    path=OUT/'raw'/f"{cfg['name']}_challenge_cases.json";path.write_text(json.dumps(cases,indent=2));digest=hashlib.sha256(path.read_bytes()).hexdigest()
    r=run(m,cases);rows=[]
    for i,c in enumerate(cases):rows.append({**{k:v for k,v in c.items() if k not in ['fs','phases','amps','harmonic_offsets','drift_amplitudes']},'model':cfg['name'],'a0_MW':c['amps'][0],'a1_MW':c['amps'][1],'f0_Hz':c['fs'][0],'f1_Hz':c['fs'][1],'peak_ratio':r['peaks'][i],'peak_time_s':r['peak_time'][i],'peak_output':m.labels[r['peak_output'][i]],'sampled_violation':bool(r['peaks'][i]>1+1e-9)})
    for starti in range(0,len(cases),16):
        end=min(starti+16,len(cases));np.savez_compressed(OUT/'raw'/f"{cfg['name']}_traces_{starti:03d}_{end-1:03d}.npz",t=r['times'],x=r['states'][:,starti:end],pcc_P_MW=r['loads'][:,starti:end],case_ids=np.arange(starti,end),peak_ratio=r['peaks'][starti:end])
    pd.DataFrame(rows).to_csv(OUT/'results'/f"{cfg['name']}_challenge_trials.csv",index=False)
    # Most severe fixed-template nonlinear shared-baseline stress case and overall worst get dt/2 checks. No nonlinear trace is covered by the LTI theorem.
    choose=[int(np.argmax(r['peaks']))]
    inx=[i for i,c in enumerate(cases) if c['condition']=='fixed_template' and c['method']=='classic_shared_grid_template_safe'];choose.append(inx[int(np.argmax(r['peaks'][inx]))]);choose=sorted(set(choose))
    fine=run(m,[cases[i] for i in choose],dt=.01)
    np.savez_compressed(OUT/'raw'/f"{cfg['name']}_dt_half_traces.npz",t=fine['times'],x=fine['states'],pcc_P_MW=fine['loads'],case_ids=np.array(choose),peak_ratio=fine['peaks'])
    conv=[{'case_id':i,'coarse_peak':float(r['peaks'][i]),'fine_peak':float(fine['peaks'][j]),'abs_difference':float(abs(r['peaks'][i]-fine['peaks'][j]))} for j,i in enumerate(choose)]
    df=pd.DataFrame(rows);summary=df.groupby(['method','condition']).agg(n=('id','size'),sampled_violations=('sampled_violation','sum'),worst_ratio=('peak_ratio','max')).reset_index();summary.to_csv(OUT/'results'/f"{cfg['name']}_challenge_summary.csv",index=False)
    meta={'model':cfg['name'],'scenario_file_sha256':digest,'cases':len(cases),'dt':.02,'T_s':90,'raw_state_dtype':'float64','dt_half_checks':conv,'seconds':time.time()-start,'nonlinear_scope':'sin(angle) synthetic swing grid, no Q/voltage/converter physics, sample peaks only','linear_steady_initial_is_not_nonlinear_periodic_initial':True}
    (OUT/'results'/f"{cfg['name']}_challenge_metadata.json").write_text(json.dumps(meta,indent=2));print(json.dumps(meta),summary.to_string(index=False),flush=True)
if __name__=='__main__':
    for cfg in MODELS:
        if len(sys.argv)>1 and cfg['name'] not in sys.argv[1:]:continue
        main(cfg)
