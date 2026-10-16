"""SQLite WAL transactional queue with crash recovery and bounded result recording."""
import json, sqlite3, threading, time, uuid
from pathlib import Path

class State:
 def __init__(self,root):
  self.root=Path(root).expanduser().resolve();self.root.mkdir(parents=True,exist_ok=True)
  self.db_path=self.root/'ripple_state.sqlite3';self.lock=threading.RLock()
  self.conn=sqlite3.connect(str(self.db_path),check_same_thread=False,timeout=10)
  with self.lock:
   self.conn.execute('PRAGMA journal_mode=WAL');self.conn.execute('PRAGMA busy_timeout=10000')
   self.conn.execute('CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, kind TEXT NOT NULL, params TEXT NOT NULL, status TEXT NOT NULL, created REAL NOT NULL, started REAL, finished REAL, result TEXT, error TEXT)')
   self.conn.execute('CREATE INDEX IF NOT EXISTS jobs_by_status ON jobs(status,created)')
   self.conn.execute('CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, job TEXT, at REAL NOT NULL, event TEXT, detail TEXT)')
   self.conn.commit()
   # Interrupted work is made explicit; no blind re-execution after a crash.
   self.conn.execute("UPDATE jobs SET status='interrupted',finished=?,error='daemon restarted during execution' WHERE status='running'",(time.time(),))
   self.conn.commit()
 def close(self):
  with self.lock:self.conn.close()
 def event(self,job,event,detail=''):
  with self.lock:
   self.conn.execute('INSERT INTO events(job,at,event,detail) VALUES(?,?,?,?)',(job,time.time(),event,str(detail)[:1000]));self.conn.commit()
 def submit(self,kind,params):
  jid=str(uuid.uuid4());now=time.time()
  with self.lock:
   cnt=self.conn.execute("SELECT COUNT(*) FROM jobs WHERE status='queued'").fetchone()[0]
   if cnt>=500:raise ValueError('queue limit 500 jobs')
   self.conn.execute('INSERT INTO jobs(id,kind,params,status,created) VALUES(?,?,?,?,?)',(jid,kind,json.dumps(params,sort_keys=True),'queued',now))
   self.conn.commit();self.event(jid,'queued',kind)
  return jid
 def queued(self,limit):
  with self.lock:
   rows=self.conn.execute("SELECT id,kind,params FROM jobs WHERE status='queued' ORDER BY created LIMIT ?",(limit,)).fetchall()
   return [(jid,kind,json.loads(p)) for jid,kind,p in rows]
 def start(self,jid):
  with self.lock:
   self.conn.execute("UPDATE jobs SET status='running',started=? WHERE id=? AND status='queued'",(time.time(),jid));self.conn.commit();self.event(jid,'started')
 def finish(self,jid,result=None,error=None):
  serialized=json.dumps(result,sort_keys=True) if result is not None else None
  if serialized and len(serialized)>100000:
   # Preserve long results as actual workspace artifacts; do not corrupt SQLite JSON by truncation.
   folder=self.root/'workspace'/'results';folder.mkdir(parents=True,exist_ok=True)
   name=f'job-{jid}.json';(folder/name).write_text(serialized,encoding='utf8')
   serialized=json.dumps({'workspace_result_file':'results/'+name,'saved_characters':len(serialized)})
  with self.lock:
   self.conn.execute('UPDATE jobs SET status=?,finished=?,result=?,error=? WHERE id=?',( 'failed' if error else 'done',time.time(),serialized,str(error)[:2000] if error else None,jid));self.conn.commit();self.event(jid,'failed' if error else 'finished')
 def get(self,jid):
  with self.lock:
   row=self.conn.execute('SELECT id,kind,params,status,created,started,finished,result,error FROM jobs WHERE id=?',(jid,)).fetchone()
  if row is None:return None
  o=dict(zip(['id','kind','params','status','created','started','finished','result','error'],row))
  for k in ('params','result'):
   if o[k] is not None:o[k]=json.loads(o[k])
  return o
 def list(self,limit=50):
  with self.lock: ids=self.conn.execute('SELECT id FROM jobs ORDER BY created DESC LIMIT ?',(max(1,min(int(limit),100)),)).fetchall()
  return [self.get(x[0]) for x in ids]
 def counts(self):
  with self.lock:return dict(self.conn.execute('SELECT status,COUNT(*) FROM jobs GROUP BY status').fetchall())
