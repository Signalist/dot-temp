from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'network_copy'))
from certify_binned import certify_one,mapping,np
src=HERE.parent/'round3_g1_20261004/network_transfer'
rows=json.loads((src/'BINNED93_LTI_CERTIFICATES.json').read_text());results=[]
for row in rows:
    worst=max(row['bin_midpoint_certificates'],key=lambda x:max(x['continuous_finite_peak_upper_Hz'],x['infinite_tail_upper_from100_Hz']))
    tag=row['tag'];d=np.load(src/(tag+'.npz'));r=worst['r'];hi=bool(d['initial_high']);fb=bool(d['feedback']);M,D=mapping(r,hi,fb)
    new=certify_one(r,hi,M@d['theta'])
    diffs={k:float(new[k]-worst[k]) for k in new if isinstance(new[k],(int,float))}
    assert max(abs(v) for v in diffs.values())<1e-9,(tag,diffs)
    results.append(dict(tag=tag,selected_r=r,recomputed=new,differences=diffs))
(HERE/'NETWORK_SELECTED_RERUN.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
