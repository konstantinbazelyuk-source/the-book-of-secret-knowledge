"""Parametric eight-leg 3-DOF IK model for digital validation ONLY.
Dimensions and joint limits are *proposed* and not fitted to upstream Octobot STEP.
No physical servo output and no motor wiring.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import atan2,acos,cos,sin,hypot,pi,ceil
import math

@dataclass(frozen=True)
class LegGeometry:
    coxa_mm:float=32.0
    femur_mm:float=72.0
    tibia_mm:float=95.0
    limit_yaw_rad:float=0.55
    limit_shoulder_rad:float=pi/2
    limit_knee_rad:float=pi/2

class Unreachable(Exception):pass

def solve_leg(x,y,z,geom=LegGeometry()):
    """Local coords: x radial out, y tangent, z positive downward.
    Three joint DOFs yaw/shoulder/knee. Returned angles are mathematical,
    not servo zero-offset directions; must calibrate actual firmware separately.
    """
    if not all(math.isfinite(v) for v in [x,y,z]):raise ValueError('bad target')
    yaw=atan2(y,x)
    h=hypot(x,y)-geom.coxa_mm
    d=hypot(h,z)
    if d < abs(geom.femur_mm-geom.tibia_mm)+1e-8 or d>geom.femur_mm+geom.tibia_mm-1e-8:raise Unreachable('link lengths cannot reach target')
    shoulder=atan2(z,h)-acos((geom.femur_mm**2+d*d-geom.tibia_mm**2)/(2*geom.femur_mm*d))
    knee=pi-acos((geom.femur_mm**2+geom.tibia_mm**2-d*d)/(2*geom.femur_mm*geom.tibia_mm))
    if abs(yaw)>geom.limit_yaw_rad or abs(shoulder)>geom.limit_shoulder_rad or abs(knee)>geom.limit_knee_rad:raise Unreachable('joint limit')
    return (yaw,shoulder,knee)

def forward_leg(angles,geom=LegGeometry()):
    yaw,shoulder,knee=angles
    # theta2=shoulder and relative tibia angle is shoulder+knee
    h=geom.coxa_mm+geom.femur_mm*cos(shoulder)+geom.tibia_mm*cos(shoulder+knee)
    z=geom.femur_mm*sin(shoulder)+geom.tibia_mm*sin(shoulder+knee)
    return h*cos(yaw),h*sin(yaw),z

def wave_support(phase,duty=0.75):
    """4+ supporting feet in analytic scheduler for 8 phase-offset legs.
    Assumes perfect independent contacts, NOT gait/stability validation.
    """
    if not(0<duty<1 and math.isfinite(phase)):raise ValueError('bad gait duty')
    return [i for i in range(8) if ((phase+i/8)%1)<duty]
