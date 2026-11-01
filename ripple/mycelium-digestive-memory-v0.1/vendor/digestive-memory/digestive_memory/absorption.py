"""Select admission to usable memory; admission is not truth verification."""
from .contracts import Candidate, Event, Policy


def admission(candidate: Candidate, event: Event, policy: Policy) -> str:
    if event.origin == 'external' or candidate.confidence < policy.min_confidence:
        return 'quarantined'
    return 'accepted'
