"""Ground-only 24-axis SpiderScan DIGITAL motor plant and commanded gait.

All lengths below are illustrative parametric geometry, NOT measured Octobot geometry.
Physical contact force, slip, servo torque, power, and collision physics are not modeled.
Only angular rate-limited first-order servomotor tracking and kinematics are modeled.
"""
from dataclasses import dataclass
from math import pi, sin, cos, atan2, hypot, isfinite
from legacy.approved_kinematics_v06 import LegGeometry, solve_leg, forward_leg, Unreachable

N_LEGS=8
GEOM=LegGeometry()

@dataclass
class DigitalMotor:
    angle: float
    max_speed_rad_s: float=3.0  # ASSUMED configurable digital actuator speed
    time_constant_s: float=0.075 # ASSUMED first-order tracking time constant
    clip_hits: int=0
    def step(self, target:float, dt:float)->float:
        if not all(isfinite(v) for v in (target,dt,self.angle)) or dt <=0 or dt>0.1:
            raise ValueError('invalid motor state or dt')
        if self.max_speed_rad_s<=0 or self.time_constant_s<=0:raise ValueError('invalid motor model')
        delta=(target-self.angle)*(1-__import__('math').exp(-dt/self.time_constant_s))
        max_delta=self.max_speed_rad_s*dt
        if abs(delta)>max_delta:
            delta=max_delta if delta>0 else -max_delta
            self.clip_hits+=1
        self.angle+=delta
        return self.angle

class SpiderMotorTwin:
    def __init__(self, motor_tau_s=0.075, motor_max_speed=3.0, stride_mm=38.0, swing_height_mm=22.0, cycle_s=1.6, duty=0.70):
        self.stride_mm=stride_mm;self.swing_height_mm=swing_height_mm
        self.cycle_s=cycle_s;self.duty=duty
        self.body_speed_mm_s = stride_mm/(cycle_s*duty) # commanded ideal translation, NOT physically solved
        home=solve_leg(130,0,105,GEOM)
        self.motors=[[DigitalMotor(q,motor_max_speed,motor_tau_s) for q in home] for _ in range(N_LEGS)]
        self.t=0.0
        self._first=True
        self.command_success=0;self.command_total=0
        self.contact_proxy_good=0;self.contact_proxy_total=0
        self.rmse_accum=0.0;self.n_errors=0
        self.min_support=8;self.ik_failures=0
    def target(self,leg,t):
        if leg<0 or leg>=8:raise ValueError('leg')
        phase=((t/self.cycle_s)+(leg%2)*0.5)%1.0
        stance=phase<self.duty
        if stance:
            travel=self.stride_mm*(0.5-phase/self.duty)
            z=105.0
        else:
            s=(phase-self.duty)/(1-self.duty)
            smooth=s*s*(3-2*s)
            travel=self.stride_mm*(-0.5+smooth)
            z=105.0-self.swing_height_mm*sin(pi*s)
        a=2*pi*leg/8
        x=130.0+travel*cos(a)
        y=-travel*sin(a)
        return (x,y,z),stance
    def tick(self,dt=0.02):
        if not 0<dt<=0.1:raise ValueError('dt')
        t=self.t; frames=[]; supports=0; contact_proxies=0
        for leg in range(8):
            xyz,stance=self.target(leg,t)
            if stance:supports+=1
            try:
                target=solve_leg(*xyz,GEOM)
                self.command_success+=1
            except Unreachable:
                self.ik_failures+=1
                target=tuple(m.angle for m in self.motors[leg])
            self.command_total+=1
            sensed=tuple(self.motors[leg][j].step(target[j],dt) for j in range(3))
            foot_local=forward_leg(sensed,GEOM)
            foot_err=hypot(hypot(foot_local[0]-xyz[0],foot_local[1]-xyz[1]), foot_local[2]-xyz[2])
            self.rmse_accum+=foot_err**2;self.n_errors+=1
            # Kinematic contact proxy, NOT collision or a force sensor.
            if stance:
                self.contact_proxy_total+=1
                is_close=foot_err <= 7.0
                self.contact_proxy_good+=is_close
                contact_proxies+=int(is_close)
            a=2*pi*leg/8
            hub=(70*cos(a),70*sin(a),0)
            # coxa tip and knee computed analytically in *body XY* orientation
            yaw,shoulder,knee=sensed
            angle=a+yaw
            coxa=(hub[0]+GEOM.coxa_mm*cos(angle),hub[1]+GEOM.coxa_mm*sin(angle),0)
            femur=(coxa[0]+GEOM.femur_mm*cos(shoulder)*cos(angle),
                   coxa[1]+GEOM.femur_mm*cos(shoulder)*sin(angle), -GEOM.femur_mm*sin(shoulder))
            toe=(hub[0]+foot_local[0]*cos(a)-foot_local[1]*sin(a),
                 hub[1]+foot_local[0]*sin(a)+foot_local[1]*cos(a),-foot_local[2])
            frames.append({'id':leg,'hip':[round(v,3) for v in hub], 'coxa':[round(v,3) for v in coxa],
                           'knee':[round(v,3) for v in femur], 'toe':[round(v,3) for v in toe],
                           'joint_angles_rad':[round(v,6) for v in sensed],
                           'target_angles_rad':[round(v,6) for v in target],
                           'stance_command':stance,'foot_error_mm':round(foot_err,4),
                           'contact_proxy':bool(stance and foot_err<=7.0)})
        self.min_support=min(self.min_support,supports)
        self.t+=dt
        return {'t_s':round(self.t,4),'body':[round(self.body_speed_mm_s*self.t,3),0.0,105.0],
                'legs':frames,'commanded_supports':supports,'proxy_supports':contact_proxies}
    def metrics(self):
        return {'duration_s':round(self.t,3), 'motor_count':24,'leg_count':8,
                'commanded_speed_mm_s':round(self.body_speed_mm_s,3),
                'commanded_distance_mm':round(self.body_speed_mm_s*self.t,3),
                'ik_success_pct':100*self.command_success/max(1,self.command_total),
                'ik_failures':self.ik_failures,'minimum_commanded_support_legs':self.min_support,
                'rms_toe_error_mm':round((self.rmse_accum/max(1,self.n_errors))**0.5,4),
                'contact_proxy_pct':round(100*self.contact_proxy_good/max(1,self.contact_proxy_total),2),
                'contact_proxy_samples':self.contact_proxy_total,
                'rate_limit_hits':sum(m.clip_hits for group in self.motors for m in group),
                'evidence':'digital_first_order_motor_model_not_dynamics_or_hardware'}
