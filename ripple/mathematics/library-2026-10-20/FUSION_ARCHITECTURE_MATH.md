# Ripple Heterogeneous Mathematical Fusion v1.0 — operational architecture and mathematics

## Verification language

- **[A] Archived source:** code copied byte-for-byte from the named Ripple release.
- **[N] New fusion:** code implemented in `fusion.py`, `node_worker.mjs`, `server.py` or `index.html`, separate from originals.
- **[E] Executed:** recorded in tests / `results` after actual execution.
- **[D] Derived:** mathematics justified from the documented assumptions.
- **[P] Pending:** not an operational capability of this release.

This is a computational architecture, **not an LLM**. It operates on *synthetic* normalized RGB signals. Nothing in these numerical results implies human visual transduction, EKG measurement, direct EEG reading, consciousness or real hardware sensor input.

## 1. Design decision

The original Ripple v0.1 leaky integrate-and-fire (LIF) source is preserved under the integrated parent, but **is not the central computation**. The primary network is an **unmodified archived Regulatory Colony v2** module (`colony/network.mjs`), instantiated with a newly specified 16-codon genome selecting 6 Delta v3, 5 Daughter v3.1 and 5 Charlie v2 neurons, **zero LIF cells by default**. Other branches compute in parallel and feed future steps through a verifiable message queue.

The Regulatory Colony already executes genuine genotype-dependent 8-channel projections, classical complex rotations, bounded recurrence, normalization and the archived neuron implementations. This fusion does not imitate the internal cell updates.

## 2. Computational compartments — original operators, data types and operational connections

| Compartment | Source | Real internal computational operation | Incoming signal | Outgoing typed signal | Connected behavior |
|---|---|---|---|---|---|
| Primary regulatory network | Regulatory Colony v2, `colony/network.mjs` [A] | 16 Delta/Daughter/Charlie cells with genome-defined 8-channel projection, normalization, wave rotation and recurrent difference | Eight bounded numerical channels with current effective RGB and prior numerical subsystem states | 80-element floating numerical feature state; mean sampled membrane | Sent to Colony causal message queue; affects next RGB and MUSHROOM/Ring carrier calculation |
| Genomic neuron | Six-gene SuperNeuron Alpha, `superneuron_multigene.py` [A] | 174 site-specific sequence-selected state filters, conductance and energy | RGB current input | Membrane state, numerical energy and six family signals | Queued for next input and network's eight-channel state |
| MUSHROOM processing graph | MUSHROOM v3, `mushroom/core.py` [A] | 27 unchanged Charlie cells; 108 directed connections with delayed pulse propagation, bounded synaptic plasticity | 24×24 engineered numerical signal carrier | Mean membrane, spikes, graph states | Queued for next RGB and network conditioning |
| Ring cyclic graph | Ring v5 distribution, `ring/core.py` [A] | Eight original MUSHROOM regions = 216 original Charlie cells; ring pulses delayed and coupled oscillators | 24×24 engineered numerical signal carrier | Eight gateways, per-region spikes, phase-order diagnostics, delivered pulses | Queued for next RGB and the eight-channel primary network |
| Alpha Lab mathematical transport | Alpha Labs v1, `engine.mjs` [A] | Conservative 10×10×3 finite-volume numerical exchange with source injections | Current eight channels; first three are RGB | Field-center three channel quantities, channel sums, conservation residual | Queued and influences next RGB |
| XYZ wave memory | Integrated Mathematical Architecture v1, `math_runtime.py` [A] | Three-dimensional trajectory indexing, dual-coordinate matching, prediction | Current effective RGB signal | Retrieved next-RGB expectation or a rejected match | When accepted, queued for next computation via bounded feedback |
| Colony transport scheduler | `fusion.py:TemporalColonyScheduler` [N] | FIFO typed event queue, one-tick delivery, zero same-tick leakage, finite capacity | Actual operators' numeric outputs | Due messages and delivery ledger | Delivers actual messages used by each following step |
| Repair and replay | Ripple Repair Cell v1, `ripple_repair/core.py` [A] | GF(256) four-data/two-parity Reed–Solomon and SHA-256-verified output; fully deterministic input replay | Serialized input + configuration ledger | RPR1 protected copy and verified decoded replay | Restores an executable computation from the same initial configuration |

### What is deliberately not implemented as an active operator

The original **Digital Evolution v0.5 Colony worker auto-scaling heuristic**, **Mycelium v0.3 threshold inversion**, **Genetic Weights v1.7 adaptive selection**, **Ring v5 EEG bridge**, and **Kokoro Ten Higher Laws** are preserved in the research history but are not executing inside this fusion. The new Colony queue is inspired by the archived scheduling/delay equations; it does **not** claim to run the v0.5 optimizer. Those proposals must earn separate integration and testing.

## 3. Typed mathematical communication

A global *fusion tick* index `k` orders calls; **the component's internal model times are not assumed identical**. The original 16-cell regulatory network uses per-cell `dt = 0.1 * genome_clock`, SuperNeuron uses its source-defined `dt`, and MUSHROOM/Ring use `dt = 1/24` model seconds. Coupling is therefore **a causal discrete integration**, not an exactly synchronized physical ODE system.

Define external normalized input `c[k] ∈ [0,1]^3`, effective input `u[k]`, and typed prior reports `z_j[k-1]` from the last completed tick. The new adapter uses:

```
u[k] = clip_[0,1](c[k] + B_r(z_reg[k-1]) + B_g(z_gene[k-1])
                   + B_m(z_mush[k-1]) + B_q(z_ring[k-1])
                   + B_l(z_lab[k-1]) + B_x(z_memory[k-1],c[k])).
```

`B` functions are **engineering-specific**, finite, bounded transfer rules—not biological units and not a fit obtained from independent data. They are explicit in `fusion.py:effective`, and can be individually ablated. Their saturation by clipping is information loss; the software reports the original external and effective values separately, and preserves the unclipped per-channel correction `delayed_correction`.

For example, a real Regulatory Colony mean membrane `m` contributes `q=.028*tanh(m)` to red and `-.4q` to green; a real six-gene controller `v` contributes `.022*tanh(v)` to green and `-.6q` to blue. Other adapters are similarly bounded and explicit in source. **These constants are not optimized hyperparameters**; further calibration should occur under held-out signals.

### 3.1 Colony delivery [N]

For every executed compartment `j`, an event `M=(id,j,output,k,k+1)` is enqueued after its current computation and delivered at **exactly** the next tick. It is *consumed* by `TemporalColonyScheduler.take` and changes the next `prior` map. For this messaging workload:

```
Q[k+1] = Q[k] + accepted_emissions[k] - delivered[k+1]
```

This is a bounded FIFO dispatcher with sequence and delivery accounting. This release doesn't claim independent OS-level scheduling, cloud distributed execution, or task migration; the communication effect is mathematical and executable within a process.

### 3.2 Archived primary network [A]

The v2 regulatory cell's genome triple `(r,g,b)` determines the cell subtype, numerical projection, internal clock, normalization, rotation angle and recurrent coupling. Eight input channels are classically rotated with an energy-bounded complex `passiveGate`, projected to RGB, normalized and fed to the actual historical Delta/Daughter/Charlie kernels. The output is an **80-element feature vector** (16 cells × 5 values). It is a functional genotype, not a decorative string.

### 3.3 Six-gene SuperNeuron [A]

Each sampled nucleotide maps to an explicitly engineered filter time constant and weighting factor; for a locus `i`:

```
x_i[k+1] = x_i[k] + (1-exp(-dt/tau_i)) * (target_i[k] - x_i[k]).
```

The five added transcript families affect the old SuperNeuron excitatory conductance and energy recovery; RHO's original 29 regulators remain in the base engine. The model's intended 174 **digital sites** are not 174 biological genes. Read the original source for constants and provenance pins.

### 3.4 MUSHROOM and Ring [A]

The original MUSHROOM graph has 27 indexed algorithmic processing cells (3×3×3) with directed nearest-neighbor links. Ring runs eight actual MUSHROOM instances with delayed inter-region transmission and a separate numerical phase-order value. `mushroom.step` and `ring.step` use their original archived classes, not a numerical stand-in or image of a network. Their stimulus is a **constructed 24×24 BGR array**, where the input colors and a small quadrant contrast encode different compartment values. **It is not a physical camera measurement.** The network outputs are real computations on synthetic input. Ring source in the v5 distribution is inherited v4 core; this fusion does not call the v5 EEG extensions.

### 3.5 Lab transport [A]

The Alpha Lab original function `diffusionStep(field,w,h,D,dt)` is called each tick over a 10×10 three-channel field with `D=.12`, `dt=.2`. The discrete flux between neighboring scalar cells is

```
F_ij = D*dt*(field_j-field_i)
field_i' += F_ij; field_j' -= F_ij
```

Sum cancellation proves conservation **after explicit source injection**. The test asserts residuals close to machine epsilon. This is a conserved **mathematical signal field**, not a physical photon fluid. The center of this same live field goes to the next tick's input adapter.

### 3.6 XYZ memory feedback [A+N]

The entire Integrated Mathematical Architecture v1 parent is copied unmodified. The genuine `JointWaveRuntime.train` indexes actual XYZ episodes and `predict` requires agreement in fluctuation XYZ *and* an invertible color XYZ coordinate representation. In this fusion, `JointWaveRuntime.step(effective,feedback=False)` continues to record the genuine parent trajectory. A suitable retrieved continuation is **enqueued** and can influence the next tick's math by

```
B_x = memory_alpha * (retrieved_next_rgb - current_external_rgb)
```

Only when a match is confirmed. The original v0.1 neuron remains in the *inherited optional memory encoder*, not the primary compute network. For identical repeated input, the feedback difference may be exactly zero; that is mathematically correct and is retained as a negative test rather than called a failure.

### 3.7 Checkpoint restoration [A+N]

`HeterogeneousRipple.checkpoint` saves the exact numeric input ledger, seeded initial configuration, active compartments and reproducible training-source identifiers. The original `ripple_repair.protect` encodes it using (4 data, 2 parity) shards per stripe. The original `repair` recovers up to two erased/damaged shards **in each protected stripe** and verifies all hashes; 3 damaged shards fail closed. Replaying the decoded ledger recreates the original computational step sequence and compares state digests, subject to matching sources and numerical environment. State replay is not arbitrary self-repair of an unprotected system.

The checkpoint JSON is **not encrypted**; RPR1 provides recoverability/integrity but not confidentiality or adversarial origin authentication.

## 4. Difference between an equation, a component, and computational capability

An equation alone is not a new neuron; a sampled RGB pixel is not a physical photon; a Fourier amplitude is not an energy field. This release requires: (1) authentic algorithm imported; (2) real input; (3) actual state update; (4) observable output; (5) output influences later computation; (6) a working ablation. Noncontributing components stay disabled or flagged for research.

## 5. Evidence and open scientific questions

Read `docs/RESULTS_AND_LIMITATIONS.md` and `results/controlled_study.json` for all runs. The 42-run baseline comparison used two seeds, three synthetic signal patterns, 24 fusion ticks per run and seven configurations. The six non-full configurations are ablations, not separate measures of intelligence. Five families showed changed final outputs in all six seed/signal cases. Memory's exact-repeat final output tied, requiring a slightly shifted input to demonstrate nonzero feedback. This falsified the naive assumption that every recognized pattern has to change a computation.

Open questions:
- How to learn or derive better **typed couplings** instead of choosing small constants by engineering judgment?
- Can native clocks be accurately aligned without overstating continuous-time fidelity?
- Which systems have measurable advantages over simpler baselines on independent functional tasks (not just state perturbations)?
- How do uncertainty and causal interventions from Kokoro Lawspace improve gating without introducing circular evidence?
- How should protected state and input ledger synchronize with the true physical Android/Dell runtime?

## 6. Research precedents

- W. Gerstner, W. Kistler, R. Naud & L. Paninski, *Neuronal Dynamics*, Cambridge University Press / EPFL online textbook, 2014. https://neuronaldynamics.epfl.ch/online/
- J. Dambre, D. Verstraeten, B. Schrauwen & S. Massar, *Information Processing Capacity of Dynamical Systems*, *Scientific Reports* 2:514 (2012), DOI 10.1038/srep00514, https://www.nature.com/articles/srep00514 — informs functional dynamical-memory benchmarks; does not independently validate Ripple.
- Archived Ripple Delta v3.0, Daughter Triplet v3.1, Regulatory Colony v2, MUSHROOM v3.0, Ring v5, Alpha Labs v1.0, SuperNeuron SixGene v0.1, Ripple Repair v1.0, Integrated Mathematical Architecture v1.0: see `SOURCE_PROVENANCE.json` for verifiable byte hashes.
