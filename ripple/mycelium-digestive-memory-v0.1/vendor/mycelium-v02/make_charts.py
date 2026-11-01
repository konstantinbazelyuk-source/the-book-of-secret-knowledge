from pathlib import Path
import json,csv,statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).parent; data=root/'data'; charts=root/'charts'; charts.mkdir(exist_ok=True)
rows=json.loads((data/'variant_sweep.json').read_text());th=json.loads((data/'thread_benchmark_summary.json').read_text())
choices=['fixed1/none/tree','backlog/steal/tree','adaptive/steal/tree','fused/steal/tree']
short={'fixed1/none/tree':'One fixed','backlog/steal/tree':'Economical','adaptive/steal/tree':'Responsive','fused/steal/tree':'Fused'}
burst={r['variant']:r for r in rows if r['scenario']=='burst'}
with (data/'selected_design_comparison.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['scenario','variant','jobs_in','jobs_completed','worker_seconds_simulated','p95_seconds_simulated','relays','peak_nodes'])
 for scenario in ['burst','steady','twin','drought']:
  for name in choices:
   r=next(r for r in rows if r['scenario']==scenario and r['variant']==name)
   w.writerow([scenario,name,r['submitted'],r['completed'],r['workerSeconds'],r['p95Latency'],r['relays'],r['peakNodes']])
fig,ax=plt.subplots(figsize=(9,5.4))
for r in [x for x in rows if x['scenario']=='burst']:
 ax.scatter(r['workerSeconds'],r['p95Latency'],s=24,alpha=.28)
for v in choices:
 r=burst[v];ax.scatter(r['workerSeconds'],r['p95Latency'],s=95,label=short[v]);ax.annotate(short[v],(r['workerSeconds'],r['p95Latency']),xytext=(6,8),textcoords='offset points')
ax.set(xlabel='Simulated active worker-seconds (lower uses fewer virtual resources)',ylabel='95th-percentile simulated job latency (seconds)',title='Ripple colony design exploration: burst workload · 72 configurations')
ax.grid(alpha=.2);fig.tight_layout();fig.savefig(charts/'simulation_design_tradeoffs.png',dpi=150);plt.close(fig)
fig,ax=plt.subplots(figsize=(9.1,5.3))
names=[x['name'] for x in th['aggregate']];values=[x['medianMs'] for x in th['aggregate']]
bars=ax.bar(names,values);ax.bar_label(bars,fmt='%.1f ms',padding=3)
ax.set(xlabel='Measured Node.js configurations',ylabel='Median wall time (ms; 5 trials)',title='Real worker-thread execution: 64 CPU jobs × 800,000 iterations');ax.set_ylim(0,max(values)*1.17)
ax.tick_params(axis='x',labelrotation=18);ax.grid(axis='y',alpha=.2);fig.tight_layout();fig.savefig(charts/'measured_thread_benchmark.png',dpi=150);plt.close(fig)
# Same workload, but generated deterministic state histories for different policies.
import subprocess
js='''const {run}=require('./src/sweep');for(const s of ['backlog','adaptive','fused']){const r=run(s,'steal','tree','burst');console.log(JSON.stringify({scale:s,summary:r.summary,snapshots:r.snapshots}));}'''
proc=subprocess.run(['node','-e',js],cwd=root,capture_output=True,text=True,check=True)
variants=[json.loads(line) for line in proc.stdout.splitlines()]
fig,ax=plt.subplots(figsize=(9,4.8))
for v in variants:
 ax.step([s['t'] for s in v['snapshots']],[s['workers'] for s in v['snapshots']],where='post',label=v['scale'])
ax.set(xlim=(0,200),ylim=(0,12),xlabel='Simulated time (seconds)',ylabel='Active neuron clones',title='Workload-driven replication and retirement · identical 84-job sequence')
ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(charts/'population_dynamics.png',dpi=150);plt.close(fig)
summary={'configuration_count':len(set(x['variant'] for x in rows)), 'scenarios':len(set(x['scenario'] for x in rows)),'scenario_trials':len(rows),'selected':[{'variant':v,'burst':burst[v]} for v in choices],'real_medians_ms':{x['name']:x['medianMs'] for x in th['aggregate']}}
(data/'experiment_summary.json').write_text(json.dumps(summary,indent=2))
print('Charts and selected designs created',summary['configuration_count'],summary['scenario_trials'])

# Real workload-intensity crossover: separate from 5-repetition principal experiment.
cross=json.loads((data/'CPU_intensity_crossover.json').read_text())
fig,ax=plt.subplots(figsize=(9.4,5.2))
order=['single-plain','four-plain','four-ripple','cost-aware-ripple']
for name in order:
 points=[x for x in cross['summary'] if x['mode']==name]
 ax.plot([x['rounds'] for x in points],[x['medianWallMs'] for x in points],marker='o',label=name)
ax.set(xscale='log',xlabel='CPU hash iterations per job (log axis)',ylabel='Measured median end-to-end time (ms; 3 trials)',title='Real threading crossover: 64 jobs, three CPU intensities')
ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(charts/'measured_task_granularity.png',dpi=150);plt.close(fig)
