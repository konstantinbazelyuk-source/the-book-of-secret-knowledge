import importlib,hashlib,json,math,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock
from PIL import Image

P=Path(os.environ.get('KOKORO_TEST_PROJECT',Path(__file__).resolve().parents[3])).resolve()
S=Path(os.environ.get('KOKORO_TEST_SHIPYARD',P.parent/'Kokoro_Engineering_Shipyard_v1_2')).resolve()
V=P/'exports'/'installed_visual_action_v1_6'
sys.path[:0]=[str(S),str(V),str(P/'exports'/'installed_reality_anchor')]
from yard.core import YardProject
import visual_action as vis

class VisualActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=YardProject(P)
        cls.source=vis.imports(cls.p,S)
    def test_sources_sha_pinned(self):
        for filename in ('Kokoro_Geometric_Interaction_Studio_v2_3.zip','Golf-Ripple-Digital-Eyes-Engine-v0.2-Complete.zip'):
            f,sha=vis.verified_archive(self.p,filename)
            self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),sha)
    def test_camera_calibration_two_unique_frames(self):
        c=vis.calibrate(self.p,self.source)
        self.assertEqual([r['instruction_degrees'] for r in c],[10,40])
        self.assertEqual(len({r['image_sha256'] for r in c}),2)
    def test_goal_25_decision(self):
        r=vis.decide(self.p,S,V/'goal_source_25_render.png',self.source)
        self.assertEqual(r['command_degrees'],25)
        self.assertTrue(r['distinct_from_calibration_images'])
        self.assertLess(r['camera']['pose']['reprojection_rmse_px'],1.)
    def test_goal_32_decision(self):
        r=vis.decide(self.p,S,V/'goal_source_32_render.png',self.source)
        self.assertEqual(r['command_degrees'],32)
        self.assertTrue(r['distinct_from_calibration_images'])
    def test_original_golf_pixels_verified(self):
        r=vis.measure_png(V/'goal_source_25_render.png',self.source)
        self.assertEqual(r['golf']['sourceHash'],r['image_sha256'])
        self.assertGreater(r['golf']['edgeFraction'],0)
    def test_copy_outside_cargo_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad=Path(tmp)/'copy.png';bad.write_bytes((V/'goal_source_25_render.png').read_bytes())
            with self.assertRaises(ValueError):vis.decide(self.p,S,bad,self.source)
    def test_known_calibration_excluded(self):
        r=vis.decide(self.p,S,P/'runs/run_5d378fc49433/frame_004.png',self.source)
        self.assertFalse(r['distinct_from_calibration_images'])
    def test_missing_markers_rejected(self):
        with tempfile.TemporaryDirectory(dir=V) as tmp:
            blank=Path(tmp)/'blank.png';Image.new('RGB',(320,420),(28,28,28)).save(blank)
            with self.assertRaises(ValueError):vis.decide(self.p,S,blank,self.source)
    def test_non_png_rejected(self):
        with tempfile.TemporaryDirectory(dir=V) as tmp:
            fake=Path(tmp)/'malformed.png';fake.write_bytes(b'not a png')
            with self.assertRaises(ValueError):vis.decide(self.p,S,fake,self.source)
    def test_wrong_label_not_used_by_decision(self):
        r=vis.decide(self.p,S,V/'goal_source_32_render.png',self.source)
        evidence=json.loads((V/'ACCEPTANCE_EVIDENCE.json').read_text())
        self.assertEqual(r['command_degrees'],evidence['case_studies'][1]['heldout_source_command_for_evaluation_only_deg'])
    def test_two_executed_outputs_persist(self):
        for angle in [25,32]:
            candidates=[json.loads(p.read_text()) for p in V.glob('action_*.json')]
            result=next(r for r in candidates if r['visual_decision']['command_degrees']==angle)
            self.assertEqual(result['visual_decision']['command_degrees'],angle)
            self.assertLess(result['visual_endpoint_error_rad'],.01)
            self.assertTrue(result['colony']['output_parity_vs_serial'])
            self.assertEqual(result['colony']['source_episodes'],6+(1 if angle==25 else 2))
            self.assertTrue((V/('action_'+result['new_spatial_episode_id']+'.json')).is_file())
    def test_autoselect_colony_mode(self):
        import subprocess
        r=vis.run_colony(self.p,S,workers=0)
        self.assertEqual(r['execution_mode'],'serial')
        self.assertGreaterEqual(r['work_units'],160)
        self.assertEqual(r['work_units'],r['source_episodes']*20)
        self.assertTrue(r['output_parity_vs_serial'])
    def test_source_name_or_hash_corruption_rejected(self):
        orig=list(self.p.data['packages'])
        try:
            self.p.data['packages']=[dict(x,sha256=('0'*64 if x['name'].startswith('Golf-Ripple-Digital-Eyes-Engine') else x['sha256'])) for x in orig]
            with self.assertRaises(ValueError):vis.verified_archive(self.p,'Golf-Ripple-Digital-Eyes-Engine-v0.2-Complete.zip')
        finally:self.p.data['packages']=orig
    def test_original_v23_pose_is_pixel_driven(self):
        a=vis.measure_png(V/'goal_source_25_render.png',self.source)
        b=vis.measure_png(V/'goal_source_32_render.png',self.source)
        self.assertGreater(b['arm_angle_rad'],a['arm_angle_rad'])
        self.assertNotEqual(a['image_sha256'],b['image_sha256'])

if __name__=='__main__':unittest.main()
