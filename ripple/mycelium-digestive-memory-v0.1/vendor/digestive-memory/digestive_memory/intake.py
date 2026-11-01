"""Input limits and identity validation, independent of source content."""
import math
import json
from .contracts import Candidate, Event, Policy, Scope

ORIGINS = {'external': 1, 'tool': 2, 'user': 3}


def label(value, name, limit=256):
    if not isinstance(value, str) or not value.strip() or len(value.encode('utf-8')) > limit:
        raise ValueError(f'invalid {name}')


def timestamp(value, name):
    if type(value) is not int or not 0 <= value <= 2**62:
        raise ValueError(f'invalid {name}: use nonnegative UTC epoch seconds')
    return value


def scope_key(scope: Scope) -> str:
    if not isinstance(scope, Scope):
        raise ValueError('Scope required')
    for k in ('tenant', 'owner', 'project'):
        label(getattr(scope, k), k)
    return json.dumps([scope.tenant, scope.owner, scope.project], ensure_ascii=False, separators=(',', ':'))


def validate_policy(policy: Policy):
    for name in ('max_event_bytes', 'max_candidates', 'context_candidates'):
        if type(getattr(policy, name)) is not int or getattr(policy, name) <= 0:
            raise ValueError(f'invalid policy {name}')
    if not isinstance(policy.min_confidence, (float, int)) or not math.isfinite(policy.min_confidence) or not 0 <= policy.min_confidence <= 1:
        raise ValueError('invalid confidence threshold')


def validate_event(event: Event, policy: Policy):
    if not isinstance(event, Event):
        raise ValueError('Event required')
    label(event.source_id, 'source_id')
    label(event.text, 'text', policy.max_event_bytes)
    timestamp(event.observed_at, 'observed_at')
    if event.origin not in ORIGINS:
        raise ValueError('unknown origin')


def validate_candidate(candidate: Candidate, event: Event):
    if not isinstance(candidate, Candidate):
        raise ValueError('Candidate required')
    for name in ('subject', 'predicate'):
        label(getattr(candidate, name), name)
    label(candidate.value, 'value', len(event.text.encode('utf-8')))
    if type(candidate.start) is not int or type(candidate.end) is not int or not 0 <= candidate.start < candidate.end <= len(event.text):
        raise ValueError('invalid source span')
    if candidate.value not in event.text[candidate.start:candidate.end]:
        raise ValueError('value is not linked to the cited source span')
    timestamp(candidate.valid_from, 'valid_from')
    if candidate.valid_to is not None:
        timestamp(candidate.valid_to, 'valid_to')
        if candidate.valid_to <= candidate.valid_from:
            raise ValueError('valid_to must follow valid_from')
    if candidate.expires_at is not None:
        timestamp(candidate.expires_at, 'expires_at')
    confidence = candidate.confidence
    if type(confidence) not in (float, int) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError('confidence must be finite and between zero and one')
