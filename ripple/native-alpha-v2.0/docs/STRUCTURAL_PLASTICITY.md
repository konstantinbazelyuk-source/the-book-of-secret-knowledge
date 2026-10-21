# Ripple neuron: activity-dependent structural plasticity v0.1

**Status:** Executed Node.js simulation and registered Ripple scheduler integration.
**Continuity:** Imports the SHA-256-locked original Ripple v0.1 LIF neuron without changing its original equations.
**Decision:** The directed computational connections are activity-dependent: growth, pruning and weight adjustment affect subsequent signals.

## Relationship to the existing runtime

- reference/v01_ripple_core_LOCKED.cjs — original preserved neuron, not modified
- integrations/structural_plasticity.cjs — graph operator around actual RippleNeuron.step(RGB, dt) calls
- ripple_native/jobs.py — a new allowlisted structural_plasticity job using the existing bounded subprocess scheduler
- tests/test_structural.cjs — local Node.js test suite
- tests/test_structural_plasticity.py — Python runtime integration tests

## Run

In ripple/native-alpha-v2.0, without starting the daemon:

    echo '{"nodes":8,"frames":800,"seed":17}' | node integrations/structural_plasticity.cjs

With the existing laptop daemon, submit this from a PowerShell window:

    .\.venv\Scripts\python.exe -m ripple_native submit structural_plasticity '{"nodes":8,"frames":800,"seed":17}'

To compare against a fixed-connectivity control, add the JSON property "plasticity":false.

Run tests:

    node --test tests/test_structural.cjs
    python -m unittest discover -s tests -p "test_*.py" -v

## Mathematical rule (proposed, explicit, measurable in code)

Let s_i be the i-th model neuron's spike count during one interval. Its decaying activity trace is

    a_i(t+dt) = a_i(t) exp(-dt/0.55) + s_i(t)

The smoothed pairwise coincidence estimator is

    q_ij(t+dt) = q_ij(t) + [1-exp(-dt/1.8)] [min(a_i, a_j) - q_ij(t)]

At each scheduled remodeling interval (40 frames default):

- Existing weight: w_ij := clamp(w_ij + 0.035(q_ij - 0.15), 0.07, 0.55).
- Existing connection can be pruned after three weak checkpoints (q_ij below 0.10), leaving at least one outgoing connection.
- A new connection can grow if q_ij - 0.012 * ring_distance(i,j) exceeds 0.18.
- Maximum number of incoming and outgoing directed edges is three per neuron.
- The updated directed, weighted graph feeds back into the next frame's original LIF optical input.

This is a computable co-activity model, not a biological causal-inference model or actual growth of physical dendrites. The constants above are design choices, not measurements extracted from the supplied microscope screenshots.

## Default controlled case — executed 2026-10-21

Linux container, Node.js 22.16.0; 8 original Ripple neuron instances; seed 17; 800 frames at dt 0.05; alternating synthetic optical-pulse cohorts.

| Quantity | Plasticity enabled | Plasticity disabled |
| --- | ---: | ---: |
| Initial directed edges | 16 | 16 |
| Grown | 16 | 0 |
| Pruned | 8 | 0 |
| Final directed edges | 24 | 16 |
| Total simulated neuron spikes | 416 | 404 |

Five local Node tests passed, including integrity of the original neuron file, replay, allowed bounds, growth/pruning and numerical effect versus fixed topology. A Python integration test was added to the repository but the full checkout, Dell hardware, and Windows runtime were not tested here.

## Next engineering gate

Graph changes currently last one experiment; they are not persisted between independent jobs. Add versioned, integrity-checked checkpoint/resume before treating this as retained learning. Then accept properly timestamped sensor-derived input and test against external measurements. Preserve the original source and its checksum.
