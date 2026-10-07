"""Audit-only reruns and separately implemented artifact/physics checks.
No writes into researcher or round2 directories.
"""
from pathlib import Path
import sys,json,hashlib,importlib.util,math,shutil
import numpy as np
import mpmath as mp
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent/'round3_g1_20261004'
NET=ROOT/'network_transfer'
BASE=HERE.parent/'round2_20261003'
checks=[]
def ck(name,ok,detail=None):
    checks.append(dict(name=name,passed=bool(ok),detail=detail))
    if not ok: raise AssertionError((name,detail))
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mod(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
# Direct reruns already write only in audit snapshot. Compare science fields.
for filename in ['interval_lower_certificate.json','interval_summary.json']:
    old=read(ROOT/'raw'/filename);new=read(HERE/'snapshot/raw'/filename)
    def without_seconds(o):
        if isinstance(o,dict):return {k:without_seconds(v) for k,v in o.items() if k!='seconds'}
        if isinstance(o,list):return [without_seconds(v) for v in o]
        return o
    ck('exact_reproduction_'+filename,without_seconds(old)==without_seconds(new))
# Every variable kind and all infinite-side multipliers independently checked.
d=np.load(ROOT/'raw/continuum_prefix_dt0.001.npz');n=5000;block=4*n+3;nv=2*block+2
ld=d['lower_dual'];ud=d['upper_dual'];eq=d['eq_dual'];ineq=d['ineq_dual']
ck('dual_dimensions',len(ld)==len(ud)==nv and len(eq)==2*(1+3*n) and len(ineq)==2*(n+1)+1)
finite_lower=np.zeros(nv,dtype=bool);finite_upper=np.zeros(nv,dtype=bool)
for group in range(2):
    x=group*block;y=x+n+1;s=y+n+1;u=s+n+1
    finite_lower[x]=finite_upper[x]=True
    finite_lower[y:y+n+1]=finite_upper[y:y+n+1]=True
    finite_lower[s:s+n+1]=True
    finite_lower[u:u+n]=finite_upper[u:u+n]=True
finite_lower[-2:]=True
ck('all_infinite_side_multipliers_zero',np.all(ld[~finite_lower]==0) and np.all(ud[~finite_upper]==0))
ck('all_dual_cone_signs',np.all(ld>=0) and np.all(ud<=0) and np.all(ineq<=0))
# Repeat 40-dps outward lower at 75 dps; compare conservative public decimal.
lower_mod=mod('audit_lower',HERE/'snapshot/core/interval_lower_certificate.py')
mp.mp.dps=110;mp.iv.dps=75
precision_root=HERE/'precision75';(precision_root/'raw').mkdir(parents=True,exist_ok=True)
shutil.copy2(ROOT/'raw/continuum_prefix_dt0.001.npz',precision_root/'raw/continuum_prefix_dt0.001.npz')
lower_mod.ROOT=precision_root
lower_mod.solve()
hires=read(precision_root/'raw/interval_lower_certificate.json')
hires['arithmetic']='mpmath.iv 75 decimal digits, overridden by independent audit; exact-decimal dual and 110-dps scalar bookkeeping'
(precision_root/'raw/interval_lower_certificate.json').write_text(json.dumps(hires,indent=2))
(HERE/'lower_75dps.json').write_text(json.dumps(hires,indent=2))
upper_mod=mod('audit_upper',HERE/'snapshot/core/interval_validate.py')
mp.mp.dps=110;mp.iv.dps=75
upper_mod.OUT=precision_root;upper_mod.FB=ROOT/'feedback_baseline'
# Rebuild module-level recovery matrix after precision override as well.
i=upper_mod.ii;cuts=upper_mod.CUTS
upper_mod.C=[[i(cuts[j+1]-cuts[j]) for j in range(3)],[-(upper_mod.ff(i(20-cuts[j]))-upper_mod.ff(i(20-cuts[j+1]))) for j in range(3)],[-(upper_mod.gg(i(20-cuts[j]))-upper_mod.gg(i(20-cuts[j+1]))) for j in range(3)]]
upper_mod.CI=upper_mod.inv3(upper_mod.C)
upper_mod.main()
for f in (precision_root/'raw').glob('interval_*.json'):
    data=read(f)
    def relabel(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if k=='arithmetic':x[k]='mpmath.iv 75 decimal digits after rebuilding recovery matrix, 110-dps scalar bookkeeping; independent audit precision override'
                else:relabel(v)
        elif isinstance(x,list):
            for v in x:relabel(v)
    relabel(data);f.write_text(json.dumps(data,indent=2))
for old,new in zip(read(ROOT/'raw/interval_summary.json'),read(precision_root/'raw/interval_summary.json')):
    for key in ['frequency_upper','power_upper','common_e0_upper','common_capacity_upper']:
        ck(old['policy']+'_'+key+'_50dps_conservative_vs75',mp.mpf(old[key])>=mp.mpf(new[key]),[old[key],new[key]])
lo40=mp.mpf(read(ROOT/'raw/interval_lower_certificate.json')['certified_energy_lower']);lo75=mp.mpf(hires['certified_energy_lower'])
ck('40dps_lower_conservative_against75dps',lo40<=lo75,dict(lower40=str(lo40),lower75=str(lo75),delta=str(lo75-lo40)))
# Primary array integrity and independent physical accounting of all 22 CSVs.
freeze=read(NET/'CONFIRMATION_FREEZE.json');summary=read(NET/'NONLINEAR_CONFIRMATION_SUMMARY.json')
ck('freeze_holdout_plan_hash',sha(NET/'HOLDOUT_PLAN.json')==freeze['holdout_plan_sha256'])
ck('freeze_qualified_model_hash',sha(BASE/'grid_transfer/kundur_reduced51.npz')==freeze['model_sha256'])
ck('freeze_controller_source_hash',sha(NET/'design_controller.py')==freeze['analysis_source_sha256'])
bylabel={r['label']:r for r in summary['rows']};physics=[]
for c in freeze['cases']:
    lab=c['label'];r=bylabel[lab]
    for stem in ['it','bess','observations']:
        ck(lab+'_'+stem+'_hash',sha(c[stem+'_csv'])==c[stem+'_sha256'])
    ck(lab+'_controller_hash',sha(NET/(c['controller']+'.npz'))==c['controller_sha256'])
    dat=np.load(NET/'nonlinear_replay'/(lab+'.npz'));t=dat['t'];idx=t>=1-1e-12
    peak=float(np.max(abs(dat['frequency_deviation_Hz'][idx])))
    ck(lab+'_raw_peak_agrees',abs(peak-r['peak_any_generator_Hz'])<1e-13)
    ck(lab+'_completed_bandpass',t[-1]==101 and peak<.1 and r['band_pass'])
    be=np.loadtxt(c['bess_csv'],delimiter=',',skiprows=1);h=np.diff(be[:,0]);p=be[:,1]
    ck(lab+'_positive_time_order',np.all(h>0))
    ck(lab+'_no_sign_crossing',np.all(p[1:]*p[:-1]>=0))
    area=.5*(p[:-1]+p[1:])*h
    debt=np.r_[0,np.cumsum(np.where(area>=0,area/.95,area*.95))]
    sl=np.diff(p)/h;v=np.r_[p[:-1]+.05*sl,p[1:]+.05*sl]
    E=float(np.max(debt)-np.min(debt));cmd=float(np.max(abs(v)));slew=float(np.max(abs(sl)))
    ck(lab+'_CSV_energy_agrees',abs(E-r['E_MWs'])<1e-8,[E,r['E_MWs']])
    ck(lab+'_CSV_terminal_tolerance',abs(debt[-1])<1e-8,float(debt[-1]))
    ck(lab+'_CSV_command_tolerance',cmd<=50+1e-8,cmd)
    ck(lab+'_CSV_slew',slew<500,slew)
    # Same initial SOC for every history in each family, across high and low classes.
    common=94.26493675271102 if c['controller'].startswith('binned93_feedback') else 127.13453434593208
    ck(lab+'_common_full_SOC',np.min(debt)>=-1e-8 and np.max(debt)<=common+1e-8)
    physics.append(dict(label=lab,CSV_energy=E,CSV_terminal_debt=float(debt[-1]),CSV_max_command=cmd,CSV_max_slew=slew,peak_Hz=peak))
ck('original22_complete',len(bylabel)==22 and summary['complete'] and summary['passed']==22 and summary['failed']==0)
nominal=[r for r in summary['rows'] if r['Pscale']==1 and r['ramp_s']==0 and not r['label'].endswith('_fine')]
ck('nominal16_and_feedback_only4_stresses',len(nominal)==16 and len([r for r in summary['rows'] if r['Pscale']!=1 or r['ramp_s']!=0])==4)
adds=read(NET/'AMPLITUDE_STRESS_ADDENDUM_RESULTS.json');peaks=[]
for a in adds:
    dat=np.load(NET/'nonlinear_replay'/(a['label']+'.npz'));peak=float(np.max(abs(dat['frequency_deviation_Hz'][dat['t']>=1-1e-12])))
    ck(a['label']+'_failed_peak_raw',abs(peak-a['window']['peak_abs_any_generator_Hz'])<1e-13 and peak>.1)
    peaks.append(peak)
ck('addendum_exceedance_dominates_step_error',peaks[1]-.1>100*abs(peaks[1]-peaks[0]),dict(fine_exceedance_Hz=peaks[1]-.1,step_difference_Hz=abs(peaks[1]-peaks[0])))
lock=read(NET/'EXECUTION_ENVIRONMENT_LOCK.json')
for p,h in lock['old_files'].items():ck('locked_source_'+p,sha(p)==h)
# Stable-modal prerequisite independently evaluated from original state matrix.
grid=np.load(BASE/'grid_transfer/kundur_reduced51.npz');A=grid['A'];l,V=np.linalg.eig(A)
ck('network_strict_Hurwitz',np.max(l.real)<0,float(np.max(l.real)))
ck('network_nonzero_modal_poles',np.min(abs(l))>.1,float(np.min(abs(l))))
network_numerics=dict(max_real_eigenvalue=float(np.max(l.real)),eigenvector_condition=float(np.linalg.cond(V)),diagonalization_residual=float(np.max(abs(A@V-V*l))))
result=dict(checks=len(checks),failed=sum(not c['passed'] for c in checks),scope='Read-only source review, audit-copy interval reruns, independent retained-array/CSV/hash reconstruction. No nonlinear simulation rerun or formal proof assistant.',network_numerics=network_numerics,physical_reconstruction=physics,checks_detail=checks)
(HERE/'INDEPENDENT_CHECKS.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['physical_reconstruction','checks_detail']},indent=2))
