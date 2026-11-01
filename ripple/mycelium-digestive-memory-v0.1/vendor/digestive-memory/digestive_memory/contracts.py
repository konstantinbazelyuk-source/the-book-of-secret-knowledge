"""Public contracts. Timestamps are integer UTC epoch seconds."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Scope:
    tenant: str
    owner: str
    project: str


@dataclass(frozen=True)
class Event:
    source_id: str
    text: str
    observed_at: int
    origin: str = 'user'


@dataclass(frozen=True)
class Candidate:
    subject: str
    predicate: str
    value: str
    start: int
    end: int
    valid_from: int
    valid_to: int | None = None
    expires_at: int | None = None
    confidence: float = 1.0


@dataclass(frozen=True)
class Policy:
    max_event_bytes: int = 65536
    max_candidates: int = 128
    min_confidence: float = .75
    context_candidates: int = 50


@dataclass(frozen=True)
class Receipt:
    source_id: str
    status: str
    absorbed: int
    quarantined: int


@dataclass(frozen=True)
class Recall:
    subject: str
    predicate: str
    status: str
    value: str | None = None
    alternatives: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    evidence: tuple[dict, ...] = ()
    valid_from: int | None = None
