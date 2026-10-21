# Ripple Miner development ledger — 2026-10-20/21

- v0.1 recovered: verified Bitcoin double SHA256, Stratum V1 client and CPU benchmark from prior conversation artifact.
- v0.2 preserved: authenticated Dell-compatible controller, v0.1 neuron bridge, ASIC cgminer API probe, basic fleet monitoring and real share loop. Inherited 19 tests initially passed.
- v0.3 new: SQLite nonce-space streams, transactional chunk lease ledger and 64x64xZ voxel addressing; actual hash-worker allocations, stale-job cancellation, failed lease reclaim; adaptive logical slots with measured EWMA throughput.
- v0.3 new: remote authenticated SHA256d agent plus candidate-share revalidation; CPU process + remote agent coexist on local test. TLS required on externally bound remote service.
- v0.3 new: pause/resume dispatch, spatial map/API/dashboard, remote-worker settings, cost estimate (only when contract hourly rate supplied), benchmark comparison script.
- v0.3 tests: original tests retained and new nonce-disjointness, crash/recovery, failed-lease reclaim, session fingerprint, responsive UI markup, remote authorization, local endpoint, end-to-end pool-share verification.
- v0.3 baseline comparison: see `experiments/RESULTS.json`; no improvement claim. GPU, Stratum V2, actual pool credits, real ASIC hashrate and external cloud billing are not tested.

**Preserve:** `legacy/v01_ripple_core_LOCKED.cjs` and inherited Bitcoin consensus hashing algorithms. Maintain package version and source hashes in release archive. Never overwrite historical releases.

## v0.4 — Original colonization context recovery (2026-10-20)

- Recovered **entire original** Mycelium v0.1, v0.2, v0.3, Charlie Forest v1.2, MUSHROOM v3.0, Ring v4.0 sources; traced tested executable behaviors, math and version distinctions.
- Reproduced source suites: 12/12, 17/17, 24/24, 78/78, 64/64, 38/38 tests. v0.2 needed regeneration of bundled sweep data. MUSHROOM/Ring needed full archived dependency/fixture reconstruction.
- Added historical source snapshot manifest with SHA256 hashes; no original file rewritten.
- Added a separate resource-bound local colony admission policy with lattice-neighbor establishment, bounded birth/retirement, workload ownership via unchanged v0.3 SQLite and SHA256d scanner.
- Connected controller policy validation, CLI flag, live process telemetry, dashboard selector, and clickable colony substrate map.
- Added recovery-unit and local mining-pool end-to-end tests. 33 tests passed (including inherited 26).
- Three paired million-hash trials per policy gave 1,652,510.32 H/s conventional vs 1,656,413.82 H/s historical median, only 0.236% above baseline; not statistically established.
- No external pool credentials/earnings, cloud provisioning, native Android APK, Stratum V2 or physical ASIC were tested.
- Remaining: evaluate full source-faithful MUSHROOM/Ring ablations against mining metrics, derive actual historical genome-driven costs and real power telemetry, validate sustained gains and provision authorized deployment only when available.