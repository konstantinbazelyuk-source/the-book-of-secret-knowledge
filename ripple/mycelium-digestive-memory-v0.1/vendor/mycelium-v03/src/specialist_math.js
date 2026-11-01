'use strict';
// Deterministic, local, inspectable computation. No generative model or external data.
const sigmoid=x=>1/(1+Math.exp(-Math.max(-40,Math.min(40,x))));
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const add=(a,b)=>a.map((v,i)=>v+b[i]);
function lossGradient(items,weights){
 const g=Array(weights.length).fill(0);let loss=0;
 for(const o of items){let z=dot(o.x,weights),p=sigmoid(z);loss+=-(o.y*Math.log(Math.max(p,1e-15))+(1-o.y)*Math.log(Math.max(1-p,1e-15)));
   for(let k=0;k<g.length;k++)g[k]+=(p-o.y)*o.x[k];}
 return {gradient:g,loss,n:items.length};
}
function productStats(items){let revenue=0,cost=0,shortfall=0,qty=0;
 for(const {quantity,unitPriceCents,unitCostCents,stock} of items){
  if(![quantity,unitPriceCents,unitCostCents,stock].every(Number.isSafeInteger)||quantity<0||unitPriceCents<0||unitCostCents<0||stock<0)throw Error('bad product');
  revenue+=quantity*unitPriceCents;cost+=quantity*unitCostCents;qty+=quantity;shortfall+=Math.max(0,quantity-stock);
 }
 return {revenue,cost,quantity:qty,shortfall};
}
function studyStats(items){
 // Evidence is an invented experimental dataset; duplicate measurement IDs must not be reused.
 for(const o of items)if(!(typeof o.id==='string'&&Number.isFinite(o.value)&&Number.isFinite(o.variance)&&o.variance>0))throw Error('invalid study evidence');
 return items.map(o=>({...o}));
}
function studyCombine(parts){
 const seen=new Set();let duplicates=0,sumW=0,sumWX=0;const samples=[];
 for(const p of parts)for(const o of p){if(seen.has(o.id)){duplicates++;continue;}seen.add(o.id);samples.push(o);let w=1/o.variance;sumW+=w;sumWX+=w*o.value;}
 const mean=sumWX/sumW,se=Math.sqrt(1/sumW);let q=0;
 for(const o of samples)q+=(o.value-mean)**2/o.variance;
 return {mean,se,ci95:[mean-1.96*se,mean+1.96*se],heterogeneityQ:q,duplicateEvidence:duplicates,evidenceIds:[...seen].sort(),n:samples.length,
  // The threshold is a simple transparent alert, not a calibrated hypothesis test.
  possibleConflict:samples.length>1&&q>2*(samples.length-1)};
}
function makeLearning(n=240){const rows=[];for(let i=0;i<n;i++){
 let x1=Math.sin((i+1)*1.37),x2=Math.cos((i+1)*2.13),bias=1;
 let y=x1*1.9-x2*1.3+.15>0?1:0;
 rows.push({x:[bias,x1,x2],y});}return rows;
}
function accuracy(rows,w){return rows.filter(r=>(sigmoid(dot(r.x,w))>=.5?1:0)===r.y).length/rows.length;}
function makeProduct(seed,n=16){return Array.from({length:n},(_,i)=>({quantity:1+(seed+i)%7,unitPriceCents:1000+((seed*31+i*47)%5000),unitCostCents:450+((seed*17+i*19)%500),stock:(seed+i)%11}));}
function makeStudy(seed,n=12){return Array.from({length:n},(_,i)=>({id:`${seed}-${i===n-1?1:i}`,value:6+.5*Math.sin(seed+i*1.7)+(seed%2?0.4:0),variance:.3+(i%3)*.15,source:`synthetic-study-${seed}`}));}
function reference(type,items,weights=[0,0,0]){if(type==='learning')return lossGradient(items,weights);if(type==='product')return productStats(items);if(type==='study')return studyCombine([studyStats(items)]);throw Error('invalid type');}
module.exports={sigmoid,dot,add,lossGradient,productStats,studyStats,studyCombine,makeLearning,accuracy,makeProduct,makeStudy,reference};
