"""Independent reference-definition audit, no original source or data changed."""
import csv, hashlib, json
from pathlib import Path
import numpy as np
from scipy.integrate import quad
ROOT=Path(__file__).resolve().parents[2]
V2=ROOT/'recovery_phase2'/'V2'
a=np.genfromtxt(V2/'original_input.csv',delimiter=',',names=True)
t=a['t']; d=a['d']; h=np.diff(t)
cum=np.r_[0,np.cumsum(h*((d[:-1]+d[1:])/2-650000))]
m=t<=.2+1e-12
rows=list(csv.DictReader(open(V2/'ENERGY_COST_TABLE_V2.csv')))
source=(V2/'recovery.cpp').read_text()
command_line=[(i+1,x) for i,x in enumerate(source.splitlines()) if x.startswith('std::array<double,6> command')][0]
c=.005/(1.5*563.3826408401309**2)
def f(x):
    demand=np.interp(x,t,d)
    return 2*demand/(1+np.sqrt(1-4*c*demand))-654498.72485653043
ideal,err=quad(f,0,.2,points=[.005,.035,.04,.07,.075,.105,.11],epsabs=1e-7)
result={
 'scope':'Static original-reference audit plus independent ideal comparator prediction, before new PWM result; not a pass threshold or fit.',
 'original_source_sha256':hashlib.sha256((V2/'recovery.cpp').read_bytes()).hexdigest(),
 'command_source_line':command_line[0], 'command_source':command_line[1],
 'S_compute_W_minmax':[float(d.min()),float(d.max())],
 'F_compute_W':650000,
 'same_time_resolved_compute_input':False,
 'S_service_compute_energy_J':float(np.trapezoid(d[m],t[m])),
 'F_service_compute_energy_J':130000.,
 'S_F_max_cumulative_compute_energy_difference_J':float(max(abs(cum))),
 'service_duration_s':.2,
 'both_compute_energy_through_.9s_J':585000.,
 'post_service_compute_input_identical':True,
 'matched_original_source_definition':{'S':'Frozen P/Q/d/u schedule during service; constant baseline after service','F':'Pbase,Q0,d650kW,uFeed0 throughout, with same service-clock outer-loop gates'},
 'input_file_end_s':float(t[-1]),
 'input_file_full_energy_J':float(np.trapezoid(d,t)),
 'ledger_paired_load_energy_residuals_J':{
 w: {'min':min(float(z['incremental_load_J']) for z in rows if z['window']==w),'max':max(float(z['incremental_load_J']) for z in rows if z['window']==w)}
 for w in ['service_cost','recovery_cost','checkpoint_total_cost']},
 'new_L_ideal_shape_increment_vs_F_J':ideal,
 'quad_absolute_error_estimate_J':err,
 'interpretation':'Old recovery-window input is identical but entry states differ due to prehistory. Its energy costs remain valid baseline-orbit recovery costs. Whole-event S-F does not isolate grid-service incremental cost conditional on the same time-resolved compute input. New S-L does, relative to a declared loss-corrected load-following no-service comparator; it is not the globally optimal no-service policy.',
 'hardware_task_caveat':'These are prescribed electrical-demand contracts and energy equality, not measured FLOP/job equivalence.'
}
OUT=Path(__file__).resolve().parent/'ORIGINAL_REFERENCE_DEFINITION.json'
OUT.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
