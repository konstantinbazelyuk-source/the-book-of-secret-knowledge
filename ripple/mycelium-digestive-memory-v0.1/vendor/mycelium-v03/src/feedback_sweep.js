'use strict';
const fs=require('node:fs');const path=require('node:path');
const {RippleNeuron,bound}=require('./ripple_core_reference');
const TAU=.5,REF=.1,LOW=.15,HIGH=2.5;
// Analytic target is achievable only for D>0, 0<target<1/REF,
// and attainable theta in [LOW,HIGH]. Derived from LIF interspike interval.
function feasibleTheta(d,target){
 if(!(d>0&&target>0&&target<1/REF))return null;
 const theta=d*(-Math.expm1(-(1/target-REF)/TAU));
 return theta>=LOW&&theta<=HIGH?theta:null;
}
function analyticFrequency(d,theta){return d<=theta?0:1/(REF+TAU*Math.log(d/(d-theta)));}
const methods=['original','fixed','feedforward-fast','feedforward-slow','hybrid-fast','hybrid-slow','rate-P','rate-PI','predictive-P'];
class ControlledNeuron{
 constructor(method='original',target=1){if(!methods.includes(method))throw Error('method');this.method=method;this.target=target;this.n=new RippleNeuron({target,adaptive:method==='original'});this.integral=0;}
 step(x,dt){
  const n=this.n, out=n.step(x,dt);
  if(this.method==='original'||this.method==='fixed')return out;
  const wanted=feasibleTheta(out.drive,this.target);
  let dth=0,err=n.rate-this.target;
  switch(this.method){
   case 'feedforward-fast':case 'feedforward-slow':{
    if(wanted!==null){let tau=this.method==='feedforward-fast'?.8:4;
     dth=(wanted-n.theta)*(-Math.expm1(-dt/tau));}
    break;
   }
   case 'hybrid-fast':case 'hybrid-slow':{
    if(wanted!==null){let tau=this.method==='hybrid-fast'?.8:4;
     dth=(wanted-n.theta)*(-Math.expm1(-dt/tau)) + .018*dt*err;
    }else dth=.04*dt*err;
    break;
   }
   case 'rate-P': dth=.08*dt*err;break;
   case 'rate-PI':{
    const proposed=bound(this.integral+dt*err,-8,8);
    dth=.08*dt*err+.012*dt*proposed;
    if((n.theta+dth>LOW&&n.theta+dth<HIGH)|| (n.theta<=LOW&&dth>0) || (n.theta>=HIGH&&dth<0))this.integral=proposed;
    break;
   }
   case 'predictive-P': dth=(wanted!==null?.10*(wanted-n.theta)*dt:0)+.06*dt*err;break;
  }
  n.theta=bound(n.theta+dth,LOW,HIGH);
  return out;
 }
}
const profiles={
 'constant-low':t=>.32,
 'constant-mid':t=>.7,
 'constant-high':t=>1.4,
 'constant-bright':t=>2.4,
 'step-up':t=>t<55?.36:1.7,
 'step-down':t=>t<55?2.2:.35,
 'alternate-20s':t=>(Math.floor(t/20)%2?1.8:.4),
 'ramped':t=>.3+1.6*Math.min(1,t/100),
 'sine':t=>1+.6*Math.sin(t/9),
 'dark-interrupt':t=>(t<40||t>=80)?1.2:0,
 'fast-switch':t=>(Math.floor(t/2)%2?1.8:.3),
 'blue-suppressed':t=>t<60? .8:-.2,
};
function driveToInput(d){return d>=0?[bound(d/2,0,1),0,0]:[0,0,bound(-d/1.4,0,1)];}
function evaluate(method,profile,target=1,seconds=150,dt=.05){
 const n=new ControlledNeuron(method,target), windows=[],times=[],wlen=10;let wSpikes=0,wDrives=[],lastCount=0;
 for(let i=0;i<Math.round(seconds/dt);i++){
  const t=i*dt,d=profiles[profile](t),out=n.step(driveToInput(d),dt);
  wSpikes+=out.count;lastCount+=out.count;wDrives.push(out.drive);times.push(...out.events);
  if((i+1)%Math.round(wlen/dt)===0){
   const meanD=wDrives.reduce((a,b)=>a+b,0)/wDrives.length;
   const feasible=feasibleTheta(meanD,target)!==null;
   windows.push({time:t+dt,f: wSpikes/wlen,err:Math.abs(wSpikes/wlen-target),feasible});
   wSpikes=0;wDrives=[];
  }
 }
 const eligible=windows.filter(w=>w.feasible && w.time>=20);
 return {method,profile,target,events:lastCount,mae:eligible.length?+(eligible.reduce((a,b)=>a+b.err,0)/eligible.length).toFixed(6):null,eligibleWindows:eligible.length,
  feasibleSeconds:eligible.length*wlen,theta:+n.n.theta.toFixed(6),finalRate:+n.n.rate.toFixed(6),rateMax:Math.max(...windows.map(x=>x.f)),rateMin:Math.min(...windows.map(x=>x.f)),zeroStimulusEvents:profile==='dark-interrupt'?times.filter(t=>t>=41&&t<80).length:0};
}
function sweep(){const rows=[];for(const m of methods)for(const p of Object.keys(profiles))for(const target of [.5,1,2])rows.push(evaluate(m,p,target));
 const groups=Object.fromEntries(methods.map(m=>[m,{method:m,n:0,mae:0,tailScore:0}]));
 for(const r of rows){if(r.mae===null)continue;groups[r.method].n++;groups[r.method].mae+=r.mae;}
 for(const g of Object.values(groups))g.mae=+(g.mae/g.n).toFixed(6);
 const out=path.resolve(__dirname,'../data');fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'feedback_trials.json'),JSON.stringify(rows,null,2));fs.writeFileSync(path.join(out,'feedback_scores.json'),JSON.stringify(Object.values(groups).sort((a,b)=>a.mae-b.mae),null,2));
 console.log('FEEDBACK_VARIANTS',JSON.stringify(Object.values(groups).sort((a,b)=>a.mae-b.mae)));
 return {rows,groups:Object.values(groups)};
}
if(require.main===module)sweep();module.exports={methods,profiles,ControlledNeuron,feasibleTheta,analyticFrequency,evaluate,sweep};
