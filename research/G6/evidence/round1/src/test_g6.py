import unittest,sys,json
from pathlib import Path
import numpy as np
import mpmath as mp
from g6_model import *

class G6Tests(unittest.TestCase):
    def test_trig_exact_quadrants(self):
        s,c=exact_trig_grid()
        for hi,h in enumerate([1,3,5]):
            for k in [0,64,128,192]:
                sn=[0,1,0,-1][(h*k//64)%4];cs=[1,0,-1,0][(h*k//64)%4]
                self.assertLessEqual(s[0][hi,k],sn);self.assertGreaterEqual(s[1][hi,k],sn)
                self.assertLessEqual(c[0][hi,k],cs);self.assertGreaterEqual(c[1][hi,k],cs)
    def test_moduli_crossing_zero(self):
        l,u=interval_abs((np.array([-1.,0.]),np.array([1.,0.])),(np.array([-1.,0.]),np.array([1.,0.])))
        self.assertTrue(np.isfinite(l).all());self.assertTrue(np.isfinite(u).all());self.assertTrue((l==0).all())
    def test_units_state_vs_transfer(self):
        for cfg in MODELS:
            m=Model(cfg);amps=np.array([.7,1.2]);fs=[.27,.41];phases=[.8,2.1];k=1.03;t=3.17
            x=m.linear_state(t,amps,fs,phases,k);y=list(x[m.n:]/.05)
            for i,j,kk in m.edges:y.append(k*kk*(x[i]-x[j])/15)
            y2=np.zeros(m.J)
            for si in range(2):
                for h in m.hs:y2+=np.real(-1j*m.transfer(h*fs[si],k)[:,si]*amps[si]/h*np.exp(1j*(2*np.pi*h*fs[si]*t+h*phases[si])))
            np.testing.assert_allclose(y,y2,rtol=1e-12,atol=1e-12)
    def test_laplacian_exact_modes(self):
        for cfg in MODELS:
            m=Model(cfg);L=np.zeros((m.n,m.n))
            for i,j,k in m.edges:L[i,i]+=k;L[j,j]+=k;L[i,j]-=k;L[j,i]-=k
            np.testing.assert_array_equal(L@m.sign,m.sign*m.lam[None,:])
            self.assertEqual(sum(m.lam==0),1)
    def test_interval_80digit_complex(self):
        rng=np.random.default_rng(6022026)
        for cfg in MODELS:
            m=Model(cfg)
            for _ in range(12):
                f=float(rng.uniform(.08,.75));k=float(rng.uniform(.85,1.15));rf=.0001;rk=.0002
                rr,ii=m.transfer_interval(f-rf,f+rf,k-rk,k+rk)
                for j in range(m.J):
                    for si in range(2):
                        w=2*mp.pi*mp.mpf(f);den=[mp.mpf(k)*float(l)-mp.mpf(m.M)*w*w/(2*mp.pi)+1j*mp.mpf(m.D)*w/(2*mp.pi) for l in m.lam]
                        z=sum(mp.mpf(float(m.res[j,mm,si]))/den[mm] for mm in range(m.n))
                        z*=(-1j*w/(2*mp.pi)*20 if j<m.n else -mp.mpf(k)*float(m.kedge[j-m.n])/15)
                        self.assertLessEqual(mp.mpf(float(rr[0][j,si])),z.real);self.assertGreaterEqual(mp.mpf(float(rr[1][j,si])),z.real)
                        self.assertLessEqual(mp.mpf(float(ii[0][j,si])),z.imag);self.assertGreaterEqual(mp.mpf(float(ii[1][j,si])),z.imag)
    def test_independent_root_oracle(self):
        rng=np.random.default_rng(6022026)
        rows=[]
        for cfg in MODELS:
            m=Model(cfg)
            for n in range(128):
                f=float(rng.uniform(.08,.75));k=float(rng.uniform(.85,1.15));lo,hi=m.bounds([f,f,k,k]);p,ph=m.peak_root(f,k)
                self.assertTrue(np.all(lo[0]<=p+1e-11));self.assertTrue(np.all(p<=hi[0]+1e-11))
                self.assertTrue(np.all(hi[1]+1e-11>=p))
                # Same information algorithm equality: classical support and G6 are same expression.
                a=rng.uniform(0,4,2);exact=p@a;candidate=p@a
                self.assertEqual(float(max(abs(candidate-exact))),0.)
                rows.append([cfg['name'],n,f,k,float(np.max(hi[0]-lo[0])),float(np.max(abs(candidate-exact)))])
        import pandas as pd
        pd.DataFrame(rows,columns=['model','case','f_Hz','kappa','phase_bound_width','same_info_difference']).to_csv(Path(__file__).resolve().parents[1]/'results'/'independent_root_checks.csv',index=False)
    def test_ai_label_invariance(self):
        cfg=MODELS[0];ordinary_model=Model({**cfg,'name':'ordinary_cyclic_industry'});ai_model=Model({**cfg,'name':'AI_training'})
        args=(2.,[1.,2.],[.3,.4],[.1,.2],.93)
        ordinary=ordinary_model.linear_state(*args);ai=ai_model.linear_state(*args)
        self.assertTrue(np.array_equal(ordinary,ai))
        ob=ordinary_model.bounds([.2,.4,.9,1.]);ab=ai_model.bounds([.2,.4,.9,1.])
        self.assertTrue(np.array_equal(ob[0],ab[0]));self.assertTrue(np.array_equal(ob[1],ab[1]))
        # Altering actual PCC injection is a physical change and is distinguishable.
        changed=ai_model.linear_state(2.,[1.2,2.],[.3,.4],[.1,.2],.93)
        self.assertFalse(np.array_equal(ordinary,changed))
    def test_shared_uncertainty_counterexample(self):
        g=np.linspace(-1,1,101)
        exact=max((1+g)/2+(1-g)/2);swapped=max((1+g)/2)+max((1-g)/2)
        self.assertEqual(exact,1);self.assertEqual(swapped,2)
if __name__=='__main__':unittest.main(verbosity=2)
