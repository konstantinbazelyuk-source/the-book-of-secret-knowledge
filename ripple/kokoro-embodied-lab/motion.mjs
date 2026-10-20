/** Deterministic, frame-driven planar skeletal motion. Coordinates in canvas pixels. */
export const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const V=(x,y)=>({x,y}),add=(a,b)=>V(a.x+b.x,a.y+b.y),sub=(a,b)=>V(a.x-b.x,a.y-b.y),scale=(a,s)=>V(a.x*s,a.y*s),length=a=>Math.hypot(a.x,a.y),distance=(a,b)=>length(sub(a,b));
export function solveTwoBone(root,target,l1,l2,bend=1){
 if(![root.x,root.y,target.x,target.y,l1,l2,bend].every(Number.isFinite)||l1<=0||l2<=0)throw Error('invalid IK input');
 const v=sub(target,root),d=length(v),dir=d>1e-8?scale(v,1/d):V(1,0);
 const min=Math.abs(l1-l2)+1e-6,max=l1+l2-1e-6,reachable=clamp(d,min,max);
 const end=add(root,scale(dir,reachable)),projection=(l1*l1+reachable*reachable-l2*l2)/(2*reachable);
 const h=Math.sqrt(Math.max(0,l1*l1-projection*projection));
 const perpendicular=V(-dir.y,dir.x);
 const elbow=add(add(root,scale(dir,projection)),scale(perpendicular,h*(bend>=0?1:-1)));
 return {joint:elbow,end,reachable:d>=min&&d<=max,requested:target};
}
export function criticallyDamped(current,target,velocity,dt,omega=12){
 if(![current,target,velocity,dt,omega].every(Number.isFinite)||dt<0||omega<=0)throw Error('invalid dynamics');
 // Stable exact critically damped spring update for constant target over dt.
 const e=Math.exp(-omega*dt),offset=current-target,temp=(velocity+omega*offset)*dt;
 return {value:target+(offset+temp)*e,velocity:(velocity-omega*temp)*e};
}
export class Controller{
 constructor(){this.behavior='idle';this.intensity=.55;this.speed=1;this.speaking=false}
}
export class Rig{
 constructor(){this.x=500;this.y=400;this.motion=0;this.velocity=0;this.lastT=0}
 pose(t,dt,c){
  const amp=clamp(c.intensity,0,1),rate=clamp(c.speed,.1,3);
  const phase=t*rate,breath=Math.sin(phase*2*Math.PI*.22)*5*amp,sway=Math.sin(phase*2*Math.PI*.14)*12*amp;
  const hip=V(this.x+sway,this.y+95-breath),neck=V(hip.x,hip.y-205),head=V(neck.x,neck.y-72);
  const leftShoulder=V(neck.x-38,neck.y+15),rightShoulder=V(neck.x+38,neck.y+15);
  const action={idle:[.1,.1],greet:[.85,.1],explain:[.7,.55],listen:[.1,.3],celebrate:[1,1]}[c.behavior]||[.1,.1];
  const wave=Math.sin(phase*2*Math.PI*1.2)*40*amp;
  const lt=V(leftShoulder.x-100-action[0]*70,leftShoulder.y+135-action[0]*190+wave*action[0]);
  const rt=V(rightShoulder.x+100+action[1]*70,rightShoulder.y+135-action[1]*190-wave*action[1]);
  const L=solveTwoBone(leftShoulder,lt,120,115,-1),R=solveTwoBone(rightShoulder,rt,120,115,1);
  const leftKnee=V(hip.x-37,hip.y+125),rightKnee=V(hip.x+37,hip.y+125);
  const leftFoot=V(hip.x-45,685),rightFoot=V(hip.x+45,685);
  // Speaking movement is an intentionally approximate envelope, not phoneme alignment.
  const mouth=c.speaking?clamp(.2+.65*Math.abs(Math.sin(t*17)+.22*Math.sin(t*31)),0,1):0;
  const blink=Math.sin(t*.9)> .985;
  return {hip,neck,head,leftShoulder,rightShoulder,leftElbow:L.joint,rightElbow:R.joint,leftHand:L.end,rightHand:R.end,leftKnee,rightKnee,leftFoot,rightFoot,mouth,blink};
 }
}
