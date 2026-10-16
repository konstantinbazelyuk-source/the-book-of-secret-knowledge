import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import unittest
import superneuron as sn

FASTA=Path(__file__).resolve().parents[1]/'data/RHO_NM_000539.3_mirror.fasta'

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.parsed=sn.parse_fasta(FASTA.read_text(),'NM_000539.3')
    def test_rho_has_real_refseq_mirror_header(self):
        self.assertEqual(self.parsed['bases'],2768)
        self.assertEqual(self.parsed['sha256'],'b7f4dbb8b20975eab3ea535177e97ad0b3beab7b99e2aec4f98eb2af5bb89db3')
    def test_no_fake_gene_default(self):
        with self.assertRaises(ValueError):sn.parse_fasta('ACG'*100,'NM_000539.3')
        with self.assertRaises(ValueError):sn.parse_fasta('>not-human\n'+'ACG'*100,'NM_000539.3')
    def test_four_power_29(self):
        self.assertGreater(sn.SEARCH_SPACE,10**17)
        for n in [0,1,1234550,sn.SEARCH_SPACE-1]:self.assertEqual(sn.encode_base4(sn.decode_base4(n)),n)
    def test_rgb_input(self):
        self.assertEqual(sn.rgb_features((0,0,0))['Y'],0)
        with self.assertRaises(ValueError):sn.rgb_features((1.1,.2,.1))
    def test_zero_input_is_quiet(self):
        s=sn.SuperNeuron(self.parsed['rna'])
        for _ in range(50):self.assertFalse(s.step((0,0,0))['spike'])
    def test_real_dynamic_response(self):
        n=sn.SuperNeuron(self.parsed['rna']);trace=[n.step(x) for x in sn.synthetic_stimulus()]
        self.assertGreater(max(x['gene_signal'] for x in trace)-min(x['gene_signal'] for x in trace),.01)
        self.assertGreater(max(x['drive'] for x in trace)-min(x['drive'] for x in trace),.1)
        self.assertTrue(any(x['spike'] for x in trace))
        self.assertGreater(max(x['energy'] for x in trace)-min(x['energy'] for x in trace),.001)
    def test_all_29_loci_actually_connected(self):
        r=sn.benchmark(self.parsed['rna'],samples=12,nsteps=240)
        self.assertTrue(r['all_regulators_have_nonzero_numerical_effect'])
        self.assertEqual(len(r['regulator_ablation']),29)
        self.assertEqual(r['simulated_candidate_genotypes'],12)
        self.assertEqual(r['population_evaluations'],45)
    def test_mode_difference(self):
        r=sn.benchmark(self.parsed['rna'],samples=2,nsteps=180)
        self.assertNotEqual(r['original']['mean_voltage'],r['controls']['lif']['mean_voltage'])
    def test_sequence_change_affects_behavior(self):
        seq=list(self.parsed['rna']);p=(self.parsed['bases'])//(2*29)
        seq[p]=next(x for x in 'ACGU' if x!=seq[p]);seq=''.join(seq)
        self.assertNotEqual(sn.locus_template(seq),sn.locus_template(self.parsed['rna']))
        src=sn.run_trial(self.parsed['rna'],sn.synthetic_stimulus(140))
        var=sn.run_trial(seq,sn.synthetic_stimulus(140))
        self.assertNotEqual(src['mean_gene_signal'],var['mean_gene_signal'])

if __name__=='__main__':unittest.main()
