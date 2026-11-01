'use strict';
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const {MemoryMycelium}=require('../src/memory_mycelium');

async function main(){
 const temporary=!process.argv[2];
 const dir=temporary?fs.mkdtempSync(path.join(os.tmpdir(),'ripple-demo-')):null;
 const dbPath=temporary?path.join(dir,'memory.sqlite'):path.resolve(process.argv[2]);
 const scope={tenant:'local',owner:'example-owner',project:'example-research'};
 let memory=await MemoryMycelium.open({dbPath,scope});
 try{
  const tasks=[{id:101,rounds:20000},{id:102,rounds:20000}];
  const cold=await memory.runBatch(tasks),warm=await memory.runBatch(tasks);
  await memory.remember({sourceId:'observation-a',subject:'fixture',predicate:'location',value:'Dallas',observedAt:100});
  await memory.remember({sourceId:'observation-b',subject:'fixture',predicate:'location',value:'Austin',observedAt:200});
  const historical=await memory.recall('fixture','location',{asOf:150});
  const current=await memory.recall('fixture','location');
  await memory.close();memory=await MemoryMycelium.open({dbPath,scope});
  const restarted=await memory.runBatch(tasks);
  console.log(JSON.stringify({label:'Executed local original workers and persistent memory; observation values are synthetic fixtures',
   cold:cold.telemetry,warm:warm.telemetry,afterRestart:restarted.telemetry,
   historical,current,context:await memory.context('fixture location',{budgetBytes:1500}),
   health:await memory.health(),databaseRetained:!temporary},null,2));
 }finally{await memory.close();if(temporary)fs.rmSync(dir,{recursive:true,force:true});}
}
main().catch(error=>{console.error(error.message);process.exitCode=1;});
