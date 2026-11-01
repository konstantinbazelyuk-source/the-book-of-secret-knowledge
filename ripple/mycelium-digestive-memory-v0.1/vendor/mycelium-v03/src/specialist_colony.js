'use strict';
const {RippleNeuron}=require('./ripple_core_reference');
const {ControlledNeuron,analyticFrequency}=require('./feedback_sweep');
const calc=require('./specialist_math');
const roles=['learning','product','study'];
const popChoices=['single','fixed4','specialists4','v2-heuristic','capacity-general','capacity-specialist'];
const routes=['leastqueue','affinity','learned','roundrobin'];
function service(role,type){return role===type?1:role==='general'?2:3;} // Explicit hypothetical event-demand, not observed speed!
function quantile(a,q){if(!a.length)return null;let s=[...a].sort((x,y)=>x-y);return s[Math.min(s.length-1,Math.ceil(q*s.length)-1)];}
class SpecialistColony{
 constructor({growth='capacity-specialist',route='affinity',graph='tree',feedback='original',maxNodes=8,dt=.05,hopDelay=.15,deadline=15,serviceMode='advantage'}={}){
  if(!popChoices.includes(growth)||!routes.includes(route)||!['tree','ring','mesh'].includes(graph)||!Number.isInteger(maxNodes)||maxNodes<1||maxNodes>24)throw Error('bad configuration');
  if(!['advantage','parity','reverse'].includes(serviceMode))throw Error('bad serviceMode');this.serviceMode=serviceMode;this.growth=growth;this.route=route;this.graph=graph;this.feedback=feedback;this.maxNodes=maxNodes;this.dt=dt;this.hopDelay=hopDelay;this.deadline=deadline;
  this.t=0;this.workers=[];this.jobs=new Map();this.completed=[];this.created=0;this.done=0;this.parts=0;this.finishedParts=0;this.spawnCount=0;this.retireCount=0;this.workerSeconds=0;this.transfers=0;this.hops=0;this.mismatchedRoles=0;this.lastGrow=-1e3;this.lastRetire=-1e3;this.coolSince=null;
  this.rr=0;this.arrivals=[];this.learned={};this.learningUpdates=0;this.weight=[0,0,0];this.trainingTrace=[];
  this.spawn('general');if(growth==='fixed4')while(this.workers.length<Math.min(4,maxNodes))this.spawn('general');
  if(growth==='specialists4')for(let role of roles)if(this.workers.length<maxNodes)this.spawn(role);
 }
 cost(role,type){return this.serviceMode==='parity'?1:this.serviceMode==='reverse'?(role==='general'?1:role===type?2:3):service(role,type);}
 spawn(role){if(this.workers.length>=this.maxNodes)return null;const id=this.created++, w={id,role,engine:this.feedback==='original'?new RippleNeuron():new ControlledNeuron(this.feedback).n,controller:this.feedback==='original'?null:new ControlledNeuron(this.feedback),queue:[],partial:null,remaining:0,completed:0,eventCount:0,lastObserved:0,startedAt:this.t};
  // Each clone's active kernel is its own independent instance.
  if(w.controller)w.engine=w.controller.n;
  this.workers.push(w);this.spawnCount++;return w;}
 load(w){return (w.partial?w.remaining:0)+w.queue.reduce((n,p)=>n+this.cost(w.role,p.type),0);}
 distance(id){const ids=this.workers.map(x=>x.id);if(id===0)return 0;if(this.graph==='mesh')return 1;if(this.graph==='ring'){let p=ids.indexOf(id);return Math.min(p,ids.length-p);}
  return Math.floor(Math.log2(id+1)); // tree path depth in static birth-ID heap, approximate after retirement.
 }
 submit(type,items,at=this.t){if(!roles.includes(type)||!Array.isArray(items)||!items.length)throw Error('bad submit');
  const id=this.jobs.size+this.completed.length;const size=Math.ceil(items.length/4);let chunks=[];
  for(let p=0;p<4;p++){const v=items.slice(p*size,(p+1)*size);if(v.length)chunks.push({id,part:p,type,items:v,created:at,readyAt:at,weights:[...this.weight]});}
  this.jobs.set(id,{id,type,items,expected:calc.reference(type,items,this.weight),created:at,parts:chunks.length,answers:new Map(),weights:[...this.weight]});this.arrivals.push({t:at,units:chunks.length*2});
  chunks.forEach(c=>this.assign(c));this.parts+=chunks.length;return id;
 }
 predictService(w,type){const key=w.role+':'+type, data=this.learned[key];return data?data.mean:2.0;}
 assign(part){const ws=this.workers;let chosen;
  if(this.route==='roundrobin'){chosen=ws[this.rr++%ws.length];}
  else {
   const ranked=ws.map(w=>{
    const dur=this.route==='learned'?this.predictService(w,part.type):this.cost(w.role,part.type);
    const queueCost=this.route==='leastqueue'?w.queue.length+(w.partial?1:0):this.load(w);
    let score=queueCost+dur;
    if(this.route==='affinity'&&w.role===part.type)score-=2;
    if(this.route==='learned')score+=this.distance(w.id)*.1;
    return {w,score};
   });
   ranked.sort((a,b)=>a.score-b.score||a.w.id-b.w.id);chosen=ranked[0].w;
  }
  const hops=this.distance(chosen.id);part.readyAt=Math.max(this.t,part.readyAt)+hops*this.hopDelay;
  this.hops+=hops;if(chosen.id!==0)this.transfers++;
  chosen.queue.push(part);
 }
 scale(){if(['single','fixed4','specialists4'].includes(this.growth))return;
  this.arrivals=this.arrivals.filter(x=>x.t>=this.t-10);
  const queued=this.workers.reduce((a,w)=>a+this.load(w),0);
  const incoming=this.arrivals.reduce((a,o)=>a+o.units,0)/10;
  let desired;
  if(this.growth==='v2-heuristic')desired=Math.ceil((incoming+queued/12)/.684);
  else {
   const avgFreq=this.workers.reduce((s,w)=>{
    const n=w.engine;let predicted=analyticFrequency(.7,n.theta);
    // Blend with observed rate only after enough exposure to active demand.
    return s+Math.max(.25,Math.min(2, w.eventCount>=4?.5*predicted+.5*n.rate:predicted));
   },0)/this.workers.length;
   const budget=Math.max(.25,avgFreq*.7); // keep simulated utilization <= 70%
   desired=Math.ceil(Math.max(incoming/budget,queued/(this.deadline*budget)));
  }
  desired=Math.max(1,Math.min(this.maxNodes,desired));
  if(desired>this.workers.length&&this.t-this.lastGrow>=1){
   const c=Math.min(2,desired-this.workers.length);for(let i=0;i<c;i++){
    let role='general';if(this.growth==='capacity-specialist'){
      const demand=Object.fromEntries(roles.map(r=>[r,0]));
      for(const w of this.workers){if(w.partial)demand[w.partial.type]+=w.remaining;for(const x of w.queue)demand[x.type]+=this.cost(w.role,x.type);}
      role=[...roles].sort((a,b)=>demand[b]-demand[a])[0]; // sorts fixed type array, only inside scale pass
    }
    const nw=this.spawn(role);
    if(nw){const donors=[...this.workers].filter(x=>x.id!==nw.id).sort((a,b)=>this.load(b)-this.load(a));const donor=donors[0];
      const transferable=donor.queue.filter(x=>x.type===role||role==='general');
      for(let j=0;j<Math.floor(transferable.length/2);j++){
        const c=transferable[j];donor.queue.splice(donor.queue.indexOf(c),1);this.assign(c);
      }
    }
   }this.lastGrow=this.t;
  }
  if(desired<this.workers.length&&queued<=this.workers.length){if(this.coolSince===null)this.coolSince=this.t;
   if(this.t-this.coolSince>=10&&this.t-this.lastRetire>=4){const candidates=this.workers.filter(w=>w.id!==0&&!w.partial&&w.queue.length===0);
    if(candidates.length){candidates.sort((a,b)=>b.id-a.id);this.workers.splice(this.workers.indexOf(candidates[0]),1);this.retireCount++;this.lastRetire=this.t;}}
  }else this.coolSince=null;
 }
 step(){this.t=Math.round((this.t+this.dt)*1000000)/1000000;
  if(Math.abs(this.t-Math.round(this.t))<this.dt/2)this.scale();
  this.workerSeconds+=this.workers.length*this.dt;
  for(const w of this.workers){
   if(!w.partial&&w.queue.length&&w.queue[0].readyAt<=this.t){w.partial=w.queue.shift();w.remaining=this.cost(w.role,w.partial.type);}
   const active=!!w.partial;const out=w.controller?w.controller.step(active?[.35,0,0]:[0,0,0],this.dt):w.engine.step(active?[.35,0,0]:[0,0,0],this.dt);
   w.eventCount+=out.count;
   for(let k=0;k<out.count&&w.partial;k++){
    w.remaining--;if(w.remaining>0)continue;
    const p=w.partial,wrole=w.role;w.completed++;this.finishedParts++;
    const key=wrole+':'+p.type,obs=this.learned[key];const cost=this.cost(wrole,p.type);
    this.learned[key]={mean:obs?.mean*.8+.2*cost||cost,n:(obs?.n||0)+1};this.learningUpdates++;
    const job=this.jobs.get(p.id);if(!job||job.answers.has(p.part))throw Error('work integrity');
    const answer=p.type==='study'?calc.studyStats(p.items):calc.reference(p.type,p.items,p.weights);
    job.answers.set(p.part,answer);w.partial=null;
    if(job.answers.size===job.parts)this.finish(job);
   }
  }
 }
 finish(job){const entries=[...job.answers.entries()].sort((a,b)=>a[0]-b[0]).map(x=>x[1]);let answer;
  if(job.type==='learning'){
   let total=entries.reduce((s,x)=>s+x.n,0),gradient=Array(this.weight.length).fill(0),loss=0;
   for(const p of entries){for(let k=0;k<gradient.length;k++)gradient[k]+=p.gradient[k];loss+=p.loss;}
   gradient=gradient.map(g=>g/total);
   answer={gradient,loss:loss/total,n:total,usedWeights:job.weights};
   const exp=job.expected;for(let k=0;k<gradient.length;k++)if(Math.abs(gradient[k]-exp.gradient[k]/total)>1e-11)throw Error('gradient mismatch');
   // Reject stale gradients if requests overlap; this is safer than silently applying out-of-order updates.
   if(job.weights.some((x,k)=>x!==this.weight[k]))answer.stale=true;
   else{const lr=.35;this.weight=this.weight.map((w,k)=>w-lr*gradient[k]);this.trainingTrace.push({t:this.t,loss:answer.loss,weights:[...this.weight]});}
  }else if(job.type==='product'){
   answer=entries.reduce((o,p)=>({revenue:o.revenue+p.revenue,cost:o.cost+p.cost,quantity:o.quantity+p.quantity,shortfall:o.shortfall+p.shortfall}),{revenue:0,cost:0,quantity:0,shortfall:0});
   for(const k of ['revenue','cost','quantity','shortfall'])if(answer[k]!==job.expected[k])throw Error('product mismatch');
  }else{
   answer=calc.studyCombine(entries);
   const exp=job.expected;
   if(Math.abs(answer.mean-exp.mean)>1e-10||answer.duplicateEvidence!==exp.duplicateEvidence||answer.evidenceIds.join('|')!==exp.evidenceIds.join('|'))throw Error('evidence mismatch');
  }
  this.completed.push({id:job.id,type:job.type,latency:this.t-job.created,answer});this.jobs.delete(job.id);this.done++;
 }
 run(seconds,arrivals){let idx=0;while(this.t<seconds-1e-9){while(idx<arrivals.length&&arrivals[idx].t<=this.t+1e-9){const a=arrivals[idx++];this.submit(a.type,a.items,a.t);}this.step();}
  return this.summary();}
 summary(){const l=this.completed.map(x=>x.latency);const byType=Object.fromEntries(roles.map(type=>[type,this.completed.filter(x=>x.type===type).length]));
  return {growth:this.growth,route:this.route,graph:this.graph,feedback:this.feedback,serviceMode:this.serviceMode,submitted:this.done+this.jobs.size,completed:this.done,pending:this.jobs.size,partsFinished:this.finishedParts,spawns:this.spawnCount,retirements:this.retireCount,remaining:this.workers.length,
   workerSeconds:+this.workerSeconds.toFixed(2),p95Latency:quantile(l,.95),avgLatency:l.length?l.reduce((a,b)=>a+b,0)/l.length:null,transfers:this.transfers,logicalHops:this.hops,learningUpdates:this.learningUpdates,weights:this.weight,byType};}
}
function workloads(profile){const out=[];const trainingRows=calc.makeLearning(220);
 for(let t=0;t<110;t+=1){
  let types=[];
  if(profile==='balanced')types=t%4===0?['learning','product','study']:t%3===0?['product']:[];
  if(profile==='learning')types=t%2===0?['learning']:t%7===0?['product']:[];
  if(profile==='product')types=t%2===0?['product']:t%9===0?['study']:[];
  if(profile==='study')types=t%2===0?['study']:t%9===0?['learning']:[];
  if(profile==='shift')types=t<55?(t%2===0?['learning']:[]):(t%2===0?['product','study']:[]);
  if(profile==='burst')types=(t<10||t>=50&&t<60)?['learning','product','study']:[];
  for(const ty of types){const seed=out.length;let items=ty==='learning'?Array.from({length:20},(_,i)=>({...trainingRows[(seed*19+i)%trainingRows.length]})):ty==='product'?calc.makeProduct(seed,12):calc.makeStudy(seed,12);
   out.push({t,type:ty,items});}
 }
 return out;
}
module.exports={roles,popChoices,routes,service,SpecialistColony,workloads};
