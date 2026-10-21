"""Functional proof of real +/- signed-wave nonce work, never fake hashes."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from miner import GENESIS_HEADER, UINT256_MAX, sha256d, scan_nonces, Work, header_prefix
from ripple_miner.spatial import WorkMap
from ripple_miner.spike_axes import SpikeAxisDispatch
from ripple_miner.regulatory_wave import RegulatoryWave


class WaveAxisTests(unittest.TestCase):
    def test_all_six_signed_positions_modify_real_work_preset(self):
        planner=SpikeAxisDispatch(2000, 1)
        planner.wave_update({'average_membrane':.2,'feature_norm':.25})
        for a,b,want_sign in ((.22,.25,1),(.29,.25,1),(.45,.25,1),(.43,.25,-1),(.36,.25,-1),(.19,.25,-1)):
            n=planner.wave_update({'average_membrane':a,'feature_norm':b})
            self.assertEqual(1 if n>0 else -1,want_sign)
            self.assertTrue(1<=abs(n)<=3)
        planner.phase=1; planner.level=3
        self.assertEqual(planner._lane_batch(planner.axes[0],2000),4000)
        self.assertEqual(planner._lane_batch(planner.axes[1],2000),1000)

    def test_distinct_preset_axes_execute_actual_sha256d_and_conserve_ownership(self):
        key='def456' * 12
        with tempfile.TemporaryDirectory() as d:
            wm=WorkMap(Path(d)/'work.sqlite3')
            p=SpikeAxisDispatch(40,1)
            p.level=3
            try:
                first=p.dispatch(wm,key,'cpu-0',40)
                second=p.dispatch(wm,key,'cpu-1',40)
                self.assertIsNotNone(first)
                self.assertIsNotNone(second)
                self.assertNotEqual(first[0]['en2'], second[0]['en2'])
                self.assertEqual({first[1],second[1]},{'positive','negative'})
                seen=set()
                work=Work('a','00'*32,'00'*4,'00'*4,(), '20000000','5f5e1000','1d00ffff',True,'0001',1,'1')
                for cell,lane in (first,second):
                    # Original hash kernel; same prefix within a stream, but
                    # distinct valid 76-byte Bitcoin headers across streams.
                    prefix=p.prefix(work,cell,header_prefix)
                    n,rows=scan_nonces(prefix,cell['start'],cell['count'],UINT256_MAX,0)
                    self.assertEqual(n,cell['count'])
                    self.assertEqual(len(rows),n)
                    self.assertEqual(rows[0][1],sha256d(prefix+cell['start'].to_bytes(4,'little'))[::-1].hex())
                    self.assertFalse(any((cell['en2'],k) in seen for k in range(cell['start'],cell['start']+n)))
                    seen.update((cell['en2'],k) for k in range(cell['start'],cell['start']+n))
                    wm.finish(cell['id'],'cpu-0' if lane=='positive' else 'cpu-1',hashes_done=n,elapsed=.05)
                self.assertEqual(len(seen),first[0]['count']+second[0]['count'])
                self.assertEqual(wm.summary()['verified_completed_hashes'],len(seen))
                self.assertEqual(p.snapshot()['dispatched'],2)
                # The two valid extranonce2 streams select distinct pool headers.
                pa=p.prefix(work,first[0],header_prefix)
                pb=p.prefix(work,second[0],header_prefix)
                self.assertEqual(len(pa),76); self.assertNotEqual(pa,pb)
                self.assertEqual(pa,p.prefix(work,first[0],header_prefix))
            finally:
                wm.close()

    def test_genuine_advanced_ripple_transition_updates_axis_policy(self):
        p=SpikeAxisDispatch(3000,1)
        with RegulatoryWave(3000,update_every=1) as wave:
            positions=[]
            for i in range(9):
                wave.observe(hashes=3000,elapsed=.05+i%3*.02,active=i%3,capacity=3)
                positions.append(p.wave_update(wave.last_network))
            self.assertEqual(wave.kinds.count('lif'),0)
            self.assertEqual(len(wave.kinds),16)
            self.assertTrue(any(x>0 for x in positions))
            self.assertTrue(any(x<0 for x in positions))
            self.assertEqual(p.tick,8)

    def test_max_extranonce_exhaustion_is_real_not_wrapped(self):
        with tempfile.TemporaryDirectory() as d:
            wm=WorkMap(Path(d)/'work.sqlite3')
            p=SpikeAxisDispatch(300,1)
            key='abcde'*14
            try:
                p.axes[0].en2=256
                p.axes[1].en2=255
                self.assertIsNotNone(p.dispatch(wm,key,'a',300))
                p.axes[1].en2=257
                self.assertIsNone(p.dispatch(wm,key,'b',300))
            finally:wm.close()

if __name__=='__main__':unittest.main()