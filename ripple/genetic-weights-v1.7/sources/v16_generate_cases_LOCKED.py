"""Generate independent, fixed-seed synthetic tasks from v1.4 optical physics.
No task truth is supplied to an inference algorithm, and no physical measurement is implied.
"""
import hashlib,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'sources'))
from v14_physics_LOCKED import Setup,profile,count_photons
SCREEN=np.linspace(-.006,.006,41)
def norm(a):return a/a.sum()
P0=norm(profile(SCREEN,Setup(visibility=.02)));P1=norm(profile(SCREEN,Setup(visibility=.98)))
R=np.log(P1/P0)
def rev(x):return int(f'{x:04b}'[::-1],2)
def rol(x):return ((x<<1)|(x>>3))&15
def popcount(x):return int(x).bit_count()
def parity(x):return 15 if x.bit_count()%2 else 0
TRUTHS={
 'control_xor7':lambda x:x^7,
 'control_rotate_xor5':lambda x:rol(x^5),
 'and_0b':lambda x:x&11,
 'or_05':lambda x:x|5,
 'mul3_plus1':lambda x:(3*x+1)&15,
 'shift_right1':lambda x:x>>1,
 'popcount':popcount,
 'parity_broadcast':parity,
 'swap_middle':lambda x:(x&9)|((x&2)<<1)|((x&4)>>1),
 'unknown_permutation':None
}
# Fixed permutation is not exposed to search, and training inputs alone cannot determine held-out outputs.
UNKNOWN=[9,4,2,13,10,3,15,1,5,7,12,0,8,6,11,14]
def tx(v,photons,rng,condition):
    out=[];hard=0
    for i,k in enumerate((3,2,1,0)):
        b=(v>>k)&1
        if condition=='matched':sample=P1 if b else P0
        elif condition=='phase_shift':
            sample=norm(profile(SCREEN,Setup(visibility=.98 if b else .02,phase_rad=.8)))
        elif condition=='contrast_collapse':sample=P0
        else:raise ValueError(condition)
        llr=float(np.dot(count_photons(sample,photons,rng),R))
        out.append(round(llr,5));hard=(hard<<1)|int(llr>0)
    return {'llr':out,'hard':hard}
def build(holdout=False):
    cases=[]
    for kind,fn in TRUTHS.items():
      for seed in ((555,666) if holdout else (111,222,333,444)):
       rng=np.random.default_rng(seed*83041+sum(map(ord,kind)))
       order=list(map(int,rng.permutation(16)))
       for photons in (6,20,80):
        for condition in ('matched','phase_shift','contrast_collapse'):
         rng2=np.random.default_rng(seed*7177+photons*61+sum(map(ord,kind))*3+sum(map(ord,condition)))
         ex=[]
         for i,x in enumerate(order):
          y=UNKNOWN[x] if fn is None else fn(x)
          ex.append({'rx':tx(x,photons,rng2,condition),'ry':tx(y,photons,rng2,condition),
           'split':'train' if i<10 else 'test','x_true':x,'y_true':y})
         cases.append({'id':f'{kind}_{seed}_{photons}_{condition}', 'kind':kind,'seed':seed,
          'photons_per_bit':photons,'condition':condition,'examples':ex})
    out={'schema':'ripple-open-grammar-cases/1','reference':'unchanged v1.4 double-slit sampling profile',
      'code_domain':'4-bit input output; 10 training and 6 held-out values',
      'light_observations':'synthetic photon sampling, detector assumptions idealized','cases':cases}
    target=ROOT/('data/holdout_cases.json' if holdout else 'data/cases.json');target.write_text(json.dumps(out,separators=(',',':')))
    print(json.dumps({'cases':len(cases),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))
if __name__=='__main__':build('--holdout' in sys.argv)
