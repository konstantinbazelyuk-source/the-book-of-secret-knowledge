"""Live process scheduler, capacity gates, authenticated loopback IPC."""
import concurrent.futures, hashlib, hmac, json, multiprocessing, os, secrets, socket, threading, time
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
from .hardware import probe, decide_budget, psutil
from .jobs import execute,validate_job
from .state import State

class Runtime:
 def __init__(self,root,aggressive=False,max_workers=None):
  self.root=Path(root).expanduser().resolve();self.root.mkdir(parents=True,exist_ok=True)
  self.workspace=self.root/'workspace';self.workspace.mkdir(exist_ok=True)
  self.state=State(self.root);self.hw=probe();self.budget=decide_budget(self.hw,aggressive,max_workers)
  self.maximum=self.budget['maximum_workers'];self.stop_flag=threading.Event()
  self.futures={};self.lock=threading.RLock();self.last_reason='initializing'
  self.pool=None;self.thread=None;self.http_server=None;self._closed=False
  self.token_file=self.root/'local_api_token.txt'
  if not self.token_file.exists():
   self.token_file.write_text(secrets.token_urlsafe(32),encoding='utf8')
   try:os.chmod(self.token_file,0o600)
   except OSError:pass
  self.token=self.token_file.read_text(encoding='utf8').strip()
 def _safe_capacity(self):
  target=self.maximum;reason=[]
  if psutil:
   mem=psutil.virtual_memory()
   # Measure actual process memory and cgroup budget; do not claim guaranteed thermal protection.
   if (self.hw.get('ram_available_bytes') or 0)<384*1024**2:target=1;reason.append('initial memory headroom low')
   if mem.available<384*1024**2:target=1;reason.append('host memory headroom low')
   cpu=psutil.cpu_percent(interval=None)
   if cpu>92 and not self.budget['aggressive']:target=max(1,target//2);reason.append('host CPU high')
   try:
    bat=psutil.sensors_battery()
    if bat and not bat.power_plugged and bat.percent<25:target=1;reason.append('low battery')
   except (AttributeError,OSError):pass
   try:
    temperatures=psutil.sensors_temperatures() or {}
    observed=[v.current for entries in temperatures.values() for v in entries if v.current is not None]
    if observed and max(observed)>=85:target=0;reason.append('temperature at or above conservative 85 C pause')
   except (AttributeError,OSError):pass
  self.last_reason=', '.join(reason) if reason else 'within configured CPU/memory gates; sensor visibility not guaranteed'
  return target
 def start(self):
  if self.pool:return
  self.pool=concurrent.futures.ProcessPoolExecutor(max_workers=self.maximum,mp_context=multiprocessing.get_context('spawn'))
  self.thread=threading.Thread(target=self._scheduler,name='ripple-scheduler',daemon=True);self.thread.start()
 def _scheduler(self):
  while not self.stop_flag.is_set():
   try:
    with self.lock:
     for f,jid in list(self.futures.items()):
      if f.done():
       try:self.state.finish(jid,result=f.result())
       except Exception as e:self.state.finish(jid,error=f'{type(e).__name__}: {e}')
       del self.futures[f]
     room=max(0,self._safe_capacity()-len(self.futures))
     for jid,kind,params in self.state.queued(room):
      self.state.start(jid)
      future=self.pool.submit(execute,kind,params,str(self.workspace))
      self.futures[future]=jid
   except Exception as e:self.state.event(None,'scheduler_error',f'{type(e).__name__}: {e}')
   self.stop_flag.wait(.12)
 def status(self):
  with self.lock:running=len(self.futures)
  return {'runtime':'Ripple Laptop Native Alpha 2.0','host_is_user_dell':'unknown; measured in current executing OS','budget':self.budget,'running':running,'queued_statuses':self.state.counts(),'current_safe_capacity':self._safe_capacity(),'governor_reason':self.last_reason,'network':'localhost API only; bearer token required','gpu_dispatch':'optional torch_matrix; fails closed if requested hardware unavailable'}
 def serve(self,host='127.0.0.1',port=8765):
  if host not in ('127.0.0.1','::1'):raise ValueError('public binding disabled; reverse proxy is separately managed')
  self.start();runtime=self
  class Handler(BaseHTTPRequestHandler):
   def log_message(self,fmt,*args):pass
   def auth(self):
    supplied=self.headers.get('Authorization','')
    return hmac.compare_digest(supplied,'Bearer '+runtime.token)
   def respond(self,status,data):
    content=json.dumps(data,sort_keys=True).encode();self.send_response(status)
    self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(content)))
    self.end_headers();self.wfile.write(content)
   def do_GET(self):
    u=urlparse(self.path)
    if u.path=='/':
     page=(Path(__file__).resolve().parent.parent/'bin'/'dashboard.html').read_bytes()
     self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(page)));self.end_headers();self.wfile.write(page);return
    if not self.auth():return self.respond(401,{'error':'authentication required'})
    if u.path=='/v1/status':return self.respond(200,runtime.status())
    if u.path=='/v1/jobs':return self.respond(200,{'jobs':runtime.state.list(50)})
    if u.path.startswith('/v1/jobs/'):
     job=runtime.state.get(u.path.rsplit('/',1)[1]);return self.respond(200 if job else 404,job or {'error':'not found'})
    return self.respond(404,{'error':'unknown endpoint'})
   def do_POST(self):
    if not self.auth():return self.respond(401,{'error':'authentication required'})
    if urlparse(self.path).path!='/v1/jobs':return self.respond(404,{'error':'unknown endpoint'})
    try:
     size=int(self.headers.get('Content-Length','0'))
     if size<1 or size>2097152:return self.respond(413,{'error':'request exceeds 2 MiB limit'})
     payload=json.loads(self.rfile.read(size));kind=payload['kind'];params=payload['params']
     validate_job(kind,params);jid=runtime.state.submit(kind,params)
     return self.respond(202,{'id':jid,'status':'queued'})
    except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:return self.respond(400,{'error':str(e)[:250]})
  self.http_server=ThreadingHTTPServer((host,port),Handler)
  self.state.event(None,'listen',f'{host}:{self.http_server.server_port}')
  try:self.http_server.serve_forever(poll_interval=.2)
  finally:self.close()
 def close(self):
  if self._closed:return
  self._closed=True
  self.stop_flag.set()
  if self.http_server:self.http_server.shutdown() if threading.current_thread()!=self.thread and threading.current_thread()!=threading.main_thread() else None
  if self.thread and self.thread.is_alive():self.thread.join(timeout=10)
  if self.pool:
   self.pool.shutdown(wait=True,cancel_futures=False);self.pool=None
  with self.lock:
   for f,jid in list(self.futures.items()):
    try:self.state.finish(jid,result=f.result())
    except Exception as e:self.state.finish(jid,error=str(e))
    del self.futures[f]
  if self.http_server:self.http_server.server_close()
  self.state.close()
