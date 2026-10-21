# Recovered advanced Ripple computation and accelerated Bitcoin hashing — October 21, 2026

## Source lineage and priority correction

Earlier Bitcoin miners integrated the original Ripple v0.1 LIF gate into each descendant. That is **not** the latest Ripple computational architecture. The exact archive `Ripple_Heterogeneous_Mathematical_Fusion_v1_Executable.zip` from the user's Library and GitHub source capsule contains a default **16-cell Regulatory Colony v2** engine composed of six Delta v3, five Daughter v3.1, and five Charlie v2 kernels, with **zero original LIF cells** in the primary network. Original preserved MUSHROOM v3 (27 cells), Ring v5 (8 x 27 cells), six-gene SuperNeuron (174 regulatory sites), Alpha Lab transport, and XYZ waveform memory are separate computational compartments with delayed causal feedback. They are distinct from the original Mycelium reproduction mechanism and from SHA-256 hashing.

Verified source evidence: `ripple/releases/2026-10-20/heterogeneous-mathematical-fusion-v1/ARCHITECTURE_AND_MATHEMATICS.md` and the recovered ZIP's unmodified `fusion.py`, `node_worker.mjs`, and `vendor/colony` submodules. Original source archive was inspected; this candidate does not replace the original.

## What was executed

1. Recovered the real `HeterogeneousRipple` class and original `node_worker.mjs`, with 16 Regulatory Colony cells and other optional compartments turned off **for the controlled ablation**.
2. Mapped **actual measured mining signals** to three bounded numerical input channels: remaining-work ratio, last observed hash throughput normalized against a declared rate, and measured share/backpressure fraction. These channels are not light/color or physical neuronal potentials.
3. Executed original Regulatory Colony updates and used its mean membrane output to **causally change real SHA-256d batch size**, instead of simulating dispatch. All nonce ranges were scanned by actual OpenSSL SHA-256d.
4. Compared it with fixed-size hashing batches at equivalent total work, over three rounds per policy.
5. Compared the unmodified miner C hash implementation against a new independent **SHA-256 midstate reuse** candidate with identical ABI, five correctness cases including Bitcoin genesis and boundary nonces, and nine benchmark rounds per candidate.

## Measured results

- Midstate C backend median **1,503,273 hashes/s** vs original C backend **881,403 hashes/s**, ratio **1.706x** in the initial nine-pair local benchmark.
- Separate Regulatory Colony experiment median fixed **1,147,887 hashes/s**; update each batch **736,939**; update every 4 batches **872,409**; update every 12 batches **928,375** (three rounds each). This shows the real mathematical controller affects dispatch but was slower than fixed batching in this benchmark. Earlier independent three-round run measured 1,659,321 vs 1,176,252 hashes/s. Absolute speed varies substantially under shared compute load; do not pool samples from different runs as a single stable CPU rating.
- Existing miner's native backend unit tests **3/3 passed** with the midstate C function substituted into the same ABI.
- Its replicated-descendant native local-pool integration test **1/1 passed** with the replacement backend.
- An attempted full combined test run timed out; the follow-up verbose log locates the stall at `test_replication_e2e.TestReplicatingMinerE2E.test_replicating_sha256d_and_real_pool_acceptance`. Therefore **do not certify this modified package as a fully passed personal miner**. The last published Phase One verified release is unchanged.

## Bitcoin correctness boundary

The second hash and the nonce-dependent second SHA-256 compression remain real SHA-256, not a substitute waveform. SHA-256 of the Bitcoin block header is consensus-defined; the 80-byte header uses a 64-byte first message block and a 16-byte tail. Midstate can be reused only while the first 64 bytes remain identical (job-specific). Bitcoin target checks use the complete final double-SHA-256. There is no demonstrated waveform predictor that avoids the need to calculate a candidate's correct hash.

## Engineering decisions

- Keep advanced Ripple families source-preserved. Do **not** automatically replace their equations with a v0.1 gate.
- Where demand is high, consider **slow-path waveform inference and fast-path native hashing**. Compare callback overhead to actual hashes gained per second, not neuron count or conceptual model times.
- Keep colony population bounded by **measured accessible hardware/remote compute**, not arbitrary static N; the logical search space may expand without a fixed configured master count, but new software objects alone do not increase physical hashes/s.
- Select production optimizations only following repeatable end-to-end stability tests and, where possible, energy-per-hash measurements.
- Unresolved: complete fused waveform+MUSHROOM+Ring real-miner acceptance, Windows native build, production mining account/payout, hot-loop shutdown hang.

## Reproduce

Baseline/midstate backend benchmark from this candidate's separate `experiments/benchmark_midstate.py` (requires access to the original installed miner from the provided source package). Original fusor study `experiments/advanced_wave_control.py` requires the separately archived original Ripple Heterogeneous Fusion v1 ZIP to be extracted under its documented path. The source of truth for raw timed observations is the JSON result records in `experiments/`.