"""New v1.7 compositional tasks, synthesized using predeclared v1.6 primitives.
Held-out outputs only used by evaluator; never by rule synthesis.
"""
import json,sys,importlib.util,hashlib
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'sources'))
spec=importlib.util.spec_from_file_location('legacy',R/'sources/v16_generate_cases_LOCKED.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
P=json.loads((R/'data/grammar_locked.json').read_text()); BY={p['expr']:p for p in P}
PAIRS=[('add3(x)','rotate2(x)'),('shl1(x)','xor5(x)'),('xor9(x)','popcount(x)'),('rotate1(x)','multiply3(x)'),('gray(x)','add1(x)'),('or3(x)','rotate1(x)'),('swap_middle(x)','add5(x)'),('xor7(x)','and5(x)')]
# One unstructured permutation, explicitly not guaranteed to be representable.
UNKNOWN=[9,4,2,13,10,3,15,1,5,7,12,0,8,6,11,14]
known={tuple(p['outputs']) for p in P}
def get():
 functions={}
 for o,i in PAIRS:
  assert o in BY and i in BY,(o,i)
  out=tuple(BY[o]['outputs'][j] for j in BY[i]['outputs'])
  name=f"{o.replace('(x)','')}({i})"
  assert out not in known, f'Cannot call {name} novel; already in parent grammar'
  functions[name]=out
 return functions

def generate():
 funcs=get();funcs['unstructured_permutation']=tuple(UNKNOWN)
 result=[]
 for name,table in funcs.items():
  for seed in (901,902,903):
   rng=np.random.default_rng(seed*87041+sum(map(ord,name)))
   order=list(map(int,rng.permutation(16)))
   for photons in (6,80):
    for condition in ('matched','phase_shift'):
     rng2=np.random.default_rng(seed*1171+photons*67+sum(map(ord,name))*3+sum(map(ord,condition)))
     ex=[]
     for k,x in enumerate(order):
      y=table[x]
      ex.append({'rx':g.tx(x,photons,rng2,condition),'ry':g.tx(y,photons,rng2,condition),'split':'train' if k<10 else 'test','x_true':x,'y_true':y})
     result.append({'id':f'{name}:{seed}:{photons}:{condition}','kind':name,'seed':seed,'photons_per_bit':photons,'condition':condition,'examples':ex})
 d={'schema':'ripple-novel-compose/1','planned_compositions':list(funcs),'cases':result}
 target=R/'data/novel_compositions.json';target.write_text(json.dumps(d,separators=(',',':')))
 print('Novel cases',len(result),'sha',hashlib.sha256(target.read_bytes()).hexdigest());return d
if __name__=='__main__':generate()
