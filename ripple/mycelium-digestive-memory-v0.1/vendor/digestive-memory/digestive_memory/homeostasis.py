"""Content-free scoped counters; no automatic learned controller."""


def health(store, key):
    db = store.db
    result = {}
    for name,table,extra in [('events','events',''),('accepted_facts','facts'," AND status='accepted'"),
                             ('quarantined_facts','facts'," AND status='quarantined'"),
                             ('cold_events','events'," AND tier='cold'"),('digests','digests',''),('tombstones','tombstones','')]:
        result[name] = db.execute(f'SELECT count(*) FROM {table} WHERE scope=?{extra}',(key,)).fetchone()[0]
    return result
