# Ripple Cybernetic Mycelium — broad design redrafts and fusion

## A. Problem definition and scope

**Desired behavior:** copy the Ripple Neuron *algorithm* into separately adapting agents; distribute divisible work through local connections; recompose verified outputs; grow only for real pending demand and stop replication at configured budget; scale down on inactivity. A master orchestrates the cycle but is not infallible.

**Not part of this scope:** generate unrequested image models, claim sentience/AI, train weights, access connected users/services, rewrite original Ripple math, interact with robotics or physical EM sensors, claim lightfield field detection, release to public without authorization.

## B. Candidate versions considered and tested

The actual exhaustive parameter space is `growth (6) × routing (4) × topology (3) = 72 configurations`, across four workload profiles for **288 independently executed simulations**. The following redrafts isolate meaningful conceptual versions:

| Redraft | Buildable definition | Advantage | Drawback / decision |
|---|---|---|---|
| A · Original root | One adaptive neuron, fixed capacity | Ground truth and continuity | Backlog grows in spikes; retained as baseline |
| B · Static cellular pool | Four continuously present independent neurons | Predictable startup and low simulated latency | Pays constant resource occupancy; retained control |
| C · Economy hyphae | Spawn from queued chunk demand, local stealing, tree | Conserves simulated worker-seconds | Higher job tail latency; retained selectable |
| D · Rapid responder | Grow based on recent arrivals and backlog, local steal, tree | Low p95 in burst example | Elevated idle clone occupancy; retained selectable |
| E · Distributed ring | Circular neighbor links; bounded-degree contacts | Alternative path and fewer links than mesh | Can be farther from work; retained selectable |
| F · Full mesh | Every active worker linked to every other | Minimal graph hop count in a logical simulation | Unrealistic to treat extra links as free; retained as experimental stressor, not default |
| G · Pressure signaling | Route by queue divided by estimated event rate | Evokes source/sink gradient | May relay excessively and delay completion; retained option |
| H · Work-stealing hypha | Idle clone draws a pending work unit from a busy neighbor | Controls unnecessary pushing and relay inflation | Requires periodic local queue inspection; selected |
| I · Fused dual-demand colony | Switch between economic and urgent capacity policy | Controls tail delay at intermediate virtual resource cost | Tunable heuristic; selected experimental default, NOT universally optimal |
| J · Physical substrate | Real MCU sensors + eventual message buses | Testable field instrument, longer-term path | No bench implementation in this fork; remains proposed |

**Selection rule:** correctness and bounded growth are gates, not scores. A fusion may improve modeled latency but must not change original neuron equations, exceed population caps, lose tasks, or imply more cognition. Under tested conditions, tree+steal was a conservative default. It is **not** proven optimal once link delay, reliability and energy are modeled.

## C. Preserved original mathematical state

Given normalized `x_R,x_G,x_B`:

```
D = 2 x_R + 1.2 x_G - 1.4 x_B
0.5 du/dt = -u + D
u(t+h) = D + (u(t)-D) exp(-h/0.5)
```

Threshold-crossing spikes reset membrane `u=0`, hold `0.1 model s`; activity estimate exponentially decays over `5 model s`; adaptive threshold has gain `0.08` and is clamped to `[0.15,2.5]`. Target is `1 spike / model second`. These values are copied from original reference. **Spikes are not modeled as network packets**: the event grants local work execution; transfers happen through separate master-managed queues.

## D. Population regulation and actual fusion

Let `Q` = queued chunks, `I` = last 10 simulated seconds' mean chunk arrival rate, `A` = age of oldest unfinished job in simulated seconds; `c=0.95` is a *proposed* chunks/s per neuron capacity estimate, `u=0.72` is a target utilization. `C = c*u = 0.684`.

**Backlog economy target:** `N_economy = clamp(ceil(Q/(12*C)),1,N_max)`.

**Responsive target:** `N_responsive = clamp(ceil((I+Q/12)/C),1,N_max)`.

**Fused target:**

```
urgent = (I > 2.5 chunks/model-s) OR (A > 6 model-s)
if urgent:
    N_target = clamp(ceil((0.65*I + Q/9)/C),1,N_max)
else:
    N_target = N_economy
```

All constants are **experimental controller settings**. They do not arise from fungal biology, calibration, or proof of optimum. `N_max=12` for published numerical tests, browser variable 1–16; spawn at most two per second; hold low load for 15 seconds; retire at most one node every five seconds. Root survives. New children receive up to half their parent's queued work. The original Ripple has a separate adaptive firing-threshold loop; population decisions do not rewrite that loop.

The `steal` policy keeps work at its owner until an idle neighbor requests it; each transfer crosses one logical edge per transfer operation. No broadcast, teleportation or uncontrolled task duplication. Dynamic topology rebuilds on clone growth/retirement.

## E. Numerical trial selection

For an identical 200-model-second 84-job burst:

| Variant | Complete | Simulated worker-seconds | p95 job delay (model s) |
|---|---:|---:|---:|
| Single | 50 / 84 | 200 | 114.70 |
| Economy/tree/steal | 84 / 84 | 416 | 9.15 |
| Responsive/tree/steal | 84 / 84 | 758 | 1.00 |
| **Fused/tree/steal** | **84 / 84** | **605** | **1.80** |

The fusion uses ~20% fewer simulated worker-seconds than responsive (`(758-605)/758`) while its p95 delay increases by 0.8 simulated seconds. Relative to economy, p95 improves by 7.35 s while using ~45% more worker-seconds. Not a universal superiority: in the steady profile economy is cheaper **and** lower in p95 than the fused policy. See `data/selected_design_comparison.csv` for all four conditions. This is an explicit Pareto trade-off, not a claim of artificial learning.

## F. Real parallel execution and controls

An independent program uses actual Node.js worker threads, each with its own freshly instantiated Ripple kernel. An additional optional `cost-aware` real-thread policy refrains from making more workers for tasks under a provisional 50,000-loop threshold; the small-task benchmark showed that forcing four threads can be slower than using one. One task is authorized by one event in *software-accelerated model time* before a reproducible 32-bit integer compute. The master maps job ID to a state (`queued`, `inflight`, `done` or `failed`) and accepts completed identity once. Workload movement happens via master-managed per-thread queue and graph neighbor ownership, NOT physical peer-to-peer network messages. There is no distributed consensus.

Failure tested: `worker.terminate()` while the worker is busy, followed by new assignment of unfinished work, also with a single root worker. Pure deterministic work passes exact result checks after retry. There are no external side effects. If a crash occurs after a side effect but before result acknowledgment, ordinary at-least-once replay would potentially repeat it. A production agent requires permission/authorization gates, durable ledger, dedupe keys and side-effect-specific compensations.

Benchmarks were **measured on one 4-execution-slot container**, not extrapolated from the model. See README and raw five-run JSON. Conventional fixed four-thread median 60.64 ms versus Ripple-mediated 61.82 ms; no demonstrated speedup from the neuron.

## G. Next engineering gates (do not conflate with achieved results)

1. Replay late and out-of-order messages, worker failures, and master restarts against an on-disk append-only ledger. Verify exact observed outputs, and at-least-once semantics for all non-idempotent actions.
2. Add edge-latency/queue-congestion simulators and CPU/energy budgets; repeat architecture sweep before selecting topology for the real network.
3. Compare motor/scanner/drone execution adapters on a non-production test harness only after real permissions, physical limit switches, and sensor calibration exist. No remote device command is included in this fork.
4. Add task-specific routing learning with a held-out workload and conventional baselines **only after** the deterministic regulated system is stable. Do not interpret the raw waveforms as reasoning ability.
5. Recreate sensors with recorded spectral intensities and timestamped reference readings; this is a future input module, not something the software currently measures.

## H. Continuity and evidence labels

**Locked:** Original unchanged v0.1 neuron math; independent clones; work redistribution; hard growth cap; original work preserved.

**Current verified:** 288 deterministic simulation trials, browser runs, actual Node worker pool computation, 17/17 new tests, 12/12 old tests, five-thread-benchmark repetitions per configuration.

**Proposed:** Fusion thresholds are heuristics; resource cost and burst response policies are not learned or optimal; physical optics and mycelial signaling remain analogy.

**Obsolete/rejected:** Treating a population spike as emergent intelligence, treating fungi as digital language processors, claiming logical worker multiplication itself increases CPU performance, assuming all-to-all links cost nothing on hardware.
