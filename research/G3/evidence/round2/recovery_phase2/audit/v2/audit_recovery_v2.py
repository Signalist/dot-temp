"""Independent read-only audit of frozen recovery outputs. Writes only audit/."""
from pathlib import Path
import hashlib,json,datetime,itertools
import numpy as np
A=Path(__file__).resolve().parent
R=A.parent.parent/'V2'
FIELDS=['ia','ib','ic','W','B','b','jd','jq','zw','cp','held','ub','frozen','da','db','dc']
def arr(tag,suffix=''):
    return dict(np.load(R/(tag+suffix+'.npz')))
def scalar(x):return float(x)
def mx(x):return float(np.max(np.abs(x)))
def record_at(z,t):
    i=np.argmin(abs(z['t']-t));assert abs(z['t'][i]-t)<1e-10,(t,z['t'])
    return {k:float(v[i]) for k,v in z.items()}
def periodic(z,end):
    # Sampled absolute time, shift one actual 50 Hz grid cycle.
    ii=np.where((z['t']>=end-.1-1e-10)&(z['t']<=end+1e-10))[0]
    vals={k:[] for k in ['W','B','ia','ib','ic']}
    for i in ii:
        j=np.searchsorted(z['t'],z['t'][i]-.02-1e-10)
        if j>=len(z['t']) or abs(z['t'][j]-(z['t'][i]-.02))>1e-9:continue
        for k in vals:vals[k].append(abs(z[k][i]-z[k][j]))
    v={k:max(x) if x else None for k,x in vals.items()}
    return {'successive_cycle_max':v,'pass':v['W'] is not None and v['W']<=.1 and v['B']<=.1 and max(v[k] for k in ['ia','ib','ic'])<=.2}
def hard(j,ramp):
    e=j['all']; tests={'voltage_min':e['Vmin']>=1080,'voltage_max':e['Vmax']<=1320,'phase_current':e['Iphase']<=1500,'space_current':e['Ispace']<=1500,'Bmin':e['Bmin']>=0,'Bmax':e['Bmax']<=100000,'b':e['bpeak']<=450000+1e-7,'u':e['u']<=450000+1e-7,'ramp':e['bdot']<=ramp+1e-6,'duty_span':e['mod']<=1,'circular_modulation':e['circular']<=1,'energy_closure':e['closure']<=.1}
    return {'pass':all(tests.values()),'checks':tests,'extrema':e,'clipped_cycles':j['clipped_cycles']}
def compare_case(tag):
    js=json.loads((R/(tag+'_s1.json')).read_text());jh=json.loads((R/(tag+'_s0.json')).read_text());cmd=js['command'];dt=float(cmd[4]);tau=float(cmd[6]);ramp=float(cmd[7]);offset=float(cmd[8]);onset=2+offset;deadline=onset+.7;end=onset+.9
    s=arr(tag+'_s1');h=arr(tag+'_s0');ds=arr(tag+'_s1','_dense');dh=arr(tag+'_s0','_dense');ss=arr(tag+'_s1','_snapshots');hs=arr(tag+'_s0','_snapshots');bins=arr(tag+'_s1','_bins')
    assert np.array_equal(s['t'],h['t']);assert np.array_equal(ds['t'],dh['t']);assert np.array_equal(ss['t'],hs['t'])
    checkpoints={k:bool(ss[k][0]==hs[k][0]) for k in FIELDS};cparr=np.genfromtxt(cmd[5],delimiter=',',names=True)
    cp_match={k:bool(ss[k][0]==cparr[k]) for k in FIELDS}
    dsample=np.diff(ds['t']); dense_max_gap=float(np.max(dsample));assert dense_max_gap<=1.00001e-6
    pw=(s['t']>=deadline-.1-1e-10)&(s['t']<=deadline+1e-10)
    diff={k:max(mx(ds[k]-dh[k]),mx(s[k][pw]-h[k][pw])) for k in ['W','B','ia','ib','ic','b','jd','jq','zw','cp','held','ub','da','db','dc','filter_energy']}
    rpass=diff['W']<=2 and diff['B']<=2 and max(diff[k] for k in ['ia','ib','ic'])<=2
    # Offline period-average cost: clip integration durations at declared window boundaries.
    prev=np.r_[2,s['t'][:-1]];dp=s['Pmean']-h['Pmean'];cost={}
    for label,ta,tb in [('preonset',2,onset),('whole_from_checkpoint',2,end),('service',onset,onset+.2),('recovery',onset+.2,deadline),('postdeadline',deadline,end),('total',onset,end)]:
        a=record_at(ss,ta);b=record_at(ss,tb);ah=record_at(hs,ta);bh=record_at(hs,tb)
        exact={k:(b[k]-a[k])-(bh[k]-ah[k]) for k in ['grid_energy','loss_energy','load_energy','battery_energy','bridge_energy']}
        exact['stored_energy_change']=sum((b[k]-a[k])-(bh[k]-ah[k]) for k in ['W','B','filter_energy'])
        exact['energy_identity_residual']=exact['stored_energy_change']-exact['grid_energy']+exact['loss_energy']+exact['load_energy']
        weights=np.maximum(0,np.minimum(s['t'],tb)-np.maximum(prev,ta));cost[label]={'signed_exact_J':exact['grid_energy'],'positive_cyclemean_J':float(np.dot(weights,np.maximum(dp,0))),'absolute_cyclemean_J':float(np.dot(weights,np.abs(dp))),'signed_cyclemean_J':float(np.dot(weights,dp)),'decomposition':exact,'healthy_grid_minus_modelbaseline_J':(bh['grid_energy']-ah['grid_energy'])-654498.7248565304*(tb-ta),'service_grid_minus_modelbaseline_J':(b['grid_energy']-a['grid_energy'])-654498.7248565304*(tb-ta)}
    rec=(s['t']>onset+.2)&(prev<deadline);cpmax=mx((s['cp']-h['cp'])[rec]);c=cost['recovery'];budget=abs(c['signed_exact_J'])<=100 and c['positive_cyclemean_J']<=100 and c['absolute_cyclemean_J']<=100 and cpmax<=5000
    per=periodic(h,deadline);errP=mx(bins['Pmean']-bins['Pcmdmean']);errQ=mx(bins['Qmean']-bins['Qcmdmean']);tracking=errP<=2000 and errQ<=10000
    s_hard=hard(js,ramp);h_hard=hard(jh,ramp)
    return {'tag':tag,'dt_s':dt,'tau_s':tau,'ramp_W_per_s':ramp,'offset_s':offset,'checkpoint_pair_equal':all(checkpoints.values()),'checkpoint_source_equal':all(cp_match.values()),'sample_alignment':{'dense_count':len(ds['t']),'dense_max_gap_s':dense_max_gap,'first_s':float(ds['t'][0]),'last_s':float(ds['t'][-1]),'pair_time_bitwise_equal':True},'recovery_differences':diff,'recovery_pass':rpass,'healthy_periodicity':per,'service_tracking':{'max_20ms_bin_P_error_W':errP,'max_20ms_bin_Q_error_var':errQ,'bin_duration_error_s':mx(bins['duration']-.02),'pass':tracking},'hard_service':s_hard,'hard_healthy':h_hard,'cost':cost,'incremental_cp_peak_W':cpmax,'budget_pass':budget,'endpoint':{'service':record_at(ss,deadline),'healthy':record_at(hs,deadline)},'pass':all([all(checkpoints.values()),all(cp_match.values()),rpass,per['pass'],tracking,s_hard['pass'],h_hard['pass'],budget])}
def main():
    out={'audited_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'audit_method':'Independent parser, calculations and assertions; no import of primary evaluation code','cases':[],'warmup':{},'missing':[]}
    for dt in ['h1','h05']:
        if (R/('warmup_'+dt+'.npz')).exists():
            z=arr('warmup_'+dt);out['warmup'][dt]=periodic(z,2)
    tags=['nominal_'+dt for dt in ['h1','h05']]+[f'tau{tau}_r{ramp}_o{offset}_{dt}' for tau,ramp,offset,dt in itertools.product([4,6],[25,35],[37,73],['h1','h05'])]+[f'tau{tau}_r{ramp}_o{offset}_{dt}' for tau,ramp,offset,dt in itertools.product([4.5,5.5],[27,33],[19,61],['h1','h05'])]
    for tag in tags:
        if all((R/(tag+f'_s{s}_bins.npz')).exists() for s in [0,1]):out['cases'].append(compare_case(tag))
        else:out['missing'].append(tag)
    out['refinement']=[]
    by={x['tag']:x for x in out['cases']}
    for tag in tags:
        if not tag.endswith('_h1') or tag not in by or tag[:-3]+'_h05' not in by:continue
        a=by[tag];b=by[tag[:-3]+'_h05'];diff={}
        for branch in ['service','healthy']:
            diff[branch]={k:abs(a['endpoint'][branch][k]-b['endpoint'][branch][k]) for k in ['W','B','ia','ib','ic']}
        out['refinement'].append({'case':tag[:-3],'differences':diff,'pass':all(v<=.1 for branch in diff.values() for v in branch.values())})
    man=json.loads((R.parent.parent/'SCIENCE_MANIFEST.json').read_text());out['core_changed']=[f['path'] for f in man['files'] if hashlib.sha256((R.parent.parent/f['path']).read_bytes()).hexdigest()!=f['sha256']]
    fr=json.loads((R/'EXECUTION_FREEZE_V2.json').read_text());out['frozen_changed']=[f for f,h in fr['files'].items() if hashlib.sha256((R/f).read_bytes()).hexdigest()!=h]
    prior=json.loads((R.parent/'V1A_COMPLETE_FREEZE.json').read_text());out['V1A_changed']=[f for f,h in prior['files'].items() if hashlib.sha256((R.parent/f).read_bytes()).hexdigest()!=h]
    out['all_available_contracts_pass']=all(x['pass'] for x in out['cases']) and all(x['pass'] for x in out['warmup'].values()) and all(x['pass'] for x in out['refinement']) and not out['core_changed'] and not out['frozen_changed'] and not out['V1A_changed']
    (A/'INDEPENDENT_RESULTS.json').write_text(json.dumps(out,indent=2,default=lambda x:x.item())+'\n')
    print(json.dumps({'cases':len(out['cases']),'missing':out['missing'],'pass':out['all_available_contracts_pass'],'failed':[x['tag'] for x in out['cases'] if not x['pass']],'core_changed':out['core_changed'],'frozen_changed':out['frozen_changed']},indent=2))
if __name__=='__main__':main()
