"""Encode only checked native renders; verify decoded frames and provenance."""
import hashlib,json,os,struct,subprocess
from pathlib import Path
from delivery_gate import issues
out=Path(os.environ['KOKORO_OUTPUT_DIR']).resolve();frames=out/'frames'
r=json.loads((out/'render_receipt.json').read_text());assert not issues(r),issues(r)
for entry in r['frames']:
    p=frames/f"frame_{entry['frame']:04d}.png"
    assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['png_sha256'],str(p)
def run(cmd):
    p=subprocess.run(cmd,capture_output=True,text=True,check=True,timeout=120)
    return p.stdout
video=out/'kokoro-motion-review.mp4';gif=out/'kokoro-motion-review.gif'
run(['ffmpeg','-v','error','-y','-framerate','12','-start_number','1','-i',str(frames/'frame_%04d.png'),'-frames:v','60','-an','-c:v','libx264','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(video)])
run(['ffmpeg','-v','error','-y','-framerate','12','-start_number','1','-i',str(frames/'frame_%04d.png'),'-filter_complex','[0:v]scale=300:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=sierra2_4a','-frames:v','60','-loop','0',str(gif)])
probe=json.loads(run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,pix_fmt,width,height,nb_read_frames,r_frame_rate:format=duration','-of','json',str(video)]))
s=probe['streams'][0]
assert s['codec_name']=='h264' and s['pix_fmt']=='yuv420p'
assert int(s['nb_read_frames'])==60 and abs(float(probe['format']['duration'])-5)<.05
assert (s['width'],s['height'])==(360,480)
decoded=run(['ffmpeg','-v','error','-i',str(video),'-map','0:v','-f','framemd5','-'])
unique={line.split(',')[-1].strip() for line in decoded.splitlines() if line and not line.startswith('#')}
assert len(unique)>=20,'Decoded video lacks distinct frames'
data=video.read_bytes();boxes=[];pos=0
while pos+8<=len(data):
    size,tag=struct.unpack('>I4s',data[pos:pos+8])
    if size==1:size=struct.unpack('>Q',data[pos+8:pos+16])[0]
    if size==0:size=len(data)-pos
    assert size>=8
    boxes.append(tag.decode('ascii'));pos+=size
assert boxes.index('moov')<boxes.index('mdat'),'Not faststart'
assert gif.read_bytes()[:6] in (b'GIF87a',b'GIF89a')
for p in (video,gif):assert p.stat().st_size<8_000_000,'Preview too large'
report={'source_sha256':r['source_sha256_before'],'mp4_probe':probe,'decoded_distinct_frames':len(unique),'faststart':True,'media':[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (video,gif)],'checks':'Native source provenance, 60 PNGs, saved head/jaw/eyelid motion, decoded video variation and stream metadata checked. Browser playback remains separate.'}
(out/'media_verification.json').write_text(json.dumps(report,indent=2))
(out/'ATTRIBUTION.txt').write_text('Rain Rig (CC) Blender Foundation | studio.blender.org\nSource rig: Rain v2, CC BY 4.0.\nKokoro derivative: silver hair, altered face/shell/materials, heart core, added hair bones and eye anchors.\nActual Blender diagnostic animation; not a final likeness or live AI controller.\n')
(out/'README.md').write_text('# Kokoro — actual motion preview\n\n![Actual Kokoro Blender rig: blink, mouth and head movement](kokoro-motion-review.gif)\n\nFive-second loop rendered from the saved Kokoro v0.3 Blender model. No project download is needed to view this page. This is a rig check, not the final character likeness or a live AI controller.\n\nRain Rig (CC) Blender Foundation | studio.blender.org — CC BY 4.0; modified as Kokoro.\n')
print(json.dumps(report,indent=2))
