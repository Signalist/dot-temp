"""Independent phase3 audit. Imports no campaign evaluator.
Compare raw F/S/L NPZ records, exact milestones, physical bounds and energy accounts.
"""
from pathlib import Path
import csv, hashlib, json, sys
import numpy as np
A=Path(__file__).resolve().parent
R=A.parent
OLD=R.parent/'recovery_phase2'/'V2'
protocol=json.loads((R/'PROTOCOL_PHASE3.json').read_text())
L_SUFFIX=sys.argv[1] if len(sys.argv)>1 else '_L'

def read(path):
    with np.load(path) as z:return {k:z[k].copy() for k in z.files}

def snapshot(z,t):
    j=int(np.argmin(abs(z['t']-t)))
    assert abs(z['t'][j]-t)<1e-9
    return {k:float(v[j]) for k,v in z.items()}

def vector_diffs(a,b,fields):
    assert np.array_equal(a['t'],b['t'])
    return {k:float(np.max(abs(a[k]-b[k]))) for k in fields}

def extrema_valid(j,ramp):
    z=j['all']
    limits={
      'V_min':z['Vmin']>=1080, 'V_max':z['Vmax']<=1320,
      'I_phase':z['Iphase']<=1500,'I_vector':z['Ispace']<=1500,
      'B_min':z['Bmin']>=0,'B_max':z['Bmax']<=100000,
      'buffer_power':z['bpeak']<=450000+1e-6,'command':z['u']<=450000+1e-6,
      'slew':z['bdot']<=ramp+1e-6,'duty_span':z['mod']<=1+1e-9,
      'theory_circle':z['circular']<=1+1e-9,
      'energy_quality':z['closure']<=.1,
    }
    return {'pass':all(limits.values()),'criteria':limits,'extrema':z}

def energy_pair(a,b,sa,sb,lo,hi):
    ta=a['t'];assert np.array_equal(ta,b['t'])
    starts=np.r_[2.,ta[:-1]]
    weights=np.clip(np.minimum(ta,hi)-np.maximum(starts,lo),0,None)
    dp=a['Pmean']-b['Pmean']
    # Positive/absolute metrics are deliberately on full PWM-cycle mean power differences.
    out={'positive_J':float(weights@np.maximum(dp,0)), 'absolute_J':float(weights@np.abs(dp))}
    a0,a1,b0,b1=snapshot(sa,lo),snapshot(sa,hi),snapshot(sb,lo),snapshot(sb,hi)
    for outkey,inkey in [('signed_J','grid_energy'),('copper_J','loss_energy'),('load_J','load_energy'),('battery_J','battery_energy'),('bridge_J','bridge_energy'),('W_J','W'),('B_J','B'),('Z_J','filter_energy')]:
      out[outkey]=(a1[inkey]-a0[inkey])-(b1[inkey]-b0[inkey])
    out['net_after_copper_J']=out['signed_J']-out['copper_J']
    out['stored_J']=out['W_J']+out['B_J']+out['Z_J']
    out['residual_J']=out['stored_J']-out['signed_J']+out['copper_J']+out['load_J']
    return out

def periodic(z,end):
    m=(z['t']>=end-.1-1e-10)&(z['t']<=end+1e-10)
    return {k:float(max(abs(z[k][m]-np.interp(z['t'][m]-.02,z['t'],z[k])))) for k in ['W','B','ia','ib','ic']}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

rows=[];ledger=[]
for cfg in protocol['configurations']:
    tag=cfg['tag']; print('Audit',tag,flush=True)
    prefixes={'F':OLD/(tag+'_s0'),'S':OLD/(tag+'_s1'),'L':R/(tag+L_SUFFIX)}
    data={k:read(Path(str(p)+'.npz')) for k,p in prefixes.items()}
    snaps={k:read(Path(str(p)+'_snapshots.npz')) for k,p in prefixes.items()}
    dense={k:read(Path(str(p)+'_dense.npz')) for k,p in prefixes.items()}
    info={k:json.loads(Path(str(p)+'.json').read_text()) for k,p in prefixes.items()}
    bins={k:read(Path(str(p)+'_bins.npz')) for k,p in prefixes.items()}
    for k in data:assert np.array_equal(data[k]['t'],data['S']['t'])
    onset=2+cfg['offset_s'];end=onset+.2;dead=end+.5;finish=dead+.2
    same_initial=all(all(snaps[k][f][0]==snaps['S'][f][0] for f in snaps['S']) for k in ['F','L'])
    diffs=vector_diffs(dense['S'],dense['L'],['W','B','ia','ib','ic','b','jd','jq','zw','cp','held','ub','da','db','dc','filter_energy'])
    max_load_discrepancy=float(np.max(abs(data['S']['load_energy']-data['L']['load_energy'])))
    max_loadmean_discrepancy=float(np.max(abs(data['S']['loadmean']-data['L']['loadmean'])))
    hard={k:extrema_valid(info[k],cfg['ramp_W_per_s']) for k in data}
    tracking={k:{p:float(max(abs(bins[k][p+'mean']-bins[k][p+'cmdmean']))) for p in ['P','Q']} for k in ['S','L']}
    tracking_pass=all(z['P']<=2000 and z['Q']<=10000 for z in tracking.values())
    windowdefs={'pre_onset':(2.,onset),'service':(onset,end),'recovery':(end,dead),'post_deadline':(dead,finish),'onset_total':(onset,finish),'checkpoint_total':(2.,finish)}
    energies={};closure=0
    for name,(lo,hi) in windowdefs.items():
      pairs={}
      for pair,ka,kb in [('S-F','S','F'),('S-L','S','L'),('L-F','L','F')]:
        e=energy_pair(data[ka],data[kb],snaps[ka],snaps[kb],lo,hi)
        pairs[pair]=e;ledger.append({'case':tag,'window':name,'pair':pair,**e})
      for field in ['signed_J','copper_J','load_J','stored_J','net_after_copper_J']:
        closure=max(closure,abs(pairs['S-F'][field]-pairs['S-L'][field]-pairs['L-F'][field]))
      energies[name]=pairs
    m=(data['S']['t']>end)&(data['S']['t']<=dead+1e-12)
    max_cp=float(max(abs(data['S']['cp'][m]-data['L']['cp'][m])))
    rec=energies['recovery']['S-L'];cost_pass=max_cp<=5000+1e-9 and abs(rec['signed_J'])<=100 and rec['positive_J']<=100 and rec['absolute_J']<=100
    return_pass=diffs['W']<=2 and diffs['B']<=2 and max(diffs[p] for p in ['ia','ib','ic'])<=2
    points={name:{k:snapshot(snaps[k],at) for k in data} for name,at in [('checkpoint',2.),('onset',onset),('service_end',end),('deadline',dead),('finish',finish)]}
    result={'tag':tag,'config':cfg,'identical_complete_checkpoint':same_initial,'max_cumulative_S_L_load_difference_J':max_load_discrepancy,'max_PWM_mean_S_L_load_difference_W':max_loadmean_discrepancy,'hard':hard,'tracking':tracking,'return_max':diffs,'max_recovery_cP_S_L_W':max_cp,'signed_decomposition_max_residual_J':closure,'energy':energies,'periodicity':{k:periodic(data[k],dead) for k in data},'snapshots':points}
    result['pass']=bool(same_initial and all(hard[k]['pass'] for k in ['S','L']) and tracking_pass and return_pass and cost_pass and max_load_discrepancy<=1e-5 and closure<=1e-8)
    rows.append(result)

res={'purpose':'Independent raw-data audit; no primary evaluator imported','case_count':len(rows),'unique_configs':len({(x['config']['tau_s'],x['config']['ramp_W_per_s'],x['config']['offset_s']) for x in rows}),'all_pass':all(x['pass'] for x in rows),'results':rows}
res['worst']={
 'W_J':max(x['return_max']['W'] for x in rows), 'B_J':max(x['return_max']['B'] for x in rows),
 'phase_A':max(x['return_max'][p] for x in rows for p in ['ia','ib','ic']),
 'recovery_abs_J':max(x['energy']['recovery']['S-L']['absolute_J'] for x in rows),
 'recovery_positive_J':max(x['energy']['recovery']['S-L']['positive_J'] for x in rows),
 'recovery_signed_magnitude_J':max(abs(x['energy']['recovery']['S-L']['signed_J']) for x in rows),
 'recovery_cP_W':max(x['max_recovery_cP_S_L_W'] for x in rows),
 'load_cumulative_discrepancy_J':max(x['max_cumulative_S_L_load_difference_J'] for x in rows),
 'signed_decomposition_residual_J':max(x['signed_decomposition_max_residual_J'] for x in rows),
 'paired_energy_ledger_residual_J':max(abs(x['residual_J']) for x in ledger)
}
res['new_L_sampling_hardware']={f:(min if f.endswith('min') else max)(x['hard']['L']['extrema'][f] for x in rows) for f in ['Vmin','Vmax','Iphase','Ispace','Bmin','Bmax','bpeak','u','bdot','mod','circular','closure']}
(A/'INDEPENDENT_RESULTS.json').write_text(json.dumps(res,indent=2)+'\n')
with open(A/'THREE_BRANCH_LEDGER.csv','w') as f:
    w=csv.DictWriter(f,fieldnames=list(ledger[0]));w.writeheader();w.writerows(ledger)
print(json.dumps({k:v for k,v in res.items() if k!='results'},indent=2))
