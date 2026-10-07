"""Independent finite QA supplements, but does not replace, analytic reduction."""
import json, unittest
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from robust_filter import env_free, Hresp, G
from validate_continuous import validate,stationary_lags,g
ROOT=Path(__file__).resolve().parent

class FeedbackTest(unittest.TestCase):
 def test_phase_envelope(self):
  rng=np.random.default_rng(19371)
  for _ in range(100):
   p=int(rng.integers(1,3));lo=float(rng.uniform(0,4.9));hi=float(rng.uniform(lo,5));ts=rng.uniform(0,20,80)
   lower,upper=env_free(ts,p,lo,hi)
   for a in np.linspace(lo,hi,101):
    y=p*G(ts)+(3-2*p)*Hresp(ts-a)
    self.assertLessEqual(float(np.max(y-upper)),2e-13);self.assertLessEqual(float(np.max(lower-y)),2e-13)
 def test_phase_kinks_included(self):
  for k in [0,5,10,15,20]:self.assertIn(k,stationary_lags())
 def test_power_nonanticipativity(self):
  rows=json.loads((ROOT/'robust_policy.json').read_text())
  for p in [1,2]:
   rs=[r for r in rows if r['p0']==p]
   for k in range(30):
    commands=[r['us'][k+1] for r in rs if r['bin']>=k]
    self.assertEqual(max(commands),min(commands))
 def test_frequency_nonanticipativity(self):
  for eta in [.005,.01,.02,.05]:
   rows=json.loads((ROOT/f'frequency_policy_eta_{eta:g}.json').read_text())
   for p in [1,2]:
    for k in range(30):
     commands=[r['us'][k+1] for r in rows if r['p0']==p and r['detection']>k]
     self.assertEqual(max(commands),min(commands))
 def test_frequency_interval_coverage(self):
  rng=np.random.default_rng(193)
  for eta in [.005,.01,.02,.05]:
   tau=brentq(lambda t:t*np.exp(-t)-2*eta,0,1)
   phases=np.r_[0.,5.,np.arange(0,5.01,.1),rng.uniform(0,5,100)]
   for a in phases:
    for pattern in range(4):
     found=False
     for k in range(1,54):
      t=k*.1;noise=[eta,-eta,eta*(-1)**k,rng.uniform(-eta,eta)][pattern]
      residual=g(t-a)+noise
      if residual>eta+1e-14:
       lo=max(0.,(k-1)*.1-tau);hi=min(5.,k*.1)
       self.assertGreaterEqual(a,lo-2e-12);self.assertLessEqual(a,hi+2e-12);found=True;break
      else:self.assertGreaterEqual(a,max(0.,t-tau)-2e-12)
     self.assertTrue(found)
 def test_continuous_bounds_against_bruteforce(self):
  rng=np.random.default_rng(45)
  sets=[json.loads((ROOT/'robust_policy.json').read_text()),json.loads((ROOT/'frequency_policy_eta_0.05.json').read_text()),json.loads((ROOT/'no_feedback_policy.json').read_text())]
  for rows in sets:
   for i in rng.choice(len(rows),min(10,len(rows)),replace=False):
    row=rows[int(i)];v=validate(row);lo,hi=v['phase_edge_interval'];ts=np.linspace(0,20,10001)
    cc=np.zeros_like(ts)
    for a,u in v['control_events']:cc+=u*G(ts-a)
    for a in np.linspace(lo,hi,21):
     yy=row['p0']*G(ts)+(3-2*row['p0'])*Hresp(ts-a)+cc
     self.assertLessEqual(float(np.max(yy)),v['max_y'][0]+5e-13)
     self.assertGreaterEqual(float(np.min(yy)),v['min_y'][0]-5e-13)
 def test_common_resources_and_terminal(self):
  paths=[ROOT/'continuous_results.json',ROOT/'no_feedback_validation.json']+[ROOT/f'frequency_validation_eta_{e:g}.json' for e in [.005,.01,.02,.05]]
  for path in paths:
   data=json.loads(path.read_text());rows=data['bins'] if isinstance(data,dict) else data
   e0=max(r['zmax'] for r in rows);E=e0-min(r['zmin'] for r in rows)
   for r in rows:
    self.assertLess(r['max_abs_y'],.6);self.assertLess(r['max_abs_u'],.5);self.assertLess(r['terminal_residual'],1e-14)
    self.assertGreaterEqual(e0-r['zmax'],-1e-14);self.assertLessEqual(e0-r['zmin'],E+1e-14)
if __name__=='__main__':unittest.main(verbosity=2)
