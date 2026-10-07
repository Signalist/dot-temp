"""Replay the saved design4 envelopes/exports without rerunning analysis or challenges."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd,mpmath as mp
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from g6_model import *
from analyze_envelopes import shared_upper_from_cover
name=sys.argv[1] if len(sys.argv)>1 else 'design4';m=Model(next(c for c in MODELS if c['name']==name));ep=ROOT/'raw'/f'{name}_envelope_coefficients.npz';e=np.load(ep);r=np.load(ROOT/'raw'/f'{name}_certificate.npz')
rec={'model':name,'envelope_artifact_sha256':hashlib.sha256(ep.read_bytes()).hexdigest(),'analyzer_sha256':hashlib.sha256((ROOT/'src/analyze_envelopes.py').read_bytes()).hexdigest()}
shared,cuts=shared_upper_from_cover(r);rec['shared_upper_reproduced']=bool(np.array_equal(shared,e['shared_upper']));rec['cuts_reproduced']=bool(np.array_equal(cuts,e['kappa_cuts']));b=r['boxes'];rec['closed_strip_full_containment']=True
for l,u in zip(cuts[:-1],cuts[1:]):
 mid=(l+u)/2;mask=(b[:,2]<=mid)&(b[:,3]>=mid)
 rec['closed_strip_full_containment'] &= bool(np.all(b[mask,2]<=l) and np.all(b[mask,3]>=u))
rec['closed_strips']=len(cuts)-1;rec['shared_dominated_by_independent']=bool(np.all(shared<=r['upper'][None,:,:,:]))
rec['validated_lower_match']=True;rec['all_lower_witness_parameters_feasible']=True;vf=e['validated_lower_frequency_Hz'];ks=e['kappa_samples'];sl=e['sample_lower']
for t,k in enumerate(ks):
 rec['all_lower_witness_parameters_feasible'] &= bool(mp.mpf('0.85')<=mp.mpf(float(k))<=mp.mpf('1.15'))
 for f in np.unique(vf[t]):
  rec['all_lower_witness_parameters_feasible'] &= bool(mp.mpf('0.08')<=mp.mpf(float(f))<=mp.mpf('0.75'))
  ll,uu=m.bounds([f,f,k,k]);mask=vf[t]==f;rec['validated_lower_match'] &= bool(np.array_equal(ll[mask],sl[t][mask]))
polys=json.loads((ROOT/'results'/f'{name}_polygons.json').read_text());summary=pd.read_csv(ROOT/'results'/f'{name}_envelope_summary.csv',float_precision='round_trip');rays=pd.read_csv(ROOT/'results'/f'{name}_allocation_rays.csv',float_precision='round_trip');rec['safe_exports']={}
for method,p in polys.items():
 if not method.endswith('_safe'):continue
 c=e[method];p=np.array(p);row=summary[summary.method==method].iloc[0];pts=[[row.axis0_MW,0],[0,row.axis1_MW],[row.balanced_total_fundamental_MW/2]*2]
 for _,v in rays[rays.method==method].iterrows():pts.append((v.total_fundamental_MW*np.array([v.share0,1-v.share0])).tolist())
 pts=np.vstack([p,np.array(pts)]);out=isum(mul(iv(c[None,:,:]),iv(pts[:,None,:])),axis=2)[1]
 rec['safe_exports'][method]={'checked_points':len(pts),'nonnegative':bool(np.all(pts>=0)),'max_outward_constraint_ratio':float(out.max()),'safe':bool(np.all(out<=1))}
rec['area_labeled_numeric']=bool('area_is_numeric_geometry_estimate' in summary.columns and summary.area_is_numeric_geometry_estimate.all())
cp=ROOT/'raw'/f'{name}_challenge_cases.json'
if cp.exists():
 cases=json.loads(cp.read_text());fixed=[c for c in cases if c['condition']=='fixed_template'];rec['challenge_cases']={'count':len(cases),'fixed_count':len(fixed),'base_scenarios':len(set(c['scenario'] for c in fixed)),'each_base_has_four_methods':all(len([c for c in fixed if c['scenario']==s])==4 for s in set(c['scenario'] for c in fixed)),'nonlinear_extension_label_all':all(c.get('nonlinear_model_extension') is True for c in cases),'old_ambiguous_out_of_contract_key_present':any('out_of_contract' in c for c in cases),'saved_effective_drift':all('requested_drift_amplitudes' in c and 'drift_amplitudes' in c for c in cases if c['condition']=='frequency_drift')}
rec['artifact_changed_during_audit']=rec['envelope_artifact_sha256']!=hashlib.sha256(ep.read_bytes()).hexdigest()
(ROOT/'review'/f'{name}_envelope_artifact_audit.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec,indent=2))
