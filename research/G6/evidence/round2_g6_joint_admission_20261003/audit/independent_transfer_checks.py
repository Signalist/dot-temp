"""Independent transfer data/kernel checks; no candidate-code import.
Ordinary floating numerical qualification, not a uniform transfer enclosure.
"""
from pathlib import Path
import json, hashlib, os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np
from scipy import sparse
from scipy.linalg import expm, solve
from scipy.sparse.linalg import splu

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent/'transfer'
SOURCE=OUT.parents[1]/'round2_20261003'/'grid_transfer'
res={'scope':'Independent frozen-data checks; no source solver/code imports; no validated-rounding, uniform descriptor-transfer or nonlinear guarantee','networks':{}}
test_s=[.004j,.023+.031j,.27+1.13j,7+23j]
for name in ['kundur','wecc']:
    modal=np.load(ROOT/f'{name}_kernel.npz')
    lam,R=modal['lam'],modal['R']
    data={}
    if name=='kundur':
        raw=np.load(SOURCE/'kundur_reduced51.npz')
        A,B,C=raw['A'],raw['B'][:,[0,2]],raw['C_frequency_Hz']
        direct=lambda s:C@solve(s*np.eye(len(A))-A,B)
        impulse=[]
        for t in [0.,.123,.7,2.,17.]:
            exact=C@expm(t*A)@B
            approximate=np.sum(R*np.exp(lam*t)[None,:,None],axis=1)
            impulse.append({'t':t,'absolute_error':float(abs(exact-approximate).max())})
        assert max(v['absolute_error'] for v in impulse)<1e-12
        data['original_matrix_impulse_checks']=impulse
    else:
        K=sparse.load_npz(SOURCE/'wecc_verified_descriptor_K.npz')
        raw=np.load(SOURCE/'wecc_descriptor_aux.npz')
        mass=raw['mass']; B=raw['G'][:,[0,2]]
        oi=np.array([i for i,x in enumerate(raw['x_names']) if x.startswith('omega GENROU ')])
        direct=lambda s:60*splu((s*sparse.diags(mass)-K).astype(complex).tocsc()).solve(B.astype(complex))[oi,:]
    checks=[]
    for s in test_s:
        exact=direct(s)
        approximate=np.sum(R/(s-lam)[None,:,None],axis=1)
        err=float(abs(exact-approximate).max())
        rel=float(np.linalg.norm(exact-approximate)/np.linalg.norm(exact))
        assert rel<1e-7
        checks.append({'s':[s.real,s.imag],'absolute_error':err,'relative_error':rel})
    data['new_original_source_resolvent_checks']=checks
    # Recompute all-phase, all-output support maxima for five rays from frozen
    # coefficient data. This avoids relying on the stored argmax locations.
    W=np.load(ROOT/f'{name}_coefficients.npy',mmap_mode='r')
    stored=np.load(ROOT/f'{name}_support_arrays.npz')
    peaks=[]
    for j in [0,10,20,30,40]:
        a=np.array([j/40,1-j/40])
        mx={key:0. for key in ['committed','dynamic_optional','fixed_optional','independent_ports']}
        for start in range(0,W.shape[1],128):
            X=W[:,start:start+128,:,:]
            p=X[:,:,0,:]*a[0];q=X[:,:,1,:]*a[1]
            v=np.abs(p+q).sum(axis=-1)
            aa=np.abs(p).sum(axis=-1);bb=np.abs(q).sum(axis=-1)
            # Independent formula, using one-lag box vertex extrema directly.
            dyn=np.maximum.reduce([np.abs(p),np.abs(q),np.abs(p+q)]).sum(axis=-1)
            arrays={'committed':v,'dynamic_optional':dyn,
                    'fixed_optional':np.maximum.reduce([v,aa,bb]),
                    'independent_ports':aa+bb}
            for key,values in arrays.items():mx[key]=max(mx[key],float(values.max()))
        errors={key:abs(value-float(stored[key+'_peak'][j])) for key,value in mx.items()}
        assert max(errors.values())<2e-16
        peaks.append({'ray':j,'peaks':mx,'differences_from_recorded':errors})
    data['independent_support_maxima']=peaks
    # All stored finite witnesses must be admissible under their own contract
    # and attain the directly projected output at their specified location.
    witnesses=np.load(ROOT/f'{name}_witnesses.npz')
    witness_errors=[]
    for contract in ['committed','dynamic_optional','independent_ports']:
        for j in range(41):
            a=np.array([j/40,1-j/40])
            word=witnesses[contract+'_input_MW_per_total_MW'][j]
            assert np.all(abs(word)<=a+1e-14)
            if contract=='committed':
                assert np.all((abs(word-a)<1e-14).all(axis=1)|(abs(word+a)<1e-14).all(axis=1))
            elif contract=='dynamic_optional':
                assert np.all(word[:,0]*word[:,1]>=-1e-14)
            o,p,_=witnesses[contract+'_argmax'][j]
            attained=float(np.sum(W[o,p].T*word))
            recorded=float(witnesses[contract+'_output'][j])
            witness_errors.append(abs(attained-recorded))
    assert max(witness_errors)<2e-16
    data['witness_contracts_checked']=123
    data['max_witness_projection_error']=max(witness_errors)
    res['networks'][name]=data
res['all_checks_passed']=True
(OUT/'INDEPENDENT_TRANSFER_RESULTS.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({'all_checks_passed':True,'networks':{
 n:{'max_new_resolvent_relative_error':max(z['relative_error'] for z in v['new_original_source_resolvent_checks']),
    'max_witness_projection_error':v['max_witness_projection_error']} for n,v in res['networks'].items()}},indent=2))
