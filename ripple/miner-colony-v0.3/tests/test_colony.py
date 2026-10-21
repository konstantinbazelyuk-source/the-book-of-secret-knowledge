import json
import hashlib
import shutil
import tempfile
import socketserver
import sys
import threading
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ripple_miner.asic import query_asic, valid_lan_address, normalize_status, parse_reply
from ripple_miner.colony import Cell, colony_summary
from ripple_miner.economics import estimate
from ripple_miner.tuning import evaluate
from ripple_miner.neuron import ripple_signal
from ripple_miner.controller import Controller


class MinerAPIHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data=self.request.recv(4096)
        command=json.loads(data)['command']
        if command=='summary':
            result={'STATUS':[{'STATUS':'S'}],'SUMMARY':[{'MHS 5s':200000000,'Accepted':20,'Rejected':1,'Hardware Errors':0}]}
        elif command=='devs':
            result={'DEVS':[{'Temperature':67.5}]}
        elif command=='pools':
            result={'POOLS':[{'POOL':0,'URL':'stratum+tcp://example.invalid:3333','Status':'Alive'}]}
        else:
            result={'STATUS':[{'STATUS':'S'}]}
        self.request.sendall(json.dumps(result).encode()+b'\0')

class LocalASIC(socketserver.ThreadingTCPServer):
    allow_reuse_address=True
    daemon_threads=True

class ASICNetworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=LocalASIC(('127.0.0.1',0),MinerAPIHandler)
        cls.port=cls.server.server_address[1]
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close()
    def test_asic_real_socket_parse_and_colony(self):
        summary=query_asic('127.0.0.1',self.port,'summary')
        devs=query_asic('127.0.0.1',self.port,'devs')
        pools=query_asic('127.0.0.1',self.port,'pools')
        status=normalize_status(summary,devs,pools)
        self.assertEqual(status['hashrate_hps'],200e12)
        self.assertEqual(status['temperature_c'],67.5)
        self.assertEqual(status['pools'][0]['status'],'Alive')
        cell=Cell('My Rig','127.0.0.1',self.port)
        cell.observe(status)
        self.assertEqual(colony_summary({'rig':cell})['measured_asic_hashrate_hps'],200e12)
    @unittest.skipUnless(shutil.which('node'),'Node.js absent')
    def test_controller_polls_asic_and_calculates_preserved_neuron(self):
        with tempfile.TemporaryDirectory() as temp:
            c=Controller(temp)
            try:
                c.add_node('127.0.0.1',self.port,'Physical API fixture')
                c.poll_once()
                nodes=c.status()['colony']['nodes']
                self.assertEqual(len(nodes),1)
                self.assertEqual(nodes[0]['hashrate_hps'],200e12)
                self.assertEqual(nodes[0]['ripple_neuron']['status'],'calculated')
                self.assertEqual(nodes[0]['ripple_neuron']['observations']>=1,True)
            finally:c.close()

    def test_private_ip_and_legacy_response(self):
        self.assertEqual(valid_lan_address('192.168.0.44'),'192.168.0.44')
        for host in ('8.8.8.8','google.com','0.0.0.0','169.254.1.4'):
            with self.assertRaises(ValueError):valid_lan_address(host)
        self.assertEqual(parse_reply('STATUS,STATUS=S|SUMMARY,MHS 5s=500000|')['SUMMARY'][0]['MHS 5s'],'500000')
    def test_attention_from_measured_degradation(self):
        cell=Cell('Hot ASIC','127.0.0.1')
        for x in (100,100,100,10):cell.observe({'hashrate_hps':x,'temperature_c':86,'accepted':100,'rejected':10})
        result=cell.assessment()
        self.assertEqual(result['status'],'attention')
        self.assertGreaterEqual(len(result['reasons']),2)

class NeuronLineageTests(unittest.TestCase):
    def test_locked_original_code_blob_matches_source_repo(self):
        data=(Path(__file__).resolve().parents[1]/'legacy'/'v01_ripple_core_LOCKED.cjs').read_bytes()
        git_blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        self.assertEqual(git_blob,'e98e12e5a43fd07de162dde795d0baada88fee15')
    @unittest.skipUnless(shutil.which('node'),'Node.js absent')
    def test_actual_original_ripple_neuron_executes(self):
        result=ripple_signal([[0.1,0,0.5],[0.9,0.1,0.1]])
        self.assertEqual(result['status'],'calculated')
        self.assertEqual(result['observations'],2)
        self.assertGreater(result['spike_count'],0)
        self.assertTrue(result['source'].endswith('locked v0.1'))

class CalculationTests(unittest.TestCase):
    def test_expected_returns_zero_and_cost(self):
        r=estimate(0,100e12,100000,3000,0.1)
        self.assertEqual(r['btc_per_day_expected'],0)
        self.assertAlmostEqual(r['electric_usd_day_calculated'],7.2)
        self.assertIsNone(r['pool_confirmed_paid_btc'])
    def test_probability_formula_and_input_validation(self):
        r=estimate(2**32/86400,1,100000,0,0,0,3.125)
        self.assertAlmostEqual(r['btc_per_day_expected'],3.125)
        for d in (0,-1):
            with self.assertRaises(ValueError):estimate(10,d,90000)
    def test_tuning_chooses_actual_supplied_measurement(self):
        fake=lambda w,c:{'workers':w,'chunk':c,'hashes':c*w,'elapsed_seconds':1,'hashes_per_second':w*100 + (c==20000)*400}
        r=evaluate(max_workers=2,scorer=fake)
        self.assertEqual(r['selected'],{'workers':2,'chunk':20000})

if __name__=='__main__':unittest.main()
