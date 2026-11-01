// Experimental colony orchestration: NOT part of the original Ripple kernel.
// Single-process, simulated-time colony with deterministic, real arithmetic work.
// No network, model inference, hardware, or concurrent threads.
class RippleMycelium {
  constructor({maxNodes=12, dt=0.05, scale=true, routing=true}={}) {
    if(!Number.isInteger(maxNodes)||maxNodes<1||maxNodes>128) throw Error('maxNodes must be 1..128');
    if(!Number.isFinite(dt)||dt<=0||dt>0.5) throw Error('dt must be (0, 0.5]');
    this.maxNodes=maxNodes; this.dt=dt; this.scaling=scale; this.routing=routing;
    this.t=0; this.nodes=new Map(); this.nextId=0; this.nextJobId=0;
    this.jobs=new Map(); this.finished=new Map(); this.arrivals=[];
    this.inCount=0; this.outCount=0; this.workDone=0; this.totalArrivedUnits=0; this.relayCount=0;
    this.spawns=0; this.retirements=0; this.scaleEvents=[]; this.log=[];
    this.lowSince=null; this.lastGrow=-100; this.lastShrink=-100;
    this.lastControl=-1; this.lastRoute=-1;
    this.spawn(null);
  }
  spawn(parentId){
    if(this.nodes.size>=this.maxNodes) return null;
    const id=this.nextId++;
    // A clone inherits the mathematical model, not its parent's transient state.
    const n={id, parent:parentId, neuron:new RippleNeuron(), queue:[], peers:new Set(), completed:0, pulses:0};
    this.nodes.set(id,n);
    if(parentId!==null){
      const p=this.nodes.get(parentId);
      if(!p)throw Error('missing parent');
      n.peers.add(parentId);p.peers.add(id);
    }
    this.spawns++; this.scaleEvents.push({t:this.t,type:'spawn',id,parent:parentId});
    if(this.scaleEvents.length>120) this.scaleEvents.shift();
    return n;
  }
  submit(payload){
    if(!Array.isArray(payload)||!payload.length||payload.some(x=>!Number.isSafeInteger(x)))throw Error('nonempty safe-integer payload required');
    if(payload.length>256)throw Error('payload must have <=256 integers');
    const id=this.nextJobId++;
    const parts=[];
    const length=Math.ceil(payload.length/4);
    for(let p=0;p<4;p++){
      const chunk=payload.slice(p*length,(p+1)*length);
      if(chunk.length)parts.push({job:id,part:parts.length,values:chunk});
    }
    const expected={sum:payload.reduce((a,x)=>a+x,0),sumsq:payload.reduce((a,x)=>a+x*x,0)};
    this.jobs.set(id,{expected, total:parts.length, partials:new Map(),created:this.t});
    const root=this.nodes.get(0); if(!root)throw Error('root unavailable');
    for(const part of parts)root.queue.push(part);
    this.inCount++;this.totalArrivedUnits+=parts.length;this.arrivals.push({time:this.t,count:parts.length});
    return id;
  }
  submitSyntheticJob(){
    const id=this.nextJobId;
    return this.submit(Array.from({length:32},(_,i)=>((id*17+i*13)%97)-48));
  }
  pending(){return [...this.nodes.values()].reduce((a,n)=>a+n.queue.length,0);}
  // Local, one-hop workload transport along actual graph edges.
  spread(){
    if(!this.routing)return;
    // More than one pass allows a branch to relay through intermediary nodes.
    for(let pass=0;pass<2;pass++){
      const nodes=[...this.nodes.values()].sort((a,b)=>b.queue.length-a.queue.length||a.id-b.id);
      for(const n of nodes){
        if(n.queue.length<2)continue;
        const peers=[...n.peers].map(id=>this.nodes.get(id)).filter(Boolean).sort((a,b)=>a.queue.length-b.queue.length||a.id-b.id);
        const dest=peers[0];
        if(dest && n.queue.length>dest.queue.length+1){
          // Move the task, never duplicate it; ownership is exclusive.
          dest.queue.push(n.queue.shift());this.relayCount++;
        }
      }
    }
  }
  // Quiescent workers only retire; non-idle workers keep pending work.
  retireOne(){
    const candidates=[...this.nodes.values()].filter(n=>n.id!==0)
      .sort((a,b)=>a.queue.length-b.queue.length||b.id-a.id);
    const node=candidates[0]; if(!node)return false;
    const destination=this.nodes.get(node.parent)??this.nodes.get(0);
    destination.queue.push(...node.queue);
    for(const peerId of node.peers){const peer=this.nodes.get(peerId);if(peer)peer.peers.delete(node.id);}
    // Reconnect grandchildren to the retiring node's former parent.
    for(const n of this.nodes.values())if(n.parent===node.id){
      n.parent=destination.id;n.peers.add(destination.id);destination.peers.add(n.id);
    }
    this.nodes.delete(node.id);this.retirements++;
    this.scaleEvents.push({t:this.t,type:'retire',id:node.id,parent:destination.id});
    if(this.scaleEvents.length>120)this.scaleEvents.shift();
    return true;
  }
  control(){
    const horizon=10, cutoff=this.t-horizon;
    this.arrivals=this.arrivals.filter(a=>a.time>cutoff);
    const incoming=this.arrivals.reduce((a,x)=>a+x.count,0)/Math.min(horizon,Math.max(1,this.t));
    const queue=this.pending();
    // PROPOSED controller: capacity estimate=0.95 completed chunks/s/active neuron.
    // 72% utilization goal plus 12-second queue drainage pressure.
    const recommended=Math.max(1,Math.min(this.maxNodes,Math.ceil((incoming+queue/12)/(0.95*0.72))));
    if(!this.scaling)return;
    if(recommended>this.nodes.size && this.t-this.lastGrow>=1-1e-8){
      const growBy=Math.min(2,recommended-this.nodes.size);
      for(let i=0;i<growBy;i++){
        const busy=[...this.nodes.values()].sort((a,b)=>b.queue.length-a.queue.length||a.id-b.id)[0];
        const newNode=this.spawn(busy.id);
        if(newNode){
          // Keep original in-place, hand ownership of some queued work to child.
          const transfer=Math.floor(busy.queue.length/2);
          newNode.queue.push(...busy.queue.splice(0,transfer));
        }
      }
      this.lastGrow=this.t;
    }
    if(recommended<this.nodes.size && queue<=this.nodes.size){
      if(this.lowSince===null)this.lowSince=this.t;
      if(this.t-this.lowSince>=15 && this.t-this.lastShrink>=5){
        if(this.retireOne())this.lastShrink=this.t;
      }
    }else this.lowSince=null;
  }
  // The exact original neuron.step determines a worker's firing events.
  step(){
    this.t=+(this.t+this.dt).toFixed(8);
    const oneSec=Math.round(this.t);
    if(Math.abs(this.t-oneSec)<this.dt/2 && oneSec!==this.lastControl){
      this.lastControl=oneSec; this.control();
    }
    const half=Math.round(this.t*2)/2;
    if(Math.abs(this.t-half)<this.dt/2 && half!==this.lastRoute){this.spread();this.lastRoute=half;}
    for(const node of this.nodes.values()){
      const active=node.queue.length>0;
      const red=active?0.35:0;
      // All work signaling on the standard R channel; G/B unused in v0.1 colony.
      // Original RGB weights and membrane equation are not modified.
      const firing=node.neuron.step([red,0,0],this.dt);
      node.pulses+=firing.count;
      for(let i=0;i<firing.count && node.queue.length;i++){
        const unit=node.queue.shift();
        const s=unit.values.reduce((a,v)=>a+v,0);
        const sq=unit.values.reduce((a,v)=>a+v*v,0);
        const job=this.jobs.get(unit.job);
        if(!job)throw Error('orphan chunk');
        if(job.partials.has(unit.part))throw Error('duplicate chunk');
        job.partials.set(unit.part,{sum:s,sumsq:sq,worker:node.id});
        node.completed++;this.workDone++;
        if(job.partials.size===job.total){
          const all=[...job.partials.values()];
          const actual={sum:all.reduce((a,v)=>a+v.sum,0),sumsq:all.reduce((a,v)=>a+v.sumsq,0)};
          if(actual.sum!==job.expected.sum||actual.sumsq!==job.expected.sumsq)throw Error('integrity failure');
          this.finished.set(unit.job,{...actual,latency:this.t-job.created,workers:[...new Set(all.map(x=>x.worker))]});
          this.jobs.delete(unit.job);this.outCount++;
        }
      }
    }
  }
  assertIntegrity(){
    const workQueued=[...this.nodes.values()].reduce((a,n)=>a+n.queue.length,0);
    const workPartial=[...this.jobs.values()].reduce((a,j)=>a+j.partials.size,0);
    const workFinished=[...this.finished.values()].length;
    if(this.inCount!==this.outCount+this.jobs.size)throw Error('jobs vanished or duplicated');
    if(workQueued+this.workDone!==this.totalArrivedUnits){
      // The completed count already contains partials and completed jobs.
      throw Error('unit accounting failure');
    }
    if(this.nodes.size<1||this.nodes.size>this.maxNodes)throw Error('population limit violated');
    for(const n of this.nodes.values())for(const peer of n.peers){
      if(!this.nodes.has(peer)||!this.nodes.get(peer).peers.has(n.id))throw Error('unpaired link');
    }
    return {queued:workQueued,partials:workPartial,finished:workFinished};
  }
  snapshot(){
    return {time:+this.t.toFixed(2),nodes:this.nodes.size,queued:this.pending(),completedJobs:this.outCount,
      submittedJobs:this.inCount,completedChunks:this.workDone,relays:this.relayCount,
      spawns:this.spawns,retirements:this.retirements,edges:[...this.nodes.values()].flatMap(n=>[...n.peers].filter(p=>p>n.id).map(p=>[n.id,p])),
      workers:[...this.nodes.values()].map(n=>({id:n.id,parent:n.parent,queued:n.queue.length,done:n.completed,pulses:n.pulses,rate:+n.neuron.rate.toFixed(3),theta:+n.neuron.theta.toFixed(3)}))};
  }
}
if(typeof module!=='undefined'&&module.exports) module.exports={RippleMycelium};
