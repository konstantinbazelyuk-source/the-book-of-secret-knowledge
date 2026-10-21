'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const crypto = require('node:crypto');
const path = require('node:path');
const {run, validate} = require('../integrations/structural_plasticity.cjs');
const ref=path.join(__dirname,'../reference/v01_ripple_core_LOCKED.cjs');

test('original preserved kernel unchanged (original SHA-256)', () => {
  assert.equal(crypto.createHash('sha256').update(fs.readFileSync(ref)).digest('hex'),
    'd75d4208e92f19623b127615bd52b4002e85d2c0a59b76471764b55a24294210');
});
test('disabled plasticity preserves graph and weight values',()=>{
  const v=run({plasticity:false});
  assert.equal(v.initial_edges,16);
  assert.equal(v.final_edges,16);
  assert.equal(v.topology_events.grown,0);
  assert.equal(v.topology_events.pruned,0);
  assert.equal(v.topology_events.weight_updates,0);
  assert.ok(v.final_links.every(e=>e.weight===0.22));
});
test('activity changes topology, affects computations, and respects budgets',()=>{
  const changing=run({}),fixed=run({plasticity:false});
  assert.ok(changing.topology_events.grown>0);
  assert.ok(changing.topology_events.pruned>0);
  assert.equal(changing.final_edges,changing.initial_edges + changing.topology_events.grown - changing.topology_events.pruned);
  assert.notDeepEqual(changing.per_neuron_spikes,fixed.per_neuron_spikes);
  assert.equal(changing.topology_events.spikes,changing.per_neuron_spikes.reduce((a,b)=>a+b,0));
  assert.ok(changing.final_degree.incoming.every(k=>k<=changing.degree_bounds.max_in));
  assert.ok(changing.final_degree.outgoing.every(k=>k<=changing.degree_bounds.max_out&&k>=changing.degree_bounds.min_out));
  assert.ok(changing.final_links.every(e=>e.weight>=0.07&&e.weight<=0.55));
});
test('same input and seed replay exactly',()=>{
  assert.deepEqual(run({nodes:10,frames:400,seed:4}),run({nodes:10,frames:400,seed:4}));
});
test('bounded inputs reject malformed jobs',()=>{
  for(const arg of [{frames:1},{frames:12001},{nodes:33},{nodes:32,frames:12000},
                    {dt:Infinity},{dt:0},{seed:-1},{plasticity:'on'},{interval:0},
                    {nodes:true}]) {
    assert.throws(()=>validate(arg));
  }
  assert.equal(validate({}).nodes,8);
});
