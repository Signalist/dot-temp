"""Original result audits; no nonlinear runs or prior-source modifications."""
from pathlib import Path
import json,hashlib,csv
import numpy as np
P=Path(__file__).resolve().parent;C=json.loads((P/'NONLINEAR_FREEZE.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,o):Path(p).write_text(json.dumps(o,indent=2,allow_nan=False))
checks=[];rows=[];curve=[]
for c in C['cases']:
 stem=c['network']+'_'+c['label'];a=np.load(P/(stem+'_input.npz'));full=a['full_word_current_to_oldest'];trim=a['trim_word_current_to_oldest'];sc=a['actual_schedule'];amp=c['total_amplitude_MW'];q=a['q'];chron=trim[::-1];waves=sc[1:-1][:,[1,3]].reshape(-1,4,2)
 inputs={'name':stem,'word_tail_exact':bool(np.array_equal(trim,full[:65])),'template_input_max_error_MW':float(abs(waves-amp*chron[:,None,:]*q[None,:,:]).max()),'block_incremental_energy_max_error_MJ':float(abs(.5*waves.sum(axis=1)).max()),'zero_Q':bool(np.all(sc[:,[2,4]]==0)),'common_sign_each_block':bool(np.all(chron[:,0]*chron[:,1]>=0)),'amplitude_bound':bool(np.all(abs(chron)<=.5)),'sign_amplitude_preserved_every_block':bool(np.all(waves==amp*chron[:,None,:]*q[None,:,:])),'actual_schedule_hash_matches_freeze':hashlib.sha256(sc.astype(np.float64).tobytes()).hexdigest()==c['actual_schedule_sha256']}
 checks.append(inputs)
 for div in [64,128]:
  jp=P/f'{stem}_dt{div}.json'
  if not jp.exists():continue
  r=json.loads(jp.read_text());m=r['metrics'];rows.append({'network':c['network'],'case':c['label'],'dt_s':r['dt_s'],'complete':r['complete'],'amplitude_MW':amp,'LTI_peak_Hz':m['exact_LTI_peak_any_generator_Hz'],'nonlinear_peak_Hz':m['nonlinear_peak_any_generator_Hz'],'LTI_margin_Hz':m['LTI_frequency_margin_Hz'],'nonlinear_margin_Hz':m['nonlinear_frequency_margin_Hz'],'max_trace_error_Hz':m['max_linear_nonlinear_error_Hz'],'target_error_Hz':m['nonlinear_target_Hz']-m['exact_LTI_target_Hz'],'min_native_plus_probe_MW':min(z['total_native_plus_probe_min_MW'] for z in r['physical_ledger']),'LTI_trim_target_error_Hz':m['full_vs_trimmed_LTI_target_error_Hz'],'LTI_trim_bound_Hz':c['LTI_trim_vs_full_tail_upper_Hz'],'original_workpoint_initial_difference':r['initial_state_max_difference']})
 jp=P/f'{stem}_dt128.json'
 if jp.exists():
  r0=json.loads((P/f'{stem}_dt64.json').read_text());r1=json.loads(jp.read_text());f=np.load(P/f'{stem}_dt128.npz');g=np.load(P/f'{stem}_dt64.npz');interp=np.stack([np.interp(f['t'],g['t'],g['frequency_Hz'][:,j]) for j in range(f['frequency_Hz'].shape[1])],axis=1);curve.append({'name':stem,'peak_refinement_difference_Hz':abs(r1['metrics']['nonlinear_peak_any_generator_Hz']-r0['metrics']['nonlinear_peak_any_generator_Hz']),'target_refinement_difference_Hz':abs(r1['metrics']['nonlinear_target_Hz']-r0['metrics']['nonlinear_target_Hz']),'max_fine_vs_interpolated_coarse_error_Hz':float(abs(f['frequency_Hz']-interp).max()),'frequency_threshold_decision_unchanged':(r1['metrics']['nonlinear_peak_any_generator_Hz']<=.05)==(r0['metrics']['nonlinear_peak_any_generator_Hz']<=.05),'same_actual_schedule_both_steps':bool(np.array_equal(f['actual_schedule'],g['actual_schedule']))})
initial=[]
for n in C['networks']:
 a=np.load(P.parent.parent/'round2_20261003/grid_transfer'/f'{n}_descriptor_aux.npz');b=np.load(P/f'{n}_initial_state.npz');initial.append({'network':n,'original_qualified_x0_max_difference':float(abs(a['x0']-b['x0']).max()),'original_qualified_y0_max_difference':float(abs(a['y0']-b['y0']).max())})
output={'complete':len(rows)==20 and all(r['complete'] for r in rows),'expected_replays':20,'completed_replays':len(rows),'original_workpoint_checks':initial,'input_checks':checks,'refinement':curve,'source_integrity_all_unchanged':all(sha(p)==v for p,v in C['source_hashes'].items()),'results':rows,'claim_scope':'Finite original nonlinear signed-injection stress checks. Supplemental P0=0 at both ports on both networks, so no physical positive compute port or calibrated work contract. Native loads retain original impedance conversion; their nonnegativity is separate. No nonlinear whole-family, infinite-time, full-versus-trimmed history, or interval-certified claim.'}
output['execution_and_input_audit_pass']=bool(output['complete'] and output['source_integrity_all_unchanged'] and all(x['original_qualified_x0_max_difference']==0 and x['original_qualified_y0_max_difference']==0 for x in initial) and all(x['word_tail_exact'] and x['template_input_max_error_MW']<1e-12 and x['block_incremental_energy_max_error_MJ']<1e-12 and x['zero_Q'] and x['common_sign_each_block'] and x['amplitude_bound'] and x['sign_amplitude_preserved_every_block'] and x['actual_schedule_hash_matches_freeze'] for x in checks) and all(x['same_actual_schedule_both_steps'] for x in curve) and all(x['LTI_trim_target_error_Hz']<=x['LTI_trim_bound_Hz']+1e-12 for x in rows))
output['refined_inner_nonlinear_transfer_failures']=[{'network':r['network'],'case':r['case'],'LTI_peak_Hz':r['LTI_peak_Hz'],'nonlinear_peak_Hz':r['nonlinear_peak_Hz']} for r in rows if r['dt_s']==1/128 and r['case'] in ['committed_inner','dynamic_optional_inner'] and r['nonlinear_peak_Hz']>.05]
output['all_refined_inner_witnesses_stay_inside_nonlinear_threshold']=bool(output['complete'] and not output['refined_inner_nonlinear_transfer_failures'])
dump(P/'NONLINEAR_AUDIT.json',output)
if rows:
 with (P/'NONLINEAR_RESULTS.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps({'complete':output['complete'],'completed':len(rows),'refinements':curve,'results':rows},indent=2))
