"""All chart data comes from actual deterministic simulation JSON, never fabricated."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(__file__).parent
load=lambda f:json.loads((D/'data'/f).read_text())
scores=load('feedback_scores.json');rows=load('service_sensitivity.json');expanded=load('expanded_colony_trials.json');learn=load('learning_verification.json')
fig,ax=plt.subplots(figsize=(10,5.8));scores=sorted(scores,key=lambda r:r['mae'],reverse=True)
ax.barh([r['method'] for r in scores],[r['mae'] for r in scores]);ax.set_xlabel('Mean absolute 10-second-window rate error (events per model second)')
ax.set_title('Ripple feedback variants — simulated, selected feasible windows')
fig.tight_layout();fig.savefig(D/'charts'/'feedback_controller_comparison.png',dpi=165);plt.close(fig)
fig,ax=plt.subplots(figsize=(11,6));names=['fixed4','specialists4','capacity-general','capacity-specialist'];loc=np.arange(len(names));bw=.24
for k,mode in enumerate(['advantage','parity','reverse']):
 p=[next(x for x in rows if x['growth']==g and x['profile']=='balanced' and x['serviceMode']==mode and x['route']=='affinity' and x['delay']==.15) for g in names]
 ax.bar(loc+(k-1)*bw,[x['p95Latency'] for x in p],width=bw,label=mode)
ax.set_xticks(loc,names,rotation=12);ax.set_ylabel('p95 job latency (simulated seconds)');ax.set_yscale('log');ax.set_title('Specialist advantage is an assumption — sensitivity analysis');ax.legend(title='Assumed work-unit costs')
fig.tight_layout();fig.savefig(D/'charts'/'specialist_assumption_sensitivity.png',dpi=165);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5.2));names=['Untrained','Ripple-mediated SGD','Conventional SGD']
values=[learn['initialAccuracy'],learn['colonyAccuracy'],learn['baselineSameStepAccuracy']]
ax.bar(names,values);ax.set_ylim(0,1);ax.set_ylabel('Held-out synthetic classification accuracy');ax.set_title('Actual learned logistic regression; conventional SGD matches result')
for i,y in enumerate(values):ax.text(i,y+.012,f'{100*y:.1f}%',ha='center')
fig.tight_layout();fig.savefig(D/'charts'/'learning_vs_conventional.png',dpi=165);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,6));pts=[x for x in expanded if x['profile']=='balanced' and x['completed']==x['arrivals']]
for g in ['fixed4','specialists4','v2-heuristic','capacity-general','capacity-specialist']:
 q=[x for x in pts if x['growth']==g];ax.scatter([r['workerSeconds'] for r in q],[r['p95Latency'] for r in q],alpha=.45,label=g,s=25)
ax.set_xlabel('Simulated worker-seconds');ax.set_ylabel('Simulated p95 latency (seconds)');ax.set_yscale('log');ax.set_title('Balanced workload: complete candidate colonies only');ax.legend(fontsize=8)
fig.tight_layout();fig.savefig(D/'charts'/'colony_latency_resource_tradeoff.png',dpi=165);plt.close(fig)
print('charts',*[p.name for p in (D/'charts').glob('*.png')])
