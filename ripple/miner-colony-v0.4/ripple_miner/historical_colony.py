"""Measurable CPU admission colony adapted from historical Ripple Mycelium and Forest.

Source relationships:
- Mycelium v0.1 README / colony.js: demand-sensitive expansion; <=2 recruits per
  observation interval, parent->child relationships, sustained-idle retirement.
- Charlie Forest v1.2 src/forest.py: bounded occupancy in neighbor space and
  suitability before establishing a new patch. Mining slots, *not* optical XYZ.
- MUSHROOM v3 / Ring v4 are preserved and studied, but not substituted for a
  software-hashing path. No neural activity implies more SHA256d throughput.

Here substrate positions are **reserved process slots**, budgeted by live host
capacity. They aren't new computers, synthetic forest biomass, or physical silicon.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque
import math
import os
import time
from .capacity import AdaptiveColony, WorkerMeasure


def xyz(index: int, width: int = 3):
    if index < 0: raise ValueError('negative index')
    return index % width, (index // width) % width, index // (width * width)


def adjacency(a, b):
    return sum(abs(i-j) for i,j in zip(a,b)) == 1


@dataclass
class ColonySite:
    name: str
    position: tuple[int,int,int]
    parent: str | None
    occupied: bool = False
    known: bool = False
    established_at: float | None = None
    last_result_hps: float | None = None
    children: set = field(default_factory=set)


class HistoricalColony(AdaptiveColony):
    """Real capacity-bound colony used by v0.3 ProcessPoolExecutor.

    Physical admission tokens are derived from a measured/passed worker ceiling;
    each occupied site corresponds to exactly one live worker *slot*. The
    workload itself is the existing, verified SHA256d nonce scanner. This layer
    controls dispatch only, and never changes Bitcoin share validity.
    """
    def __init__(self, capacity, *, clock=None, memory_limit=None):
        super().__init__(capacity,mode='adaptive')
        self.max_slots = self.capacity
        self._clock = clock or time.monotonic
        self.sites = {f'cpu-{i}':ColonySite(f'cpu-{i}', xyz(i), None) for i in range(self.max_slots)}
        self.established = set()
        self.transitions=[]
        self.last_tick=self._clock()-1.01
        self.low_since=None
        self.last_retired=-math.inf
        self._establish('cpu-0', parent=None)
        self.capacity=1
        self.memory_limit=memory_limit
        self.obs_completion=0
        self.observed_rate=0.
        self.wanted=self.max_slots
        self.last_budget=self.max_slots

    def _establish(self, name, *, parent):
        site=self.sites[name]
        if site.occupied: raise ValueError('site already occupied')
        if parent is not None and not adjacency(site.position,self.sites[parent].position):
            raise ValueError('new site must neighbor an occupied parent')
        site.occupied=True;site.known=True
        site.parent=parent;site.established_at=self._clock()
        self.established.add(name)
        if parent is not None:self.sites[parent].children.add(name)
        self.transitions.append({'event':'establish','site':name,'parent':parent,'at':site.established_at})

    def _retire(self, name):
        if name=='cpu-0' or not self.sites[name].occupied:raise ValueError('cannot retire root or empty site')
        if self.workers[name].busy:raise ValueError('cannot retire busy site')
        node=self.sites[name]
        # Keep a connected lattice. Retire leaf sites only.
        if node.children:raise ValueError('cannot retire parent with active children')
        self.established.remove(name);node.occupied=False
        self.sites[node.parent].children.remove(name)
        self.transitions.append({'event':'retire','site':name,'at':self._clock()})
        node.parent=None

    def admission_budget(self):
        """Never infer nonexistent thermal or power sensors. Memory is a hard cap
        when observable, preserving root and at least 384 MiB free headroom.
        """
        bound=self.max_slots
        try:
            import psutil
            avail=psutil.virtual_memory().available
            bound=min(bound,max(1,(avail-(512<<20))//(384<<20)))
            # A measured unsafe temperature can prevent additional recruitment.
            vals=[q.current for group in (psutil.sensors_temperatures() or {}).values()
                  for q in group if q.current is not None]
            if vals and max(vals)>=85: bound=1
        except (ImportError, OSError, AttributeError):pass
        return max(1,int(bound))

    def tick(self, *, demand: bool, now=None, budget_override=None):
        now=self._clock() if now is None else float(now)
        if now-self.last_tick<1.:return self.snapshot()
        self.last_tick=now
        bound = self.admission_budget() if budget_override is None else max(1,min(self.max_slots,int(budget_override)))
        self.last_budget=bound
        # Continuous valid Stratum work presents unbounded nonce-search demand.
        # Unlike Mycelium's finite chunk arrival, target here is remaining host
        # admission capacity. It is NOT a predicted effective hashing speed.
        self.wanted=bound if demand else 1
        if demand and len(self.established)<self.wanted:
            for _ in range(min(2,self.wanted-len(self.established))):
                frontier=[]
                for name,site in self.sites.items():
                    if site.occupied:continue
                    for parent in sorted(self.established):
                        if adjacency(site.position,self.sites[parent].position):
                            frontier.append((len(self.sites[parent].children),name,parent));break
                if not frontier:break
                _,child,parent=min(frontier)
                self._establish(child,parent=parent)
            self.low_since=None
        elif len(self.established)>self.wanted:
            if self.low_since is None:self.low_since=now
            if now-self.low_since>=15 and now-self.last_retired>=5:
                leaves=sorted([s for s in self.established if s!='cpu-0'
                    and not self.sites[s].children and not self.workers[s].busy],reverse=True)
                if leaves:
                    self._retire(leaves[0]);self.last_retired=now
        else:self.low_since=None
        self.capacity=len(self.established)+(1 if "remote-0" in self.workers else 0)
        return self.snapshot()

    def recruit(self):
        free=[self.workers[x] for x in sorted(self.established) if not self.workers[x].busy]
        if 'remote-0' in self.workers and not self.workers['remote-0'].busy:
            free.append(self.workers['remote-0'])
        if not free:return None
        # Preserve existing EWMA worker measurement as the selection metric.
        chosen=min(free,key=lambda w:(w.tasks>0,-w.hps,w.failures,w.name))
        chosen.busy=True
        return chosen.name

    def record(self,name,count,elapsed,success=True):
        super().record(name,count,elapsed,success)
        if name in self.sites:
            self.sites[name].last_result_hps=count/max(elapsed,1e-9) if success else 0.
        self.obs_completion+=1 if success else 0

    def snapshot(self):
        return {'policy':'historical_mycelium_forest_admission','occupied':len(self.established),
             'max_physical_slots':self.max_slots,'measured_admission_budget':self.last_budget,
             'sites':[{'name':s.name,'xyz':s.position,'parent':s.parent,
                       'occupied':s.occupied,'last_hps':s.last_result_hps}
                       for s in self.sites.values()],
             'completed_chunks_observed':self.obs_completion,
             'transitions':self.transitions[-100:]}