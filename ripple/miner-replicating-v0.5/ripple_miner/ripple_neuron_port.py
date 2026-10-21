"""Numerical Python port of preserved Ripple Neuron v0.1's exact LIF step.

This file does not replace or modify the authoritative
legacy/v01_ripple_core_LOCKED.cjs. Side-by-side Node regression tests verify
observable (t,u,theta,rate,count,event times) agreement.
"""
import math


def bound(v,lo,hi):return max(lo,min(hi,v))

class RippleNeuron:
    def __init__(self,theta=.45,adaptive=True,target=1):
        self.theta=theta;self.adaptive=adaptive;self.target=target
        self.tauV=.5;self.tauR=5;self.refractory=.1;self.eta=.08
        self.lo=.15;self.hi=2.5;self.t=0.;self.u=0.;self.rate=0.;self.rest=0.
    def step(self,x,dt):
        if len(x)!=3 or any(not math.isfinite(v) for v in x) or not math.isfinite(dt) or not 0<dt<=.5:
            raise ValueError('Invalid input or elapsed time')
        x=[bound(v,0,1) for v in x]
        drive=2*x[0]+1.2*x[1]-1.4*x[2]
        start=self.t;events=[];elapsed=0.
        while elapsed<dt-1e-12:
            left=dt-elapsed
            if self.rest>1e-12:
                held=min(left,self.rest);self.rest=max(0,self.rest-held);self.u=0.;elapsed+=held;continue
            crossing=math.inf
            if self.u>=self.theta:crossing=0.
            elif drive>self.theta:
                crossing=self.tauV*math.log((drive-self.u)/(drive-self.theta))
            if crossing<=left+1e-12:
                elapsed+=max(0,min(left,crossing));events.append(start+elapsed)
                self.u=0.;self.rest=self.refractory
            else:
                self.u=max(0,drive+(self.u-drive)*math.exp(-left/self.tauV));elapsed=dt
        decay=math.exp(-dt/self.tauR)
        integral=self.rate*self.tauR*(1-decay)
        self.rate*=decay
        for event in events:
            d=math.exp(-(start+dt-event)/self.tauR)
            self.rate+=d/self.tauR;integral+=1-d
        if self.adaptive:self.theta=bound(self.theta+self.eta*(integral-self.target*dt),self.lo,self.hi)
        self.t=start+dt
        return {'t':self.t,'u':self.u,'theta':self.theta,'rate':self.rate,
                'drive':drive,'count':len(events),'events':events}