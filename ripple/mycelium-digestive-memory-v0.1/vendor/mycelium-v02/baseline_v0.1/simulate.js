// Run: node simulate.js [maxNodes=12] [outputPrefix=results]
const fs=require('node:fs');
const {RippleNeuron}=require('./ripple_core_reference.js');global.RippleNeuron=RippleNeuron;
const {RippleMycelium}=require('./colony.js');
function run(maxNodes=12){
  const c=new RippleMycelium({maxNodes});
  const timeline=[];
  for(let k=0;k<200/c.dt;k++){
    // Fixed deterministic phases, identical for all maxNode configurations.
    const t=c.t;
    if(t<30){if(Math.round(t*20)%100===0)c.submitSyntheticJob();} // every 5s
    else if(t<110){if(Math.round((t-30)*20)%22===0)c.submitSyntheticJob();} // every 1.1s
    else if(t<160){if(Math.round((t-110)*20)%240===0)c.submitSyntheticJob();} // 12s
    c.step();
    if(Math.round(c.t*20)%20===0){c.assertIntegrity();timeline.push(c.snapshot());}
  }
  c.assertIntegrity();
  const final=c.snapshot();
  return {metadata:{durationSeconds:200,dt:c.dt,maxNodes,simulation:true,actualArithmetic:true,
    concurrentWorkers:false,originalKernel:'Ripple v0.1 unchanged'},timeline,final,
    completedResults:[...c.finished.entries()].map(([id,v])=>({id,...v})),
    pendingJobs:c.jobs.size,scaleEvents:c.scaleEvents};
}
if (require.main===module){
 const maxNodes=Number(process.argv[2]??12); const prefix=process.argv[3]??'results';
 const r=run(maxNodes);
 fs.writeFileSync(prefix+'.json',JSON.stringify(r,null,2));
 fs.writeFileSync(prefix+'.csv',['time,nodes,queued,submittedJobs,completedJobs,completedChunks,relays',...
  r.timeline.map(x=>[x.time,x.nodes,x.queued,x.submittedJobs,x.completedJobs,x.completedChunks,x.relays].join(','))].join('\n')+'\n');
 console.log(JSON.stringify({final:r.final,pendingJobs:r.pendingJobs,results:r.completedResults.length},null,2));
}
module.exports={run};
