/** Ripple Embodied control primitives: deterministic state-space control and motion planning. */
export const bound=(x,a,b)=>Math.max(a,Math.min(b,x));
export function finite(...xs){if(!xs.every(Number.isFinite))throw new TypeError('non-finite control input')}
export function smoothstep(x){finite(x);const t=bound(x,0,1);return t*t*(3-2*t)}
export function quintic(x){finite(x);const t=bound(x,0,1);return t*t*t*(10+t*(-15+6*t))}
export function shortestAngle(a,b){finite(a,b);return Math.atan2(Math.sin(b-a),Math.cos(b-a))}
export function stepServo(state,target,dt,{omega=9,maxVelocity=260,maxAcceleration=1500}={}){
 finite(state.position,state.velocity,target,dt,omega,maxVelocity,maxAcceleration);
 if(dt<0||omega<=0||maxVelocity<=0||maxAcceleration<=0)throw RangeError('invalid servo bounds');
 if(dt===0)return {...state};
 // Stable semi-implicit integration with substeps to bound frame-time variability.
 let x=state.position,v=state.velocity;
 const steps=Math.max(1,Math.ceil(dt/(1/120))),h=dt/steps;
 for(let i=0;i<steps;i++){
   const acceleration=bound(omega*omega*(target-x)-2*omega*v,-maxAcceleration,maxAcceleration);
   v=bound(v+acceleration*h,-maxVelocity,maxVelocity);
   x+=v*h;
 }
 return {position:x,velocity:v};
}
export function planMinimumJerk(from,to,t,duration){
 finite(from,to,t,duration);if(duration<=0)throw RangeError('duration must be positive');
 return from+(to-from)*quintic(t/duration);
}
export function contactError(foot,groundY){
 finite(foot.x,foot.y,groundY);
 return Math.max(0,foot.y-groundY);
}
export function correctGroundPenetration(foot,groundY){
 const error=contactError(foot,groundY);
 return {foot:{x:foot.x,y:foot.y-error},penetration:error};
}
export function adaptiveBehaviorWeights(weights,losses,learningRate=.02){
 if(!Array.isArray(weights)||!Array.isArray(losses)||weights.length!==losses.length||weights.length===0)throw TypeError('aligned arrays required');
 finite(learningRate,...weights,...losses);
 if(learningRate<0||learningRate>1||weights.some(w=>w<0)||losses.some(l=>l<0))throw RangeError('invalid weights or losses');
 // Multiplicative weights: w_i' proportional to w_i exp(-eta * loss_i).
 const updated=weights.map((w,i)=>w*Math.exp(-learningRate*losses[i]));
 const sum=updated.reduce((a,b)=>a+b,0);
 if(sum<=0||!Number.isFinite(sum))throw RangeError('degenerate weights');
 return updated.map(w=>w/sum);
}
export function scoreMotion(samples,{smoothness=1,penetration=10,target=1}={}){
 if(!Array.isArray(samples)||samples.length<3)throw TypeError('three or more samples required');
 finite(smoothness,penetration,target);
 let jerkPenalty=0,groundPenalty=0,targetPenalty=0;
 for(let i=0;i<samples.length;i++){
  const s=samples[i];finite(s.position,s.target,s.penetration);
  targetPenalty+=(s.position-s.target)**2;
  groundPenalty+=s.penetration**2;
  if(i>=3){
   const p=samples;const j=p[i].position-3*p[i-1].position+3*p[i-2].position-p[i-3].position;
   jerkPenalty+=j*j;
  }
 }
 return {total:smoothness*jerkPenalty+penetration*groundPenalty+target*targetPenalty,jerkPenalty,groundPenalty,targetPenalty};
}
