"""Execute original motor modules against the portable worker; no VTK fixture required."""
import hashlib,json,math,os,shutil,sys,time
from pathlib import Path
W=Path('/tmp/kokoro_runtime_transfer_20261102');B=Path('/tmp/kokoro_controller_integration_20261102')
sys.path.insert(0,str(W/'studio'))
from ripple_genome.robotics import VirtualRobot
from upstream.motor_neuron_v07 import DT
from kokoro_bridge.native_rig import NativeRigProfile,pose_from_packet
from kokoro_bridge.portable_session import PortableRigSession
baseline=json.loads((W/'fresh_controller_run.json').read_text())
robot=VirtualRobot();env=dict(os.environ,KOKORO_BROWSER_UNSANDBOXED='1',KOKORO_SOFTWARE_GL='1',KOKORO_HEADLESS='0')
started=time.perf_counter();session=PortableRigSession(shutil.which('node'),W,B/'runtime/usr/lib/chromium/chromium',env=env,display_mode='window');load=time.perf_counter()-started
rows=[];t0=time.perf_counter();matched=0
try:
 for i in range(30):
  if i==0:robot.set_targets({'arm_R':.65,'forearm_R':-.35,'head':.25})
  if i==10:robot.set_targets({'arm_R':.28,'forearm_R':.25,'head':-.23})
  if i==20:robot.set_targets({'arm_R':0.,'forearm_R':0.,'head':0.})
  for _ in range(round(.2/DT)):state=robot.step(DT)
  profile=NativeRigProfile().to_dict();profile['face'].update(blink=1. if i in (6,7,22) else 0.,jaw_open=.6 if 12<=i<=17 else 0.,gaze_x=.2*math.sin(i*.2),gaze_y=.15*math.cos(i*.25),pupil=.25)
  profile=NativeRigProfile.from_dict(profile)
  actual={j:state[j]['position'] for j in state}
  assert all(abs(actual[j]-baseline['frames'][i]['pose']['joints_rad'][j])<1e-12 for j in actual),'Original engine/motor trace disagreement'
  matched+=1
  pose=pose_from_packet({'frame':i+1,'sim_time_s':round((i+1)*.2,6),'virtual_actual_angles_rad':actual},profile)
  reply=session.apply(pose,True)
  assert reply['applied_joint_positions_rad']==actual and reply['rendered'] is True
  assert session.read_frame(reply) is None and not list(session.out.glob('*.png'))
  canonical=json.dumps({k:v for k,v in pose.items() if k!='pose_sha256'},sort_keys=True,separators=(',',':'),allow_nan=False)
  rows.append({'pose':pose,'target':dict(robot.goal),'receipt':reply,'envelope':{'canonical_pose_body':canonical,'pose_sha256':pose['pose_sha256'],'canonical_profile_body':json.dumps(profile.to_dict(),sort_keys=True,separators=(',',':'),allow_nan=False)}})
 elapsed=time.perf_counter()-t0
 try:session.apply(rows[-1]['pose']);stale=False
 except ValueError:stale=True
 assert stale and not session.closed
 assert not (B/'native/Kokoro_Rain_Derivative_v0_3.blend').exists()
 report={'schema':'kokoro/portable-live-motor-rerun/1','source_sha256':profile.source_sha256,'asset_sha256':session.asset_sha256,'runtime':session.ready,'load_seconds':load,'wall_seconds':elapsed,'simulation_seconds':6.,'frames':rows,'current_motor_steps':300,'matches_original_interaction_engine_frames':matched,'direct_window_without_image_files':True,'native_source_unavailable_during_runtime':True,'blender_invoked_at_runtime':False,'stale_rejected':stale,'legacy_optical_feedback_replaced':False,'scope':'Original VirtualRobot and Ripple/motor modules freshly executed. Their 30 outputs exactly match the preserved full InteractionEngine trace; this rerun omits that separate VTK optical fixture.'}
 (W/'audit_20261102/live_motor_report.json').write_text(json.dumps(report,indent=2))
 (W/'fresh_controller_run.json').write_text(json.dumps({'frames':rows,'simulation_seconds':6.,'source':'fresh live original motor-module output'},indent=2))
 print('LIVE_MOTOR',json.dumps({k:v for k,v in report.items() if k not in ('frames','runtime')}),flush=True)
finally:session.close()
assert session.process.poll() is not None
