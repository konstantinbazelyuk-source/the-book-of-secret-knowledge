"""Live controller -> pool -> masters -> descendants -> verified shares."""
import json,sys,tempfile,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_end_to_end import VerifyingPool
from ripple_miner.controller import Controller

class TestReplicatingMinerE2E(unittest.TestCase):
    def test_replicating_sha256d_and_real_pool_acceptance(self):
        pool=VerifyingPool();pool.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                c=Controller(tmp)
                try:
                    c.start_cpu({'host':'127.0.0.1','port':pool.port,'user':'ripple.clone.test',
                        'password':'x','workers':3,'chunk':2400,'tls':False,
                        'policy':'replicating','seconds':5.1})
                    deadline=time.monotonic()+25
                    while time.monotonic()<deadline and c.status()['cpu']['state'] not in ('stopped','failed'):
                        time.sleep(.1)
                    info=c.status()['cpu']
                    self.assertEqual(info['state'],'stopped',str(info))
                    self.assertGreater(info['hashes'],0)
                    self.assertGreater(pool.accepted,0)
                    self.assertGreater(info['accepted'],0)
                    self.assertIn('replication',info)
                    self.assertGreater(info['replication']['births'],0)
                    self.assertEqual(info['replication']['unabsorbed_assignments'],0)
                    self.assertIn('done',c.spatial_status()['summary']['counts'])
                    self.assertNotIn('password',json.dumps(c.status()))
                finally:c.close()
        finally:pool.close()