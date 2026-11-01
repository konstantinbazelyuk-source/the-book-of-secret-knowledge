'use strict';
// Separate research fork of the v0.1 colony. Original Ripple equations loaded unchanged.
const { RippleNeuron }=require('./ripple_core_reference');
const ROUTES=['none','neighbor','steal','pressure'];
const SCALES=['fixed1','fixed4','arrival','backlog','adaptive','fused'];
const GRAPHS=['tree','ring','mesh'];
function assertChoice(v,allowed,name){if(!allowed.includes(v))throw Error(`Invalid ${name}: ${v}`);}
class VariantColony {
 constructor({routing='pressure',scaling='adaptive',graph='ring',maxNodes=12,dt=.05,routePeriod=.5}={}){
  assertChoice(routing,ROUTES,'routing');assertChoice(scaling,SCALES,'scaling');assertChoice(graph,GRAPHS,'graph');
  if(!Number.isInteger(maxNodes)||maxNodes<1||maxNodes>64)throw Error('maxNodes must be 1..64');
  if(!Number.isFinite(dt)||dt<=0||dt>.5)throw Error('bad dt');
  this.routing=routing;this.scaling=scaling;this.graph=graph;this.maxNodes=maxNodes;this.dt=dt;this.routePeriod=routePeriod;
  this.t=0;this.nextId=0;this.nextJob=0;this.nodes=new Map();this.jobs=new Map();this.finished=new Map();
  this.inCount=0;this.outCount=0;this.totalUnits=0;this.unitsDone=0;this.relayCount=0;this.forwardHops=0;this.spawns=0;this.retires=0;
  this.arrivals=[];this.lastGrow=-1e5;this.lastShrink=-1e5;this.lowSince=null;this.lastControl=-1;this.lastRoute=-1;
  this.peakNodes=0;this.nodeSeconds=0;this.latencies=[];this.scaleLog=[];
  this.spawn(null);
  if(scaling==='fixed4')for(let i=1;i<Math.min(4,maxNodes);i++)this.spawn(0);
 }
 rebuild(){
  const a=[...this.nodes.values()].sort((x,y)=>x.id-y.id);for(const n of a)n.peers.clear();
  const link=(x,y)=>{if(x===y)return;x.peers.add(y.id);y.peers.add(x.id);};
  if(this.graph==='tree'){for(const n of a)if(n.parent!==null&&this.nodes.has(n.parent))link(n,this.nodes.get(n.parent));}
  if(this.graph==='ring'){for(let i=0;i<a.length-1;i++)link(a[i],a[i+1]);if(a.length>2)link(a[0],a[a.length-1]);}
  if(this.graph==='mesh'){for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++)link(a[i],a[j]);}
 }
 spawn(parentId){
  if(this.nodes.size>=this.maxNodes)return null;
  const id=this.nextId++;const n={id,parent:parentId,neuron:new RippleNeuron(),queue:[],peers:new Set(),done:0,pulses:0};this.nodes.set(id,n);this.spawns++;
  this.peakNodes=Math.max(this.peakNodes,this.nodes.size);this.scaleLog.push({t:+this.t.toFixed(2),type:'spawn',id});this.rebuild();return n;
 }
 retire(){
  if(this.nodes.size<=1)return false;
  const n=[...this.nodes.values()].filter(v=>v.id!==0).sort((a,b)=>a.queue.length-b.queue.length||b.id-a.id)[0];
  const parent=this.nodes.get(n.parent)||this.nodes.get(0);parent.queue.push(...n.queue);
  this.nodes.delete(n.id);for(const child of this.nodes.values())if(child.parent===n.id)child.parent=parent.id;
  this.rebuild();this.retires++;this.scaleLog.push({t:+this.t.toFixed(2),type:'retire',id:n.id});return true;
 }
 submit(values){
  if(!Array.isArray(values)||values.length<1||values.length>256||values.some(x=>!Number.isSafeInteger(x)||Math.abs(x)>1e5))throw Error('bad work');
  const id=this.nextJob++;const count=Math.ceil(values.length/4);let parts=[];
  for(let p=0;p<4;p++){const v=values.slice(p*count,(p+1)*count);if(v.length)parts.push({job:id,part:p,values:v});}
  const expected={sum:values.reduce((a,x)=>a+x,0),sumsq:values.reduce((a,x)=>a+x*x,0)};
  this.jobs.set(id,{expected,partials:new Map(),size:parts.length,created:this.t});
  // Fused seed distribution: put incoming work at best currently available node, not always the root.
  const target=[...this.nodes.values()].sort((a,b)=>a.queue.length-b.queue.length||a.id-b.id)[0];
  target.queue.push(...parts);this.arrivals.push({t:this.t,count:parts.length});this.inCount++;this.totalUnits+=parts.length;return id;
 }
 syntheticJob(){const id=this.nextJob;return this.submit(Array.from({length:32},(_,i)=>((id*17+i*13)%97)-48));}
 pending(){let n=0;for(const w of this.nodes.values())n+=w.queue.length;return n;}
 spread(){
  if(this.routing==='none')return;
  // Only graph-local single-hop handoffs; even "steal" and "pressure" cannot teleport work.
  const passes=this.routing==='neighbor'?2:3;
  for(let pass=0;pass<passes;pass++){
   const all=[...this.nodes.values()];
   const sources=(this.routing==='steal'?all.filter(n=>n.queue.length===0):all.filter(n=>n.queue.length>1));
   sources.sort((a,b)=>this.routing==='steal'?a.id-b.id:b.queue.length-a.queue.length||a.id-b.id);
   for(const n of sources){
    let dest=null,source=null;
    if(this.routing==='steal'){
      const neighbors=[...n.peers].map(i=>this.nodes.get(i)).filter(p=>p.queue.length>1);
      neighbors.sort((a,b)=>b.queue.length-a.queue.length||a.id-b.id);
      source=neighbors[0];dest=n;
    }else{
      const neighbors=[...n.peers].map(i=>this.nodes.get(i));
      if(this.routing==='pressure')neighbors.sort((a,b)=>((a.queue.length+1)/(a.neuron.rate+.3))-((b.queue.length+1)/(b.neuron.rate+.3))||a.id-b.id);
      else neighbors.sort((a,b)=>a.queue.length-b.queue.length||a.id-b.id);
      dest=neighbors[0];source=n;
    }
    if(source&&dest&&source.queue.length>dest.queue.length+1){dest.queue.push(source.queue.shift());this.relayCount++;}
   }
  }
 }
 control(){
  if(this.scaling==='fixed1'||this.scaling==='fixed4')return;
  const horizon=10;this.arrivals=this.arrivals.filter(x=>x.t>this.t-horizon);
  const incoming=this.arrivals.reduce((s,x)=>s+x.count,0)/Math.min(horizon,Math.max(1,this.t));
  const q=this.pending();const cap=.95*.72;
  let desired;
  if(this.scaling==='arrival')desired=Math.ceil(incoming/cap);
  else if(this.scaling==='backlog')desired=Math.ceil(q/(12*cap));
  else if(this.scaling==='fused') {
   // Resource-first under mild demand; add burst capacity when queue age is alarming.
   const oldest=[...this.jobs.values()].reduce((a,j)=>Math.max(a,this.t-j.created),0);
   const qGoal=Math.ceil(q/(12*cap));
   const urgent=incoming>2.5||oldest>6;
   desired=urgent?Math.ceil((incoming*.65+q/9)/cap):qGoal;
  } else desired=Math.ceil((incoming+q/12)/cap);
  desired=Math.max(1,Math.min(this.maxNodes,desired));
  if(desired>this.nodes.size&&this.t-this.lastGrow>=1-1e-8){
   let add=Math.min(2,desired-this.nodes.size);
   while(add--){const busy=[...this.nodes.values()].sort((a,b)=>b.queue.length-a.queue.length||a.id-b.id)[0];const child=this.spawn(busy.id);if(child){const moved=Math.floor(busy.queue.length/2);child.queue.push(...busy.queue.splice(0,moved));}}
   this.lastGrow=this.t;
  }
  const cooldown=(this.scaling==='adaptive'||this.scaling==='fused')?15:8;
  if(desired<this.nodes.size&&q<=this.nodes.size){
   if(this.lowSince===null)this.lowSince=this.t;
   if(this.t-this.lowSince>=cooldown&&this.t-this.lastShrink>=5){if(this.retire())this.lastShrink=this.t;}
  }else this.lowSince=null;
 }
 step(){
  const start=this.t;this.t=+(this.t+this.dt).toFixed(8);
  const sec=Math.round(this.t);if(Math.abs(this.t-sec)<this.dt/2&&sec!==this.lastControl){this.lastControl=sec;this.control();}
  const rt=Math.round(this.t/this.routePeriod)*this.routePeriod;
  if(Math.abs(this.t-rt)<this.dt/2&&rt!==this.lastRoute){this.lastRoute=rt;this.spread();}
  this.nodeSeconds+=this.nodes.size*this.dt;
  for(const n of this.nodes.values()){
   const out=n.neuron.step(n.queue.length?[.35,0,0]:[0,0,0],this.dt);n.pulses+=out.count;
   for(let i=0;i<out.count&&n.queue.length;i++){
    const c=n.queue.shift();const job=this.jobs.get(c.job);if(!job||job.partials.has(c.part))throw Error('duplicate/missing work');
    job.partials.set(c.part,{sum:c.values.reduce((a,x)=>a+x,0),sumsq:c.values.reduce((a,x)=>a+x*x,0),worker:n.id});n.done++;this.unitsDone++;
    if(job.partials.size===job.size){let sum=0,sumsq=0;const workers=[];for(const p of job.partials.values()){sum+=p.sum;sumsq+=p.sumsq;workers.push(p.worker);}
     if(sum!==job.expected.sum||sumsq!==job.expected.sumsq)throw Error('wrong result');
     const latency=this.t-job.created;this.latencies.push(latency);this.finished.set(c.job,{sum,sumsq,latency,workers:[...new Set(workers)]});this.jobs.delete(c.job);this.outCount++;
    }
   }
  }
 }
 assertIntegrity(){
  if(this.inCount!==this.outCount+this.jobs.size||this.pending()+this.unitsDone!==this.totalUnits)throw Error('accounting failed');
  if(this.nodes.size<1||this.nodes.size>this.maxNodes)throw Error('population cap');
  const seen=new Set([0]),stack=[0];while(stack.length){const n=this.nodes.get(stack.pop());for(const id of n.peers){if(!this.nodes.get(id)?.peers.has(n.id))throw Error('broken edge');if(!seen.has(id)){seen.add(id);stack.push(id);}}}
  if(seen.size!==this.nodes.size)throw Error('disconnected graph');return true;
 }
 summary(){
  const l=[...this.latencies].sort((a,b)=>a-b);const p95=l.length?l[Math.ceil(l.length*.95)-1]:null;
  return {variant:`${this.scaling}/${this.routing}/${this.graph}`,scaling:this.scaling,routing:this.routing,graph:this.graph,
   seconds:this.t,submitted:this.inCount,completed:this.outCount,pendingJobs:this.jobs.size,pendingChunks:this.pending(),
   processedChunks:this.unitsDone,spawns:this.spawns,retirements:this.retires,peakNodes:this.peakNodes,remainingNodes:this.nodes.size,
   relays:this.relayCount,workerSeconds:+this.nodeSeconds.toFixed(3),p95Latency:p95===null?null:+p95.toFixed(3),
   meanLatency:l.length?+(l.reduce((a,b)=>a+b,0)/l.length).toFixed(3):null};
 }
}
module.exports={VariantColony,ROUTES,SCALES,GRAPHS};
