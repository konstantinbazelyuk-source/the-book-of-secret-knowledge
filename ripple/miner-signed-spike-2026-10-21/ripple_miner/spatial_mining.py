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
from .historical_colony import HistoricalColony
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
    if getattr(miner,'policy','')=='replicating':
        from .replicating_mining import mine_replicating
        return await mine_replicating(miner)
    # Import inherited protocol engine lazily to prevent changing its public API.
    from miner import header_prefix, target_for_difficulty, target_from_bits
    from .nativehash import scan_preferred
    import struct
    loop=asyncio.get_running_loop()
    wm=WorkMap(miner.spatial_db)
    wave=None
    axes=None
    if getattr(miner,'policy','')=='waveform':
        from .regulatory_wave import RegulatoryWave
        try:
            wave=RegulatoryWave(miner.chunk)
        except Exception:
            wm.close()
            raise
    governor=(HistoricalColony(miner.workers) if getattr(miner,'policy','adaptive')=='historical'
              else AdaptiveColony(miner.workers, mode='round_robin' if getattr(miner,'policy','')=='waveform' else getattr(miner,'policy','adaptive')))
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
    productive_started=None
    try:
        with ProcessPoolExecutor(max_workers=miner.workers,mp_context=multiprocessing.get_context('spawn')) as executor:
            while True:
                if miner.duration and productive_started is not None and time.monotonic()-productive_started>=miner.duration:
                    break
                if miner.duration and productive_started is None and time.monotonic()-miner.started>18:
                    raise RuntimeError('no completed mining work within startup deadline')
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
                        if wave is not None:
                            from .spike_axes import SpikeAxisDispatch
                            axes=SpikeAxisDispatch(miner.chunk,work.extranonce2_size)
                        share_target=target_for_difficulty(work.difficulty)
                        block_target=target_from_bits(int(work.nbits,16))
                    if isinstance(governor,HistoricalColony):
                        governor.tick(demand=True)
                    while len(active)<governor.capacity and miner.generation==generation:
                        ident=governor.recruit()
                        if ident is None:break
                        if axes is not None:
                            assignment=axes.dispatch(wm,key,ident,wave.chunk)
                            if assignment is None:
                                raise RuntimeError('all Stratum extranonce2 values exhausted')
                            cell,axis=assignment
                            prefix=axes.prefix(work,cell,header_prefix)
                        else:
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
                            f=loop.run_in_executor(executor,scan_preferred,prefix,cell['start'],cell['count'],share_target,block_target)
                        active[f]=(cell,ident,generation,begin,work)
                if isinstance(governor,HistoricalColony) and (not miner.authorized or paused):
                    governor.tick(demand=False)
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
                            if wave is not None:
                                changed=wave.observe(hashes=count,elapsed=elapsed,active=len(active),capacity=governor.capacity,
                                             pending_shares=len(miner.pending),rejected_shares=miner.rejected,paused=paused)
                                if changed and axes is not None:
                                    axes.wave_update(wave.last_network)
                            if productive_started is None: productive_started=time.monotonic()
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
                            'historical_colony':governor.snapshot() if isinstance(governor,HistoricalColony) else None,
                            'advanced_waveform':({**wave.snapshot(), 'spike_axes':axes.snapshot() if axes else None} if wave else None),
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
        if wave is not None:wave.close()
        wm.close()