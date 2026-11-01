"""Logical erasure plus replay tombstones; backups are the host's concern."""
import hashlib


def source_hash(source_id: str) -> str:
    return hashlib.sha256(source_id.encode('utf-8')).hexdigest()


def forget(store, key, source_id):
    with store.transaction() as db:
        dependent = [r[0] for r in db.execute('SELECT digest_id FROM digest_sources WHERE scope=? AND source_id=?',(key,source_id))]
        facts = db.execute('SELECT count(*) FROM facts WHERE scope=? AND source_id=?',(key,source_id)).fetchone()[0]
        for digest in dependent:
            db.execute('DELETE FROM digests WHERE scope=? AND id=?',(key,digest))
        removed = db.execute('DELETE FROM events WHERE scope=? AND source_id=?',(key,source_id)).rowcount
        db.execute('INSERT OR IGNORE INTO tombstones VALUES(?,?)',(key,source_hash(source_id)))
        return {'events_deleted':removed,'facts_deleted':facts,'digests_deleted':len(dependent),'tombstone':True}
