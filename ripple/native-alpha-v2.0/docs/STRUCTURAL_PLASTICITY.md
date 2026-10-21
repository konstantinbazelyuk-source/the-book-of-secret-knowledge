# Ripple neuron: activity-dependent structural plasticity v0.2

**Status:** Executed Node.js model with registered Ripple job integration and durable checkpoint/resume.
**Continuity:** Imports the SHA-256-locked original Ripple v0.1 LIF neuron without changing its original equations.
**Decision:** The directed computational connections are activity-dependent: growth, pruning and weight adjustment affect subsequent signals.

## Relationship to the existing runtime

- reference/v01_ripple_core_LOCKED.cjs — original preserved neuron, not modified
- integrations/structural_plasticity.cjs — graph operator around actual RippleNeuron.step(RGB, dt) calls
- ripple_native/jobs.py — a new allowlisted structural_plasticity job using the existing bounded subprocess scheduler
- tests/test_structural.cjs — local Node.js test suite
- ripple_native/structural.py — atomic JSON checkpoints, integrity digest, crash-safe OS locks, no implicit overwrite
- tests/test_structural_plasticity.py — Python runtime and disk-restart integration tests

## Run

In ripple/native-alpha-v2.0, without starting the daemon:

    echo '{"nodes":8,"frames":800,"seed":17}' | node integrations/structural_plasticity.cjs

With the existing laptop daemon, submit this from a PowerShell window:

    .\.venv\Scripts\python.exe -m ripple_native submit structural_plasticity '{"nodes":8,"frames":800,"seed":17}'

To compare against a fixed-connectivity control, add the JSON property "plasticity":false.

Run a persistent network session (PowerShell with the existing local Ripple daemon running):

    .\.venv\Scripts\python.exe -m ripple_native submit structural_plasticity '{"state_policy":"start","state_id":"kokoro-neuron","nodes":8,"frames":240,"seed":17}'
    .\.venv\Scripts\python.exe -m ripple_native submit structural_plasticity '{"state_policy":"continue","state_id":"kokoro-neuron","nodes":8,"frames":560,"seed":17}'

The first command creates a checkpoint under the authorized workspace's neuron_states folder. The second retrieves the same graph weights, neuron membrane/rate/threshold values, spike histories, coincidence matrix, PRNG state and time step. A start with an existing name is rejected, and a continue without a valid checkpoint fails rather than fabricating an initialized state. state_policy=fresh is a stateless run with no disk changes.

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

Seven local Node tests passed, including integrity of the original neuron file, replay, allowed bounds, growth/pruning and numerical effect versus fixed topology. A Python integration test was added to the repository but the full checkout, Dell hardware, and Windows runtime were not tested here.

## Next engineering gate

Graph changes currently last one experiment; they are not persisted between independent jobs. Add versioned, integrity-checked checkpoint/resume before treating this as retained learning. Then accept properly timestamped sensor-derived input and test against external measurements. Preserve the original source and its checksum.


## Persistent state and consistency (v0.2)

Checkpoint envelope has schema ripple.structural.checkpoint/1, a SHA-256 digest of the JSON payload (for accidental corruption detection, not authentication), and the complete numerical model state. It is atomically replaced after a successful job, with the file fsynced before replace. The lock is an OS-managed file lock, which is released if a worker process dies; multiple concurrent jobs with the same state_id are serialized. Existing checkpoints cannot be overwritten using state_policy=start. Node verifies bounds and version/config matches on reload, including link counts and spike conservation. Cross-run deterministic integration uses fixed connection summation order.

Workspace-relative paths are not accepted as state IDs. state_id permits only 1 to 48 ASCII letters/digits/underscore/hyphen. No arbitrary paths, user-supplied raw checkpoint blobs, or global shared folders are authorized through the job interface.

### Local evidence (2026-10-21)

- Original v0.1 checksum verified: d75d4208e92f19623b127615bd52b4002e85d2c0a59b76471764b55a24294210
- With 8 nodes and 800 synthetic frames: activity remodeling grows 16 links, prunes 8, finishing with 24 (416 simulated spikes); static topology remains at 16 links (404 simulated spikes).
- A 240-frame state checkpoint followed by 560-frame resume produced identical full numerical model state to 800 continuous frames in Node local testing.
- Node tests: 7 passed locally. Python storage tests: 5 passed locally with actual OS files and Node subprocesses.
- A Python test of the existing Ripple scheduler dispatch is supplied in the repository and must run on a full checkout; it is not counted as locally verified until that full integration executes.
- No Dell/Windows physical execution, biological neuron calibration or persistent application deployment has been measured in this environment.
