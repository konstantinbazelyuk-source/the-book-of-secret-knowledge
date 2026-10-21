"""Historical-colony resource admission, neighbor establishment and mining bridge."""
import unittest
from unittest.mock import patch
from ripple_miner.historical_colony import HistoricalColony,xyz,adjacency
from ripple_miner.spatial import WorkMap
from miner import sha256d,scan_nonces
from tempfile import TemporaryDirectory
from pathlib import Path

class Clock:
    def __init__(self):self.now=100.
    def __call__(self):return self.now

class TestHistoricalColony(unittest.TestCase):
    def setUp(self):self.clock=Clock()
    def test_growth_frontier_and_physical_budget(self):
        c=HistoricalColony(9,clock=self.clock)
        self.assertEqual(c.capacity,1)
        for i in range(4):
            self.clock.now+=1.1;c.tick(demand=True,budget_override=5)
        self.assertEqual(len(c.established),min(5,c.max_slots))
        for s in c.sites.values():
            if s.occupied and s.parent is not None:
                self.assertTrue(adjacency(s.position,c.sites[s.parent].position))
        self.assertEqual(c.snapshot()['measured_admission_budget'],min(5,c.max_slots))
        self.assertLessEqual(c.max_slots,9)
    def test_idle_retires_leaf_not_active(self):
        c=HistoricalColony(3,clock=self.clock)
        self.clock.now+=1.1;c.tick(demand=True,budget_override=3)
        self.assertEqual(c.capacity,3)
        c.workers['cpu-2'].busy=True
        self.clock.now+=1.1;c.tick(demand=False,budget_override=3)
        self.clock.now+=16;c.tick(demand=False,budget_override=3)
        self.assertEqual(c.capacity,3)  # leaf busy: cannot vanish
        c.workers['cpu-2'].busy=False
        self.clock.now+=5.1;c.tick(demand=False,budget_override=3)
        self.assertEqual(c.capacity,2)
    def test_allocation_never_duplicates(self):
        with TemporaryDirectory() as tmp:
            w=WorkMap(Path(tmp)/'cells.db');c=HistoricalColony(3,clock=self.clock)
            self.clock.now+=1.1;c.tick(demand=True,budget_override=3)
            cells=[]
            for name in sorted(c.established):
                wid=c.recruit();self.assertIsNotNone(wid)
                cells.append(w.claim('a'*64,0,wid,1000,limit=5000))
            self.assertEqual(len({z['start'] for z in cells}),3)
            for z in cells:
                w.finish(z['id'],w.map()[0]['worker'] if False else next(row['worker'] for row in w.map() if row['id']==z['id']), hashes_done=z['count'], elapsed=.1)
            self.assertEqual(w.summary()['verified_completed_hashes'],3000)
            w.close()
    def test_real_sha256d_compute_from_claim(self):
        with TemporaryDirectory() as tmp:
            w=WorkMap(Path(tmp)/'cells.db')
            c=w.claim('b'*64,0,'cpu-0',100,limit=1000)
            prefix=b'\x00'*76
            n, shares=scan_nonces(prefix,c['start'],c['count'],(1<<256)-1,(1<<256)-1)
            self.assertEqual(n,100)
            self.assertEqual(len(shares),100)
            self.assertEqual(shares[0][1],sha256d(prefix + (0).to_bytes(4,'little'))[::-1].hex())
            w.finish(c['id'],'cpu-0',hashes_done=n,elapsed=.01)
            w.close()
    def test_remote_slots_are_real_recruits(self):
        from ripple_miner.capacity import WorkerMeasure
        c=HistoricalColony(2,clock=self.clock)
        c.workers['remote-0']=WorkerMeasure('remote-0')
        c.capacity+=1
        a=c.recruit();b=c.recruit();self.assertEqual({a,b},{'cpu-0','remote-0'})
        c.record('remote-0',50,.1)
        self.assertEqual(c.obs_completion,1)
    def test_monotonic_observed_budget(self):
        c=HistoricalColony(4,clock=self.clock)
        self.clock.now+=1.1;c.tick(demand=True,budget_override=2)
        self.assertLessEqual(len(c.established),2)
        self.assertEqual(xyz(9),(0,0,1))

if __name__=='__main__':unittest.main()