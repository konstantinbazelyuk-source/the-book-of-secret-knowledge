'use strict';
const fs=require('node:fs');const path=require('node:path');
const {VariantColony,ROUTES,SCALES,GRAPHS}=require('./colony_variants');
const outdir=path.resolve(__dirname,'../data');
const regimes={
 burst(t){return t<30?(Math.round(t*20)%100===0):t<110?(Math.round((t-30)*20)%22===0):t<160?(Math.round((t-110)*20)%240===0):false;},
 steady(t){return t<150&&(Math.round(t*20)%48===0);},
 twin(t){return (t>=10&&t<55&&Math.round((t-10)*20)%16===0)||(t>=95&&t<135&&Math.round((t-95)*20)%16===0);},
 drought(t){return t<20&&(Math.round(t*20)%10===0);}
};
function run(scaling,routing,graph,regime='burst',maxNodes=12){
 const c=new VariantColony({routing,scaling,graph,maxNodes});const steps=Math.round(200/c.dt);const snapshots=[];
 for(let k=0;k<steps;k++){
  if(regimes[regime](c.t))c.syntheticJob();c.step();
  if(k%20===19){c.assertIntegrity();if(regime==='burst')snapshots.push({t:c.t,workers:c.nodes.size,pending:c.pending(),completed:c.outCount,relays:c.relayCount});}
 }
 c.assertIntegrity();return {summary:{scenario:regime,...c.summary()},snapshots,finish:[...c.finished.entries()].sort((a,b)=>a[0]-b[0]).map(([id,x])=>({id,...x}))};
}
function sweep(){
 const rows=[],scenarios=Object.keys(regimes);
 for(const s of SCALES)for(const r of ROUTES)for(const g of GRAPHS)for(const scenario of scenarios)rows.push(run(s,r,g,scenario).summary);
 fs.mkdirSync(outdir,{recursive:true});fs.writeFileSync(path.join(outdir,'variant_sweep.json'),JSON.stringify(rows,null,2));
 const cols=Object.keys(rows[0]);fs.writeFileSync(path.join(outdir,'variant_sweep.csv'),[cols.join(','),...rows.map(x=>cols.map(k=>x[k]??'').join(','))].join('\n')+'\n');
 const fused=run('fused','steal','tree','burst');fs.writeFileSync(path.join(outdir,'fused_burst_trace.json'),JSON.stringify(fused,null,2));
 console.log(`Simulated ${rows.length} configuration/scenario combinations.`);
 const subset=rows.filter(x=>x.scenario==='burst').sort((a,b)=>b.completed-a.completed||a.workerSeconds-b.workerSeconds||a.relays-b.relays);
 console.log('Top burst:',JSON.stringify(subset.slice(0,6),null,2));
 console.log('Fused:',JSON.stringify(fused.summary,null,2));
}
if(require.main===module)sweep();module.exports={run,sweep,regimes};
