# Ripple lineage and new computational replication — mathematical trace

## Source hierarchy and authority

- `legacy/v01_ripple_core_LOCKED.cjs` is SHA-256 **d75d4208e92f19623b127615bd52b4002e85d2c0a59b76471764b55a24294210**. The unchanged original LIF model and coefficients are the authoritative neuron source. Every independent mining descendant checks that source hash before executing its mathematically inherited model.
- `historical_sources/mycelium-v01/colony.js` contains the original separate logical clone `spawn`, `control`, `spread`, `retireOne`, `step`. Each clone inherits a new RippleNeuron instance with **fresh transient state**, not inherited membrane value. The workload is transferred rather than duplicated. Original control recommendation:

  `recommended = clamp( ceil((arrival_rate + queue_length/12) / (0.95 * 0.72)), 1, max_nodes)`

  Its original experiment is a sequential JS simulation; v0.2 adds genuine Node worker-thread computation. The miner retains growth of at most two descendants per >=1-second interval, default 15 seconds of low demand and five seconds between retirement events. Testing shortens these timing constants *without changing production defaults*.
- `historical_sources/charlie-forest-v12/forest.py` is the separate conserved-resource forest ecology, not physical CPU fabrication. The miner only inherits the **capacity admission** concept from this source, not synthetic biomass or optical coordinates.
- `historical_sources/mushroom-ring/core.py` and `historical_sources/mushroom-ring/187471ff_core.py` preserve the v3 and v4 conductance graph studies. No function from these cores is implied to speed SHA-256d. Integration is intentionally gated by comparative evidence.
- `historical_sources/voxel-study/` preserves the standalone digital world study. The mining coordinates belong only to `ripple_miner/spatial.py` and are contiguous independent nonce partitions, not historical RGB/XYZ image coordinates.

## Exact inherited neuron equations

For normalized RGB `r,g,b`, the neuron uses `D = 2r + 1.2g - 1.4b`. Between spikes, `tau_V du/dt = -u + D`, with `tau_V=0.5`, adaptation time constant `tau_R=5`, refractory interval `0.1`, original initial threshold `0.45`, adaptation gain `eta=0.08`, and threshold bounds `[0.15, 2.5]`. The original implementation calculates crossing times in each step exactly using logarithmic threshold intersection and exponential decay. `ripple_miner/ripple_neuron_port.py` is cross-language tested against that archived JS on multiple excitation/inhibition traces; *this is not an invented neuron*.

In a mining descendant each valid firing event authorizes one execution batch (`batch` SHA-256d searches). If no firing occurs within 20 steps of model time `dt=0.5`, the worker fails explicitly. Thus the neuron changes the execution control path. The original code is unchanged; a genotype can vary the permitted **initial threshold** and **number of nonces per allowed batch**. This entails CPU overhead rather than a guaranteed speedup.

## New hierarchy and contracts

- Root process: owns Stratum credentials, is the sole work allocator, validates candidates, owns SQLite `WorkMap` and `HiveLedger`.
- Master processes: `M=1` for local worker budget 1, otherwise `M=min(W,max(2,isqrt(W)))`; capacity is distributed across independent subcolony masters. The governing *physical* worker budget `W` comes from CPU affinity/cgroup quotas, operator-requested maximum, and accessible memory/temperatures. There is no promise of infinitely many real CPU processes.
- Descendants: inherit the locked mathematical program and a parent genotype, generate their own transient neuron state, and perform actual SHA-256d loops. Hashing occurs in their separate OS PIDs. Every successful share is checked against the independently recomputed digest and the pool target.
- Work ownership: unique `(job_fingerprint, extranonce2, start_nonce)` in SQLite WAL, lease owner, and monotonic nonce cursor. Stale job generations never submit as current work. Reclaimed partially processed assignments can repeat hashes, which is reported as a recovery cost rather than silently double-crediting completed work.
- Absorption: master-to-root result messages are verified, then `WorkMap.finish` writes `hashes_done==count`; the ledger stores lineage, genome, result count, measured descendant elapsed time and transitions.
- Decomposition: idle non-root descendants receive `None` termination, are joined, and release process resources. The first descendant in an active master remains as original Mycelium's persistent root until master shutdown. If the controller unexpectedly dies, masters detect their parent exit; descendants similarly detect their own master exit.
- Genetic selection: offspring inherit mining genotype, mutate batch and initial threshold within explicit bounds, parent choice uses observed EWMA hashing speed. The ledger retains measured genotype throughput, and future colonies can inherit the highest recorded genotype with at least three successful observations. No improvement is asserted without controlled experiment.

## Other limits

`sha256d(header[0:76] + nonce_le32)` is a one-way hash, not encrypted Bitcoin information. Ripple's AES-GCM event cipher (`ripple/mathematics/SIGNAL_POINTS_AND_CIPHER.md` in parent repository) may protect stored events but cannot decrypt proof of work. Software replication can search nonoverlapping nonce spaces across real processors; it cannot increase silicon capacity by creating more in-memory neuron objects.