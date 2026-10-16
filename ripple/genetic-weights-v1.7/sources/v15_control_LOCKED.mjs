/** Ripple Code-Reasoning Colony Alpha v1.5
 * Uses exact, checksum-locked v0.1 LIF + v0.7 quaternary code.
 * Named 'hypothesis trace', not an internal conscious thought process.
 * No user-defined JS execution, file writes, network calls or API keys.
 */
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {pack4,unpack4,toBits,fromBits,QuadEncoder} from '../sources/v07_quaternary_core_LOCKED.mjs';
const require=createRequire(import.meta.url);
const {RippleNeuron}=require('../sources/v01_ripple_core_LOCKED.cjs');
const mask=x=>x&15;
const rev=x=>parseInt(x.toString(2).padStart(4,'0').split('').reverse().join(''),2);
const rol=(x,k)=>mask((x<<k)|(x>>(4-k)));
const nodeId=x=>createHash('sha256').update(x).digest('hex').slice(0,16);

/** Explicit finite grammar; no eval, Function, dynamic import of model-generated programs. */
export function hypotheses(composed=true){
 const candidates=[]; const add=(family,expr,complexity,fn)=>{
   const outputs=Array.from({length:16},(_,x)=>mask(fn(x)));
   if(candidates.some(e=>e.outputs.every((y,i)=>y===outputs[i])))return;
   const m={id:nodeId(expr+'|'+outputs.join(',')),family,expr,complexity,outputs};candidates.push(m);
 };
 add('bitwise','identity(x)',1,x=>x);
 for(let k=1;k<16;k++)add('bitwise',`xor${k}(x)`,1,x=>x^k);
 for(let k=1;k<16;k++)add('arithmetic',`add${k}(x)`,1,x=>x+k);
 for(let k=1;k<4;k++)add('structure',`rotate${k}(x)`,1,x=>rol(x,k));
 add('structure','gray(x)',1,x=>x^(x>>1));
 add('structure','reverse(x)',1,x=>rev(x));
 if(composed){
  for(let k=1;k<16;k++)for(let r=1;r<4;r++)add('composed',`rotate${r}(xor${k}(x))`,2,x=>rol(x^k,r));
  for(let a=1;a<16;a++)for(let k=1;k<16;k++)add('composed',`xor${k}(add${a}(x))`,2,x=>mask(x+a)^k);
  for(let k=1;k<16;k++)add('composed',`xor${k}(reverse(x))`,2,x=>rev(x)^k);
 }
 return candidates;
}
const negSoftplus=x=> x>30?-x: -Math.log1p(Math.exp(x));
function symbolLogProbs(llrs){
 // log P(binary observations | candidate bit) up to a candidate-independent factor.
 // calibrated LLR = log P(counts|bit=1)/P(counts|bit=0)
 const arr=Array(16).fill(0);
 for(let x=0;x<16;x++)for(let k=0;k<4;k++){
  const p=llrs[k];const b=(x>>(3-k))&1;
  arr[x]+=b?negSoftplus(-p):negSoftplus(p);
 }
 return arr;
}
export function decode(example){
 const x=example.rx.hard,y=example.ry.hard;
 if(!Number.isInteger(x)||x<0||x>15||!Number.isInteger(y)||y<0||y>15)throw Error('invalid received nibble');
 if(!Array.isArray(example.rx.llr)||example.rx.llr.length!==4||!Array.isArray(example.ry.llr)||example.ry.llr.length!==4)throw Error('invalid optical evidence');
 for(const v of [...example.rx.llr,...example.ry.llr])if(!Number.isFinite(v))throw Error('nonfinite photon log likelihood');
 // Real v0.7 quaternary 2-bit interface: 4 binary bits -> 2 symbols; checked roundtrip.
 const xy=[x,y].map(v=>[ (v>>2)&3,v&3 ]);
 const packed=pack4([...xy[0],...xy[1]]);
 const unpacked=unpack4(packed);
 if(x!==((unpacked[0]<<2)|unpacked[1])||y!==((unpacked[2]<<2)|unpacked[3]))throw Error('quaternary roundtrip failure');
 return {x,y,rx:example.rx.llr,ry:example.ry.llr,pack:packed,quaternary:unpacked,
   bitstrings:unpacked.map(toBits),inLog:symbolLogProbs(example.rx.llr),outLog:symbolLogProbs(example.ry.llr)};
}
function logsumexp(arr){const m=Math.max(...arr);return m+Math.log(arr.reduce((a,v)=>a+Math.exp(v-m),0));}
// Marginalize latent transmitted input X over 16 possible nibbles instead of pretending hard decode is certain.
export function score(candidate,observations,method='soft'){
 let s=0;
 for(const o of observations){
  if(method==='hard') { // negative number mismatched hard bits; independent conventional baseline
   const diff=(candidate.outputs[o.x]^o.y);s-=(diff&1)+((diff>>1)&1)+((diff>>2)&1)+((diff>>3)&1);continue;
  }
  const terms=Array.from({length:16},(_,x)=>o.inLog[x]+o.outLog[candidate.outputs[x]]);
  s+=logsumexp(terms); // candidate-independent -ln(16) omitted
 }
 return s;
}
class RippleSpecialist{
 constructor(family){this.family=family;this.neuron=new RippleNeuron({theta:.45,adaptive:true,target:1});this.encoder=new QuadEncoder({threshold:.1,dwell:1});this.spikes=0;this.codes=[];this.processed=0;}
 receive(observations){
  let emitted=0;
  for(const obs of observations){
   for(const llr of [...obs.rx,...obs.ry]){
    const drive=.35+.6*Math.min(1,Math.abs(llr)/5);
    const r=this.neuron.step([drive,0,0],.2);
    emitted+=r.count;this.spikes+=r.count;
    const e=this.encoder.step({drive:llr>0?Math.min(1,llr/5):-Math.min(1,-llr/5)});
    if(this.codes.length<8)this.codes.push(e.label);
   }
  }
  return emitted>0;
 }
 evaluate(pool,observations,method){
  const rows=pool.map(c=>({...c,score:score(c,observations,method)}));
  rows.sort((a,b)=>b.score-a.score || a.complexity-b.complexity || a.expr.localeCompare(b.expr));
  this.processed+=pool.length;
  return rows.slice(0,5).map(c=>({id:c.id,expr:c.expr,family:c.family,score:c.score,complexity:c.complexity,outputs:c.outputs}));
 }
}
const families=['bitwise','arithmetic','structure','composed'];
function rankCandidates(pool,observations,mode){
 const out=pool.map(c=>({...c,score:score(c,observations,mode)}));out.sort((a,b)=>b.score-a.score||a.complexity-b.complexity||a.expr.localeCompare(b.expr));return out;
}

export function runCase(caseData,{composed=true,method='soft',colony=true,maxTraining=10,traceDetail=false}={}){
 const pool=hypotheses(composed);
 const received=caseData.examples.map(decode);
 const observedTrain=received.slice(0,10), heldout=received.slice(10);
 if(!observedTrain.some(o=>[...o.rx,...o.ry].some(v=>Math.abs(v)>1e-12))) {
   return {id:caseData.id,task:caseData.kind,seed:caseData.seed,photons:caseData.photons_per_bit,
     model:null,decision:'ABSTAIN_NO_INFORMATION',knownCodeRecovered:false,holdoutCorrect:0,
     holdoutTotal:heldout.length,ambiguous:true,trainingUsed:0,rounds:[],births:0,retirements:0,peakPopulation:0,
     trace:traceDetail?[{stage:'OBSERVE',text:'All optical likelihood ratios were zero; channel cannot distinguish bit values.'},
       {stage:'ABSTAIN',text:'No model admitted; unknown code cannot be inferred from identical evidence.'}]:undefined};
 }
 const trace=[{stage:'OBSERVE',text:'Decoded photon-pattern likelihoods into 4-bit input/output symbols using the locked v0.7 quaternary functions.',
    details:{trainingAvailable:10,heldOut:6,photonsPerBit:caseData.photons_per_bit,opticalSensing:'synthetic'}}];
 const workers=Object.fromEntries(families.map(f=>[f,new RippleSpecialist(f)]));
 const rounds=[];let leader=null,ambiguous=true,used=0;
 let clones=[];let births=0;const maxNodes=7;
 for(let n=3;n<=Math.min(10,maxTraining);n++){
  const evidence=observedTrain.slice(0,n);
  let ranked=[];
  if(colony){
   // Parent receives evidence first. Only firing parent can authorize bounded replication.
   const parent=workers.composed;
   if(composed && n>=4 && !clones.length && pool.filter(c=>c.family==='composed').length>40
      && parent.receive([evidence.at(-1)]) && families.length+2<=maxNodes){
      clones=[new RippleSpecialist('composed'),new RippleSpecialist('composed')];births=2;
      trace.push({stage:'REPLICATE',text:'Composed-policy parent fired; 2 independent LIF descendants added for bounded candidate partitioning. No operating-system process was spawned.',
        details:{population:6,ancestry:'composed parent → composed-1, composed-2',maxNodes}});
   }
   for(const f of families){
    const parts=pool.filter(c=>c.family===f);
    if(!parts.length)continue;
    const members=f==='composed'?[workers[f],...clones]:[workers[f]];
    for(let wi=0;wi<members.length;wi++){
     const subset=parts.filter((_,i)=>i%members.length===wi);
     if(!subset.length)continue;
     const specialist=members[wi];
     if(!specialist.receive([evidence.at(-1)]))continue;
     ranked.push(...specialist.evaluate(subset,evidence,method));
    }
   }
   ranked.sort((a,b)=>b.score-a.score||a.complexity-b.complexity||a.expr.localeCompare(b.expr));
  } else ranked=rankCandidates(pool,evidence,method);
  if(!ranked.length){rounds.push({n,reason:'No Ripple firing authorization',winner:null});continue;}
  const best=ranked[0],second=ranked[1];
  const margin=second?best.score-second.score:Infinity;
  leader=best;used=n;
  // No oracle or heldout labels are read during candidate selection.
  ambiguous= !second || margin<4.0 || (method==='hard'&&margin<1);
  rounds.push({n,winner:best.expr,family:best.family,score:Number(best.score.toFixed(4)),margin:Number.isFinite(margin)?Number(margin.toFixed(4)):null,ambiguous,
               candidates:ranked.slice(0,3).map(x=>({rule:x.expr,score:Number(x.score.toFixed(3))}))});
  if(!ambiguous&&n>=4)break;
 }
 trace.push({stage:'HYPOTHESIZE',text:`Generated ${pool.length} distinct candidate functions from a bounded known grammar and split them across ${composed?4:3} specialist families.`});
 trace.push({stage:'TEST_AND_REVISE',text: `Evaluated successively larger training subsets; ${rounds.length} evidence rounds. Additional examples were disclosed only if the candidate score margin was insufficient.`,rounds});
 const model=leader;
 const predictions=heldout.map((o,i)=>({index:10+i,inputObserved:o.x,inputTrue:caseData.examples[10+i].x_true,
   predicted:model?model.outputs[o.x]:null,truth:caseData.examples[10+i].y_true,
   correct:model?model.outputs[o.x]===caseData.examples[10+i].y_true:false}));
 const correct=predictions.filter(p=>p.correct).length;
 // Ground truth is consumed ONLY after training, for the external evaluator.
 const truthSignature=Array(16).fill(null);
 for(const ex of caseData.examples){
   if(!Number.isInteger(ex.x_true)||ex.x_true<0||ex.x_true>15 ||
      !Number.isInteger(ex.y_true)||ex.y_true<0||ex.y_true>15)throw Error('invalid evaluator-only ground truth');
   truthSignature[ex.x_true]=ex.y_true;
 }
 if(truthSignature.some(x=>x===null))throw Error('evaluation requires all 16 unique input values');
 const exactModel=!!model&&model.outputs.every((y,x)=>y===truthSignature[x]);
 trace.push({stage:'COMPARE',text:model?`Top candidate ${model.expr}, evidence ambiguity ${ambiguous?'unresolved':'below threshold'}.`:'No candidate authorized.'});
 trace.push({stage:'VERIFY_HELDOUT',text:`Scored ${predictions.length} samples unseen by candidate search: ${correct}/${predictions.length} correct.`,result:{correct,total:predictions.length,exactModel}});
 // Absolute fit gate: compare relation model to a null channel with 4-bit Y independent of X.
 // Null log-likelihood = -ln(16) per independent training example.
 const fitGain=model?model.score+used*Math.log(16):null;
 const decision=!model?'ABSTAIN_NO_SPIKES':fitGain<2?'ABSTAIN_POOR_GRAMMAR_FIT':ambiguous?'PROVISIONAL_NOT_VALIDATED':'EVIDENCE_SUPPORTED';
 const workerTelemetry=colony?[...families.map(f=>({role:f,spikes:workers[f].spikes,codeExamples:workers[f].codes,modelsTested:workers[f].processed,
    threshold:Number(workers[f].neuron.theta.toFixed(5))})), ...clones.map((w,i)=>({role:'composed-child-'+(i+1),spikes:w.spikes,codeExamples:w.codes,modelsTested:w.processed,threshold:Number(w.neuron.theta.toFixed(5))}))]:[];
 return {id:caseData.id,task:caseData.kind,seed:caseData.seed,photons:caseData.photons_per_bit,
   model:model?{expr:model.expr,family:model.family,id:model.id,complexity:model.complexity}:null,
   knownCodeRecovered:exactModel,holdoutCorrect:correct,holdoutTotal:predictions.length,margin:rounds.at(-1)?.margin??null,
   ambiguous,decision,fitGain:fitGain===null?null:Number(fitGain.toFixed(4)),
   births,retirements:births,peakPopulation:colony?4+births:0,trainingUsed:used,rounds,trace:traceDetail?trace:undefined,
   predictions:traceDetail?predictions:undefined,telemetry:traceDetail?workerTelemetry:undefined};
}
export const stableHash=o=>createHash('sha256').update(JSON.stringify(o)).digest('hex');
