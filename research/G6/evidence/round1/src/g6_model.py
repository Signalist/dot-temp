"""Original synthetic model and outward-rounded rectangular interval arithmetic.
Not an IEEE benchmark, measured data, or a full AC/PQ/UPS model.
"""
import numpy as np
from dataclasses import dataclass
from pathlib import Path
import mpmath as mp
mp.mp.dps=80
mp.iv.dps=80
NEG=-np.inf; POS=np.inf

def down(x):return np.nextafter(np.asarray(x,dtype=float),NEG)
def up(x):return np.nextafter(np.asarray(x,dtype=float),POS)
def iv(x):a=np.asarray(x,dtype=float);return a,a

def iconst(x):
    v=float(x); lo=np.nextafter(v,NEG);hi=np.nextafter(v,POS)
    assert mp.mpf(float(lo))<=x<=mp.mpf(float(hi))
    return np.array(lo),np.array(hi)
def ivconst(x):
    # mpmath interval transcendental backend supplies enclosing endpoints.
    return np.array(np.nextafter(float(x.a),NEG)),np.array(np.nextafter(float(x.b),POS))
PI=ivconst(mp.iv.pi)
def add(a,b):return down(a[0]+b[0]),up(a[1]+b[1])
def neg(a):return -a[1],-a[0]
def sub(a,b):return add(a,neg(b))
def mul(a,b):
    vals=np.array(np.broadcast_arrays(a[0]*b[0],a[0]*b[1],a[1]*b[0],a[1]*b[1]))
    return down(np.min(vals,axis=0)),up(np.max(vals,axis=0))
def div(a,b):
    assert np.all((b[0]>0)|(b[1]<0))
    return mul(a,(down(1/b[1]),up(1/b[0])))
def sq(a):
    lo=np.minimum(a[0]**2,a[1]**2);hi=np.maximum(a[0]**2,a[1]**2)
    lo=np.where((a[0]<=0)&(a[1]>=0),0.,lo)
    return np.maximum(0,down(lo)),up(hi)
def isum(a,axis=None):
    # Sequential outward addition, avoiding uncertain reduction order.
    if axis is None:return isum((a[0].ravel(),a[1].ravel()),0)
    aa=np.moveaxis(a[0],axis,0);bb=np.moveaxis(a[1],axis,0)
    lo=np.zeros(aa.shape[1:]);hi=np.zeros(bb.shape[1:])
    for l,h in zip(aa,bb):lo=down(lo+l);hi=up(hi+h)
    return lo,hi

def interval_abs(re,im):
    ab=add(sq(re),sq(im))
    return np.maximum(0,down(np.sqrt(np.maximum(ab[0],0.)))),up(np.sqrt(ab[1]))

def exact_trig_grid(P=256):
    hs=np.array([1,3,5]);lo_s=[];hi_s=[];lo_c=[];hi_c=[]
    for h in hs:
        ss=[ivconst(mp.iv.sin(mp.iv.pi*(2*int(h)*k)/P)) for k in range(P)]
        cc=[ivconst(mp.iv.cos(mp.iv.pi*(2*int(h)*k)/P)) for k in range(P)]
        lo_s.append([x[0] for x in ss]);hi_s.append([x[1] for x in ss]);lo_c.append([x[0] for x in cc]);hi_c.append([x[1] for x in cc])
    return (np.array(lo_s),np.array(hi_s)),(np.array(lo_c),np.array(hi_c))

MODELS=[
 {'name':'design4','n':4,'weights':{1:90,2:65,3:25},'M':160.,'D':26.,'sources':[0,3]},
 {'name':'interior4','n':4,'weights':{1:45,2:90,3:10},'M':180.,'D':28.,'sources':[0,1]},
 {'name':'transfer8_cube','n':8,'weights':{1:70,2:90,4:50},'M':160.,'D':26.,'sources':[0,7]},
 {'name':'transfer8_mesh','n':8,'weights':{1:90,2:40,3:10,4:65,6:15,7:5},'M':190.,'D':30.,'sources':[1,6]},
]

class Model:
    def __init__(self,cfg):
        self.cfg=cfg; self.n=n=cfg['n'];self.M=cfg['M'];self.D=cfg['D'];self.sources=cfg['sources']
        self.sign=np.array([[(-1)**((m&i).bit_count()) for m in range(n)] for i in range(n)],float)
        self.lam=np.array([sum(w*(1-(-1)**((m&k).bit_count())) for k,w in cfg['weights'].items()) for m in range(n)],float)
        self.edges=[(i,i^k,float(w)) for k,w in cfg['weights'].items() if w for i in range(n) if i<(i^k)]
        # output x mode x source residues, exact binary rationals.
        rf=np.array([self.sign[j,:,None]*self.sign[self.sources].T/n for j in range(n)])
        re=np.array([(self.sign[i,:,None]-self.sign[j,:,None])*self.sign[self.sources].T/n for i,j,k in self.edges])
        self.res=np.concatenate([rf,re],axis=0)
        self.labels=[f'f_Hz_bus{i}' for i in range(n)]+[f'flow_MW_{i}_{j}' for i,j,k in self.edges]
        self.kedge=np.array([k for i,j,k in self.edges]); self.J=len(self.labels)
        self.S,self.C=exact_trig_grid();self.hs=np.array([1,3,5],float)

    def transfer(self,f,kappa):
        w=2*np.pi*np.asarray(f);den=kappa*self.lam-self.M*w*w/(2*np.pi)+1j*self.D*w/(2*np.pi)
        qq=np.einsum('jmi,m->ji',self.res,1/den)
        qq[:self.n]*=-1j*w/(2*np.pi)/.05
        qq[self.n:]*=-kappa*self.kedge[:,None]/15.
        return qq

    def transfer_interval(self,fl,fu,kl,ku,_refine=True):
        f=(np.array(fl),np.array(fu));kap=(np.array(kl),np.array(ku))
        twopi=mul(iv(2.),PI);w=mul(twopi,f)
        real=sub(mul(kap,iv(self.lam)),div(mul(iv(self.M),sq(w)),twopi))
        imag=div(mul(iv(self.D),w),twopi)
        den=add(sq(real),sq(imag))
        ire=div(real,den); iim=neg(div(imag,den))
        ar=mul(iv(self.res), (ire[0][None,:,None],ire[1][None,:,None]))
        ai=mul(iv(self.res), (iim[0][None,:,None],iim[1][None,:,None]))
        qr=isum(ar,axis=1);qi=isum(ai,axis=1)
        nf=div(neg(w),mul(twopi,div(iv(1.),iv(20.)))) # imaginary multiplier -i*w/(2pi)/.05
        f_re=neg(mul(nf,(qi[0][:self.n],qi[1][:self.n])))
        f_im=mul(nf,(qr[0][:self.n],qr[1][:self.n]))
        ne=div(neg(mul(kap,iv(self.kedge[:,None]))),iv(15.))
        e_re=mul(ne,(qr[0][self.n:],qr[1][self.n:]));e_im=mul(ne,(qi[0][self.n:],qi[1][self.n:]))
        rr=(np.vstack([f_re[0],e_re[0]]),np.vstack([f_re[1],e_re[1]]))
        ii=(np.vstack([f_im[0],e_im[0]]),np.vstack([f_im[1],e_im[1]]))
        if _refine and (fu>fl or ku>kl):
            fc=(fl+fu)/2;kc=(kl+ku)/2
            wc=mul(twopi,iv(fc));dcr=sub(mul(iv(kc),iv(self.lam)),div(mul(iv(self.M),sq(wc)),twopi));dci=div(mul(iv(self.D),wc),twopi)
            rho=interval_abs(sub(real,dcr),sub(imag,dci))[1]
            dcmin=interval_abs(dcr,dci)[0];margin=down(dcmin-rho)
            if np.all(margin>0):
                invrad=div(iv(rho),mul(iv(dcmin),iv(margin)))[1]
                invmax=div(iv(1.),iv(margin))[1]
                sr=isum(mul(iv(abs(self.res)),iv(invrad[None,:,None])),axis=1)[1]
                sm=isum(mul(iv(abs(self.res)),iv(invmax[None,:,None])),axis=1)[1]
                dw=sub(w,wc);dwmax=np.maximum(abs(dw[0]),abs(dw[1]))
                nc=div(wc,mul(twopi,div(iv(1.),iv(20.))))[1]
                nd=div(iv(dwmax),mul(twopi,div(iv(1.),iv(20.))))[1]
                rf=add(mul(iv(nc),iv(sr[:self.n])),mul(iv(nd),iv(sm[:self.n])))[1]
                dk=sub(kap,iv(kc));dkmax=np.maximum(abs(dk[0]),abs(dk[1]))
                ec=div(mul(iv(kc),iv(self.kedge[:,None])),iv(15.))[1]
                ed=div(mul(iv(dkmax),iv(self.kedge[:,None])),iv(15.))[1]
                re=add(mul(iv(ec),iv(sr[self.n:])),mul(iv(ed),iv(sm[self.n:])))[1]
                radius=np.vstack([rf,re])
                cr,ci=self.transfer_interval(fc,fc,kc,kc,_refine=False)
                rr=(np.maximum(rr[0],down(cr[0]-radius)),np.minimum(rr[1],up(cr[1]+radius)))
                ii=(np.maximum(ii[0],down(ci[0]-radius)),np.minimum(ii[1],up(ci[1]+radius)))
        return rr,ii

    def bounds(self,box):
        fl,fu,kl,ku=box;rr=[];ii=[]
        for h in self.hs:
            # h integers, correctly enclose products with dyadic f boundaries.
            r,i=self.transfer_interval(down(h*fl),up(h*fu),kl,ku)
            rh=div(r,iv(h));ih=div(i,iv(h));rr.append(rh);ii.append(ih)
        re=(np.array([r[0] for r in rr]),np.array([r[1] for r in rr]))
        im=(np.array([i[0] for i in ii]),np.array([i[1] for i in ii]))
        mag=interval_abs(re,im)
        l1=isum(mag,axis=0)
        # h,output,source,phase interval product
        ss=(self.S[0][:,None,None,:],self.S[1][:,None,None,:]);cc=(self.C[0][:,None,None,:],self.C[1][:,None,None,:])
        v=add(mul((re[0][...,None],re[1][...,None]),ss),mul((im[0][...,None],im[1][...,None]),cc))
        q=isum(v,axis=0)
        low=np.max(q[0],axis=-1);high=np.max(q[1],axis=-1)
        curvature=isum(mul(mag,iv(self.hs[:,None,None]**2)),axis=0)
        step=div(mul(iv(2.),PI),iv(self.S[0].shape[1]))
        error=div(mul(sq(step),curvature),iv(8.))
        locked=(low,up(high+error[1]))
        return np.array([locked[0],l1[0]]),np.array([locked[1],l1[1]])

    def peak_root(self,f,kappa):
        """Independent classical trigonometric-polynomial stationary-point oracle."""
        H=np.array([self.transfer(h*f,kappa)/h for h in self.hs]);z=-1j*H
        out=np.empty((self.J,2));phase=np.empty_like(out)
        for j in range(self.J):
            for i in range(2):
                coeff=np.zeros(11,complex)
                for k,h in enumerate(self.hs.astype(int)):
                    coeff[5+h]=1j*h*z[k,j,i]/2
                    coeff[5-h]=-1j*h*np.conj(z[k,j,i])/2
                roots=np.roots(np.trim_zeros(coeff,'b')[::-1]);ang=np.angle(roots[abs(abs(roots)-1)<1e-6])
                ang=np.r_[ang,0.];vals=np.real(np.exp(1j*np.outer(ang,self.hs))@z[:,j,i]);idx=np.argmax(vals)
                out[j,i]=vals[idx];phase[j,i]=ang[idx]
        return out,phase

    def linear_state(self,t,amps,fs,phases,kappa):
        """Physical angle/frequency steady state, including common angle component."""
        out=np.zeros(2*self.n)
        for si,src in enumerate(self.sources):
            residues=self.sign*self.sign[src][None,:]/self.n
            for h in self.hs:
                w=2*np.pi*h*fs[si];den=kappa*self.lam-self.M*w*w/(2*np.pi)+1j*self.D*w/(2*np.pi)
                angle=-np.sum(residues/den[None,:],axis=1)*(-1j)*amps[si]/h*np.exp(1j*(w*t+h*phases[si]))
                out[:self.n]+=angle.real;out[self.n:]+=(1j*w/(2*np.pi)*angle).real
        return out
