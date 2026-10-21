import json
import socket
import tempfile
import threading
import time
import unittest
from http.client import HTTPConnection
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ripple_miner.controller import Controller
from app import Handler, Server

class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.controller=Controller(self.folder.name)
    def tearDown(self):
        self.controller.close();self.folder.cleanup()
    def test_persistence_registry_and_private_addresses(self):
        self.controller.add_node('127.0.0.1',4028,'Loopback rig')
        self.assertEqual(self.controller.status()['colony']['count'],1)
        self.assertEqual(json.loads((Path(self.folder.name)/'devices.json').read_text())[0]['name'],'Loopback rig')
        self.controller.remove_node('127.0.0.1',4028)
        self.assertEqual(self.controller.status()['colony']['count'],0)
    def test_pool_credential_validation(self):
        with self.assertRaises(ValueError):self.controller.start_cpu({'host':'','port':0})
        self.assertEqual(self.controller.status()['cpu']['state'],'idle')
    def test_http_token_and_calculations(self):
        server=Server(('127.0.0.1',0),Handler,self.controller,'secret-local-token')
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            port=server.server_port
            def req(path, body=None, auth=False):
                c=HTTPConnection('127.0.0.1',port,timeout=5)
                h={'Authorization':'Bearer secret-local-token'} if auth else {}
                if body is None:c.request('GET',path,headers=h)
                else:
                    h['Content-Type']='application/json'
                    c.request('POST',path,body=json.dumps(body),headers=h)
                r=c.getresponse();data=r.read();out=(r.status,json.loads(data));c.close();return out
            self.assertEqual(req('/api/state')[0],401)
            self.assertEqual(req('/api/state',auth=True)[0],200)
            code,spatial=req('/api/spatial',auth=True)
            self.assertEqual(code,200)
            self.assertIn('summary',spatial)
            self.assertEqual(req('/api/cpu/pause',{},auth=True)[0],400)
            code,data=req('/api/economics',{'hashrate_hps':1e12,'difficulty':1e14,'btc_usd':100000,'power_w':3000},auth=True)
            self.assertEqual(code,200)
            self.assertIsNone(data['pool_confirmed_paid_btc'])
            self.assertEqual(req('/api/asic/add',{'host':'8.8.8.8','name':'Bad'},auth=True)[0],400)
            self.assertEqual(req('/api/asic/add',{'host':'127.0.0.1','name':'Test ASIC'},auth=True)[0],200)
            self.assertEqual(req('/api/asic/switchpool',{'host':'127.0.0.1','port':4028,'index':0},auth=True)[0],400)
        finally:
            server.shutdown();server.server_close()

if __name__=='__main__':unittest.main()
