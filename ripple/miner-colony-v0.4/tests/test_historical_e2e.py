"""Actual Stratum shares submitted under the historical colony policy."""
import sys,time,tempfile,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_end_to_end import VerifyingPool
from ripple_miner.controller import Controller

class TestHistoricalE2E(unittest.TestCase):
    def test_originally_derived_colony_controls_real_stratum_hashing(self):
        pool=VerifyingPool();pool.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                c=Controller(tmp)
                try:
                    c.start_cpu({'host':'127.0.0.1','port':pool.port,'user':'research.worker',
                                 'password':'x','workers':2,'chunk':150,'tls':False,
                                 'policy':'historical','seconds':3.2})
                    end=time.monotonic()+15
                    while time.monotonic()<end and c.status()['cpu']['state'] not in ('stopped','failed'):
                        time.sleep(.1)
                    state=c.status()['cpu']; self.assertEqual(state['state'],'stopped',str(state))
                    self.assertGreater(state['hashes'],0)
                    self.assertGreater(pool.accepted,0)
                    self.assertIn('done',c.spatial_status()['summary']['counts'])
                    self.assertNotIn('password',json.dumps(c.status()))
                finally:c.close()
        finally:pool.close()