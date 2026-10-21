"""Real Node and real filesystem tests of persisted structural neuron sessions."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from ripple_native.structural import run_with_storage, _read
from ripple_native.jobs import execute, validate_job

ROOT = Path(__file__).resolve().parent.parent

def node(program, args, timeout=90):
    p=subprocess.run(['node',str(ROOT/'integrations'/program)],
                     input=json.dumps(args),capture_output=True,text=True,timeout=timeout)
    if p.returncode:raise RuntimeError(p.stderr.strip())
    return json.loads(p.stdout)

class StructuralPersistence(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.base=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def session(self,p):return run_with_storage(p,str(self.base),node)

    def test_original_scheduler_dispatch(self):
        a=execute('structural_plasticity',{'state_policy':'start','state_id':'sched','frames':240},str(self.base))
        self.assertEqual(a['kind'],'structural_plasticity')
        self.assertTrue(a['actual_execution'])
        self.assertTrue(a['simulated_data'])
        self.assertEqual(a['output']['checkpoint']['frame'],240)
        b=execute('structural_plasticity',{'state_policy':'continue','state_id':'sched','frames':560},str(self.base))
        self.assertEqual(b['output']['end_frame'],800)
        self.assertEqual(b['output']['topology_events']['spikes'],416)

    def test_replay_equals_single(self):
        a=self.session({'frames':240,'state_id':'A','state_policy':'start'})
        self.assertNotIn('checkpoint_state',a)
        b=self.session({'frames':560,'state_id':'A','state_policy':'continue'})
        single=self.session({'frames':800})
        self.assertEqual(b['final_links'],single['final_links'])
        self.assertEqual(b['per_neuron_spikes'],single['per_neuron_spikes'])
        self.assertEqual(_read(self.base/'neuron_states/A.json')['frame'],800)

    def test_corruption_detected_without_advancement(self):
        self.session({'frames':80,'state_id':'A','state_policy':'start'})
        path=self.base/'neuron_states/A.json'
        value=json.loads(path.read_text())
        value['payload']['frame']=3
        path.write_text(json.dumps(value))
        before=path.read_bytes()
        with self.assertRaisesRegex(ValueError,'digest'):
            self.session({'frames':40,'state_id':'A','state_policy':'continue'})
        self.assertEqual(before,path.read_bytes())

    def test_start_protects_existing_state(self):
        self.session({'frames':80,'state_id':'A','state_policy':'start'})
        with self.assertRaises(FileExistsError):
            self.session({'frames':40,'state_id':'A','state_policy':'start'})
        with self.assertRaisesRegex(RuntimeError,'checkpoint'):
            self.session({'frames':40,'state_id':'A','state_policy':'continue','seed':99})
        self.assertEqual(_read(self.base/'neuron_states/A.json')['frame'],80)

    def test_independent_sessions_and_safe_paths(self):
        self.session({'frames':80,'state_id':'A','state_policy':'start'})
        self.session({'frames':60,'state_id':'B','state_policy':'start'})
        self.assertEqual(_read(self.base/'neuron_states/A.json')['frame'],80)
        self.assertEqual(_read(self.base/'neuron_states/B.json')['frame'],60)
        for name in ('../escape','bad name','x'*49):
            with self.assertRaises(ValueError):self.session({'state_id':name,'state_policy':'start'})
            with self.assertRaises(ValueError):validate_job('structural_plasticity',{'state_id':name,'state_policy':'start'})

    def test_parallel_continuation_is_serialized(self):
        self.session({'frames':80,'state_id':'shared','state_policy':'start'})
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:self.session({'frames':40,'state_id':'shared','state_policy':'continue'}),range(2)))
        self.assertEqual(sorted(x['end_frame'] for x in results),[120,160])
        self.assertEqual(_read(self.base/'neuron_states/shared.json')['frame'],160)

    def test_internal_state_cannot_be_submitted_by_client(self):
        for bad in ({'state_policy':'reset'},
                    {'state_id':'../escape'},
                    {'checkpoint_state':{}},
                    {'save_state':True},
                    {'frames':4000,'nodes':32}):
            with self.assertRaises(ValueError):validate_job('structural_plasticity',bad)

if __name__=='__main__':unittest.main()
