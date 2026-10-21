'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const fs=require('node:fs');
const path=require('node:path');
const {run,validate}=require('../integrations/structural_plasticity.cjs');

test('original immutable Ripple LIF',()=>{
 assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'../reference/v01_ripple_core_LOCKED.cjs'))).digest('hex'),
 'd75d4208e92f19623b127615bd52b4002e85d2c0a59b76471764b55a24294210');
});
test('plasticity disabled preserves graph and weights',()=>{
 const x=run({plasticity:false});
 assert.equal(x.initial_edges,16);
 assert.equal(x.final_edges,16);
 assert.equal(x.topology_events.grown,0);
 assert.equal(x.topology_events.pruned,0);
 assert.ok(x.final_links.every(e=>e.weight===0.22));
});
test('activity remodeling affects subsequent simulated neuron behavior',()=>{
 const x=run({}),f=run({plasticity:false});
 assert.ok(x.topology_events.grown>0);
 assert.ok(x.topology_events.pruned>0);
 assert.equal(x.initial_edges+x.topology_events.grown-x.topology_events.pruned,x.final_edges);
 assert.notDeepEqual(x.per_neuron_spikes,f.per_neuron_spikes);
 assert.equal(x.topology_events.spikes,x.per_neuron_spikes.reduce((a,b)=>a+b,0));
 assert.ok(x.final_degree.incoming.every(n=>n<=3));
 assert.ok(x.final_degree.outgoing.every(n=>n<=3&&n>=1));
});
test('repeatable from seed',()=>assert.deepEqual(run({seed:4,frames:120}),run({seed:4,frames:120})));
test('checkpoint/resume equals one-shot run to exact snapshot floats',()=>{
 const a=run({frames:240,save_state:true});
 const b=run({frames:560,checkpoint_state:a.checkpoint_state,save_state:true});
 const c=run({frames:800,save_state:true});
 assert.deepEqual(b.checkpoint_state,c.checkpoint_state);
 assert.deepEqual(b.final_links,c.final_links);
 assert.equal(b.end_frame,800);
});
test('checkpoint mismatches and corrupt structure rejected',()=>{
 const a=run({frames:80,save_state:true});
 assert.throws(()=>run({seed:55,checkpoint_state:a.checkpoint_state}));
 const bad=structuredClone(a.checkpoint_state);
 bad.edges[0].from=-9;
 assert.throws(()=>run({checkpoint_state:bad}));
});
test('bounded inputs reject unsafe work sizes',()=>{
 for(const bad of [{frames:-1},{frames:12001},{nodes:33},{nodes:32,frames:4000},{dt:Infinity},{seed:-1},{plasticity:'true'},{interval:0},{nodes:true}])assert.throws(()=>validate(bad));
});