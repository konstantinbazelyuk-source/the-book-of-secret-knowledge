'use strict';
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const {performance}=require('node:perf_hooks');
const {execFileSync}=require('node:child_process');
const {MemoryMycelium}=require('../src/memory_mycelium');
const {ROOT,verifySources,sha256}=require('../src/pins');
const {ParallelColony}=require('../vendor/mycelium-v02/src/parallel_colony');
const {calculate}=require('../vendor/mycelium-v02/src/cpu_task');
const config={maxWorkers:4,policy:'elastic',mode:'ripple',topology:'ring'};
const scope={tenant:'benchmark',owner:'fixture-owner',project:'reuse'};
const tasks=Array.from({length:24},(_,id)=>({id,rounds:400000}));
const samples=[];
const ms=start=>performance.now()-start;

function check(results,expected=tasks){
 if(results.length!==expected.length)throw Error('result count mismatch');
 for(let i=0;i<expected.length;i++)if(results[i].value!==calculate(expected[i].id,expected[i].rounds))throw Error('serial mismatch');
}

async function original(repetition,checked){
 const start=performance.now(),colony=new ParallelColony(config);let report;
 try{
  for(const t of tasks)colony.submit(t.id,t.rounds);
  await colony.waitDone();report=colony.report();
  if(checked)for(const t of tasks)if(colony.completed.get(t.id)!==calculate(t.id,t.rounds))throw Error('baseline parity failure');
 }finally{await colony.close();}
 const elapsed=ms(start);
 // Output verification outside timing also checks the unverified baseline.
 for(const t of tasks)if(colony.completed.get(t.id)!==calculate(t.id,t.rounds))throw Error('baseline output mismatch');
 samples.push({repetition,mode:checked?'original_plus_serial_check':'original_workers',milliseconds:elapsed,
   workerJobs:tasks.length,cacheHits:0,serialChecks:checked?tasks.length:0,includesBridgeStartup:false,
   actualWorkerThreadCount:report.workerSamples.length});
}

async function memoryModes(repetition,dir){
 const dbPath=path.join(dir,'memory-'+repetition+'.sqlite');
 let start=performance.now(),memory=await MemoryMycelium.open({dbPath,scope,colonyOptions:config});
 let result=await memory.runBatch(tasks),elapsed=ms(start);check(result.results);
 samples.push({repetition,mode:'memory_cold',milliseconds:elapsed,...result.telemetry,includesBridgeStartup:true,
   actualWorkerThreadCount:result.colonyReport.actualWorkerThreadIds.length});
 start=performance.now();result=await memory.runBatch(tasks);elapsed=ms(start);check(result.results);
 samples.push({repetition,mode:'memory_warm_session',milliseconds:elapsed,...result.telemetry,includesBridgeStartup:false,actualWorkerThreadCount:0});
 await memory.close();
 start=performance.now();memory=await MemoryMycelium.open({dbPath,scope,colonyOptions:config});
 try{
  result=await memory.runBatch(tasks);elapsed=ms(start);check(result.results);
  samples.push({repetition,mode:'memory_warm_restart',milliseconds:elapsed,...result.telemetry,includesBridgeStartup:true,actualWorkerThreadCount:0});
  const mixed=[...tasks.slice(0,12),...Array.from({length:12},(_,i)=>({id:100+i,rounds:400000}))];
  start=performance.now();result=await memory.runBatch(mixed);elapsed=ms(start);check(result.results,mixed);
  samples.push({repetition,mode:'memory_half_repeated',milliseconds:elapsed,...result.telemetry,includesBridgeStartup:false,
    actualWorkerThreadCount:result.colonyReport.actualWorkerThreadIds.length});
 }finally{await memory.close();}
 return fs.statSync(dbPath).size;
}

async function main(){
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'ripple-benchmark-'));const databaseBytes=[];
 try{
  for(let repetition=1;repetition<=3;repetition++){
   for(const checked of repetition%2?[false,true]:[true,false])await original(repetition,checked);
   databaseBytes.push(await memoryModes(repetition,dir));
  }
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
 const summary={};
 for(const mode of [...new Set(samples.map(s=>s.mode))]){
  const group=samples.filter(s=>s.mode===mode),times=group.map(s=>s.milliseconds).sort((a,b)=>a-b);
  summary[mode]={medianMs:times[1],minMs:times[0],maxMs:times[2],workerJobsPerRun:group.map(s=>s.workerJobs),
    cacheHitsPerRun:group.map(s=>s.cacheHits),includesBridgeStartup:group[0].includesBridgeStartup};
 }
 const output={label:'Measured local deterministic CPU workload; not an AI quality benchmark',tasksPerRun:24,roundsPerTask:400000,
  repetitions:3,configuration:config,summary,samples,databaseBytes,
  environment:{node:process.version,python:execFileSync(process.platform==='win32'?'python':'python3',['--version'],{encoding:'utf8'}).trim(),
    platform:process.platform,arch:process.arch,availableParallelism:os.availableParallelism()},sourcePins:verifySources(),
  adapterSourceHashes:Object.fromEntries(['src/memory_mycelium.js','src/memory_bridge.js','src/pins.js','python/memory_service.py']
    .map(rel=>[rel,sha256(fs.readFileSync(path.join(ROOT,rel)))])),
  timingScope:'Original modes include worker creation/execution/shutdown. Checked baseline includes serial parity. Memory cold includes bridge startup, worker lifecycle, serial parity and writes; warm session excludes bridge startup; warm restart includes bridge startup. Memory bridge shutdown is outside those measured memory phases.',
  limits:['All tasks are deterministic integer CPU kernels, not research reasoning or model inference.',
    'Warm cases repeat exact keys. Changed task parameters/source hash miss the cache.',
    'Serial validation and persistent storage increase cold-path work.',
    'Only three repetitions on shared host; no generalized speedup or hardware-energy claim.',
    'Cache lookup uses a scoped full scan in the reference memory engine.']};
 fs.mkdirSync(path.join(ROOT,'evidence'),{recursive:true});
 fs.writeFileSync(path.join(ROOT,'evidence','benchmark.json'),JSON.stringify(output,null,2));
 const columns=['repetition','mode','milliseconds','workerJobs','cacheHits','serialChecks','includesBridgeStartup'];
 fs.writeFileSync(path.join(ROOT,'evidence','benchmark.csv'),columns.join(',')+'\n'+samples.map(s=>columns.map(c=>s[c]).join(',')).join('\n')+'\n');
 console.log(JSON.stringify(output,null,2));
}
main().catch(error=>{console.error(error.stack);process.exitCode=1;});
