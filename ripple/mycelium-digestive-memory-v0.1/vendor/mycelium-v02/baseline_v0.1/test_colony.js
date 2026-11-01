const assert=require('node:assert/strict');
const fs=require('node:fs');
const {RippleNeuron}=require('./ripple_core_reference');global.RippleNeuron=RippleNeuron;
const {RippleMycelium}=require('./colony');
const {run}=require('./simulate'); // NOTE this module has CLI output side effects; replaced below.
const tests=[];function test(name,fn){tests.push([name,fn]);}
test('original kernel class and bound function are byte-identical to archival v0.1 source',()=>{
 const original=fs.readFileSync('source_reference/Ripple-Neuron-Simulator-v0.1-original.html','utf8');
 const actual=fs.readFileSync('ripple_core_reference.js','utf8');
 const bound=original.match(/^const bound=.*;$/m)[0];
 const core=original.slice(original.indexOf('class RippleNeuron{'),original.indexOf('\n}',original.indexOf('class RippleNeuron{'))+2);
 assert(actual.includes(bound+'\n'+core));
});
test('original leaky neuron begins with documented constants',()=>{const n=new RippleNeuron();assert.equal(n.theta,.45);assert.equal(n.tauV,.5);assert.equal(n.tauR,5);assert.equal(n.refractory,.1);});
test('darkness does not fire spontaneously',()=>{const n=new RippleNeuron();let events=0;for(let i=0;i<200;i++)events+=n.step([0,0,0],.05).count;assert.equal(events,0);});
test('blue channel inhibits input against red',()=>{const a=new RippleNeuron(),b=new RippleNeuron();let na=0,nb=0;for(let i=0;i<200;i++){na+=a.step([.35,0,0],.05).count;nb+=b.step([.35,0,.5],.05).count;}assert(na>0);assert.equal(nb,0);});
test('clone has new independent membrane state and original math',()=>{
 const c=new RippleMycelium({maxNodes:2}); const root=c.nodes.get(0);root.neuron.step([.35,0,0],.05);
 const n=c.spawn(0); assert(n.neuron instanceof RippleNeuron);assert.notEqual(root.neuron,n.neuron);assert.equal(n.neuron.t,0);assert.equal(n.neuron.theta,.45);assert.equal(c.nodes.size,2);
});
test('no uncontrolled replication beyond hard cap',()=>{
 const c=new RippleMycelium({maxNodes:3});for(let i=0;i<80;i++)c.submitSyntheticJob();for(let k=0;k<1000;k++)c.step();assert(c.nodes.size<=3);c.assertIntegrity();
});
test('logical work is shared across clones and recomposed',()=>{
 const c=new RippleMycelium({maxNodes:8});for(let i=0;i<30;i++)c.submitSyntheticJob();for(let k=0;k<1800;k++)c.step();c.assertIntegrity();assert.equal(c.outCount,30);assert.equal(c.pending(),0);assert(c.spawns>1);assert(c.relayCount>0);
 const workerIds=new Set([...c.finished.values()].flatMap(x=>x.workers));assert(workerIds.size>1);
});
test('copies shrink to one under extended quiet',()=>{
 const c=new RippleMycelium({maxNodes:8});for(let i=0;i<30;i++)c.submitSyntheticJob();for(let k=0;k<5000;k++)c.step();c.assertIntegrity();assert.equal(c.nodes.size,1);assert(c.retirements>0);
});
test('mesh tree remains undirected and connected after retirement',()=>{
 const c=new RippleMycelium({maxNodes:6});c.spawn(0);c.spawn(1);c.spawn(2);c.retireOne();c.assertIntegrity();
 const seen=new Set([0]);let frontier=[0];while(frontier.length){const n=c.nodes.get(frontier.shift());for(const id of n.peers)if(!seen.has(id)){seen.add(id);frontier.push(id);}}
 assert.equal(seen.size,c.nodes.size);
});
test('rejects malformed payloads and time steps',()=>{
 const c=new RippleMycelium();for(const input of [[],[NaN],[1.1],Array(257).fill(1)])assert.throws(()=>c.submit(input));
 assert.equal(c.inCount,0);assert.throws(()=>new RippleMycelium({maxNodes:0}));assert.throws(()=>new RippleMycelium({dt:.6}));
});
test('same workload leads to higher simulated completions with adaptive colony',()=>{
 const single=run(1),colony=run(12);assert.equal(single.final.submittedJobs,colony.final.submittedJobs);
 assert.equal(single.final.submittedJobs,84);assert(single.final.completedJobs<colony.final.completedJobs);
 assert.equal(colony.final.completedJobs,84);assert.equal(colony.final.queued,0);
 assert.equal(colony.final.nodes,1);assert.equal(colony.final.spawns,7);assert.equal(colony.final.retirements,6);
});
test('deterministic replay and exact result verification',()=>{
 const a=run(12),b=run(12);assert.deepEqual(a.final,b.final);assert.deepEqual(a.completedResults,b.completedResults);
 for(const v of a.completedResults){assert(Number.isInteger(v.sum));assert(Number.isInteger(v.sumsq));}
});
let failures=0;for(const [name,fn] of tests){try{fn();console.log('PASS',name);}catch(e){console.error('FAIL',name,e);failures++;}}
console.log(`${tests.length-failures}/${tests.length} tests passed.`);if(failures)process.exitCode=1;
