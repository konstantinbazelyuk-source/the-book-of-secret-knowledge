import hashlib,json,os,socket,subprocess,sys,tempfile,time,unittest,urllib.error,urllib.request
from pathlib import Path
from ripple_native.hardware import probe,decide_budget
from ripple_native.jobs import execute,validate_job
from ripple_native.state import State
from ripple_native.cli import request
ROOT=Path(__file__).resolve().parent.parent

class CheckHardware(unittest.TestCase):
 def test_cpu_budget_detected(self):
  h=probe();self.assertGreaterEqual(h['effective_parallel_cpus'],1)
  b=decide_budget(h);self.assertGreaterEqual(b['maximum_workers'],1)
  self.assertLessEqual(b['maximum_workers'],h['effective_parallel_cpus'])
 def test_no_fabricated_dell(self):
  h=probe();self.assertIn('NOT user',h['measured_in'])
 def test_reference_immutability(self):
  core=(ROOT/'reference/v01_ripple_core_LOCKED.cjs').read_bytes()
  quad=(ROOT/'reference/v07_quaternary_core_LOCKED.mjs').read_bytes()
  self.assertEqual(hashlib.sha256(core).hexdigest(),'d75d4208e92f19623b127615bd52b4002e85d2c0a59b76471764b55a24294210')
  self.assertEqual(hashlib.sha256(quad).hexdigest(),'9c1879f6bc024e564e5e25b0294ac62b34d67aafffe26f9ddfae52675d66f695')

class CheckJobs(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.work=Path(self.tmp.name)/'workspace';self.work.mkdir()
 def tearDown(self):self.tmp.cleanup()
 def test_prime(self):
  out=execute('prime_count',{'start':2,'stop':101},str(self.work));self.assertEqual(out['output']['prime_count'],25)
  self.assertNotEqual(out['pid'],0)
 def test_reject_unknown(self):
  with self.assertRaises(ValueError):validate_job('run_arbitrary_python',{})
 def test_reject_bad_numbers(self):
  for kind,p in [('ripple_lif',{'frames':10,'rgb':[1,float('nan'),0]}),('prime_count',{'start':0,'stop':9_999_999}),('torch_matrix',{'size':9000})]:
   with self.subTest(kind=kind),self.assertRaises(ValueError):validate_job(kind,p)
 def test_file_scope(self):
  (self.work/'x.txt').write_text('ab')
  o=execute('sha256_file',{'path':'x.txt'},str(self.work))
  self.assertEqual(o['output']['sha256'],hashlib.sha256(b'ab').hexdigest())
  for name in ('../secret','/etc/passwd'):
   with self.assertRaises(ValueError):execute('sha256_file',{'path':name},str(self.work))
 def test_outbound_policy(self):
  with self.assertRaises(ValueError):validate_job('https_digest',{'url':'http://example.com','allow_hosts':['example.com']})
  with self.assertRaises(ValueError):validate_job('https_digest',{'url':'https://evil.example','allow_hosts':['good.example']})
 def test_app_opt_in(self):
  with self.assertRaises(RuntimeError):execute('registered_app',{'name':'calc'},str(self.work))
 def test_workspace_file_operations(self):
  execute('workspace_write',{'path':'a/b.txt','content':'real file'},str(self.work))
  self.assertEqual(execute('workspace_read',{'path':'a/b.txt'},str(self.work))['output']['text'],'real file')
  execute('workspace_move',{'path':'a/b.txt','destination':'c.txt'},str(self.work))
  with self.assertRaises(ValueError):execute('workspace_delete',{'path':'c.txt','confirm':False},str(self.work))
  execute('workspace_delete',{'path':'c.txt','confirm':True},str(self.work))
  self.assertFalse((self.work/'c.txt').exists())
 def test_signal_frequency(self):
  try:import numpy
  except ImportError:self.skipTest('optional numpy unavailable')
  import math
  samples=[math.sin(2*math.pi*8*k/64) for k in range(64)]
  o=execute('signal_fft',{'samples':samples,'sample_rate_hz':64},str(self.work))
  self.assertEqual(o['output']['peak_frequency_hz'],8.0)
 def test_neural_training_optional(self):
  try:import torch
  except ImportError:self.skipTest('optional torch unavailable')
  o=execute('torch_train',{'epochs':120,'seed':42},str(self.work))
  self.assertEqual(o['output']['training_accuracy'],1.0)
  self.assertTrue(o['simulated_data']);self.assertTrue(o['actual_execution'])
 def test_v17_unmodified_source_execution(self):
  o=execute('v17_composition',{},str(self.work))
  result=o['output'];self.assertTrue(o['simulated_data'])
  self.assertEqual(result['counts']['total'],2238)
  self.assertEqual(result['groups']['composed_ripple']['accepted'],40)
  self.assertEqual(result['groups']['composed_ripple']['acceptedCorrect'],221)
  self.assertEqual(result['groups']['composed_ripple']['acceptedCorrect'],result['groups']['composed_serial']['acceptedCorrect'])
  self.assertTrue((self.work/result['result_file']).is_file())
 def test_untrusted_workspace_cannot_register_apps(self):
  (self.work/'apps.json').write_text(json.dumps({'calc':{'executable':sys.executable,'arguments':['-c','print(999)']}}))
  with self.assertRaises(RuntimeError):execute('registered_app',{'name':'calc'},str(self.work))
 def test_registered_process(self):
  (self.work.parent/'app_registry.json').write_text(json.dumps({'safe_python':{'executable':sys.executable,'arguments':['-c','print(271828)']}}))
  out=execute('registered_app',{'name':'safe_python'},str(self.work))
  self.assertEqual(out['output']['exit_code'],0);self.assertIn('271828',out['output']['stdout_tail'])
 def test_archive_inventory(self):
  d=self.work/'sources';d.mkdir()
  import zipfile
  with zipfile.ZipFile(d/'s.zip','w') as z:z.writestr('f.txt','test')
  o=execute('archive_inventory',{'subfolder':'sources'},str(self.work))
  self.assertEqual(o['output']['archives'][0]['members'],1)
  self.assertFalse(o['output']['executed_archive_members'])
 def test_ripple_original_actual(self):
  o=execute('ripple_lif',{'frames':500,'rgb':[.6,.3,.1]},str(self.work))
  self.assertGreater(o['output']['spikes'],0);self.assertEqual(o['output']['kernel'],'locked-Ripple-v0.1')
  self.assertTrue(o['simulated_data'])
 def test_quaternary_actual(self):
  o=execute('quaternary',{'symbols':[0,1,2,3]},str(self.work))
  self.assertEqual(o['output']['byte'],27);self.assertEqual(o['output']['decoded'],[0,1,2,3])
 def test_torch_cpu_optional(self):
  try: import torch
  except ImportError:self.skipTest('optional torch unavailable')
  o=execute('torch_matrix',{'size':32,'device':'cpu'},str(self.work))
  self.assertTrue(o['output']['validated']);self.assertEqual(o['output']['device'],'cpu')

class CheckPersistence(unittest.TestCase):
 def test_transactional_recovery(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=State(tmp);id1=s.submit('prime_count',{'start':2,'stop':100});id2=s.submit('prime_count',{'start':4,'stop':100});s.start(id1);s.finish(id2,{'ok':True});s.close()
   s=State(tmp)
   self.assertEqual(s.get(id1)['status'],'interrupted');self.assertEqual(s.get(id2)['status'],'done')
   self.assertEqual(s.counts()['done'],1);s.close()

class CheckLongResult(unittest.TestCase):
 def test_long_result_is_valid_json_artifact(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=State(tmp);jid=s.submit('prime_count',{'start':2,'stop':3})
   s.finish(jid,result={'big':'x'*130000})
   job=s.get(jid);self.assertEqual(job['status'],'done')
   ref=job['result']['workspace_result_file'];self.assertEqual(len(json.loads((Path(tmp)/'workspace'/ref).read_text())['big']),130000)
   s.close()

class CheckDaemon(unittest.TestCase):
 def test_http_scheduler_and_auth(self):
  with tempfile.TemporaryDirectory() as tmp:
   with socket.socket() as sk:sk.bind(('127.0.0.1',0));port=sk.getsockname()[1]
   p=subprocess.Popen([sys.executable,'-m','ripple_native','--root',tmp,'daemon','--port',str(port),'--max-workers','2'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
   try:
    for i in range(120):
     if (Path(tmp)/'local_api_token.txt').exists():
      try:status=request(tmp,'GET','/v1/status',port=port);break
      except (ConnectionRefusedError,urllib.error.URLError):pass
     if p.poll() is not None:raise RuntimeError('daemon quit: '+p.stderr.read().decode()[:600])
     time.sleep(.12)
    else:self.fail('daemon startup timeout')
    self.assertGreaterEqual(status['budget']['maximum_workers'],1)
    with urllib.request.urlopen('http://127.0.0.1:%d/'%port) as dash:
     self.assertIn(b'Native Runtime Alpha',dash.read())
    with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen('http://127.0.0.1:%d/v1/status'%port)
    self.assertEqual(e.exception.code,401)
    params=[('prime_count',{'start':10_000,'stop':40000}),('quaternary',{'symbols':[3,2,1,0]}),('ripple_lif',{'frames':120,'rgb':[.7,.2,.2]})]
    ids=[]
    for kind,arg in params:ids.append(request(tmp,'POST','/v1/jobs',{'kind':kind,'params':arg},port)['id'])
    deadline=time.monotonic()+60
    while time.monotonic()<deadline:
     jobs=[request(tmp,'GET','/v1/jobs/'+id,port=port) for id in ids]
     if all(j['status'] in ('done','failed') for j in jobs):break
     time.sleep(.2)
    self.assertEqual([j['status'] for j in jobs],['done']*3)
    self.assertEqual(jobs[1]['result']['output']['byte'],228)
    self.assertTrue(jobs[2]['result']['simulated_data'])
    self.assertNotEqual(jobs[0]['result']['pid'],p.pid)
    # Persistent DB is safe to inspect independently once service exits.
   finally:
    p.terminate()
    try:p.wait(timeout=20)
    except subprocess.TimeoutExpired:p.kill();p.wait()
    p.stderr.close()
   s=State(tmp)
   self.assertEqual(s.counts()['done'],3);s.close()

if __name__=='__main__':unittest.main()
