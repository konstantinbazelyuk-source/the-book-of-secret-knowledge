# Ripple signed-spike dual-workstream: Windows executable and real work evidence

2026-10-21

**Windows workflow**: https://github.com/konstantinbazelyuk-source/the-book-of-secret-knowledge/actions/runs/39678380567 — **completed successfully**.

**Windows installer release**: https://github.com/konstantinbazelyuk-source/the-book-of-secret-knowledge/releases/tag/ripple-signed-spike-win-2026-10-21

## What executes

- The authentic, source-hash-checked 16-neuron Delta/Daughter/Charlie Regulatory Colony v2 runs and produces actual state changes.
- A new *mining-specific* adapter `ripple_miner/spike_axes.py` interprets signed membrane movement as preset positions +1/+2/+3 and -1/-2/-3.
- Both positive and negative paths carry disjoint `extranonce2` Bitcoin search streams; the existing SQLite WorkMap allocates nonoverlapping nonce intervals; the original native SHA-256d scanner computes actual hashes. Valid shares go through the inherited Stratum V1 protocol.
- The original Regulatory model remains unchanged and the previous round-robin and earlier waveform allocation implementations remain recoverable.

## Verification

- Existing and new Linux test suite: **63 tests complete; 6 skipped**, zero failures, in **50.350 seconds** on the available container.
- The focused 4 new signed-axis tests pass; 4 advanced Regulatory suite tests also pass including local verifying Stratum share acceptance.
- New 2-worker local pool comparison, four three-second productive mining sessions, actual CPU native SHA-256d: conventional round-robin **5,600,000 and 9,100,000 hashes** versus signed-axis **8,555,932 and 5,737,988 hashes**. Each variant obtained qualifying shares accepted by the local verifying pool. The paired sums are 14,700,000 vs 14,293,920 hashes respectively; *no reproducible gain is established*.
- **Windows x64 CI** restored and checksum-verified the exact source ZIP, executed new and inherited advanced-Ripple tests, compiled the native DLL, froze both desktop/worker binaries, installed the application and executed the native hashing worker. All workflow steps passed.
- On that GitHub Windows runner, native SHA256d measured **1,782,097 H/s** before installation and **1,872,096 H/s** after installation (150,000 real hashes). This `bench` measurement does **not** run signed-axis control; it demonstrates the native hash backend still works after packaging.
- The previous installed Windows native measurement was **1,405,733 H/s**; the new 1,872,096 H/s was on a different run with variable host CPU scheduling, and should **not** be interpreted as a recovered 466,363 H/s from the new neural controller.

## Why the old 600k "loss" was not a proven computation regression

The reports compared Linux standalone SHA-256d ~2.04 MH/s, Windows preinstallation ~1.87 MH/s and Windows postinstallation ~1.41 MH/s on different conditions and short durations. The standalone native `bench` path does not execute the 16-cell network, and its different numbers don't establish that advanced Ripple waveforms consumed 600,000 Bitcoin hashes per second.

## Source and release hash

Full ZIP SHA256: `5639c15c6870b7721467e2c2be65962e58f214f8a9b6ded1993b5155a5e7013c`, **141 ZIP entries including 140 manifest-verified source files**. The GitHub source ZIP is Base64-encoded because the connected repository publishing interface writes UTF-8 text.

## Remaining factual boundary

No personal Dell CPU measurements, authorized public-pool share credits, or BTC payouts have been observed. Signed-wave worker allocation is genuinely active in CPU mining, but there is no measured SHA-256 acceleration attributable to those signed transitions. The miner's nonce-batch size is limited to 500,000 by the existing work protocol; the overall count of assignments is not capped at that value.
