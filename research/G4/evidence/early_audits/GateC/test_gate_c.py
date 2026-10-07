import unittest,json
from pathlib import Path
import numpy as np,pandas as pd
import run_gate_c as g
P=Path(__file__).parent
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.result=json.loads((P/'GATE_C_RESULTS.json').read_text())
 def test_full_trace_inventory(self):
  self.assertEqual(len(list((P/'traces').glob('*.npz'))),9)
 def test_energy_domain_and_conservation(self):
  for m in self.result['physical_cases']:
   self.assertGreaterEqual(m['energy_min_MWs'],-1e-9)
   self.assertLessEqual(m['energy_max_MWs'],m['capacity_MWs']+1e-9)
   self.assertLess(m['energy_balance_max_MWs'],1e-8)
 def test_power_and_slew(self):
  for m in self.result['physical_cases']:
   self.assertLessEqual(m['max_charge_MW'],g.PMAX+1e-9);self.assertLessEqual(m['max_discharge_MW'],g.PMAX+1e-9)
   self.assertLessEqual(m['max_buffer_slew_MW_per_s'],m['buffer_slew_bound_MW_per_s']*(1+1e-6));self.assertGreater(m['min_PCC_MW'],0.)
 def test_grid_equivalence(self):
  self.assertLess(self.result['max_PMU_equivalence_error_Hz'],1e-10)
 def test_contraction_bound(self):
  for m in self.result['physical_cases']:
   self.assertGreater(m['period_contraction_bound'],0);self.assertLess(m['period_contraction_bound'],1)
   self.assertLessEqual(m['state_gap_end_MWs'],m['initial_difference_end_bound_MWs']+1e-7)
   self.assertLessEqual(m['max_state_gap_increase_MWs'],1e-7)
 def test_hard_map_fixed_after_one_cycle(self):
  d=pd.read_csv(P/'hard_comparator.csv');np.testing.assert_allclose(d.E_after_one,d.E_after_two,atol=1e-12)
 def test_extra_bits_and_margins(self):
  d=pd.read_csv(P/'extra_bit_witnesses.csv')
  self.assertTrue((d.energy_bit_world_A!=d.energy_bit_world_B).all());self.assertTrue((d.PCC_bit_world_A!=d.PCC_bit_world_B).all())
  self.assertGreater(d.PCC_bit_margin_MW.min(),.1)
  self.assertTrue(d.total_energy_initial_same.all());self.assertTrue(d.unlabelled_energy_multiset_same.all())
 def test_state_derivative(self):
  C=2.;Es=.05*C
  for u in [8.,9.,11.,12.]:
   for e in [.1,.5,1.,1.9]:
    h=1e-6
    def f(x):
     c,d,_=g.control(u,np.array([x]),C);return (g.ETA*c-d/g.ETA)[0]
    num=(f(e+h)-f(e-h))/(2*h);dc=min(max(u-g.PREF,0),3);cc=min(max(g.PREF-u,0),3)
    ana=-dc*Es/(g.ETA*(e+Es)**2)-g.ETA*cc*Es/(C-e+Es)**2
    self.assertAlmostEqual(num,ana,places=7)
 def test_initial_gap_power_budget(self):
  for m in self.result['physical_cases']:
   tag=f"f{m['frequency_Hz']:g}_cap{m['cap_ratio']:g}";d=np.load(P/'traces'/(tag+'.npz'));t=d['time_s'];p=d['PCC_MW'];E=d['energy_MWs'];gap=E[:,1]-E[:,0]
   self.assertGreaterEqual(float(gap.min()),-1e-7);self.assertGreaterEqual(float((p[:,0]-p[:,1]).min()),-1e-7)
   area=np.trapezoid(abs(p[:,0]-p[:,1]),t)
   self.assertLessEqual(area,m['state_gap_initial_MWs']/g.ETA+1e-3)
 def test_declared_source_classes(self):
  d=pd.read_csv(P/'source_class_windows.csv');self.assertEqual(int(d.classes_differ.sum()),9)
  self.assertFalse(d[d.first_cycle==195].classes_differ.any())
 def test_numerical_sentinel(self):
  d=self.result['numerical_sentinel'];self.assertLess(d['max_PCC_difference_MW'],1e-6);self.assertLess(d['max_PMU_difference_Hz'],1e-7)
if __name__=='__main__':unittest.main()
