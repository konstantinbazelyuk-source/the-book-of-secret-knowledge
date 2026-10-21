"""Ripple AntMiner Alpha: real BTC SHA256d CPU mining and Stratum V1 worker.

Designed as a standalone module under the Book of Secret Knowledge's ripple/
tree. Integrates unmodified Ripple Laptop v2 hardware budget when available.
Actual ASIC chips are not emulated; external ASIC dispatch is future work.
"""
from __future__ import annotations

import argparse
import asyncio
from concurrent.futures import ProcessPoolExecutor
from contextlib import nullcontext
from dataclasses import dataclass
from decimal import Decimal, localcontext
import hashlib
import json
import os
import multiprocessing
from pathlib import Path
import ssl
import struct
import sys
import time
import random
from typing import Optional

DIFF1_TARGET = 0x00FFFF * (1 << (8 * (0x1D - 3)))
UINT256_MAX = (1 << 256) - 1
GENESIS_HEADER = bytes.fromhex(
    '01000000' + '00'*32 +
    '3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a' +
    '29ab5f49' + 'ffff001d' + '1dac2b7c')
GENESIS_HASH = '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'


def sha256d(blob: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(blob).digest()).digest()


def block_hash(header: bytes) -> str:
    if len(header) != 80:
        raise ValueError('Bitcoin header must be 80 bytes')
    return sha256d(header)[::-1].hex()


def target_from_bits(bits: int) -> int:
    exp, coeff = bits >> 24, bits & 0x007fffff
    if bits & 0x00800000 or coeff == 0:
        raise ValueError('invalid compact difficulty target')
    target = coeff >> (8 * (3-exp)) if exp <= 3 else coeff << (8 * (exp-3))
    if target <= 0 or target > UINT256_MAX:
        raise ValueError('compact target out of range')
    return target


def target_for_difficulty(difficulty: str | int | float) -> int:
    diff = Decimal(str(difficulty))
    if not diff.is_finite() or diff <= 0:
        raise ValueError('pool difficulty must be finite and positive')
    with localcontext() as context:
        context.prec = 110
        return max(1, min(UINT256_MAX, int(Decimal(DIFF1_TARGET) / diff)))


def wordswap(hex_value: str) -> bytes:
    """Legacy Bitcoin Stratum V1 prevhash: reverse the bytes of each 4-byte word."""
    raw = bytes.fromhex(hex_value)
    if len(raw) != 32:
        raise ValueError('previous block hash should contain 32 bytes')
    return b''.join(raw[i:i+4][::-1] for i in range(0, 32, 4))


@dataclass(frozen=True)
class Work:
    job_id: str
    prevhash: str
    coinb1: str
    coinb2: str
    branches: tuple[str, ...]
    version: str
    nbits: str
    ntime: str
    clean_jobs: bool
    extranonce1: str
    extranonce2_size: int
    difficulty: str


def header_prefix(work: Work, extranonce2: int) -> bytes:
    if not 1 <= work.extranonce2_size <= 16:
        raise ValueError('unsupported extranonce2 length')
    en2 = extranonce2.to_bytes(work.extranonce2_size, 'big')
    coinbase = bytes.fromhex(work.coinb1 + work.extranonce1) + en2 + bytes.fromhex(work.coinb2)
    root = sha256d(coinbase)
    for branch in work.branches:
        item = bytes.fromhex(branch)
        if len(item) != 32:
            raise ValueError('merkle branch length must be 32 bytes')
        root = sha256d(root + item)
    version = bytes.fromhex(work.version)[::-1]
    time_bytes = bytes.fromhex(work.ntime)[::-1]
    bits_bytes = bytes.fromhex(work.nbits)[::-1]
    if len(version) != 4 or len(time_bytes) != 4 or len(bits_bytes) != 4:
        raise ValueError('malformed version, ntime, or nbits')
    header = version + wordswap(work.prevhash) + root + time_bytes + bits_bytes
    if len(header) != 76:
        raise AssertionError('incorrect header prefix construction')
    return header


def scan_nonces(prefix: bytes, start: int, count: int, share_target: int, block_target: int):
    """Search disjoint nonces, returning every actual qualifying hash, not fake shares."""
    if len(prefix) != 76 or not 0 <= start < (1 << 32) or not 0 <= count <= (1 << 32) - start:
        raise ValueError('invalid nonce batch')
    successes = []
    for nonce in range(start, start + count):
        digest = sha256d(prefix + struct.pack('<I', nonce))
        value = int.from_bytes(digest, 'little')
        if value <= share_target:
            successes.append((nonce, digest[::-1].hex(), value <= block_target))
    return count, successes


def ripple_worker_budget(requested: int) -> tuple[int, str]:
    """Reuse actual Ripple Laptop hardware capacity probe if available, with a fallback.

    This deliberately uses the existing unmodified ripple_native.hardware module.
    """
    native = Path(__file__).resolve().parent.parent / 'native-alpha-v2.0'
    if native.exists():
        sys.path.insert(0, str(native))
        try:
            from ripple_native.hardware import probe, decide_budget
            hw = probe()
            budget = decide_budget(hw, max_workers=requested)
            return min(requested, budget['maximum_workers']), 'Ripple Laptop v2.0 hardware governor'
        finally:
            sys.path.pop(0)
    return min(requested, max(1, (os.cpu_count() or 1) - 1)), 'standalone conservative CPU count'


class StratumMiner:
    def __init__(self, host: str, port: int, username: str, password: str,
                 *, workers: int = 1, chunk: int = 5000, tls: bool = False,
                 duration: float = 0, quiet: bool = False,
                 spatial_db=None, control_file=None, policy='adaptive',remote_url=None,remote_token=None,remote_usd_hour=None,
                 genetics=True,neuron_gating=True):
        if not host or not username or not 1 <= port <= 65535 or not 1 <= workers <= 128 or not 1 <= chunk <= 500000:
            raise ValueError('invalid mining configuration')
        self.host, self.port, self.username, self.password = host, port, username, password
        self.workers, self.chunk, self.tls, self.duration, self.quiet = workers, chunk, tls, duration, quiet
        self.spatial_db, self.control_file, self.policy = spatial_db, control_file, policy
        self.genetics,self.neuron_gating=bool(genetics),bool(neuron_gating)
        self.remote_url,self.remote_token=remote_url,remote_token
        if remote_usd_hour is not None and not 0<=float(remote_usd_hour)<=100000:
            raise ValueError('remote hourly rate out of range')
        self.remote_usd_hour=remote_usd_hour
        self.writer = None
        self.authorized = False
        self.extranonce1 = None
        self.extranonce2_size = None
        self.current_difficulty = '1'
        self.next_difficulty = '1'
        self.work: Optional[Work] = None
        self.generation = 0
        self.request_id = 2
        self.shares_submitted = 0
        self.accepted = 0
        self.rejected = 0
        self.hashes = 0
        self.started = None
        self.pending = set()

    async def send(self, method: str, params: list, *, rid: Optional[int] = None):
        if rid is None:
            self.request_id += 1
            rid = self.request_id
        packet = json.dumps({'id': rid, 'method': method, 'params': params}, separators=(',', ':')) + '\n'
        self.writer.write(packet.encode('utf-8'))
        await self.writer.drain()
        return rid

    async def handle_message(self, msg: dict):
        if msg.get('method'):
            method, params = msg['method'], msg.get('params') or []
            if method == 'mining.set_difficulty':
                self.next_difficulty = str(params[0])
                target_for_difficulty(self.next_difficulty)
            elif method == 'mining.set_extranonce':
                self.extranonce1, self.extranonce2_size = str(params[0]), int(params[1])
                self.work = None
                self.generation += 1
            elif method == 'mining.notify':
                if self.extranonce1 is None:
                    return
                if len(params) != 9:
                    raise ValueError('mining.notify should contain 9 parameters')
                self.current_difficulty = self.next_difficulty
                self.work = Work(str(params[0]), params[1], params[2], params[3], tuple(params[4]),
                                 params[5], params[6], params[7], bool(params[8]),
                                 self.extranonce1, self.extranonce2_size, self.current_difficulty)
                self.generation += 1
                if not self.quiet:
                    print(json.dumps({'event': 'job', 'id': self.work.job_id,
                                      'difficulty': self.work.difficulty, 'generation': self.generation}), flush=True)
            elif method == 'client.get_version':
                self.writer.write((json.dumps({'id': msg.get('id'), 'result': 'RippleAntMiner/0.1', 'error': None})+'\n').encode())
                await self.writer.drain()
            return
        rid = msg.get('id')
        if rid == 1:
            if msg.get('error') or not isinstance(msg.get('result'), list) or len(msg['result']) != 3:
                raise RuntimeError('mining.subscribe failed: '+str(msg.get('error')))
            self.extranonce1 = str(msg['result'][1])
            self.extranonce2_size = int(msg['result'][2])
            if not 1 <= self.extranonce2_size <= 16:
                raise ValueError('unsupported pool extranonce2 length')
            await self.send('mining.authorize', [self.username, self.password], rid=2)
        elif rid == 2:
            if msg.get('result') is not True:
                raise RuntimeError('mining.authorize rejected: '+str(msg.get('error')))
            self.authorized = True
            if not self.quiet:
                print(json.dumps({'event':'authorized','username':self.username}),flush=True)
        elif rid in self.pending:
            self.pending.discard(rid)
            if msg.get('result') is True:
                self.accepted += 1
            else:
                self.rejected += 1
            if not self.quiet:
                print(json.dumps({'event': 'share_result', 'accepted': self.accepted,
                                  'rejected': self.rejected, 'error': msg.get('error')}), flush=True)

    async def read_loop(self, reader):
        while True:
            line = await reader.readline()
            if not line:
                raise ConnectionError('pool closed the Stratum connection')
            if len(line) > 1024 * 1024:
                raise ValueError('Stratum response too large')
            await self.handle_message(json.loads(line))

    async def mine_loop(self):
        if getattr(self,'spatial_db',None):
            from ripple_miner.spatial_mining import mine_spatial
            return await mine_spatial(self)
        loop = asyncio.get_running_loop()
        ex2 = 0
        seen_generation = -1
        nonce_cursor = 0
        prefix = None
        block_target = 0
        share_target = 0
        last_report = time.monotonic()
        last_hashes = 0
        # For one worker a thread avoids OS spawn latency, which could exceed
        # short pool test jobs and waste connection time before first hashes.
        backend=(ProcessPoolExecutor(max_workers=self.workers, mp_context=multiprocessing.get_context('spawn'))
                 if self.workers>1 else nullcontext(None))
        with backend as executor:
            while True:
                if self.duration and time.monotonic() - self.started >= self.duration:
                    if self.pending:
                        await asyncio.sleep(.15)
                    return
                if not (self.authorized and self.work):
                    await asyncio.sleep(.025)
                    continue
                if seen_generation != self.generation:
                    seen_generation = self.generation
                    ex2 = 0
                    nonce_cursor = 0
                    work = self.work
                    share_target = target_for_difficulty(work.difficulty)
                    block_target = target_from_bits(int(work.nbits, 16))
                    prefix = header_prefix(work, ex2)
                # Do not cross an extranonce2 boundary inside one batch: every
                # resulting share must be submitted with its exact coinbase nonce.
                if nonce_cursor + self.workers * self.chunk > (1 << 32):
                    ex2 += 1
                    if ex2 >= (1 << (8 * work.extranonce2_size)):
                        raise RuntimeError('extranonce2 exhausted; cannot safely repeat work')
                    prefix = header_prefix(work, ex2)
                    nonce_cursor = 0
                tasks = []
                for _ in range(self.workers):
                    start = nonce_cursor
                    nonce_cursor += self.chunk
                    if executor is None:
                        tasks.append(asyncio.to_thread(scan_nonces, prefix, start, self.chunk, share_target, block_target))
                    else:
                        tasks.append(loop.run_in_executor(executor, scan_nonces, prefix, start, self.chunk,
                                                          share_target, block_target))
                for task in asyncio.as_completed(tasks):
                    count, results = await task
                    self.hashes += count
                    if self.generation != seen_generation:
                        continue
                    for nonce, h, valid_block in results:
                        rid = await self.send('mining.submit', [self.username, work.job_id,
                                              ex2.to_bytes(work.extranonce2_size, 'big').hex(),
                                              work.ntime, struct.pack('>I', nonce).hex()])
                        self.pending.add(rid)
                        self.shares_submitted += 1
                        if valid_block and not self.quiet:
                            print(json.dumps({'event':'network_target_met','block_hash':h,'nonce':nonce}),flush=True)
                now = time.monotonic()
                if now - last_report >= 2:
                    if not self.quiet:
                        print(json.dumps({'event': 'rate', 'hashes': self.hashes,
                                          'hps_recent': round((self.hashes-last_hashes)/(now-last_report)),
                                          'submitted': self.shares_submitted,
                                          'accepted': self.accepted, 'rejected': self.rejected}),flush=True)
                    last_report, last_hashes = now, self.hashes
                await asyncio.sleep(0)  # allow socket reader to apply clean jobs

    async def run(self):
        worker_count, source = ripple_worker_budget(self.workers)
        self.workers = worker_count
        ctx = ssl.create_default_context() if self.tls else None
        self.started = time.monotonic()
        reader, writer = await asyncio.wait_for(asyncio.open_connection(
            self.host, self.port, ssl=ctx, server_hostname=self.host if ctx else None), timeout=12)
        self.writer = writer
        if not self.quiet:
            print(json.dumps({'event': 'connected', 'host': self.host, 'workers': self.workers,
                              'governor': source, 'tls': self.tls}), flush=True)
        receive = None
        mine = None
        try:
            await self.send('mining.subscribe', ['RippleAntMiner/0.1'], rid=1)
            receive = asyncio.create_task(self.read_loop(reader))
            mine = asyncio.create_task(self.mine_loop())
            done, pending = await asyncio.wait([receive, mine], return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        finally:
            # Cancellation is not cleanup: wait for the mining loop's finally
            # block to terminate masters and descendants before retrying the pool.
            tasks=[t for t in (receive,mine) if t is not None]
            for t in tasks:t.cancel()
            if tasks:
                try:
                    await asyncio.wait_for(asyncio.gather(*tasks,return_exceptions=True),timeout=22)
                except asyncio.TimeoutError:
                    if not self.quiet:
                        print(json.dumps({'event':'cleanup_timeout','seconds':22}),flush=True)
                    # Explicit failure: do not silently claim the process tree was reaped.
                    writer.close()
                    raise RuntimeError('mining task cleanup exceeded 22 seconds')
            writer.close()
            try:await asyncio.wait_for(writer.wait_closed(),timeout=5)
            except (ConnectionError,OSError,asyncio.TimeoutError):pass
        elapsed = max(.000001, time.monotonic()-self.started)
        stats = {'event': 'complete', 'hashes': self.hashes, 'seconds': round(elapsed, 3),
                 'average_hps': round(self.hashes / elapsed), 'shares_submitted': self.shares_submitted,
                 'accepted': self.accepted, 'rejected': self.rejected,
                 'host': 'local CPU; never a remotely verified ASIC'}
        print(json.dumps(stats), flush=True)
        return stats


async def run_with_retries(factory, max_retries=0, *, backoff_cap=60, jitter=True, backup_factory=None):
    """Keep a personal miner connected. None means retry indefinitely until stopped.

    Authentication/protocol failures are not retried without operator intervention.
    Explicit max_retries values remain backwards compatible for existing tests.
    """
    if max_retries is not None and not 0 <= max_retries <= 10:
        raise ValueError('max_retries outside 0..10 or None for continuous operation')
    retries=0
    while True:
        try:
            target = backup_factory if (backup_factory is not None and retries % 2 == 1) else factory
            return await target().run()
        except (ConnectionError,OSError,asyncio.TimeoutError) as exc:
            if max_retries is not None and retries>=max_retries:raise
            retries+=1
            delay=min(backoff_cap,2**min(retries,12))
            if max_retries is None and jitter:delay=round(delay*(.85+random.random()*.3),2)
            print(json.dumps({'event':'reconnecting','attempt':retries,'delay_seconds':delay,
                              'error_type':type(exc).__name__}),flush=True)
            await asyncio.sleep(delay)


def benchmark(n: int):
    if not 1 <= n <= 10_000_000:
        raise ValueError('benchmark hashes must be 1..10,000,000')
    start = time.perf_counter()
    total, _ = scan_nonces(GENESIS_HEADER[:76], 0, n, 0, 0)
    seconds = time.perf_counter() - start
    return {'hashes': total, 'seconds': seconds, 'hashes_per_second': round(n / seconds),
            'hardware': 'current Python process', 'known_genesis_hash': block_hash(GENESIS_HEADER)}


def main():
    cli = argparse.ArgumentParser(description='Ripple AntMiner Alpha Bitcoin CPU Stratum V1 miner')
    sub = cli.add_subparsers(dest='command', required=True)
    b = sub.add_parser('bench', help='measure real SHA256d hashes on this machine')
    b.add_argument('--hashes', type=int, default=100000)
    m = sub.add_parser('mine', help='connect to a pool and search real hashes')
    m.add_argument('--host', required=True)
    m.add_argument('--port', required=True, type=int)
    m.add_argument('--user', required=True, help='mining-pool worker login, not a wallet private key')
    m.add_argument('--password', default='x')
    m.add_argument('--password-env', action='store_true', help='read password from RIPPLE_POOL_PASS environment variable')
    m.add_argument('--tls', action='store_true')
    m.add_argument('--workers', type=int, default=1)
    m.add_argument('--chunk', type=int, default=5000)
    m.add_argument('--spatial-db', default=None, help='SQLite-backed nonce chunk scheduler')
    m.add_argument('--control-file', default=None, help='operator pause/resume control file')
    m.add_argument('--policy', choices=('adaptive','round_robin','historical','replicating'), default='adaptive')
    m.add_argument('--native-hash',action='store_true',help='optional locally built OpenSSL SHA256d backend (replicating policy)')
    m.add_argument('--disable-genetics',action='store_true',help='ablation: disable descendant parameter mutations')
    m.add_argument('--disable-neuron-gate',action='store_true',help='ablation: skip Ripple neuron authorization of hash sub-batches')
    m.add_argument('--remote-url',default=None, help='explicit HTTPS authorized remote worker (or localhost)')
    m.add_argument('--remote-token-env',action='store_true')
    m.add_argument('--remote-usd-hour',type=float,default=None)
    m.add_argument('--seconds', type=float, default=0, help='0=continue until interrupted')
    m.add_argument('--retries', type=int, default=0, help='pool reconnect attempts 0..10; -1 retries continuously')
    m.add_argument('--backup-host',default=None,help='backup Stratum pool hostname')
    m.add_argument('--backup-port',type=int,default=None,help='backup Stratum pool port')
    m.add_argument('--backup-tls',action='store_true',help='backup pool uses TLS')
    m.add_argument('--backup-user',default=None,help='backup pool worker identifier')
    args = cli.parse_args()
    if args.command == 'bench':
        print(json.dumps(benchmark(args.hashes), indent=2))
    else:
        if args.native_hash:
            from ripple_miner.nativehash import DLL
            if not DLL.is_file():raise SystemExit('native hashing requires locally compiled compatible library: '+str(DLL))
            os.environ['RIPPLE_NATIVE_HASH']='1'
        try:
            def new_miner(backup=False):
                return StratumMiner(args.backup_host if backup else args.host,
                      args.backup_port if backup else args.port,
                      (args.backup_user or args.user) if backup else args.user,
                      os.environ.get('RIPPLE_POOL_PASS','') if args.password_env else args.password,
                      workers=args.workers, chunk=args.chunk,
                      tls=args.backup_tls if backup else args.tls,
                      duration=args.seconds, spatial_db=args.spatial_db,
                      control_file=args.control_file, policy=args.policy,
                      remote_url=args.remote_url,
                      remote_token=os.environ.get('RIPPLE_REMOTE_TOKEN') if args.remote_token_env else None,
                      remote_usd_hour=args.remote_usd_hour,
                      genetics=not args.disable_genetics,neuron_gating=not args.disable_neuron_gate)
            if args.backup_host and not 1 <= (args.backup_port or 0) <= 65535:
                raise ValueError('backup pool requires a valid port')
            asyncio.run(run_with_retries(lambda:new_miner(False),
                     max_retries=None if args.retries == -1 else args.retries,
                     backup_factory=(lambda:new_miner(True)) if args.backup_host else None))
        except KeyboardInterrupt:
            print('stopped by operator', file=sys.stderr)


if __name__ == '__main__':
    main()