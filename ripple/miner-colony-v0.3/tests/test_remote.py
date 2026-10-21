import tempfile
import threading
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from miner import GENESIS_HEADER,sha256d
from ripple_miner.remote import RemoteClient,RemoteServer,url_allowed

class RemoteTests(unittest.TestCase):
    def test_host_validation(self):
        with self.assertRaises(ValueError):url_allowed('http://example.com')
        self.assertEqual(url_allowed('http://127.0.0.1:8990'),'http://127.0.0.1:8990')
    def test_worker_auth_and_proofs(self):
        secret='temporary-test-token-22chr+'
        server=RemoteServer(('127.0.0.1',0),secret)
        t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
        try:
            client=RemoteClient('http://127.0.0.1:'+str(server.server_port),secret)
            self.assertEqual(client.health()['kind'],'actual CPU hashing')
            count,shares=client.scan(GENESIS_HEADER[:76],0,100,(1<<256)-1,(1<<256)-1)
            self.assertEqual(count,100)
            self.assertEqual(len(shares),100)
            self.assertEqual(shares[0][1],sha256d(GENESIS_HEADER[:76]+bytes(4))[::-1].hex())
            with self.assertRaises(Exception):RemoteClient(client.url,'incorrect-not-valid-token').health()
        finally:
            server.shutdown();server.server_close();t.join(3)
