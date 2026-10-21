# Ripple recovery and GitHub publication process

## Observed workflow from the project's history

1. Identify prior Ripple source names and derivatives from the current conversation, model-accessible past-conversation context, and the user's Library. Favor original releases and source over earlier assistant descriptions.
2. Compare versioned Library ZIP names, SHA-256 originals, and direct source paths against the public Book's Git tree. Existing mathematical registry, release ledger, and earlier source capsule publication are read-only baselines.
3. Retrieve original archives without rewriting them. Check ZIP CRC and reject unsafe paths. Identify duplicate original ZIP bytes by SHA-256 and preserve name aliases.
4. Recover FIRST-PARTY runnable source, firmware, tests, editable CAD source, and mathematical documents. Apply conservative limits; exclude nested predecessor ZIP copies, binary assets, compiled installers, artifacts, secret-looking strings, and unreasonably large inline HTML. **Record exclusions instead of pretending completeness**.
5. Write version/family source ZIP packages with `_SOURCE_PROVENANCE.json`: original ZIP hash, names and aliases, per-member source SHA-256, exact path, bytes, and reasons for source exclusions.
6. Derive Git blob SHA-1 locally over `blob <byte-count>\\0<exact bytes>`. Upload the actual compressed ZIP bytes through a GitHub Git blob with Base64 encoding, verify the returned object SHA matches the calculated value, and attach the blob to its category path through a Git tree.
7. Commit on a public branch, open a PR, review the comparison, merge only when the changes are grounded, then read the default branch and relevant paths to verify publication. Keep the older Book files unmodified.
8. If a source needs runtime validation, run the historical project's own tests in a clean environment; preservation hashes are **not runtime tests**. Keep measured/calculated/simulated evidence separately from device and hardware claims.
9. For future passes, rescan Library, compare full SHA-256 original archives and extracted member hashes, and upload additional source/complete archives without renaming existing verified releases. Log unfinished hardware, installers, and binary assets separately.

## Known completeness boundaries

This batch covers **106 byte-distinct original ZIP packages** across ten research families, containing **3,115 selected source files**, not every historical chat message, Library item, Google Drive or Dropbox folder, every ZIP member, or every executable binary. The prior [release ledger](../releases/PUBLICATION_LEDGER_20261020.md) was a presence audit, not a complete upload. Neither source archiving nor GitHub publication establishes a physical sensor measurement, neural intelligence, or Windows/Android deployment.

## Preservation and rollback

All changes are additive in `ripple/releases/section-source`, `ripple/process`, and `ripple/research-lineage`. Source selection tracks originals by checksum. Older locked neuron mathematics, published artifacts and original Git history are retained.
