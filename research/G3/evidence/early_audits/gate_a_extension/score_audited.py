"""Authoritative report-only scoring. Preserve the original trajectory and JSON.
Clarifies hard-contact termination, checks every held modulation norm, and
labels electrical-state restoration separately from battery inventory.
"""
from pathlib import Path
import json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'gate_a_extension/results';P=json.loads((ROOT/'protocol/GATE_A_EXTENSION_V1.json').read_text());D=json.loads((ROOT/'protocol/GATE_A_LOCKED_V2_1.json').read_text())
rows=[]
for path in sorted(OUT.glob('*_h*.json')):
 if path.name.endswith(('_checkpoint.json','_final_state.json','.audited.json')):continue
 s=json.loads(path.read_text())
 if 'case' not in s or 'max_step_s' not in s:continue
 z=np.load(path.with_suffix('.npz'));ct=z['control'];st=z['full_normalized_state'];a=z['endpoint_trace'];m=dict(s['metrics'])
 # Include the initial checkpoint's pre-promotion left limit, not only post-update intervals.
 left=a[0]
 m['max_actual_current_pu']=max(m['max_actual_current_pu'],float(left[12]));m['min_dc_pu']=min(m['min_dc_pu'],float(left[13]));m['max_dc_pu']=max(m['max_dc_pu'],float(left[13]))
 m['max_pcc_S_VA']=max(m['max_pcc_S_VA'],float(np.hypot(left[14],left[15])));m['max_abs_Ppcc_W']=max(m['max_abs_Ppcc_W'],float(abs(left[14])));m['max_abs_Pb_W']=max(m['max_abs_Pb_W'],float(abs(left[4])))
 m['min_soc']=min(m['min_soc'],float(left[21]));m['max_soc']=max(m['max_soc'],float(left[21]));m['max_frequency_error_Hz']=max(m['max_frequency_error_Hz'],float(abs(left[23]-60)))
 initial=s['initial_record']
 if 'checkpoint_file' in initial:
  cp=json.loads((ROOT/initial['checkpoint_file']).read_text());init_mod=max(abs(complex(*cp['controller'][k])) for k in ['applied','queued'])
 else:init_mod=abs(complex(*initial['u_inv0']))/D['V_dc_initial_V']
 mod=float(max(init_mod,max(ct[:,7]),max(np.hypot(st[:,9],st[:,10])),max(np.hypot(st[:,11],st[:,12]))))
 limit=D['svpwm_linear_voltage_derating']/np.sqrt(3);modsafe=mod<=limit*(1+1e-8)
 normalised_margins=dict(current=1-m['max_actual_current_pu'],dc_lower=m['min_dc_pu']-.8,dc_upper=1.1-m['max_dc_pu'],apparent_power=1-m['max_pcc_S_VA']/1.2e6,active_power=1-m['max_abs_Ppcc_W']/950000,battery_terminal_power=1-m['max_abs_Pb_W']/1e6,soc_lower=m['min_soc']-.2,soc_upper=.8-m['max_soc'],modulation=1-mod/limit)
 contact={}
 for name in ['actual_current_emergency','dc_low','dc_high','soc_low','soc_high']:
  if s['stop_reason']==name:contact[name]=s['final_time_s']
 if s['current_limit_crossings_s']:contact['actual_current_continuous']=s['current_limit_crossings_s'][0]
 release={}
 for j,key in enumerate(['current_reference','voltage_modulation','battery_command','pll_frequency']):
  active=np.flatnonzero(ct[:,11+j]>.5)
  if len(active)==0:release[key]=dict(status='never_active',release_sample_s=None,after_clearance_s=None)
  elif active[-1]+1>=len(ct):release[key]=dict(status='no_observed_exit_before_stop',release_sample_s=None,after_clearance_s=None,last_active_sample_s=float(ct[active[-1],0]))
  else:
   tt=float(ct[active[-1]+1,0]);release[key]=dict(status='observed_exit_and_no_later_reactivation',release_sample_s=tt,last_active_sample_s=float(ct[active[-1],0]),after_clearance_s=tt-s['event_clearance_s'] if s['event_clearance_s'] is not None else None)
 target_only=None;count=0
 if s['case'].startswith('sag'):
  for cc in s['checks']:
   okay=(cc['target_difference'] is not None and cc['target_difference']<=1e-5 and cc['safe_window'] and cc['limiters_released'] and cc['metrics']['max_frequency_error_Hz']<=.001 and cc['time_s']>=s['event_clearance_s']+.15-1e-12)
   count=count+1 if okay else 0
   if count>=3:target_only=cc['time_s'];break
 completed=s['stop_reason']=='completed';safe=bool(s['all_hard_limits_safe'] and modsafe and min(normalised_margins.values())>=-1e-8 and min(ct[:,3])>=45-1e-8 and max(ct[:,3])<=75+1e-8)
 audited=dict(case=s['case'],max_step_s=s['max_step_s'],raw_summary_file=path.name,raw_summary_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),raw_trace_sha256=hashlib.sha256(path.with_suffix('.npz').read_bytes()).hexdigest(),raw_summary_unchanged=True,score_version='reporting_audit_v1',stop_reason=s['stop_reason'],simulation_completed=completed,no_hard_violation_observed_up_to_stop_with_roundoff=safe,hard_limit_contacts=contact,first_observed_strict_beyond_roundoff=s['first_observed_hard_violation_s'],contact_interpretation='A terminal boundary contact ends the test even if the sampled state is still on the admissible equality. No-violation-up-to-stop does not mean complete safe recovery.',all_held_and_new_modulation_max_norm=mod,modulation_norm_limit=limit,modulation_safe=bool(modsafe),normalised_hard_margins=normalised_margins,electrical_control_recovery_joint_rule_time_s=s['recovered_time_s'],electrical_control_target_only_recovery_time_s=target_only,recovery_rule_clarification='Official conservative common score requires both 50ms self-cycle convergence and return to pre-fault target for sag, each<=1e-5, plus three qualifying checks and a safe/unclipped150ms window. Target-only time is separately shown; no dynamics or threshold was changed.',complete_safe_electrical_control_recovery=bool(completed and safe),battery_energy_restoration_claimed=False,battery_note='Actual stored battery energy, passive integrals, and SoC are retained and bounded, but excluded from electrical orbit recurrence. Constant positive P keeps depleting inventory. See paired no-fault energy accounting for disturbance debt/surplus.',limiter_release=release,metrics=m,terminal_battery_energy_change_since_test_start_J=float(a[-1,5]-a[0,5]),test_end_s=s['final_time_s'],periodic_frozen_bias_W=s.get('frozen_bias_W'),periodic_cycles=s.get('cycles',[]))
 path.with_name(path.stem+'.audited.json').write_text(json.dumps(audited,indent=2)+'\n');rows.append(audited)
report={'score_version':'reporting_audit_v1','protocol_sha256':hashlib.sha256((ROOT/'protocol/GATE_A_EXTENSION_V1.json').read_bytes()).hexdigest(),'diagnostic_condition_budget':12,'paired_no_fault_reference_not_a_new_disturbance_condition':True,'results':rows}
(OUT/'AUDITED_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps([{'case':x['case'],'h':x['max_step_s'],'completed':x['simulation_completed'],'safe_electrical_recovery':x['complete_safe_electrical_control_recovery'],'hard_contacts':x['hard_limit_contacts'],'recovery_s':x['electrical_control_recovery_joint_rule_time_s']} for x in rows],indent=2))
