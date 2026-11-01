# Independent review and resolutions

A fresh reviewer inspected the integration source and tests read-only, ran integration tests and targeted subprocess/concurrency reproductions. Original vendor code remained unchanged. The reviewer did not assess the concurrently authored benchmark or report.

| Severity | Reproduced finding | Resolution |
|---|---|---|
| P1 | An observation project name could equal another project's generated cache scope; a forged result could be read as a warm hit | Both observation and result scopes are now derived from the original project under disjoint prefixes. The chosen-project regression first returned workerJobs=0 incorrectly; it now requires real execution and exact output. |
| P2 | JSON `null` on the memory subprocess output caused an uncaught Node error | Validate non-null object envelope, positive integer id, boolean status and expected result/error fields. A regression reproduced the TypeError; malformed envelopes now fail the bridge cleanly. The reviewer also independently verified the corrected process behavior. |
| P3 | Concurrent identical stores could both report `stored`, even though the second core ingest replayed the first event | Honor the core Receipt. A real two-process SQLite regression synchronizes stale pre-reads and uses a controlled fixture clock. It first returned stored/stored; it now returns stored/already_known with exactly one persisted event. |

The reviewer verified FIFO queued operations, revocation during another process's computation, persistent task erasure and matching concurrent results. Final review stated no remaining P1/P2 issue, and recommended the telemetry correction followed by full verification. That correction was made after the final review; no second independent review is claimed.

## Scope decisions

- Benchmark/documentation correctness is checked separately by the implementer, with raw results retained.
- Arbitrary workloads, AI capability and mathematical validity beyond the preserved numeric kernels are not inferred.
- Source/digest checks assume a host-controlled database. A hostile owner able to rewrite data and hashes is outside this local integrity mechanism.
- Cache lookup currently scans the scoped history before selecting keys. Request limits bound protocol/batch sizes; they do not make backend scanning constant-time.
- Deletion prevents new retrieval and same-source recaching. Data already returned to a caller cannot be recalled from that caller.

All fixes have reproducing red/green evidence logs and a final full-suite run. No reported defect remains deferred.
