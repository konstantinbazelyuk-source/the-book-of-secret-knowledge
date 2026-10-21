# Ripple Miner v0.3: algorithms, provenance and real operating limits

## Preserved originals

- `legacy/v01_ripple_core_LOCKED.cjs`: identical to the v0.2 package, which was independently matched to `ripple/native-alpha-v2.0/reference/v01_ripple_core_LOCKED.cjs` in the Secret Book of Knowledge. Original drive `D=2R+1.2G-1.4B`, leaky integration `tau_v=0.5`, refractory `0.1`, adaptation remains unmodified. It changes ASIC telemetry polling only.
- `miner.sha256d`, `miner.header_prefix`, `miner.scan_nonces`, Stratum V1 socket and share acknowledgement are inherited. The original legacy nonce loop still exists when `--spatial-db` is omitted.
- Previous v0.2 tests are retained; new components are additive and isolated.
- Source history: `ripple/mathematics/LINEAGE_AND_UPGRADES.md`, `ripple/recovery-2026-10/COMPLETE_PROJECT_CATALOG.md`, recovered Ripple Mycelium and Digital World Lab v0.5. v0.5's 2D/3D voxel replay used **synthetic spatial scenes**; v0.3 uses real nonce-space addresses, not a claim that its prior scene simulator mined Bitcoin.

## Actual spatial partition

A Stratum job/session fingerprint is:

`work_key = SHA256(JSON_canonical(pool_host, pool_user, Work))`

It includes extranonce1, job parameters, difficulty, ntime and branch data. Under a fixed `work_key` and extranonce2, the worker searches integer nonces in `[0,2^32)`.

A transactional SQLite stream `(work_key,extranonce2)` maintains the next unassigned cursor, and each chunk owns:

`[start_nonce, start_nonce + count)`

The mapping of a monotonically increasing segment index `s` to a 3D logical cell:

- `x = s mod 64`
- `y = floor(s/64) mod 64`
- `z = floor(s/4096)`

This grid is a **new nonce addressing scheme informed by Ripple's voxel study**, not an assertion of a pre-existing exact 64-cell formula. There is no physics effect associated with the coordinate mapping.

SQLite uses a unique `(work_key,extranonce2,start_nonce)` constraint, atomic cursor advancement and WAL journaling. Lease owners are logical scheduling slots, not guaranteed CPU core affinity. A completed cell cannot be reclaimed. Interrupted/incomplete cells may be recomputed after a lease expires, because exact partial computation progress cannot be inferred after a hard crash. Different extranonce2 values modify the coinbase and Merkle root, producing distinct header search spaces.

## Bitcoin mathematical proof-of-work

`h = SHA256(SHA256(header_80_bytes))`

Pool share: `uint256_le(h) <= floor(diff1_target / share_difficulty)`.
Network block candidate: `uint256_le(h) <= target(nBits)`.

Proof-work outputs are verified from the inherited SHA-256 computation and an independently validating local Stratum test server. Local easy-difficulty test shares are **not Bitcoin balances**, and success of a CPU hashing loop is not evidence of economic viability.

## Colony control

`hps_ewma(t)=0.3*hps_sample(t)+0.7*hps_ewma(t-1)`

Measured sample is completed hashes divided by elapsed dispatch-to-return time. The adaptive scheduler first samples unmeasured workers and then selects available logical worker slots based on measured rate. In v0.3 all CPU tasks use a bounded `ProcessPoolExecutor`; logical slot assignments are not pinned to physical OS processes. The persistent scheduler records actual SHA-256d scan completion, failure, stale jobs and recovery. CPU worker count is bounded by v0.2's existing Ripple hardware governor when installed under the same repository, otherwise by a conservative CPU count fallback.

Remote worker: a dedicated HTTPS endpoint (or loopback-only HTTP for local verification/SSH tunnel) accepts authenticated, bounded `{prefix,start,count,share_target,block_target}` work. It does not accept arbitrary shell commands or pool credentials. The coordinator recomputes each candidate's double-SHA-256 proof before passing it to the pool. `hashes_reported` is a signed-in worker report rather than a cryptographic proof that every unsuccessful nonce was calculated. Independent measurement of remote CPU consumption and billing remains provider-dependent.

## Reproducible comparison

Run `python experiments/compare.py --workers 2 --chunk 3000 --batches 40 --rounds 3`.

The two modes use the same `scan_nonces` function, same header prefix, process worker count, nonce ranges and total hashes. One mode uses sequential in-memory allocation; the other persists allocations and completion to SQLite. Real wall-clock runtime includes process startup. The trials alternate order to reduce systematic warmup bias. Energy joules and physical temperatures are not inferred when sensors are missing. Persisted data is useful for recovery but can reduce raw throughput.

## Engineering boundaries

- No actual Antminer, Dell host, production pool authorization, pool payout or cloud purchase was accessed during this build.
- Stratum V2 is not implemented. Integration should use the official Stratum V2 reference translator/proxy separately and test interoperability; never relabel the V1 socket as V2.
- Remote worker TLS certificates are operator supplied; HTTPS validation uses Python's system trust. The integrated test uses loopback HTTP only.
- No mobile APK is included. The responsive dashboard can be accessed from Android over an explicitly configured, secure operator-controlled tunnel; by default it binds to Dell localhost only.
- Financial estimates are derived from supplied data; power is not treated as physically measured unless an actual device reports it. No real pool balance API exists in this version.
