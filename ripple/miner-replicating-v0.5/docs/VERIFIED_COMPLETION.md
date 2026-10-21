# Acceptance matrix — Ripple Replicating Colony Miner v0.5

| Requirement | Evidence and exact state |
|---|---|
| Preserve original v0.1 source | Pinned SHA-256 and byte-for-byte source in `legacy/`; Node and Python port equivalence test |
| Multiple real master OS processes | `ReplicatingHive` creates independent `multiprocessing.Process` masters when measured hardware has >=2 worker slots; integration tests use Linux cgroup budget of 3 |
| Replicated actual descendant OS workers | Master creates separate processes with inherited genome, original source verification and worker PID; `test_replication.py` |
| Neuron causally controls work | Firing of inherited LIF equations gates actual SHA-256d sub-batches; ablation with gate disabled measured separately |
| Genome inheritance/mutation/selection | Batch and initial threshold vary; parent chosen using measured EWMA; SQLite stores tested genome performance; benefit unproven |
| Unique nonce ranges | Existing transactional `WorkMap`; root verifies every share and marks entire cell complete only after count matching |
| Result absorption | Independent root candidate verification; accepted work written to SQLite and returned to Stratum |
| Demand recruitment/idle contraction | Master burst <=2 per control tick; idle worker retirement and process destruction covered in tests |
| Worker failure and durable recovery | SIGKILL descendant, detect failure, re-claim exact SQLite cell and successfully complete rescanned work; test only on Unix |
| Pool communication | Existing Stratum V1, verified shares from local test pool under replicated and native backend modes |
| Authorized remote worker | Existing bearer-token TLS remote adapter participates simultaneously with locally replicated descendants; verified on loopback only |
| ASIC observation | Inherited cgminer interface, no physical hardware present |
| Native hashing acceleration | Linux C/OpenSSL SHA-256d backend compiled and verified against original Python and genesis vectors; Windows compiled binary not built |
| Android interface | Responsive web UI in existing app; no signed APK and no smartphone network end-to-end test |
| UI controls | Actual start, pause, resume, stop, capacity policy, gene/gate ablations, native backend switch, worker/nonce state, costs; no remote browser accessibility without secure forwarding |
| MUSHROOM/Ring coordination | Preserved archived 27-neuron/eight-colony code and prior tests; not used in active hashing because no verified benefit shown |
| Stratum V2 and GPU | Not implemented |
| Production pool shares, cloud instance, money | **Not verified**: no user credentials, ASIC, cloud purchase authorization, or pool payout evidence available |
| Proven net financial gain | **Not established**. The tested reproducing colony is slower than conventional CPU dispatch on this measured environment. |

## Evidence classification

- **Measured:** local 39+ tests, subprocess PIDs, nonce counts, actual SHA256d time, local verifier share acknowledgements, C/Python CPU benchmark.
- **Calculated:** financial projections from operator-entered inputs and any hourly-rate cloud estimates.
- **Simulated or historical:** original v0.1/Forest/MUSHROOM/voxel experiments with their own fixtures. They remain distinct from independently measured mining operations.
- **Not available:** actual user's Dell specs, physical power meter, production BTC accounting, cloud permissions and cost invoices, real ASIC device.

The release is an **operational research miner** for actual CPU proof of work, not a completed commercially viable bitcoin mining operation. Software clones on fixed local compute do not increase total physical hashing capacity.