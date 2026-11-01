'use strict';
const {parentPort,workerData}=require('node:worker_threads');
const {RippleNeuron}=require('./ripple_core_reference');
const {calculate}=require('./cpu_task');
const neuron=new RippleNeuron();
let pulses=0, jobs=0, modelSeconds=0;
function pulsePermit(){
 for(let k=0;k<5000;k++){
  const x=neuron.step([.35,0,0],.05);modelSeconds+=.05;
  if(x.count){pulses+=x.count;return;}
 }
 throw Error('Ripple neuron failed to emit an event within model-time limit');
}
parentPort.on('message',m=>{
 if(m.kind==='stop'){parentPort.close();return;}
 if(m.kind!=='work')return;
 try{
  if(workerData.mode==='ripple')pulsePermit();
  const result=calculate(m.id,m.rounds);jobs++;
  const response={kind:'result',id:m.id,result,attempt:m.attempt,
   sample:{pulses,jobs,modelSeconds:+modelSeconds.toFixed(4),rate:neuron.rate,threshold:neuron.theta}};
  if(workerData.resultDelayMs>0)setTimeout(()=>parentPort.postMessage(response),workerData.resultDelayMs);
  else parentPort.postMessage(response);
 }catch(e){parentPort.postMessage({kind:'error',id:m.id,error:String(e.message)});}
});
parentPort.postMessage({kind:'ready'});
