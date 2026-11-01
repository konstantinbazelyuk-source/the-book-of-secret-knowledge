'use strict';
const fs=require('node:fs');const path=require('node:path');const os=require('node:os');const {performance}=require('node:perf_hooks');
const {calculate}=require('./cpu_task');const {ParallelColony}=require('./parallel_colony');
async function one({name,workers,policy,mode,topology='ring',tasks=64,rounds=400000,rep=0}){
 const colony=new ParallelColony({maxWorkers:workers,policy,mode,topology,idleMs:250});
 const cpuStart=process.cpuUsage();const rssStart=process.memoryUsage().rss;const t0=performance.now();
 try{
  for(let i=0;i<tasks;i++)colony.submit(i,rounds);
  const report=await colony.waitDone({timeoutMs:120000});const elapsed=performance.now()-t0;
  const cpu=process.cpuUsage(cpuStart);
  for(let i=0;i<tasks;i++){const expected=calculate(i,rounds);if(colony.completed.get(i)!==expected)throw Error(`checksum failed on ${i}`);}
  return {name,rep,workers,policy,mode,topology,tasks,rounds,wallMs:+elapsed.toFixed(2),cpuMs:+((cpu.user+cpu.system)/1000).toFixed(2),rssStartMB:+(rssStart/1048576).toFixed(2),rssEndMB:+(process.memoryUsage().rss/1048576).toFixed(2),...report};
 }finally{await colony.close();}
}
async function main(){
 const configs=[
  {name:'single-plain',workers:1,policy:'fixed',mode:'plain'},
  {name:'four-plain',workers:4,policy:'fixed',mode:'plain'},
  {name:'four-ripple',workers:4,policy:'fixed',mode:'ripple'},
  {name:'elastic-plain',workers:4,policy:'elastic',mode:'plain'},
  {name:'elastic-ripple',workers:4,policy:'elastic',mode:'ripple'}
 ];
 const tasks=Number(process.argv[2]||64),rounds=Number(process.argv[3]||400000),reps=Number(process.argv[4]||3);
 const rows=[];
 for(let rep=0;rep<reps;rep++){
  // Rotate starting mode to reduce, not eliminate, time-of-run effects.
  for(let j=0;j<configs.length;j++){
   const c=configs[(j+rep)%configs.length];const r=await one({...c,tasks,rounds,rep});rows.push(r);
   process.stdout.write(`${rep+1}/${reps} ${c.name} ${r.wallMs.toFixed(2)} ms ${r.completed}/${r.tasks} verified peak ${r.peakThreads}\n`);
  }
 }
 const meta={node:process.version,platform:process.platform,arch:process.arch,availableParallelism:os.availableParallelism?.()??os.cpus().length,
  logicalCPUs:os.cpus().length,iterations:rounds,tasks,repetitions:reps,timing:'performance.now wall clock includes startup, dispatch and computation but not serial checksum verification; all samples from this container'};
 const file=path.resolve(__dirname,'../data/thread_benchmark.json');fs.writeFileSync(file,JSON.stringify({meta,rows},null,2));
 const agg=configs.map(c=>{const s=rows.filter(r=>r.name===c.name).map(r=>r.wallMs).sort((a,b)=>a-b);return {name:c.name,samples:s,medianMs:s[Math.floor(s.length/2)],completed:tasks};});
 fs.writeFileSync(path.resolve(__dirname,'../data/thread_benchmark_summary.json'),JSON.stringify({meta,aggregate:agg},null,2));
 console.log(JSON.stringify(agg));return {meta,agg};
}
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});module.exports={one,main};
