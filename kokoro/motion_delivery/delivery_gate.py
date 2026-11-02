"""Validate this rig-preview receipt, not arbitrary capability claims."""
import math
import re
EXPECTED_SOURCE = 'be9cb6b2575334ff912f45a9ff226a552f7216d2b1d7707ba830f8867690ce93'
ACTION = 'KOKORO — blink, jaw and head check'

def issues(receipt: dict) -> list[str]:
    problems = []
    for key in ('source_sha256_before','source_sha256_after'):
        if receipt.get(key) != EXPECTED_SOURCE:
            problems.append('wrong or modified native source: '+key)
    if receipt.get('action') != ACTION:
        problems.append('wrong saved action')
    if receipt.get('fps') != 12 or receipt.get('duration_seconds') != 5:
        problems.append('wrong timing')
    frames = receipt.get('frames')
    if not isinstance(frames,list) or len(frames)!=60 or any(not isinstance(f,dict) for f in frames):
        return problems + ['exactly 60 frame records required']
    if [f.get('frame') for f in frames] != list(range(1,61)):
        problems.append('frame sequence incomplete or out of order')
    hashes = [f.get('png_sha256') for f in frames]
    if not all(isinstance(h,str) and re.fullmatch(r'[0-9a-f]{64}',h) for h in hashes):
        problems.append('invalid PNG hashes')
    elif len(set(hashes)) < 20:
        problems.append('insufficient distinct rendered frames')
    for key in ('head_z','jaw_x','left_eyelid_y','right_eyelid_y'):
        values=[f.get(key) for f in frames]
        if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in values):
            problems.append('missing or nonfinite control: '+key)
        elif max(values)-min(values) <= .01:
            problems.append('static control: '+key)
    return problems
