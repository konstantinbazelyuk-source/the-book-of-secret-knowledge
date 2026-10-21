"""Ripple-derived multi-rig colony: actual observations, bounded adaptive policy."""
from collections import deque
from dataclasses import dataclass, field
from time import time

@dataclass
class Cell:
    name: str
    host: str
    port: int = 4028
    history: deque = field(default_factory=lambda: deque(maxlen=24))
    signals: deque = field(default_factory=lambda: deque(maxlen=24))
    neuron_state: dict = field(default_factory=dict)
    last: dict = field(default_factory=dict)
    error: str = ''
    updated_at: float = 0

    def observe(self, report, error=''):
        self.error = str(error)[:260]
        self.updated_at = time()
        if error:
            self.last = {}
            return
        self.last = report
        h = report.get('hashrate_hps')
        if h is not None:
            h = float(h)
            prior = sum(self.history)/len(self.history) if self.history else h
            deviation = min(1, abs(h-prior)/max(1, prior))
            a, r = report.get('accepted'), report.get('rejected')
            rejects = min(1, float(r)/(float(a)+float(r))) if a is not None and r is not None and float(a)+float(r)>0 else 0
            temp = report.get('temperature_c')
            # Defined telemetry-to-RGB encoding, not an optical measurement.
            inhibition = max(0, min(1, (85-float(temp))/30)) if temp is not None else 1
            self.signals.append([deviation, rejects, inhibition])
            self.history.append(h)

    def assessment(self):
        report = self.last
        rate = report.get('hashrate_hps')
        temp = report.get('temperature_c')
        baseline = sum(self.history) / len(self.history) if self.history else None
        reasons = []
        if self.error:
            reasons.append('API offline: '+self.error)
        if rate is not None and baseline and len(self.history) >= 4 and rate < .72 * baseline:
            reasons.append('hashrate below 72% of recent measured baseline')
        if temp is not None and temp >= 85:
            reasons.append('reported device temperature >=85 C; inspect ASIC cooling')
        a, r = report.get('accepted'), report.get('rejected')
        if a is not None and r is not None and a+r > 0 and r/(a+r) >= .05:
            reasons.append('rejected share ratio >=5%')
        return {'name': self.name, 'host': self.host, 'port': self.port,
                'status': 'offline' if self.error else ('attention' if reasons else 'online' if report else 'pending'),
                'reasons': reasons, 'updated_at': self.updated_at, 'baseline_hps': baseline,
                'observations': len(self.history), 'ripple_neuron': self.neuron_state, **report}


def colony_summary(nodes):
    rows = [node.assessment() for node in nodes.values()]
    online = [n for n in rows if n['status'] in ('online', 'attention')]
    return {'nodes': rows, 'count': len(rows), 'active': len(online),
            'measured_asic_hashrate_hps': sum(n.get('hashrate_hps') or 0 for n in online),
            'alerts': [{'node': n['name'], 'details': n['reasons']} for n in rows if n['reasons']]}
