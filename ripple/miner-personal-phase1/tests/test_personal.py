"""Personal mining workflow tests without outside pool accounts or charges."""
import asyncio
from unittest.mock import patch,AsyncMock
import json
import socket
import tempfile
import threading
import time
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from miner import run_with_retries
from ripple_miner.pool_profiles import PoolProfiles
from ripple_miner.mining_ledger import MiningLedger
from ripple_miner.pool_probe import probe
from app import Server,Handler
from ripple_miner.controller import Controller
from http.client import HTTPConnection

class PersistenceTests(unittest.TestCase):
    def test_profile_keeps_nonsecret_fields_and_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=PoolProfiles(tmp)
            o=p.upsert({'name':'My Pool','host':'stratum.example.net','port':3333,
                  'user':'account.worker','tls':True,'password':'top-secret'})
            self.assertNotIn('password',o)
            self.assertEqual(PoolProfiles(tmp).list()[0]['user'],'account.worker')
            self.assertNotIn('top-secret',(Path(tmp)/'pool_profiles.json').read_text())
            self.assertEqual(p.delete('My Pool')['deleted'],'My Pool')
            self.assertEqual(p.list(),[])
    def test_durable_local_audit_is_not_a_payout(self):
        with tempfile.TemporaryDirectory() as tmp:
            l=MiningLedger(tmp);l.add('share_response',{'accepted_total':3,'rejected_total':0});l.close()
            l=MiningLedger(tmp)
            self.assertEqual(l.recent()[0]['data']['accepted_total'],3)
            self.assertNotIn('paid_btc',str(l.recent()))
            l.close()

class UnlimitedReconnect(unittest.IsolatedAsyncioTestCase):
    async def test_unlimited_transport_errors_until_success(self):
        count=[0]
        class Fake:
            async def run(self):
                count[0]+=1
                if count[0]<4:raise ConnectionError('pool temporary failure')
                return {'connected':True}
        with patch('miner.asyncio.sleep',new_callable=AsyncMock) as sleep:
            x=await run_with_retries(lambda:Fake(),max_retries=None,jitter=False)
        self.assertTrue(x['connected'])
        self.assertEqual(count[0],4)
        self.assertEqual([c.args[0] for c in sleep.await_args_list],[2,4,8])
    async def test_rejected_authorization_is_not_infinite_retry(self):
        class Reject:
            async def run(self):raise RuntimeError('mining.authorize rejected')
        with self.assertRaises(RuntimeError):await run_with_retries(lambda:Reject(),max_retries=None)

class LivePoolProbe(unittest.TestCase):
    def test_real_socket_subscribe_and_authorize(self):
        async def serve(r,w):
            try:
                a=json.loads(await r.readline())
                self.assertEqual(a['method'],'mining.subscribe')
                w.write((json.dumps({'id':1,'result':[[], 'cafe',4],'error':None})+'\n').encode());await w.drain()
                b=json.loads(await r.readline())
                self.assertEqual(b['method'],'mining.authorize')
                self.assertEqual(b['params'][0],'myaccount.worker')
                w.write((json.dumps({'id':2,'result':True,'error':None})+'\n').encode());await w.drain()
            finally:
                w.close();await w.wait_closed()
        loop=asyncio.new_event_loop();ready=threading.Event();holder={}
        def run():
            asyncio.set_event_loop(loop)
            server=loop.run_until_complete(asyncio.start_server(serve,'127.0.0.1',0))
            holder['server']=server;holder['port']=server.sockets[0].getsockname()[1]
            ready.set();loop.run_forever()
            loop.run_until_complete(server.wait_closed());loop.close()
        t=threading.Thread(target=run,daemon=True);t.start();self.assertTrue(ready.wait(5))
        try:
            ans=probe('127.0.0.1',holder['port'],'myaccount.worker','x',False)
            self.assertTrue(ans['authorized'])
            self.assertTrue(ans['subscribed'])
            self.assertNotIn('paid',ans)
        finally:
            loop.call_soon_threadsafe(holder['server'].close)
            loop.call_soon_threadsafe(loop.stop)
            t.join(3)

class AccountEndpoints(unittest.TestCase):
    def test_authenticated_profile_and_history_endpoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctl=Controller(tmp)
            srv=Server(('127.0.0.1',0),Handler,ctl,'private-access')
            th=threading.Thread(target=srv.serve_forever,daemon=True);th.start()
            try:
                def req(path,body=None):
                    con=HTTPConnection('127.0.0.1',srv.server_port,timeout=5)
                    head={'Authorization':'Bearer private-access','Content-Type':'application/json'}
                    if body is None:con.request('GET',path,headers=head)
                    else:con.request('POST',path,json.dumps(body),headers=head)
                    resp=con.getresponse();raw=resp.read();con.close()
                    return resp.status,json.loads(raw)
                code,_=req('/api/pools/save',{'name':'Personal','host':'pool.example.com',
                                 'port':3333,'tls':True,'user':'alice.ripple','password':'not-stored'})
                self.assertEqual(code,200)
                code,data=req('/api/pools');self.assertEqual(code,200)
                self.assertEqual(data['profiles'][0]['name'],'Personal')
                self.assertNotIn('password',str(data))
                code,data=req('/api/history');self.assertEqual(code,200)
                self.assertIn('events',data)
            finally:
                srv.shutdown();srv.server_close();ctl.close()