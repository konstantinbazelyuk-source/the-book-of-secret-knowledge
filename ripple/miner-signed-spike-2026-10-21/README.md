# Ripple signed-spike dual-workstream miner — October 21, 2026

## Implemented in the actual mining path

`ripple_miner/spike_axes.py` is a *new mining-specific work adapter*. It does not overwrite the archived original Ripple Regulatory Colony v2.

1. The preserved `ripple_miner/regulatory_wave.py` calls the actual archived 16-cell Delta/Daughter/Charlie network, not the original v0.1 neuron.
2. Every completed 12 nonce-work assignments, the Regulatory Colony performs an actual recurrent update on 8 measured mining-state signals.
3. `SpikeAxisDispatch.wave_update()` measures **signed** changes of the original network's `average_membrane` response relative to its prior output; feature norm gives the denominator for three amplitude bins (`.08`, `.20`). The bins are *new controller parameters*, not recovered equations.
4. Positive (+1,+2,+3) and negative (-1,-2,-3) transitions select preconfigured work-packet sizes, not superficial visual states. `positive` and `negative` are two separately addressable, concurrent **Bitcoin extranonce2 workstreams** (`0,2,...` and `1,3,...`). They use distinct valid 76-byte Bitcoin headers and have nonoverlapping `(extranonce2, nonce)` combinations.
5. Both streams execute actual SHA-256d through the inherited worker pool and the optional verified native scanner; qualifying shares are submitted through inherited Stratum V1.
6. `spatial.py:WorkMap` exclusively leases and commits every interval. Automatic reclaim may reassign an unfinished interval across workers, but each completed interval has only one credited owner. Original signed signal feedback is visible under authenticated `advanced_waveform.spike_axes` runtime telemetry.
7. The complete cryptographic result remains exact double-SHA-256. This feature does not omit SHA-256 rounds, invent a third hardware lane, or multiply physical CPU throughput by creating more logical tasks.

### Verified algorithmic behavior

- Four new tests exercise all six signed positions, real SHA-256d on both axes with nonoverlap, source-verified execution of the advanced 16-cell network, exhaustion behavior, and actual bitcoin header separation.
- Four previous advanced-Regulatory tests pass, including actual local Stratum V1 verifying-pool share acceptance after this source change.
- Four independent **3.0 productive-second** miner runs using the same test machine and real native SHA-256d, two workers, 100000 base nonce batch, and a local pool with realistic-enough validating difficulty to avoid too many share callbacks, yielded:
  - round_robin 5,600,000; signed-wave 8,555,932
  - signed-wave 5,737,988; round_robin 9,100,000
- The order was reversed between rounds, but substantial host/runtime variation remains. The sum was 14,700,000 baseline hashes vs 14,293,920 signed-wave hashes. **No statistically reliable throughput benefit** is established by this brief trial; raw data is in `experiments/spike_work_local_pool_results.json`.
- One attempted C prescreen implementation avoided serializing SHA state for failing nonces, passed exact hash correctness, but was **slower** on the sustained benchmark (approximately 1.44 MH/s vs 1.59 MH/s). It was **not installed into the production miner**.

### Recovered measured comparison mistake

Earlier reports compared a standalone Linux native scanner (~2.04 MH/s), preinstallation Windows native scanner (~1.87 MH/s) and installed-Windows benchmark (~1.41 MH/s). Those are different execution environments and durations. They do not establish that Ripple's advanced waveform caused a loss of 600k H/s. The installed Windows native scanner was explicitly benchmarked without executing the Regulatory network in its `bench` path. An apples-to-apples Dell benchmark remains unmeasured.

### How to use

Select policy `waveform` / Advanced Ripple Regulatory v2. Start mining against an authorized Stratum V1 pool. The signed axes are active automatically; the original source code, ordinary round-robin mode, and the optimized native hasher are retained. Do not assume a locally accepted pool test share corresponds to money paid by a public pool.