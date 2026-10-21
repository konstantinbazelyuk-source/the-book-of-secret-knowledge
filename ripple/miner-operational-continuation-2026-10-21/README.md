# RIPPLE MINER — Reliability, Native Hashing & Productive Runtime (2026-10-21)

This continuation modifies the existing personal-miner source without changing locked Ripple neuron equations or the Bitcoin Stratum V1 protocol. It is not a verified Dell executable installer nor a BTC earnings claim.

## Executable changes

1. `ripple_miner/replication.py` cooperative master stop, cancels queued work, terminates descendants with bounded escalation and drains queued telemetry to avoid multiprocessing feeder deadlock. An interrupted assignment remains uncompleted in SQLite.
2. `ripple_miner/replicating_mining.py` bounded timed-session cancellation and recoverable work leases. Remote HTTP worker has finite request timeout. Mining durations start when the first completed hash batch arrives; startup has an 18-second progress deadline during timed sessions. Production runs with duration=0 continuously.
3. `ripple_miner/replication.py` retains the original locked JS hash and the independently cross-tested numerical port but removes one unnecessary Node.js process launch **per newly born descendant**. Actual live Ripple neuron spike gating remains active in Python; locked JS original remains unchanged.
4. `ripple_miner/nativehash.py` implements `scan_preferred` so **all spatial policies**, not only reproducing mode, can use the accelerated native backend; checks native results against reference hashes at startup. On native output-buffer exhaustion, the worker falls back to the original Python algorithm without losing shares.
5. `native/sha256d_scan.c` computes exact double SHA-256 using preserved 64-byte SHA-256 midstate, while `native/sha256d_scan_original.c` retains previous implementation.
6. `tests/test_continuation.py` adds native reference parity, safe overflow fallback, and live descendant shutdown plus exact SQLite nonce lease reclaim.

## Evidence

- A single uninterrupted post-optimization suite: **55/55 tests passed** on the available Linux environment. Raw log: `evidence/full_suite_55.log`.
- Native hashing comparison: original **927,170 H/s**, midstate **1,614,895 H/s** median, **1.742x** for the measured nine-round 150,000-hash workload, same host. Raw samples: `experiments/waveform/midstate_report_rerun.json`.
- Local Stratum pool shares are mathematically verified in unit/integration tests, not production-pool payouts.
- Original historical fusion waveform control is retained as a research experiment with a recorded negative throughput outcome; this release does not automatically add its expensive controller to the hashing hot loop.

## How to launch (source)

Requires Python 3.11+ and Node.js 20+ for legacy telemetry; Linux native backend also requires a compatible C compiler and OpenSSL development headers. `python -m unittest discover -s tests -q` performs local tests. To compile optimized native Linux backend, run `./scripts/build-native-linux.sh` (source compilation needs GCC/Clang and OpenSSL). Use the existing launcher, configure an authorized Stratum V1 pool, choose a spatial policy, and enable Compiled CPU hashing if the native library is available and verified.

## Actual acceptance boundary

No Windows-native DLL was compiled, the Windows installer has not been tested on the user's Dell, and no production pool credentials, payout, or mining-approved cloud compute were accessed. The original SHA-256d / Stratum engine and Ripple source are preserved; this is a tested Linux source release, not a declaration of industrial ASIC-class performance.