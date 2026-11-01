'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const {VariantColony,ROUTES,SCALES,GRAPHS}=require('../src/colony_variants');
const {run,regimes}=require('../src/sweep');
const {ParallelColony}=require('../src/parallel_colony');const {calculate}=require('../src/cpu_task');
const {RippleNeuron}=require('../src/ripple_core_reference');
const tests=[];const test=(name,fn)=>tests.push([name,fn]);
test('original kernel source identical, no amended neuron equations',()=>{
 const a=fs.readFileSync(path.resolve(__dirname,'../baseline_v0.1/ripple_core_reference.js'));
 const b=fs.readFileSync(path.resolve(__dirname,'../src/ripple_core_reference.js'));
 assert(a.equals(b));
});
test('all routing, topology and scale choices make a connected graph',()=>{
 for(const scaling of SCALES)for(const routing of ROUTES)for(const graph of GRAPHS){const c=new VariantColony({scaling,routing,graph,maxNodes:8});
  while(c.nodes.size<8)c.spawn(0);c.assertIntegrity();while(c.nodes.size>1){c.retire();c.assertIntegrity();}}
});
test('new clones are independent, fresh original neurons',()=>{
 const c=new VariantColony();const a=c.nodes.get(0);a.neuron.step([.35,0,0],.05);
 const b=c.spawn(0);assert(b.neuron instanceof RippleNeuron);assert.notEqual(a.neuron,b.neuron);assert.equal(b.neuron.theta,.45);assert.equal(b.neuron.t,0);
});
test('all selected fused runs finish and recompose every job',()=>{
 for(const reg of Object.keys(regimes)){const {summary,finish}=run('fused','steal','tree',reg);assert.equal(summary.completed,summary.submitted);assert.equal(summary.pendingChunks,0);assert.equal(finish.length,summary.completed);}
});
test('fused final population contracts to one after burst',()=>{const v=run('fused','steal','tree');assert.equal(v.summary.remainingNodes,1);assert(v.summary.peakNodes>=2);assert(v.summary.retirements>0);});
test('all parameter combinations keep exact job conservation on four profiles',()=>{
 const rows=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../data/variant_sweep.json')));
 assert.equal(rows.length,SCALES.length*ROUTES.length*GRAPHS.length*Object.keys(regimes).length);
 for(const r of rows){assert.equal(r.submitted,r.completed+r.pendingJobs);assert(r.remainingNodes<=12);assert(r.processedChunks<=r.submitted*4);assert(r.relayCount===undefined||r.relays>=0);}
});
test('simulation deterministic under repeated identical inputs',()=>{for(const scale of ['backlog','adaptive','fused']){const a=run(scale,'steal','tree','burst');const b=run(scale,'steal','tree','burst');assert.deepEqual(a.summary,b.summary);assert.deepEqual(a.finish,b.finish);}});
test('original blue inhibition and silence invariants remain unchanged',()=>{
 const dark=new RippleNeuron(),blue=new RippleNeuron();let a=0,b=0;
 for(let i=0;i<200;i++){a+=dark.step([0,0,0],.05).count;b+=blue.step([.35,0,.5],.05).count;}
 assert.equal(a,0);assert.equal(b,0);
});
test('malformed input and illegal configurations rejected',()=>{
 for(const bad of [['a'],[],[NaN],[1.1],Array(257).fill(0)])assert.throws(()=>new VariantColony().submit(bad));
 for(const x of [{maxNodes:0},{graph:'zero'},{scaling:'free'},{routing:'random'},{dt:1}])assert.throws(()=>new VariantColony(x));
});
test('real thread pool calculates exact CPU results and reports completed ledger',async()=>{
 const c=new ParallelColony({maxWorkers:3,policy:'fixed',mode:'plain'});
 try{for(let i=0;i<18;i++)c.submit(i,50000);const r=await c.waitDone();assert.equal(r.completed,18);for(let i=0;i<18;i++)assert.equal(c.completed.get(i),calculate(i,50000));assert.equal(r.retries,0);}finally{await c.close();}
});
test('thread-level Ripple activity emits a pulse per admitted CPU task',async()=>{
 const c=new ParallelColony({maxWorkers:4,policy:'elastic',mode:'ripple'});
 try{for(let i=0;i<24;i++)c.submit(i,60000);const r=await c.waitDone();assert.equal(r.completed,24);assert(r.peakThreads>1);let total=0;for(const n of r.workerSamples){assert.equal(n.pulses,n.jobs);total+=n.jobs;}assert.equal(total,24);}
 finally{await c.close();}
});
test('adaptive parallel colony safely contracts after jobs complete',async()=>{
 const c=new ParallelColony({maxWorkers:4,policy:'elastic',mode:'ripple',idleMs:60,intervalMs:10});
 try{for(let i=0;i<30;i++)c.submit(i,50000);await c.waitDone();await new Promise(ok=>setTimeout(ok,300));assert.equal(c.nodes.size,1);assert(c.retires>=1);}finally{await c.close();}
});
test('cost-aware policy stays at one thread for tiny tasks',async()=>{
 const c=new ParallelColony({maxWorkers:4,policy:'cost-aware',mode:'ripple'});
 try{for(let i=0;i<32;i++)c.submit(i,5000);const r=await c.waitDone();assert.equal(r.completed,32);assert.equal(r.peakThreads,1);}finally{await c.close();}
});
test('cost-aware policy can expand for heavier tasks',async()=>{
 const c=new ParallelColony({maxWorkers:4,policy:'cost-aware',mode:'ripple'});
 try{for(let i=0;i<32;i++)c.submit(i,100000);const r=await c.waitDone();assert.equal(r.completed,32);assert.equal(r.peakThreads,4);}finally{await c.close();}
});
test('duplicate identity rejected before dispatch',async()=>{const c=new ParallelColony();try{c.submit(0,20);assert.throws(()=>c.submit(0,20));await c.waitDone();assert.equal(c.completed.size,1);}finally{await c.close();}});
test('killed busy worker loses no job: retry and exact verification',async()=>{
 const c=new ParallelColony({maxWorkers:3,policy:'elastic',mode:'ripple',resultDelayMs:150});
 try{for(let i=0;i<12;i++)c.submit(i,30000);
  await new Promise(ok=>setTimeout(ok,80));const killed=await c.injectCrash();assert.equal(killed,true);
  const r=await c.waitDone({timeoutMs:20000});assert.equal(r.completed,12);assert(r.retries>=1);
  for(let i=0;i<12;i++)assert.equal(c.completed.get(i),calculate(i,30000));
 }finally{await c.close();}
});
test('crashed only/root thread is replaced and task completed',async()=>{
 const c=new ParallelColony({maxWorkers:1,policy:'elastic',mode:'ripple',resultDelayMs:160});
 try{c.submit(0,30000);await new Promise(ok=>setTimeout(ok,70));assert.equal(await c.injectCrash(),true);
  const r=await c.waitDone({timeoutMs:20000});assert.equal(r.completed,1);assert(r.retries>=1);assert.equal(c.completed.get(0),calculate(0,30000));assert(c.nodes.size>=1);
 }finally{await c.close();}
});
(async()=>{let failed=0;for(const [name,fn] of tests){try{await fn();console.log('PASS',name);}catch(e){failed++;console.error('FAIL',name,e.stack);}}console.log(`${tests.length-failed}/${tests.length} tests passed`);if(failed)process.exitCode=1;})();
