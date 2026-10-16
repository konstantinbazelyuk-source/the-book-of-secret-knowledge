"""Ripple v1.4 double-slit physical-law reference + statistical sensor simulator.

These are established optics equations. Simulation does not measure real waves/photons.
"""
import math
from dataclasses import dataclass
import numpy as np

C=299792458.0
EPS0=8.8541878128e-12
H=6.62607015e-34

@dataclass(frozen=True)
class Setup:
    wavelength_m:float=532e-9
    separation_m:float=0.3e-3
    width_m:float=0.05e-3
    distance_m:float=1.8
    visibility:float=1.0
    phase_rad:float=0.0
    def validate(self):
        if not(380e-9<=self.wavelength_m<=750e-9):raise ValueError('visible light range only')
        if not(0<self.width_m<self.separation_m):raise ValueError('nonoverlapping slits required')
        if not(0<self.distance_m<=100):raise ValueError('distance must be positive')
        if not(0<=self.visibility<=1):raise ValueError('0<=visibility<=1')
        if not math.isfinite(self.phase_rad):raise ValueError('finite phase needed')
        return self

def sinc(x):
    """sin(x)/x stable at zero for scalar/array."""
    x=np.asarray(x,dtype=float)
    return np.sinc(x/np.pi)

def profile(x_m,setup:Setup,finite=True):
    """Relative intensity with 1.0 central maximum for v=1, phi=0.
    I=0.5 sinc(beta)^2 [1 + V cos(delta + phi)],
    beta=pi*a*sin(theta)/lambda, delta=2pi*d*sin(theta)/lambda.
    Partial coherence uses REAL degree of coherence V in [0,1].
    No photon location/path is assigned by this formula.
    """
    setup.validate()
    x=np.asarray(x_m,dtype=float)
    st=x/np.hypot(x,setup.distance_m)
    beta=np.pi*setup.width_m*st/setup.wavelength_m
    delta=2*np.pi*setup.separation_m*st/setup.wavelength_m + setup.phase_rad
    env=sinc(beta)**2 if finite else np.ones_like(x)
    p=0.5*env*(1+setup.visibility*np.cos(delta))
    return np.maximum(p,0.0)

def field_superposition(x_m,setup:Setup,finite=True):
    """Coherent two-equal-slit scalar phasors, I=|A1+A2|^2.
    Does NOT track polarization, optical time oscillations, or measured E vector.
    """
    setup.validate()
    if setup.visibility!=1:raise ValueError('phasor equality check requires coherence V=1')
    x=np.asarray(x_m,dtype=float)
    st=x/np.hypot(x,setup.distance_m)
    beta=np.pi*setup.width_m*st/setup.wavelength_m
    delta=2*np.pi*setup.separation_m*st/setup.wavelength_m+setup.phase_rad
    envelope=sinc(beta) if finite else np.ones_like(x)
    a1=.5*envelope*np.exp(.5j*delta)
    a2=.5*envelope*np.exp(-.5j*delta)
    return np.abs(a1+a2)**2

def naive_intensity_sum(x_m,setup:Setup,finite=True):
    """Two mutually incoherent equal-intensity slit contributions. No interference."""
    return profile(x_m,Setup(setup.wavelength_m,setup.separation_m,setup.width_m,setup.distance_m,0,setup.phase_rad),finite)

def field_amplitudes_from_irradiance(irradiance_w_m2:float):
    """Conditional *derived* plane-wave sinusoidal amplitudes in vacuum.
    NO measurement of optical E(t) or B(t) is performed.
    """
    if not np.isfinite(irradiance_w_m2) or irradiance_w_m2<0:raise ValueError('nonnegative finite irradiance required')
    e=math.sqrt(2*irradiance_w_m2/(C*EPS0))
    return dict(e_peak_v_m=e,b_peak_t=e/C,photon_energy_at_532nm_j=H*C/(532e-9))

def count_photons(intensities, n:int, rng:np.random.Generator):
    """Conditional multinomial sampling of EXACTLY n photon detection positions.
    Distribution proportional to ideal relative intensity over sampled screen bins.
    Detector loss, antibunching, dead time, coincidence effects not simulated.
    """
    v=np.asarray(intensities,float)
    if n<0 or len(v)==0 or np.any(~np.isfinite(v)) or np.any(v<0) or v.sum()<=0:raise ValueError('invalid rate or total')
    return rng.multinomial(n,v/v.sum())

def simulated_sensor(values, scale:float, dark:float, rng:np.random.Generator, clip=1.0):
    """Independent Poisson detection count for fixed integration bins; estimate intensity.
    Clipped estimates treated as sensor-saturated, not true observations.
    """
    if scale<=0 or dark<0:raise ValueError('invalid detector gain/dark background')
    vals=np.asarray(values,float)
    counts=rng.poisson(scale*np.maximum(vals,0)+dark)
    return np.clip((counts-dark)/scale,0,clip),counts

if __name__=='__main__':
    x=np.linspace(-.015,.015,601)
    p=profile(x,Setup())
    print('central',profile(np.array([0.]),Setup())[0], 'central finite intensity',p[len(p)//2])
