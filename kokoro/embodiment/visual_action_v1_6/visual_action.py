"""Kokoro visual-goal -> genuine source-pinned v2.3 motor -> memory -> source-backed colony.

Camera reports virtual object geometry only. This is fiducial-guided avatar control,
not markerless perception, original cognitive Psyche, or physical sensing.
"""
from __future__ import annotations
import argparse, hashlib, importlib, json, math, os, sqlite3, subprocess, sys, time, zipfile
from pathlib import Path
import cv2
import numpy as np

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]

def sha_bytes(data):return hashlib.sha256(data).hexdigest()
def safe_png(p:Path):
    p=Path(p).resolve()
    if not p.is_file() or p.stat().st_size>8_000_000 or p.read_bytes()[:8]!=b'\x89PNG\r\n\x1a\n':
        raise ValueError('No valid bounded target PNG')
    image=cv2.imread(str(p),cv2.IMREAD_COLOR)
    if image is None or image.ndim!=3:raise ValueError('PNG pixel decoding failed')
    return image,sha_bytes(p.read_bytes())

def verified_archive(project,name):
    from yard.core import sha256,valid_archive_info
    matches=[a for a in project.data['packages'] if a['name']==name]
    if len(matches)!=1:raise ValueError('Missing or duplicate registered source: '+name)
    item=matches[0];file=project.root/item['path']
    if sha256(file)!=item['sha256']:raise ValueError('Source package SHA changed: '+name)
    with zipfile.ZipFile(file) as z:valid_archive_info(z)
    return file,item['sha256']

def imports(project,shipyard):
    sys.path.insert(0,str(Path(shipyard).resolve()))
    from yard.core import YardProject
    from yard.engine_run import RELEASE
    bridge_dir=str((project.root/'exports'/'installed_reality_anchor').resolve())
    if bridge_dir not in sys.path:sys.path.insert(0,bridge_dir)
    archive,h=verified_archive(project,RELEASE)
    cache=project.root/'cache'/'kokoro_v23'/'Kokoro_Geometric_Interaction_Studio_v2_3'
    from yard.core import valid_archive_info
    with zipfile.ZipFile(archive) as z:
        valid_archive_info(z)
        for member in z.infolist():
            if member.is_dir():continue
            dst=(cache/member.filename.split('/',1)[-1]).resolve()
            if not dst.is_relative_to(cache.resolve()):raise ValueError('Unsafe source member')
            if not dst.is_file():
                dst.parent.mkdir(parents=True,exist_ok=True)
                dst.write_bytes(z.read(member))
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            if member.is_dir():continue
            dst=(cache/member.filename.split('/',1)[-1]).resolve()
            if not dst.is_relative_to(cache.resolve()) or not dst.is_file() or sha_bytes(dst.read_bytes())!=sha_bytes(z.read(member)):
                raise ValueError('Original v2.3 source cache altered: '+member.filename)
    if str(cache) not in sys.path:sys.path.insert(0,str(cache))
    from vision3d.geometry import observe_pixels,estimate_pose,Calibration
    from upstream.vtk_renderer import load_model
    golf_zip,golf_hash=verified_archive(project,'Golf-Ripple-Digital-Eyes-Engine-v0.2-Complete.zip')
    gp=project.root/'cache'/('golf_eyes_'+golf_hash[:16])
    target=gp/'Golf-Ripple-Digital-Eyes-v0.2'/'src'/'eyes.py'
    with zipfile.ZipFile(golf_zip) as z:
        inner='Golf-Ripple-Digital-Eyes-v0.2/src/eyes.py'
        src=z.read(inner)
    if not target.is_file():
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(src)
    if target.read_bytes()!=src:raise ValueError('Cached original Golf source changed')
    golf_dir=str(target.parent)
    if golf_dir not in sys.path:sys.path.insert(0,golf_dir)
    from eyes import vision
    from bridge import validated_episodes,anchor_episodes
    return {'observe':observe_pixels,'estimate':estimate_pose,'calibration':Calibration,'bones':load_model()[0]['bones'],
            'golf':vision,'episodes':validated_episodes,'anchor':anchor_episodes,
            'sources':{'v23_sha256':h,'golf_sha256':golf_hash}}

def measure_png(p:Path,resources):
    image,digest=safe_png(p)
    tags=resources['observe'](cv2.cvtColor(image,cv2.COLOR_BGR2RGB))
    pose=resources['estimate'](tags,resources['bones'],resources['calibration'](size=(image.shape[1],image.shape[0]),yaw=.45))
    if not pose['available']:raise ValueError('Observed pixels lack a verifiable 3D pose: '+pose['reason'])
    if pose['reprojection_rmse_px']>2.0:raise ValueError('Pose reprojection error too high')
    original=resources['golf'](Path(p))
    return {'arm_angle_rad':float(pose['angles']['arm_R']),'pose':pose,
            'golf':{k:original[k] for k in ('meanRGB','edgeFraction','orbKeypoints','lumaMean','sourceHash')},
            'image_sha256':digest,'pixel_size':[int(image.shape[1]),int(image.shape[0])]}

def calibrate(project,resources):
    from yard.core import YardProject
    from bridge import CONTROL_PATTERN
    items=[];seen=set()
    for ep in resources['episodes'](project,restrict='arm'):
        # Training labels are allowed only on verified previously recorded calibration episodes.
        label=ep['instruction'];matched=CONTROL_PATTERN.fullmatch(label)
        if not matched:continue
        angle=int(matched.group(1))
        if angle not in (10,40):continue
        last=ep['episode']['samples'][-1]
        digest=last['frame_png_sha256']
        if digest in seen:continue
        seen.add(digest)
        # Exact observed camera pose is pre-existing and verified against the original saved PNG.
        pose=last['camera'];value=pose['angles_rad']['arm_R']
        if not pose['available'] or not math.isfinite(value):raise ValueError('Calibration missing verified visual pose')
        items.append({'instruction_degrees':angle,'measured_angle_rad':float(value),'image_sha256':digest,
                      'source_episode_id':ep['episode_id']})
    items.sort(key=lambda k:k['instruction_degrees'])
    if [x['instruction_degrees'] for x in items]!=[10,40]:raise ValueError('Need two distinct, verified 10 and 40-degree calibration images')
    if not items[1]['measured_angle_rad']-items[0]['measured_angle_rad']>.2:raise ValueError('Calibration response lacks useful separation')
    return items

def decide(project,shipyard,png:Path,resources=None):
    if resources is None:resources=imports(project,shipyard)
    png=Path(png).resolve()
    if not png.is_relative_to(project.root.resolve()):raise ValueError('Target image must be a file within project cargo')
    target=measure_png(png,resources);cal=calibrate(project,resources)
    a,b=(x['measured_angle_rad'] for x in cal)
    angle=10.+30.*(target['arm_angle_rad']-a)/(b-a)
    if not 9.5<=angle<=40.5:raise LookupError('Observed target outside calibrated motor range')
    cmd=max(10,min(40,int(round(angle))))
    # Explicit aliasing controls: an image equal to a training image is NOT a heldout trial.
    unique=target['image_sha256'] not in {x['image_sha256'] for x in cal}
    return {'schema':'kokoro/image-derived-goal/1','image_sha256':target['image_sha256'],
            'camera':target,'calibration':cal,'inferred_command_degrees_unrounded':angle,
            'command_degrees':cmd,'instruction':f'raise right arm {cmd} degrees',
            'distinct_from_calibration_images':unique,'source':'actual saved VTK RGB pixels + original v2.3 inverse camera + original Golf pixel measurements',
            'limitations':'registered virtual markers / fixed documented camera; only bounded 10-40 degree training interval'}

def run_colony(project,shipyard,workers=0):
    colony=project.root/'exports'/'installed_information_colony'/'colony.py'
    command=[sys.executable,str(colony),'--project',str(project.root),'--shipyard',str(shipyard),'run','--workers',str(workers)]
    # Spawn-friendly stable module path: subprocess executes colony.py as __main__,
    # and worker functions are declared at top level of that script. No dynamic importlib specs.
    child=subprocess.run(command,cwd=colony.parent,text=True,capture_output=True,timeout=160)
    if child.returncode:raise RuntimeError('Colony failed (not a partial pass): '+child.stderr[-1800:])
    result=json.loads(child.stdout)
    if not result['output_parity_vs_serial']:raise AssertionError('Original colony / independent serial result mismatch')
    return result

def execute(project,shipyard,png:Path,workers=0,frames=5):
    from yard.assembled import record_and_recall
    resources=imports(project,shipyard)
    choice=decide(project,shipyard,png,resources)
    if not choice['distinct_from_calibration_images']:
        raise ValueError('Target is a known calibration frame; not an independent visual-goal test')
    before=resources['episodes'](project,restrict='arm')
    result=record_and_recall(project,choice['instruction'],frames)
    eid=result['memory']['episode_id']
    ep=next(x for x in resources['episodes'](project,restrict='arm') if x['episode_id']==eid)
    final=ep['episode']['samples'][-1]['camera']['angles_rad']['arm_R']
    error=float(abs(final-choice['camera']['arm_angle_rad']))
    anch=resources['anchor'](project,[eid])
    # FIX for prior v1.6 failure: stable named original worker module, never dynamic temp import.
    colony=run_colony(project,shipyard,workers)
    report={'schema':'kokoro/verified-visual-action/1','visual_decision':choice,
        'executed_command':choice['instruction'],'new_spatial_episode_id':eid,
        'target_measured_arm_rad':choice['camera']['arm_angle_rad'],
        'executed_measured_arm_rad':final,'visual_endpoint_error_rad':error,
        'memory':result['memory'],'anchor':anch,'colony':colony,
        'classification':'executed source-pinned virtual motor and rendered-image perception; no physical robot or learned policy'}
    out=project.root/'exports'/'installed_visual_action_v1_6'
    out.mkdir(parents=True,exist_ok=True)
    p=out/('action_'+eid+'.json');p.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    project.log('verified_visual_action',{'episode':eid,'command':choice['instruction'],'error_rad':error,'colony_jobs':colony['work_units']})
    return report

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--shipyard',required=True)
    sub=ap.add_subparsers(dest='command',required=True)
    for name in ('measure','act'):
        s=sub.add_parser(name);s.add_argument('image');s.add_argument('--workers',type=int,default=0)
    args=ap.parse_args();sys.path.insert(0,str(Path(args.shipyard).resolve()))
    from yard.core import YardProject
    project=YardProject(args.project)
    response=decide(project,Path(args.shipyard),Path(args.image)) if args.command=='measure' else execute(project,Path(args.shipyard),Path(args.image),args.workers)
    print(json.dumps(response,indent=2,allow_nan=False))
if __name__=='__main__':main()