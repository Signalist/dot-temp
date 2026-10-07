"""Read-only diagnosis of the frozen recovery criterion, never a rescoring rule."""
from pathlib import Path
import json,hashlib,numpy as np
R=Path(__file__).resolve().parent;O=R/'results';rows=[]
for cid in ['P0-fast','R0-fast','P50-fast','R50-fast']:
 p=O/f'{cid}_h1e-05.json';d=json.loads(p.read_text());z=np.load(O/d['trace_file']);iv=z['interval_extrema'];ct=z['control'];end=2.75
 w=iv[(iv[:,1]>end-.15+1e-11)&(iv[:,1]<=end+1e-11)];c=ct[(ct[:,0]>=end-.15-1e-11)&(ct[:,0]<end-1e-11)]
 row={'case':cid,'window_start_s':2.6,'window_end_s':2.75,'full_intervals':len(w),'flags_order':['current_ref_clip','voltage_clip','source_cmd_clip','PLL_clip','guard_intervened'],'active_interval_counts':w[:,12:17].sum(axis=0).astype(int).tolist(),'guard_modification_norm_min':float(c[:,-1].min()),'guard_modification_norm_max':float(c[:,-1].max()),'frozen_unclipped_condition_in_this_window':bool(not np.any(w[:,12:17]>.5)),'physical_complete_hard_safe':d['complete_hard_safe'],'source_summary_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_npz_sha256':d['trace_sha256']}
 if d['event']:
  row['official_recovery_unchanged']=d['recovery']['joint_recovery_time_s'];row['official_checks_count']=len(d['recovery']['checks']);row['official_checks_with_unclipped_true']=sum(x['unclipped_including_guard_150ms'] for x in d['recovery']['checks']);row['official_last_check']=d['recovery']['checks'][-1]
 rows.append(row)
out={'status':'READ_ONLY_CRITERION_COMPATIBILITY_DIAGNOSIS_NOT_RESCORING','rows':rows,'conclusion':'Both observed healthy reference trajectories themselves have persistent common-guard intervention in the final150ms. Exact return to those recorded targets cannot satisfy the frozen all-limiters-off condition in that window. Physical/reference-trajectory recovery and exit of the baseline guard are different predicates.','scope':'Observed fixed N/K/Omega/terminal implementation only; not a proof of unavoidable intervention for all future time, all guards or all safe control.','official_scores_changed':False,'new_trajectories':0,'new_optimizer_calls':0,'inventory_rebalanced_claim':False}
(R/'RECOVERY_CRITERION_COMPATIBILITY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
