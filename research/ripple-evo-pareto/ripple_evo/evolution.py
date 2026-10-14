"""Ripple SpiderScan Alpha v1.2 evolutionary motor-policy adapter.

Preserves v1.1 digital motor plant, v0.6 kinematics, and original neuron core.
No claims of physical motors or spatial intelligence. Synthetic motor experiments ONLY.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict, replace
from math import isfinite, sqrt
import math
import random
import hashlib
import json
import statistics
from legacy.digital_motor_v11_LOCKED import SpiderMotorTwin
from legacy.ripple_optical_agent_LOCKED import RippleNeuron

BASELINE = {'stride_mm':38.0,'swing_height_mm':22.0,'cycle_s':1.6,'duty':0.70,'gain':0.0}
BOUNDS = {'stride_mm':(26.0,48.0),'swing_height_mm':(12.0,32.0),'cycle_s':(1.15,2.25),'duty':(.60,.82),'gain':(0.0,.55)}
DT = .04
DURATION = 6.4

@dataclass(frozen=True)
class Genome:
    stride_mm:float = 38.0
    swing_height_mm:float=22.0
    cycle_s:float=1.6
    duty:float=.70
    gain:float=0.0
    def check(self):
        for k,(lo,hi) in BOUNDS.items():
            if not isfinite(getattr(self,k)) or not lo<=getattr(self,k)<=hi:raise ValueError(k)
        return self
    def id(self):return hashlib.sha256(json.dumps(asdict(self),sort_keys=True).encode()).hexdigest()[:16]

class EvolvingColonyTwin(SpiderMotorTwin):
    """8 independent approved Ripple neurons observe per-leg actuator tracking.
    Only an external, bounded stride-scaling adapter is evolvable.
    The RGB slots encode DERIVED errors/limits and not physical wavelengths.
    """
    def __init__(self,genome:Genome,motor_tau_s:float,motor_max_speed:float):
        genome.check()
        super().__init__(motor_tau_s=motor_tau_s,motor_max_speed=motor_max_speed,
            stride_mm=genome.stride_mm,swing_height_mm=genome.swing_height_mm,
            cycle_s=genome.cycle_s,duty=genome.duty)
        self.genome=genome
        self.nodes=[RippleNeuron() for _ in range(8)]
        self.risk=[0.0]*8
        self.neuron_spikes=0
        self.distance_command_proxy_mm=0.0
        self.support_loss_frames=0
        self.risk_trace=[]
        self._last_clips=[[0]*3 for _ in range(8)]
    def tick(self,dt=DT):
        # A single bounded global stride signal from eight independently maintained node states.
        risk=max(self.risk)
        self.stride_mm=self.genome.stride_mm*(1.0-self.genome.gain*risk)
        self.body_speed_mm_s=self.stride_mm/(self.cycle_s*self.duty)
        frame=super().tick(dt)
        self.distance_command_proxy_mm+=self.body_speed_mm_s*dt
        if frame['proxy_supports']<4:self.support_loss_frames+=1
        for i,leg in enumerate(frame['legs']):
            # RED = tracking mismatch; GREEN = rate clipping; BLUE = target compliance.
            # These are categorical channels; NOT optical field measurements.
            error=leg['foot_error_mm']
            clips=sum(m.clip_hits for m in self.motors[i])
            delta=clips-sum(self._last_clips[i]);self._last_clips[i]=[m.clip_hits for m in self.motors[i]]
            rgb=(min(1.0,error/15.0),min(1.0,delta/3),1.0 if error <3 else 0.0)
            step=self.nodes[i].step(rgb,dt)
            self.neuron_spikes+=step['count']
            self.risk[i]=min(1.0,self.risk[i]*math.exp(-dt/.30)+.70*step['count'])
        self.risk_trace.append(round(max(self.risk),4))
        return frame
    def metrics(self):
        out=super().metrics()
        out.update(neuron_spikes=self.neuron_spikes,
            command_distance_proxy_mm=round(self.distance_command_proxy_mm,3),
            feedback_max_risk=round(max(self.risk_trace or [0]),3),
            support_proxy_loss_frames=self.support_loss_frames,
            evidence='software_only_first_order_servo_kinematics_with_ripple_neuron_adapter')
        return out

def scenario(seed:int,split='train'):
    r=random.Random(('train-' if split=='train' else 'holdout-')+str(seed))
    return {'seed':seed,'split':split,'tau_s':round(r.uniform(.047,.16),6),
       'max_speed_rad_s':round(r.uniform(1.6,3.8),6)}

def simulate(genome:Genome,setting:dict,duration_s=DURATION,dt=DT):
    n=round(duration_s/dt)
    twin=EvolvingColonyTwin(genome,setting['tau_s'],setting['max_speed_rad_s'])
    for _ in range(n):twin.tick(dt)
    return twin.metrics()

def loss(metric:dict):
    """Pre-registered task loss; no learned intelligence score.
    Penalize stationary trick relative to v1.1 target speed ~33.93 mm/s.
    All quantities are software proxies; not displacement or ground contacts.
    """
    target_speed=38.0/(1.6*.7)
    proxy_speed=metric['command_distance_proxy_mm']/metric['duration_s']
    slow_penalty=2.0*max(0.0,target_speed-proxy_speed)
    # Sufficient commanded support is NOT proof of real stability.
    return (metric['rms_toe_error_mm']+slow_penalty+
       .025*metric['rate_limit_hits']+
       .2*metric['support_proxy_loss_frames']+
       8.0*metric['ik_failures'])

def evaluate(genome:Genome,scenarios:list[dict]):
    trials=[simulate(genome,s) for s in scenarios]
    losses=[loss(x) for x in trials]
    # Mean and 90th-percentile tail for protection against worst simulated regimes.
    high=sorted(losses)[max(0,math.ceil(.90*len(losses))-1)]
    return {'objective':round(.75*statistics.mean(losses)+.25*high,6),
        'mean_loss':round(statistics.mean(losses),6),'p90_loss':round(high,6),
        'avg_toe_rmse_mm':round(statistics.mean(x['rms_toe_error_mm'] for x in trials),6),
        'mean_proxy_speed_mm_s':round(statistics.mean(x['command_distance_proxy_mm']/x['duration_s'] for x in trials),6),
        'total_spikes':sum(x['neuron_spikes'] for x in trials),
        'scenario_count':len(trials)}

def mutate(genome:Genome,rng:random.Random,rate=.20):
    v=asdict(genome)
    for k,(lo,hi) in BOUNDS.items():
        if rng.random()<.73:
            v[k]=round(max(lo,min(hi,v[k]+rng.gauss(0.0,rate*(hi-lo)))),5)
    return Genome(**v).check()

def evolve(seed=20261013,population=12,generations=5,train_n=4,holdout_n=8):
    rng=random.Random(seed)
    base=Genome()
    train=[scenario(i,'train') for i in range(train_n)]
    holdout=[scenario(1000+i,'holdout') for i in range(holdout_n)]
    members=[base]+[mutate(base,rng,rate=.32) for _ in range(population-1)]
    history=[]
    cache={}
    for generation in range(generations):
        results=[]
        for g in members:
            k=g.id()
            if k not in cache:cache[k]=evaluate(g,train)
            results.append((cache[k]['objective'],g))
        results.sort(key=lambda x:(x[0],x[1].id()))
        best=results[0]
        history.append({'generation':generation,'best_loss':round(best[0],5),
                        'best_genome':asdict(best[1]),'evaluated_distinct':len(cache)})
        elite=[g for _,g in results[:max(2,population//4)]]
        members=[base,elite[0]]
        while len(members)<population:
            members.append(mutate(rng.choice(elite),rng,rate=max(.04,.22*(.75**generation))))
    # Return best from all generations (not merely the final mutation cohort).
    best_g=Genome(**min(history,key=lambda x:x['best_loss'])['best_genome'])
    base_train=evaluate(base,train);best_train=evaluate(best_g,train)
    base_hold=evaluate(base,holdout);best_hold=evaluate(best_g,holdout)
    promotion=bool(best_hold['objective']<base_hold['objective'] and best_hold['avg_toe_rmse_mm']<=base_hold['avg_toe_rmse_mm']
                  and best_hold['mean_proxy_speed_mm_s']>=.85*base_hold['mean_proxy_speed_mm_s'])
    return {'schema':'ripple-evolution-alpha/1','locked_core':True,'training_seed':seed,
      'search':{'population':population,'generations':generations,'candidate_evaluations':len(cache),'train_scenarios':train,'holdout_scenarios':holdout},
      'baseline':asdict(base),'best_candidate':asdict(best_g),'history':history,
      'training_comparison':{'baseline':base_train,'candidate':best_train},
      'holdout_comparison':{'baseline':base_hold,'candidate':best_hold},
      'promotion_gate_passed':promotion,
      'evidence':'executed_software_simulation_only_not_physics_not_sensor_not_cloud_without_external_ci_logs'}

if __name__=='__main__':
    import argparse,pathlib
    p=argparse.ArgumentParser();p.add_argument('--out',default='results/evolution.json');p.add_argument('--seed',type=int,default=20261013)
    p.add_argument('--population',type=int,default=12);p.add_argument('--generations',type=int,default=5)
    a=p.parse_args();r=evolve(seed=a.seed,population=a.population,generations=a.generations)
    target=pathlib.Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'out':str(target),'promoted':r['promotion_gate_passed'],'holdout':r['holdout_comparison'],'best':r['best_candidate']},indent=2))