"""Offline extraction. No semantic inference or external model calls."""
from typing import Protocol, Sequence
import hashlib
from .contracts import Candidate, Event


class Extractor(Protocol):
    def extract(self, event: Event) -> Sequence[Candidate]: ...


class DeclarativeExtractor:
    """Parse `subject | predicate | literal value`; other lines become episodes."""
    def extract(self, event: Event) -> list[Candidate]:
        candidates = []
        offset = 0
        for i, raw in enumerate(event.text.splitlines(keepends=True)):
            line = raw.strip()
            if line:
                parts = line.split('|', 2)
                if len(parts) == 3 and all(x.strip() for x in parts):
                    subject, predicate, value = (x.strip() for x in parts)
                    local = raw.index('|', raw.index('|')+1)+1
                    start = offset + local + raw[local:].index(value)
                else:
                    reference = hashlib.sha256(event.source_id.encode('utf-8')).hexdigest()
                    subject, predicate, value = 'episode', f'{reference}:{i}', line
                    start = offset + raw.index(line)
                candidates.append(Candidate(subject, predicate, value, start, start+len(value), event.observed_at))
            offset += len(raw)
        return candidates
