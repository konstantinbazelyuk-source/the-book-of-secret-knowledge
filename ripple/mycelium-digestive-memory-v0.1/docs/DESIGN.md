# Ripple Mycelium + Digestive Memory

The user authorized improving existing Ripple Mycelium with the working Digestive Memory package. Preserve the original neuron, scheduler and specialist mathematics. The source baseline is repository commit 78fd9d3289b7ce9c82d25caf6679d8a4aa42c2ce. All recovered members have recorded source hashes.

## Implementation decision

Wrap the existing real Node worker-thread `ParallelColony` with a persistent Python/SQLite memory subprocess. A private JSON-lines pipe carries typed requests; no network, model, arbitrary job code or miner is used. The Python side uses the existing Digestive Memory engine unchanged.

The wrapper adds durable reuse of exactly identified, serial-parity-checked CPU task results; explicit structured observations; source/date/conflict-aware recall; bounded context; and source deletion. An input tuple includes task id, rounds, schema and hashes of the frozen worker/kernel/scheduler/neuron files. Cache observations live in a separate scope from user observations. Only the master creates verified-result entries after checking worker output against serial execution. This is exact result memoization, not trained expertise or free-form language extraction.

## Public API

`await MemoryMycelium.open({dbPath,scope,python?,colonyOptions?})`; `runBatch([{id,rounds}],{timeoutMs?})`; `remember({sourceId,subject,predicate,value,observedAt,validFrom?,validTo?,expiresAt?,confidence?,origin?})`; `recall(subject,predicate,{asOf?,knownAt?})`; `context(query,{budgetBytes?})`; `consolidate()`; `forgetSource(sourceId)`; `forgetTask(id,rounds)`; `health()`; `close()`.

Misses run the original scheduler; all new outputs are checked before absorption. Hits are checked for schema, exact task identity, content digest and source links. Corrupt hits are rejected and source-revoked, then recomputed. The original scheduler still controls actual worker ownership, retries and contraction. Results forgotten by exact task identity are recomputed when requested but cannot silently repopulate the same deleted cache source. New input/source versions get new task identities.

## Boundaries

Cold misses include serial checking and persistent-write overhead; no universal speed gain is assumed. A warm repeated workload can avoid worker execution. Measure cold, warm, restart-warm and ordinary-colony runs separately, including bridge startup. Cache trust assumes a local database controlled by the host; hashes are integrity checks, not protection against a malicious owner rewriting both data and digests. One wrapper serializes batches and bounds pending work. Original worker crash tests remain unchanged. The memory process owns its SQLite connection; pipe timeout/failure rejects pending requests and closes resources.

## Completion contract

Run original v0.2/v0.3 tests and Digestive Memory's 41 tests, new integration and boundary tests, real subprocess/restart/cache tests, pinned-source checks, a controlled reuse benchmark and an independent code review. Publish tested source and evidence in an isolated new repository directory; preserve existing versions. No edits to the original equations or files. Keep measured CPU execution distinct from stored observations and numeric model results.
