'use strict';
const math=require('./specialist_math'),{workloads,SpecialistColony}=require('./specialist_colony');
const fs=require('node:fs'),path=require('node:path');
const data=workloads('learning').filter(x=>x.type==='learning'),holdout=math.makeLearning(360).slice(220);
function plainSGD(steps){let w=[0,0,0],trace=[];for(const job of data.slice(0,steps)){
 const ans=math.lossGradient(job.items,w);w=w.map((x,i)=>x-.35*ans.gradient[i]/ans.n);trace.push({loss:ans.loss/ans.n,weight:[...w]});}
 return {weights:w,accuracy:math.accuracy(holdout,w),trace};}
function runBench(){const c=new SpecialistColony({growth:'capacity-specialist',route:'affinity'}),simulation=c.run(230,workloads('learning'));
 const learningSteps=c.trainingTrace.length,baseline=plainSGD(learningSteps);
 let measurements=[];
 for(let rep=0;rep<9;rep++){
  let a=process.hrtime.bigint();const colony=new SpecialistColony({growth:'capacity-specialist',route:'affinity'});colony.run(230,workloads('learning'));let b=process.hrtime.bigint();
  const flatJobs=workloads('learning').filter(x=>x.type==='learning');let w=[0,0,0];let d=process.hrtime.bigint();
  for(const job of flatJobs){let g=math.lossGradient(job.items,w);w=w.map((x,k)=>x-.35*g.gradient[k]/g.n);}let e=process.hrtime.bigint();
  measurements.push({rep,colonyMs:Number(b-a)/1e6,conventionalSGDMs:Number(e-d)/1e6,conventionalAccuracy:math.accuracy(holdout,w)});
 }
 const med=a=>[...a].sort((x,y)=>x-y)[Math.floor(a.length/2)];
 const result={kind:'Node process high-resolution clock; nine serial trials; not energy or parallel CPU speed',trainingJobs:data.length,appliedUpdates:learningSteps,
 initialAccuracy:math.accuracy(holdout,[0,0,0]),colonyAccuracy:math.accuracy(holdout,c.weight),baselineSameStepAccuracy:baseline.accuracy,baselineAllJobsAccuracy:measurements[0].conventionalAccuracy,
 modelSimulatedJobLatency:simulation.p95Latency,colonyWallMedianMs:med(measurements.map(x=>x.colonyMs)),flatWallMedianMs:med(measurements.map(x=>x.conventionalSGDMs)),observations:measurements};
 fs.writeFileSync(path.resolve(__dirname,'../data/learning_verification.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({...result,observations:'see dataset'},null,2));return result;}
if(require.main===module)runBench();module.exports={plainSGD,runBench};
