"""Kokoro -> bounded expressive robot virtual-actuation layer.

Original source is immutable. This independent controller validates v1.3
Shipyard timeline records + corresponding PNGs before numerical replay.
FR-NIA mapping is semantic/virtual, not a hardware driver.
Python >=3.11, stdlib only.
"""
from __future__ import annotations
import argparse
import csv
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import zipfile

AXES = (
    'neck_yaw','neck_pitch','neck_roll',
    'eyes_horizontal','eyes_vertical','blink_left','blink_right',
    'mouth_open','mouth_smile','brow',
)
# *Proposed virtual limits*, never represented as actual FR-NIA specifications.
LIMITS = {k: (-45., 45.) for k in AXES}
LIMITS.update({'neck_pitch':(-25.,25.),'neck_roll':(-20.,20.),
               'eyes_horizontal':(-30.,30.),'eyes_vertical':(-20.,20.),
               'blink_left':(0.,1.),'blink_right':(0.,1.),
               'mouth_open':(0.,1.),'mouth_smile':(-1.,1.),'brow':(-1.,1.)})
SCHEMA = 'kokoro/embodiment/replay/1'


def digest(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def finite(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)


def validate_target(target:dict)->dict:
    if not isinstance(target,dict) or not target:raise ValueError('Target requires known axes')
    out={}
    for axis,value in target.items():
        if axis not in LIMITS:raise ValueError('Unsupported axis '+str(axis))
        if not finite(value):raise ValueError('Non-finite axis value')
        lo,hi=LIMITS[axis]
        if not lo<=value<=hi:raise ValueError(f'{axis}: {value} outside proposed simulation limit')
        out[axis]=float(value)
    return out


@dataclass
class Axis:
    pos:float=0.
    velocity:float=0.


class KinematicPlant:
    """Virtual bounded velocity/acceleration actuator; not a servo calibration."""
    def __init__(self,dt=.02,max_speed=60.,max_acceleration=250.):
        if not all(map(finite,(dt,max_speed,max_acceleration))) or not(0<dt<=.1 and max_speed>0 and max_acceleration>0):
            raise ValueError('Bad step/velocity/acceleration')
        self.dt=dt;self.speed=max_speed;self.acc=max_acceleration
        self.axes={a:Axis() for a in AXES};self.target={a:0. for a in AXES}
        self.stopped=False
        self.model_time_s=0.
    def command(self,update:dict):
        if self.stopped:raise RuntimeError('Emergency-stopped')
        self.target.update(validate_target(update))
    def estop(self):
        self.stopped=True
        for a in self.axes.values():a.velocity=0.
    def step(self):
        if self.stopped:raise RuntimeError('Emergency-stopped')
        for key,axis in self.axes.items():
            delta=self.target[key]-axis.pos
            # Conservative speed target. Enforce both speed and acceleration limits.
            brake=min(self.speed,math.sqrt(2*self.acc*abs(delta)))
            vgoal=math.copysign(brake,delta) if abs(delta)>1e-12 else 0.
            dv=max(-self.acc*self.dt,min(self.acc*self.dt,vgoal-axis.velocity))
            new_v=max(-self.speed,min(self.speed,axis.velocity+dv))
            advance=new_v*self.dt
            if abs(advance)>=abs(delta) and advance*delta>=0:
                axis.pos=self.target[key];axis.velocity=0.
            else:
                axis.pos+=advance;axis.velocity=new_v
            lo,hi=LIMITS[key]
            if not lo-1e-9<=axis.pos<=hi+1e-9:raise AssertionError('Simulation limit crossed')
        self.model_time_s+=self.dt
        return {k:v.pos for k,v in self.axes.items()}


class SQLiteJournal:
    """Append-only local software replay log with a verifiable digest chain."""
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(self.path)
        self.db.execute('CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, previous_hash TEXT NOT NULL, hash TEXT NOT NULL, event_json TEXT NOT NULL)')
        self.db.commit()
    def __enter__(self):return self
    def __exit__(self,*args):self.db.close()
    def append(self,event:dict):
        payload=json.dumps(event,sort_keys=True,separators=(',',':'),allow_nan=False)
        last=self.db.execute('SELECT seq,hash FROM events ORDER BY seq DESC LIMIT 1').fetchone()
        seq=1 if not last else last[0]+1
        prev='0'*64 if not last else last[1]
        sig=digest((prev+'|'+str(seq)+'|'+payload).encode())
        self.db.execute('INSERT INTO events VALUES (?,?,?,?)',(seq,prev,sig,payload))
        self.db.commit()
        return sig
    def verify(self):
        prev='0'*64;count=0
        for seq,ph,sign,data in self.db.execute('SELECT seq,previous_hash,hash,event_json FROM events ORDER BY seq'):
            count+=1
            if seq!=count or ph!=prev or sign!=digest((prev+'|'+str(seq)+'|'+data).encode()):return False
            try:json.loads(data)
            except json.JSONDecodeError:return False
            prev=sign
        return True


def load_v13_cargo(cargo:str,session:str|None=None)->tuple[list[dict],dict]:
    """Read original cargo as data. Verify each PNG byte SHA, time & continuity."""
    with zipfile.ZipFile(cargo) as z:
        runs=sorted(n for n in z.namelist() if n.startswith('runs/') and n.endswith('/timeline.json'))
        if not runs:raise ValueError('Cargo does not contain a recorded timeline')
        if session:
            runs=[p for p in runs if p.split('/')[1]==session]
            if len(runs)!=1:raise ValueError('Unknown/ambiguous session')
        path=runs[0];folder=path.rsplit('/',1)[0]+'/'
        raw=z.read(path);series=json.loads(raw)
        if not isinstance(series,list) or not series:raise ValueError('Empty timeline')
        prev=-math.inf; continuity=None;count=0
        for row in series:
            t=row.get('sim_time_s')
            if not finite(t) or t<=prev:raise ValueError('Nonmonotonic virtual time')
            prev=t
            continuity=continuity or row.get('continuity_capsule_hash')
            if not continuity or row.get('continuity_capsule_hash')!=continuity:
                raise ValueError('Continuity mixed/absent')
            name=folder+f"frame_{row['frame']-1:03d}.png"
            try:b=z.read(name)
            except KeyError:raise ValueError('Missing recorded PNG: '+name)
            if not b.startswith(b'\x89PNG\r\n\x1a\n') or digest(b)!=row.get('image_sha256'):
                raise ValueError('Rendered source PNG hash mismatch')
            actual=row.get('virtual_actual_angles_rad',{})
            if not finite(actual.get('head')):raise ValueError('Missing virtual head angle')
            if not isinstance(row.get('wrist_world_xyz_m'),list) or len(row['wrist_world_xyz_m'])!=3 or not all(map(finite,row['wrist_world_xyz_m'])):
                raise ValueError('Bad virtual spatial coordinates')
            count+=1
        return series,{'cargo_sha256':file_digest(cargo),'session':folder.split('/')[1],
                       'timeline_sha256':digest(raw),'continuity_hash':continuity,
                       'validated_rendered_pngs':count,
                       'source_label':'Shipyard v1.3 recorded VTK virtual scene'}


def file_digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for part in iter(lambda:f.read(1<<20),b''):h.update(part)
    return h.hexdigest()


def replay(series:list[dict],source:dict, output_dir:Path, dt=.02, max_speed=60., max_acceleration=250.):
    """Replay one real saved *virtual* head trajectory through a NEW bounded virtual plant.

    This is driven by archived v1.3 numerical outputs; it does NOT reexecute the
    old VTK renderer. Mapping is only one verified axis: virtual head->neck_yaw.
    All other 9 logical axes remain neutral, not inferred facial expressions.
    """
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    plant=KinematicPlant(dt,max_speed,max_acceleration)
    journal=output_dir/'events.sqlite'
    points=[];source_idx=0
    virtual_source=[]
    for r in series:
        a=r['virtual_actual_angles_rad']['head']; virtual_source.append((float(r['sim_time_s']), math.degrees(a)))
    final_time=virtual_source[-1][0]
    steps=math.ceil(final_time/dt-1e-10)
    with SQLiteJournal(journal) as log:
        if log.db.execute('SELECT COUNT(*) FROM events').fetchone()[0]:raise ValueError('Refuse to overwrite preexisting journal')
        for tick in range(steps):
            target_t=min((tick+1)*dt, final_time)
            while source_idx < len(virtual_source)-1 and target_t>virtual_source[source_idx][0]:source_idx+=1
            before_t,before_v=(0.,0.) if source_idx==0 else virtual_source[source_idx-1]
            after_t,after_v=virtual_source[source_idx]
            f=max(0.,min(1.,(target_t-before_t)/(after_t-before_t)))
            desired=before_v+f*(after_v-before_v)
            # This is a virtual mapping. Input must pass explicitly proposed safety limits.
            plant.command({'neck_yaw':desired})
            result=plant.step()
            row={'schema':SCHEMA,'tick':tick+1,'model_time_s':round(plant.model_time_s,9),
                 'source_sim_time_s':round(target_t,9),'source_neck_yaw_deg':desired,
                 'commanded_virtual':dict(plant.target),'simulated_position':result,
                 'classification':'simulated virtual actuator following verified archived 3D virtual motion',
                 'provenance':source['timeline_sha256']}
            log.append(row);points.append(row)
        if not log.verify():raise AssertionError('Journal checksum chain did not verify')
    final_error=abs(points[-1]['simulated_position']['neck_yaw']-points[-1]['source_neck_yaw_deg'])
    out={'schema':SCHEMA,'steps':steps,'virtual_duration_s':final_time,'dt_s':dt,
         'input_frames':len(series),'source':source,'final_tracking_error_deg':final_error,
         'last_source_yaw_deg':points[-1]['source_neck_yaw_deg'],
         'last_simulated_yaw_deg':points[-1]['simulated_position']['neck_yaw'],
         'output_event_chain_verified':True,'classification':'calculated simulation from original Kokoro archived virtual frames; no physical robot'}
    (output_dir/'report.json').write_text(json.dumps(out,indent=2,sort_keys=True),'utf8')
    with open(output_dir/'trajectory.csv','w',newline='') as f:
        w=csv.writer(f);w.writerow(['model_time_s','source_yaw_deg','simulated_yaw_deg','simulated_velocity_deg_s'])
        for i,p in enumerate(points):
            v=(p['simulated_position']['neck_yaw']-(points[i-1]['simulated_position']['neck_yaw'] if i else 0))/dt
            w.writerow([p['model_time_s'],p['source_neck_yaw_deg'],p['simulated_position']['neck_yaw'],v])
    return out



def simulate_expressions(keyframes_path:Path, output_dir:Path, dt=.02):
    """Executable 10-axis expressive control from an explicit authored schedule.

    These axes are conceptual normalized channels; they do not assert an FR-NIA
    register protocol or the manufacturer's joint mapping. No AI inference.
    """
    spec=json.loads(Path(keyframes_path).read_text('utf8'))
    frames=spec.get('keyframes',[])
    duration=spec.get('duration_s')
    if not finite(duration) or not(.04<=duration<=60):raise ValueError('Bad expression duration')
    if not isinstance(frames,list) or not frames or len(frames)>300:raise ValueError('Invalid keyframe list')
    last=-1.;validated=[]
    for frame in frames:
        t=frame.get('time_s')
        if not finite(t) or not 0<=t<=duration or t<=last:raise ValueError('Non-monotonic keyframe times')
        last=t;validated.append((float(t),validate_target(frame.get('target'))))
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    source_hash=file_digest(keyframes_path)
    plant=KinematicPlant(dt);cursor=0
    steps=math.ceil(duration/dt-1e-10)
    records=[]
    with SQLiteJournal(output_dir/'events.sqlite') as log:
        if log.db.execute('SELECT COUNT(*) FROM events').fetchone()[0]:raise ValueError('Refuse overwrite')
        for tick in range(steps):
            t=(tick+1)*dt
            while cursor<len(validated) and validated[cursor][0]<=t+1e-12:
                plant.command(validated[cursor][1]);cursor+=1
            pos=plant.step()
            row={'schema':'kokoro/embodiment/expression/1','model_time_s':round(plant.model_time_s,9),
                 'simulated_position':pos,'commanded_virtual':dict(plant.target),'provenance':source_hash,
                 'classification':'simulated user-authored 10-channel face and neck keyframes'}
            log.append(row);records.append(row)
        if not log.verify():raise AssertionError('Journal verification failed')
    with open(output_dir/'expression_trajectory.csv','w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['model_time_s',*AXES])
        for r in records:writer.writerow([r['model_time_s'],*[r['simulated_position'][a] for a in AXES]])
    result={'schema':'kokoro/embodiment/expression/1','steps':steps,'dt_s':dt,'source_sha256':source_hash,
            'end_state':records[-1]['simulated_position'], 'journal_verified':True,
            'classification':'calculated proposed virtual expressions; no FR-NIA protocol or hardware'}
    (output_dir/'report.json').write_text(json.dumps(result,indent=2),'utf8')
    return result


def cli():
    p=argparse.ArgumentParser(description='Kokoro verified virtual robot-motion bridge')
    sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('replay');s.add_argument('--cargo',required=True);s.add_argument('--session');s.add_argument('--out',required=True)
    s.add_argument('--dt',type=float,default=.02);s.add_argument('--speed',type=float,default=60.);s.add_argument('--acceleration',type=float,default=250.)
    e=sub.add_parser('express');e.add_argument('--keyframes',required=True);e.add_argument('--out',required=True)
    v=sub.add_parser('verify');v.add_argument('--sqlite',required=True)
    x=p.parse_args()
    if x.command=='verify':
        with SQLiteJournal(x.sqlite) as log:print(json.dumps({'verified':log.verify()}))
    elif x.command=='express':print(json.dumps(simulate_expressions(Path(x.keyframes),Path(x.out)),indent=2))
    else:
        series,src=load_v13_cargo(x.cargo,x.session)
        print(json.dumps(replay(series,src,Path(x.out),x.dt,x.speed,x.acceleration),indent=2))
if __name__=='__main__':cli()