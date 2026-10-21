"""Measured same-machine SHA256d scheduler comparison; no real pool or payouts.

Run from project root: python experiments/compare_historical.py
The scheduler setups are initialized before the timed section; process creation is
inside the timed section, equally for all variants. Reports raw per-round values.
"""
from __future__ import annotations
import concurrent.futures, json, os, pathlib, statistics, sys, tempfile, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from miner import scan_nonces
from ripple_miner.historical_colony import HistoricalColony
from ripple_miner.capacity import AdaptiveColony
from ripple_miner.spatial import WorkMap

WORKERS=2
COUNT=50000
CHUNKS=20
PREFIX=bytes.fromhex('00'*76)

def run_variant(kind):
    if kind=='historical':
        governor=HistoricalColony(WORKERS)
        governor.last_tick-=3
        governor.tick(demand=True,budget_override=WORKERS)
        assert len(governor.established)==WORKERS
    else:governor=AdaptiveColony(WORKERS,mode=kind)
    ready=[];hashes=0
    with tempfile.TemporaryDirectory() as tmp:
        work=WorkMap(pathlib.Path(tmp)/'workmap.db')
        begun=time.perf_counter()
        with concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS) as pool:
            while hashes < COUNT*CHUNKS:
                while len(ready)<WORKERS:
                    selected=governor.recruit()
                    if selected is None:break
                    claim=work.claim('b'*64,0,selected,COUNT,limit=COUNT*CHUNKS)
                    if claim is None:
                        governor.workers[selected].busy=False
                        break
                    future=pool.submit(scan_nonces,PREFIX,claim['start'],claim['count'],0,0)
                    ready.append((future,claim,selected,time.perf_counter()))
                if not ready:break
                completed=[]
                for f,c,w,start in list(ready):
                    if f.done():
                        n,result=f.result()
                        assert not result and n==c['count']
                        elapsed=time.perf_counter()-start
                        work.finish(c['id'],w,hashes_done=n,elapsed=elapsed)
                        governor.record(w,n,elapsed)
                        hashes+=n
                        completed.append((f,c,w,start))
                if not completed:time.sleep(.001)
                for x in completed:ready.remove(x)
        elapsed=time.perf_counter()-begun
        summary=work.summary();work.close()
    assert summary['verified_completed_hashes']==COUNT*CHUNKS==hashes
    return {'policy':kind,'hashes':hashes,'wall_seconds':round(elapsed,6),
            'hps':round(hashes/elapsed,2),'verified':True,'workers':WORKERS}

def main():
    order=('round_robin','adaptive','historical')
    trials=[]
    for j in range(3):
        for policy in order[j:]+order[:j]:
            trials.append(run_variant(policy))
    medians={policy:round(statistics.median(x['hps'] for x in trials if x['policy']==policy),2)
             for policy in order}
    output={'classification':'measured local CPU SHA-256d throughput, no mining income',
            'environment':{'python':sys.version.split()[0],'cpu_count_reported':os.cpu_count(),
                           'device':'this executing development container; not Dell'},
            'config':{'workers':WORKERS,'chunks':CHUNKS,'nonces_per_chunk':COUNT,
                      'hashes_per_variant_per_round':CHUNKS*COUNT,'repetitions':3},
            'trials':trials,'median_hashrate_hps':medians,
            'note':'Observed order-dependent variability; do not interpret as ASIC or payout performance.'}
    path=pathlib.Path(__file__).parent/'historical_results.json'
    path.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output['median_hashrate_hps'],indent=2))
if __name__=='__main__':main()