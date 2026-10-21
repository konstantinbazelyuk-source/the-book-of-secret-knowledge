# RIPPLE MINER — Spatial Colony v0.3.0

**Executable Bitcoin SHA256d CPU miner, Stratum V1 client, transactional voxel workload scheduler, authenticated optional remote worker, cgminer-compatible ASIC monitor, and live laptop/mobile-responsive dashboard.** The previous v0.2 components are preserved and extended. No physical Antminer is required to run CPU hash tests.

## Install and run

- Dell/Windows: Python 3.11+; Node.js 20+ if using the legacy Ripple neuron on ASIC telemetry. Extract ZIP and double-click `Run-Ripple-Miner-Windows.cmd`.
- Linux: run `./Run-Ripple-Miner-Linux.sh` (or `python3 app.py`).
- Open `http://127.0.0.1:8877`; paste the local token from `~/.ripple_antminer_v02/api_token.txt` (on Windows `%USERPROFILE%\.ripple_antminer_v02\api_token.txt`).
- Enter a Stratum V1 host/port, pool-authorized worker ID and password. Configure TLS according to pool instructions. Click **Start actual hashing**. Stop/pause/resume controls govern live hashing dispatch. The data and work map are kept under the controller data directory.
- To add an ASIC, first connect/configure the actual device on the LAN with firmware supported by cgminer/BMminer API, then enter its LAN IP and register it in the dashboard. No device is emulated.
- To add a remote authorized compute worker, follow `docs/REMOTE_AND_CLOUD.md`. No remote computer is automatically rented.
- The same responsive HTML is usable on Android via an operator-approved reverse tunnel; this package does **not** include an APK.

## Verified execution

```sh
python -m unittest discover -s tests -v
python miner.py bench --hashes 200000
python experiments/compare.py --workers 2 --chunk 3000 --batches 40 --rounds 3
```

Tests include a local pool which independently validates submitted shares at deliberately easy test difficulty. It pays no BTC. All actual earnings are **unknown** until real production pool account records and payouts are provided.

## What the new architecture does

- Maps non-overlapping `(work_fingerprint, extranonce2, nonce_start, nonce_count)` ranges to real SQLite voxel cells, leases chunks to hashing processes and logs completion/failures. Cells are algorithmic scheduling partitions, not fictional hardware.
- Routes actual `miner.scan_nonces` computational work through real Python OS processes, preserving inherited Stratum V1 operation.
- Supports responsive controls and a clickable map of actual nonce ranges with observed worker identity, hashes and timings.
- Adds a separately operable authenticated remote worker, using HTTPS away from loopback and verifying every submitted candidate share locally.
- Retains the preserved Ripple neuron and original v0.2 ASIC API code; adds measured worker fitness allocation and transparent benchmark comparisons.

## Boundaries

No cloud subscription is configured; pool payouts and ASIC/physical power sensors remain unconnected until an owner supplies appropriate device, network and authorization. A remote worker can mine only on computing infrastructure on which this use is authorized. Stratum V2 is a **future separate protocol integration**, not currently present. `experiments/RESULTS.json` shows a spatial-allocator overhead in the first measured comparison; no guaranteed increase in hashrate or profits is claimed.

See `docs/ARCHITECTURE_AND_MATH.md`, `docs/REMOTE_AND_CLOUD.md`, `DEVELOPMENT_LOG.md`, and `EVIDENCE.json` for full source provenance and testing.

---

# Version 0.4 — Colonization source recovery and CPU admission policy

This version is an **additive** upgrade to v0.3, not a replacement of the verified Bitcoin mining engine. It preserves the inherited `miner.py`, `WorkMap`, remote ASIC/CPU protocol interfaces, Dell-local controller, and browser dashboard. The added `HistoricalColony` is a separate candidate admission policy that actually determines how many **physical CPU process slots** are allowed to accept the next nonce chunks. It does not create more silicon by cloning worker objects.

## Run

- Windows: double-click `Run-Ripple-Miner-Windows.cmd`, then open `http://127.0.0.1:8877` on the same host.
- Linux: run `./Run-Ripple-Miner-Linux.sh`, then open `http://127.0.0.1:8877`.
- In the dashboard set **Colony admission policy → Historical Mycelium + Forest**, enter a real, authorized Stratum V1 mining-pool host/port/worker, and start CPU hashing. The new **Established processor substrate** map updates from live process telemetry. The existing nonce chunk map is a different map, and remains persistent in SQLite.
- Direct CLI: `python miner.py mine --host YOUR_POOL_HOST --port PORT --user AUTHORIZED_WORKER --workers 2 --spatial-db local_cells.sqlite3 --policy historical --seconds 60`. Check provider rules and pool credentials before connecting externally.
- Local independent suite: `python -m unittest discover -s tests -q`.
- Paired real SHA256d scheduling experiment: `python experiments/compare_historical.py`.

See `recovery/COLONIZATION_LINEAGE.md`, `recovery/MATHEMATICAL_SPEC.md`, `recovery/MINING_ADAPTATION.md`, `recovery/EXPERIMENTAL_REPORT.md` and `recovery/SOURCE_MANIFEST.json`. Historical source files were copied byte-for-byte from recovered Library releases and included for inspection, not silently combined.

**Status:** Confirmed real CPU hashing and locally verifying Stratum V1 shares; no confirmed production shares, accepted pool balance, BTC payout, physical ASIC, paid cloud, or Dell/Samsung device benchmark. MUSHROOM and Ring originals are preserved and independently regression-tested, not wired as decorative proxy hashers. Historical policy gains are unproven.