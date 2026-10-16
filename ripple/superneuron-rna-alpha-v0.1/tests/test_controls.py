import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import unittest
import superneuron as sn

D=Path(__file__).resolve().parents[1]/'data/RHO_NM_000539.3_mirror.fasta'

class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rna=sn.parse_fasta(D.read_text(), 'NM_000539.3')['rna']
    def test_29_loci_have_causal_membrane_effect(self):
        r=sn.benchmark(self.rna,samples=7,nsteps=400)
        self.assertTrue(r['all_regulators_have_nonzero_numerical_effect'])
        self.assertTrue(all(x['max_abs_membrane_voltage_change']>1e-14 for x in r['regulator_ablation'].values()))
    def test_energy_limits_firing_under_overload(self):
        n=sn.SuperNeuron(self.rna)
        samples=[n.step((1.,1.,1.)) for _ in range(3000)]
        self.assertLess(min(x['energy'] for x in samples),.10)
        self.assertTrue(any(not x['spike'] and x['energy']<.10 for x in samples))
    def test_reversible_state_initialization(self):
        a=sn.SuperNeuron(self.rna);b=sn.SuperNeuron(self.rna)
        x=sn.synthetic_stimulus(400)
        self.assertEqual([a.step(v)['spike'] for v in x],[b.step(v)['spike'] for v in x])
    def test_synthetic_is_not_physical_data(self):
        r=sn.benchmark(self.rna,samples=3,nsteps=120)
        self.assertEqual(r['status'],'EXECUTED_SYNTHETIC_SOFTWARE')
        self.assertTrue(r['no_biological_fitness_or_intelligence_metric'])
if __name__=='__main__':unittest.main()
