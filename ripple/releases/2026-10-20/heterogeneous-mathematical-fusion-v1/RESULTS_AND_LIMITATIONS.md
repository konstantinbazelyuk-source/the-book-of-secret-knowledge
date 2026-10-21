# Results and limitations — Ripple Heterogeneous Fusion v1.0

## Actual execution in the current container

Tests: `python -m unittest discover -s tests -v` passes **15/15** checks at release creation. The tests invoke actual historical 16-cell regulatory, 174-digital-site genomic, 27-cell MUSHROOM and 216-cell Ring engines; test actual HTTP, queue delivery, deterministic replay and original Ripple Repair protected checkpoints, including verified exact recovery after two intentional shard faults and failure after three.

Study: `python run_study.py`: 42 runs (2 seeds × 3 synthetic inputs × 7 architectures), 24 numerical fusion ticks/run. 36 paired ablation comparisons. The independent wall clock is logged per run. Raw outcomes remain in `results/controlled_study.json`. Do not count 1008 model steps as hardware seconds; within a tick each preserved engine has its own timebase.

### Ablations

The final effective RGB output was changed on all six seed/signal combinations by disabling separately: Regulatory v2, six-gene SuperNeuron, MUSHROOM, Ring, and Lab. This proves a numerical effect in the new cross-operator feedback path, **not improved prediction accuracy**. Disabling memory made no final-output difference on exactly repeated training fixtures because predicted and observed RGB coincided; that is preserved, not hidden.

An additional intervention deliberately shifts a repeating input red channel upward by 0.018. With correctly matching waveform training, the memory controller changes the future effective numerical input relative to the memory-disabled version. The added test asserts a nonzero effect (`>0.001` max channel difference). A physiological claim is not supported.

### Other direct checks

- All 16 Regulatory v2 codons instantiate original `DeltaRippleNeuron`, `DaughterTripletNeuron` and `CharlieNeuron` classes, without a default v0.1 LIF cell.
- Original MUSHROOM graph 27 Charlie neurons; original Ring has 8 × 27 Charlie neurons. Delayed Ring deliveries are tested positive under sustained synthetic input.
- Alpha Lab's finite-volume source/transfer has residuals within approximately floating-point rounding. Tested thresholds are recorded by assertions; no physical conservation law is implied.
- Original RPR1 recovery preserves the input/checkpoint bytes and deterministic replay recovers identical effective inputs and archived-network feature hashes for the tested case.
- Browser desktop/mobile controls were exercised using Chromium with a **test-only bridge** that sends their requests to the real Python localhost API. This is not a claim that direct Chromium-to-localhost navigation worked in this restricted environment; direct navigation was blocked by administrator policy.
- `node --check` validates the Node bridge and inline browser JavaScript syntax.

## Status of external deployment

The downloadable package is **executable local source** with a browser-connected numerical engine. Android APK: **not built**. Dell-specific installer: **not built**. Actual hardware: **not connected or benchmarked**. GitHub Actions cloud workflow provided, **not yet independently run against this exact package**. Network APIs and remote deployment are not part of the local HTTP server.

## Unresolved bottlenecks

- The six mathematical coupling coefficients are bounded engineered values, not calibrated via a task-specific fitting procedure.
- Resource and memory costs on the target Android device and Dell laptop are unknown.
- Checkpoint provenance uses file integrity hashes, not a public-key signature. RPR1's recovery ability is limited by its erasure budget.
- The prior XYZ memory's v0.1 sources remain present inside its archived encoder; they are not the central engine but complete migration away from that encoder is a future option.
- No native camera, microphone, EEG or physical EKG stream has been ingested by this new release; its RGB is synthetic or user-set numeric input.
- State replay depends on matched source hashes, deterministic engines, and numerical environment; cross-platform binary-identical floating-point behavior is not automatically established.
- We have not established generalized problem-solving intelligence or autonomous model invention; the implemented feature is causal heterogeneous mathematical computation with bounded memory feedback.