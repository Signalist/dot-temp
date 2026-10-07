"""Original independent audit of reinitialized positive-load data.
No candidate-code import. May be rerun after nonlinear outputs finish.
"""
from pathlib import Path
import os,json,hashlib
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent/'positive_workpoint'
def ash(a):return hashlib.sha256(np.asarray(a,dtype=np.float64).tobytes()).hexdigest()
qual=json.loads((ROOT/'QUALIFICATION.json').read_text())
initial=json.loads((ROOT/'QUALIFICATION_initial_sink_probe.json').read_text())
assert qual['qualification_pass'] and not initial['qualification_pass']
K=sparse.load_npz(ROOT/'positive_descriptor_K.npz');d=np.load(ROOT/'positive_descriptor_aux.npz')
kernel=np.load(ROOT/'positive_kernel.npz');n=len(d['x_names']);sink=len(d['mass'])-1
row=K.getrow(sink).toarray()[0];col=K.getcol(sink).toarray()[:,0]
assert np.count_nonzero(row)==np.count_nonzero(col)==1 and row[sink]==col[sink]==1
assert not np.any(d['G'][sink]) and d['y_names'][sink-n]==''
z=np.random.default_rng(2601003).normal(size=len(row));z/=np.linalg.norm(z)
initial_error=max(v['max_abs_error'] for v in initial['central_difference_checks'])
assert abs(initial_error-abs(z[sink]))<1e-14
res={'scope':'Independent floating positive-workpoint audit; no uniform nonlinear certificate',
     'sink_correction':{'index':sink,'isolated_diagonal':1,'input_row_zero':True,
       'original_direction_sink_value':float(z[sink]),'original_derivative_error':initial_error,
       'corrected_max_relative_derivative_error':max(v['relative_L2_error'] for v in qual['central_difference_checks'])}}
oi=np.array([i for i,s in enumerate(d['x_names']) if s.startswith('omega GENROU')])
resolv=[]
for s in [.004j,.023+.031j,.27+1.13j,7+23j]:
    direct=60*splu((s*sparse.diags(d['mass'])-K).astype(complex).tocsc()).solve(d['G'][:,[0,2]].astype(complex))[oi]
    modal=np.sum(kernel['R']/(s-kernel['lam'])[None,:,None],axis=1)
    rel=float(np.linalg.norm(direct-modal)/np.linalg.norm(direct));assert rel<1e-8
    resolv.append({'s':[s.real,s.imag],'relative_error':rel,'absolute_error':float(abs(direct-modal).max())})
res['new_descriptor_resolvents']=resolv
assert qual['metadata']['baseline_port_MW']==[50,50]
assert qual['positive_compute_workpoint']['ZIP']['pp0']==[.5,.5]
assert qual['changed_model_check']['A_sha256']!=qual['changed_model_check']['old_A_sha256']
res['baseline_MW']=[50,50]
res['slack_generator_P_change_MW']=100*(qual['positive_compute_workpoint']['GENROU']['p0'][0]-qual['old_zero_compute_workpoint']['GENROU']['p0'][0])
# Independently reconstruct equal-ray full-grid maxima.
W=np.load(ROOT/'positive_coefficients.npy',mmap_mode='r');saved=np.load(ROOT/'positive_support_arrays.npz')
mx={'committed':0.,'dynamic_optional':0.,'independent_ports':0.}
for start in range(0,W.shape[1],128):
    p=W[:,start:start+128,0,:]/2;q=W[:,start:start+128,1,:]/2
    vals={'committed':abs(p+q).sum(axis=-1),
          'dynamic_optional':np.maximum.reduce([abs(p),abs(q),abs(p+q)]).sum(axis=-1),
          'independent_ports':(abs(p)+abs(q)).sum(axis=-1)}
    for key,val in vals.items():mx[key]=max(mx[key],float(val.max()))
for key,value in mx.items():assert abs(value-saved[key+'_peak'][20])<2e-16
res['independent_equal_ray_peaks']=mx
cases=json.loads((ROOT/'POSITIVE_NONLINEAR_CASES.json').read_text())
res['frozen_support_source_integrity']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected
                                      for name,expected in cases['support_inputs_hashes'].items()}
assert all(res['frozen_support_source_integrity'].values())
physical=[]
for case in cases['cases']:
    label=case['label'];data=np.load(ROOT/(label+'_input.npz'))
    word=data['word_current_to_oldest'];schedule=data['schedule'];amp=case['total_amplitude_MW']
    assert len(word)==257 and ash(word)==case['word_sha256'] and ash(schedule)==case['schedule_sha256']
    assert schedule[0,0]==0 and schedule[1,0]==1 and schedule[-1,0]==515
    # Full piecewise-constant energy by explicit interval lengths, rather than
    # by the generation code's symbolic zero-sum assertion.
    block_rows=schedule[1:-1,[1,3]].reshape(257,4,2)
    dt=np.diff(schedule[1:,0]).reshape(257,4)
    assert np.all(dt==.5)
    incremental=np.sum(block_rows*dt[:,:,None],axis=1)
    baseline_energy=np.sum((50+block_rows)*dt[:,:,None],axis=1)
    assert abs(incremental).max()<1e-12 and abs(baseline_energy-100).max()<1e-12
    assert np.min(50+block_rows)>=0
    # The first chronological block must match the oldest retained word.
    Q=np.array([[1,1],[1,-1],[-1,-1],[-1,1]])
    assert np.max(abs(block_rows-amp*word[::-1,None,:]*Q[None,:,:]))<1e-12
    physical.append({'case':label,'full_blocks':257,'minimum_compute_MW':float(np.min(50+block_rows)),
                     'max_incremental_block_energy_MWs':float(abs(incremental).max()),
                     'max_block_energy_difference_from_100_MWs':float(abs(baseline_energy-100).max()),
                     'chronology_verified':True,'physical_cap_applied':case['physical_cap_applied']})
res['physical_schedule_checks']=physical
# Independently check completed nonlinear output ledgers, without pretending
# that still-pending cases or intersample points have been checked.
nl=[];initial_states=set()
for file in sorted(ROOT.glob('*_dt*.json')):
    r=json.loads(file.read_text());raw=np.load(file.with_suffix('.npz'))
    if not r.get('complete'):continue
    initial_states.add((r['initial_x_sha256'],r['initial_y_sha256']))
    peak=float(abs(raw['frequency_Hz']).max());minimum=float(raw['total_compute_MW'].min())
    assert abs(peak-r['metrics']['nonlinear_peak_Hz'])<1e-13 and minimum>=0
    assert abs(raw['t'][-1]-535)<1e-10
    nl.append({'case':r['label'],'peak_Hz':peak,'margin_Hz':.05-peak,
               'minimum_compute_MW':minimum,'completed':True})
res['completed_nonlinear_raw_checks']=nl
assert len(initial_states)<=1
res['all_completed_runs_share_initial_state']=len(initial_states)==1
res['nonlinear_review_complete']=len(nl)==10
res['all_current_checks_passed']=True
(OUT/'INDEPENDENT_POSITIVE_RESULTS.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({'all_current_checks_passed':True,'new_resolvent_max_relative':max(x['relative_error'] for x in resolv),
                  'physical_schedules_checked':len(physical),'completed_nonlinear_cases_checked':len(nl),
                  'nonlinear_review_complete':res['nonlinear_review_complete']},indent=2))
