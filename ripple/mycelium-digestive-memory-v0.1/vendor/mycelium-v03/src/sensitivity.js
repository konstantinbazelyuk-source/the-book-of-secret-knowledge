'use strict';const {SpecialistColony,workloads}=require('./specialist_colony');const fs=require('node:fs'),path=require('node:path');
const rows=[];
for(const mode of ['advantage','parity','reverse'])for(const delay of [0,.15,1])for(const growth of ['fixed4','specialists4','capacity-general','capacity-specialist'])for(const route of ['leastqueue','affinity'])for(const profile of ['balanced','learning','product','study','shift','burst']){
 const c=new SpecialistColony({serviceMode:mode,hopDelay:delay,growth,route,graph:'tree'}),jobs=workloads(profile),s=c.run(230,jobs);
 if(s.completed+s.pending!==jobs.length)throw Error('loss');rows.push({profile,delay,...s,arrived:jobs.length});
}
const dir=path.resolve(__dirname,'../data');fs.writeFileSync(path.join(dir,'service_sensitivity.json'),JSON.stringify(rows,null,2));
for(const mode of ['advantage','parity','reverse']){const sample=rows.filter(r=>r.serviceMode===mode&&r.profile==='balanced'&&r.delay===.15&&r.route==='affinity');console.log(mode,JSON.stringify(sample.map(x=>({growth:x.growth,complete:`${x.completed}/${x.arrived}`,p95:x.p95Latency,workerSeconds:x.workerSeconds}))));}
console.log('SENSITIVITY_TRIALS',rows.length);
