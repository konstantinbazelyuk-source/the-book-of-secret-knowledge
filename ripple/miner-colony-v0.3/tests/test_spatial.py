import asyncio
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ripple_miner.spatial import WorkMap,coords
from ripple_miner.capacity import AdaptiveColony,compare_schedules
from ripple_miner.spatial_mining import work_fingerprint,observed_pause
from miner import StratumMiner,Work

class SpatialTests(unittest.TestCase):
    def test_voxel_coordinates_and_nonoverlap(self):
        self.assertEqual(coords(4096),(0,0,1))
        self.assertEqual(coords(65),(1,1,0))
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'ledger.sqlite3';db=WorkMap(p)
            cells=[db.claim('a'*64,0,'cpu-'+str(i%3),130,limit=1000) for i in range(8)]
            self.assertEqual(sum(c['count'] for c in cells),1000)
            self.assertEqual(sorted(set(n for c in cells for n in range(c['start'],c['start']+c['count']))),list(range(1000)))
            self.assertIsNone(db.claim('a'*64,0,'cpu-final',130,limit=1000))
            self.assertEqual(len(set(tuple(c['xyz']) for c in cells)),8)
            for c in cells:db.finish(c['id'],'cpu-'+str(c['segment']%3),hashes_done=c['count'],elapsed=.1)
            self.assertEqual(db.summary()['verified_completed_hashes'],1000)
            db.close();db=WorkMap(p)
            self.assertEqual(db.summary()['verified_completed_hashes'],1000)
            self.assertIsNone(db.claim('a'*64,0,'cpu-final',100,limit=1000))
            db.close()
    def test_expired_lease_and_stale_job_protection(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=WorkMap(Path(tmp)/'x.db')
            first=db.claim('b'*64,0,'node-1',10,lease_seconds=1)
            with db.connection:db.connection.execute('UPDATE cells SET lease_until=? WHERE id=?',(0,first['id']))
            reclaimed=db.claim('b'*64,0,'node-2',10)
            self.assertEqual(reclaimed['start'],first['start'])
            self.assertTrue(reclaimed['reclaimed'])
            with self.assertRaises(ValueError):db.finish(first['id'],'node-1',hashes_done=10,elapsed=.1)
            db.finish(first['id'],'node-2',hashes_done=10,elapsed=.2)
            self.assertEqual(db.summary()['counts']['done'],1)
            c=db.claim('b'*64,0,'node-2',12)
            db.fail(c['id'],'node-2')
            recovered=db.claim('b'*64,0,'node-3',12)
            self.assertEqual(recovered['id'],c['id'])
            db.stale('b'*64)
            with self.assertRaises(ValueError):db.finish(c['id'],'node-2',hashes_done=12,elapsed=.1)
            db.close()
    def test_adaptive_measured_accounting(self):
        c=AdaptiveColony(2)
        name=c.recruit();self.assertIsNotNone(name)
        c.record(name,1000,.01)
        self.assertGreater(c.workers[name].hps,10000)
        self.assertGreater(c.snapshot()['workers'][0]['tasks']+c.snapshot()['workers'][-1]['tasks'],0)
        result=compare_schedules([1,3,7])
        self.assertEqual(result['classification'].split()[0],'analytical')
    def test_mining_work_identity_separates_sessions(self):
        w=Work('x','00'*32,'aa','bb',(),'20000000','207fffff','5f5e1000',True,'cafe',4,'1')
        m=StratumMiner('127.0.0.1',1001,'user','x')
        w2=Work('x','00'*32,'aa','bb',(),'20000000','207fffff','5f5e1000',True,'dead',4,'1')
        self.assertNotEqual(work_fingerprint(m,w),work_fingerprint(m,w2))
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'control.json';self.assertFalse(observed_pause(p));p.write_text('{"state":"paused"}')
            self.assertTrue(observed_pause(p))

if __name__=='__main__':unittest.main()
