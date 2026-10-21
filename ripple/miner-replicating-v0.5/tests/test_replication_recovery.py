"""Failure injection against real descendant process, sqlite work reclamation."""
import os,signal,sys,tempfile,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from miner import GENESIS_HEADER
from ripple_miner.replication import ReplicatingHive
from ripple_miner.spatial import WorkMap

@unittest.skipUnless(hasattr(signal,'SIGKILL'),'Unix SIGKILL fault injection only')
class TestRecovery(unittest.TestCase):
    def test_killed_real_descendant_reclaims_exact_nonce_cell(self):
        with tempfile.TemporaryDirectory() as td:
            wm=WorkMap(Path(td)/'map.sqlite3')
            hive=ReplicatingHive(Path(td)/'hive.sqlite3',workers=1,control_seconds=.15)
            key='f'*64;cell=wm.claim(key,0,'hive-root',500000)
            self.assertEqual(cell['start'],0)
            killed=False;failed=False;completed=False;known_pid=None;assigned=False
            try:
                hive.submit(cell,GENESIS_HEADER[:76],0,0)
                deadline=time.monotonic()+9
                while time.monotonic()<deadline and not failed:
                    for e in hive.poll():
                        if e['event']=='born':known_pid=e['pid']
                        if e['event']=='assigned':assigned=True
                        if e['event']=='result' and not killed:
                            self.fail('descendant completed before fault injection')
                        if e['event']=='failed' and e.get('id')==cell['id']:failed=True
                    if known_pid and assigned and not killed:
                        os.kill(known_pid,signal.SIGKILL);killed=True
                    time.sleep(.01)
                self.assertTrue(killed)
                self.assertTrue(failed)
                wm.fail(cell['id'],'hive-root')
                again=wm.claim(key,0,'hive-root',500000)
                self.assertEqual(again['id'],cell['id'])
                self.assertTrue(again['reclaimed'])
                hive.submit(again,GENESIS_HEADER[:76],0,0)
                deadline=time.monotonic()+12
                while time.monotonic()<deadline and not completed:
                    for e in hive.poll():
                        if e['event']=='result' and e.get('id')==cell['id']:
                            self.assertEqual(e['count'],500000)
                            wm.finish(cell['id'],'hive-root',hashes_done=e['count'],elapsed=e['elapsed'])
                            completed=True
                    time.sleep(.02)
                self.assertTrue(completed)
                self.assertEqual(wm.summary()['verified_completed_hashes'],500000)
            finally:hive.close();wm.close()