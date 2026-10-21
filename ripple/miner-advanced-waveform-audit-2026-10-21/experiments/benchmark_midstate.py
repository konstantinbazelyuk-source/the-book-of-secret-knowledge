import ctypes,hashlib,json,random,statistics,struct,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MINER_ROOT=ROOT
sys.path.insert(0,str(MINER_ROOT))
from miner import GENESIS_HEADER,sha256d,DIFF1_TARGET,target_from_bits

def load(name):
 lib=ctypes.CDLL(str(ROOT/'native'/name))
 f=lib.ripple_scan_sha256d
 f.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint32]
 f.restype=ctypes.c_int64
 return f

def scan(f,prefix,start,count,target=(1<<256)-1,block_target=DIFF1_TARGET):
 nonces=(ctypes.c_uint32*max(count,1))();digests=(ctypes.c_uint8*max(count*32,32))();blocks=(ctypes.c_uint8*max(count,1))()
 p=ctypes.create_string_buffer(prefix,76)
 st=ctypes.create_string_buffer(target.to_bytes(32,'little'),32)
 bt=ctypes.create_string_buffer(block_target.to_bytes(32,'little'),32)
 t=time.perf_counter()
 rc=f(p,start,count,st,bt,nonces,digests,blocks,count)
 elapsed=time.perf_counter()-t
 if rc<0:raise RuntimeError(f'Native failure {rc}')
 result=[(nonces[i],bytes(digests[i*32:(i+1)*32]).hex(),bool(blocks[i])) for i in range(rc)]
 return result,elapsed

def main():
 fs={name:load(name) for name in ['libripple_baseline.so','libripple_midstate.so']}
 origin=GENESIS_HEADER[:76]
 tests=[]
 for case,(prefix,start,count,share,block) in enumerate([
    (origin,int.from_bytes(GENESIS_HEADER[-4:],'little'),1,(1<<256)-1,target_from_bits(0x1d00ffff)),
    (origin,0,310,(1<<256)-1,DIFF1_TARGET),
    (origin,12345,37,(1<<256)//3,(1<<256)//10),
    (bytes(range(76)),16,144,(1<<256)-1,0),
    (origin,(1<<32)-3,3,(1<<256)-1,DIFF1_TARGET),
 ]):
    res={k:scan(v,prefix,start,count,share,block)[0] for k,v in fs.items()}
    assert res['libripple_baseline.so']==res['libripple_midstate.so'],str(case)
    for nonce,digest,is_block in res['libripple_midstate.so']:
      correct=sha256d(prefix+struct.pack('<I',nonce))
      assert correct==bytes.fromhex(digest),str((case,nonce))
      assert (int.from_bytes(correct,'little')<=block)==is_block
    if case==0:assert res['libripple_midstate.so'][0][2]
    tests.append({'case':case,'verified_matches':len(res['libripple_midstate.so'])})

 rng=random.Random(42)
 # Full target is used to force store/serialize identical digests, capturing data-plane behavior.
 prefix=bytes(rng.randrange(256) for _ in range(76))
 results={k:[] for k in fs}
 trial_count=150000
 for round_index in range(9):
  order=list(fs);rng.shuffle(order)
  for name in order:
   _,sec=scan(fs[name],prefix,round_index*trial_count,trial_count)
   results[name].append(trial_count/sec)
 baseline=statistics.median(results['libripple_baseline.so'])
 midstate=statistics.median(results['libripple_midstate.so'])
 report={'environment':{'python':sys.version.split()[0],'openssl':'system linked','platform':sys.platform},'algorithm':'Double SHA-256 over Bitcoin 80-byte block header','tests':tests,'trial_hashes':trial_count,'repetitions':9,'baseline_hps':baseline,'midstate_hps':midstate,'speed_ratio':midstate/baseline,'samples_hps':results,'integration_status':'independent drop-in C native hashing ABI; not selected production backend'}
 (ROOT/'experiments'/'waveform'/'midstate_report_rerun.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:report[k] for k in ('tests','baseline_hps','midstate_hps','speed_ratio')},indent=2))
if __name__=='__main__':main()