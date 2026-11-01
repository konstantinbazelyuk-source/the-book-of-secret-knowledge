'use strict';
const {verifySources,sha256}=require('./pins');
const {MemoryBridge}=require('./memory_bridge');

function validateTask(task){
 if(!task||typeof task!=='object'||!Number.isSafeInteger(task.id)||task.id<0||
   !Number.isSafeInteger(task.rounds)||task.rounds<1||task.rounds>3000000)throw Error('invalid task parameters');
 return {id:task.id,rounds:task.rounds};
}

class MemoryMycelium {
 static async open(options={}){
  const instance=new MemoryMycelium(options);
  try{await instance.bridge.request('ping');return instance;}
  catch(error){await instance.bridge.close().catch(()=>{});throw error;}
 }
 constructor(options){
  this.pins=verifySources();
  const {ParallelColony}=require('../vendor/mycelium-v02/src/parallel_colony');
  const {calculate}=require('../vendor/mycelium-v02/src/cpu_task');
  this.ParallelColony=ParallelColony;this.calculate=calculate;
  this.colonyOptions={maxWorkers:4,policy:'elastic',mode:'ripple',...options.colonyOptions};
  this.bridge=new MemoryBridge(options);this.tail=Promise.resolve();this.pending=0;this.closed=false;
 }
 _enqueue(action){
  if(this.closed)return Promise.reject(Error('memory mycelium closed'));
  if(this.pending>=16)return Promise.reject(Error('operation queue capacity exceeded'));
  this.pending++;
  const operation=this.tail.then(action);this.tail=operation.catch(()=>{});
  return operation.finally(()=>{this.pending--;});
 }
 _descriptor(task){
  const payload={schema:'ripple-result/1',kernelHash:this.pins.sourceDigest,id:task.id,rounds:task.rounds};
  return {...task,cacheKey:sha256(JSON.stringify(payload))};
 }
 _cachedValue(recall,task){
  if(!recall||recall.status!=='known'||typeof recall.value!=='string')return null;
  try{
   const body=JSON.parse(recall.value),p=body.payload;
   if(!p||p.schema!=='ripple-result/1'||p.kernelHash!==this.pins.sourceDigest||p.cacheKey!==task.cacheKey||
     p.id!==task.id||p.rounds!==task.rounds||p.verification!=='serial-parity'||
     !Number.isInteger(p.value)||p.value<0||p.value>0xffffffff||body.digest!==sha256(JSON.stringify(p)))return null;
   const source='result:'+task.cacheKey;
   if(!recall.source_ids.includes(source)||!recall.evidence.some(e=>e.source_id===source&&e.quote===recall.value))return null;
   return p.value;
  }catch{return null;}
 }
 async runBatch(tasks,{timeoutMs=30000}={}){
  if(!Array.isArray(tasks)||tasks.length>128)throw Error('task batch limit exceeded');
  if(!Number.isSafeInteger(timeoutMs)||timeoutMs<1||timeoutMs>60000)throw Error('invalid batch timeout');
  const normalized=tasks.map(validateTask),seen=new Set();
  for(const task of normalized){if(seen.has(task.id))throw Error('duplicate task id in batch');seen.add(task.id);}
  return this._enqueue(()=>this._run(normalized.map(t=>this._descriptor(t)),timeoutMs));
 }
 async _run(tasks,timeoutMs){
  const telemetry={cacheHits:0,cacheRejected:0,workerJobs:0,serialChecks:0,memoryWritesStored:0,memoryWritesRevoked:0};
  const results=new Map();const misses=[];let colonyReport=null;
  if(!tasks.length)return {results:[],telemetry,colonyReport};
  const lookup=await this.bridge.request('lookup_many',{keys:tasks.map(t=>t.cacheKey)});
  const found=new Map(lookup.map(r=>[r.key,r.recall]));
  for(const task of tasks){
   const recall=found.get(task.cacheKey);const value=this._cachedValue(recall,task);
   if(value!==null){
    results.set(task.id,{...task,value,origin:'memory',sourceId:'result:'+task.cacheKey});telemetry.cacheHits++;
   }else{
    if(recall){await this.bridge.request('forget_task',{key:task.cacheKey});telemetry.cacheRejected++;}
    misses.push(task);
   }
  }
  if(misses.length){
   const colony=new this.ParallelColony(this.colonyOptions);
   const records=[];
   try{
    for(const task of misses)colony.submit(task.id,task.rounds);
    await colony.waitDone({timeoutMs});
    for(const task of misses){
     const value=colony.completed.get(task.id);
     if(value!==this.calculate(task.id,task.rounds))throw Error('serial verification failed; result not absorbed');
     telemetry.serialChecks++;
     const payload={schema:'ripple-result/1',kernelHash:this.pins.sourceDigest,cacheKey:task.cacheKey,
       id:task.id,rounds:task.rounds,value,verification:'serial-parity'};
     const body=JSON.stringify({payload,digest:sha256(JSON.stringify(payload))});
     records.push({key:task.cacheKey,value:body});
     results.set(task.id,{...task,value,origin:'worker',sourceId:'result:'+task.cacheKey});
    }
    colonyReport={...colony.report(),actualWorkerThreadIds:[...colony.nodes.values()].map(n=>n.worker.threadId)};
    telemetry.workerJobs=misses.length;
   }finally{await colony.close();}
   const receipts=await this.bridge.request('store_results',{records});
   for(const receipt of receipts){
    if(receipt.status==='stored')telemetry.memoryWritesStored++;
    if(receipt.status==='revoked')telemetry.memoryWritesRevoked++;
   }
  }
  return {results:tasks.map(t=>results.get(t.id)),telemetry,colonyReport};
 }
 remember(observation){return this._enqueue(()=>this.bridge.request('remember',observation));}
 recall(subject,predicate,{asOf,knownAt}={}){return this._enqueue(()=>this.bridge.request('recall',{subject,predicate,asOf,knownAt}));}
 context(query,{budgetBytes=8192}={}){return this._enqueue(()=>this.bridge.request('context',{query,budgetBytes}));}
 consolidate(){return this._enqueue(()=>this.bridge.request('consolidate'));}
 forgetSource(sourceId){return this._enqueue(()=>this.bridge.request('forget_source',{sourceId}));}
 forgetTask(id,rounds){const task=this._descriptor(validateTask({id,rounds}));return this._enqueue(()=>this.bridge.request('forget_task',{key:task.cacheKey}));}
 health(){return this._enqueue(()=>this.bridge.request('health'));}
 async close(){
  if(!this.closePromise){this.closed=true;this.closePromise=this.tail.then(()=>this.bridge.close());}
  return this.closePromise;
 }
}
module.exports={MemoryMycelium};
