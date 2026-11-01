'use strict';
const path=require('node:path');const {Worker}=require('node:worker_threads');const {performance}=require('node:perf_hooks');
// Real Node worker threads. Master-owned queues; neighbor-local transfers; no external actions.
class ParallelColony {
 constructor({maxWorkers=4,policy='elastic',mode='ripple',topology='ring',idleMs=180,intervalMs=15,maxAttempts=3,resultDelayMs=0}={}){
  if(!Number.isInteger(maxWorkers)||maxWorkers<1||maxWorkers>32)throw Error('bad worker count');
  if(!['elastic','fixed','cost-aware'].includes(policy)||!['ripple','plain'].includes(mode)||!['ring','tree','mesh'].includes(topology))throw Error('bad policy');
  this.resultDelayMs=resultDelayMs;this.maxWorkers=maxWorkers;this.policy=policy;this.mode=mode;this.topology=topology;this.idleMs=idleMs;this.intervalMs=intervalMs;this.maxAttempts=maxAttempts;
  this.work=new Map();this.completed=new Map();this.nodes=new Map();this.nextId=0;
  this.spawns=0;this.retires=0;this.retries=0;this.relays=0;this.peakNodes=0;this.lastBusy=performance.now();this.closing=false;
  this.events=[];this.pendingResolvers=[];this.failures=[];
  this.spawn();
  if(policy==='fixed')while(this.nodes.size<this.maxWorkers)this.spawn();
  this.timer=setInterval(()=>{if(!this.closing)this.pump();},intervalMs);
 }
 link(){
  const a=[...this.nodes.values()].sort((x,y)=>x.id-y.id);for(const n of a)n.peers.clear();
  const add=(x,y)=>{if(x===y)return;x.peers.add(y.id);y.peers.add(x.id);};
  if(this.topology==='ring'){for(let i=0;i<a.length-1;i++)add(a[i],a[i+1]);if(a.length>2)add(a[0],a[a.length-1]);}
  if(this.topology==='mesh')for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++)add(a[i],a[j]);
  if(this.topology==='tree')for(let i=1;i<a.length;i++)add(a[Math.floor((i-1)/2)],a[i]);
 }
 spawn(){
  if(this.closing||this.nodes.size>=this.maxWorkers)return null;
  const id=this.nextId++;const worker=new Worker(path.join(__dirname,'parallel_worker.js'),{workerData:{mode:this.mode,resultDelayMs:this.resultDelayMs}});
  const n={id,worker,queue:[],peers:new Set(),ready:false,busy:null,retiring:false,done:0,observed:null};
  this.nodes.set(id,n);this.spawns++;this.peakNodes=Math.max(this.peakNodes,this.nodes.size);this.events.push({type:'spawn',id});this.link();
  worker.on('message',msg=>this.onMessage(n,msg));
  worker.on('error',err=>{this.failures.push({id,error:String(err)});});
  worker.on('exit',code=>this.onExit(n,code));return n;
 }
 onMessage(n,m){
  if(!this.nodes.has(n.id)||n.retiring||this.closing)return;
  if(m.kind==='ready'){n.ready=true;this.pump();return;}
  if(m.kind==='result'||m.kind==='error'){
   const id=n.busy;n.busy=null;
   if(id!==m.id)return; // stale response (e.g. after requeue); never duplicate a completion
   const rec=this.work.get(id);if(!rec||rec.status!=='inflight'||rec.owner!==n.id)return;
   if(m.kind==='error'){this.requeue(rec,'worker reported error');}
   else {rec.status='done';rec.owner=null;rec.value=m.result;rec.finished=performance.now();this.completed.set(id,m.result);n.observed=m.sample;n.done++;this.lastBusy=performance.now();}
   this.pump();this.resolveWaiters();
  }
 }
 requeue(rec,why){
  if(rec.status==='done')return;
  if(rec.attempt>=this.maxAttempts){rec.status='failed';rec.owner=null;this.failures.push({id:rec.id,error:`retry limit: ${why}`});return;}
  rec.status='queued';rec.owner=null;const root=[...this.nodes.values()].sort((a,b)=>a.id-b.id)[0];
  if(root)root.queue.push(rec.id);this.retries++;
 }
 onExit(n,code){
  if(!this.nodes.has(n.id))return;
  this.nodes.delete(n.id);
  const leftovers=[...n.queue];if(n.busy!==null)leftovers.push(n.busy);
  if(!this.nodes.size&&!this.closing)this.spawn();
  const root=[...this.nodes.values()].sort((a,b)=>a.id-b.id)[0];
  for(const id of leftovers){const rec=this.work.get(id);if(!rec||rec.status==='done'||rec.status==='failed')continue;
   if(rec.status==='inflight')this.requeue(rec,`worker ${n.id} exited code ${code}`);
   else if(root)root.queue.push(id);else {rec.status='queued';rec.owner=null;}
  }
  this.link();this.events.push({type:n.retiring?'retired':'unexpected_exit',id:n.id,code});
  if(!n.retiring&&!this.closing)this.failures.push({worker:n.id,error:`unexpected exit ${code}`});
  if(!this.closing)this.pump();this.resolveWaiters();
 }
 submit(n,rounds=200000){
  if(this.closing)throw Error('closed');
  if(!Number.isSafeInteger(n)||n<0||this.work.has(n))throw Error('duplicate or invalid job id');
  if(!Number.isSafeInteger(rounds)||rounds<1||rounds>3000000)throw Error('bad rounds');
  const rec={id:n,rounds,status:'queued',owner:null,attempt:0,created:performance.now()};this.work.set(n,rec);
  const root=[...this.nodes.values()].sort((a,b)=>a.id-b.id)[0];if(!root)throw Error('no root');root.queue.push(n);
  this.lastBusy=performance.now();this.pump();return n;
 }
 backlog(){return [...this.work.values()].filter(w=>w.status==='queued').length;}
 pump(){
  if(this.closing)return;
  const queued=this.backlog();
  if(this.policy!=='fixed'&&queued>0){
   const inFlight=[...this.nodes.values()].filter(n=>n.busy!==null).length;
   const enoughCompute=this.policy!=='cost-aware'||[...this.work.values()].some(rec=>rec.status!=='done'&&rec.rounds>=50000);
   const desired=enoughCompute?Math.min(this.maxWorkers,Math.max(1,Math.ceil((queued+inFlight)/5))):1;
   while(this.nodes.size<desired)this.spawn();
  }
  // One-hop moves along an undirected logical graph. Every unit has one queue owner.
  for(let pass=0;pass<4;pass++)for(const source of [...this.nodes.values()].sort((a,b)=>b.queue.length-a.queue.length||a.id-b.id)){
   if(source.queue.length<2)continue;
   const peers=[...source.peers].map(id=>this.nodes.get(id)).filter(Boolean).sort((a,b)=>a.queue.length-b.queue.length||a.id-b.id);
   const dst=peers[0];if(dst&&source.queue.length>dst.queue.length+1){dst.queue.push(source.queue.shift());this.relays++;}
  }
  for(const n of this.nodes.values()){
   if(n.ready&&!n.retiring&&n.busy===null&&n.queue.length){
    const id=n.queue.shift();const rec=this.work.get(id);if(!rec||rec.status!=='queued')throw Error('queue integrity error');
    rec.status='inflight';rec.owner=n.id;rec.attempt++;n.busy=id;n.worker.postMessage({kind:'work',id,rounds:rec.rounds,attempt:rec.attempt});
   }
  }
  if(this.policy!=='fixed'&&queued===0&&[...this.nodes.values()].every(n=>n.busy===null)&&performance.now()-this.lastBusy>this.idleMs&&this.nodes.size>1){
    // Safe retirement: only a ready, idle, empty-queue clone can be stopped.
    const rootId=Math.min(...this.nodes.keys());
    const spare=[...this.nodes.values()].filter(n=>n.id!==rootId&&n.busy===null&&n.queue.length===0&&!n.retiring).sort((a,b)=>b.id-a.id)[0];
    if(spare){spare.retiring=true;this.retires++;spare.worker.postMessage({kind:'stop'});}
  }
 }
 waitDone({timeoutMs=30000}={}){
  return new Promise((resolve,reject)=>{
   const w={resolve,reject,timeout:setTimeout(()=>{this.pendingResolvers=this.pendingResolvers.filter(x=>x!==w);reject(Error('timeout'));},timeoutMs)};
   this.pendingResolvers.push(w);this.resolveWaiters();
  });
 }
 resolveWaiters(){
  const failed=[...this.work.values()].filter(x=>x.status==='failed');
  const allDone=this.work.size>0&&this.completed.size===this.work.size;
  if(!failed.length&&!allDone)return;
  for(const w of this.pendingResolvers.splice(0)){clearTimeout(w.timeout);if(failed.length)w.reject(Error(`${failed.length} failed tasks`));else w.resolve(this.report());}
 }
 report(){
  const latencies=[...this.work.values()].filter(x=>x.finished).map(x=>x.finished-x.created).sort((a,b)=>a-b);
  return {policy:this.policy,mode:this.mode,topology:this.topology,submitted:this.work.size,completed:this.completed.size,
   pending:this.backlog(),inflight:[...this.nodes.values()].filter(x=>x.busy!==null).length,
   p95LatencyMs:latencies.length?+latencies[Math.ceil(latencies.length*.95)-1].toFixed(2):null,
   peakThreads:this.peakNodes,createdThreads:this.spawns,retiredThreads:this.retires,retries:this.retries,relays:this.relays,
   workerSamples:[...this.nodes.values()].filter(x=>x.observed).map(x=>({id:x.id,...x.observed})),
   failures:this.failures};
 }
 async injectCrash(){const n=[...this.nodes.values()].find(n=>n.busy!==null&&!n.retiring);if(!n)return false;await n.worker.terminate();return true;}
 async close(){
  this.closing=true;clearInterval(this.timer);
  for(const w of this.pendingResolvers.splice(0)){clearTimeout(w.timeout);w.reject(Error('colony closed'));}
  await Promise.allSettled([...this.nodes.values()].map(n=>n.worker.terminate()));
  this.nodes.clear();
 }
}
module.exports={ParallelColony};
