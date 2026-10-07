"""Independent checks only; does not reoptimize or rerun the full transfer study."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from scipy.linalg import expm
from scipy.integrate import quad
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from kundur_transfer import ModalGrid,SOURCE
raw=np.load(SOURCE);A=raw['A'];C=raw['C_frequency_Hz']
results=json.loads((ROOT/'network_transfer/RESULTS.json').read_text())
out={'status':'independent exploratory numerical review; not interval certificate or hardware validation','source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'A_shape':list(A.shape),'input_names':raw['input_names'].tolist(),'kernel_checks':[],'propagation_checks':[],'area_checks':[],'same_cap_checks':[]}
# Direct 51-by-51 exponentials, shared between input ports.
times=[0.,.01,.5,1.,5.,20.,60.,140.]
for t in times:
    E=expm(A*t)
    for bus,col in [(7,0),(8,2)]:
        grid=ModalGrid(SOURCE,col,200.)
        direct=C@E@grid.B
        modal=np.real(np.exp(grid.lam*t)@grid.res.T)
        out['kernel_checks'].append({'bus':bus,'gain':200.,'time':t,'direct':direct.tolist(),'modal':modal.tolist(),'max_abs_error':float(max(abs(direct-modal)))})
# Forced response with a separate augmented-matrix propagation.
for bus,col in [(7,0),(8,2)]:
    grid=ModalGrid(SOURCE,col,200.);q=np.zeros(51,dtype=complex);xx=np.zeros(51)
    aug=np.zeros((53,53));aug[:51,:51]=A;aug[:51,51]=grid.B;aug[51,52]=1
    for p,u,T in [(0.,1.,.23),(.23,-.4,.31),(.106,.1,.5),(.156,-1.,.156),(0.,0.,10.)]:
        qnext=grid.advance(q,p,u,T)
        direct=(expm(aug*T)@np.r_[xx,p,u])[:51]
        modal_state=np.real(grid.V@(grid.beta*qnext))
        ym=np.real(grid.res@qnext);yd=C@direct
        _,lo,up=grid.segment_peak(q,p,u,T)
        # Independent much finer modal observations; analytic review supplies the bound between them.
        fine=np.linspace(0,T,10001)
        ev=np.exp(fine[:,None]*grid.lam);zz=ev*q+p*np.expm1(fine[:,None]*grid.lam)/grid.lam+u*(np.expm1(fine[:,None]*grid.lam)-fine[:,None]*grid.lam)/grid.lam**2
        peak=np.max(abs(np.real(zz@grid.res.T)),axis=0)
        out['propagation_checks'].append({'bus':bus,'gain':200.,'p_start':p,'slope':u,'duration':T,'state_max_abs_error':float(max(abs(direct-modal_state))),'output_max_abs_error':float(max(abs(yd-ym))),'sample_lower':lo.tolist(),'reported_upper':up.tolist(),'fine_sample_peak':peak.tolist(),'minimum_upper_minus_fine_peak':float(min(up-peak))})
        q=qnext;xx=direct
# Independently recompute h+/- interpolation integrals from archived samples.
for case in results:
    bus=case['bus'];gain=case['gain'];b=case['gain_bounds'];d=np.load(ROOT/f'network_transfer/kernel_bus{bus}_gain{gain}.npz');t=d['time'];h=d['frequency_impulse_Hz_per_model_power'];dt=np.diff(t)
    pos=np.zeros(4);neg=np.zeros(4)
    for j in range(4):
        l=h[:-1,j];r=h[1:,j];same=l*r>=0
        signed=(l+r)*dt/2
        pos[j]=signed[same&(signed>0)].sum();neg[j]=-signed[same&(signed<0)].sum()
        ix=~same;frac=abs(l[ix])/(abs(l[ix])+abs(r[ix]));aa=l[ix]*dt[ix]*frac/2;bb=r[ix]*dt[ix]*(1-frac)/2
        pos[j]+=np.maximum(aa,0).sum()+np.maximum(bb,0).sum();neg[j]+=np.maximum(-aa,0).sum()+np.maximum(-bb,0).sum()
    grid=ModalGrid(SOURCE,0 if bus==7 else 2,gain);T=t[-1];step=t[1]-t[0];N=len(t)-1
    geom=(1-np.exp(grid.lam.real*N*step))/(1-np.exp(grid.lam.real*step))
    interp=step**3/8*np.sum(abs(grid.res*grid.lam**2)*geom,axis=1)
    tail=np.sum(abs(grid.res)*np.exp(grid.lam.real*T)/(-grid.lam.real),axis=1)
    out['area_checks'].append({'bus':bus,'gain':gain,'positive_area_error':float(max(abs(pos-np.array(b['positive_interpolant_area'])))),'negative_area_error':float(max(abs(neg-np.array(b['negative_interpolant_area'])))),'remainder_formula_error':float(max(abs(interp-np.array(b['interpolation_area_remainder'])))),'tail_formula_error':float(max(abs(tail-np.array(b['tail_area_remainder'])))),'stable':bool(np.all(grid.lam.real<0)),'modal_condition':grid.condition,'max_pole_real':grid.maxreal})
    cap=min(1.,case['guard_cap']);tar=case['same_cap_global_target'];sol=case['policies']['guarded'];M=2.;R=1.
    def costs(x,z):
        sums=np.zeros(3)
        for i in range(len(x)-1):
            l,r=x[i:i+2];v=(z[i+1]-z[i])/(r-l)
            def evaluate(w,k):
                zz=max(0,z[i]+v*(w-l));p=(1.5*zz)**(2/3);S=1-w/M
                if k==0:return S*np.sqrt(p)+p*p/(2*R*M)
                if k==1:return S/np.sqrt(p)+p/(R*M)
                return S*(p+1)/np.sqrt(p)+(p*p/2+p)/(R*M)
            for k in range(3):sums[k]+=quad(lambda w:evaluate(w,k),l,r,epsabs=1e-11,epsrel=1e-11,limit=100)[0]
        return sums
    co=costs(np.linspace(0,2,len(sol['z'])),sol['z']);ct=costs(tar['x'],tar['z'])
    observed=1-co[2]/ct[2]
    out['same_cap_checks'].append({'bus':bus,'gain':gain,'shared_power_cap':cap,'solver_recorded_cap':sol['physical_pcap'],'solver_peak_power':float(max((1.5*np.array(sol['z']))**(2/3))),'target_peak_power':tar['target'],'solver_direct_energy_cycle_objective':co.tolist(),'target_direct_energy_cycle_objective':ct.tolist(),'solver_objective_error':float(abs(co[2]-sol['parts']['objective'])),'target_objective_error':float(abs(ct[2]-tar['parts']['objective'])),'relative_gain_direct':float(observed),'relative_gain_recorded':case['guarded_gain_vs_target'],'all_work_all_time_amplitude_bound_max':float(cap*max(case['gain_bounds']['G_upper'])),'replay_upper_max':float(max(max(r['frequency_peak_upper_Hz']) for r in sol['replays']))})
out['summary']={'kernel_max_abs_error':max(a['max_abs_error'] for a in out['kernel_checks']),'propagation_output_max_abs_error':max(a['output_max_abs_error'] for a in out['propagation_checks']),'propagation_state_max_abs_error':max(a['state_max_abs_error'] for a in out['propagation_checks']),'minimum_intersample_upper_minus_fine_peak':min(a['minimum_upper_minus_fine_peak'] for a in out['propagation_checks']),'max_independent_objective_error':max(max(a['solver_objective_error'],a['target_objective_error']) for a in out['same_cap_checks'])}
review_path=ROOT/'review/NETWORK_TRANSFER_REVIEW.json'
previous=json.loads(review_path.read_text()) if review_path.exists() else {}
for key in ['analytic_review','support_lp_review_file','portability_review']:
    if key in previous:out[key]=previous[key]
out['portability_review']={'bundled_source':'inputs/kundur_reduced51.npz','sha256':out['source_sha256'],'verifier_resolves_source':'imports SOURCE from code/kundur_transfer.py','source_is_bundled':SOURCE.resolve()==(ROOT/'inputs/kundur_reduced51.npz').resolve()}
review_path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out['summary'],indent=2))
print(json.dumps(out['same_cap_checks'],indent=2))
