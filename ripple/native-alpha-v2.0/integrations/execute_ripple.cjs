'use strict';
// Actual original locked neuron evaluated by a separate OS process, not a behavioral mock.
const fs=require('fs'); const crypto=require('crypto');
const {RippleNeuron}=require('../reference/v01_ripple_core_LOCKED.cjs');
let raw=fs.readFileSync(0,'utf8');let req=JSON.parse(raw);
const rgb=req.rgb??[.5,.25,.1],dt=req.dt??.05,n=req.frames;
if(!Number.isInteger(n)||n<1||n>250000||!Array.isArray(rgb)||rgb.length!==3||rgb.some(x=>!Number.isFinite(x)||x<0||x>1)||!Number.isFinite(dt)||dt<=0||dt>.5)throw Error('invalid input');
let p=new RippleNeuron({theta:req.theta??.45,adaptive:req.adaptive??true,target:req.target??1});
let spikes=0,hasher=crypto.createHash('sha256');
for(let i=0;i<n;i++){
 let out=p.step(rgb,dt);spikes+=out.count;
 for(const event of out.events)hasher.update(event.toPrecision(15)+'|');
}
console.log(JSON.stringify({frames:n,model_seconds:p.t,spikes,final_theta:p.theta,rate:p.rate,event_hash:hasher.digest('hex'),kernel:'locked-Ripple-v0.1',real_execution:true,source_input:'user-supplied numeric or synthetic constants'}));
