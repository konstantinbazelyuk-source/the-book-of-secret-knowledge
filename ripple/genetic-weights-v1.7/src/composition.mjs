/** Finite, typed program recombination. No string eval or untrusted JS.
 * Search operators use truth tables from immutable v1.6 grammar. The search never reads oracle outputs.
 */
import fs from 'node:fs';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {registry} from '../sources/grammar.mjs';
import {prepare,logLik} from '../sources/engine.mjs';
import {QuadEncoder} from '../sources/v07_quaternary_core_LOCKED.mjs';
const require=createRequire(import.meta.url);const {RippleNeuron}=require('../sources/v01_ripple_core_LOCKED.cjs');
const parent=registry().all;const primitives=parent.filter(p=>!p.family.startsWith('composed'));
const fingerprint=p=>p.outputs.join(',');
const unique=new Map(parent.map(x=>[fingerprint(x),x]));const external=[];
for(const inner of primitives){for(const outer of primitives){
  const outputs=inner.outputs.map(x=>outer.outputs[x]);const sig=outputs.join(',');
  if(!unique.has(sig)){
   const expr=outer.expr.endsWith('(x)')?outer.expr.slice(0,-3)+'('+inner.expr+')':outer.expr+' ∘ '+inner.expr;
   const item={expr,outputs,complexity:2,family:'composed-forest',id:createHash('sha256').update(expr+sig).digest('hex').slice(0,16)};
   unique.set(sig,item);external.push(item);
  }
}}
const full=[...parent,...external];
export function counts(){return {parents:parent.length,primitives:primitives.length,newSemantics:external.length,total:full.length}}
function best(pool,observed,complexityPenalty=.12){
 let one=null,two=null;
 for(const p of pool){const raw=logLik(p,observed);const rank=raw-complexityPenalty*p.complexity;
  const rec={p,raw,rank};
  if(!one||rec.rank>one.rank+1e-10){two=one;one=rec}
  else if(!two||rec.rank>two.rank+1e-10)two=rec;
 }
 return {one,two};
}
function granted(train){let n=new RippleNeuron({adaptive:true,target:1});let events=0;const codec=new QuadEncoder({threshold:.1,dwell:1});
 const codes=[];
 for(let k=0;k<10;k++){
  const evidence=Math.min(1,[...train[k].rx,...train[k].ry].reduce((a,b)=>a+Math.abs(b),0)/40);
  for(let j=0;j<10;j++)events+=n.step([.2+.8*evidence,0,0],.2).count;
  const sym=codec.step({drive:Math.max(-1,Math.min(1,train[k].rx[0]/5))});if(k<4)codes.push(sym.label);
 }
 return {emitted:events>0,events,codes,threshold:n.theta};
}
export function assess(data,{mode='parent',colony=false}={}){
 if(!['parent','composed'].includes(mode))throw Error('mode');
 const observed=prepare(data.examples).slice(0,10);
 const baseline=best(parent,observed);const grant=colony?granted(observed):{emitted:true,events:0,codes:[]};
 const choice=mode==='composed'&&grant.emitted?best(full,observed):baseline;
 const first=choice.one;
 const quality=observed.reduce((v,o)=>v+Math.max(...o.xp)*Math.max(...o.yp),0)/10;
 const gain=first.raw+10*Math.log(16);
 const margin=first.rank-choice.two.rank;
 const accepted=!!grant.emitted&&quality>=.20&&gain>=4&&margin>=1.5;
 const holds=data.examples.slice(10);
 const correct=holds.filter(e=>first.p.outputs[e.x_true]===e.y_true).length;
 return {id:data.id,seed:data.seed,kind:data.kind,photons:data.photons_per_bit,condition:data.condition,
   mode,decision:accepted?'SUPPORTED':'ABSTAIN',correct,total:6,model:first.p.expr,novel:!parent.some(p=>fingerprint(p)===fingerprint(first.p)),
   gain:+gain.toFixed(3),margin:+margin.toFixed(3),quality:+quality.toFixed(3),spikes:grant.events,codes:grant.codes};
}
function main(){const records=JSON.parse(fs.readFileSync(new URL('../data/novel_compositions.json',import.meta.url))).cases;
 const groups={};let examples=[],parentExamples=[];
 for(const mode of ['parent','composed']){
  for(const colony of [false,true]){
   let rows=[];
   for(const c of records)rows.push(assess(c,{mode,colony}));
   const accepted=rows.filter(x=>x.decision==='SUPPORTED');
   const rec={mode,colony,cases:rows.length,accepted:accepted.length,acceptedCorrect:accepted.reduce((s,r)=>s+r.correct,0),
    acceptedOutputs:accepted.length*6,provisionalCorrect:rows.reduce((s,r)=>s+r.correct,0),totalOutputs:rows.length*6,
    novelPrograms:rows.filter(x=>x.novel).length,spikes:rows.reduce((s,r)=>s+r.spikes,0)};
   groups[mode+'_'+(colony?'ripple':'serial')]=rec;
   if(mode==='composed'&&colony)examples=rows;
   if(mode==='parent'&&colony)parentExamples=rows;
  }
 }
 const report={schema:'ripple-v17-grammar-compose/1',components:counts(),groups,samples:examples.slice(0,30),fullRecords:examples,parentRecords:parentExamples};
 fs.writeFileSync(new URL('../data/composition_results.json',import.meta.url),JSON.stringify(report,null,2));
 console.log('COMPOSITIONS',JSON.stringify({components:counts(),groups}));
}
if(import.meta.url===new URL(`file://${process.argv[1]}`).href)main();
