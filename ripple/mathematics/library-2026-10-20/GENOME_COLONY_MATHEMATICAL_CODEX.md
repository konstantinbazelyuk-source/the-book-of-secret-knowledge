# Ripple digital-genome and colony mathematics v0.5

## Invariants (unchanged)

The original JavaScript class `RippleNeuron` is a leaky integrate-and-fire model with weighted channels:

\[D = 2x_R+1.2x_G-1.4x_B,\quad \tau_v \frac{du}{dt}=-u+D\]

The state resets at threshold and enters a refractory interval; feedback changes threshold slowly. The source file SHA-256 is `d75d4208e92f19623b127615bd52b4002e85d2c0a59b76471764b55a24294210` in this and v0.4 packages. No new biology or consciousness is implied.

## New digital genome: typed configuration, not actual DNA

A complete `ripple-genome/1` marker is SHA-256 over a canonical JSON record `{schema,genes,parent}`. The codec sorts keys, checks types and legal ranges, prohibits unknown fields, checks the marker on decode and supports lineage by carrying the parent marker in child records. A mutation is a seeded change to one legal parameter. Genetic selection is *finite stochastic hyperparameter optimization* against an explicit objective. It is NOT mutation of model weights, cryptographic key generation, autonomous intelligence, or a biological genotype.

Genome fields:
- `growth`: single, fixed4, reactive, capacity, economy, hybrid;
- `routing`: roundrobin, leastload, spatial, affinity, learned;
- `graph`: tree, ring, mesh;
- `role`: general or mixed, whose apparent efficiencies are *assumptions* controlled by experiment;
- `feedback`: preserved `original` (no simulated redesign of neuron equations);
- `spawnThreshold`: backlog needed per replica; `retireDelay`: sustained idle wait;
- `maxWorkers`: hard cap; `hopPreference`: *preference* for shorter logical routes; `energyPenalty`: increases the backlog threshold for scaling.

**Design correction after the first sweep:** an early genetic variant could mutate the environmental `hopCost` to zero. This falsely rewarded genetic search for making communications free. It was removed; all genomes are evaluated at an externally fixed `.2 simulated second / hop` delay. The gene `hopPreference` only changes worker selection, not the environment.

## New task/data model

Work is a grid of 100 2D positions or 147 3D positions with independent synthetic occupancy/resource/spectral channels. Tasks enter under burst, shift or stream arrival schedules, are sent to a live worker clone via a graph-distance delay, and only execute after an event from that clone's *original* Ripple neuron. Each task performs actual numeric calculation:

- learning: the v0.3 source's logistic-regression loss and gradient calculation (without a globally trained or self-updating neural classifier in this version);
- product: integer-cent inventory/revenue/cost/stockout aggregation;
- study: inverse-variance synthesis of two synthetic readings, with duplicate input rejection;
- mapping: deterministic 2D/3D coordinate collection and synthetic optical-signal sample with retry on a deliberately clipped input.

**Important non-result:** the mapping task's `occupancy` is supplied directly by the synthetic world oracle, not inferred from light intensity. It validates the *data pipeline*, not computer vision, obstacle recognition or physical scanner ability.

The arrival positions and ground truth are seeded, but the simulated workers do not physically move or perform a genuine network/optical measurement. Topologies cause modeled per-hop latency only. No `worker_threads` are employed in v0.5; v0.2 retains real threading benchmarks.

## Objective and selection

All 4,320 enumeration trials are 6 scaling policies × 5 routing schemes × 3 graphs × 2 role policies × 2 dimensions × 3 arrival profiles × 2 training seeds × 2 service assumptions.

Research objective, deliberately a chosen preference and **not** a mathematical universal optimum:

\[J = 1200 \cdot \text{coverage} - 0.52 \cdot \text{worker-seconds} - 2.5 \cdot p_{95}\text{(latency)} - 0.03 \cdot \text{logical hops}\]

The genome optimizer runs 15 generations, at most 16 candidates in each pool, and evaluates parity service across training seeds 11 and 17. Holdout evaluation is on 41, 43 and 47 and across service modes parity, assumed specialization advantage and reversed advantage. Mutation ancestry is included in its audit ledger. Training metrics are not confirmation of new intelligence.

The fitness cannot be compared with real CPU speed; virtual neuron time and virtual resource-seconds are separate from host elapsed milliseconds.

## Proposed next real mathematics, not yet implemented

- Process noise covariance estimated from *real* AS7341 recordings; add masks and uncertainty thresholds rather than treating clipped samples as valid.
- Coupled assignment/feedback stability, with queue-stability bounds from measured service-rate and arrival-rate distributions. Characterize the regime \(\lambda < c\mu\) rather than claiming stability under all workloads.
- Pheromone-like graph weights updated using verified delivery delay, with exploration/decay and congestion control; separate measured performance from biological analogy.
- Sensor-calibration and physical geometry mapping on a real game engine / robotics testbed; compare with baseline BFS/A*/Dijkstra and conventional workers.
