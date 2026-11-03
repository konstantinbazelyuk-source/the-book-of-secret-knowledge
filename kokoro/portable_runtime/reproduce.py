"""Reproduce the recovered GLB pipeline with explicit source/evidence boundaries."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time,zipfile
from receipt_fix import apply as apply_receipt_fix
HERE=Path(__file__).resolve().parent
W=Path('/tmp/kokoro_runtime_transfer_20261102')
B=Path('/tmp/kokoro_controller_integration_20261102')
OUT=Path(os.environ['KOKORO_DELIVERY_OUT']).resolve()
SOURCE='be9cb6b2575334ff912f45a9ff226a552f7216d2b1d7707ba830f8867690ce93'
AUDIT='662d220244fb5973f89ae49ff123819c5c764313ef2662a56b0871308b401af9'
NATIVE_ZIP='771c0706275782909cc25a94ba51585df0de547e62bea7c0bd3d1562aa6d7e2f'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def extract(archive,dest):
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  for i in z.infolist():
   n=Path(i.filename)
   assert not n.is_absolute() and '..' not in n.parts and '\\' not in i.filename
  z.extractall(dest)
def command(name,args,cwd=None,timeout=240,expected=0):
 start=time.perf_counter();r=subprocess.run(list(map(str,args)),cwd=cwd,env=os.environ,capture_output=True,text=True,timeout=timeout)
 (W/'audit_20261102'/f'{name}.log').write_text(r.stdout+'\n'+r.stderr)
 print(name,'exit',r.returncode,'seconds',round(time.perf_counter()-start,2),r.stdout[-1200:],r.stderr[-1200:],flush=True)
 if expected is not None:assert r.returncode==expected,(name,r.returncode)
 return r
assert not W.exists(),'Use a fresh runner: never overwrite another active research workspace'
W.mkdir();(W/'audit_20261102').mkdir();OUT.mkdir(parents=True,exist_ok=True)
audit=Path(os.environ['KOKORO_AUDIT_ZIP']);nativezip=Path(os.environ['KOKORO_NATIVE_ZIP'])
assert digest(audit)==AUDIT and digest(nativezip)==NATIVE_ZIP
extract(audit,W)
archived=W/'archived_reports';archived.mkdir()
for n in ['portable_evidence','control_response_evaluation.json','material_conversion.json','direct_display_report.json','gui_portable_report.json','final_gltf_validation.json']:
 p=W/n
 if p.exists():shutil.move(p,archived/n)
preserved=json.loads((W/'integration_manifest.json').read_text())['unmodified_controller_files']
assert all(digest(W/'studio'/n)==h for n,h in preserved.items()),'Original controller or sensor source drift'
B.mkdir(exist_ok=True);(B/'native').mkdir(exist_ok=True);shutil.copytree(W/'studio',B/'studio',dirs_exist_ok=True)
extract(nativezip,B/'source_package')
models=list((B/'source_package').rglob('Kokoro_Rain_Derivative_v0_3.blend'));assert len(models)==1
native=B/'native/Kokoro_Rain_Derivative_v0_3.blend';shutil.copy2(models[0],native);assert digest(native)==SOURCE
shutil.copy2(HERE/'test_portable_receipt.py',W/'studio/tests/test_portable_receipt.py')
red=command('receipt_red',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_portable_receipt.py','-v'],W/'studio',expected=None)
assert red.returncode!=0 and 'failures=9' in red.stderr
apply_receipt_fix(W)
command('receipt_green',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_portable_receipt.py','-v'],W/'studio')
p=W/'repair_export.py';s=p.read_text();s=s.replace('export_morph_normal=False,export_morph_tangent=False','export_morph_normal=False,export_morph_tangent=False,export_tangents=True');p.write_text(s)
blender=Path(os.environ['KOKORO_BLENDER'])
for n in ['export_first.py','repair_export.py','sample_controls.py','attach_anchors.py']:
 command(n,[blender,'--background','--factory-startup','--disable-autoexec','-t','4','--python-exit-code','1','--python',W/n],W,timeout=240)
assert digest(native)==SOURCE
command('npm_ci',['npm','ci','--ignore-scripts','--no-audit','--no-fund'],W/'web')
chrome=shutil.which('google-chrome') or shutil.which('google-chrome-stable') or shutil.which('chromium');assert chrome,'Chrome/Chromium required'
link=B/'runtime/usr/lib/chromium/chromium';link.parent.mkdir(parents=True,exist_ok=True);link.symlink_to(chrome)
keys=['PATH','HOME','DISPLAY','LANG','LIBGL_ALWAYS_SOFTWARE','LP_NUM_THREADS']
(W/'browser_env.json').write_text(json.dumps({k:os.environ[k] for k in keys if k in os.environ}))
manifest={'schema':'kokoro/portable-runtime/1','source_sha256':SOURCE,'files':{n:digest(W/n) for n in ['kokoro_runtime.glb','control_response.json','web/index.html','web/viewer.mjs','web/rig_view.mjs','web/portable_driver.mjs','web/portable_worker.mjs']},'classification':'Runtime model plus sampled constraint response; original native source preserved'}
(W/'runtime_manifest.json').write_text(json.dumps(manifest,indent=2))
validation="import fs from 'node:fs';import validator from 'gltf-validator';const r=await validator.validateBytes(new Uint8Array(fs.readFileSync('../kokoro_runtime.glb')),{uri:'kokoro_runtime.glb'});fs.writeFileSync('../final_gltf_validation.json',JSON.stringify(r,null,2));console.log(JSON.stringify(r.issues));if(r.issues.numErrors)process.exitCode=1;"
command('gltf_validate',['node','--input-type=module','-e',validation],W/'web')
command('driver_tests',['node','--test','test_portable_driver.mjs'],W/'web')
held=native.with_suffix('.blend.offline_only');native.rename(held)
try:
 command('live_motor',[sys.executable,HERE/'live_motor_probe.py'],W)
 command('runtime_capture',['node','runtime_test.mjs'],W/'web')
 command('viewport',['node','viewport_test.mjs'],W/'web')
 command('context_loss',['node','context_loss_test.mjs'],W/'web')
finally:held.rename(native)
assert digest(native)==SOURCE
from PIL import Image,ImageDraw
media=W/'portable_evidence';combined=media/'combined';combined.mkdir(exist_ok=True)
report=json.loads((media/'runtime_report.json').read_text());assert len(report['frames'])==30
for i,item in enumerate(report['frames'],1):
 a=media/f'frame_{i:04d}.png';b=media/f'face_{i:04d}.png'
 assert digest(a)==item['png_sha256'] and digest(b)==item['face_png_sha256']
 im1=Image.open(a).convert('RGB');im2=Image.open(b).convert('RGB');assert im1.size==im2.size
 canvas=Image.new('RGB',(im1.width*2,im1.height+30),(24,30,42));canvas.paste(im1,(0,30));canvas.paste(im2,(im1.width,30));draw=ImageDraw.Draw(canvas)
 draw.text((9,9),'KOKORO / GLB + controller',fill='white');draw.text((im1.width+9,9),'Face controls / no Blender runtime',fill='white');canvas.save(combined/f'frame_{i:04d}.png')
video=OUT/'kokoro-portable-runtime.mp4';gif=OUT/'kokoro-portable-runtime.gif'
command('encode_video',['ffmpeg','-v','error','-y','-framerate','5','-i',combined/'frame_%04d.png','-frames:v','30','-an','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',video])
command('encode_gif',['ffmpeg','-v','error','-y','-i',video,'-filter_complex','[0:v]fps=5,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=sierra2_4a','-loop','0',gif])
probe=json.loads(command('media_probe',['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,pix_fmt,nb_read_frames,width,height:format=duration','-of','json',video]).stdout)
assert probe['streams'][0]['codec_name']=='h264' and int(probe['streams'][0]['nb_read_frames'])==30 and abs(float(probe['format']['duration'])-6)<.05
with Image.open(gif) as g:assert g.n_frames==30 and g.info.get('loop')==0
for p in [video,gif]:assert p.stat().st_size<8_000_000
package=OUT/'Kokoro_Portable_Runtime_v0_1';runtime=package/'runtime';runtime.mkdir(parents=True,exist_ok=True)
for n in ['kokoro_runtime.glb','control_response.json','runtime_manifest.json']:shutil.copy2(W/n,runtime/n)
(runtime/'web').mkdir()
for n in ['index.html','viewer.mjs','rig_view.mjs','portable_driver.mjs','portable_worker.mjs','package.json','package-lock.json']:shutil.copy2(W/'web'/n,runtime/'web'/n)
overlay=package/'studio_overlay';overlay.mkdir()
for n in ['kokoro_bridge/engine.py','kokoro_bridge/desktop.py','kokoro_bridge/portable_session.py','tests/test_portable_receipt.py','tests/test_portable_engine_contract.py']:
 p=overlay/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/'studio'/n,p)
conversion=package/'offline_conversion';conversion.mkdir()
for n in ['export_first.py','repair_export.py','sample_controls.py','attach_anchors.py']:shutil.copy2(W/n,conversion/n)
evidence=package/'evidence';evidence.mkdir()
for n in ['control_response_evaluation.json','material_conversion.json','final_gltf_validation.json','integration_manifest.json','fresh_controller_run.json']:shutil.copy2(W/n,evidence/n)
shutil.copytree(W/'audit_20261102',evidence/'fresh_checks');shutil.copy2(media/'runtime_report.json',evidence/'runtime_report.json');shutil.copy2(media/'heldout_surface_error.json',evidence/'heldout_surface_error.json');shutil.copytree(combined,evidence/'recorded_frames')
readme='''# Kokoro portable GLB runtime v0.1

Use the existing Kokoro controller/configuration studio. Blender is needed only to author or re-export the model, not to display the converted character.

The runtime folder contains the GLB, sampled rig-response data and WebGL renderer. From runtime/web run `npm ci --ignore-scripts`. Node 22.12+ and a locally installed Chrome/Chromium are required. The existing Python studio retains its own dependencies.

The studio_overlay targets the already delivered Controller Rig Integration v0.1. Back up the corresponding files before applying the overlay; do not replace an independently modified engine or desktop without merging its changes. In the existing Native rig tab select Node, the runtime folder, and Chrome/Chromium, enable the direct browser window, and connect the portable model. Existing commands and actual simulated motor positions drive the character. Facial controls remain manual. Save/Load/Restart preserve profiles without auto-launching executables.

This is a three-motor adapter (head, right arm, right forearm) plus blink, jaw, gaze and pupil controls. It is not a full port of every Rain rig constraint. Offline sampled control combinations approximate the source. The source .blend is separately preserved, not duplicated here. Neutral procedural material channels are baked; refraction, subsurface lighting and non-armature modifiers are not claimed identical.

The original VTK optical feedback remains separate and unchanged. No physical sensing, generalized cognition, automatic emotion or speech is claimed. Linux was tested; Windows and phones were not.

Credit: Rain Rig (CC) Blender Foundation | studio.blender.org — CC BY 4.0. Modified as Kokoro.
'''
(package/'README.md').write_text(readme)
(package/'ATTRIBUTION.txt').write_text('Rain Rig (CC) Blender Foundation | studio.blender.org\nCC BY 4.0. Modified as Kokoro.\nNative source SHA256 '+SOURCE+'\n')
asset_manifest={str(p.relative_to(package)):digest(p) for p in package.rglob('*') if p.is_file()};(package/'MANIFEST_SHA256.json').write_text(json.dumps(asset_manifest,indent=2))
archive=Path(shutil.make_archive(str(OUT/'Kokoro_Portable_Runtime_v0_1'),'zip',OUT,package.name))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
live=json.loads((W/'audit_20261102/live_motor_report.json').read_text());validation=json.loads((W/'final_gltf_validation.json').read_text())
result={'source_sha256':SOURCE,'source_unchanged':True,'preserved_controller_files':len(preserved),'glb_sha256':digest(runtime/'kokoro_runtime.glb'),'glb_bytes':(runtime/'kokoro_runtime.glb').stat().st_size,'format_errors':validation['issues']['numErrors'],'format_warnings':validation['issues']['numWarnings'],'runtime':report['runtime'],'native_model_absent_during_runtime':True,'live_motor_frames':len(live['frames']),'live_motor_seconds':live['wall_seconds'],'live_matches_original_full_engine':live['matches_original_interaction_engine_frames'],'capture_frames':30,'render_ms_median':report['render_ms_median'],'capture_wall_seconds':report['wall_seconds_with_capture'],'heldout_max_vertex_error_model_units':report['heldout_max_vertex_error_model_units'],'receipt_tests':10,'driver_tests':15,'media':[{'name':p.name,'sha256':digest(p),'bytes':p.stat().st_size} for p in [gif,video,archive]],'boundaries':['Not full Blender constraint equivalence','Held-out surface comparison applies independently evaluated source joint/morph data to the exported mesh, not full native modifier output','No GLB-camera feedback connected to the original VTK visual servo','Rig appearance is still a work in progress','Recorded playback rate is not proof of realtime performance on other machines']}
(OUT/'REPRODUCTION_RESULT.json').write_text(json.dumps(result,indent=2));print('REPRODUCTION_COMPLETE',json.dumps(result),flush=True)
