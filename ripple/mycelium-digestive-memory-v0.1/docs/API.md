# Integration API

## Runtime prerequisites

Node 20+ and Python 3.10+; no npm or Python third-party runtime dependency. Actual verification used Node v24.22.1 and Python 3.12.14 on Linux. Windows execution is not asserted by these tests. Pass a Python executable path through `python` when the platform default is unsuitable.

`MemoryMycelium.open({dbPath, scope, python?, requestTimeoutMs?, colonyOptions?})` creates a private Python subprocess. `scope={tenant,owner,project}` is supplied by the host. Fields are nonempty strings up to 256 UTF-8 bytes. Authentication and authorization belong to the host application.

The adapter maps the project into disjoint internal observation/result namespaces. Host-supplied project names cannot directly address either generated namespace. The SQLite file is the durable store; protect it as application data. No HTTP listener is started.

## Real worker execution and memory reuse

`await runBatch([{id,rounds}], {timeoutMs=30000})` accepts at most 128 tasks. Ids are nonnegative safe integers, unique within a batch. Rounds are safe integers in [1,3000000]. These are the exact parameters of the original deterministic integer CPU kernel. Different batches may reuse an id with different rounds; the input keys will differ.

Each key contains a schema id and hashes of the original CPU kernel, worker, scheduler and neuron source, plus id and rounds. The adapter verifies vendored source hashes when opening. A worker result is compared with serial execution of the same pinned kernel before any new results from that batch are absorbed. This checks execution parity; it is not an independent mathematical or scientific discovery.

Memory reuse validates the result schema, task parameters, content digest and source citation. A corrupt selected record is revoked and its task recomputed. Pure repeated hits start no worker colony. Cache writes are typed internal operations and cannot be issued through the ordinary observation method.

Return shape:

```javascript
{
  results: [{id, rounds, cacheKey, value, origin: 'worker' /* or 'memory' */, sourceId}],
  telemetry: {
    cacheHits, cacheRejected, workerJobs, serialChecks,
    memoryWritesStored, memoryWritesRevoked
  },
  colonyReport: null // or the original report plus actualWorkerThreadIds
}
```

`memoryWritesStored` counts actual new events, not idempotent replays. Concurrent identical writes may return `already_known` internally without incrementing this count. Batches and other public operations on one adapter are FIFO and capped at 16 outstanding operations. Separate adapters use separate connections and SQLite transactions; there is no distributed ownership claim.

## Structured observation memory

`remember({sourceId,subject,predicate,value,observedAt,validFrom?,validTo?,expiresAt?,confidence?,origin?})` records a typed observation. Strings are preserved literally; the service builds a source-linked Candidate and calls the existing memory engine. Use factual assertions supplied by the host or by a separately validated extractor. No free-form language understanding is added by this adapter.

Origin defaults to user; tool is accepted under the existing confidence rule; external is quarantined. Confidence defaults to 1 and must be finite in [0,1]. It is an input score, not a measured truth probability. `observedAt` is mandatory. Times are integer UTC epoch seconds. Changed content under the same sourceId rejects; identical retries replay.

`recall(subject,predicate,{asOf?,knownAt?})` returns known, conflict or missing plus sources, quotes and dates. The inherited engine chooses the highest admitted authority then latest applicable effective start. Equal-priority different values remain explicit conflicts. `validTo` is half-open; `expiresAt` is checked against the real clock even for historical queries.

`context(query,{budgetBytes=8192})` returns a compact memory packet. Maximum budget is 65,536 bytes. The checked size is UTF-8 bytes of compact JSON, including complete records, citations and wrapper metadata. It is not a model-token budget. Up to 50 search candidates are considered under the unchanged default memory policy.

`consolidate()` produces timestamped source-dependent observation snapshots. They are not automatically refreshed and are not used as live cache answers.

## Erasure and lifecycle

`forgetSource(sourceId)` removes an observation source, its facts and every dependent digest. It records a replay tombstone. It does not enumerate independent reports under other source ids.

`forgetTask(id,rounds)` revokes the exact task identity under the current source fingerprint. Later requests recompute its result but report a revoked memory write and cannot silently recache that source. A changed program fingerprint is a different task identity. This is exact task-cache erasure, not topic erasure across all future program versions.

`health()` returns separate stored counters for observations and verified results. Stored accepted counts include historical/expired versions, not just currently retrievable values.

`close()` waits for already queued operations and then closes the memory subprocess. New operations reject once closing begins. Memory pipe failure or timeout rejects pending requests and terminates the failed subprocess. Call close in a finally block. It is idempotent.

## Resource and trust boundaries

IPC requests/responses are capped at 1 MiB and the memory request timeout defaults to 10 seconds. Task execution timeout is separate from memory I/O. One timeout failure does not trigger unbounded retries. Unknown protocol operations are rejected.

The underlying memory lookup currently resolves a full scoped cache history, then selects the requested keys. It is suitable for this measured bounded local workload, and needs an indexed key/version lookup before very large histories. Persisting a verified result adds startup, validation, IPC and database costs to cold work. Measure before deciding which workloads to cache.

No miner, arbitrary kernel, remote URL, shell job or external model call is dispatched. Observations are inert data. Provider/model integration, topic-wide erasure, backup policies and additional scientific task adapters remain host work outside this exact-kernel integration.
