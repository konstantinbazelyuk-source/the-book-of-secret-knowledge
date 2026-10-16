import json
from pathlib import Path
import sys
import threading
import unittest
import urllib.error
import urllib.request
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from superneuron import parse_fasta
from serve import make_server
F=Path(__file__).resolve().parents[1]/'data/RHO_NM_000539.3_mirror.fasta'
class UITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=make_server(parse_fasta(F.read_text(),'NM_000539.3')['rna'],port=0)
        cls.t=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.t.start()
        cls.base=f'http://127.0.0.1:{cls.http.server_port}'
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.t.join()
    def req(self,path,data=None):
        body=None if data is None else json.dumps(data).encode()
        req=urllib.request.Request(self.base+path,body,headers={'Content-Type':'application/json'} if body else {})
        with urllib.request.urlopen(req,timeout=3) as r:return json.loads(r.read())
    def test_actual_controls_and_state_changes(self):
        first=self.req('/api/state')
        result=self.req('/api/step',{'rgb':[.8,.8,.8],'steps':150})
        last=self.req('/api/state')
        self.assertGreater(last['time_s'],first['time_s'])
        self.assertEqual(last['spikes'],result['spikes_total'])
        self.assertGreater(last['voltage'],0)
        self.assertEqual(self.req('/api/reset',{})['spikes'],0)
    def test_input_validation(self):
        with self.assertRaises(urllib.error.HTTPError):self.req('/api/step',{'rgb':[-1,0,0]})
        with self.assertRaises(urllib.error.HTTPError):self.req('/api/step',{'rgb':[1,1,1],'steps':900})
if __name__=='__main__':unittest.main()