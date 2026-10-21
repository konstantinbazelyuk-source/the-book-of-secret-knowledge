"""Actual Stratum V1 mining loop using a living multi-master Ripple colony.

WorkMap is the sole durable nonce owner; masters/descendants cannot claim or
complete Bitcoin cells without root verification. Pool credentials never enter
worker process queues. Historical algorithm constants remain in replication.py.
"""
from __future__ import annotations
import asyncio
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import struct
import time
from miner import header_prefix, sha256d, target_from_bits, target_for_difficulty
from .replication import ReplicatingHive
from .spatial import WorkMap
from .remote import RemoteClient, MAX_CHUNK
from .spatial_mining import observed_pause, work_fingerprint


def _verified_results(prefix, rows, share_target, block_target, start, count):
    """Validate returned candidates independently before forwarding to pool."""
    seen=set()
    for nonce,hash_hex,is_block in rows:
        if type(nonce)!=int or not start<=nonce<start+count or nonce in seen:raise ValueError('bad or repeated nonce')
        seen.add(nonce)
        value=sha256d(prefix+struct.pack('<I',nonce))
        if value[::-1].hex()!=hash_hex:raise ValueError('reported hash invalid')
        proof=int.from_bytes(value,'little')
        if proof>share_target or bool(is_block)!=(proof<=block_target):raise ValueError('invalid share target claim')
    return rows


async def mine_replicating(miner):
    wm=WorkMap(miner.spatial_db)
    ledger_path=str(Path(miner.spatial_db).with_name('replication.sqlite3'))
    hive=ReplicatingHive(ledger_path,miner.workers,
                          genetics=getattr(miner,"genetics",True),neuron_gating=getattr(miner,"neuron_gating",True))
    remote=None;remote_task=None;remote_meta=None;remote_wall_seconds=0.
    if getattr(miner,'remote_url',None):
        remote=RemoteClient(miner.remote_url,miner.remote_token)
        remote.health()  # real authenticated remote service or explicit connection failure
    current_generation=-1;key=None;ex2=0;in_flight={}
    last_report=time.monotonic();last_hashes=0
    terminating=False;terminate_at=None
    try:
        while True:
            now=time.monotonic()
            if miner.duration and now-miner.started>=miner.duration:
                if not terminating:terminating=True;terminate_at=now
            paused=observed_pause(getattr(miner,'control_file',None))
            if miner.authorized and miner.work and not terminating:
                if miner.generation!=current_generation:
                    if key is not None:wm.stale(key)
                    current_generation=miner.generation
                    work=miner.work;key=work_fingerprint(miner,work)
                    share_target=target_for_difficulty(work.difficulty)
                    block_target=target_from_bits(int(work.nbits,16));ex2=0
                if not paused:
                    # Maintain bounded useful backlog to trigger reproduction.
                    while len(in_flight)<max(2,hive.capacity*2):
                        cell=wm.claim(key,ex2,'hive-root',miner.chunk)
                        if cell is None:
                            ex2+=1
                            if ex2>=1<<(8*work.extranonce2_size):raise RuntimeError('extranonce space exhausted')
                            cell=wm.claim(key,ex2,'hive-root',miner.chunk)
                        if cell is None:break
                        prefix=header_prefix(work,cell['en2'])
                        mid=hive.submit(cell,prefix,share_target,block_target)
                        in_flight[cell['id']]={'cell':cell,'master':mid,'gen':current_generation,
                                                 'work':work,'prefix':prefix,
                                                 'share_target':share_target,'block_target':block_target,
                                                 'at':now}
                    if remote is not None and remote_task is None:
                        rcell=wm.claim(key,ex2,'hive-remote',min(miner.chunk,MAX_CHUNK))
                        if rcell is None:
                            ex2+=1
                            if ex2>=1<<(8*work.extranonce2_size):raise RuntimeError('extranonce space exhausted')
                            rcell=wm.claim(key,ex2,'hive-remote',min(miner.chunk,MAX_CHUNK))
                        if rcell is not None:
                            rprefix=header_prefix(work,rcell['en2'])
                            remote_meta={'cell':rcell,'gen':current_generation,'work':work,
                                'prefix':rprefix,'share_target':share_target,'block_target':block_target,'at':now}
                            remote_task=asyncio.create_task(asyncio.to_thread(remote.scan,rprefix,rcell['start'],
                                      rcell['count'],share_target,block_target))
            for ev in hive.poll():
                if ev['event'] not in ('result','failed'):continue
                meta=in_flight.pop(ev.get('id'),None)
                if meta is None:continue
                cell=meta['cell']
                if ev['event']=='failed':
                    if meta['gen']==miner.generation:wm.fail(cell['id'],'hive-root')
                    if not miner.quiet:print(json.dumps({'event':'colony_error','error':ev.get('error')}),flush=True)
                    continue
                if meta['gen']!=miner.generation:continue
                try:
                    if ev['count']!=cell['count']:raise ValueError('incomplete descendant scan')
                    _verified_results(meta['prefix'],ev['shares'],meta['share_target'],meta['block_target'],cell['start'],cell['count'])
                    wm.finish(cell['id'],'hive-root',hashes_done=ev['count'],elapsed=max(1e-9,ev['elapsed']))
                    miner.hashes+=ev['count']
                    for nonce,hash_hex,is_block in ev['shares']:
                        rid=await miner.send('mining.submit',[miner.username,meta['work'].job_id,
                          cell['en2'].to_bytes(meta['work'].extranonce2_size,'big').hex(),
                          meta['work'].ntime,struct.pack('>I',nonce).hex()])
                        miner.pending.add(rid);miner.shares_submitted+=1
                        if is_block and not miner.quiet:
                            print(json.dumps({'event':'network_target_met','hash':hash_hex,'nonce':nonce}),flush=True)
                except Exception as e:
                    try:wm.fail(cell['id'],'hive-root')
                    except ValueError:pass
                    if not miner.quiet:print(json.dumps({'event':'colony_invalid_result','error':str(e)[:200]}),flush=True)
            if remote_task is not None and remote_task.done():
                meta=remote_meta;cell=meta['cell'];elapsed=max(0,time.monotonic()-meta['at']);remote_wall_seconds+=elapsed
                try:
                    count,rows=remote_task.result()
                    if meta['gen']==miner.generation:
                        if count!=cell['count']:raise ValueError('incomplete remote scan')
                        _verified_results(meta['prefix'],rows,meta['share_target'],meta['block_target'],cell['start'],cell['count'])
                        wm.finish(cell['id'],'hive-remote',hashes_done=count,elapsed=elapsed)
                        miner.hashes+=count
                        for nonce,hash_hex,is_block in rows:
                            rid=await miner.send('mining.submit',[miner.username,meta['work'].job_id,
                                cell['en2'].to_bytes(meta['work'].extranonce2_size,'big').hex(),
                                meta['work'].ntime,struct.pack('>I',nonce).hex()])
                            miner.pending.add(rid);miner.shares_submitted+=1
                except Exception as e:
                    if meta['gen']==miner.generation:
                        try:wm.fail(cell['id'],'hive-remote')
                        except ValueError:pass
                    if not miner.quiet:print(json.dumps({'event':'remote_error','reason':type(e).__name__}),flush=True)
                remote_task=None;remote_meta=None
            # Detect independent master process failure; reclaim work promptly.
            for mid,(proc,q) in hive.masters.items():
                if not proc.is_alive() and not terminating:
                    for cid,meta in list(in_flight.items()):
                        if meta['master'] == mid:
                            in_flight.pop(cid)
                            try:wm.fail(cid,'hive-root')
                            except ValueError:pass
                    raise RuntimeError(f'colony master {mid} terminated; fail closed')
            if now-last_report>=2:
                if not miner.quiet:
                    print(json.dumps({'event':'rate','hashes':miner.hashes,
                      'hps_recent':round((miner.hashes-last_hashes)/(now-last_report)),
                      'submitted':miner.shares_submitted,'accepted':miner.accepted,'rejected':miner.rejected,
                      'replication':hive.snapshot(),'spatial':wm.summary(),
                      'remote_wall_seconds':round(remote_wall_seconds,3),
                      'remote_cost_usd_calculated':round(remote_wall_seconds/3600*miner.remote_usd_hour,8) if miner.remote_usd_hour is not None else None}),flush=True)
                last_report,last_hashes=now,miner.hashes
            if terminating:
                if not in_flight and remote_task is None:break
                if now-terminate_at>15:break
            await asyncio.sleep(.03)
        if miner.pending:await asyncio.sleep(.25)
    finally:
        # Deliver final verified measurements to the real controller, not just
        # the last periodic sample, which may precede finished descendants.
        hive.poll()
        if not miner.quiet:
            print(json.dumps({'event':'rate','hashes':miner.hashes,
                'hps_recent':round(miner.hashes/max(.001,time.monotonic()-miner.started)),
                'submitted':miner.shares_submitted,'accepted':miner.accepted,'rejected':miner.rejected,
                'replication':hive.snapshot(),'spatial':wm.summary(),
                'remote_wall_seconds':round(remote_wall_seconds,3),
                      'remote_cost_usd_calculated':round(remote_wall_seconds/3600*miner.remote_usd_hour,8) if miner.remote_usd_hour is not None else None}),flush=True)
        hive.close(timeout=12)
        # For uncompleted claims, retained as leases and retried by WorkMap after timeout.
        wm.close()