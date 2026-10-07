"""Pure synthetic-array checks of the independent recovery audit. No trajectory."""
from pathlib import Path
import copy,hashlib,json,sys
sys.dont_write_bytecode=True
import numpy as np
from unittest.mock import patch
import audit_artifact_checks as audit
rm=audit.rm
_,_,case,d,_,_=rm.load_design('P50-fast')
times=np.arange(6000,14001,dtype=float)*1e-4
states=np.zeros((len(times),len(rm.NORMALIZED_NAMES)));states[:,0]=times
intervals=np.zeros((len(times)-1,len(rm.INTERVAL_COLS)))
intervals[:,0]=times[:-1];intervals[:,1]=times[1:]
intervals[:,2]=.8;intervals[:,3:5]=1.;intervals[:,5]=1e6
intervals[:,6]=8e5;intervals[:,7]=8e5;intervals[:,8:10]=.5;intervals[:,17]=.4
results=[]
with patch.object(rm,'run',audit.forbidden),patch.object(rm,'rhs',audit.forbidden),patch.object(rm,'solve_ivp',audit.forbidden),patch.object(audit.cg,'minimize',audit.forbidden):
    for name in ['all_pass','guard_active','reference_current_clip','voltage_clip','source_clip','PLL_clip','hard_current','self_cycle','matched_target','PLL_frequency','earlier_violation']:
        s=states.copy();r=states.copy();iv=intervals.copy();global_safe=name!='earlier_violation'
        if name=='guard_active':iv[:,16]=1.
        if name=='reference_current_clip':iv[:,12]=1.
        if name=='voltage_clip':iv[:,13]=1.
        if name=='source_clip':iv[:,14]=1.
        if name=='PLL_clip':iv[:,15]=1.
        if name=='hard_current':iv[:,2]=1.01
        if name=='self_cycle':s[:,1]=np.arange(len(s))*1e-6;r=s.copy()
        if name=='matched_target':r[:,2]=1e-4
        if name=='PLL_frequency':iv[:,10]=.002
        stored=rm.recovery_score(case,True,global_safe,s,iv,r,d)
        summary={'event':case['event'],'simulation_completed':True,'no_physical_hard_contact_up_to_stop':global_safe,'recovery':stored}
        out=audit.independent_recovery(summary,s,iv,r,d)
        if name in ['all_pass','earlier_violation']:
            assert abs(out['joint_recovery_time_s']-1.05)<1e-12
            assert out['global_safe_recovery']==(name=='all_pass')
        else:assert out['joint_recovery_time_s'] is None and not out['global_safe_recovery']
        if name=='guard_active':assert out['failed_subitem_counts']['unclipped_including_guard']==out['checks_recomputed']
        results.append({'fixture':name,'status':'PASS','joint_recovery_time_s':out['joint_recovery_time_s'],'global_safe_recovery':out['global_safe_recovery'],'failed_subitem_counts':out['failed_subitem_counts']})
path=Path(__file__)
out={'status':'PASS_SYNTHETIC_RECOVERY_ORACLE_SELFTEST','physical_trajectories_executed':0,'real_optimization_calls':0,'fixture_count':len(results),'results':results,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'artifact_checker_sha256':hashlib.sha256((path.parent/'audit_artifact_checks.py').read_bytes()).hexdigest(),'qualification':'Isolated synthetic arrays; no plant or optimization calls. Frozen guard-limiting and recovery criteria remain unchanged.'}
(path.parent/'audit_recovery_fixture_results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
