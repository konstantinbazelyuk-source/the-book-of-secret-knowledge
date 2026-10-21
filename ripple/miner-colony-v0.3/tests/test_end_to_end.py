"""Controller launches genuine child miner against a local verifying pool.

The pool uses artificially easy difficulty and pays nothing. This proves the
actual controller -> subprocess -> Stratum -> share -> controller telemetry path.
"""
import asyncio
import json
from pathlib import Path
import tempfile
import threading
import time
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ripple_miner.controller import Controller
from miner import Work, header_prefix, sha256d, target_for_difficulty

class VerifyingPool:
    def __init__(self):
        self.loop=asyncio.new_event_loop()
        self.ready=threading.Event()
        self.port=None
        self.accepted=0
        self.thread=threading.Thread(target=self.run,daemon=True)
    def run(self):
        asyncio.set_event_loop(self.loop)
        self.server=self.loop.run_until_complete(asyncio.start_server(self.client,'127.0.0.1',0))
        self.port=self.server.sockets[0].getsockname()[1]
        self.ready.set()
        self.loop.run_forever()
    async def client(self,reader,writer):
        w=Work('e2e','00'*32,'aa','bb',(),'20000000','207fffff','5f5e1000',True,'cafe',4,'0.000001')
        try:
            while line:=await reader.readline():
                req=json.loads(line)
                if req['method']=='mining.subscribe':
                    packets=[{'id':req['id'],'result':[[['mining.notify','e2e']],'cafe',4],'error':None}]
                elif req['method']=='mining.authorize':
                    packets=[{'id':req['id'],'result':True,'error':None},
                             {'id':None,'method':'mining.set_difficulty','params':[1e-6]},
                             {'id':None,'method':'mining.notify','params':['e2e','00'*32,'aa','bb',[],'20000000','207fffff','5f5e1000',True]}]
                elif req['method']=='mining.submit':
                    p=req['params'];nonce=int(p[4],16);ex=int(p[2],16)
                    valid=int.from_bytes(sha256d(header_prefix(w,ex)+nonce.to_bytes(4,'little')),'little')<=target_for_difficulty(w.difficulty)
                    if valid:self.accepted+=1
                    packets=[{'id':req['id'],'result':valid,'error':None}]
                else: packets=[]
                for pkt in packets:
                    writer.write((json.dumps(pkt)+'\n').encode())
                await writer.drain()
        finally:
            writer.close();await writer.wait_closed()
    def start(self):
        self.thread.start()
        if not self.ready.wait(5):raise RuntimeError('pool not ready')
    def close(self):
        async def shutdown():
            self.server.close();await self.server.wait_closed()
            tasks=[t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            for t in tasks:t.cancel()
            await asyncio.gather(*tasks,return_exceptions=True)
        asyncio.run_coroutine_threadsafe(shutdown(),self.loop).result(5)
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(5)
        self.loop.close()

class EndToEndTest(unittest.TestCase):
    def test_laptop_controller_mines_and_reports_real_local_shares(self):
        pool=VerifyingPool();pool.start()
        with tempfile.TemporaryDirectory() as folder:
            c=Controller(folder)
            try:
                c.start_cpu({'host':'127.0.0.1','port':pool.port,'user':'operator.test',
                            'password':'x','workers':1,'chunk':200,'tls':False,'seconds':2.1})
                until=time.monotonic()+12
                while time.monotonic()<until:
                    s=c.status()['cpu']
                    if s['state'] in ('stopped','failed'):
                        break
                    time.sleep(.1)
                s=c.status()['cpu']
                self.assertGreater(s['hashes'],0)
                self.assertGreater(s['accepted'],0)
                self.assertGreater(pool.accepted,0)
                self.assertEqual(s['state'],'stopped',str(s))
                self.assertNotIn('password',json.dumps(c.status()))
            finally:c.close()
        pool.close()

if __name__=='__main__':unittest.main()
