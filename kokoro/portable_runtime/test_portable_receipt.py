"""Negative transport fixtures; these tests do not claim model deformation."""
import json,queue,subprocess,sys,tempfile,threading,unittest
from collections import deque
from pathlib import Path
from kokoro_bridge.portable_session import PortableRigSession
from kokoro_bridge.native_rig import NativeRigProfile,pose_from_packet
ASSET='7f2951acb7003286c1e1b9bdaf8f36feeacdeb99175cb78d23998634e0dc1bf0'
class PortableReceiptIntegrity(unittest.TestCase):
 def session(self,mode):
  s=PortableRigSession.__new__(PortableRigSession);s.timeout=2;s.asset_sha256=ASSET;s.display_mode='window'
  s._temporary=tempfile.TemporaryDirectory();s.out=Path(s._temporary.name);s.messages=queue.Queue(maxsize=16);s.logs=deque(maxlen=160);s.last_frame=0;s.last_time=-1.;s.closed=False
  script='''import sys,json
mode=sys.argv[1];asset=sys.argv[2]
for line in sys.stdin:
 q=json.loads(line)
 if q.get('operation')=='close':break
 p=json.loads(q['envelope']['canonical_pose_body'])
 r={'status':'ok','source_sha256':p['source_sha256'],'asset_sha256':asset,'frame':p['frame'],'sim_time_s':p['sim_time_s'],'pose_sha256':q['envelope']['pose_sha256'],'profile_sha256':p['profile_sha256'],'applied_joint_positions_rad':p['joints_rad'],'manual_face_controls':p['face'],'rendered':q['render'],'resolution':[p['camera']['render_width'],p['camera']['render_height']],'view':'external_'+p['camera']['view'],'display_mode':'window','image_file':None,'image_delivery':'direct_browser' if q['render'] else 'not_rendered','feeds_legacy_feedback':False}
 if mode=='time':r['sim_time_s']+=1
 if mode=='profile':r['profile_sha256']='f'*64
 if mode=='joints':r['applied_joint_positions_rad']['head']=.12
 if mode=='face':r['manual_face_controls']['blink']=1
 if mode=='asset':r['asset_sha256']='a'*64
 if mode=='draw':r['rendered']=not q['render']
 if mode=='resolution':r['resolution']=[1,1]
 if mode=='view':r['view']='external_face'
 if mode=='delivery':r['image_delivery']='not_rendered'
 print('KOKORO_NATIVE '+json.dumps(r),flush=True)
'''
  s.process=subprocess.Popen([sys.executable,'-u','-c',script,mode,ASSET],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
  s.reader=threading.Thread(target=s._read,daemon=True);s.reader.start();self.addCleanup(s.close);return s
 def pose(self):return pose_from_packet({'frame':1,'sim_time_s':.2,'virtual_actual_angles_rad':{'arm_R':0.,'forearm_R':0.,'head':0.}},NativeRigProfile())
 def test_matching_receipt_is_accepted(self):
  s=self.session('valid');self.assertEqual(s.apply(self.pose())['frame'],1);self.assertFalse(s.closed)
 def reject(self,mode):
  s=self.session(mode)
  with self.assertRaises(ValueError):s.apply(self.pose())
  self.assertTrue(s.closed);self.assertEqual(s.last_frame,0)
for field in ['time','profile','joints','face','asset','draw','resolution','view','delivery']:
 setattr(PortableReceiptIntegrity,'test_rejects_wrong_'+field,lambda self,key=field:self.reject(key))
