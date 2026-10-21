import hashlib,io,json,math,tempfile,unittest,zipfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]))
from controller import KinematicPlant,SQLiteJournal,load_v13_cargo,replay,validate_target
from reachy_adapter import send_trajectory

PNG=b'\x89PNG\r\n\x1a\n' + b'virtual-test-png-bytes'

def mock_cargo(path, *,tamper=False,mixed=False):
    series=[]
    with zipfile.ZipFile(path,'w') as z:
        for j in range(1,4):
            row={'frame':j,'sim_time_s':j*.2,'continuity_capsule_hash':'src' if not mixed or j<3 else 'other',
                 'virtual_actual_angles_rad':{'head':j*.04},'wrist_world_xyz_m':[.86,1.28,.38],
                 'image_sha256':hashlib.sha256(PNG).hexdigest()}
            z.writestr(f'runs/session/frame_{j-1:03}.png',PNG if not tamper or j<3 else PNG+b'forged')
            series.append(row)
        z.writestr('runs/session/timeline.json',json.dumps(series))

class TestReplay(unittest.TestCase):
    def test_validated_replay(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);mock_cargo(p/'cargo.zip');series,source=load_v13_cargo(str(p/'cargo.zip'))
            r=replay(series,source,p/'out')
            self.assertEqual(r['steps'],30)
            self.assertEqual(r['source']['validated_rendered_pngs'],3)
            self.assertTrue(r['output_event_chain_verified'])
            self.assertGreater(r['last_simulated_yaw_deg'],0)
            with SQLiteJournal(p/'out/events.sqlite') as l:self.assertTrue(l.verify())
            dry=send_trajectory(p/'out/trajectory.csv');self.assertEqual(dry['mode'],'dry-run')
    def test_refuse_modified_rendered_png(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.zip';mock_cargo(p,tamper=True)
            with self.assertRaisesRegex(ValueError,'hash mismatch'):load_v13_cargo(str(p))
    def test_refuse_mixed_continuity(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.zip';mock_cargo(p,mixed=True)
            with self.assertRaisesRegex(ValueError,'Continuity'):load_v13_cargo(str(p))
    def test_target_rejects_nan_and_unknown_and_bad_range(self):
        for x in ({'neck_yaw':float('nan')},{'invented_axis':1},{'neck_yaw':70},{'mouth_open':2}):
            with self.assertRaises(ValueError):validate_target(x)
    def test_plant_bounds_velocity_and_estop(self):
        p=KinematicPlant();p.command({'neck_yaw':30});prior=0
        for _ in range(100):
            pos=p.step()['neck_yaw'];self.assertLessEqual(abs(pos-prior),60*.02+1e-6);prior=pos
        p.estop()
        with self.assertRaises(RuntimeError):p.step()
    def test_journal_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with SQLiteJournal(Path(d)/'db.sqlite') as j:
                j.append({'x':1});j.append({'x':2});self.assertTrue(j.verify())
                j.db.execute("UPDATE events SET event_json='{}' WHERE seq=1");j.db.commit()
                self.assertFalse(j.verify())
    def test_no_accidental_replay_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);mock_cargo(p/'c.zip');ss,source=load_v13_cargo(str(p/'c.zip'))
            replay(ss,source,p/'o')
            with self.assertRaisesRegex(ValueError,'overwrite'):replay(ss,source,p/'o')
    def test_reachy_refuses_overspeed_movement(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.csv';p.write_text('model_time_s,simulated_yaw_deg\n0.02,18\n')
            with self.assertRaises(ValueError):send_trajectory(p)
    def test_invalid_time_and_physical_limit_unsupported(self):
        with self.assertRaises(ValueError):KinematicPlant(dt=0)
        with self.assertRaises(ValueError):KinematicPlant(dt=100)
        with self.assertRaises(ValueError):KinematicPlant(dt=float('nan'))
if __name__=='__main__':unittest.main()

class TestExpression(unittest.TestCase):
    def test_explicit_expressive_control_runs(self):
        from controller import simulate_expressions,AXES
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); spec={'duration_s':.8,'keyframes':[
                {'time_s':0,'target':{'blink_left':1,'blink_right':1,'mouth_open':.5,'neck_pitch':8,'eyes_horizontal':10,'mouth_smile':.2,'brow':.5}},
                {'time_s':.4,'target':{'blink_left':0,'blink_right':0,'mouth_open':0}}]}
            (p/'k.json').write_text(json.dumps(spec))
            r=simulate_expressions(p/'k.json',p/'o')
            self.assertEqual(r['steps'],40)
            self.assertEqual(len(r['end_state']),len(AXES))
            self.assertTrue(r['journal_verified'])
            self.assertGreater(r['end_state']['neck_pitch'],0)
    def test_expression_rejects_bad_user_keyframe(self):
        from controller import simulate_expressions
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'k.json').write_text(json.dumps({'duration_s':1,'keyframes':[{'time_s':2,'target':{'neck_yaw':5}}]}))
            with self.assertRaises(ValueError):simulate_expressions(p/'k.json',p/'o')