import hashlib,math,unittest
from pathlib import Path
from ripple_evo.pareto import *
from ripple_evo.evolution import Genome
ROOT=Path(__file__).resolve().parents[1]
LOCKED={
'legacy/ripple_optical_agent_LOCKED.py':'7f2f611cd8f1717c3d3dcae745dbd41efc37e24315d93878231db52eaf614f77',
'legacy/approved_kinematics_v06.py':'aef18eba0520dde2e80a80d9c1e5f774bf4c355d60d879404108d21a881a4561',
'legacy/digital_motor_v11_LOCKED.py':'cce5ce28199475d8f9b063c8eb5861c5e8de02da67a1bb37df12b6d54dbad8a4'}
class ParetoTests(unittest.TestCase):
 def test_locked_sha(self):
  for f,sha in LOCKED.items():self.assertEqual(hashlib.sha256((ROOT/f).read_bytes()).hexdigest(),sha)
 def test_splits_independent(self):self.assertNotEqual(stress_scenarios(2,split='train'),stress_scenarios(2,split='holdout'))
 def test_performance_real_numbers(self):
  d=describe(Genome(),stress_scenarios(2),duration_s=.4)
  self.assertTrue(math.isfinite(d['mean_toe_error_mm']))
  self.assertEqual(d['n_scenarios'],2)
 def test_domination(self):
  a={'objectives_minimize':(1.,-30.,0.,0.),'total_ik_failures':0,'mean_commanded_speed_mm_s':30.,'total_support_proxy_loss_frames':0,'n_scenarios':1}
  b={**a,'objectives_minimize':(2.,-20.,1.,0.),'mean_commanded_speed_mm_s':20.}
  self.assertTrue(dominates(a,b));self.assertFalse(dominates(b,a))
 def test_infeasible_rejected(self):
  b={'objectives_minimize':(1.,-19.,0.,0.),'total_ik_failures':0,'mean_commanded_speed_mm_s':19.,'total_support_proxy_loss_frames':0,'n_scenarios':1}
  a={**b,'objectives_minimize':(5.,-30.,0.,0.),'mean_commanded_speed_mm_s':30.}
  self.assertTrue(dominates(a,b))
 def test_pareto_fronts(self):
  d={k:{'objectives_minimize':v,'total_ik_failures':0,'mean_commanded_speed_mm_s':30.,'total_support_proxy_loss_frames':0,'n_scenarios':1}
   for k,v in [('a',(1.,-30.,0.,0.)),('b',(2.,-31.,1.,0.)),('c',(3.,-29.,2.,0.))]}
  self.assertEqual(set(nondominated_fronts(['a','b','c'],d)[0]),{'a','b'})
 def test_archive_deterministic(self):
  a=evolve_pareto(seed=99,population=4,generations=2,train_n=2,holdout_n=2)
  b=evolve_pareto(seed=99,population=4,generations=2,train_n=2,holdout_n=2)
  self.assertEqual(a['policies'],b['policies'])
 def test_policies_provenance(self):
  a=evolve_pareto(seed=91,population=4,generations=1,train_n=2,holdout_n=2)
  self.assertEqual(set(a['policies']),{'baseline','previous_v1_2','precision','throughput'})
  self.assertTrue(all(x['holdout']['zero_ground_truth'] for x in a['policies'].values()))
 def test_mutate_bounds(self):
  r=random.Random(2);g=Genome()
  for i in range(100):g=mutate(g,r);g.check()
 def test_train_not_holdout(self):
  a=evolve_pareto(seed=11,population=4,generations=1,train_n=2,holdout_n=2)
  b=evolve_pareto(seed=11,population=4,generations=1,train_n=2,holdout_n=5)
  self.assertEqual(a['policies']['precision']['genome'],b['policies']['precision']['genome'])
 def test_rejected_fast_policy_cannot_be_deployed(self):
  a=evolve_pareto(seed=20261013,population=18,generations=6,train_n=6,holdout_n=16)
  self.assertFalse(a['policies']['throughput']['hardware_deployment_authorized'])
  self.assertIn(a['policies']['throughput']['release_gate'],('REJECTED_HOLDOUT_PROXY_GATE','PASS_SIMULATION_PROXY_GATE'))
 def test_stress_case_percentage(self):
  a=describe(Genome(),stress_scenarios(3),duration_s=.4)
  self.assertTrue(0<=a['proxy_stress_cases_pct']<=100)
  self.assertTrue(0<=a['proxy_stress_cases_passed']<=3)
 def test_data_finite(self):
  a=evolve_pareto(seed=19,population=4,generations=1,train_n=2,holdout_n=3)
  for p in a['policies'].values():
   for v in p['holdout']['objectives_minimize']:self.assertTrue(math.isfinite(v))
if __name__=='__main__':unittest.main()