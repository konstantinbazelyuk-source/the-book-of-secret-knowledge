#!/usr/bin/env python3
"""Source-pinned, read-only critical transition analysis for Ripple.

Usage (from checkout): python research/ripple-critical-transitions-v0.1/analyze.py [--run-graph]
Outputs JSON. Does not modify locked sources or infer intelligence/consciousness.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = 'd75d4208e92f19623b127615bd52b4002e85d2c0a59b76471764b55a24294210'
ORIGINAL = ROOT / 'docs' / 'ripple-core.js'
GRAPH = ROOT / 'ripple/native-alpha-v2.0/integrations/structural_plasticity.cjs'


def rate(D, theta=.45):
    return 0.0 if D <= theta else 1/(.1+.5*math.log(D/(D-theta)))


def check_neuron():
    digest = hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
    if digest != EXPECTED:
        raise RuntimeError('locked original neuron SHA-256 changed; refusing to infer source parity')
    script = '''
const {RippleNeuron}=require(process.argv[1]);
let result=[];
for(const D of [.44,.45,.50,.54,.60]){
  let n=new RippleNeuron({adaptive:false}),events=[];
  for(let t=0;t<2400;t++) events.push(...n.step([D/2,0,0],.05).events);
  let hz=events.length>1?(events.length-1)/(events.at(-1)-events[0]):0;
  result.push({D,spikes:events.length,observed_hz:hz});
}
process.stdout.write(JSON.stringify(result));'''
    run=subprocess.run(['node','-e',script,str(ORIGINAL)],
                       text=True,capture_output=True,timeout=40,check=True)
    trials=json.loads(run.stdout)
    for item in trials:
        expected=rate(item['D'])
        item['analytic_hz']=expected
        item['absolute_error']=abs(item['observed_hz']-expected)
        if item['absolute_error']>1e-10:
            raise RuntimeError('original neuron numerical output disagrees with analytic law')
    return {'sha256':digest,'cases':trials,'fixed_theta_drive_for_1Hz':
            .45/(-math.expm1(-1.8))}


def graph_run(plasticity):
    config={'nodes':8,'frames':800,'dt':.05,'seed':17,'interval':40,
            'plasticity':plasticity}
    r=subprocess.run(['node',str(GRAPH)],input=json.dumps(config),
                     text=True,capture_output=True,check=True,timeout=100)
    obj=json.loads(r.stdout)
    return {'input':config,'final_edges':obj['final_edges'],
            'simulated_spikes':obj['topology_events']['spikes'],
            'grown':obj['topology_events']['grown'],
            'pruned':obj['topology_events']['pruned']}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--run-graph',action='store_true',help='also execute original 8-neuron structural graph two ways')
    opt=p.parse_args()
    result={'evidence':'original source execution and derived mathematics; synthetic model only',
            'ripple':check_neuron(),
            'growth_q_strict_greater_than':{str(d):.18+.012*d for d in range(1,5)},
            'kokoro':{'conditional_feedback':'memory_alpha * (retrieved_next_rgb - current_external_rgb)',
                      'full_fusion_execution':'not attempted by this command'}}
    if opt.run_graph:
        result['graph_source_runs']={'plastic':graph_run(True),'static':graph_run(False)}
    print(json.dumps(result,indent=2))

if __name__ == '__main__':main()
