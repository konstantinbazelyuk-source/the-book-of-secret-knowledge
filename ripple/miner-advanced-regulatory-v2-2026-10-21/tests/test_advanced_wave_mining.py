"""Prove that the recovered mixed Regulatory v2 changes actual Bitcoin work."""
import tempfile, sys, unittest, time, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ripple_miner.regulatory_wave import RegulatoryWave, NODE_WORKER
from miner import GENESIS_HEADER, UINT256_MAX, scan_nonces, sha256d
from ripple_miner.spatial import WorkMap

class OriginalMixedWaveform(unittest.TestCase):
    def test_16_executing_mixed_cells_are_not_v01(self):
        with RegulatoryWave(100000, update_every=1) as wave:
            self.assertEqual(wave.kinds.count('lif'),0)
            self.assertEqual(len(wave.kinds),16)
            self.assertEqual(set(wave.kinds),{'delta','daughter','charlie'})
            self.assertTrue(NODE_WORKER.exists())
            old=wave.chunk
            self.assertTrue(wave.observe(hashes=100000,elapsed=.1,active=1,capacity=2))
            self.assertNotEqual(old,wave.chunk)
            self.assertEqual(wave.snapshot()['real_hashes_observed'],100000)
            self.assertEqual(wave.snapshot()['network']['cells'],16)
            self.assertEqual(wave.steps,1)

    def test_dynamic_waveform_chunk_is_actual_nonce_ownership_and_sha256d(self):
        with tempfile.TemporaryDirectory() as temp, RegulatoryWave(2000, update_every=1) as wave:
            workmap=WorkMap(Path(temp)/'nonce.sqlite3')
            try:
                # First real Bitcoin scan done with the inherited source kernel.
                a=workmap.claim('0123456789abcdef'*4,0,'wave-worker',wave.chunk)
                count,rows=scan_nonces(GENESIS_HEADER[:76],a['start'],a['count'],UINT256_MAX,0)
                self.assertEqual(count,2000)
                self.assertEqual(len(rows),count)
                for nonce, digest, is_block in rows:
                    self.assertEqual(digest,sha256d(GENESIS_HEADER[:76]+nonce.to_bytes(4,'little'))[::-1].hex())
                workmap.finish(a['id'],'wave-worker',hashes_done=count,elapsed=.1)
                self.assertTrue(wave.observe(hashes=count,elapsed=.1,active=1,capacity=2))
                self.assertNotEqual(wave.chunk,2000)
                # Next task has a causally changed number of *actual* nonce hashes.
                b=workmap.claim('0123456789abcdef'*4,0,'wave-worker',wave.chunk)
                self.assertEqual(b['count'],wave.chunk)
                self.assertGreaterEqual(b['start'],a['start']+a['count'])
                n,rows2=scan_nonces(GENESIS_HEADER[:76],b['start'],b['count'],UINT256_MAX,0)
                self.assertEqual(n,b['count'])
                workmap.finish(b['id'],'wave-worker',hashes_done=n,elapsed=.1)
                self.assertEqual(workmap.summary()['counts'].get('done'),2)
            finally:workmap.close()

    def test_background_waveform_process_exits_cleanly(self):
        with RegulatoryWave(8000, update_every=2) as wave:
            proc=wave.proc
            self.assertFalse(wave.observe(hashes=200,elapsed=.1,active=1,capacity=1))
            self.assertTrue(wave.observe(hashes=200,elapsed=.1,active=1,capacity=1))
        self.assertIsNotNone(proc.poll())

if __name__=='__main__': unittest.main()

class RealAdvancedWavePoolIntegration(unittest.TestCase):
    def test_original_delta_daughter_charlie_controller_mines_real_pool_shares(self):
        # Local *verifying* Stratum V1 server: actual pool protocol, no money.
        from test_end_to_end import VerifyingPool
        from ripple_miner.controller import Controller
        pool=VerifyingPool();pool.start()
        try:
            with tempfile.TemporaryDirectory() as temp:
                ctl=Controller(temp)
                try:
                    ctl.start_cpu({'host':'127.0.0.1','port':pool.port,'user':'wave.real.hash',
                                   'password':'x','workers':2,'chunk':2400,'tls':False,
                                   'policy':'waveform','seconds':4.0})
                    deadline=time.monotonic()+25
                    while time.monotonic()<deadline and ctl.status()['cpu']['state'] not in ('stopped','failed'):
                        time.sleep(0.15)
                    status=ctl.status()['cpu']
                    self.assertEqual(status['state'],'stopped',str(status))
                    self.assertGreater(status['hashes'],0)
                    self.assertGreater(pool.accepted,0)
                    self.assertGreater(status['accepted'],0)
                    self.assertGreater(status['advanced_waveform']['ticks'],0)
                    self.assertGreater(status['advanced_waveform']['real_hashes_observed'],0)
                    self.assertGreater(len(status['advanced_waveform']['recent_changes']),0)
                finally:ctl.close()
        finally:pool.close()