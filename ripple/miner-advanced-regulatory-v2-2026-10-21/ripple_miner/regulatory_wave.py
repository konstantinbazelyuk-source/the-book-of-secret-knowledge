"""Authentic Regulatory Colony v2 as a mining *control-plane* operator.

The archived source under advanced/ is byte-identical to Ripple Heterogeneous
Mathematical Fusion v1. It is kept outside the Bitcoin SHA256d data plane.
Its 16 Delta/Daughter/Charlie cells read eight *measured* [0,1] mining signals
and change the size of the next REAL nonce assignments. All candidate digests
continue to be verified against Bitcoin's reference double-SHA256 function.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import time

NODE_WORKER = Path(__file__).parent / 'advanced' / 'node_worker.mjs'


class RegulatoryWave:
    def __init__(self, base_chunk: int, *, node: str | None = None, update_every: int = 12):
        if not 100 <= base_chunk <= 500000:
            raise ValueError('base nonce chunk must be within 100..500000')
        if update_every < 1:
            raise ValueError('update_every must be positive')
        self.base_chunk = int(base_chunk)
        self.chunk = int(base_chunk)
        self.update_every = int(update_every)
        self.completed = 0
        self.total_hashes = 0
        self.total_elapsed = 0.0
        self.failures = 0
        self.last_signal = [0.0] * 8
        self.steps = 0
        self.transitions = []
        self.last_network = None
        source_root = NODE_WORKER.parent
        pinned = json.loads((source_root/'ORIGINAL_SHA256.json').read_text())
        for rel, digest in pinned.items():
            actual = hashlib.sha256((source_root/rel).read_bytes()).hexdigest()
            if actual != digest:
                raise RuntimeError('archived Ripple Regulatory source changed: '+rel)
        self.source_sha256 = hashlib.sha256(NODE_WORKER.read_bytes()).hexdigest()
        exe = node or os.environ.get('RIPPLE_NODE_BIN') or os.environ.get('RIPPLE_NODE') or 'node'
        self.proc = subprocess.Popen([exe, str(NODE_WORKER)], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                     text=True, bufsize=1)
        try:
            hello = self._command({'op': 'status'})
            kinds = hello.get('kinds')
            if not isinstance(kinds, list) or len(kinds) != 16 or set(kinds) != {'delta', 'daughter', 'charlie'}:
                raise RuntimeError('expected original advanced Regulatory v2 16-cell mixed network')
            self.kinds = kinds
        except Exception:
            self.close()
            raise

    def _command(self, msg: dict) -> dict:
        if self.proc.poll() is not None:
            raise RuntimeError('advanced regulatory engine terminated')
        self.proc.stdin.write(json.dumps(msg, separators=(',', ':')) + '\n')
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError('advanced regulatory engine returned EOF')
        response = json.loads(line)
        if response.get('ok') is not True:
            raise RuntimeError('advanced Ripple engine error: ' + str(response.get('error', 'unknown'))[:180])
        return response['result']

    def observe(self, *, hashes: int, elapsed: float, active: int, capacity: int,
                pending_shares: int = 0, rejected_shares: int = 0, paused: bool = False) -> bool:
        """A real finished mining assignment conditions the next waveform tick.

        Updating only after N completed work cells amortizes the Node control
        process and avoids pretending a mathematical spike is a Bitcoin hash.
        """
        if hashes < 0 or elapsed <= 0 or capacity < 1 or active < 0 or pending_shares < 0 or rejected_shares < 0:
            raise ValueError('invalid mining observations')
        self.completed += 1
        self.total_hashes += hashes
        self.total_elapsed += elapsed
        if hashes == 0:
            self.failures += 1
        if self.completed % self.update_every:
            return False
        speed = self.total_hashes / max(self.total_elapsed, 1e-12)
        # Bounded physically measured signals; no fabricated RGB sensor data.
        # Eight independent signal channels are passed to original v2 unchanged.
        hps_score = speed / (speed + 1_000_000.)
        utilization = min(1., active / capacity)
        work_scale = self.chunk / 500000.
        failure_fraction = min(1., self.failures / self.completed)
        queue_pressure = min(1., pending_shares / 128.)
        share_rejections = min(1., rejected_shares / 32.)
        latency_pressure = min(1., max(0., elapsed) / 2.)
        alive = 0. if paused else 1.
        frame = [hps_score, utilization, work_scale, failure_fraction,
                 queue_pressure, share_rejections, latency_pressure, alive]
        self.last_signal = frame
        data = self._command({'op': 'step', 'frame': frame, 'regulatory': True, 'laboratory': False})
        reg = data['regulatory']
        if reg['cells'] != 16 or not math.isfinite(float(reg['average_membrane'])) or not math.isfinite(float(reg['feature_norm'])):
            raise RuntimeError('invalid advanced Ripple numerical output')
        # Causal link: recovered Regulatory Colony membrane and feature norm
        # *directly* set next REAL scanning size. With constant input, the
        # underlying recurrent state may still evolve, unlike fixed scheduling.
        state = float(reg['average_membrane'])
        norm = float(reg['feature_norm'])
        modifier = 1.0 + 0.50 * math.tanh(state + norm - 0.25)
        proposed = int(self.base_chunk * modifier)
        new_chunk = max(100, min(500000, proposed))
        old_chunk = self.chunk
        self.chunk = new_chunk
        self.steps = int(reg['steps'])
        self.last_network = {'average_membrane': state, 'feature_norm': norm,
                             'cells': 16, 'steps': self.steps}
        self.transitions.append({'completed_cells': self.completed, 'before': old_chunk,
                                 'after': new_chunk, 'measured_hps': speed,
                                 'signals': frame, 'network': self.last_network})
        self.transitions = self.transitions[-24:]
        return True

    def snapshot(self) -> dict:
        return {'engine': 'archived-regulatory-colony-v2',
                'source_sha256': self.source_sha256, 'cells': 16,
                'cell_kinds': self.kinds, 'completed_cells': self.completed,
                'real_hashes_observed': self.total_hashes, 'ticks': self.steps,
                'base_chunk': self.base_chunk, 'active_chunk': self.chunk,
                'network': self.last_network, 'recent_changes': self.transitions[-6:]}

    def close(self):
        if getattr(self, 'proc', None) is None:
            return
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=2)
        for pipe in (self.proc.stdin, self.proc.stdout):
            if pipe:
                pipe.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()