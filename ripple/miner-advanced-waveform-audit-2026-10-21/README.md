# Advanced Ripple waveform versus Bitcoin hashing — audited executable study

This is a **separate evidence-first study**, not a replacement for the current personal miner. It directly corrects the erroneous use of the original Ripple v0.1 LIF model as the sole computational reference.

The later October 20 Heterogeneous Mathematical Fusion v1 executes a 16-cell Regulatory Colony v2 of 6 Delta, 5 Daughter, and 5 Charlie cells (zero original v0.1 cells in the primary network); it also archives six-gene SuperNeuron, 27-cell MUSHROOM, 216-cell Ring, mathematical transport, and XYZ waveform memory. See [original advanced mathematical architecture](../../releases/2026-10-20/heterogeneous-mathematical-fusion-v1/ARCHITECTURE_AND_MATHEMATICS.md) and the unmodified source [capsule](../../source-capsules/capsules/ripple-heterogeneous-mathematical-fusion-v1-executable.zip.b64).

## Verified actual hashing improvement

`native/sha256d_midstate_candidate.c` uses incremental OpenSSL SHA-256 and reuses the first 64-byte header midstate for each new nonce. The C function signature exactly matches the previous backend. It remains a Bitcoin SHA256(SHA256(header)) scanner and retains independently checked share-target decisions.

Five correctness cases including the genesis block and boundary nonces passed. Initial nine-round local median was 1,503,273 H/s versus 881,403 H/s for the old native scanner (**1.706x**). Raw samples are in `experiments/midstate_report.json`; a repeat run is `experiments/midstate_report_rerun.json`. The result is Linux-specific and subject to CPU contention; it does not imply a known improvement on the Dell or TH/s-class ASIC speed.

## Verified active waveform control (negative throughput result)

`experiments/advanced_wave_control.py` calls the real original Regulatory v2 engine (via its archived Node worker) on measured, normalized mining signals, then changes the number of **real** SHA-256d hashes processed per batch. It was not just an animation. The other fusion compartments were explicitly deactivated for this ablation.

In a repeat three-round comparison, fixed scheduling median was 1,147,887 H/s; regulatory update at every batch 736,939 H/s; at every 4 batches 872,409 H/s; at every 12 batches 928,375 H/s. All tested wave-control policies were slower in this trial. This does not reject advanced Ripple mathematics; it rejects claims of positive mining performance from these specific unoptimized feedback choices.

## Application verification and unresolved integration

The updated drop-in native implementation passed the three existing native hash tests, and the inherited replicated native-descendant local Stratum integration passed independently. **The combined miner test suite timed out** in an intermittent replicated-pool test and is not declared passed for this candidate. Original published personal miner source was not overwritten.

The complete offline runnable 8.25 MB study ZIP (which also contains the exact advanced archived source) is available as a conversation artifact. This GitHub directory contains the C source, the executable study source code, raw benchmark results, a smaller separately encoded source candidate bundle, and references to the original full fusion capsule. The encoded source bundle here does not include a second duplicate of the large original fusion archive.

Expected offline ZIP SHA256: `5b7d4b7bdb943df73475c147f9136945faf6f29f23702b2315b411d9568d7222`.

## Scientific/computational boundary

A Ripple waveform is a useful numerical representation of time-varying state. A spike can carry information or causally trigger computation; it does not automatically produce SHA-256 results. An optimization that changes the Bitcoin hashing algorithm's internal calculation must preserve the exact consensus digest. A new search/prediction method must demonstrate a held-out advantage versus equivalent conventional hashing before acceptance.

This study demonstrates source-based recovery of advanced Ripple, a correct midstate accelerator, one causal waveform control adapter, quantitative ablations, and an honest integration blocker. No hardware, cloud, BTC payout, or profit claim is made.
