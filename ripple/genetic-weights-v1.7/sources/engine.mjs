/** Ripple v1.6 - bounded grammar expansion and OOD checking over copied source kernels.
 * Designed as an experimental inference process, NOT general intelligence.
 */
import {createRequire} from 'node:module';
import {registry} from './grammar.mjs';
import {decode} from './v15_control_LOCKED.mjs';
import {createHash} from 'node:crypto';
import {QuadEncoder} from '../sources/v07_quaternary_core_LOCKED.mjs';
const require=createRequire(import.meta.url);
const {RippleNeuron}=require('../sources/v01_ripple_core_LOCKED.cjs');
const LOG16=Math.log(16);
const catalogue=registry();
const classes=['bitwise','arithmetic','structure','composed','expanded'];
const finite=x=>Number.isFinite(x)&&!Number.isNaN(x);
const specificity=(p)=>p.complexity*0.12;
export function prepare(examples){
 return examples.map(e=>{
  const o=decode(e);
  const xp=o.inLog.map(Math.exp),yp=o.outLog.map(Math.exp);
  return {...o,xp,yp};
 });
}
export function logLik(program,data){
 let s=0;
 for(const o of data){let sum=0;for(let x=0;x<16;x++)sum+=o.xp[x]*o.yp[program.outputs[x]];
  s+=Math.log(Math.max(sum,1e-300));
 }
 return s;
}
function top(pool,observations,n=4){
 const rows=pool.map(p=>({p,score:logLik(p,observations),rank:0}));
 for(let i=0;i<rows.length;i++)rows[i].rank=rows[i].score-specificity(rows[i].p);
 rows.sort((a,b)=>b.rank-a.rank||a.p.complexity-b.p.complexity||a.p.expr.localeCompare(b.p.expr));
 return rows.slice(0,n);
}
class Specialist{
 constructor(name){this.name=name;this.neuron=new RippleNeuron({adaptive:true,target:1});this.encoder=new QuadEncoder({threshold:.1,dwell:1});this.spikes=0;this.codes=[];this.gateTimes=0;}
 authorize(observed){
  // Gate relates to real locked LIF event generation, not to source semantics.
  const strength=Math.min(1,observed.reduce((a,x)=>a+[...x.rx,...x.ry].reduce((s,llr)=>s+Math.abs(llr),0)/8,0)/10);
  let triggered=false;
  for(let i=0;i<24;i++){
   const event=this.neuron.step([.25+.65*strength,0,0],.2);this.spikes+=event.count;
   if(event.count)triggered=true;
  }
  for(let i=0;i<Math.min(observed.length,3);i++){
   const llr=observed[i].rx[0];const z=this.encoder.step({drive:Math.max(-1,Math.min(1,llr/5))});this.codes.push(z.label);
  }
  this.gateTimes++;return triggered;
 }
}
function infer(pool,train,supportOnly=false){
 // Calibration split 7+3; never read withheld six cases or oracle labels.
 const support=train.slice(0,7),confirmation=train.slice(7,10);
 const ranked=top(pool,support,pool.length); // Explicit bounded brute-force search
 // Re-rank top candidates on all ten TRAIN examples; validation evidence remains independent of initial ranking.
 const tested=ranked.map(x=>({p:x.p,score:logLik(x.p,train), confirm:logLik(x.p,confirmation)}));
 tested.sort((a,b)=>(b.score-specificity(b.p))-(a.score-specificity(a.p))||a.p.expr.localeCompare(b.p.expr));
 let best=tested[0],second=tested[1];
 let gain=best?best.score+train.length*LOG16:-Infinity;
 let delta=best&&second?(best.score-specificity(best.p))-(second.score-specificity(second.p)):0;
 let confirmGain=best?best.confirm+confirmation.length*LOG16:-Infinity;
 // Both relative ambiguity AND absolute evidence. Conservative at low photons.
 let status= !best||gain<4||confirmGain<.7?'ABSTAIN_UNSUPPORTED':delta<1.5?'ABSTAIN_AMBIGUOUS':'SUPPORTED';
 return {best,second,gain,delta,confirmGain,status,ranked:tested.slice(0,3)};
}
export function analyze(data,{mode='adaptive',withColony=true,detailed=false,minReliability=0}={}){
 if(!['adaptive','fixed','expanded'].includes(mode))throw Error('unknown mode');
 if(!data||!Array.isArray(data.examples)||data.examples.length!==16)throw Error('bad case');
 const observations=prepare(data.examples);
 const train=observations.slice(0,10);
 const noInfo=train.every(o=>[...o.rx,...o.ry].every(x=>Math.abs(x)<1e-9));
 const distinctObservedInputs=new Set(train.map(o=>o.x)).size;
 const collapsed=distinctObservedInputs<3;
 const signalQuality=train.reduce((sum,o)=>sum+Math.max(...o.xp)*Math.max(...o.yp),0)/train.length;
 const actors=withColony?classes.map(c=>new Specialist(c)):[];
 const trace=[{stage:'OBSERVE',detail:`10 training pairs, 6 reserved inputs; ${data.photons_per_bit} simulated photons/bit; condition ${data.condition}.`}];
 let base=null,active=null,triggered=false,births=0;
 if(!noInfo&&!collapsed){
  if(withColony){triggered=actors.every(a=>a.authorize(train));}else triggered=true;
  if(triggered){
   base=infer(catalogue.base,train);
   trace.push({stage:'BASELINE_SEARCH',detail:`${catalogue.base.length} finite functions; best ${base.best.p.expr}; fit gain ${base.gain.toFixed(3)}; status ${base.status}.`});
   const expand=mode==='expanded'||(mode==='adaptive' && base.status!=='SUPPORTED');
   if(expand){
    const child=withColony?new Specialist('child-grammar'):null;
    if(withColony && child.authorize(train)){actors.push(child);births=1;}
    else if(withColony){trace.push({stage:'GATE',detail:'No new operation admitted because expanded worker emitted no LIF event.'});}
    if(!withColony||births===1){
      active=infer(catalogue.all,train);
      trace.push({stage:'GRAMMAR_EXPAND',detail:`Re-evaluated ${catalogue.all.length} typed functions including masks, arithmetic and nonlinear counts; best ${active.best.p.expr}; status ${active.status}.`});
    }else active=base;
   }else active=base;
  }
 }
 if(!triggered)trace.push({stage:'ABSTAIN',detail:noInfo?'Input contained no distinguishable optical bit evidence.':collapsed?'Fewer than three distinct decoded training inputs; optical channel/representation collapsed.':'No neuron authorizations.'});
 let best=active?.best?.p??null;
 const predictions=observations.slice(10).map((o,i)=>({input:o.x,predicted:best?best.outputs[o.x]:null,truth:data.examples[i+10].y_true}));
 const correct=predictions.filter(p=>p.predicted!==null&&p.predicted===p.truth).length;
 const truth=Array(16).fill(null);
 for(const e of data.examples)truth[e.x_true]=e.y_true; // EVALUATOR ONLY, AFTER selection
 const exact=best?best.outputs.every((y,x)=>y===truth[x]):false;
 const rawDecision=active?.status||(noInfo?'ABSTAIN_NO_INFORMATION':collapsed?'ABSTAIN_INPUT_COLLAPSE':'ABSTAIN_NO_SPIKES');
 const decision=signalQuality<minReliability?'ABSTAIN_WEAK_OPTICAL_EVIDENCE':rawDecision;
 trace.push({stage:'EVALUATE_RESERVED',detail:`External evaluator: ${correct}/${predictions.length} unseen values correct; exact mapping ${exact}. Not fed back to search.`});
 const result={id:data.id,kind:data.kind,seed:data.seed,photons:data.photons_per_bit,condition:data.condition,mode,
  decision,correct,heldout:predictions.length,exact,proposed:best?.expr??null,
  newPrimitive:!!best&&!catalogue.base.some(x=>x.id===best.id),
  expanded:!!active&&active!==base,baseDecision:base?.status??null,
  fitGain:finite(active?.gain)?+active.gain.toFixed(5):null,margin:finite(active?.delta)?+active.delta.toFixed(5):null,
  births,peak:withColony?actors.length:0,
  noInfo,collapsed,distinctObservedInputs,signalQuality:+signalQuality.toFixed(6),rawDecision,trace:detailed?trace:undefined,
  predictions:detailed?predictions:undefined,
  telemetry:detailed?actors.map(a=>({role:a.name,spikes:a.spikes,threshold:a.neuron.theta,codes:a.codes})):undefined};
 return result;
}
export const statHash=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
export const grammarCounts=()=>({base:catalogue.base.length,added:catalogue.extra.length,total:catalogue.all.length});
