/** Kokoro XYZ v0.1 — mathematical 3D rig and point-cloud skinning, no dependencies.
 * Right-handed coordinates: +Y up, camera looks from +Z toward origin.
 * Matrices are column-major 4x4; points are [x,y,z].
 */
export const clamp3=(v,a,b)=>Math.max(a,Math.min(b,v));
export function assertVec(v){if(!Array.isArray(v)||v.length!==3||!v.every(Number.isFinite))throw TypeError('finite XYZ required');return v}
export const add3=(a,b)=>a.map((v,i)=>v+b[i]);
export const sub3=(a,b)=>a.map((v,i)=>v-b[i]);
export const scale3=(a,s)=>a.map(v=>v*s);
export const dot3=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
export const norm3=a=>Math.hypot(...a);
export const cross3=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
export function unit3(a){const n=norm3(a);if(n<1e-10)throw RangeError('zero vector');return scale3(a,1/n)}
export function rotateAxis(point,axis,angle){assertVec(point);assertVec(axis);if(!Number.isFinite(angle))throw TypeError('finite angle required');const u=unit3(axis),c=Math.cos(angle),s=Math.sin(angle);return add3(add3(scale3(point,c),scale3(cross3(u,point),s)),scale3(u,dot3(u,point)*(1-c)))}
export function perspective(point,{eye=[0,1.55,5.5],look=[0,1.3,0],up=[0,1,0],fov=55,aspect=1,near=.05}={}){
 assertVec(point);assertVec(eye);assertVec(look);assertVec(up);
 if(!(fov>1&&fov<179&&aspect>0&&near>0))throw RangeError('invalid camera');
 const forward=unit3(sub3(look,eye)),right=unit3(cross3(forward,up)),vertical=cross3(right,forward),relative=sub3(point,eye),depth=dot3(relative,forward);
 if(depth<=near)return null;
 const f=1/Math.tan(fov*Math.PI/360);
 return {x:f*dot3(relative,right)/(depth*aspect),y:f*dot3(relative,vertical)/depth,depth};
}
export const BONES=[
 ['root',null,[0,1.02,0]],['spine','root',[0,.35,0]],['chest','spine',[0,.32,0]],['neck','chest',[0,.20,0]],['head','neck',[0,.25,0]],
 ['shoulderL','chest',[-.24,.12,0]],['elbowL','shoulderL',[-.31,-.26,0]],['wristL','elbowL',[-.28,-.23,0]],
 ['shoulderR','chest',[.24,.12,0]],['elbowR','shoulderR',[.31,-.26,0]],['wristR','elbowR',[.28,-.23,0]],
 ['hipL','root',[-.15,-.06,0]],['kneeL','hipL',[-.03,-.49,0]],['ankleL','kneeL',[0,-.47,0]],
 ['hipR','root',[.15,-.06,0]],['kneeR','hipR',[.03,-.49,0]],['ankleR','kneeR',[0,-.47,0]]
];
export function skeletonPose(time,behavior='idle',intensity=.6){
 if(!Number.isFinite(time)||!Number.isFinite(intensity))throw TypeError('finite pose arguments required');
 const I=clamp3(intensity,0,1),p=new Map(),joints=[];
 const wave=behavior==='greet'?1:behavior==='celebrate'?.85:behavior==='explain'?.55:0;
 const breath=.014*I*Math.sin(time*1.4),sway=.028*I*Math.sin(time*.8);
 for(const [name,parent,offset] of BONES){
  let local=offset.slice();
  if(name==='root')local[0]+=sway;
  if(name==='chest')local[1]+=breath;
  if(name==='elbowR'){local=rotateAxis(local,[0,0,1],-wave*(.7+.25*Math.sin(time*5)))}
  if(name==='wristR'){local=rotateAxis(local,[0,0,1],-wave*(.8+.25*Math.sin(time*5)))}
  if(name==='elbowL'&&behavior==='celebrate')local=rotateAxis(local,[0,0,1],.85);
  if(name==='wristL'&&behavior==='celebrate')local=rotateAxis(local,[0,0,1],.9);
  const pos=parent?add3(p.get(parent),local):local;
  p.set(name,pos);joints.push({name,parent,position:pos});
 }
 return joints;
}
export function sampleBoneCloud(joints,{rings=5,sides=9,radius=.07}={}){
 if(!Number.isInteger(rings)||!Number.isInteger(sides)||rings<2||sides<3||!(radius>0))throw RangeError('invalid sampling');
 const byName=new Map(joints.map(j=>[j.name,j])),points=[];
 for(const joint of joints){
  if(!joint.parent)continue;
  const start=byName.get(joint.parent)?.position,end=joint.position;
  if(!start)throw Error('missing bone parent');
  const tangent=unit3(sub3(end,start)),reference=Math.abs(tangent[1])<.9?[0,1,0]:[1,0,0],u=unit3(cross3(tangent,reference)),v=cross3(tangent,u);
  const thick=joint.name==='head'?.16:joint.name==='chest'?.18:joint.name==='spine'?.14:radius;
  for(let i=0;i<rings;i++)for(let k=0;k<sides;k++){
   const q=i/(rings-1),a=k*2*Math.PI/sides,center=add3(scale3(start,1-q),scale3(end,q));
   const pos=add3(center,add3(scale3(u,thick*Math.cos(a)),scale3(v,thick*Math.sin(a))));
   points.push({position:pos,bone:joint.name,weight:1,depth:0});
  }
 }
 return points;
}
export function projectCloud(points,camera){
 return points.map(p=>({...p,projected:perspective(p.position,camera)})).filter(p=>p.projected!==null).sort((a,b)=>b.projected.depth-a.projected.depth);
}
