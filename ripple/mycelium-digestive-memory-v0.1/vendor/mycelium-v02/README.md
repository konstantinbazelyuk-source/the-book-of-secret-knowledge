# Ripple Cybernetic Mycelium · v0.2 research fork

**Status:** offline browser simulation verified + real parallel Node.js worker-thread experiment executed and benchmarked. **No physical prototype, trained intelligence, fungal computation, biological electrical sensing, or production-grade distributed consensus.** This is a mathematical software model with actual CPU computation.

This package is **an isolated versioned fork**. It does not modify the original Ripple Neuron, the v0.1 colony, connected repositories, running experiments or live software. The original kernel is byte-for-byte identical to v0.1's `ripple_core_reference.js`; original HTML is archived in `baseline_v0.1/`.

## Start here

1. **Interactive explorer (offline):** open `Ripple-Cybernetic-Mycelium-v0.2.html` in a modern browser, choose workload, cloning control, topology and routing policy. Click **Start**. Its calculation is numerically simulated; all task arithmetic is real, sequential JavaScript execution.
2. **Numerical simulation and complete architecture sweep** (Node.js 20+ recommended, no npm install):
   ```sh
   node src/sweep.js
   node tests/test_v2.js
   cd baseline_v0.1 && node test_colony.js && cd ..
   ```
   `src/sweep.js` executes **72 distinct design configurations × four workload shapes = 288 scenario trials** at 0.05 simulated-second steps. It emits full JSON and CSV. Four stable stimulus profiles are deterministic.
3. **Real CPU work on operating-system threads** (Node.js with `worker_threads`):
   ```sh
   node src/bench_threads.js 64 800000 5
   ```
   Runs 64 tasks, 800,000 integer-loop iterations each, 5 repetitions per policy; emits both raw runs and medians in `data/`. Independent numerical checksum validation occurs **outside the timed section**.
4. **Regenerate graphics** (optional Python with `matplotlib`): `python make_charts.py`. Rebuild offline HTML from versioned source: `python build_explorer.py`.

## What was kept unchanged

The same v0.1 neuron `RippleNeuron.step([R,G,B], dt)` uses exact crossing integration, input weights `D=2R+1.2G-1.4B`, `tau_v=0.5`, refractory `0.1`, rate decay `tau_r=5`, threshold adaptation gain `0.08`, threshold bounds `[0.15,2.5]`, and target one event per model second. Each clone starts with a **new independent kernel instance**; it copies the algorithm, not its parent's transient membrane state. The exact source file is compared automatically against the archived version.

## Two execution paths, not interchangeable

### Deterministic colony simulation (`src/colony_variants.js`)

- Every request comprises 32 integers split into four arithmetic chunks. One Ripple **simulated firing event** lets one worker compute a real sum and sum of squares. The master verifies the recomposed result against an independent expected reduction.
- Nodes hold one queue each. Transfers are **one-hop only**, and job identity is unique. Tree, ring, and mesh are logical graph shapes with instantaneous transfers; no real communication delay, power or network congestion is modeled. The mesh therefore has no penalty for its greater number of links.
- Workers spawn by copying the unchanged kernel and taking queued work from the parent. Growth has a hard cap of 12 by default (user may explore 1–16 in browser). Retiring workers return pending work and reconnect the graph.
- **Growth strategies:** fixed one, fixed four, arrival-only, backlog-only, arrival+backlog responsive, and fused economy+urgency. **Routing:** none, neighbor-push, neighbor work-stealing, pressure-weighted neighbor. **Topologies:** tree, ring, mesh. Total: `6×4×3=72` configurations.
- Four workloads: burst/recovery, steady flow, twin demand peaks, and drought after initial surge. All test curves are deterministic. The numerical sweep assumes no cost to clone or communicate, so worker-seconds is a simulated resource proxy—not electrical energy, memory allocation, or CPU usage.

### Real operating-system threads (`src/parallel_colony.js` and `src/parallel_worker.js`)

- Node `worker_threads` execute a reproducible CPU-bound 32-bit integer hash, with independent input validation and checked exact outputs. A root-owned ledger tracks queued, in-flight, and completed jobs. Worker queues are managed by the master and redistributed along ring/tree/mesh graph edges.
- In `ripple` mode, **each worker's own unchanged Ripple kernel** advances its numerical clock to the next firing event **before** executing one CPU task. Thus a firing event gates work. This time is **accelerated simulated neuron time**, not physical firing in one-second intervals, an electronic oscillator, or a photonic device.
- In `plain` mode, exactly the same deterministic CPU work runs in standard threads without waiting for the simulated Ripple event. Fixed pool and elastic growth versions form conventional controls.
- A worker can crash. Unfinished work is requeued and retried up to the configured budget, and duplicate job IDs are rejected. Completed outcomes are not counted twice. **This is suitable for pure, idempotent computations, NOT exactly-once external side effects.** Recovery has no durable on-disk journal and is not reliable across master process crashes.
- Idle clones retire after a short real-time grace period while the root persists. There is a hard worker cap. An optional `cost-aware` policy keeps only one worker for an all-tiny batch (all unfinished tasks < 50,000 hash iterations), preventing the worker-count explosion for jobs whose parallelism overhead may dominate. That threshold is an **experimentally chosen heuristic**, not an optimized crossover point. No internet or background services are used.

## Fused design: explicit engineering choice

The exploration demonstrates a meaningful trade-off between quick reaction and low occupied capacity. `fused/steal/tree` combines:

- **Independent adaptive neuron per clone**, no changed neuron weights or dynamics.
- **Master oversight** for bookkeeping, integrity and population hard cap.
- **Backlog-based conservation** under mild workload and **urgency escalation** if arrivals exceed 2.5 chunks/s or oldest pending job is older than six simulated seconds.
- **Undirected branching tree** with one-hop neighbor work stealing; each new node inherits half the busy parent's queued work. Tree has only `N−1` links, avoiding assuming all-to-all contacts have zero physical cost.
- **Hysteresis**: grow by at most two nodes per simulated second; hold a low-load condition for 15 seconds before shrinking; at most one retirement per five seconds; never retire the last/root node.

The exact proposed scale equations, not biological laws, are in `docs/DESIGN_FUSION.md`. The user's initial vision of a nutrient-distribution factory is implemented as **bounded task ownership and information flow**, not biological metabolism or intelligence.

## Reproduced numerical results (200 simulated seconds, 84 arriving jobs)

| Policy/routing/tree | Completed | Simulated worker-seconds | Simulated p95 latency | Peak nodes |
|:--|--:|--:|--:|--:|
| Fixed 1 / none | 50 / 84 | 200 | 114.70s | 1 |
| Economy backlog / steal | 84 / 84 | 416 | 9.15s | 4 |
| Responsive adaptive / steal | 84 / 84 | 758 | 1.00s | 6 |
| **Fused urgency / steal** | **84 / 84** | **605** | **1.80s** | **5** |

*These comparisons do not prove faster execution on physical hardware.* The browser fused run was checked in headless Chromium: 84/84 jobs, 336/336 chunks, seven total clones ever created, six retired, one active at the end, 149 one-hop transfers, and no JavaScript exceptions. The mobile view was tested at 390px; a fixed-one control reproduced 50/84 jobs with no horizontal overflow or errors. Screenshots under `charts/` are evidence of the UI tests.

## Real benchmark (measured in this container, not predicted)

Environment: Linux x64, Node 22.16.0, four available logical CPU execution slots (`os.availableParallelism()`), 64 CPU tasks × 800,000 hash iterations each, 5 independent repetitions per configuration. All 64 checksums were verified for every run. Timed region includes thread startup, data handling and CPU work, but excludes the repeated serial reference calculation; do not use as universal performance claims.

| Implementation | Median actual elapsed wall time |
|:--|--:|
| 1 fixed ordinary thread | 143.49 ms |
| 4 fixed ordinary threads | 60.64 ms |
| 4 fixed Ripple-mediated threads | 61.82 ms |
| Elastic 4-thread cap, ordinary | 69.82 ms |
| Elastic 4-thread cap, Ripple-mediated | 64.71 ms |

**Interpretation:** four conventional threads were **2.37×** faster than one on this particular CPU workload by elapsed time. Four Ripple-gated threads were approximately **1.9% slower** than four conventional threads in the median measured run. Adaptive pool runs are noisier and do not demonstrate a consistent advantage. In particular, *the neuron has not been shown to outperform a conventional scheduler or to learn*.

## Additional measured test: when cloning is wasteful

A second three-repetition experiment sent 64 jobs with three different CPU intensities through a single ordinary worker, four ordinary workers, four Ripple-mediated workers, and a new **cost-aware Ripple colony** that holds at one worker for small jobs. These timings include worker startup. This supports **not creating clones for a trivial task load**, without proving the 50,000-iteration threshold is optimal.

| Iterations / job | One ordinary thread | Four ordinary threads | Four Ripple threads | Cost-aware Ripple |
|---:|---:|---:|---:|---:|
| 5,000 | 29.79 ms | 38.60 ms | 38.77 ms | 33.19 ms |
| 100,000 | 40.93 ms | 33.58 ms | 36.85 ms | 36.19 ms |
| 800,000 | 134.04 ms | 61.38 ms | 60.55 ms | 67.97 ms |

These are **measured**, not simulated, and vary with system noise. The cost-aware policy avoids unnecessary clone creation for tiny work but adds scheduling/clone startup overhead and is not consistently faster. Full trial rows: `data/CPU_intensity_crossover.json`. Visualization: `charts/measured_task_granularity.png`.

## Testing evidence

- Archived v0.1 `test_colony.js`: **12/12 passed** using copied archive.
- New `tests/test_v2.js`: **17/17 passed**, including exact kernel preservation, all configuration accounting, branching connectivity during repeated retirement, deterministic replay, verified arithmetic composition, true threads, cancellation/retirement, duplicate rejection, crash of active worker, and crash of only/root worker with recovery.
- `data/v2_tests.txt`, `data/thread_benchmark.json`, `data/CPU_intensity_crossover.json`, `data/variant_sweep.json`, `data/selected_design_comparison.csv` contain logs and data for re-analysis.
- Outcomes were executed in the author's test environment; users must rerun on their own environments to replicate performance numbers.

## Limits and research priorities

1. **Master remains a single point of failure**: create durable transaction journal + restart recovery, with explicit command idempotency for side-effecting tools.
2. **Transport physics absent** in the numerical model: simulate delays, partitions, link capacities and message overhead; only then compare tree versus ring versus mesh fairly.
3. **No learned weights or semantic understanding**: task partitioning is predefined and numerical. Route policy is engineered, not self-trained.
4. **Stimuli are software-normalized RGB**, with red=.35 for active queues. This is not a measurement of an optical E or B field or fungal electrical signaling.
5. **Real power/energy not measured**. CPU-time and RSS figures in the raw benchmark are OS reports, not calibrated energy meters. The measured worker-thread demo uses software-accelerated simulation time for pulses, not time-synchronized optical sensors.
6. **Meaningful next target:** track workload performance and regulated activity simultaneously across real sensor samples and independent physical timing. Compare equal-resource neuron-gated versus non-neuron schedulers before arguing a benefit.

## Real references

- User's archived v0.1 Ripple Neuron HTML original and exact copied source.
- FEMS Microbiology Reviews (2025): *Electrical signaling in fungi: past and present challenges*, https://doi.org/10.1093/femsre/fuaf009 . Evidence of electrophysiological investigations, **not** proof of linguistic/intelligent computation by fungi.
- Node.js standard worker threads: https://nodejs.org/api/worker_threads.html . CPU-oriented parallel threads; operating-system and startup overhead still matter.
- Kubernetes Horizontal Pod Autoscaling control design background: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/ . Used as conceptual engineering background, not copied or integrated.

## Public-use terms

This new experimental source and reports are offered for copying/adaptation under **CC0-1.0**; see `LICENSE.txt`. User-created original Ripple materials are included according to their existing CC0-1.0 release. Third-party names, cited articles and operating system/runtime components do not become CC0 through this package. Free release does not constitute novelty or patent clearance. No repository, web page or external service was changed to prepare this local artifact.
