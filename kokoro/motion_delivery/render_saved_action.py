"""Render the existing Kokoro action, without saving or altering the source."""
import hashlib, json, os, sys, time
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from delivery_gate import EXPECTED_SOURCE, ACTION, issues
root=Path(os.environ['KOKORO_SOURCE_DIR']).resolve()
out=Path(os.environ['KOKORO_OUTPUT_DIR']).resolve();out.mkdir(parents=True,exist_ok=True)
choices=list(root.rglob('Kokoro_Rain_Derivative_v0_3.blend'))
assert len(choices)==1, f'Expected one native source, found {choices}'
src=choices[0];before=hashlib.sha256(src.read_bytes()).hexdigest()
assert before==EXPECTED_SOURCE, 'Native source checksum mismatch'
bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False)
scene=bpy.context.scene
rig=bpy.data.objects.get('RIG-rain');action=bpy.data.actions.get(ACTION)
assert rig and action and len(action.fcurves)>0,'Saved rig/action unavailable'
rig.animation_data_create();rig.animation_data.action=action
scene.render.engine='BLENDER_EEVEE'
scene.eevee.taa_render_samples=4
scene.eevee.use_gtao=True
scene.eevee.use_soft_shadows=False
scene.eevee.shadow_cube_size='512'
scene.eevee.shadow_cascade_size='512'
scene.render.resolution_x=360;scene.render.resolution_y=480
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene.render.film_transparent=False
assert scene.camera,'Saved camera missing'
scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=.69
scene.camera.location=(.16,-2,1.49)
scene.camera.rotation_euler=(Vector((0,-.02,1.35))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
frames_dir=out/'frames';frames_dir.mkdir(exist_ok=True)
records=[];started=time.time()
for frame in range(1,61):
    scene.frame_set(frame);bpy.context.view_layer.update()
    target=frames_dir/f'frame_{frame:04d}.png'
    scene.render.filepath=str(target);bpy.ops.render.render(write_still=True)
    record={'frame':frame,'png_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
      'head_z':rig.pose.bones['FK-Head'].rotation_euler.z,
      'jaw_x':rig.pose.bones['MSTR-Jaw'].rotation_euler.x,
      'left_eyelid_y':rig.pose.bones['ACT-Eyelid_Upper.L'].location.y,
      'right_eyelid_y':rig.pose.bones['ACT-Eyelid_Upper.R'].location.y}
    records.append(record)
    print('KOKORO_FRAME',json.dumps(record),flush=True)
receipt={'source_sha256_before':before,'source_sha256_after':hashlib.sha256(src.read_bytes()).hexdigest(),
  'action':action.name,'blender_version':bpy.app.version_string,'render_engine':scene.render.engine,
  'resolution':[360,480],'fps':12,'duration_seconds':5,'frames':records,
  'render_seconds':time.time()-started,'evidence':'Actual native .blend rendering of the saved diagnostic action. Not generative video, not physical hardware, not a final likeness.'}
(out/'render_receipt.json').write_text(json.dumps(receipt,indent=2))
errors=issues(receipt)
assert not errors, errors
print('KOKORO_RENDER_ACCEPTED',len(records),flush=True)
