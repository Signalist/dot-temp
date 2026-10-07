"""Public-core verification and post-regeneration numerical assessment.
The frozen scientific source is imported unchanged in its equations and assess logic.
Original full-archive hash checks cannot run with intentionally omitted raw traces;
this wrapper reports public-core integrity separately rather than falsifying them.
"""
from pathlib import Path
import hashlib, json, sys, importlib.util, itertools
R=Path(__file__).resolve().parent

def verify():
    m=json.loads((R/'PUBLIC_FILE_MANIFEST.json').read_text())
    errors=[]
    for e in m['included']:
        f=R/e['path']
        if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest()!=e['public_sha256']:errors.append(e['path'])
    print(json.dumps({'public_files_checked':len(m['included']),'errors':errors},indent=2))
    if errors:raise SystemExit(1)

def summarize(stage):
    folder=R/'recovery_phase2'
    if stage=='V2':folder=folder/'V2'
    elif stage!='V1A':raise SystemExit('Choose V1A or V2')
    spec=importlib.util.spec_from_file_location('frozen_assessment',folder/'summarize.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    rows=[]
    configs=[('nominal',.005,30e6,0)]
    configs += [('regression' if stage=='V2' else 'holdout',t,r,o) for t,r,o in itertools.product([.004,.006],[25e6,35e6],[37e-6,73e-6])]
    if stage=='V2':configs += [('confirmation',t,r,o) for t,r,o in itertools.product([.0045,.0055],[27e6,33e6],[19e-6,61e-6])]
    for group,t,r,o in configs:
        for dt in [1e-6,.5e-6]:
            h='h1' if dt==1e-6 else 'h05'
            tag='nominal_'+h if group=='nominal' else f'tau{t*1000:g}_r{r/1e6:.0f}_o{o*1e6:.0f}_{h}'
            if not (folder/(tag+'_s1.npz')).exists():raise SystemExit('Regenerate raw trajectories first: missing '+tag)
            row=m.assess(tag,t,r,o,dt);row['evidence_group']=group;rows.append(row)
    result={'scope':'Post-regeneration numerical reassessment with original assess function; no claim to reproduce original historical full-archive hashes','case_count':len(rows),'full_pass_count':sum(x['pass'] for x in rows),'cases':rows}
    out=folder/('REPRODUCED_PUBLIC_SUMMARY_'+stage+'.json');out.write_text(json.dumps(result,indent=2)+'\n')
    print(out.relative_to(R));print('full pass',result['full_pass_count'],'/',len(rows))

def phase3():
    folder=R/'recovery_phase3_workload_match'
    spec=importlib.util.spec_from_file_location('frozen_phase3_assessment',folder/'evaluate_phase3.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    cum,work=m.workload_definition()
    configs=json.loads((folder/'PROTOCOL_PHASE3.json').read_text())['configurations']
    for c in configs:
        if not (folder/(c['tag']+'_L.npz')).exists():raise SystemExit('Regenerate phase3 L and prior V2 S/F raw trajectories first')
    rows=[m.assess(c,cum) for c in configs]
    out={'scope':'Retrospective same-input comparator numerical reassessment using original workload_definition and assess; historical full-archive preservation hashes not asserted','no_new_blind_confirmation':True,'case_count':len(rows),'full_pass_count':sum(x['pass'] for x in rows),'workload':work,'cases':rows}
    dest=folder/'REPRODUCED_PUBLIC_SUMMARY_PHASE3.json';dest.write_text(json.dumps(out,indent=2)+'\n')
    print(dest.relative_to(R));print('full pass',out['full_pass_count'],'/',len(rows))

if __name__=='__main__':
    if len(sys.argv)==2 and sys.argv[1]=='verify':verify()
    elif len(sys.argv)==3 and sys.argv[1]=='summarize' and sys.argv[2]=='PHASE3':phase3()
    elif len(sys.argv)==3 and sys.argv[1]=='summarize':summarize(sys.argv[2])
    else:raise SystemExit('Usage: python PUBLIC_REPRODUCE.py verify | summarize V1A | summarize V2 | summarize PHASE3')
