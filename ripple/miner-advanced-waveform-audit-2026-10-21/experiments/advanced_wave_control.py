"""Experiment only: archived 16-cell Regulatory v2 computes causal batching policy.

SHA256d is always computed by the real native midstate backend. The archived
HeterogeneousRipple calls its original Regulatory Colony v2, with other modules
explicitly disabled for this ablation. Input channels are actual measured
workload ratio, throughput, and share/backpressure ratio, not optical colors.
"""
from __future__ import annotations
import ctypes,json,math,random,statistics,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FUSION_BASE=ROOT/'experiments'/'waveform'/'heterogeneous_source'
FUSION=FUSION_BASE/'Ripple_Heterogeneous_Fusion_v1'
if not FUSION.exists():
    import hashlib,zipfile
    original=ROOT/'experiments'/'waveform'/'Ripple_Heterogeneous_Mathematical_Fusion_v1_Executable.zip'
    expected='47d1b0765fde49c64643982599ee0a67ef46169afc336a76d43df5a13adef173'
    if hashlib.sha256(original.read_bytes()).hexdigest()!=expected:
        raise RuntimeError('Original advanced Ripple archive SHA256 mismatch')
    with zipfile.ZipFile(original) as z:
        if any(x.startswith('/') or '..' in Path(x).parts for x in z.namelist()):
            raise RuntimeError('Unsafe archive path')
        z.extractall(FUSION_BASE)
sys.path.insert(0,str(FUSION))
from fusion import HeterogeneousRipple
from benchmark_midstate import load,scan


def run(policy,total=750000,update_every=1):
    lib=load('libripple_midstate.so')
    prefix=bytes((19*i+37)%256 for i in range(76))
    rem=total;nonce=0;last_hps=1500000.;last_share_fraction=0.;batches=[];neural=[]
    control_sec=0.;hash_sec=0.;start=time.perf_counter();last_count=20000;loop_index=0
    brain=HeterogeneousRipple(enable={'regulatory':True,'genomic':False,'mushroom':False,'ring':False,'laboratory':False,'memory':False}) if policy=='regulatory-v2' else None
    try:
      while rem:
        if brain and loop_index%update_every==0:
          # Channels are documented numeric *mining signals* mapped to [0,1].
          rgb=[min(1.,rem/total),min(1.,last_hps/2500000.),min(1.,last_share_fraction)]
          before=time.perf_counter();state=brain.step(rgb);control_sec+=time.perf_counter()-before
          membrane=state['regulatory']['average_membrane']
          # Designed, task-specific causal coupling; evaluate rather than assume optimal.
          count=max(2500,min(40000,round(20000*(1+0.55*math.tanh(membrane)))))
          neural.append({'inputs':rgb,'membrane':membrane,'selected_batch':count})
          last_count=count
        elif brain:count=last_count
        else:count=20000
        count=min(count,rem)
        rows,elapsed=scan(lib,prefix,nonce,count,0,0)
        assert not rows
        hash_sec+=elapsed
        nonce+=count;rem-=count;last_hps=count/max(elapsed,1e-9)
        batches.append(count);loop_index+=1
      wall=time.perf_counter()-start
      return {'policy':policy,'hashes':nonce,'wall_seconds':wall,'hash_seconds':hash_sec,
            'controller_seconds':control_sec,'update_every':update_every,'effective_hps':nonce/wall,'batches':len(batches),
            'min_batch':min(batches),'max_batch':max(batches),'first_signals':neural[:4]}
    finally:
      if brain:brain.close()

def main():
 random.seed(5)
 arr=[]
 for i in range(3):
   variants=['fixed','regulatory-v2','wave-every-4','wave-every-12']
   if i%2:variants.reverse()
   for p in variants:
     arr.append({'round':i,**run('fixed' if p=='fixed' else 'regulatory-v2',update_every=1 if p=='regulatory-v2' else (4 if p=='wave-every-4' else 12)),'variant':p})
 overall={p:statistics.median(x['effective_hps'] for x in arr if x['variant']==p) for p in ('fixed','regulatory-v2','wave-every-4','wave-every-12')}
 report={'inputs':'real SHA-256d scan throughput and remaining work, normalized as numeric channels','advanced_source':'unmodified archived Ripple Heterogeneous Fusion v1 Regulatory Colony v2: 16 Delta/Daughter/Charlie cells, with other compartments disabled','hardware':'local Linux container, native C/OpenSSL midstate SHA256d','rounds':arr,'median_hps':overall,'effect_ratios':{k:v/overall['fixed'] for k,v in overall.items()},'scoped_conclusion':'Ablation of one advanced original mathematical family as a causal controller, not cryptanalytic Bitcoin shortcut or integrated financial miner'}
 (ROOT/'experiments'/'waveform'/'advanced_wave_report_rerun.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({'median_hps':overall,'relative_speed':report['effect_ratios'],'trials':len(arr),'first_wave_transitions':next(x['first_signals'] for x in arr if x['policy']=='regulatory-v2')[:3]},indent=2))
if __name__=='__main__':main()