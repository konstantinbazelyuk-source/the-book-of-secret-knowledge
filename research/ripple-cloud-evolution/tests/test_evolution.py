import hashlib
import math
import unittest
from pathlib import Path
from ripple_evo.evolution import Genome, EvolvingColonyTwin,scenario,simulate,loss,evaluate,mutate,evolve
from legacy.ripple_optical_agent_LOCKED import RippleNeuron

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/mnt/data/Ripple_SpiderScan_Digital_Avatar_Alpha_v1_1/legacy/ripple_optical_agent_LOCKED.py')
class TestEvo(unittest.TestCase):
    def test_locked_neuron(self):
        self.assertEqual(hashlib.sha256((ROOT/'legacy/ripple_optical_agent_LOCKED.py').read_bytes()).hexdigest(),'7f2f611cd8f1717c3d3dcae745dbd41efc37e24315d93878231db52eaf614f77')
    def test_locked_motor(self):
        self.assertEqual(hashlib.sha256((ROOT/'legacy/digital_motor_v11_LOCKED.py').read_bytes()).hexdigest(),'cce5ce28199475d8f9b063c8eb5861c5e8de02da67a1bb37df12b6d54dbad8a4')
    def test_bounds(self):
        with self.assertRaises(ValueError):Genome(duty=.99).check()
    def test_evo_kinematics(self):
        m=simulate(Genome(),scenario(1),duration_s=.20)
        self.assertEqual(m['motor_count'],24)
        self.assertEqual(m['leg_count'],8)
        self.assertEqual(m['ik_failures'],0)
    def test_neuron_steps(self):
        t=EvolvingColonyTwin(Genome(gain=.25),.075,3.0)
        for _ in range(30):t.tick()
        self.assertEqual(len(t.nodes),8)
        self.assertGreater(t.nodes[0].t,1.)
        self.assertTrue(all(math.isfinite(n.theta) for n in t.nodes))
        self.assertGreaterEqual(t.neuron_spikes,0)
    def test_determinism(self):self.assertEqual(scenario(22),scenario(22))
    def test_mutation_bounds(self):
        import random
        rng=random.Random(27)
        for _ in range(100):mutate(Genome(),rng).check()
    def test_slow_penalty(self):
        normal={'duration_s':6,'command_distance_proxy_mm':200,'rms_toe_error_mm':4,'rate_limit_hits':1,'support_proxy_loss_frames':0,'ik_failures':0}
        slow={**normal,'command_distance_proxy_mm':10}
        self.assertGreater(loss(slow),loss(normal))
    def test_selection_reproducible(self):
        x=evolve(seed=42,population=4,generations=2,train_n=1,holdout_n=1)
        y=evolve(seed=42,population=4,generations=2,train_n=1,holdout_n=1)
        self.assertEqual(x['best_candidate'],y['best_candidate'])
    def test_disjoint_seed_labels(self):self.assertNotEqual(scenario(1,'train'),scenario(1,'holdout'))
    def test_holdout(self):
        r=evolve(seed=6,population=3,generations=1,train_n=1,holdout_n=2)
        self.assertEqual(r['holdout_comparison']['candidate']['scenario_count'],2)
        self.assertIsInstance(r['promotion_gate_passed'],bool)

if __name__=='__main__':unittest.main()
