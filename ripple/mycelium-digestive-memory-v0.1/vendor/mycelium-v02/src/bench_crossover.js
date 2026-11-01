'use strict';
const path=require('node:path');const fs=require('node:fs');const os=require('node:os');
const {one}=require('./bench_threads');
async function main(){const rows=[];const roundsCases=[5000,100000,800000];const tasks=64,reps=3;
 const options=[{name:'single-plain',workers:1,policy:'fixed',mode:'plain'},
  {name:'four-plain',workers:4,policy:'fixed',mode:'plain'},
  {name:'four-ripple',workers:4,policy:'fixed',mode:'ripple'},
  {name:'cost-aware-ripple',workers:4,policy:'cost-aware',mode:'ripple'}];
 for(const rounds of roundsCases){for(let rep=0;rep<reps;rep++)for(let j=0;j<options.length;j++){
   const opts=options[(j+rep)%options.length],result=await one({...opts,tasks,rounds,rep});rows.push(result);console.log(rounds,rep,opts.name,result.wallMs);
 }}
 const median=a=>{a.sort((a,b)=>a-b);return a[Math.floor(a.length/2)];};const summary=[];
 for(const rounds of roundsCases)for(const o of options){const r=rows.filter(x=>x.rounds===rounds&&x.name===o.name);summary.push({rounds,mode:o.name,n:r.length,medianWallMs:median(r.map(x=>x.wallMs)),allVerified:r.every(x=>x.completed===tasks&&x.failures.length===0)});}
 const file=path.resolve(__dirname,'../data/CPU_intensity_crossover.json');fs.writeFileSync(file,JSON.stringify({environment:{node:process.version,availableParallelism:os.availableParallelism(),os:process.platform},tasks,reps,summary,rows},null,2));console.log('SUMMARY',JSON.stringify(summary));
}
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
