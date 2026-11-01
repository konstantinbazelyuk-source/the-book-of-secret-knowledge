"""Cold tier and lossless current-slot digests, with explicit provenance."""
from dataclasses import asdict
import hashlib
import json


def archive(store, key, before):
    with store.transaction() as db:
        cur = db.execute("UPDATE events SET tier='cold' WHERE scope=? AND observed_at<? AND tier!='cold'",(key,before))
        return cur.rowcount


def consolidate(store, key, recalls, snapshot):
    groups = {}
    for r in recalls:
        groups.setdefault(r.subject,[]).append(r)
    ids = []
    with store.transaction() as db:
        db.execute('DELETE FROM digests WHERE scope=?',(key,))
        for subject, group in sorted(groups.items()):
            body = json.dumps({'snapshot':snapshot,'items':[asdict(r) for r in group]},ensure_ascii=False,sort_keys=True,separators=(',',':'))
            digest_id = hashlib.sha256((key+'\n'+body).encode()).hexdigest()
            db.execute('INSERT INTO digests VALUES(?,?,?)',(digest_id,key,body))
            for source in sorted(set(s for r in group for s in r.source_ids)):
                db.execute('INSERT INTO digest_sources VALUES(?,?,?)',(digest_id,key,source))
            ids.append(digest_id)
    return ids
