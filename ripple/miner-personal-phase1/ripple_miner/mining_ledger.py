"""Durable operator mining events; does not invent pool accounting credits."""
import json
import sqlite3
import time
import threading
from pathlib import Path

class MiningLedger:
    def __init__(self,root):
        self.lock=threading.RLock()
        self.path=Path(root)/'personal_mining_history.sqlite3'
        self.db=sqlite3.connect(self.path,timeout=10,check_same_thread=False)
        self.db.execute('PRAGMA journal_mode=WAL')
        with self.db:
            self.db.execute('''CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY, at REAL NOT NULL, kind TEXT NOT NULL,
                session INTEGER, payload TEXT NOT NULL)''')
        self.session=int(time.time()*1000000)
    def add(self,kind,detail):
        with self.lock, self.db:
            self.db.execute('INSERT INTO events(at,kind,session,payload) VALUES(?,?,?,?)',
                 (time.time(),kind,self.session,json.dumps(detail,sort_keys=True,default=str)[:4096]))
    def recent(self,limit=100):
        with self.lock:rows=self.db.execute('SELECT at,kind,session,payload FROM events ORDER BY id DESC LIMIT ?',
                              (min(500,max(1,int(limit))),)).fetchall()
        return [{'at':r[0],'kind':r[1],'session':r[2],'data':json.loads(r[3])} for r in rows]
    def close(self):
        with self.lock:self.db.close()