# Ripple Miner development ledger — 2026-10-20/21

- v0.1 recovered: verified Bitcoin double SHA256, Stratum V1 client and CPU benchmark from prior conversation artifact.
- v0.2 preserved: authenticated Dell-compatible controller, v0.1 neuron bridge, ASIC cgminer API probe, basic fleet monitoring and real share loop. Inherited 19 tests initially passed.
- v0.3 new: SQLite nonce-space streams, transactional chunk lease ledger and 64x64xZ voxel addressing; actual hash-worker allocations, stale-job cancellation, failed lease reclaim; adaptive logical slots with measured EWMA throughput.
- v0.3 new: remote authenticated SHA256d agent plus candidate-share revalidation; CPU process + remote agent coexist on local test. TLS required on externally bound remote service.
- v0.3 new: pause/resume dispatch, spatial map/API/dashboard, remote-worker settings, cost estimate (only when contract hourly rate supplied), benchmark comparison script.
- v0.3 tests: original tests retained and new nonce-disjointness, crash/recovery, failed-lease reclaim, session fingerprint, responsive UI markup, remote authorization, local endpoint, end-to-end pool-share verification.
- v0.3 baseline comparison: see `experiments/RESULTS.json`; no improvement claim. GPU, Stratum V2, actual pool credits, real ASIC hashrate and external cloud billing are not tested.

**Preserve:** `legacy/v01_ripple_core_LOCKED.cjs` and inherited Bitcoin consensus hashing algorithms. Maintain package version and source hashes in release archive. Never overwrite historical releases.
