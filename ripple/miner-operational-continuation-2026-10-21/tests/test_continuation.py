"""Additional real hashing + workload teardown tests for continued Ripple development."""
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from miner import GENESIS_HEADER, UINT256_MAX, scan_nonces
from ripple_miner.nativehash import DLL,scan_preferred,native_selftest
from ripple_miner.replication import ReplicatingHive
from ripple_miner.spatial import WorkMap

class NativeParity(unittest.TestCase):
    def test_portable_backend_preserves_every_valid_nonce(self):
        with patch.dict(os.environ,{'RIPPLE_NATIVE_HASH':'0'}):
            a=scan_preferred(GENESIS_HEADER[:76],128,4,UINT256_MAX,0)
        self.assertEqual(a,scan_nonces(GENESIS_HEADER[:76],128,4,UINT256_MAX,0))

    @unittest.skipUnless(DLL.exists(),'compiled native library unavailable')
    def test_compiled_backend_verified_before_selection(self):
        self.assertEqual(native_selftest()['result'],'pass')
        with patch.dict(os.environ,{'RIPPLE_NATIVE_HASH':'1'}):
            count,proofs=scan_preferred(GENESIS_HEADER[:76],2083236893,2,UINT256_MAX,0)
        self.assertEqual((count,proofs),scan_nonces(GENESIS_HEADER[:76],2083236893,2,UINT256_MAX,0))

    @unittest.skipUnless(DLL.exists(),'compiled native library unavailable')
    def test_compiled_backend_easiest_pool_overflow_uses_exact_fallback(self):
        with patch.dict(os.environ,{'RIPPLE_NATIVE_HASH':'1'}):
            count,proofs=scan_preferred(GENESIS_HEADER[:76],0,10001,UINT256_MAX,0)
        self.assertEqual((count,len(proofs)),(10001,10001))
        self.assertEqual(proofs[0],scan_nonces(GENESIS_HEADER[:76],0,1,UINT256_MAX,0)[1][0])

class ReplicationTeardown(unittest.TestCase):
    def test_running_descendant_shutdown_is_bounded_and_reclaimable(self):
        with tempfile.TemporaryDirectory() as td:
            work=WorkMap(Path(td)/'work.sqlite3')
            hive=ReplicatingHive(Path(td)/'hive.sqlite3',workers=1,control_seconds=.1)
            cell=work.claim('9'*64,0,'hive-root',500000)
            self.assertIsNotNone(cell)
            try:
                hive.submit(cell,GENESIS_HEADER[:76],0,0)
                until=time.monotonic()+6
                seen=[]
                while time.monotonic()<until and not any(ev.get('event')=='assigned' for ev in seen):
                    seen.extend(hive.poll());time.sleep(.03)
                self.assertTrue(any(ev.get('event')=='assigned' for ev in seen),str(seen[-4:]))
                started=time.monotonic()
                hive.close(timeout=4)
                self.assertLess(time.monotonic()-started,6)
                # A cancelled incomplete work assignment remains recoverable,
                # never committed to the completed-hash count.
                self.assertEqual(work.summary()['verified_completed_hashes'],0)
                work.fail(cell['id'],'hive-root')
                retry=work.claim('9'*64,0,'hive-root',500000)
                self.assertTrue(retry['reclaimed'])
                self.assertEqual(retry['id'],cell['id'])
            finally:
                hive.close(timeout=2)
                work.close()
if __name__=='__main__':unittest.main()