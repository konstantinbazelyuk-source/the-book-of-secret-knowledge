"""Signed-wave **work** pipeline for the original mixed Regulatory Colony.

Positive and negative axes are separate, disjoint Bitcoin extranonce2 streams,
not invented shortcut hashes or simulated neurons.  Each position maps to a
predefined real nonce-batch workload.  Every candidate is still SHA256d-hashed
by the existing worker.  Original Regulatory equations are not modified.
"""
from __future__ import annotations
from dataclasses import dataclass
import math


@dataclass
class Axis:
    name: str
    en2: int
    dispatched: int = 0
    hashes_assigned: int = 0


class SpikeAxisDispatch:
    """Convert real signed network changes into pre-set, exclusive work streams.

    A negative axis is not 'negative hashes': it is independent useful nonce
    space, with a different extranonce2 and consequently a different header.
    Both streams can run concurrently.  Jobs still belong solely to WorkMap.
    """
    def __init__(self, base_chunk: int, extranonce2_size: int):
        if not 1 <= extranonce2_size <= 16 or not 1 <= base_chunk <= 500000:
            raise ValueError('invalid Bitcoin nonce space or batch size')
        self.limit=1 << (8 * extranonce2_size)
        self.base_chunk=base_chunk
        self.axes=[Axis('positive',0), Axis('negative',1)]
        self.phase=1
        self.level=1
        self.previous=None
        self.center=None
        self.tick=0
        self.dispatches=0
        self.prefixes={}
        self.transitions=[]

    def wave_update(self, report: dict):
        """Source-derived signed membrane movement; level bins are new mining policy.

        Normalization uses source network feature norm.  Bins are declared
        controller parameters, *not* hidden original Ripple equations.
        """
        if not isinstance(report,dict):raise ValueError('missing source report')
        membrane=float(report['average_membrane'])
        norm=float(report['feature_norm'])
        if not math.isfinite(membrane) or not math.isfinite(norm) or norm<0:
            raise ValueError('invalid original network output')
        if self.previous is None:
            self.previous=membrane
            self.center=membrane
            return self.phase*self.level
        delta=membrane-self.previous
        self.previous=membrane
        self.center += .15*(membrane-self.center)
        scaled=abs(delta)/max(.05,norm)
        level=3 if scaled>=.20 else 2 if scaled>=.08 else 1
        if delta>0:self.phase=1
        elif delta<0:self.phase=-1
        self.level=level
        self.tick+=1
        self.transitions.append({'tick':self.tick,'position':self.phase*self.level,
                                 'delta':delta,'normalized':scaled,'center':self.center})
        self.transitions=self.transitions[-32:]
        return self.phase*self.level

    def _lane_batch(self, lane: Axis, suggested_chunk: int):
        base=max(1,min(int(suggested_chunk),500000))
        # The exact pre-programmed response at +/-1,2,3 is task size.
        # Neither direction discards work.  Batch counts are bounded by the
        # existing native worker API, not the number of assignments possible.
        if lane.name=='positive':
            factors=(1.0,1.5,2.0)
        else:
            factors=(1.0,.75,.50)
        factor=factors[self.level-1]
        return max(1,min(500000,round(base*factor)))

    def dispatch(self, workmap, key, worker, suggested_chunk):
        """Return one genuinely claimed, unshared work interval or None.

        Alternate lanes, prioritizing the current spike sign first.  WorkMap
        may transparently re-lease a crashed worker's interval from either
        stream; the returned extranonce2 always determines the actual prefix.
        """
        first=0 if self.phase>0 else 1
        index=(first + self.dispatches)%2
        for offset in (0,1):
            lane=self.axes[(index+offset)%2]
            while lane.en2<self.limit:
                cell=workmap.claim(key,lane.en2,worker,self._lane_batch(lane,suggested_chunk))
                if cell is None:
                    lane.en2+=2
                    continue
                actual=self.axes[cell['en2']%2]
                actual.dispatched+=1
                actual.hashes_assigned+=cell['count']
                self.dispatches+=1
                return cell, actual.name
        return None

    def prefix(self, work, cell, header_prefix):
        en2=cell['en2']
        if en2 not in self.prefixes:
            self.prefixes[en2]=header_prefix(work,en2)
        return self.prefixes[en2]

    def snapshot(self):
        return {'position':self.phase*self.level,'prepared_axes':['positive','negative'],
                'dispatched':self.dispatches,'lanes':{a.name:{'assignments':a.dispatched,
                'nonces_assigned':a.hashes_assigned,'active_en2':a.en2} for a in self.axes},
                'recent_transitions':self.transitions[-6:]}