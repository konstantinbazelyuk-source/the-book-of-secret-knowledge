'use strict';
/**
 * Ripple v0.1 structural-plasticity adapter. The original RippleNeuron.step
 * equations are imported unchanged. This adapter modifies the directed graph
 * between model neurons; no geometry, membranes or physical neurite is moved.
 *
 * All stimuli and spikes in this experiment are generated model data.
 */
const { RippleNeuron, bound } = require('../reference/v01_ripple_core_LOCKED.cjs');

function validate(config) {
  if (!config || typeof config !== 'object' || Array.isArray(config)) throw Error('object required');
  const {nodes=8,frames=800,dt=0.05,seed=17,plasticity=true,interval=40} = config;
  if (!Number.isInteger(nodes) || nodes<4 || nodes>32) throw Error('nodes must be 4..32');
  if (!Number.isInteger(frames) || frames<40 || frames>12000 || frames*nodes*nodes>3e6) throw Error('frames or workload exceeds budget');
  if (typeof dt!=='number' || !Number.isFinite(dt) || dt<=0 || dt>0.5) throw Error('dt must be 0..0.5');
  if (!Number.isInteger(seed) || seed<0 || seed>1000000) throw Error('seed out of bounds');
  if (typeof plasticity!=='boolean') throw Error('plasticity must be boolean');
  if (!Number.isInteger(interval) || interval<10 || interval>200) throw Error('interval must be 10..200');
  return {nodes,frames,dt,seed,plasticity,interval};
}

function seeded(seed) {
  let s=(seed>>>0)||1;
  return () => {s^=s<<13; s^=s>>>17; s^=s<<5; return (s>>>0)/4294967296;};
}

function run(config) {
  const opt=validate(config);
  const {nodes:n,frames,dt,seed,plasticity,interval}=opt;
  const random=seeded(seed);
  const units=Array.from({length:n},()=>new RippleNeuron());
  const edges=new Map();
  const edgeKey=(a,b)=>a+':'+b;
  const addEdge=(a,b,w,initial)=>{
    const key=edgeKey(a,b);
    if(a===b || edges.has(key)) throw Error('invalid or duplicate edge');
    edges.set(key,{from:a,to:b,weight:w,age:0,weakWindows:0,initial});
  };
  // Original directed sparse substrate. Nonlocal connections are not fabricated.
  for(let a=0;a<n;a++) {
    addEdge(a,(a+1)%n,0.22,true);
    addEdge(a,(a+2)%n,0.22,true);
  }
  const initialEdges=edges.size;
  const initialLinks=[...edges.values()].map(e=>[e.from,e.to]).sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
  const trace=new Array(n).fill(0);
  const scores=Array.from({length:n},()=>new Array(n).fill(0));
  const counts=new Array(n).fill(0);
  const history=[];
  const totals={grown:0,pruned:0,spikes:0,weight_updates:0};
  const maxOutgoing=Math.min(3,n-1),maxIncoming=Math.min(3,n-1),minOutgoing=1;
  const graphDegrees=()=>{
    const incoming=new Array(n).fill(0),outgoing=new Array(n).fill(0);
    for(const e of edges.values()) {incoming[e.to]++;outgoing[e.from]++;}
    return {incoming,outgoing};
  };
  for(let frame=0;frame<frames;frame++){
    const spikes=new Array(n).fill(0);
    // External alternating optical pulse cohorts; initial graph has both
    // same-cohort and cross-cohort edges, allowing an actual pruning test.
    const phase=Math.floor(frame/80)%2;
    for(let j=0;j<n;j++){
      let recurrent=0;
      for(const e of edges.values()) if(e.to===j) recurrent+=e.weight*trace[e.from];
      const inCohort=j%2===phase;
      const jitter=0.02*(random()-.5);
      const red=bound((inCohort?0.76:0.12)+jitter+0.11*recurrent,0,1);
      const out=units[j].step([red,0.2,0.15],dt);
      spikes[j]=out.count;
      counts[j]+=out.count;
      totals.spikes+=out.count;
    }
    const decay=Math.exp(-dt/0.55);
    for(let j=0;j<n;j++) trace[j]=trace[j]*decay+spikes[j];
    // Exponential coincidence estimate (proposed topology eligibility rule).
    const factor=1-Math.exp(-dt/1.8);
    for(let a=0;a<n;a++) for(let b=0;b<n;b++) {
      if(a!==b) scores[a][b]+=(Math.min(trace[a],trace[b])-scores[a][b])*factor;
    }
    if ((frame+1)%interval===0 && plasticity) {
      const degrees=graphDegrees();
      // Stabilize existing synapses while weak synapses progressively decay.
      for(const [key,e] of [...edges.entries()]){
        e.age++;
        const coherence=scores[e.from][e.to];
        e.weight=bound(e.weight+0.035*(coherence-0.15),0.07,0.55);
        totals.weight_updates++;
        e.weakWindows=coherence<0.10?e.weakWindows+1:0;
        if (e.age>=3 && e.weakWindows>=3 && degrees.outgoing[e.from]>minOutgoing){
          edges.delete(key);
          degrees.outgoing[e.from]--;
          degrees.incoming[e.to]--;
          totals.pruned++;
        }
      }
      // Recruit potential connections only after sustained correlated firing,
      // constrained by bounded in/out degree and distance cost on a ring.
      const candidates=[];
      for(let a=0;a<n;a++) for(let b=0;b<n;b++){
        if(a===b || edges.has(edgeKey(a,b)))continue;
        const distance=Math.min((a-b+n)%n,(b-a+n)%n);
        const merit=scores[a][b]-0.012*distance;
        if(merit>0.18)candidates.push({a,b,merit});
      }
      candidates.sort((u,v)=>v.merit-u.merit||u.a-v.a||u.b-v.b);
      for(const c of candidates){
        if(degrees.outgoing[c.a]>=maxOutgoing || degrees.incoming[c.b]>=maxIncoming)continue;
        addEdge(c.a,c.b,0.18,false);
        degrees.outgoing[c.a]++;
        degrees.incoming[c.b]++;
        totals.grown++;
      }
      history.push({frame:frame+1,edges:edges.size,grown:totals.grown,pruned:totals.pruned});
    }
  }
  const degrees=graphDegrees();
  const finalLinks=[...edges.values()].map(e=>({from:e.from,to:e.to,weight:+e.weight.toFixed(5),coherence:+scores[e.from][e.to].toFixed(5)})).sort((a,b)=>a.from-b.from||a.to-b.to);
  return {
    kernel:'locked-Ripple-v0.1',adapter:'ripple-structural-plasticity-v0.1',
    evidence:'computed model events; no external hardware or live-cell measurement',
    config:opt,initial_edges:initialEdges,final_edges:edges.size,
    initial_links:initialLinks,final_links:finalLinks,per_neuron_spikes:counts,
    per_neuron_thresholds:units.map(x=>+x.theta.toFixed(5)),
    topology_events:totals,degree_bounds:{max_in:maxIncoming,max_out:maxOutgoing,min_out:minOutgoing},
    final_degree:degrees,plasticity_history:history
  };
}

if(require.main===module){
  try{let s='';process.stdin.setEncoding('utf8');process.stdin.on('data',c=>{s+=c;if(s.length>8192)throw Error('input exceeds size limit');});process.stdin.on('end',()=>process.stdout.write(JSON.stringify(run(JSON.parse(s))))) }
  catch(e){console.error(e.message);process.exitCode=1;}
}
module.exports={run,validate};
