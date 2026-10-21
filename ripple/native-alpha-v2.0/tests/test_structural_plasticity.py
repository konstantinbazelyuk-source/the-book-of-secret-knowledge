"""Integration tests: locked Ripple neuron with activity-driven graph remodeling."""
import tempfile
import unittest
from ripple_native.jobs import execute, validate_job

class CheckStructuralPlasticity(unittest.TestCase):
    def test_job_input_limits(self):
        for params in ({'frames':1},{'nodes':100},{'nodes':32,'frames':12000},
                       {'dt':0},{'seed':-1},{'plasticity':'yes'}):
            with self.subTest(params=params), self.assertRaises(ValueError):
                validate_job('structural_plasticity',params)

    def test_real_scheduler_job_function(self):
        with tempfile.TemporaryDirectory() as tmp:
            changed=execute('structural_plasticity',{},tmp)
            frozen=execute('structural_plasticity',{'plasticity':False},tmp)
        self.assertTrue(changed['actual_execution'])
        self.assertTrue(changed['simulated_data'])
        self.assertEqual(changed['output']['kernel'],'locked-Ripple-v0.1')
        self.assertGreater(changed['output']['topology_events']['grown'],0)
        self.assertGreater(changed['output']['topology_events']['pruned'],0)
        self.assertEqual(frozen['output']['final_edges'],frozen['output']['initial_edges'])
        self.assertNotEqual(changed['output']['per_neuron_spikes'],frozen['output']['per_neuron_spikes'])

if __name__=='__main__':unittest.main()
