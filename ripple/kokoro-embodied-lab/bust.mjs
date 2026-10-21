/** Kokoro bust: 3D anisotropic Gaussian primitives, deformation and projection. */
import {perspective,rotateAxis} from './xyz.mjs';
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
export function createBust({rings=24,slices=48}={}){
 if(!Number.isInteger(rings)||!Number.isInteger(slices)||rings<8||slices<12)throw RangeError('invalid bust resolution');
 const out=[];
 function ellipsoid(part,center,radii,countR,countS,color){
  for(let i=1;i<countR;i++){const theta=Math.PI*i/countR;
   for(let j=0;j<countS;j++){const phi=2*Math.PI*j/countS;
    const xyz=[center[0]+radii[0]*Math.sin(theta)*Math.cos(phi),center[1]+radii[1]*Math.cos(theta),center[2]+radii[2]*Math.sin(theta)*Math.sin(phi)];
    out.push({part,rest:xyz,radius:Math.min(...radii)*.10,color});
   }
  }
 }
 ellipsoid('head',[0,1.65,0],[.34,.46,.31],rings,slices,[239,189,204]);
 ellipsoid('neck',[0,1.10,0],[.16,.24,.15],12,24,[219,173,192]);
 ellipsoid('shoulders',[0,.82,0],[.67,.25,.28],16,36,[116,142,197]);
 // Facial features on the +Z facing surface.
 for(const side of [-1,1]){
  ellipsoid('eye'+side,[side*.145,1.71,.293],[.069,.046,.022],8,16,[57,78,112]);
  ellipsoid('iris'+side,[side*.145,1.71,.316],[.027,.035,.012],8,16,[112,202,208]);
  ellipsoid('brow'+side,[side*.145,1.805,.295],[.093,.015,.019],6,14,[83,66,88]);
 }
 ellipsoid('nose',[0,1.57,.329],[.065,.09,.052],8,16,[226,166,181]);
 ellipsoid('upperLip',[0,1.425,.294],[.125,.023,.023],7,24,[163,73,108]);
 ellipsoid('lowerLip',[0,1.393,.296],[.123,.025,.023],7,24,[163,73,108]);
 return out;
}
export function deformBust(primitives,time,{yaw=0,pitch=0,gazeX=0,gazeY=0,mouth=0,blink=0}={}){
 if(![time,yaw,pitch,gazeX,gazeY,mouth,blink].every(Number.isFinite))throw TypeError('nonfinite pose');
 const m=clamp(mouth,0,1),b=clamp(blink,0,1),gX=clamp(gazeX,-1,1),gY=clamp(gazeY,-1,1);
 return primitives.map(p=>{
  const pos=p.rest.slice();let ry=p.radius;
  if(p.part==='lowerLip')pos[1]-=.075*m;
  if(p.part==='upperLip')pos[1]+=.012*m;
  if(p.part.startsWith('eye')||p.part.startsWith('iris')){pos[1]=1.71+(pos[1]-1.71)*(1-.94*b)}
  if(p.part.startsWith('iris')){pos[0]+=.026*gX;pos[1]+=.019*gY}
  if(p.part==='head'||p.part.startsWith('eye')||p.part.startsWith('iris')||p.part==='nose'||p.part.includes('Lip')||p.part.startsWith('brow')){
   const pivot=[0,1.18,0];let q=[pos[0]-pivot[0],pos[1]-pivot[1],pos[2]-pivot[2]];
   q=rotateAxis(q,[0,1,0],yaw);q=rotateAxis(q,[1,0,0],pitch);pos[0]=q[0]+pivot[0];pos[1]=q[1]+pivot[1];pos[2]=q[2]+pivot[2];
  }
  if(p.part==='shoulders')pos[1]+=.006*Math.sin(time*1.6);
  return {...p,position:pos,radius:ry};
 });
}
export function projectGaussians(primitives,camera){
 const projected=[];
 for(const p of primitives){
  const v=perspective(p.position,camera);if(!v)continue;
  // Pixel-space kernel width is proportional to 3D primitive scale / depth.
  const focal=1/Math.tan((camera.fov??55)*Math.PI/360);
  projected.push({...p,screen:v,sigma:Math.max(.0001,p.radius*focal/v.depth)});
 }
 return projected.sort((a,b)=>b.screen.depth-a.screen.depth);
}
export function gaussian2D(dx,dy,sigmaX,sigmaY){
 if(![dx,dy,sigmaX,sigmaY].every(Number.isFinite)||sigmaX<=0||sigmaY<=0)throw RangeError('invalid Gaussian');
 return Math.exp(-.5*((dx/sigmaX)**2+(dy/sigmaY)**2));
}
