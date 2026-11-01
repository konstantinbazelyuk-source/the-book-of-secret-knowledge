"""Facade composing the digestive memory stages."""
from dataclasses import asdict
import hashlib
import json
import time
import uuid
from itertools import islice
from .contracts import Candidate, Event, Policy, Receipt, Scope
from .intake import ORIGINS, label, scope_key, timestamp, validate_candidate, validate_event, validate_policy
from .digestion import DeclarativeExtractor
from .absorption import admission
from .storage import Store
from .consolidation import resolve, resolve_all
from .retrieval import rank
from .context import pack
from . import retention, excretion, homeostasis


class Memory:
    def __init__(self, path=':memory:', *, policy=None, extractor=None, clock=None):
        self.policy = policy or Policy()
        validate_policy(self.policy)
        self.extractor = extractor or DeclarativeExtractor()
        self.clock = clock or (lambda:int(time.time()))
        self._store = Store(path)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        self._store.close()

    def ingest(self, scope: Scope, event: Event, candidates=None) -> Receipt:
        key = scope_key(scope)
        validate_event(event,self.policy)
        incoming = self.extractor.extract(event) if candidates is None else candidates
        candidates = tuple(islice(incoming,self.policy.max_candidates+1))
        if len(candidates) > self.policy.max_candidates:
            raise ValueError('candidate limit exceeded')
        for c in candidates:
            validate_candidate(c,event)
        payload = {'event':asdict(event),'candidates':[asdict(c) for c in candidates]}
        signature = hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,allow_nan=False).encode()).hexdigest()
        with self._store.transaction() as db:
            if db.execute('SELECT 1 FROM tombstones WHERE scope=? AND source_hash=?',(key,excretion.source_hash(event.source_id))).fetchone():
                raise ValueError('source was revoked; replay denied')
            old = db.execute('SELECT signature FROM events WHERE scope=? AND source_id=?',(key,event.source_id)).fetchone()
            if old:
                if old['signature'] != signature:
                    raise ValueError('source id already exists with a different payload')
                counts = dict(db.execute('SELECT status,count(*) FROM facts WHERE scope=? AND source_id=? GROUP BY status',(key,event.source_id)))
                return Receipt(event.source_id,'replayed',counts.get('accepted',0),counts.get('quarantined',0))
            db.execute('INSERT INTO events(scope,source_id,text,observed_at,authority,signature) VALUES(?,?,?,?,?,?)',
                       (key,event.source_id,event.text,event.observed_at,ORIGINS[event.origin],signature))
            accepted = quarantined = 0
            for c in candidates:
                status = admission(c,event,self.policy)
                accepted += status == 'accepted'
                quarantined += status == 'quarantined'
                db.execute('INSERT INTO facts VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
                    (uuid.uuid4().hex,key,event.source_id,c.subject,c.predicate,c.value,event.text[c.start:c.end],
                     c.valid_from,c.valid_to,c.expires_at,c.confidence,status))
            return Receipt(event.source_id,'stored',accepted,quarantined)

    def _times(self, as_of, known_at):
        now = timestamp(self.clock(),'clock')
        return {'as_of':now if as_of is None else timestamp(as_of,'as_of'),
                'known_at':now if known_at is None else timestamp(known_at,'known_at'),'now':now}

    def recall(self, scope: Scope, subject: str, predicate: str, *, as_of=None, known_at=None):
        key = scope_key(scope)
        label(subject,'subject'); label(predicate,'predicate')
        return resolve(self._store.facts(key),subject,predicate,**self._times(as_of,known_at))

    def search(self, scope: Scope, query: str, *, limit=10, as_of=None, known_at=None):
        key = scope_key(scope)
        if not isinstance(query,str) or len(query.encode('utf-8')) > self.policy.max_event_bytes:
            raise ValueError('invalid query')
        if type(limit) is not int or limit < 0:
            raise ValueError('limit must be a nonnegative integer')
        recalls = resolve_all(self._store.facts(key),**self._times(as_of,known_at))
        return rank(recalls,query,limit)

    def context(self, scope: Scope, query: str, *, budget_bytes=8192, as_of=None, known_at=None):
        recalls = self.search(scope,query,limit=self.policy.context_candidates,as_of=as_of,known_at=known_at)
        return pack(recalls,budget_bytes)

    def consolidate(self, scope: Scope, *, as_of=None, known_at=None):
        key = scope_key(scope)
        times = self._times(as_of,known_at)
        recalls = resolve_all(self._store.facts(key),**times)
        snapshot = {'as_of':times['as_of'],'known_at':times['known_at'],'created_at':times['now']}
        return retention.consolidate(self._store,key,recalls,snapshot)

    def archive(self, scope: Scope, *, before: int):
        return retention.archive(self._store,scope_key(scope),timestamp(before,'before'))

    def forget(self, scope: Scope, source_id: str):
        label(source_id,'source_id')
        return excretion.forget(self._store,scope_key(scope),source_id)

    def health(self, scope: Scope):
        return homeostasis.health(self._store,scope_key(scope))
