"""Generate the comparison chart and README from the measured benchmark."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'evidence/benchmark.json').read_text())
modes=['original_workers','original_plus_serial_check','memory_cold','memory_warm_session','memory_warm_restart','memory_half_repeated']
labels=['Original workers','Original + serial check','Memory: first encounter','Memory: repeated, same session','Memory: repeated, after restart','Memory: 12 repeated + 12 new']
colors=['#65768b','#536c91','#087e8b','#c58b24','#d7ac5b','#3f99a3']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                     'figure.facecolor':'white','savefig.facecolor':'white','text.color':'#16263e','axes.labelcolor':'#16263e'})
fig,(ax,bx)=plt.subplots(1,2,figsize=(12,5.7),gridspec_kw={'width_ratios':[1.5,1]})
y=np.arange(len(modes))
v=[r['summary'][m]['medianMs'] for m in modes]
lower=[a-r['summary'][m]['minMs'] for a,m in zip(v,modes)]
upper=[r['summary'][m]['maxMs']-a for a,m in zip(v,modes)]
ax.barh(y,v,color=colors,xerr=[lower,upper],capsize=3,error_kw={'ecolor':'#263b52'})
ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_xlabel('Milliseconds (median; whiskers = 3-run range)')
ax.set_xlim(0,max(r['summary'][m]['maxMs'] for m in modes)*1.25)
for i,(a,mode) in enumerate(zip(v,modes)):
 ax.text(r['summary'][mode]['maxMs']+max(v)*.025,i,f'{a:.2f}',va='center',fontsize=9,fontweight='bold')
ax.set_title('Measured local response time',loc='left',fontweight='bold')
workers=[r['summary'][m]['workerJobsPerRun'][0] for m in modes]
hits=[r['summary'][m]['cacheHitsPerRun'][0] for m in modes]
bx.barh(y,workers,color='#087e8b',label='Executed by workers')
bx.barh(y,hits,left=workers,color='#d39b36',label='Reused from memory')
bx.set_yticks(y,[]);bx.invert_yaxis();bx.set_xlim(0,26);bx.set_xlabel('Tasks per run (24 total)')
bx.set_title('Where the answers came from',loc='left',fontweight='bold')
for i,(a,b) in enumerate(zip(workers,hits)):
 if a:bx.text(a/2,i,str(a),ha='center',va='center',color='white',fontweight='bold')
 if b:bx.text(a+b/2,i,str(b),ha='center',va='center',color='#16263e',fontweight='bold')
fig.legend(*bx.get_legend_handles_labels(),loc='lower right',bbox_to_anchor=(.98,.09),ncol=1,frameon=False)
fig.suptitle('Ripple Mycelium with persistent digestive memory',x=.04,ha='left',fontsize=16,fontweight='bold')
fig.text(.04,.025,'24 deterministic CPU tasks x 400,000 rounds; 3 repetitions. Cold memory includes startup, serial checking and writes. Exact repeated-key workload.',fontsize=8.3,color='#53657b')
fig.tight_layout(rect=[0,.16,1,.94])
fig.savefig(ROOT/'docs/memory-comparison.png',dpi=190,bbox_inches='tight')
fig.savefig(ROOT/'docs/memory-comparison.svg',bbox_inches='tight')
plt.close(fig)

rows=[]
for label,mode in zip(labels,modes):
 s=r['summary'][mode]
 rows.append(f'| {label} | {s["medianMs"]:.2f} | {s["minMs"]:.2f}-{s["maxMs"]:.2f} | {s["workerJobsPerRun"][0]} | {s["cacheHitsPerRun"][0]} |')

readme='''# Ripple Mycelium + Digestive Memory v0.1

Ripple's original worker colony now has a persistent memory adapter. It can reuse exact, previously checked work across restarts, store dated observations with their sources, preserve conflicts, retrieve bounded context and honor source deletion.

The original scheduler, neuron equations and specialist mathematics are preserved byte-for-byte. The new code wraps the real v0.2 Node worker-thread colony and connects the existing Python Digestive Memory engine through a private local pipe. It does not replace the colony with renamed ordinary functions.

## What improves

| Before | With the adapter |
|---|---|
| Completed job results were held in one colony instance | Exact checked results persist in SQLite and can be reused after restart |
| Repeating the same task created worker work again | A matching valid memory record can answer without starting workers |
| No general dated observation memory in this scheduler | Structured observations retain sources, effective dates and explicit conflicts |
| No durable task-memory erasure | Deleted exact task identities stay revoked and cannot silently recache |
| Worker completion alone was the task result | New results are serial-parity checked before absorption |

## Run

Node 20+ and Python 3.10+. No third-party runtime package installation is required. Actual tests were run on Linux with the versions recorded in evidence/benchmark.json.

```bash
npm test
npm run demo
npm run benchmark
```

`npm test` verifies 60 original source hashes, regenerates the original omitted synthetic sweep fixture, and runs every included suite: 17 original real-worker tests, 24 original specialist tests, 41 original memory tests, 17 integration tests and 1 multi-process accounting test. **100 tests total passed.**

The demo runs fresh work, repeats it, closes the process and retrieves the results after reopening the same database. Its location observations are synthetic examples. Pass a database path with `node scripts/demo.js ./memory.sqlite` to retain that demo database; otherwise the demo uses and removes a temporary directory.

## Use the real colony through the adapter

```javascript
const {MemoryMycelium}=require('./src/memory_mycelium');

(async()=>{
  const colony=await MemoryMycelium.open({
    dbPath:'./memory.sqlite',
    scope:{tenant:'local',owner:'me',project:'my-research'}
  });
  try {
    const tasks=[{id:1,rounds:400000},{id:2,rounds:400000}];
    console.log((await colony.runBatch(tasks)).telemetry); // fresh work or remembered results
    console.log((await colony.runBatch(tasks)).telemetry); // exact repeated work
    await colony.remember({sourceId:'experiment-1',subject:'bench-A',
      predicate:'condition',value:'dry',observedAt:Math.floor(Date.now()/1000)});
    console.log(await colony.recall('bench-A','condition'));
  } finally {
    await colony.close();
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
```

The current worker payload remains the original deterministic integer kernel (`id`, `rounds`). Structured observations can describe other experiments, but this release does not dispatch arbitrary scientific models or extract facts from unrestricted conversation.

## Measured comparison

![Measured timing and actual worker versus memory answers](docs/memory-comparison.png)

Same 24 tasks x 400,000 integer rounds, three repetitions per mode, four-worker elastic Ripple configuration. Every returned value matched serial computation. Raw measurements: [JSON](evidence/benchmark.json), [CSV](evidence/benchmark.csv).

| Mode | Median ms | Three-run range ms | Worker jobs/run | Memory hits/run |
|---|---:|---:|---:|---:|
__ROWS__

These timings show an exact repeated-work benefit and a cold-path cost. First-encounter memory work includes bridge startup, original worker execution/shutdown, serial checking and persistent writes. Repeated same-session work excludes bridge startup; the restart row includes startup. Memory subprocess shutdown is outside those memory phases. Original rows include worker startup/shutdown; the second baseline also includes serial checking.

Cold and partly new work need not be faster. Do not apply the warm-cache ratio to new questions, model inference, energy use or unrelated workloads. Lookup currently scans the scoped cache history; use an indexed adapter before very large histories. Three repetitions on a shared runtime are not a deployment SLO.

## Memory rules that matter

- Keys bind exact inputs, schema and source fingerprint. Changed parameters or code get a different identity.
- The master checks all new worker outputs before storing any result from that batch.
- Result records and ordinary observations use structurally disjoint derived namespaces; user observations cannot become verified cache results.
- External and low-confidence observations remain quarantined under the inherited policy.
- Dates and evidence receipt cutoffs are separate. Equal-priority conflicting values remain conflicts.
- Deleting a source invalidates its dependent digests. Deleting an exact task key prevents silent re-absorption; later requests can still calculate it afresh.
- Source/digest checks detect recorded integrity problems; the local database remains controlled by the host. Hashes are not protection against an owner forging both content and hashes.

## Files and evidence

| Path | Purpose |
|---|---|
| src/memory_mycelium.js | Original worker-colony wrapper and verified reuse |
| src/memory_bridge.js | Bounded private-pipe lifecycle and protocol validation |
| python/memory_service.py | Typed adapter over the unchanged memory engine |
| vendor/mycelium-v02/ | Preserved original real scheduler and tests |
| vendor/mycelium-v03/ | Preserved specialist math and tests |
| vendor/digestive-memory/ | Existing memory runtime and its original 41 tests |
| SOURCE_PROVENANCE.json / VENDOR_INTEGRITY.json | Repository/archive lineage and 60 exact source hashes |
| test/ | New integration, corruption, namespace, protocol and concurrency tests |
| docs/API.md | Exact API, resource bounds and lifecycle semantics |
| docs/DESIGN.md / PLAN.md | Design choices and completed implementation sequence |
| docs/REVIEW.md | Independent review findings and regression fixes |
| evidence/ | Raw measurements, demo, red/green regressions and verification |

The repository source baseline is `78fd9d3289b7ce9c82d25caf6679d8a4aa42c2ce`. Historical vendor folders are source-only capsule restorations, not a claim to include every old binary, dataset or asset. Original source licenses are retained. No external inference service, miner, credentials or physical hardware was used by this integration.
'''.replace('__ROWS__','\n'.join(rows))
(ROOT/'README.md').write_text(readme)
print('Wrote measured chart (PNG/SVG) and README with all six comparison modes.')
