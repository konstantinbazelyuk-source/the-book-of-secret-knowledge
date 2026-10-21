"""Reproducible BASELINE vs SQLITE-VOXEL experiment on identical hashes.
This benchmark does not use Stratum or claim actual pool payouts.
"""
from concurrent.futures import ProcessPoolExecutor
import argparse
import json
import multiprocessing
import os
from pathlib import Path
import platform
import statistics
import sys
import tempfile
from time import perf_counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from miner import GENESIS_HEADER,scan_nonces
from ripple_miner.spatial import WorkMap


def run_trial(mode,workers,chunk,batches):
    assert mode in ('baseline','spatial')
    all_work=chunk*batches
    begin=perf_counter()
    with tempfile.TemporaryDirectory() as folder:
        ledger=WorkMap(Path(folder)/'test.sqlite3') if mode=='spatial' else None
        with ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('spawn')) as pool:
            pending=[]
            for i in range(batches):
                if ledger:
                    cell=ledger.claim('b'*64,0,'bench-'+str(i%workers),chunk)
                    start,count=cell['start'],cell['count']
                else:start,count=i*chunk,chunk
                f=pool.submit(scan_nonces,GENESIS_HEADER[:76],start,count,0,0)
                pending.append((f,cell if ledger else None,i))
            done=0
            for f,cell,i in pending:
                count,shares=f.result(timeout=45)
                if shares:raise AssertionError('unexpected share under zero target')
                if ledger:ledger.finish(cell['id'],'bench-'+str(i%workers),hashes_done=count,elapsed=0.)
                done+=count
        if ledger:
            recorded=ledger.summary()['verified_completed_hashes']
            assert recorded==done
            ledger.close()
    elapsed=perf_counter()-begin
    assert done==all_work
    return {'seconds':round(elapsed,5),'hashes':done,'hashes_per_second':round(done/elapsed)}


def main():
    p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=2)
    p.add_argument('--chunk',type=int,default=3000);p.add_argument('--batches',type=int,default=40)
    p.add_argument('--rounds',type=int,default=3);p.add_argument('--out',default='experiments/RESULTS.json')
    a=p.parse_args()
    if not 1<=a.workers<=8 or not 100<=a.chunk<=100000 or not 1<=a.batches<=1000 or not 1<=a.rounds<=5:
        p.error('invalid bounded experiment configuration')
    records=[]
    for r in range(a.rounds):
        for mode in (('baseline','spatial') if r%2==0 else ('spatial','baseline')):
            records.append({'round':r+1,'mode':mode,**run_trial(mode,a.workers,a.chunk,a.batches)})
    medians={mode:statistics.median(x['hashes_per_second'] for x in records if x['mode']==mode)
             for mode in ('baseline','spatial')}
    out={'classification':'measured local CPU wall-clock throughput; not mining earnings',
         'environment':{'python':sys.version.split()[0],'platform':platform.platform(),
                        'cpu_visible':os.cpu_count()},
         'inputs':{'workers':a.workers,'chunk':a.chunk,'batches':a.batches,'rounds':a.rounds,
                   'hashing_function':'inherited miner.scan_nonces, GENESIS_HEADER 76-byte prefix'},
         'runs':records,'median_hashes_per_second':medians,
         'spatial_vs_baseline_percent':round(100*(medians['spatial']/medians['baseline']-1),2),
         'note':'spatial scheduling adds SQLite durability and can impose overhead; same CPU process pool and same SHA256d work'}
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
