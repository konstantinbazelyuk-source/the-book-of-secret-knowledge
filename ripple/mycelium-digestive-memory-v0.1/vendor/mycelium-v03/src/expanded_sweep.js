'use strict';
const fs=require('node:fs'),path=require('node:path');
const {SpecialistColony,workloads}=require('./specialist_colony');
const types=['balanced','learning','product','study','shift','burst'];
const growth=['fixed4','specialists4','v2-heuristic','capacity-general','capacity-specialist'];
const routes=['leastqueue','affinity','learned','roundrobin'];
const graphs=['tree','ring','mesh'];const fb=['original','hybrid-fast'];
function run(){const rows=[];
 for(const g of growth)for(const r of routes)for(const topo of graphs)for(const t of types)for(const neuron of fb){
   const colony=new SpecialistColony({growth:g,route:r,graph:topo,feedback:neuron});const tasks=workloads(t),summary=colony.run(230,tasks);
   if(summary.completed+summary.pending!==tasks.length||summary.partsFinished>tasks.length*4)throw Error('integrity mismatch');
   rows.push({profile:t,growth:g,route:r,graph:topo,feedback:neuron,arrivals:tasks.length,...summary,learningApplied:colony.trainingTrace.length});
 }
 const out=path.resolve(__dirname,'../data');fs.writeFileSync(path.join(out,'expanded_colony_trials.json'),JSON.stringify(rows,null,2));
 const best=[];for(const t of types){const full=rows.filter(x=>x.profile===t&&x.completed===x.arrivals);const tops=[...full].sort((a,b)=>a.workerSeconds-b.workerSeconds||a.p95Latency-b.p95Latency).slice(0,4);
 const quickest=[...full].sort((a,b)=>a.p95Latency-b.p95Latency||a.workerSeconds-b.workerSeconds).slice(0,4);best.push({profile:t,feasible:full.length,all:rows.filter(x=>x.profile===t).length,cheapest:tops,fastest:quickest});}
 fs.writeFileSync(path.join(out,'expanded_rankings.json'),JSON.stringify(best,null,2));
 console.log('EXPANDED_TRIALS',rows.length,JSON.stringify(best.map(x=>({profile:x.profile,feasible:x.feasible,all:x.all,cheapest:{growth:x.cheapest[0]?.growth,route:x.cheapest[0]?.route,graph:x.cheapest[0]?.graph,feedback:x.cheapest[0]?.feedback,workers:x.cheapest[0]?.workerSeconds,p95:x.cheapest[0]?.p95Latency},fastest:{growth:x.fastest[0]?.growth,route:x.fastest[0]?.route,graph:x.fastest[0]?.graph,feedback:x.fastest[0]?.feedback,workers:x.fastest[0]?.workerSeconds,p95:x.fastest[0]?.p95Latency}}))));
 return rows;
}
if(require.main===module)run();module.exports={run};
