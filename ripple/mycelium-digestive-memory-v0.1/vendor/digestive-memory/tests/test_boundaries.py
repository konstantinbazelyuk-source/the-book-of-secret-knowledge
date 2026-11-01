"""Boundary and real-database failure cases."""
import json
import sqlite3
import unittest
from digestive_memory import Candidate, Event, Memory, Policy, Scope
from tests.test_memory import S, add


class BoundaryTests(unittest.TestCase):
    def test_candidate_iterable_consumption_is_bounded(self):
        consumed=[]
        def stream():
            for i in range(10000):
                consumed.append(i)
                yield Candidate('Mira','city','Dallas',0,6,10)
        with Memory(policy=Policy(max_candidates=1),clock=lambda:100) as m:
            with self.assertRaises(ValueError):
                m.ingest(S,Event('a','Dallas',10),stream())
            self.assertLessEqual(len(consumed),2)
            self.assertEqual(m.health(S)['events'],0)

    def test_maximum_source_id_can_store_plain_text(self):
        with Memory(clock=lambda:100) as m:
            m.ingest(S,Event('x'*256,'plain workshop text',10))
            self.assertEqual(m.search(S,'workshop')[0].value,'plain workshop text')

    def test_evidence_order_is_independent_of_fact_ids(self):
        with Memory(clock=lambda:100) as m:
            text='Dallas Paris'
            m.ingest(S,Event('a',text,10),[Candidate('Mira','city','Dallas',0,6,10),Candidate('Mira','city','Paris',7,12,10)])
            m._store.db.execute("UPDATE facts SET id='zz' WHERE value='Dallas'")
            m._store.db.execute("UPDATE facts SET id='aa' WHERE value='Paris'")
            r=m.recall(S,'Mira','city')
            self.assertEqual([e['quote'] for e in r.evidence],['Dallas','Paris'])

    def test_digest_records_its_snapshot_times(self):
        with Memory(clock=lambda:100) as m:
            add(m,'a','Dallas')
            m.consolidate(S,as_of=20,known_at=30)
            body=json.loads(m._store.db.execute('SELECT body FROM digests').fetchone()[0])
            self.assertEqual(body['snapshot'],{'as_of':20,'known_at':30,'created_at':100})
            self.assertEqual(body['items'][0]['value'],'Dallas')

    def test_sql_failure_after_first_fact_rolls_back_event(self):
        with Memory(clock=lambda:100) as m:
            m._store.db.execute("""CREATE TRIGGER reject_bad BEFORE INSERT ON facts
                WHEN NEW.predicate='bad' BEGIN SELECT RAISE(ABORT,'injected constraint'); END""")
            a = Candidate('Mira','city','Dallas',0,6,10)
            b = Candidate('Mira','bad','Dallas',0,6,10)
            with self.assertRaises(sqlite3.IntegrityError):
                m.ingest(S,Event('a','Dallas',10),[a,b])
            self.assertEqual(m.health(S)['events'],0)
            self.assertEqual(m.health(S)['accepted_facts'],0)

    def test_expired_new_version_does_not_resurrect_old_value(self):
        with Memory(clock=lambda:100) as m:
            add(m,'old','Dallas',at=10)
            add(m,'new','Paris',at=20,expires=50)
            self.assertEqual(m.recall(S,'Mira','city').status,'missing')

    def test_historical_request_cannot_bypass_memory_expiry(self):
        with Memory(clock=lambda:100) as m:
            add(m,'a','Dallas',at=10,expires=50)
            self.assertEqual(m.recall(S,'Mira','city',as_of=20).status,'missing')

    def test_tombstone_is_scoped_to_project_and_tenant(self):
        with Memory(clock=lambda:100) as m:
            m.forget(S,'a')
            for scope in [Scope('tenant-b','owner-a','project-a'), Scope('tenant-a','owner-a','project-b')]:
                add(m,'a','Paris',scope=scope)
                self.assertEqual(m.recall(scope,'Mira','city').value,'Paris')

    def test_candidate_count_bound_and_span_bound(self):
        with Memory(policy=Policy(max_candidates=1),clock=lambda:100) as m:
            with self.assertRaises(ValueError):
                m.ingest(S,Event('a','Mira | city | Dallas\nMira | color | Blue',10))
            with self.assertRaises(ValueError):
                m.ingest(S,Event('b','Dallas',10),[Candidate('Mira','city','Dallas',0,7,10)])
            self.assertEqual(m.health(S)['events'],0)

    def test_scope_delimiters_cannot_collide(self):
        a,b=Scope('a/b','c','d'),Scope('a','b/c','d')
        with Memory(clock=lambda:100) as m:
            add(m,'a','Dallas',scope=a)
            self.assertEqual(m.recall(b,'Mira','city').status,'missing')

    def test_sql_metacharacters_are_data(self):
        value="Paris'; DROP TABLE events; --"
        with Memory(clock=lambda:100) as m:
            add(m,'a',value)
            self.assertEqual(m.recall(S,'Mira','city').value,value)
            self.assertEqual(m.health(S)['events'],1)

    def test_all_byte_budget_boundaries(self):
        with Memory(clock=lambda:100) as m:
            add(m,'a','日本語 "blue" \\ newline\nline')
            full=m.context(S,'Mira',budget_bytes=10000)
            size=len(json.dumps(full,ensure_ascii=False,separators=(',',':')).encode())
            self.assertEqual(len(m.context(S,'Mira',budget_bytes=size)['items']),1)
            self.assertEqual(m.context(S,'Mira',budget_bytes=size-1)['items'],[])


if __name__=='__main__':
    unittest.main()
