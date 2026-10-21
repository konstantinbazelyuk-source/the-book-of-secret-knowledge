"""Bounded genetic-variation analogue: select measured worker/chunk candidates.

No ML, no predictions; this varies hardware allocation parameters and selects by
measured Bitcoin SHA256d work. Existing Ripple genetic/math cores remain intact.
"""
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import os
from time import perf_counter
from miner import GENESIS_HEADER, scan_nonces


def measure_candidate(workers, chunk, rounds=2):
    start = perf_counter()
    with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        for _ in range(rounds):
            future = [pool.submit(scan_nonces, GENESIS_HEADER[:76], i*chunk, chunk, 0, 0)
                      for i in range(workers)]
            for f in future:
                actual, successes = f.result(timeout=30)
                if actual != chunk or successes:
                    raise RuntimeError('benchmark count mismatch')
    elapsed = perf_counter()-start
    return {'workers': workers, 'chunk': chunk, 'hashes': rounds * workers * chunk,
            'elapsed_seconds': round(elapsed, 4),
            'hashes_per_second': round(rounds * workers * chunk/elapsed, 2)}


def evaluate(max_workers=2, chunks=(10000, 20000), scorer=measure_candidate):
    max_workers = max(1, min(int(max_workers), 4, max(1, (os.cpu_count() or 1)-1)))
    configs = [(w, c) for w in range(1, max_workers+1) for c in chunks]
    trials = [scorer(w, c) for w, c in configs]
    winner = max(trials, key=lambda x: x['hashes_per_second'])
    return {'trials': trials, 'selected': {'workers': winner['workers'], 'chunk': winner['chunk']},
            'classification': 'measured tuning on executing machine; not an ASIC benchmark'}
