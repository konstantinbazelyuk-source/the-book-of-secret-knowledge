"""Real remote-worker hashing and integration against locally verifying Stratum pool."""
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ripple_miner.controller import Controller
from ripple_miner.remote import RemoteServer
from ripple_miner.spatial import WorkMap
from test_end_to_end import VerifyingPool

class DistributedEndToEndTests(unittest.TestCase):
    def test_local_cpu_and_remote_worker_contribute_real_pool_shares(self):
        token='integration-token-for-test-32-characters'
        agent=RemoteServer(('127.0.0.1',0),token)
        server_thread=threading.Thread(target=agent.serve_forever,daemon=True)
        server_thread.start()
        pool=VerifyingPool();pool.start()
        with tempfile.TemporaryDirectory() as tmp:
            c=Controller(tmp)
            try:
                c.start_cpu({'host':'127.0.0.1','port':pool.port,'user':'worker.test',
                  'password':'x','workers':1,'chunk':150,'seconds':3,'tls':False,
                  'remote_url':'http://127.0.0.1:'+str(agent.server_port),
                  'remote_token':token})
                stop=time.monotonic()+14
                while time.monotonic()<stop:
                    state=c.status()['cpu']
                    if state['state'] in ('stopped','failed'):break
                    time.sleep(.1)
                state=c.status()['cpu']
                self.assertEqual(state['state'],'stopped',str(state))
                self.assertGreater(state['accepted'],0)
                self.assertGreater(pool.accepted,0)
                data=c.spatial_status()
                self.assertGreater(data['summary']['verified_completed_hashes'],0)
                self.assertIn('remote-0',{x['worker'] for x in data['cells']})
                self.assertNotIn(token,str(state))
            finally:c.close()
        pool.close();agent.shutdown();agent.server_close();server_thread.join(3)
