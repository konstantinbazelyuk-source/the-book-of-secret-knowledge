// RIPPLE ORIGINAL CORE, VERBATIM (except module export and source header).
// Source: user's original Ripple-Neuron-Simulator.html (v0.1), 2026-10-13.
// Never edit these equations in the mycelium experiment.
const bound=(x,lo,hi)=>Math.max(lo,Math.min(hi,x));
class RippleNeuron{
 constructor(o={}){this.theta=o.theta??0.45;this.adaptive=o.adaptive??true;this.target=o.target??1;this.tauV=.5;this.tauR=5;this.refractory=.1;this.eta=.08;this.lo=.15;this.hi=2.5;this.t=0;this.u=0;this.rate=0;this.rest=0;}
 step(x,dt){if(x.length!==3||x.some(v=>!Number.isFinite(v))||!Number.isFinite(dt)||dt<=0||dt>.5)throw Error('Invalid input or elapsed time');x=x.map(v=>bound(v,0,1));const drive=2*x[0]+1.2*x[1]-1.4*x[2],start=this.t,events=[];let elapsed=0;
  while(elapsed<dt-1e-12){const left=dt-elapsed;if(this.rest>1e-12){let held=Math.min(left,this.rest);this.rest=Math.max(0,this.rest-held);this.u=0;elapsed+=held;continue;}let crossing=Infinity;if(this.u>=this.theta)crossing=0;else if(drive>this.theta)crossing=this.tauV*Math.log((drive-this.u)/(drive-this.theta));if(crossing<=left+1e-12){elapsed+=Math.max(0,Math.min(left,crossing));events.push(start+elapsed);this.u=0;this.rest=this.refractory;}else{this.u=Math.max(0,drive+(this.u-drive)*Math.exp(-left/this.tauV));elapsed=dt;}}
  const decay=Math.exp(-dt/this.tauR);let integral=this.rate*this.tauR*(1-decay);this.rate*=decay;for(const event of events){const d=Math.exp(-(start+dt-event)/this.tauR);this.rate+=d/this.tauR;integral+=1-d;}if(this.adaptive)this.theta=bound(this.theta+this.eta*(integral-this.target*dt),this.lo,this.hi);this.t=start+dt;return{t:this.t,u:this.u,theta:this.theta,rate:this.rate,drive,count:events.length,events};}
 attainable(drive){if(drive<=0)return false;const th=drive*(1-Math.exp(-(1/this.target-this.refractory)/this.tauV));return this.lo<=th&&th<=this.hi;}
}
if (typeof module !== 'undefined' && module.exports) module.exports = {RippleNeuron, bound};
