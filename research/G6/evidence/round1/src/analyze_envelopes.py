from g6_model import *
import json,time,sys
import pandas as pd
OUT=Path(__file__).resolve().parents[1]

def polytope(coeff):
    coeff=np.asarray(coeff).reshape(-1,2);caps=1/coeff.max(axis=0)
    p=np.array([[0,0],[caps[0],0],caps,[0,caps[1]]],float)
    for c in coeff:
        if len(p)==0:break
        new=[]
        for i,s in enumerate(p):
            e=p[(i+1)%len(p)];ds=float(c@s-1);de=float(c@e-1)
            if ds<=1e-13:new.append(s)
            if (ds<0 and de>0) or(ds>0 and de<0):new.append(s+(e-s)*(-ds)/(de-ds))
        p=np.array(new)
    area=abs(np.dot(p[:,0],np.roll(p[:,1],-1))-np.dot(p[:,1],np.roll(p[:,0],-1)))/2
    return float(area),p

def shared_upper_from_cover(r):
    b=r['boxes'];u=r['leaf_upper'];cuts=np.unique(b[:,[2,3]])
    cs=(cuts[1:]+cuts[:-1])/2;arr=[]
    for k in cs:
        mask=(b[:,2]<=k)&(b[:,3]>=k)
        assert np.any(mask)
        selected=b[mask];order=selected[np.argsort(selected[:,0])]
        end=order[0,1]
        assert order[0,0] <= float(down(.08))
        for v in order[1:]:
            assert v[0] <= end
            end=max(end,v[1])
        assert end >= float(up(.75))
        arr.append(u[mask].max(axis=0))
    return np.array(arr),cuts

def many_transfer(m,fs,k):
    w=2*np.pi*fs;den=k*m.lam[None,:]-m.M*w[:,None]**2/(2*np.pi)+1j*m.D*w[:,None]/(2*np.pi)
    q=np.einsum('jmi,fm->fji',m.res,1/den)
    q[:,:m.n]*=-1j*w[:,None,None]/(2*np.pi)/.05
    q[:,m.n:]*=-k*m.kedge[None,:,None]/15
    return q

def sample_lower(m):
    ks=np.linspace(.85,1.15,65);ks[0]=float(up(.85));ks[-1]=float(down(1.15));fs=np.linspace(.08,.75,513);ph=2*np.pi*np.arange(64)/64;rows=[];witness=[];validated_freqs=[]
    sins=np.sin(m.hs[:,None]*ph);cos=np.cos(m.hs[:,None]*ph)
    for k in ks:
        H=np.array([many_transfer(m,fs*h,k)/h for h in m.hs])
        q=np.einsum('hfji,hp->fjip',H.real,sins)+np.einsum('hfji,hp->fjip',H.imag,cos)
        support=q.max(axis=(0,3));l1=np.abs(H).sum(axis=0).max(axis=0)
        # Turn each numerical optimizer witness into a rigorous feasible-point lower bound.
        inds0=q.transpose(1,2,0,3).reshape(m.J,2,-1).argmax(axis=-1)//64
        inds1=np.abs(H).sum(axis=0).argmax(axis=0)
        for fi in np.unique(np.r_[inds0.ravel(),inds1.ravel()]):
            ll,uu=m.bounds([float(fs[fi]),float(fs[fi]),float(k),float(k)])
            mask0=inds0==fi;mask1=inds1==fi
            support[mask0]=ll[0][mask0];l1[mask1]=ll[1][mask1]
        # These validated samples are rigorous lower witnesses, never safety upper bounds.
        rows.append(np.array([support,l1]));inds=q.transpose(1,2,0,3).reshape(m.J,2,-1).argmax(axis=-1)
        witness.append(np.stack([fs[inds//64],ph[inds%64]],axis=-1))
        validated_freqs.append(np.stack([fs[inds0],fs[inds1]],axis=0))
    return np.array(rows),ks,np.array(witness),np.array(validated_freqs)

def main(cfg):
    t0=time.time();m=Model(cfg);r=np.load(OUT/'raw'/f"{cfg['name']}_certificate.npz")
    shared,cuts=shared_upper_from_cover(r);sample,ks,wit,vfreq=sample_lower(m)
    sparse=[]
    for k in [.85,1.,1.15]:
        rr=[]
        for f in np.linspace(.08,.75,9):rr.append(m.peak_root(float(f),k)[0])
        sparse.append(np.max(rr,axis=0))
    sparse=np.array(sparse).max(axis=0)
    coeffs={
      'candidate_independent_grid_template_safe':r['upper'][0],
      'classic_shared_grid_template_safe':shared[:,0].reshape(-1,2),
      'classic_shared_grid_template_sample_outer':sample[:,0].reshape(-1,2),
      'phase_free_harmonic_shared_grid_safe':shared[:,1].reshape(-1,2),
      'phase_free_harmonic_shared_grid_sample_outer':sample[:,1].reshape(-1,2),
      'phase_free_harmonic_independent_grid_safe':r['upper'][1],
      'scalar_sum_of_site_worst_safe':np.max(r['upper'][0],axis=0)[None,:],
      'sparse_3x9_template_UNCERTIFIED':sparse,
    }
    summary=[];rays=[];polys={}
    for method,c in coeffs.items():
        area,poly=polytope(c)
        if method.endswith('_safe'):
            poly*=1-1e-10
            upper_check=isum(mul(iv(c[None,:,:]),iv(poly[:,None,:])),axis=2)[1]
            assert np.max(upper_check)<=1., (method,float(np.max(upper_check)))
        area=abs(np.dot(poly[:,0],np.roll(poly[:,1],-1))-np.dot(poly[:,1],np.roll(poly[:,0],-1)))/2
        inward=(1-1e-10) if method.endswith('_safe') else 1.
        axis0=inward/np.max(c[:,0]);axis1=inward/np.max(c[:,1]);balanced=inward/np.max(c@np.ones(2))
        if method.endswith('_safe'):
            endpoints=np.array([[axis0,0.],[0.,axis1],[balanced,balanced]])
            assert np.max(isum(mul(iv(c[None,:,:]),iv(endpoints[:,None,:])),axis=2)[1])<=1.
        polys[method]=poly.tolist();row={'model':cfg['name'],'method':method,'area_MW2':area,'area_is_numeric_geometry_estimate':True,'balanced_total_fundamental_MW':2*balanced,'axis0_MW':axis0,'axis1_MW':axis1,'constraints':len(c)};summary.append(row)
        for mix in np.linspace(0,1,41):
            w=np.array([mix,1-mix]);lam=inward/max(c@w)
            if method.endswith('_safe'):assert np.max(isum(mul(iv(c),iv((lam*w)[None,:])),axis=1)[1])<=1.
            rays.append({'model':cfg['name'],'method':method,'share0':mix,'total_fundamental_MW':lam})
    np.savez_compressed(OUT/'raw'/f"{cfg['name']}_envelope_coefficients.npz",shared_upper=shared,kappa_cuts=cuts,sample_lower=sample,kappa_samples=ks,sample_search_seed=wit,validated_lower_frequency_Hz=vfreq,validated_lower_phase_grid_size=np.array(256),sparse=sparse,**{k:v for k,v in coeffs.items()})
    pd.DataFrame(summary).to_csv(OUT/'results'/f"{cfg['name']}_envelope_summary.csv",index=False)
    pd.DataFrame(rays).to_csv(OUT/'results'/f"{cfg['name']}_allocation_rays.csv",index=False)
    (OUT/'results'/f"{cfg['name']}_polygons.json").write_text(json.dumps(polys,indent=2))
    print(cfg['name'],'analysis_s',time.time()-t0,json.dumps(summary),flush=True)
if __name__=='__main__':
    for cfg in MODELS:
        if len(sys.argv)>1 and cfg['name'] not in sys.argv[1:]:continue
        main(cfg)
