import json
import sys
from pathlib import Path
import threading
import unittest
import urllib.request
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from superneuron import parse_fasta,synthetic_stimulus
from superneuron_multigene import load_genes,MultiGeneSuperNeuron,evaluate,EXPECTED_NCBI_RNA_SHA256
from serve import make_server
R=Path(__file__).resolve().parents[1]
class MultiGeneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rho=parse_fasta((R/'data/RHO_NM_000539.3_mirror.fasta').read_text(),'NM_000539.3')['rna']
        cls.genes=load_genes(R/'data/ncbi_genes')
    def test_all_real_gene_sequences_pinned(self):
        self.assertEqual(set(self.genes),set(EXPECTED_NCBI_RNA_SHA256))
        self.assertTrue(all(len(s)>=87 for s in self.genes.values()))
    def test_forged_gene_input_rejected(self):
        with self.assertRaises(ValueError):
            MultiGeneSuperNeuron(self.rho,{'GNAT2':'ACGU'*30})
    def test_all_145_new_loci_causally_connected(self):
        r=evaluate(self.rho,self.genes,nsteps=140)
        self.assertEqual(r['actual_evaluations'],154)
        self.assertTrue(r['all_added_loci_causal'])
        self.assertEqual(sum(x['total'] for x in r['individual_locus_ablation'].values()),145)
        self.assertTrue(all(x['max_abs_state_difference']>1e-10 for x in r['gene_family_ablation'].values()))
    def test_recovery_path_acts_on_energy(self):
        samples=[(1.,1.,1.)]*500
        a=MultiGeneSuperNeuron(self.rho,self.genes);b=MultiGeneSuperNeuron(self.rho,self.genes,knockout_gene='RPE65')
        for x in samples:ra=a.step(x);rb=b.step(x)
        self.assertNotEqual(ra['energy'],rb['energy'])
    def test_full_six_gene_dashboard_executes(self):
        server=make_server(self.rho,port=0,genes=self.genes)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        root=f'http://127.0.0.1:{server.server_port}'
        try:
            with urllib.request.urlopen(root+'/api/state',timeout=2) as r:initial=json.load(r)
            self.assertEqual(initial['loci'],174)
            payload=json.dumps({'rgb':[.7,.5,.3],'steps':25}).encode()
            with urllib.request.urlopen(urllib.request.Request(root+'/api/step',data=payload,headers={'Content-Type':'application/json'}),timeout=2) as r:v=json.load(r)
            self.assertEqual(v['gene_count'],6)
            self.assertEqual(set(v['gene_values']),set(self.genes))
            self.assertGreater(v['t'],0)
        finally:server.shutdown();server.server_close();thread.join()
if __name__=='__main__':unittest.main()
