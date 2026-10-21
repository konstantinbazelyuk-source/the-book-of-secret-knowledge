"""Optional Reachy Mini SDK head-pose backend for the verified Kokoro event trace.

Not FR-NIA. The SDK supports head poses via create_head_pose and set_target;
this interface is NOT a validated hardware installation. No movement occurs
without both a local environment opt-in and --execute.
"""
from __future__ import annotations
import argparse,csv,json,math,os,time
from pathlib import Path


def send_trajectory(path:Path,*,execute=False,device='localhost_only',max_yaw=15.):
    if not (0<max_yaw<=15):raise ValueError('Conservative yaw ceiling is 15 degrees')
    with open(path,newline='') as f:rows=list(csv.DictReader(f))
    if not rows:raise ValueError('Empty event trajectory')
    prev=-1.
    for row in rows:
        t=float(row['model_time_s']);a=float(row['simulated_yaw_deg'])
        if not(math.isfinite(t) and math.isfinite(a)) or t<=prev or abs(a)>max_yaw:
            raise ValueError('Trace violates safe temporal/range bound; abort whole run')
        prev=t
    result={'samples':len(rows),'mode':'dry-run' if not execute else 'hardware-attempt',
            'target':'Reachy Mini SDK head-yaw only; nine FR-NIA semantic axes not mapped'}
    if not execute:return result
    if os.environ.get('KOKORO_ENABLE_REACHY_HARDWARE')!='YES':
        raise PermissionError('Set KOKORO_ENABLE_REACHY_HARDWARE=YES explicitly')
    if device!='localhost_only':raise ValueError('Only local SDK daemon permitted in this experimental adapter')
    from reachy_mini import ReachyMini
    from reachy_mini.utils import create_head_pose
    with ReachyMini(connection_mode=device,media_backend='no_media') as mini:
        last=0.
        try:
            for r in rows:
                t=float(r['model_time_s']);yaw=float(r['simulated_yaw_deg'])
                time.sleep(max(0.,t-last));last=t
                mini.set_target(head=create_head_pose(roll=0.,pitch=0.,yaw=yaw,degrees=True,mm=True))
        finally:
            # Do not rely on network to stop; explicit zero command is best effort.
            mini.set_target(head=create_head_pose(roll=0.,pitch=0.,yaw=0.,degrees=True,mm=True))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('trajectory');p.add_argument('--execute',action='store_true')
    a=p.parse_args();print(json.dumps(send_trajectory(Path(a.trajectory),execute=a.execute),indent=2))