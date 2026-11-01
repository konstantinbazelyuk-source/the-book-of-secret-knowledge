# Verified integration - 1 November 2026

The completed integration uses the existing real Ripple worker-thread scheduler and unchanged Digestive Memory engine. Verification was performed on Linux with Node v24.22.1 and Python 3.12.14. No inference provider, miner, physical hardware or cloud workload was run.

## Final suite

`npm test` runs all five original/new suites after checking 60 vendor file hashes:

| Suite | Passed |
|---|---:|
| Original v0.2 real worker colony | 17 |
| Original v0.3 specialist experiments | 24 |
| Original Digestive Memory engine | 41 |
| New Node integration | 17 |
| New real multi-process SQLite accounting | 1 |
| **Total** | **100** |

The original v0.2 sweep data is regenerated with its unchanged script because the upstream source-only capsule excludes datasets. No old source test was changed or skipped. Original worker tests retain crash/requeue/root-replacement and contraction coverage.

Integration tests cover actual worker execution, exact-key warm reuse, restart persistence, changed input misses, persistent task revocation, correction/history/source tracing, explicit conflicts, quarantine, digest invalidation, tenant/owner/project isolation, a crafted namespace collision, invalid/duplicate/bounded inputs, empty batches, exact context bytes, subprocess loss, malformed protocol and corrupt cache rejection.

The concurrency test uses two real subprocesses/SQLite connections, a barrier after both stale pre-reads and a fixed fixture clock. It verifies actual stored-row accounting, not a mock receipt. The passing suite and reproducible failed regressions are in evidence/.

## Performance evidence

The six benchmark modes each ran three times on the same 24 deterministic tasks x 400,000 rounds. All 432 returned values were checked against serial computation. Exact timings, per-run worker/memory counts, environment, source fingerprints and timing boundaries are recorded in benchmark.json and benchmark.csv.

Warm runs produced 24 memory hits and zero worker jobs every time, both within a session and after restarting the Python memory process. Half-repeated runs produced 12 worker jobs and 12 hits. Cold runs produced 24 worker jobs, 24 serial checks and 24 new stored results. Results do not imply an improvement for new/unrelated workloads; first-encounter checks/storage add cost. A scoped full scan remains the cache lookup bottleneck at larger histories.

## Source and review evidence

- All 60 preserved source files retain their recorded hashes.
- Benchmark adapter hashes match the final runtime files.
- A fresh independent code review found and verified fixes for a namespace collision and malformed-envelope crash. A concurrent-write telemetry defect was also fixed with a two-process regression and full suite.
- The chart was generated from raw measurements and visually inspected; labels were moved outside range whiskers.
- The standalone integration folder includes original source, new adapter code, tests, executable demo, measurements and API/design notes. Runtime use requires no third-party dependency installation.

The original neuron and scheduler remain separate preserved artifacts. This release adds explicit memory and exact-result reuse; it does not add arbitrary scientific task dispatch or free-form conversational fact extraction. Snapshot digests remain point-in-time artifacts. Erasure does not retract data already returned to another caller or clear backups managed by the host.
