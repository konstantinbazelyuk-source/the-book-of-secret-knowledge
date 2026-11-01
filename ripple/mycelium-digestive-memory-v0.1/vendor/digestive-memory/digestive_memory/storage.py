"""Transactional single-process SQLite backend with explicit source lineage."""
import sqlite3
from contextlib import contextmanager

SCHEMA = '''
CREATE TABLE IF NOT EXISTS events (
 scope TEXT NOT NULL, source_id TEXT NOT NULL, text TEXT NOT NULL,
 observed_at INTEGER NOT NULL, authority INTEGER NOT NULL, signature TEXT NOT NULL,
 tier TEXT NOT NULL DEFAULT 'hot', PRIMARY KEY(scope,source_id)
);
CREATE TABLE IF NOT EXISTS facts (
 id TEXT PRIMARY KEY, scope TEXT NOT NULL, source_id TEXT NOT NULL,
 subject TEXT NOT NULL, predicate TEXT NOT NULL, value TEXT NOT NULL,
 quote TEXT NOT NULL, valid_from INTEGER NOT NULL, valid_to INTEGER,
 expires_at INTEGER, confidence REAL NOT NULL, status TEXT NOT NULL,
 FOREIGN KEY(scope,source_id) REFERENCES events(scope,source_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS fact_slot ON facts(scope,subject,predicate);
CREATE TABLE IF NOT EXISTS digests (
 id TEXT PRIMARY KEY, scope TEXT NOT NULL, body TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS digest_sources (
 digest_id TEXT NOT NULL, scope TEXT NOT NULL, source_id TEXT NOT NULL,
 PRIMARY KEY(digest_id,scope,source_id),
 FOREIGN KEY(digest_id) REFERENCES digests(id) ON DELETE CASCADE,
 FOREIGN KEY(scope,source_id) REFERENCES events(scope,source_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS tombstones (
 scope TEXT NOT NULL, source_hash TEXT NOT NULL, PRIMARY KEY(scope,source_hash)
);
'''


class Store:
    def __init__(self, path):
        self.db = sqlite3.connect(str(path), isolation_level=None, timeout=5)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA secure_delete=ON')
        self.db.executescript(SCHEMA)

    @contextmanager
    def transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield self.db
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise

    def facts(self, key):
        rows = self.db.execute('''SELECT f.*, e.observed_at, e.authority FROM facts f
            JOIN events e ON f.scope=e.scope AND f.source_id=e.source_id
            WHERE f.scope=? AND f.status='accepted' ''', (key,)).fetchall()
        return [dict(row) for row in rows]

    def close(self):
        self.db.close()
