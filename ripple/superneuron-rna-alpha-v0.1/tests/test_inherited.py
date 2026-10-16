import hashlib
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from vendor.charlie_v2.neuron import CharlieNeuron
from superneuron import parse_fasta,benchmark
ROOT=Path(__file__).resolve().parents[1]
class InheritedCharlieTest(unittest.TestCase):
    def test_byte_identical_original_parent(self):
        p=ROOT/'vendor/charlie_v2/neuron.py'
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),'bf96fc4dae90eeee65e3f895207c6c5714f736b1b9dbf09569e1c24a8b440f77')
    def test_original_executable_and_reported(self):
        c=CharlieNeuron()
        for _ in range(30):x=c.step((1.,.9,.15),.05)
        self.assertGreaterEqual(c.count,1)
        self.assertEqual(x['total_events'],c.count)
        rna=parse_fasta((ROOT/'data/RHO_NM_000539.3_mirror.fasta').read_text(),'NM_000539.3')['rna']
        result=benchmark(rna,samples=2,nsteps=140)
        self.assertIn('inherited_charlie_v2',result['controls'])
if __name__=='__main__': unittest.main()