"""Single-valued temporal slots; deterministic conflicts remain visible."""
from .contracts import Recall


def resolve(rows: list[dict], subject: str, predicate: str, *, as_of: int, known_at: int, now: int) -> Recall:
    applicable = [r for r in rows if r['subject']==subject and r['predicate']==predicate
                  and r['observed_at'] <= known_at and r['valid_from'] <= as_of
                  and (r['valid_to'] is None or as_of < r['valid_to'])]
    if not applicable:
        return Recall(subject, predicate, 'missing')
    priority = max((r['authority'], r['valid_from']) for r in applicable)
    selected = [r for r in applicable if (r['authority'],r['valid_from']) == priority]
    # Expiry is evaluated at the actual clock, not a caller-controlled historical date.
    # Never fall back to an older claim merely because a later one expired.
    selected = [r for r in selected if r['expires_at'] is None or now < r['expires_at']]
    if not selected:
        return Recall(subject, predicate, 'missing')
    values = tuple(sorted(set(r['value'] for r in selected)))
    selected.sort(key=lambda r:(r['source_id'],r['value'],r['quote'],r['observed_at']))
    evidence = tuple({'source_id':r['source_id'], 'quote':r['quote'],
                      'observed_at':r['observed_at'], 'authority':r['authority']}
                     for r in selected)
    return Recall(subject, predicate, 'known' if len(values)==1 else 'conflict',
                  values[0] if len(values)==1 else None,
                  values if len(values)>1 else (),
                  tuple(sorted(set(r['source_id'] for r in selected))), evidence, priority[1])


def resolve_all(rows: list[dict], *, as_of: int, known_at: int, now: int) -> list[Recall]:
    slots = sorted(set((r['subject'],r['predicate']) for r in rows))
    # Group once; avoid scanning all rows independently for every slot.
    groups = {slot:[] for slot in slots}
    for row in rows:
        groups[(row['subject'],row['predicate'])].append(row)
    recalls = [resolve(groups[(s,p)],s,p,as_of=as_of,known_at=known_at,now=now) for s,p in slots]
    return [r for r in recalls if r.status != 'missing']
