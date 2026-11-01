'use strict';
const fs=require('node:fs');const path=require('node:path');
const {SpecialistColony,workloads}=require('./specialist_colony');
const policies=['single','fixed4','specialists4','v2-heuristic','capacity-general','capacity-specialist'];
const routers=['leastqueue','affinity','learned','roundrobin'];
const tasks=['balanced','learning','product','study','shift','burst'];
function run(growth,route,task,feedback='original',maxNodes=8){const c=new SpecialistColony({growth,route,graph:'tree',feedback,maxNodes});const arrivals=workloads(task);const stats=c.run(230,arrivals);
 if(stats.submitted!==arrivals.length)throw Error('missing input');if(stats.completed+stats.pending!==arrivals.length)throw Error('loss');
 return {task,arrived:arrivals.length,...stats,trained:stats.learningUpdates?c.trainingTrace.length:0};}
function sweep(){const rows=[];for(const p of policies)for(const r of routers)for(const t of tasks)rows.push(run(p,r,t));
 const out=path.resolve(__dirname,'../data');fs.writeFileSync(path.join(out,'specialist_trials.json'),JSON.stringify(rows,null,2));
 const ranking=rows.filter(x=>x.task==='balanced').sort((a,b)=>b.completed-a.completed||a.p95Latency-b.p95Latency||a.workerSeconds-b.workerSeconds);
 fs.writeFileSync(path.join(out,'specialist_balanced_ranking.json'),JSON.stringify(ranking,null,2));
 console.log('COLONY_TRIALS',rows.length,'BALANCED_TOP',JSON.stringify(ranking.slice(0,7).map(x=>({growth:x.growth,route:x.route,completed:x.completed,arrived:x.arrived,p95:+x.p95Latency.toFixed(2),workerSeconds:x.workerSeconds,trained:x.trained}))));
 const failures=rows.filter(x=>x.completed!==x.arrived);console.log('INCOMPLETE_CASES',failures.length,'EXAMPLES',JSON.stringify(failures.slice(0,4).map(x=>({task:x.task,growth:x.growth,route:x.route,completed:x.completed,arrived:x.arrived}))));
 return rows;
}
if(require.main===module)sweep();module.exports={run,sweep};
