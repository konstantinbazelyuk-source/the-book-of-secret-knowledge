"""Transactional nonce-space colony map. Cells ARE allocated SHA256d work, not pixels.

The input work_key must uniquely identify the Stratum session and immutable job payload.
Cell coordinates are 3D addresses of contiguous nonce ranges within one extranonce2.
SQLite leases permit crash recovery but a crashed worker may have partially hashed a
chunk: incomplete chunks can be recomputed; no completed chunk is reassigned.
"""
from __future__ import annotations
import json
import sqlite3
import threading
import time
from pathlib import Path

UINT32_SPACE = 1 << 32
GRID_SIDE = 64


def coords(segment: int) -> tuple[int, int, int]:
    if segment < 0:
        raise ValueError('negative segment')
    return (segment % GRID_SIDE, (segment // GRID_SIDE) % GRID_SIDE,
            segment // (GRID_SIDE * GRID_SIDE))


class WorkMap:
    def __init__(self, filename):
        path = Path(filename).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path, check_same_thread=False, timeout=15)
        self.lock = threading.RLock()
        self.connection.execute('PRAGMA journal_mode=WAL')
        self.connection.execute('PRAGMA busy_timeout=15000')
        with self.connection:
            self.connection.executescript('''
                CREATE TABLE IF NOT EXISTS streams (
                  work_key TEXT NOT NULL, en2 INTEGER NOT NULL,
                  cursor INTEGER NOT NULL DEFAULT 0,
                  next_segment INTEGER NOT NULL DEFAULT 0,
                  PRIMARY KEY(work_key,en2));
                CREATE TABLE IF NOT EXISTS cells (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  work_key TEXT NOT NULL, en2 INTEGER NOT NULL, segment INTEGER NOT NULL,
                  x INTEGER NOT NULL, y INTEGER NOT NULL, z INTEGER NOT NULL,
                  start_nonce INTEGER NOT NULL, count INTEGER NOT NULL,
                  worker TEXT NOT NULL, status TEXT NOT NULL,
                  lease_until REAL NOT NULL, attempts INTEGER NOT NULL DEFAULT 1,
                  hashes_done INTEGER NOT NULL DEFAULT 0,
                  elapsed REAL, created REAL NOT NULL, updated REAL NOT NULL,
                  UNIQUE(work_key,en2,start_nonce));
                CREATE INDEX IF NOT EXISTS cell_status ON cells(work_key,status,lease_until);
                CREATE TABLE IF NOT EXISTS events (
                  id INTEGER PRIMARY KEY AUTOINCREMENT, at REAL NOT NULL,
                  action TEXT NOT NULL, data TEXT NOT NULL);
            ''')

    def _event(self, action, data):
        self.connection.execute('INSERT INTO events(at,action,data) VALUES(?,?,?)',
                                (time.time(), action, json.dumps(data, sort_keys=True)[:3000]))

    def claim(self, work_key: str, en2: int, worker: str, count: int,
              *, lease_seconds=120., limit=UINT32_SPACE):
        if not isinstance(work_key, str) or not 12 <= len(work_key) <= 128:
            raise ValueError('invalid work key')
        if not isinstance(worker, str) or not 1 <= len(worker) <= 96:
            raise ValueError('invalid worker id')
        if type(en2) is not int or en2 < 0 or type(count) is not int or not 1 <= count <= 500000:
            raise ValueError('invalid allocation bounds')
        if type(limit) is not int or not 1 <= limit <= UINT32_SPACE or not 1 <= lease_seconds <= 3600:
            raise ValueError('invalid search-space or lease')
        now = time.time()
        with self.lock, self.connection:
            # Expired leases for THIS work identity may be retried, preserving original range.
            row = self.connection.execute('''SELECT id,en2,start_nonce,count,segment,attempts
                FROM cells WHERE work_key=? AND status='leased' AND lease_until<?
                ORDER BY updated,id LIMIT 1''', (work_key, now)).fetchone()
            if row:
                cid, old_en2, start, size, segment, attempts = row
                self.connection.execute('''UPDATE cells SET worker=?, lease_until=?,
                    attempts=?, updated=? WHERE id=?''',
                    (worker, now + lease_seconds, attempts + 1, now, cid))
                self._event('reclaimed', {'cell':cid,'worker':worker,'attempts':attempts+1})
                return dict(id=cid,en2=old_en2,start=start,count=size,segment=segment,
                            xyz=coords(segment),reclaimed=True)
            self.connection.execute('INSERT OR IGNORE INTO streams(work_key,en2) VALUES(?,?)', (work_key,en2))
            cursor, segment = self.connection.execute('SELECT cursor,next_segment FROM streams WHERE work_key=? AND en2=?', (work_key,en2)).fetchone()
            if cursor >= limit:
                return None
            size = min(count, limit - cursor)
            xyz = coords(segment)
            self.connection.execute('UPDATE streams SET cursor=?,next_segment=? WHERE work_key=? AND en2=?',
                                    (cursor+size,segment+1,work_key,en2))
            cur = self.connection.execute('''INSERT INTO cells (
                work_key,en2,segment,x,y,z,start_nonce,count,worker,status,
                lease_until,created,updated) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (work_key,en2,segment,*xyz,cursor,size,worker,'leased',now+lease_seconds,now,now))
            return dict(id=cur.lastrowid,en2=en2,start=cursor,count=size,segment=segment,xyz=xyz,reclaimed=False)

    def finish(self, cell_id, worker, *, hashes_done, elapsed):
        if type(hashes_done) is not int or hashes_done < 0 or elapsed < 0:
            raise ValueError('invalid result')
        with self.lock, self.connection:
            row = self.connection.execute('SELECT count,status,worker FROM cells WHERE id=?', (cell_id,)).fetchone()
            if row is None or row[1] != 'leased' or row[2] != worker:
                raise ValueError('stale or unauthorized cell completion')
            if hashes_done != row[0]:
                raise ValueError('incomplete scan must not be marked complete')
            self.connection.execute("UPDATE cells SET status='done',hashes_done=?,elapsed=?,updated=? WHERE id=?",
                                    (hashes_done,elapsed,time.time(),cell_id))

    def fail(self, cell_id, worker):
        '''Return a definitively failed worker assignment to immediate reclaim.'''
        with self.lock, self.connection:
            result=self.connection.execute(
                "UPDATE cells SET lease_until=0,updated=? WHERE id=? AND worker=? AND status='leased'",
                (time.time(),cell_id,worker))
            if result.rowcount != 1:raise ValueError('cell not leased to this worker')
            self._event('worker_failed',{'cell':cell_id,'worker':worker})

    def stale(self, work_key):
        with self.lock, self.connection:
            self.connection.execute("UPDATE cells SET status='stale',updated=? WHERE work_key=? AND status='leased'",
                                    (time.time(),work_key))
            self._event('stale_job', {'work_key':work_key})

    def map(self, work_key=None, limit=180):
        limit = max(1, min(int(limit), 500))
        with self.lock:
            if work_key is None:
                rows = self.connection.execute('''SELECT id,work_key,en2,x,y,z,start_nonce,count,
                    worker,status,hashes_done,attempts,elapsed FROM cells ORDER BY id DESC LIMIT ?''',(limit,)).fetchall()
            else:
                rows = self.connection.execute('''SELECT id,work_key,en2,x,y,z,start_nonce,count,
                    worker,status,hashes_done,attempts,elapsed FROM cells WHERE work_key=? ORDER BY id DESC LIMIT ?''',(work_key,limit)).fetchall()
        keys = ['id','work_key','en2','x','y','z','start','count','worker','status','hashes_done','attempts','elapsed']
        return [dict(zip(keys,r)) for r in rows]

    def summary(self):
        with self.lock:
            rows = self.connection.execute('SELECT status,COUNT(*),COALESCE(SUM(hashes_done),0) FROM cells GROUP BY status').fetchall()
            count = self.connection.execute('SELECT COUNT(DISTINCT worker) FROM cells').fetchone()[0]
            last = self.connection.execute('SELECT work_key FROM cells ORDER BY id DESC LIMIT 1').fetchone()
        return {'counts': {r[0]:r[1] for r in rows},'verified_completed_hashes': sum(r[2] for r in rows if r[0]=='done'),
                'worker_identities':count,'latest_work_key':last[0] if last else None}

    def close(self):
        with self.lock:self.connection.close()
