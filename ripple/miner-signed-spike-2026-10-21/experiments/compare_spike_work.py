"""Real mining comparison, equal resources, no mock hashing or payout claims.

Local verifying Stratum protocol endpoint; candidate shares verified using SHA256d.
Measures total successful nonce hashing during productive session, includes
child-process management but deliberately excludes engine start by mine duration.
"""
import asyncio
from pathlib import Path
import json,os,sys,tempfile,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from miner import Work,header_prefix,sha256d,target_for_difficulty
from ripple_miner.controller import Controller
from test_end_to_end import VerifyingPool

class ModeratePool(VerifyingPool):
    async def client(self,reader,writer):
        w=Work('e2e','00'*32,'aa','bb',(),'20000000','207fffff','5f5e1000',True,'cafe',4,'0.0001')
        try:
            while line:=await reader.readline():
                req=json.loads(line)
                if req['method']=='mining.subscribe':
                    packets=[{'id':req['id'],'result':[[['mining.notify','e2e']],'cafe',4],'error':None}]
                elif req['method']=='mining.authorize':
                    packets=[{'id':req['id'],'result':True,'error':None},
                             {'id':None,'method':'mining.set_difficulty','params':[.0001]},
                             {'id':None,'method':'mining.notify','params':['e2e','00'*32,'aa','bb',[],'20000000','207fffff','5f5e1000',True]}]
                elif req['method']=='mining.submit':
                    p=req['params'];nonce=int(p[4],16);ex=int(p[2],16)
                    valid=int.from_bytes(sha256d(header_prefix(w,ex)+nonce.to_bytes(4,'little')),'little')<=target_for_difficulty(w.difficulty)
                    if valid:self.accepted+=1
                    packets=[{'id':req['id'],'result':valid,'error':None}]
                else: packets=[]
                for pkt in packets:writer.write((json.dumps(pkt)+'\n').encode())
                await writer.drain()
        finally:writer.close();await writer.wait_closed()

def one(policy):
    pool=ModeratePool();pool.start()
    try:
        with tempfile.TemporaryDirectory() as temp:
            c=Controller(temp)
            try:
                c.start_cpu({'host':'127.0.0.1','port':pool.port,'user':'bench.user',
                    'password':'x','workers':2,'chunk':100000,'policy':policy,
                    'native_hash':True,'seconds':3.0})
                deadline=time.monotonic()+28
                while time.monotonic()<deadline:
                    state=c.status()['cpu']
                    if state['state'] in ('stopped','failed'):break
                    time.sleep(.15)
                snap=c.status()['cpu']
                if snap['state']!='stopped':raise RuntimeError('not stopped '+str(snap))
                if snap['hashes']<=0:raise RuntimeError('no real Bitcoin hashes completed')
                return {'policy':policy,'hashes':snap['hashes'],'accepted':snap['accepted'],
                        'submitted':snap.get('submitted'), 'pool_accepted':pool.accepted,
                        'wave':snap.get('advanced_waveform')}
            finally:c.close()
    finally:pool.close()

def main():
    arr=[]
    for repeat in range(2):
        order=['round_robin','waveform'] if repeat%2==0 else ['waveform','round_robin']
        for policy in order:
            d=one(policy); d['round']=repeat;arr.append(d)
            print(policy,d['hashes'],'accepted',d['accepted'],'wave ticks',d['wave']['ticks'] if d['wave'] else None,flush=True)
    p=Path(__file__).with_name('spike_work_local_pool_results.json')
    p.write_text(json.dumps({'status':'measured real SHA256d vs local validating Stratum (no BTC)',
                             'seconds_productive':3.,'parallel_workers':2,
                             'total':arr},indent=2))
    print(str(p))
if __name__=='__main__':main()