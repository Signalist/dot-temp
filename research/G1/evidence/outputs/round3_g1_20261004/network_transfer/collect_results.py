from design_controller import *
from datetime import datetime,timezone
import csv

def exact_trace(times,it,be):
 z=np.zeros(len(lam),complex);ys=[np.zeros(4)];cache={}
 for a,b in zip(times[:-1],times[1:]):
  h=b-a
  if h<1e-11:ys.append((CV@z).real);continue
  mid=(a+b)/2;ii=np.searchsorted(it[:,0],mid,side='right')-1;bi=np.searchsorted(be[:,0],mid,side='right')-1
  if bi==len(be)-1:pp=be[-1,1];slope=0.
  else:slope=(be[bi+1,1]-be[bi,1])/(be[bi+1,0]-be[bi,0]);pp=be[bi,1]+slope*(a-be[bi,0])
  q=it[ii,1]-pp;r=-slope
  key=round(h,11)
  if key not in cache:
   ex=np.exp(lam*h);em=np.expm1(lam*h);cache[key]=(ex,em/lam,(em-lam*h)/lam**2)
  ex,S,R=cache[key];z=ex*z+bm*(q*S+r*R);ys.append((CV@z).real)
 return np.array(ys)

manifest=json.loads((OUT/'CONFIRMATION_FREEZE.json').read_text());rows=[];missing=[]
for c in manifest['cases']:
 path=OUT/'nonlinear_replay'/(c['label']+'.json')
 if not path.exists():missing.append(c['label']);continue
 r=json.loads(path.read_text());d=np.load(path.with_suffix('.npz'));t=d['t'];f=d['frequency_deviation_Hz'];it=np.genfromtxt(c['it_csv'],delimiter=',',skip_header=1);be=np.genfromtxt(c['bess_csv'],delimiter=',',skip_header=1)
 y=exact_trace(t,it,be);linpeak=float(np.max(abs(y)));diff=float(np.max(abs(y-f)));s=c['physics'];peak=r['window']['peak_abs_any_generator_Hz']
 row={'label':c['label'],'controller':c['controller'],'initial_high':c['initial_high'],'r_s':c['r_s'],'Pscale':c['Pscale'],'ramp_s':c['ramp_s'],'dt_s':c['dt_s'],'tds_return':r['tds_return'],'end_time_s':r['end_time'],'peak_any_generator_Hz':peak,'band_pass':peak<=.1 and r['tds_return'] and abs(r['end_time']-c['tf_s'])<1e-8,'peak_COI_Hz':r['window']['peak_abs_COI_Hz'],'J100_Hz2s':r['window']['frequency_weighted_squared_integral_Hz2s'],'min_voltage_pu':r['window']['min_bus_voltage_pu'],'max_voltage_pu':r['window']['max_bus_voltage_pu'],'same_input_linear_sample_peak_Hz':linpeak,'same_input_trace_discrepancy_Hz':diff,**s}
 rows.append(row)
 if not path.with_name(path.stem+'_linear.npz').exists():np.savez_compressed(path.with_name(path.stem+'_linear.npz'),t=t,frequency_deviation_Hz=y,it_csv_sha256=c['it_sha256'],bess_csv_sha256=c['bess_sha256'])
if rows:
 with (OUT/'NONLINEAR_CONFIRMATION_SUMMARY.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={'collected_utc':datetime.now(timezone.utc).isoformat(),'complete':not missing,'planned':len(manifest['cases']),'completed':len(rows),'missing':missing,'passed':sum(r['band_pass'] for r in rows),'failed':sum(not r['band_pass'] for r in rows),'rows':rows}
serialized_audit=OUT/'SERIALIZED_INPUT_NUMERICAL_AUDIT.json'
if serialized_audit.exists():
 sa=json.loads(serialized_audit.read_text())
 summary['physical_metric_precision_scope']={'original_row_physical_metrics':'computed from model arrays; preserved unchanged','actual_replay_inputs':'12-significant-digit CSV serialization','serialized_input_audit':serialized_audit.name,'max_serialized_command_MW':sa['max_serialized_command_MW'],'max_abs_serialized_terminal_depletion_MWs':sa['max_abs_serialized_terminal_depletion_MWs'],'command_numerical_tolerance_MW':sa['command_numerical_tolerance_MW'],'terminal_recovery_numerical_tolerance_MWs':sa['terminal_recovery_numerical_tolerance_MWs']}
(OUT/'NONLINEAR_CONFIRMATION_SUMMARY.json').write_text(json.dumps(summary,indent=2))
print({k:v for k,v in summary.items() if k!='rows'},flush=True)
lock=json.loads((OUT/'EXECUTION_ENVIRONMENT_LOCK.json').read_text());changed=[]
for p,h in lock['old_files'].items():
 if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h:changed.append(p)
check={'verified_utc':datetime.now(timezone.utc).isoformat(),'n_locked_round2_files':len(lock['old_files']),'all_unchanged':not changed,'changed':changed,'complete_confirmation':not missing}
grid=OUT.parents[1]/'round2_20261003/grid_transfer';old_paths=set(lock['old_files']);current_cache=[q for loc in [grid/'home',grid/'__pycache__'] for q in loc.rglob('*') if q.is_file()]
# The before-lock paths are workspace-relative; normalize both for inventory checks.
old_resolved={str(Path(q).resolve()) for q in old_paths}
check['new_files_in_round2_cache_locations']=[str(q) for q in current_cache if str(q.resolve()) not in old_resolved]
check['all_round2_cache_paths_unchanged']=not check['new_files_in_round2_cache_locations'] and check['all_unchanged']
(OUT/'ROUND2_INTEGRITY_CHECK.json').write_text(json.dumps(check,indent=2));print(check,flush=True)
