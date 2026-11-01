# Ripple memory integration implementation plan

Spec: `docs/DESIGN.md`. The user's standing instruction authorizes full execution without intermediate permission gates. Implementation is inline with final independent review.

1. Verify recovered source members, regenerate omitted synthetic sweep data using the original script, and run original suites. Copy the memory runtime and its tests byte-for-byte; record hashes.
2. Write integration tests before implementation: cold worker result then warm hit; different parameters miss; restart hits; scoped observation correction/history/conflict/quarantine; strict deletion and derived invalidation; reserved cache scope; malformed/bounded requests; child-process shutdown.
3. Implement a typed, bounded Python JSON-lines service over the existing memory engine; implement Node request lifecycle and failure handling. No shell or arbitrary code execution.
4. Implement the original-colony wrapper. Validate tasks before side effects; identify them by pinned code/input/schema; serial-check new worker results before storing. Track returned evidence and actual worker reports separately.
5. Measure original execution, cold verified-memory execution, warm reuse and restart reuse on the same deterministic tasks. Compare all outputs; include overhead and failed cases. Generate raw JSON/CSV and a comparison chart.
6. Review, fix reproduced defects, run final verification, create a source/evidence package and commit the additive repository change. Link the concrete result.

Review focus: concurrent/repeated ids, trust crossing from user memory into verified cache, stale/corrupt cache entries, task erasure during later computation, bridge exit/timeout/oversized protocol, no-process/no-batch worker path and unchanged vendor hashes.
