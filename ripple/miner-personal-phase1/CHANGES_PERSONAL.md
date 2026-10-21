# Personal Miner functional repair changelog

- Standard single-CPU hashing no longer waits for a fresh OS process pool to spawn before performing the first real hash; it uses a thread executor to preserve event-loop responsiveness and improve start-to-first-share latency in the loopback tests.
- Explicit async mining-loop cancellation now waits for descendant cleanup before network reconnect.
- Real pool authorization reported distinctly from socket connection.
- Continuous reconnect operation (`-1`) retains bounded exponential backoff and jitter; bounded retry settings remain backward compatible.
- Optional fallback Stratum pool endpoint with worker identity and TLS selection.
- Profile save/load/delete API and UI. Never saves mining password to plaintext profile file.
- Real Stratum subscribe/authorize probe connected to the dashboard.
- Locally persisted SQLite event history with a history viewing panel.
- Explicit controller cleanup waits for process reader and ASIC monitor threads before closing the local ledger.
- Added personal desktop control window and source-only Windows packaging recipes.
- 50-test full Python suite result: PASS (Linux test environment). No production pool or Windows tests yet.