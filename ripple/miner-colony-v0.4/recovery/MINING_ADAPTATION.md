# Mining adaptation, controls, and operational scope

## One-to-one transfer ledger

| Historic property | Mining counterpart | Executed implementation | Evidence | Status |
| --- | --- | --- | --- | --- |
| Mycelium bounded recruitment | Real CPU worker *admission* | `HistoricalColony.tick(demand=True)` | Unit growth tests, Stratum E2E | Implemented |
| Mycelium parent/child edges | Contiguous available scheduling coordinates | `ColonySite.position`, `adjacency`, `_establish` | Unit adjacency tests | Implemented; logical geometry |
| Mycelium sustained low-demand contraction | Return occupied admission tokens | `_retire` on idle non-root leaves after timing thresholds | Clock-controlled tests | Implemented |
| Mycelium one-owner chunks | Single owner of nonce partition | Preserved `WorkMap.claim()` SQLite uniqueness | E2E and allocation tests | Implemented |
| Forest environmental suitability | Host resource admissibility | `admission_budget()` reading available RAM and accessible temperature | Bounded tests, external sensors not available | Conditional |
| Forest conservation | Token conservation (occupied <= admitted budget) | Active slots bounded by process pool; no synthetic energy supply | Invariant tests | Implemented |
| Forest local knowledge and relay | Propagate worker measurements | Existing local coordinator uses EWMA measured H/s | Instrumented selection; delay not tested | Partial mapping |
| MUSHROOM delayed 27-site neuron graph | Coordination experiment on measured signals | Original preserved; **not wired to pool** | Original tests passed | Research-only |
| Ring 8-colony delayed conductance | Future ablation of control-signal latency | Original preserved; **not wired to pool** | Original tests passed | Research-only |
| Voxel xyz replay | Persistent real nonce chunks | Preserved `spatial.py` SQLite; separate from admissions geometry | Chunk tests and UI map | Implemented |
| Digital genotype | Optimize observed worker configuration | Existing v0.3 tuning; no historical genome wired in | Existing tests | Separate; not fused |
| Real pool mining | Bitcoin SHA256d and Stratum V1 | Existing miner unchanged except policy choice | Actual local verifying pool | Tested locally |

## Integration dependencies

- Dell Windows run: Python 3.11+, available processors, pool credentials, local port `8877`; **not executed on user's Dell**.
- Samsung monitoring: local responsive web interface, secured access/tunnel required; native Android APK **not built**.
- Authorized cloud: existing HTTPS remote worker can be configured manually with a bearer token. **No cloud account, mining permission, cost or earnings verified**.
- ASIC: existing cgminer-compatible API integration; no physical ASIC installed/connected.
- Production share and payout: requires valid external pool credentials and target difficulty; none supplied/used in tests.
- Stratum V2: not implemented; v1 is the actual protocol path.

## Safety/integrity distinction

Work-map uniqueness prevents simultaneous allocation of overlapping nonce ranges for an unmodified work key, but a crashed worker's partially hashed interval may be retried. The remote worker's candidate shares are cryptographically checked by the coordinator. There is no guarantee that a remote worker truthfully scanned every absent nonce merely because it reports completion; such proof is not provided by Bitcoin protocol. Confirmed pool credits are reported as unavailable, never inferred from local accepted test shares.