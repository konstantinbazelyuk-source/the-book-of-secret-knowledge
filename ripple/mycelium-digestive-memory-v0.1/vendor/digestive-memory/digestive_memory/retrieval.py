"""Deterministic lexical baseline. Replace with hybrid retrieval at scale."""
import re
from .contracts import Recall


def terms(text: str) -> set[str]:
    return set(re.findall(r'\w+', text.casefold()))


def rank(recalls: list[Recall], query: str, limit: int) -> list[Recall]:
    q = terms(query)
    scored = []
    for r in recalls:
        content = ' '.join((r.subject,r.predicate,r.value or '',*r.alternatives))
        score = len(q & terms(content))/len(q) if q else 1.0
        if score > 0:
            scored.append((score,r))
    scored.sort(key=lambda x:(-x[0],-(x[1].valid_from or 0),x[1].subject,x[1].predicate))
    return [r for _,r in scored[:limit]]
