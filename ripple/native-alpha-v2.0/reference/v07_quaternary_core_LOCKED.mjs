/** Ripple Q v0.7: deterministic four-symbol sensor computer.
 * v0.1 Ripple neuron's numerical core is not modified.
 * -0 and +0 are distinct SYMBOLS, not claims about negative electrical zero.
 * Four symbols occupy two conventional bits per symbol.
 */
export const LABELS = Object.freeze(['-1', '-0', '0', '1']);
export const BITS = Object.freeze(['00','01','10','11']);
export const SYMBOL_TO_CODE = Object.freeze({'-1':0,'-0':1,'0':2,'1':3});
export const toSymbol = (code) => LABELS[code];
export const toBits = (code) => {if(!Number.isInteger(code)||code<0||code>3) throw Error('invalid base-4 symbol'); return BITS[code];};
export const fromBits = (bits) => {const n=BITS.indexOf(bits);if(n===-1)throw Error('invalid two-bit symbol');return n;};
export const pack4 = (symbols) => {if(symbols.length!==4||symbols.some(s=>!Number.isInteger(s)||s<0||s>3))throw Error('Expected exactly four base-4 symbols');return symbols.reduce((acc,s)=>(acc<<2)|s,0)};
export const unpack4 = (byte) => {if(!Number.isInteger(byte)||byte<0||byte>255)throw Error('invalid byte');return [6,4,2,0].map(shift=>(byte>>shift)&3);};
export const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
export const intensity = rgb => .2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2];
export const drive = rgb => 2*rgb[0]+1.2*rgb[1]-1.4*rgb[2];

/** 32x32 RGBA central ROI; contrast is scene texture proxy, not mass or atomic density.
 * frameDifference is frame-registered pixel difference; it is NOT full optical flow.
 */
export function frameFeatures(rgba,width=32,height=32,previous=null){
 if(!(rgba instanceof Uint8ClampedArray)&&!(rgba instanceof Uint8Array))throw Error('RGBA byte array required');
 if(width*height*4!==rgba.length||width<2||height<2)throw Error('wrong frame shape');
 const lum = new Float64Array(width*height);const rgb=[0,0,0];let clip=0;
 for(let p=0;p<width*height;p++){
  const i=p*4,r=rgba[i],g=rgba[i+1],b=rgba[i+2];
  rgb[0]+=r;rgb[1]+=g;rgb[2]+=b;lum[p]=(.2126*r+.7152*g+.0722*b)/255;
  if(r>=250||g>=250||b>=250)clip++;
 }
 const n=width*height;for(let i=0;i<3;i++)rgb[i]/=(255*n);
 let edge=0,count=0;
 for(let y=1;y<height-1;y++)for(let x=1;x<width-1;x++){
  const k=y*width+x;
  const gx=(-lum[k-width-1]-2*lum[k-1]-lum[k+width-1]+lum[k-width+1]+2*lum[k+1]+lum[k+width+1])/8;
  const gy=(-lum[k-width-1]-2*lum[k-width]-lum[k-width+1]+lum[k+width-1]+2*lum[k+width]+lum[k+width+1])/8;
  edge+=Math.hypot(gx,gy);count++;
 }
 let frameDifference=null;
 if(previous&&previous.length===n){let s=0;for(let i=0;i<n;i++)s+=Math.abs(lum[i]-previous[i]);frameDifference=s/n;}
 return {rgb,meanLight:intensity(rgb),edgeDensity:count?edge/count:0,frameDifference,clipFraction:clip/n,luminance:lum,
  measured:'display-referred camera pixels',warning:'Edge-density is spatial contrast only; frame difference is not object speed or mass density.'};
}

/** Permissionless capability probes reveal only what a browser exposes.
 * 'Samsung' CPU model/SoC specs cannot generally be determined from a webpage.
 */
export async function deviceProfile(nav=globalThis.navigator||{},win=globalThis){
 const p={platform:nav.userAgentData?.platform||nav.platform||'unknown',model:'not available',
   logicalProcessorHint:Number.isFinite(nav.hardwareConcurrency)?nav.hardwareConcurrency:null,
   approximateDeviceMemoryGB:Number.isFinite(nav.deviceMemory)?nav.deviceMemory:null,
   cameraAPI:!!nav.mediaDevices?.getUserMedia,motionAPI:'DeviceMotionEvent' in win,
   magnetometerAPI:typeof win.Magnetometer==='function',ambientLightAPI:typeof win.AmbientLightSensor==='function',
   secureContext:!!win.isSecureContext,details:'Hardware model, CPU clock and SoC are not available via ordinary browser APIs; hints can be rounded.'};
 if(nav.userAgentData?.getHighEntropyValues){try{const h=await nav.userAgentData.getHighEntropyValues(['model','architecture','platformVersion']);p.model=h.model||'not exposed';p.architecture=h.architecture||'not exposed';p.platformVersion=h.platformVersion||'not exposed';}catch{}}
 return p;
}

// A one-shot bounded CPU measurement only; not an actual SoC benchmark or FLOPS rating.
export function runtimeProbe(loops=100000){
 loops=Math.floor(clamp(loops,1000,1000000));let a=1,b=0;
 const before=performance.now();for(let i=0;i<loops;i++){a=(Math.imul(a,1664525)+1013904223)|0;b^=a>>>10;}
 const elapsed=Math.max(.001,performance.now()-before);
 return {loops,elapsedMs:elapsed,iterationsPerSecond:loops*1000/elapsed,checksum:b|0,note:'JavaScript main-thread loop throughput, not manufacturer processing power.'};
}

/** Temporal machine with noise-adaptive Schmitt thresholds and explicit inhibitory rest.
 * Code order 0=-1 negative change, 1=-0 suppressed/negative-drive rest,
 * 2=0 neutral hold, 3=1 positive change.
 * This coding is engineered; it is not a natural language emerging from a neuron.
 */
export class QuadEncoder{
 constructor(opts={}){this.base=clamp(opts.threshold??.12,.005,2);this.noiseMult=clamp(opts.noiseMult??4,0,20);this.dwell=Math.max(1,Math.min(10,Math.floor(opts.dwell??2)));this.reset();}
 reset(){this.previous=null;this.prevDrive=null;this.referenceDrive=null;this.noise=0;this.pending=null;this.pendingCount=0;this.last=2;this.counts=[0,0,0,0];this.n=0;}
 step(s){
  const d=Number(s.drive);
  if(!Number.isFinite(d))throw Error('input must have finite drive');
  if(this.referenceDrive===null)this.referenceDrive=d;
  const diff=d-this.referenceDrive;
  const threshold=Math.max(this.base,this.noiseMult*this.noise);
  let candidate;
  if(this.prevDrive!==null&&diff>threshold)candidate=3;
  else if(this.prevDrive!==null&&diff<-threshold)candidate=0;
  else if(d< -Math.max(this.base,.04)||s.inhibited===true)candidate=1;
  else candidate=2;
  if(candidate===this.pending)this.pendingCount++;else{this.pending=candidate;this.pendingCount=1;}
  if(this.pendingCount>=this.dwell){
   this.last=candidate;
   // Only a confirmed change updates the reference, so a sustained physical
   // illumination step can pass a two-frame debounce test.
   if(candidate===3||candidate===0)this.referenceDrive=d;
  }
  // Update the noise floor only when the sample is near the existing reference.
  if(this.prevDrive!==null&&Math.abs(diff)<threshold)this.noise=.95*this.noise+.05*Math.abs(d-this.prevDrive);
  this.prevDrive=d;this.n++;this.counts[this.last]++;
  return {code:this.last,label:toSymbol(this.last),bits:toBits(this.last),candidate:toSymbol(candidate),drive:d,diff,threshold,noiseFloor:this.noise,count:this.n};
 }
}

/** Opcode = two base-4 symbols = four binary bits. Supported ISA is intentionally bounded.
 * Programs are authored presets, never arbitrary JavaScript generated by an incoming signal.
 */
export const OPS=Object.freeze([
 'PUSH_R','PUSH_G','PUSH_B','PUSH_DRIVE','PUSH_EDGE','PUSH_FRAME_DIFF','PUSH_ACCEL','PUSH_MAG',
 'PUSH_LUX','PUSH_ZERO','ADD','SUB','MUL','CLAMP01','QUANTIZE','EMIT'
]);
export const opcodeSymbols=op=>{const i=OPS.indexOf(op);if(i<0)throw Error('unknown instruction: '+op);return [(i>>2)&3,i&3];};
export const disassemble = pairs => pairs.map(([a,b])=>OPS[(a<<2)|b]||'INVALID');
export function compile(source){
 const tokens=Array.isArray(source)?source:String(source).split(/[;\n]+/).map(x=>x.trim()).filter(Boolean);
 if(!tokens.length||tokens.length>32)throw Error('Program length must be 1..32 instructions');
 const pairs=tokens.map(opcodeSymbols);
 if(tokens.at(-1)!=='EMIT')throw Error('A program must end with EMIT');
 return {source:tokens.join('; '),ops:tokens,pairs,bits:pairs.flatMap(p=>p.map(toBits)).join(' '),symbols:pairs.flatMap(p=>p.map(toSymbol)).join(' ')};
}
const presets=Object.freeze({
 'Drive events':['PUSH_DRIVE','QUANTIZE','EMIT'],
 'Optical density proxy':['PUSH_EDGE','QUANTIZE','EMIT'],
 'Pixel change':['PUSH_FRAME_DIFF','QUANTIZE','EMIT'],
 'Phone acceleration':['PUSH_ACCEL','QUANTIZE','EMIT'],
 'Magnetic field':['PUSH_MAG','QUANTIZE','EMIT'],
 'Light level':['PUSH_LUX','QUANTIZE','EMIT'],
 'Red minus blue':['PUSH_R','PUSH_B','SUB','QUANTIZE','EMIT']
});
export const PROGRAMS=presets;
export class QuadVM{
 constructor(source='Drive events',opts={}){this.program=compile(presets[source]||source);this.encoder=new QuadEncoder(opts);this.emitted=[];}
 reset(){this.encoder.reset();this.emitted=[];}
 run(sample){
  const stack=[],events=[],f=(x)=>Number.isFinite(x)?x:0;
  for(const op of this.program.ops){
   if(op.startsWith('PUSH_')){
    const look={PUSH_R:sample.rgb?.[0],PUSH_G:sample.rgb?.[1],PUSH_B:sample.rgb?.[2],PUSH_DRIVE:sample.drive,
     PUSH_EDGE:sample.edgeDensity,PUSH_FRAME_DIFF:sample.frameDifference,PUSH_ACCEL:sample.acceleration,
     PUSH_MAG:sample.magnetometer,PUSH_LUX:sample.lux,PUSH_ZERO:0};
    if(['PUSH_ACCEL','PUSH_MAG','PUSH_LUX','PUSH_FRAME_DIFF'].includes(op)&&!Number.isFinite(look[op]))throw Error(op+' unavailable: no genuine sensor reading');
    stack.push(f(look[op]));
   } else if(['ADD','SUB','MUL'].includes(op)){
    if(stack.length<2)throw Error('Stack underflow for '+op);
    const b=stack.pop(),a=stack.pop();stack.push(op==='ADD'?a+b:op==='SUB'?a-b:a*b);
   }else if(op==='CLAMP01'){
    if(!stack.length)throw Error('stack underflow');stack.push(clamp(stack.pop(),0,1));
   }else if(op==='QUANTIZE'){
    if(!stack.length)throw Error('stack underflow');const v=stack.pop();const event=this.encoder.step({drive:v});events.push(event);
   }else if(op==='EMIT'){
    if(!events.length)throw Error('QUANTIZE must precede EMIT');this.emitted.push(events.at(-1));
    if(this.emitted.length>10000)this.emitted.shift();
   }
   if(stack.length>64)throw Error('stack capacity');
  }
  return events.at(-1);
 }
}
/** Uniformly sampled scalar DFT with Hann window, DC removal, and peak test.
 * Input must be true numerical time-series readings. Does not identify RF or
 * optical carrier frequency. Only frequencies below Nyquist are resolvable.
 */
export function temporalFrequencyHz(samples, timestampsMs){
 if(!Array.isArray(samples)||!Array.isArray(timestampsMs)||samples.length!==timestampsMs.length||samples.length<24)
  return {valid:false,reason:'Insufficient genuine samples'};
 const n=Math.min(128,samples.length),v=samples.slice(-n),t=timestampsMs.slice(-n);
 if(v.some(x=>!Number.isFinite(x))||t.some(x=>!Number.isFinite(x)))return{valid:false,reason:'Nonfinite sample'};
 const elapsed=(t.at(-1)-t[0])/1000;if(elapsed<=0)return{valid:false,reason:'Invalid sample timing'};
 const intervals=t.slice(1).map((x,i)=>x-t[i]),meanDt=intervals.reduce((a,b)=>a+b,0)/intervals.length;
 const jitter=Math.max(...intervals.map(x=>Math.abs(x-meanDt)))/meanDt;
 if(jitter>.2)return{valid:false,reason:'Sampling too irregular for FFT-style estimate',jitter};
 const sampleHz=1000/meanDt;const mean=v.reduce((a,b)=>a+b,0)/n;
 const x=v.map((y,i)=>(y-mean)*(.5-.5*Math.cos(2*Math.PI*i/(n-1))));
 let best=0,bestK=-1,power=0;
 for(let k=1;k<Math.floor(n/2);k++){
  let re=0,im=0;for(let j=0;j<n;j++){const phase=2*Math.PI*k*j/n;re+=x[j]*Math.cos(phase);im-=x[j]*Math.sin(phase);}
  const p=re*re+im*im;power+=p;if(p>best){best=p;bestK=k;}
 }
 if(bestK<1||best<1e-10||best/power<.35)return{valid:false,reason:'No clear dominant temporal oscillation',sampleHz,nyquistHz:sampleHz/2};
 return {valid:true,hz:bestK*sampleHz/n,nyquistHz:sampleHz/2,dominance:best/power,sampleHz,n,
  note:'Temporal modulation of a sampled sensor reading; not an optical carrier or a person’s emitted energy frequency.'};
}
/** Bounded heuristic program generator: inspect available numeric sensor ranges and
 * select one proven-safe preset. No new JS code, arbitrary opcodes or autonomous
 * model training is produced. Each decision is traceable to input statistics.
 */
export function proposeProgram(records){
 if(!Array.isArray(records)||records.length<4)return{program:'Drive events',reason:'Insufficient observations: default to preserved neuron drive.',computed:false};
 const finite=x=>Number.isFinite(x);
 const stats=(key)=>{const a=records.map(r=>r[key]).filter(finite);if(a.length<4)return null;
  const min=Math.min(...a),max=Math.max(...a),mean=a.reduce((x,y)=>x+y,0)/a.length;
  return {count:a.length,mean,range:max-min};};
 const field=stats('magnetometer'),move=stats('acceleration'),frame=stats('frameDifference'),edge=stats('edgeDensity'),drv=stats('drive');
 // Require genuine samples and nontrivial variation before choosing extra sensors.
 if(field&&field.range>=1.0&&field.count>=20)return{program:'Magnetic field',reason:'Magnetometer actually provided '+field.count+' samples with '+field.range.toFixed(2)+' µT span.',computed:true};
 if(move&&move.range>=.5&&move.count>=20)return{program:'Phone acceleration',reason:'Motion sensor actually provided '+move.count+' samples with '+move.range.toFixed(2)+' m/s² span.',computed:true};
 if(frame&&frame.mean>.03&&frame.count>=8)return{program:'Pixel change',reason:'Camera frame-change proxy mean='+frame.mean.toFixed(3)+' across '+frame.count+' frames.',computed:true};
 if(edge&&edge.mean>.035&&edge.count>=8)return{program:'Optical density proxy',reason:'Camera ROI spatial-edge proxy mean='+edge.mean.toFixed(3)+' across '+edge.count+' frames. It is not atomic or mass density.',computed:true};
 return{program:'Drive events',reason:'Existing neuron drive is the best available verified numeric stream ('+(drv?.count??0)+' samples).',computed:true};
}
