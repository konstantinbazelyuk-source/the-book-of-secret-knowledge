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
- 51-test full Python suite result: PASS (Linux test environment). No production pool or Windows tests yet.
- Windows operator bootstrap (`Install-Ripple-Personal-Miner.cmd`) downloads official Python/Node runtimes and creates a desktop shortcut. This path is untested on Windows because Windows runtime and external DNS were unavailable.
- Local authenticated shutdown endpoint (`/api/application/shutdown`) and real dashboard Shutdown button; targeted shutdown test passed.
- 51/51 suite PASSED after the application-shutdown and bootstrap source additions; Windows bootstrap remains unverified on Windows.