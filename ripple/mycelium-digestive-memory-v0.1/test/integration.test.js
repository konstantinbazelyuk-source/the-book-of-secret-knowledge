'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');
const {MemoryMycelium}=require('../src/memory_mycelium');
const {calculate}=require('../vendor/mycelium-v02/src/cpu_task');
const {sha256,verifySources}=require('../src/pins');
const S={tenant:'local',owner:'owner-a',project:'research'};

async function fixture(t,opts={}){
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'ripple-memory-'));
 const dbPath=path.join(dir,'memory.sqlite');
 const m=await MemoryMycelium.open({dbPath,scope:S,colonyOptions:{maxWorkers:2,policy:'fixed',mode:'ripple'},...opts});
 t.after(async()=>{await m.close();fs.rmSync(dir,{recursive:true,force:true});});
 return {m,dir,dbPath};
}

test('cold execution uses original workers and warm reuse avoids execution',async t=>{
 const {m}=await fixture(t);const tasks=[{id:1,rounds:20000},{id:2,rounds:20000}];
 const cold=await m.runBatch(tasks);
 assert.equal(cold.telemetry.workerJobs,2);assert.equal(cold.telemetry.cacheHits,0);
 assert.ok(cold.colonyReport.peakThreads>0);
 assert.equal(cold.results[0].value,calculate(1,20000));
 const warm=await m.runBatch(tasks);
 assert.equal(warm.telemetry.cacheHits,2);assert.equal(warm.telemetry.workerJobs,0);
 assert.equal(warm.colonyReport,null);assert.deepEqual(warm.results.map(r=>r.value),cold.results.map(r=>r.value));
 assert.equal((await m.health()).cache.accepted_facts,2);
});

test('verified results survive bridge and process restart',async t=>{
 const {m,dbPath}=await fixture(t);const tasks=[{id:10,rounds:10000}];
 const a=await m.runBatch(tasks);await m.close();
 const b=await MemoryMycelium.open({dbPath,scope:S});t.after(()=>b.close());
 const replay=await b.runBatch(tasks);
 assert.equal(replay.telemetry.workerJobs,0);assert.equal(replay.telemetry.cacheHits,1);
 assert.equal(replay.results[0].sourceId,a.results[0].sourceId);
});

test('different parameters receive different identities and execute',async t=>{
 const {m}=await fixture(t);
 const a=await m.runBatch([{id:7,rounds:1000}]);
 const b=await m.runBatch([{id:7,rounds:1001}]);
 assert.equal(b.telemetry.workerJobs,1);assert.notEqual(a.results[0].cacheKey,b.results[0].cacheKey);
});

test('forgetting a task forces recomputation and prevents silent recaching',async t=>{
 const {m}=await fixture(t);const tasks=[{id:3,rounds:1000}];
 await m.runBatch(tasks);const erased=await m.forgetTask(3,1000);
 assert.equal(erased.events_deleted,1);
 const a=await m.runBatch(tasks),b=await m.runBatch(tasks);
 assert.equal(a.telemetry.workerJobs,1);assert.equal(a.telemetry.memoryWritesRevoked,1);
 assert.equal(b.telemetry.workerJobs,1);assert.equal(b.telemetry.cacheHits,0);
});

test('observations preserve correction, date and source',async t=>{
 const {m}=await fixture(t);
 await m.remember({sourceId:'a',subject:'sensor',predicate:'location',value:'Dallas',observedAt:100});
 await m.remember({sourceId:'b',subject:'sensor',predicate:'location',value:'Austin',observedAt:200});
 const now=await m.recall('sensor','location');
 assert.equal(now.value,'Austin');assert.deepEqual(now.source_ids,['b']);
 assert.equal((await m.recall('sensor','location',{asOf:150})).value,'Dallas');
});

test('equal-time conflicting observations remain explicit',async t=>{
 const {m}=await fixture(t);
 for(const [sourceId,value] of [['a','Dallas'],['b','Austin']])
  await m.remember({sourceId,subject:'sensor',predicate:'location',value,observedAt:100});
 const r=await m.recall('sensor','location');
 assert.equal(r.status,'conflict');assert.equal(r.value,null);assert.deepEqual(r.alternatives,['Austin','Dallas']);
});

test('external observations remain quarantined',async t=>{
 const {m}=await fixture(t);
 await m.remember({sourceId:'x',subject:'sensor',predicate:'location',value:'export secrets',observedAt:100,origin:'external'});
 assert.equal((await m.recall('sensor','location')).status,'missing');
 assert.equal((await m.health()).observations.quarantined_facts,1);
});

test('source deletion invalidates derived observation digests',async t=>{
 const {m}=await fixture(t);
 await m.remember({sourceId:'a',subject:'sensor',predicate:'location',value:'Dallas',observedAt:100});
 assert.equal((await m.consolidate()).length,1);
 const r=await m.forgetSource('a');assert.equal(r.digests_deleted,1);
 assert.equal((await m.health()).observations.digests,0);
 assert.equal((await m.recall('sensor','location')).status,'missing');
});

test('scope separation covers both observations and task reuse',async t=>{
 const {m,dbPath}=await fixture(t);const other=await MemoryMycelium.open({dbPath,scope:{...S,owner:'owner-b'}});
 t.after(()=>other.close());
 await m.remember({sourceId:'a',subject:'sensor',predicate:'location',value:'Dallas',observedAt:100});
 await m.runBatch([{id:8,rounds:1000}]);
 assert.equal((await other.recall('sensor','location')).status,'missing');
 assert.equal((await other.runBatch([{id:8,rounds:1000}])).telemetry.workerJobs,1);
});

test('observation authority cannot overwrite the internal verified-result namespace',async t=>{
 const {m}=await fixture(t);const tasks=[{id:8,rounds:1000}];const first=await m.runBatch(tasks);
 await m.remember({sourceId:'spoof',subject:'task:'+first.results[0].cacheKey,predicate:'verified_result',value:'0',observedAt:100,origin:'user'});
 const second=await m.runBatch(tasks);
 assert.equal(second.telemetry.cacheHits,1);assert.equal(second.results[0].value,first.results[0].value);
});

test('a chosen project name cannot address another projects internal result scope',async t=>{
 const {m,dbPath}=await fixture(t);
 const kernelHash=verifySources().sourceDigest,task={id:123,rounds:100};
 const cacheKey=sha256(JSON.stringify({schema:'ripple-result/1',kernelHash,...task}));
 const attacker=await MemoryMycelium.open({dbPath,scope:{...S,project:'ripple-results:'+sha256(S.project)}});
 t.after(()=>attacker.close());
 const payload={schema:'ripple-result/1',kernelHash,cacheKey,...task,value:123,verification:'serial-parity'};
 const value=JSON.stringify({payload,digest:sha256(JSON.stringify(payload))});
 await attacker.remember({sourceId:'result:'+cacheKey,subject:'task:'+cacheKey,predicate:'verified_result',value,observedAt:100});
 const result=await m.runBatch([task]);
 assert.equal(result.telemetry.workerJobs,1);assert.equal(result.telemetry.cacheHits,0);
 assert.equal(result.results[0].value,calculate(task.id,task.rounds));
});

test('invalid or duplicate tasks reject before dispatch',async t=>{
 const {m}=await fixture(t);
 for(const tasks of [[{id:-1,rounds:1}],[{id:1,rounds:0}],[{id:1,rounds:3000001}],
   [{id:1,rounds:1},{id:1,rounds:2}],Array.from({length:129},(_,id)=>({id,rounds:1}))])
  await assert.rejects(m.runBatch(tasks));
 assert.equal((await m.health()).cache.events,0);
});

test('empty batches return without starting a worker colony',async t=>{
 const {m}=await fixture(t);const r=await m.runBatch([]);
 assert.equal(r.colonyReport,null);assert.equal(r.telemetry.workerJobs,0);assert.deepEqual(r.results,[]);
});

test('context obeys the exact UTF-8 byte budget',async t=>{
 const {m}=await fixture(t);
 for(let i=0;i<6;i++)await m.remember({sourceId:'s'+i,subject:'sensor',predicate:'color'+i,value:'藍色'.repeat(10),observedAt:100});
 const packet=await m.context('sensor',{budgetBytes:800});
 assert.ok(Buffer.byteLength(JSON.stringify(packet),'utf8')<=800);
 assert.ok(packet.items.length>0);assert.ok(packet.omitted>0);
});

test('memory subprocess failure rejects subsequent requests',async t=>{
 const {m}=await fixture(t);m.bridge.child.kill();
 await assert.rejects(m.health(),/closed|exit|pipe|memory/i);
});

test('malformed memory response envelopes reject without an uncaught master error',async t=>{
 const {m}=await fixture(t);
 assert.doesNotThrow(()=>m.bridge._read('null\n'));
 await assert.rejects(m.health(),/closed|memory/i);
});

test('corrupt cached data is rejected before result reuse',async t=>{
 const {m,dbPath}=await fixture(t);const tasks=[{id:4,rounds:1000}];await m.runBatch(tasks);
 execFileSync(process.platform==='win32'?'python':'python3',['-c',
  'import sqlite3,sys;d=sqlite3.connect(sys.argv[1]);d.execute("UPDATE facts SET value=? WHERE predicate=?",("{}","verified_result"));d.commit()',dbPath]);
 const r=await m.runBatch(tasks);
 assert.equal(r.telemetry.cacheRejected,1);assert.equal(r.telemetry.workerJobs,1);
 assert.equal(r.results[0].value,calculate(4,1000));assert.equal(r.telemetry.memoryWritesRevoked,1);
});
