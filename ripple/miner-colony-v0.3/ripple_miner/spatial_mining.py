"""Real Stratum V1 work loop backed by transactional voxel-addressed nonce cells.

No invented shares: results go through the inherited scan_nonces function.
Supports multiple local OS processes, task recovery, adaptive observation and
operator pause/resume. Retains the v0.2 Stratum transport and message validation.
"""
from __future__ import annotations
import asyncio
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
import hashlib
import json
import multiprocessing
from pathlib import Path
import time
from .spatial import WorkMap, UINT32_SPACE
from .capacity import AdaptiveColony, WorkerMeasure
from .remote import RemoteClient


def work_fingerprint(miner, work):
    obj = {'pool':miner.host,'user':miner.username,'work':asdict(work)}
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def observed_pause(control_file):
    if not control_file:return False
    try:
        return json.loads(Path(control_file).read_text()).get('state') == 'paused'
    except (FileNotFoundError, OSError, ValueError, AttributeError):
        return False

async def mine_spatial(miner):
    # Import inherited protocol engine lazily to prevent changing its public API.
    from miner import header_prefix, target_for_difficulty, target_from_bits, scan_nonces
    import struct
    loop=asyncio.get_running_loop()
    wm=WorkMap(miner.spatial_db)
    governor=AdaptiveColony(miner.workers, mode=getattr(miner,'policy','adaptive'))
    generation=-1
    key=None
    active={}
    remote = None
    if getattr(miner,'remote_url',None):
        remote=RemoteClient(miner.remote_url,miner.remote_token)
        remote.health()  # authenticated and reachable; any failure is explicit.
        governor.workers['remote-0']=WorkerMeasure('remote-0')
        governor.capacity+=1
    ex2=0
    next_counter=0
    last_report=time.monotonic()
    last_hashes=0
    remote_wall_seconds=0.0
    try:
        with ProcessPoolExecutor(max_workers=miner.workers,mp_context=multiprocessing.get_context('spawn')) as executor:
            while True:
                if miner.duration and time.monotonic()-miner.started >= miner.duration:
                    break
                # Application can pause dispatch while Stratum socket continues receiving updates.
                paused=observed_pause(getattr(miner,'control_file',None))
                if miner.authorized and miner.work and not paused:
                    if miner.generation != generation:
                        if key is not None:wm.stale(key)
                        generation=miner.generation
                        key=work_fingerprint(miner,miner.work)
                        ex2=0
                        next_counter=0
                        work=miner.work
                        share_target=target_for_difficulty(work.difficulty)
                        block_target=target_from_bits(int(work.nbits,16))
                    while len(active)<governor.capacity and miner.generation==generation:
                        ident=governor.recruit()
                        if ident is None:break
                        cell=wm.claim(key,ex2,ident,miner.chunk)
                        if cell is None:
                            ex2+=1
                            if ex2 >= (1 << (8*work.extranonce2_size)):
                                raise RuntimeError('all Stratum extranonce2 values exhausted')
                            cell=wm.claim(key,ex2,ident,miner.chunk)
                            if cell is None:raise RuntimeError('no nonce space available')
                        prefix=header_prefix(work,cell['en2'])
                        begin=time.monotonic()
                        if remote and ident == 'remote-0':
                            # One opt-in remote logical slot; results are independently
                            # verified before pool submission by RemoteClient.scan.
                            f=asyncio.create_task(asyncio.to_thread(remote.scan,prefix,cell['start'],
                                  cell['count'],share_target,block_target))
                        else:
                            f=loop.run_in_executor(executor,scan_nonces,prefix,cell['start'],cell['count'],share_target,block_target)
                        active[f]=(cell,ident,generation,begin,work)
                if active:
                    done,_=await asyncio.wait(active,timeout=.12,return_when=asyncio.FIRST_COMPLETED)
                    for future in done:
                        cell,ident,gen,begin,assigned_work=active.pop(future)
                        elapsed=max(1e-8,time.monotonic()-begin)
                        try:
                            count,results=future.result()
                            if ident=='remote-0':remote_wall_seconds+=elapsed
                            if gen != miner.generation:
                                governor.record(ident,0,elapsed,False)
                                continue
                            wm.finish(cell['id'],ident,hashes_done=count,elapsed=elapsed)
                            governor.record(ident,count,elapsed,True)
                            miner.hashes+=count
                            for nonce,hash_value,is_block in results:
                                rid=await miner.send('mining.submit',[miner.username,assigned_work.job_id,
                                    cell['en2'].to_bytes(assigned_work.extranonce2_size,'big').hex(),
                                    assigned_work.ntime,struct.pack('>I',nonce).hex()])
                                miner.pending.add(rid)
                                miner.shares_submitted+=1
                                if is_block and not miner.quiet:
                                    print(json.dumps({'event':'network_target_met','hash':hash_value,'nonce':nonce}),flush=True)
                        except Exception as exc:
                            governor.record(ident,0,elapsed,False)
                            wm.fail(cell['id'],ident)
                            if not miner.quiet:
                                print(json.dumps({'event':'cell_failed','cell':cell['id'],'error':type(exc).__name__}),flush=True)
                            # Intentionally leave lease to expire, rather than marking the cell complete.
                else:
                    await asyncio.sleep(.12)
                now=time.monotonic()
                if now-last_report>=2.0:
                    if not miner.quiet:
                        print(json.dumps({'event':'rate','hashes':miner.hashes,
                            'hps_recent':round((miner.hashes-last_hashes)/(now-last_report)),
                            'submitted':miner.shares_submitted,'accepted':miner.accepted,
                            'rejected':miner.rejected,'colony_workers':governor.capacity,
                            'spatial':wm.summary(),
                            'remote_wall_seconds':round(remote_wall_seconds,3),
                            'remote_cost_usd_calculated':round(remote_wall_seconds/3600*miner.remote_usd_hour,8)
                                if miner.remote_usd_hour is not None else None}),flush=True)
                    last_report,last_hashes=now,miner.hashes
                await asyncio.sleep(0)
            # Wait for bounded in-flight scanning, allowing submitted shares to be acknowledged.
            for future,(cell,ident,gen,begin,assigned_work) in list(active.items()):
                try:
                    count,results=await future
                    if gen==miner.generation:
                        wm.finish(cell['id'],ident,hashes_done=count,elapsed=max(1e-8,time.monotonic()-begin))
                        miner.hashes+=count
                        for nonce,hash_value,is_block in results:
                            rid=await miner.send('mining.submit',[miner.username,assigned_work.job_id,
                                cell['en2'].to_bytes(assigned_work.extranonce2_size,'big').hex(),
                                assigned_work.ntime,struct.pack('>I',nonce).hex()])
                            miner.pending.add(rid);miner.shares_submitted+=1
                except Exception:
                    pass
            if miner.pending:
                await asyncio.sleep(.2)
    finally:
        wm.close()
