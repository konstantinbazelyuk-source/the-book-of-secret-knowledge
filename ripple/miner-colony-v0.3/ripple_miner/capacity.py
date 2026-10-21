"""Bounded adaptive dispatcher; selection uses measured hash throughput, not invented genes.

Fitness: EWMA hashes/second penalized by observed task failure and latency.
Baseline mode: rotating round-robin; adaptive mode: greatest measured capacity.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import os
import time

@dataclass
class WorkerMeasure:
    name: str
    hps: float = 0.0
    tasks: int = 0
    failures: int = 0
    busy: bool = False
    last_seen: float = 0.0

class AdaptiveColony:
    def __init__(self, capacity=None, mode='adaptive'):
        if mode not in ('adaptive','round_robin'):raise ValueError('unknown mode')
        bound = max(1,(os.cpu_count() or 1)-1)
        self.capacity = max(1, min(int(capacity or bound),bound,32))
        self.mode=mode
        self.workers = {f'cpu-{i}': WorkerMeasure(f'cpu-{i}') for i in range(self.capacity)}
        self.round = 0
        self.history = []
    def available(self):
        return [w for w in self.workers.values() if not w.busy]
    def recruit(self):
        free=self.available()
        if not free:return None
        if self.mode == 'round_robin':
            selected = free[self.round % len(free)]
            self.round += 1
        else:
            # Unmeasured workers first: sample all before exploiting measured fitness.
            selected = min(free,key=lambda w:(w.tasks>0,-w.hps,w.failures,w.name))
        selected.busy=True
        return selected.name
    def record(self, name, count, elapsed, success=True):
        w=self.workers[name]
        if count < 0 or elapsed < 0:raise ValueError('invalid observation')
        sample=count/max(elapsed,1e-9) if success else 0.
        w.hps=sample if w.tasks==0 else 0.3*sample+0.7*w.hps
        w.tasks+=1
        w.failures+=0 if success else 1
        w.last_seen=time.time()
        w.busy=False
        self.history.append({'name':name,'hashes':count if success else 0,'elapsed':elapsed,'ok':bool(success)})
        if len(self.history)>500:self.history=self.history[-500:]
    def snapshot(self):
        return {'mode':self.mode,'capacity':self.capacity,'workers':[vars(w).copy() for w in self.workers.values()]}


def compare_schedules(durations_by_worker, iterations=100):
    """Deterministic MODEL for regression tests; explicitly not physical measurements."""
    if not durations_by_worker or min(durations_by_worker)<=0:raise ValueError('positive timings required')
    models={}
    for mode in ('round_robin','adaptive'):
        end=[0.]*len(durations_by_worker)
        samples=[None]*len(durations_by_worker)
        for j in range(iterations):
            index=(j%len(end)) if mode=='round_robin' else min(range(len(end)),key=lambda i:end[i])
            elapsed=float(durations_by_worker[index]);end[index]+=elapsed
            samples[index]=elapsed
        models[mode]={'makespan_model_seconds':max(end),'assigned_by_worker':[round(v/durations_by_worker[i]) for i,v in enumerate(end)]}
    return {'classification':'analytical deterministic schedule model, not hashing benchmark','results':models}
