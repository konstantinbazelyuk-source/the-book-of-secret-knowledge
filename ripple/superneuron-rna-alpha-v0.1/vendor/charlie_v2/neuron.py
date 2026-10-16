"""Charlie Ripple Core v2 — NEW conductance-based adaptive spiking neuron.

Original Ripple source is kept independently, never imported into this model.
All values are dimensionless simulation states except model time in seconds.
The optical RGB inputs are normalized abstract signals; no instrument calibration is implied.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from math import exp, isfinite
from typing import Sequence


def clip(x: float, lo: float, hi: float) -> float:
    return min(hi, max(lo, x))


def sigmoid(z: float) -> float:
    if z >= 0:
        return 1. / (1. + exp(-min(z, 700.)))
    t = exp(max(z, -700.))
    return t / (1. + t)


@dataclass(frozen=True)
class CoreParameters:
    capacitance: float = 0.5            # model seconds * conductance
    leak: float = 1.0
    reversal_exc: float = 1.4
    reversal_inh: float = 0.0
    tau_exc: float = 0.070             # seconds; NEW synaptic memory
    tau_inh: float = 0.120             # seconds; NEW inhibitory persistence
    tau_adapt: float = 1.8             # seconds; NEW after-spike current
    adapt_jump: float = 0.095
    threshold_initial: float = 0.45
    threshold_low: float = 0.15
    threshold_high: float = 1.1
    tau_rate: float = 5.
    target_rate_hz: float = 1.
    threshold_eta: float = 0.018
    refractory_s: float = 0.10
    max_internal_step: float = 0.0025
    gradient_gain: float = 8.0
    recurrent_exc_pulse: float = 0.28  # dimensionless conductance increment per delivered event
    recurrent_inh_pulse: float = 0.28
    max_synaptic_conductance: float = 12.0
    weight_low: float = 0.12
    weight_high: float = 4.0

    def __post_init__(self):
        positive = ('capacitance', 'leak', 'tau_exc', 'tau_inh', 'tau_adapt',
                    'tau_rate', 'target_rate_hz', 'refractory_s',
                    'max_internal_step', 'gradient_gain', 'max_synaptic_conductance')
        for k in positive:
            if not isfinite(getattr(self, k)) or getattr(self, k) <= 0:
                raise ValueError(f'{k} must be positive and finite')
        if not (self.threshold_low <= self.threshold_initial <= self.threshold_high):
            raise ValueError('threshold bounds invalid')
        if not (0 < self.weight_low < self.weight_high):
            raise ValueError('weight bounds invalid')
        if not all(isfinite(getattr(self,k)) for k in ['reversal_exc','reversal_inh','adapt_jump','threshold_eta']):
            raise ValueError('nonfinite core parameter')


def valid_rgb(rgb: Sequence[float]) -> tuple[float, float, float]:
    if len(rgb) != 3 or any(not isfinite(float(x)) or not 0 <= x <= 1 for x in rgb):
        raise ValueError('RGB must contain exactly three finite [0,1] channels')
    return tuple(float(x) for x in rgb)


@dataclass
class CharlieNeuron:
    """Core equations:
      tau_e de/dt = w_R R+w_G G - e
      tau_i di/dt = w_B B - i
      tau_a da/dt = -a ; a <- a+delta_a on each spike
      C du/dt = -gL*u + e*(Ee-u)+i*(Ei-u)-a
      u >= theta => spike, u=0 and refractory.
      dr/dt = -r/tau_rate + sum(delta_event)/tau_rate
      dtheta/dt = eta*(r-r_target) with finite bounds.

    Firing times are bracketed/interpolated inside bounded microsteps;
    do NOT claim analytic exact crossings of this coupled system.
    """
    params: CoreParameters = field(default_factory=CoreParameters)
    weights: list[float] = field(default_factory=lambda:[2.0,1.2,1.4])
    membrane: float = 0.
    exc: float = 0.
    inh: float = 0.
    adapt: float = 0.
    theta: float = 0.45
    rate: float = 0.
    refractory: float = 0.
    time: float = 0.
    count: int = 0

    def __post_init__(self):
        if len(self.weights) != 3 or not all(isfinite(w) and self.params.weight_low<=w<=self.params.weight_high for w in self.weights):
            raise ValueError('three bounded finite positive synaptic weights required')

    def reset_state(self):
        self.membrane=self.exc=self.inh=self.adapt=self.rate=self.refractory=self.time=0.
        self.theta=self.params.threshold_initial; self.count=0

    def step(self, rgb: Sequence[float], dt: float, *, homeostasis: bool = True,
             exc_pulses: int = 0, inh_pulses: int = 0) -> dict:
        R,G,B=valid_rgb(rgb)
        if not isinstance(exc_pulses,int) or not isinstance(inh_pulses,int) or not (0<=exc_pulses<=8 and 0<=inh_pulses<=8):
            raise ValueError("recurrent pulses must be finite integers 0..8")
        if not isfinite(dt) or not 0<dt<=0.5:
            raise ValueError('dt must be finite in (0,0.5]')
        import math
        # Internal spike-delivery pathway: pulses directly change the conductance state.
        # The source neurons delivered these pulses in a prior time step (causal delay).
        self.exc=clip(self.exc+exc_pulses*self.params.recurrent_exc_pulse,0.,self.params.max_synaptic_conductance)
        self.inh=clip(self.inh+inh_pulses*self.params.recurrent_inh_pulse,0.,self.params.max_synaptic_conductance)
        n=math.ceil(dt/self.params.max_internal_step); h=dt/n
        timestamps=[]; p=self.params
        target_e=self.weights[0]*R+self.weights[1]*G
        target_i=self.weights[2]*B
        for _ in range(n):
            begin=self.time
            self.exc=target_e+(self.exc-target_e)*exp(-h/p.tau_exc)
            self.inh=target_i+(self.inh-target_i)*exp(-h/p.tau_inh)
            self.adapt *= exp(-h/p.tau_adapt)
            self.rate *= exp(-h/p.tau_rate)
            resting=min(h,self.refractory)
            self.refractory=max(0.,self.refractory-resting)
            if resting>0: self.membrane=0.
            available=h-resting
            if available>1e-14:
                total=p.leak+self.exc+self.inh
                eq=(p.reversal_exc*self.exc+p.reversal_inh*self.inh-self.adapt)/total
                u0=self.membrane
                u1=eq+(u0-eq)*exp(-available*total/p.capacitance)
                if u1>=self.theta:
                    # crossing under frozen within-substep conductance approx.
                    fraction=clip((self.theta-u0)/(u1-u0),0.,1.) if u1!=u0 else 0.
                    timestamps.append(begin+resting+fraction*available)
                    self.count+=1
                    self.rate+=1./p.tau_rate
                    self.adapt+=p.adapt_jump
                    self.membrane=0.
                    self.refractory=p.refractory_s
                else: self.membrane=max(0.,u1)
            if homeostasis:
                self.theta=clip(self.theta+p.threshold_eta*h*(self.rate-p.target_rate_hz),p.threshold_low,p.threshold_high)
            self.time=begin+h
        return {'t':self.time,'membrane':self.membrane,'exc':self.exc,'inh':self.inh,
                'adapt':self.adapt,'theta':self.theta,'rate_hz':self.rate,
                'events':timestamps,'count':len(timestamps),'total_events':self.count,
                'weights':list(self.weights)}

    def equilibrium(self,rgb:Sequence[float]):
        R,G,B=valid_rgb(rgb);p=self.params
        e=self.weights[0]*R+self.weights[1]*G;i=self.weights[2]*B
        d=p.leak+e+i
        u=(e*p.reversal_exc+i*p.reversal_inh)/d
        return u,e,i,d

    def probability(self,rgb:Sequence[float]):
        u,*_=self.equilibrium(rgb)
        return sigmoid(self.params.gradient_gain*(u-self.params.threshold_initial))

    def loss_grad(self,rgb:Sequence[float],label:int) -> tuple[float,list[float]]:
        """EXACT analytic gradient of *stationary* logistic cross-entropy.
        It is not a derivative through spike/reset dynamics.
        """
        if label not in (0,1): raise ValueError('label must be 0 or 1')
        R,G,B=valid_rgb(rgb);p=self.params
        u,e,i,d=self.equilibrium((R,G,B))
        prob=sigmoid(p.gradient_gain*(u-p.threshold_initial))
        import math
        loss=-label*math.log(max(prob,1e-12))-(1-label)*math.log(max(1-prob,1e-12))
        coef=(prob-label)*p.gradient_gain/d
        grad=[coef*(p.reversal_exc-u)*R,coef*(p.reversal_exc-u)*G,
              coef*(p.reversal_inh-u)*B]
        return loss,grad

    def train(self, samples:list[tuple[Sequence[float],int]], *, epochs:int=20,
              learning_rate:float=0.025, regularization:float=0.) -> list[float]:
        if not 0<epochs<=200 or not 0<learning_rate<=1 or not 0<=regularization<=1:
            raise ValueError('training hyperparameters out of bounds')
        if not samples: raise ValueError('empty training data')
        # All examples must be validated BEFORE mutating any weight.
        validated=[(valid_rgb(x),y) for x,y in samples]
        if any(y not in (0,1) for _,y in validated):raise ValueError('invalid label')
        history=[]
        for epoch in range(epochs):
            for x,y in validated:
                loss,grad=self.loss_grad(x,y)
                self.weights=[clip(w-learning_rate*(g+regularization*(w-d)),self.params.weight_low,self.params.weight_high)
                              for w,g,d in zip(self.weights,grad,(2.0,1.2,1.4))]
            history.append(sum(self.loss_grad(x,y)[0] for x,y in validated)/len(validated))
        return history