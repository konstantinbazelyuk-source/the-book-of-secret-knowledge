# Ripple v0.5 final runtime validation — October 21, 2026

This file records final tests without changing the checksum-locked v0.5 ZIP release.

## Verified functionality

- The 89-file source ZIP integrity check passed against every entry in SHA256SUMS.
- The v0.4 33-test regression suite passed before modification. After new multi-master integration, an uninterrupted 39-test run passed before addition of the optional native backend.
- After native integration, targeted final tests independently passed: three C/Python SHA-256d comparison tests, Unix SIGKILL descendant recovery with SQLite re-claim, native descendant SHA-256d pool E2E, and authenticated remote-worker pool E2E.
- A combined post-native full-suite run was attempted but stalled in controller/process teardown and was aborted. **Do not state that the post-native 44+ test suite passed atomically.** The issue is retained for further root-cause investigation.
- The actual authenticated HTTP dashboard returned status 200 on loopback. The page contained the Replicating policy, genetic variation and native backend controls. The authorized /api/state endpoint returned measured local CPU capacity 3 and payout field null.
- The inline dashboard JavaScript passed Node's static syntax check.
- Live Stratum V1 pool tests were against a locally verifying artificially easy test pool, not a production BTC account. No physical ASIC or mining-authorized cloud provider was connected.

## Measured performance and limits

- Conventional CPU process pool median: **534,198 H/s**.
- Replicating colony with genetics and neuron gating median: **350,731 H/s** (34.3% slower).
- Replicating colony without mutations median: **364,686 H/s**.
- Replicating colony with the neuron gate disabled median: **372,295 H/s**.
- Native OpenSSL SHA-256d vs Python scan in a separate single-process test: **1,646,916 versus 1,007,709 H/s**, measured ratio **1.63x**.
- These are single host measurements inclusive of setup where applicable; they are neither Dell nor ASIC measurements, and there is no electricity meter.

## External integration blockers

Pool-authorized production credentials, pool credits/payout account, user Dell machine, native Android APK testing, physical ASIC, Windows native C compilation, and a cloud host whose terms permit mining are not available in the current environment. No financial resources were purchased or used.

## Release source

Full ZIP Base64 under `Ripple-Replicating-Colony-Miner-v0.5.0.zip.b64`.
Expected decoded ZIP SHA-256:
`a6a03d05b898b6af608516b60127ada5c49b6c1e4bf7fa4a309809f289f59e19`.

Do not confuse computational replication with obtaining additional physical hash throughput on a fixed CPU. No mining-revenue benefit of the colony was demonstrated.
