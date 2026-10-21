'use strict';
// Drives the original untouched Ripple v0.1 implementation with numeric
// mining observations. The model is signal-processing; it does not mine hashes.
const fs = require('node:fs');
const path = require('node:path');
const orig = path.resolve(__dirname, '../../native-alpha-v2.0/reference/v01_ripple_core_LOCKED.cjs');
const local = path.resolve(__dirname, '../legacy/v01_ripple_core_LOCKED.cjs');
const {RippleNeuron} = require(fs.existsSync(orig) ? orig : local);
const items = JSON.parse(fs.readFileSync(0, 'utf8'));
if (!Array.isArray(items) || items.length > 24) throw Error('invalid observation batch');
const neuron = new RippleNeuron();
let total = 0, recent = null;
for (const rgb of items) {
  if (!Array.isArray(rgb) || rgb.length !== 3) throw Error('RGB observation must be a triple');
  recent = neuron.step(rgb, .5);
  total += recent.count;
}
process.stdout.write(JSON.stringify({source: fs.existsSync(orig)?'repository locked v0.1':'shipped locked v0.1',
  observations:items.length, spike_count:total,
  latest_step_spikes:recent?.count ?? 0,
  firing_rate:recent?.rate ?? 0, threshold:recent?.theta ?? .45})+'\n');
