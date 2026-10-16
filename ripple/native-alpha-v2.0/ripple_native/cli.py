"""Local desktop-native command line and controlled loopback API client."""
import argparse,json,os,sys,time,urllib.request,urllib.error,statistics,concurrent.futures,multiprocessing,shutil
from pathlib import Path
from .hardware import probe,decide_budget
from .jobs import execute,validate_job,_prime_count
from .runtime import Runtime

def default_root():
 if sys.platform=='win32':return str(Path(os.environ.get('LOCALAPPDATA',str(Path.home())))/'RippleLaptop')
 return str(Path.home()/'.local'/'share'/'ripple-laptop')

def request(root,method,path,payload=None,port=8765):
 token=(Path(root)/'local_api_token.txt').read_text().strip()
 data=json.dumps(payload).encode() if payload is not None else None
 req=urllib.request.Request(f'http://127.0.0.1:{port}{path}',data=data,method=method,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=10) as resp:return json.load(resp)

def benchmark(level=30000,workers=2):
 # This is measured elapsed wall-clock speed on the executing environment only.
 # Spawn process pool from importable main module, CPU-heavy prime counting.
 stop=min(3_000_000,100000+level);start=100000
 spans=[(a,min(stop,a+10000)) for a in range(start,stop,10000)]
 t=time.perf_counter();serial=[_prime_count(a,b) for a,b in spans];serial_time=time.perf_counter()-t
 t=time.perf_counter()
 with concurrent.futures.ProcessPoolExecutor(max_workers=max(1,workers),mp_context=multiprocessing.get_context('spawn')) as ex:
  parallel=list(ex.map(_prime_count,(s[0] for s in spans),(s[1] for s in spans)))
 parallel_time=time.perf_counter()-t
 if parallel!=serial:raise RuntimeError('parallel output mismatch')
 return {'measured_on':'executing environment, not assumed Dell','serial_wall_seconds':serial_time,'multiprocess_wall_seconds':parallel_time,'speedup_ratio':serial_time/parallel_time if parallel_time else None,'worker_processes':workers,'prime_count':sum(parallel),'interval':[start,stop], 'includes_process_spawn_overhead':True}

def main(argv=None):
 ap=argparse.ArgumentParser(description='Ripple laptop native runtime (not artificial intelligence)')
 ap.add_argument('--root',default=default_root(),help='State and allowlisted file workspace')
 sub=ap.add_subparsers(dest='cmd',required=True)
 sub.add_parser('probe')
 d=sub.add_parser('daemon');d.add_argument('--port',type=int,default=8765);d.add_argument('--aggressive',action='store_true');d.add_argument('--max-workers',type=int)
 s=sub.add_parser('submit');s.add_argument('kind');s.add_argument('parameters',help='JSON object');s.add_argument('--port',type=int,default=8765)
 q=sub.add_parser('status');q.add_argument('--port',type=int,default=8765)
 w=sub.add_parser('wait');w.add_argument('id');w.add_argument('--port',type=int,default=8765);w.add_argument('--timeout',type=float,default=30)
 l=sub.add_parser('jobs');l.add_argument('--port',type=int,default=8765)
 g=sub.add_parser('gpu-calibrate');g.add_argument('--size',type=int,default=512)
 a=sub.add_parser('register-app');a.add_argument('name');a.add_argument('executable');a.add_argument('arguments',nargs='*')
 b=sub.add_parser('bench');b.add_argument('--level',type=int,default=30000);b.add_argument('--workers',type=int,default=2)
 args=ap.parse_args(argv);root=str(Path(args.root).expanduser().resolve())
 if args.cmd=='probe':result={'hardware':probe(),'conservative_budget':decide_budget(probe())}
 elif args.cmd=='daemon':
  runtime=Runtime(root,args.aggressive,args.max_workers)
  print(json.dumps({'listening':'http://127.0.0.1:'+str(args.port),'root':root,'hardware':runtime.hw,'budget':runtime.budget},indent=2),flush=True)
  try:runtime.serve(port=args.port)
  except KeyboardInterrupt:runtime.close()
  return
 elif args.cmd=='submit':result=request(root,'POST','/v1/jobs',{'kind':args.kind,'params':json.loads(args.parameters)},args.port)
 elif args.cmd=='status':result=request(root,'GET','/v1/status',port=args.port)
 elif args.cmd=='jobs':result=request(root,'GET','/v1/jobs',port=args.port)
 elif args.cmd=='wait':
  deadline=time.monotonic()+args.timeout
  while True:
   result=request(root,'GET','/v1/jobs/'+args.id,port=args.port)
   if result['status'] in ('done','failed','interrupted') or time.monotonic()>deadline:break
   time.sleep(.2)
 elif args.cmd=='gpu-calibrate':
  from .jobs import _torch_matrix
  if args.size<64 or args.size>1024:raise ValueError('calibration size 64..1024')
  candidates=['cpu'];hw=probe();gpu=hw['gpu']
  if gpu.get('torch',{}).get('cuda_available'):candidates.append('cuda')
  if gpu.get('torch',{}).get('mps_available'):candidates.append('mps')
  if gpu.get('directml',{}).get('device_count',0)>0:candidates.append('directml')
  times={};problems={}
  for device in candidates:
   try:
    _torch_matrix(args.size,device) # warmup
    times[device]=min(_torch_matrix(args.size,device)['seconds'] for _ in range(3))
   except Exception as ex:problems[device]=str(ex)[:250]
  if 'cpu' not in times:raise RuntimeError('CPU baseline failed; no GPU policy installed')
  winner=min(times,key=times.get)
  if winner!='cpu' and times[winner]>.85*times['cpu']:winner='cpu'
  result={'measured_on':'executing host, calibration workload only','times_seconds':times,'failures':problems,'selected_device':winner,'criterion':'GPU at least 15% faster than measured CPU at same shape'}
  dest=Path(root);dest.mkdir(parents=True,exist_ok=True);(dest/'gpu_policy.json').write_text(json.dumps(result,indent=2))
 elif args.cmd=='register-app':
  if not args.name.isidentifier():raise ValueError('application name must be an identifier')
  path=Path(args.executable).expanduser().resolve()
  if not path.is_file():raise FileNotFoundError(path)
  folder=Path(root);folder.mkdir(parents=True,exist_ok=True)
  config=folder/'app_registry.json';items=json.loads(config.read_text()) if config.exists() else {}
  items[args.name]={'executable':str(path),'arguments':args.arguments}
  config.write_text(json.dumps(items,indent=2));result={'registered':args.name,'executable':str(path),'automatic_execution':False}
 elif args.cmd=='bench':result=benchmark(args.level,args.workers)
 print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
