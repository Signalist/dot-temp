"""State-continuous energy-buffer observability witnesses. Synthetic mechanisms only."""
from pathlib import Path
import json,time,platform
import numpy as np,pandas as pd
from scipy.integrate import solve_ivp,quad
from scipy.optimize import brentq
from scipy.signal import StateSpace,lsim
P=Path(__file__).parent
P0=10.;A=2.;KAPPA=3.;ETA=.95;PMAX=3.;FREQS=[.25,.5,.75];CAPS=[.5,2.,20.];CYCLES=200;SAMPLES=800;TAU=.5
WINDOWS=[(0,1),(0,5),(20,25),(100,105),(195,200)]

def load_phase(q):return P0+A*np.tanh(KAPPA*np.cos(2*np.pi*np.asarray(q)))
def pref_and_unit_energy():
 def integrals(pref):
  c=quad(lambda q:max(pref-load_phase(q),0.),0,1,epsabs=1e-10,limit=300)[0]
  d=quad(lambda q:max(load_phase(q)-pref,0.),0,1,epsabs=1e-10,limit=300)[0]
  return c,d
 pref=brentq(lambda p:ETA*integrals(p)[0]-integrals(p)[1]/ETA,P0-1,P0+1,xtol=1e-12)
 c,d=integrals(pref);return pref,d/ETA,c,d
PREF,RUNIT,ICHARGE,IDISCHARGE=pref_and_unit_energy()

def control(u,E,C):
 # Invariant-domain checks below verify E remains inside; clipping here protects roundoff only.
 x=np.clip(E,0,C);Es=.05*C
 dc=np.minimum(np.maximum(u-PREF,0.),PMAX);cc=np.minimum(np.maximum(PREF-u,0.),PMAX)
 d=dc*x/(x+Es);c=cc*(C-x)/(C-x+Es)
 return c,d,u+c-d

def grid_system():
 n=6;m=np.array([150.,185.,160.,160.,160.,160.]);d=np.array([25.,30.,26.,26.,26.,26.]);lap=np.zeros((n,n))
 for i,j,k in [(0,1,105.)]+[(1,j,80.) for j in range(2,6)]:
  lap[i,i]+=k;lap[j,j]+=k;lap[i,j]-=k;lap[j,i]-=k
 aa=np.block([[np.zeros((n,n)),2*np.pi*np.eye(n)],[-lap/m[:,None],-np.diag(d/m)]])
 bb=np.zeros((12,2));bb[6+2,0]=-1/m[2];bb[6+3,1]=-1/m[3]
 cc=np.zeros((2,12));cc[0,6]=1;cc[1,7]=1
 return StateSpace(aa,bb,cc,np.zeros((2,2))),aa,bb,cc

def simulate(f,capratio,samples=SAMPLES,rtol=1e-10,atol=1e-11,maxstep_factor=80):
 T=1/f;C=capratio*RUNIT*T;initial=np.array([.01*C,.5*C])
 def rhs(t,x):
  u=load_phase(t/T);c,d,p=control(u,x[:2],C)
  return np.r_[ETA*c-d/ETA,c,d]
 t=np.arange(CYCLES*samples+1)*(T/samples)
 sol=solve_ivp(rhs,(0,CYCLES*T),np.r_[initial,np.zeros(4)],method='DOP853',rtol=rtol,atol=atol,max_step=T/maxstep_factor,t_eval=t)
 if not sol.success:raise RuntimeError(sol.message)
 E=sol.y[:2].T;u=load_phase(t/T);c,d,pcc=control(u[:,None],E,C)
 sys,aa,bb,cc=grid_system();_,y,_=lsim(sys,U=pcc-PREF,T=t);_,yswap,_=lsim(sys,U=pcc[:,::-1]-PREF,T=t)
 energy_residual=E-initial-ETA*sol.y[2:4].T+sol.y[4:6].T/ETA
 # Exact continuous-time contraction bound from the least-negative state derivative over E in [0,C].
 Es=.05*C;period_K=Es/(C+Es)**2*T*(IDISCHARGE/ETA+ETA*ICHARGE)
 qbound=np.exp(-period_K)
 slope_bound=A*KAPPA*2*np.pi*f+PMAX**2/(ETA*Es)
 signed=d-c;actual_slope=np.max(abs(np.diff(signed,axis=0)/(T/samples)))
 meta=dict(frequency_Hz=f,period_s=T,cap_ratio=capratio,capacity_MWs=C,capacity_MWh=C/3600,energy_initial_MWs=initial.tolist(),pref_MW=PREF,
  energy_min_MWs=float(E.min()),energy_max_MWs=float(E.max()),energy_balance_max_MWs=float(abs(energy_residual).max()),
  max_charge_MW=float(c.max()),max_discharge_MW=float(d.max()),min_PCC_MW=float(pcc.min()),max_buffer_slew_MW_per_s=float(actual_slope),buffer_slew_bound_MW_per_s=float(slope_bound),
  PMU_swap_max_error_Hz=float(abs(y-yswap).max()),PMU_peak_Hz=float(abs(y).max()),state_gap_initial_MWs=float(initial[1]-initial[0]),state_gap_end_MWs=float(E[-1,1]-E[-1,0]),
  max_state_gap_increase_MWs=float(np.max(np.diff(E[:,1]-E[:,0]))),period_contraction_bound=float(qbound),
  initial_difference_end_bound_MWs=float((initial[1]-initial[0])*qbound**CYCLES),model_cycles=CYCLES,samples_per_cycle=samples,nfev=sol.nfev,
  physical_scope='Continuous energy and buffer power, finite energy/power/slew within this analyst-defined soft-derating model; not hardware calibration or battery chemistry validation.')
 return dict(t=t,E=E,u=u,c=c,d=d,pcc=pcc,y=y,yswap=yswap,energy_residual=energy_residual,meta=meta)

def harmonic(t,p,f):
 return 2/(t[-1]-t[0])*np.trapezoid(p*np.exp(-2j*np.pi*f*t)[:,None],t,axis=0)

def analytic_hard_comparator():
 # Square load, exact loss-balanced reference; adequate or inadequate energy capacity.
 pref=P0+A*(1-ETA**2)/(1+ETA**2);charge=pref-(P0-A);discharge=P0+A-pref
 out=[]
 for f in FREQS:
  T=1/f;R=ETA*charge*T/2
  for cr in CAPS:
   C=cr*R
   for frac in [.01,.5,.99]:
    E=frac*C;E1=min(C,max(0,E-R)+R);E2=min(C,max(0,E1-R)+R)
    out.append(dict(frequency_Hz=f,capacity_ratio=cr,initial_fraction=frac,R_MWs=R,capacity_MWs=C,E_after_one=E1,E_after_two=E2,
       next_cycle_same_periodic_output=True,steady_type='flat_PCC' if C>=R else 'common_clipped_periodic_PCC'))
 pd.DataFrame(out).to_csv(P/'hard_comparator.csv',index=False)
 return dict(pref_MW=pref,charge_MW=charge,discharge_MW=discharge,energy_rate_charge=ETA*charge,energy_rate_discharge=discharge/ETA,
             period_map='min(C,max(0,E-R)+R)',scope='Ideal hard saturation with power jumps; analytic comparator only, not the continuous main witness')

def main():
 start=time.time();(P/'traces').mkdir(exist_ok=True);rows=[];metas=[];percycles=[];bits=[]
 for f in FREQS:
  for cr in CAPS:
   d=simulate(f,cr)
   before=d['meta'];tol_domain=1e-9
   if before['energy_min_MWs'] < -tol_domain or before['energy_max_MWs'] > before['capacity_MWs']+tol_domain:
    d=simulate(f,cr,rtol=1e-12,atol=1e-13,maxstep_factor=320)
    d['meta']['numerical_domain_refinement']=dict(original_min_MWs=before['energy_min_MWs'],original_max_MWs=before['energy_max_MWs'],rtol=1e-12,atol=1e-13,maxstep_factor=320)
   m=d['meta']
   if m['energy_min_MWs'] < -tol_domain or m['energy_max_MWs'] > m['capacity_MWs']+tol_domain:
    raise RuntimeError('Energy domain validation failed after one bounded numerical refinement')
   m['numerical_domain_tolerance_MWs']=tol_domain
   metas.append(m);tag=f"f{f:g}_cap{cr:g}";t=d['t'];pcc=d['pcc'];s=SAMPLES
   # Save every sampled computed quantity needed to recompute classes, constraints and the observed equivalence.
   np.savez_compressed(P/'traces'/f'{tag}.npz',time_s=t,energy_MWs=d['E'],load_MW=d['u'],charge_MW=d['c'],discharge_MW=d['d'],PCC_MW=pcc,
       PMU_Hz=d['y'],PMU_swapped_Hz=d['yswap'],energy_balance_residual_MWs=d['energy_residual'])
   for left,right in WINDOWS:
    sl=slice(left*s,right*s+1);h=harmonic(t[sl],pcc[sl],f);support=abs(h)>TAU
    different=bool(support[0]!=support[1])
    rows.append(dict(case=tag,frequency_Hz=f,cap_ratio=cr,first_cycle=left,last_cycle=right,window_start_s=t[left*s],window_end_s=t[right*s],
      low_start_harmonic_MW=float(abs(h[0])),high_start_harmonic_MW=float(abs(h[1])),class_world_A=';'.join(map(str,np.flatnonzero(support))),
      class_world_B=';'.join(map(str,np.flatnonzero(support[::-1]))),classes_differ=different,
      ordinary_label_invariant=True,PMU_only_set_claim=not different,energy_bit_resolves=different,direct_PCC_bit_resolves=different))
   for k in range(CYCLES):
    sl=slice(k*s,(k+1)*s+1);h=abs(harmonic(t[sl],pcc[sl],f));percycles.append(dict(case=tag,cycle=k,low_start_harmonic_MW=h[0],high_start_harmonic_MW=h[1],different_source_class=bool((h[0]>TAU)!=(h[1]>TAU))))
   ebits=d['E'][0]<=.1*m['capacity_MWs'];pbits=pcc[0]>PREF+A/4
   assert ebits[0]!=ebits[1] and pbits[0]!=pbits[1]
   bits.append(dict(case=tag,energy_threshold_MWs=.1*m['capacity_MWs'],energy_bit_world_A=bool(ebits[0]),energy_bit_world_B=bool(ebits[1]),
       PCC_threshold_MW=PREF+A/4,PCC_bit_world_A=bool(pbits[0]),PCC_bit_world_B=bool(pbits[1]),
       energy_bit_margin_MWs=float(np.min(abs(d['E'][0]-.1*m['capacity_MWs']))),PCC_bit_margin_MW=float(np.min(abs(pcc[0]-(PREF+A/4)))),
       total_energy_initial_same=True,unlabelled_energy_multiset_same=True,full_state_reconstruction_required=False))
 pd.DataFrame(rows).to_csv(P/'source_class_windows.csv',index=False);pd.DataFrame(percycles).to_csv(P/'per_cycle_harmonics.csv',index=False);pd.DataFrame(bits).to_csv(P/'extra_bit_witnesses.csv',index=False)
 pd.DataFrame(metas).to_csv(P/'physical_validation.csv',index=False)
 # Independent tighter integration/sampling sentinel. Not a second scientific sample.
 ref=simulate(.5,20.,samples=1600,rtol=1e-12);orig=np.load(P/'traces'/'f0.5_cap20.npz');base=next(m for m in metas if m['frequency_Hz']==.5 and m['cap_ratio']==20.)
 eE=float(np.max(abs(ref['E'][::2]-orig['energy_MWs'])));ep=float(np.max(abs(ref['pcc'][::2]-orig['PCC_MW'])))
 sentinel=dict(frequency_Hz=.5,cap_ratio=20,refinement_samples_per_cycle=1600,reference_rtol=1e-12,max_energy_difference_MWs=eE,max_PCC_difference_MW=ep,
    max_PMU_difference_Hz=float(np.max(abs(ref['y'][::2]-orig['PMU_Hz']))),scope='Numerical sensitivity check, not independent physical validation')
 (P/'numerical_sentinel.json').write_text(json.dumps(sentinel,indent=2)+'\n')
 hard=analytic_hard_comparator();df=pd.DataFrame(rows);pc=pd.DataFrame(percycles)
 result=dict(paper_ready=False,model_cases=len(metas),period_windows=len(df),distinct_class_windows=int(df.classes_differ.sum()),
     first_cycle_distinct_cases=int(df[(df.first_cycle==0)&(df.last_cycle==1)].classes_differ.sum()),
     last5_cycle_distinct_cases=int(df[(df.first_cycle==195)&(df.last_cycle==200)].classes_differ.sum()),
     max_energy_balance_error_MWs=max(x['energy_balance_max_MWs'] for x in metas),max_PMU_equivalence_error_Hz=max(x['PMU_swap_max_error_Hz'] for x in metas),
     hard_comparator=hard,numerical_sentinel=sentinel,elapsed_seconds=time.time()-start,
     conclusion='Only transient initial-energy attribution ambiguity is supported. The continuous model has a unique periodic response by contraction; no persistent initial-state-specific FO class is established. One energy bit and one direct-PCC bit both resolve the two-world finite-window witness.',
     environment=dict(python=platform.python_version(),numpy=np.__version__),physical_cases=metas)
 (P/'GATE_C_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
