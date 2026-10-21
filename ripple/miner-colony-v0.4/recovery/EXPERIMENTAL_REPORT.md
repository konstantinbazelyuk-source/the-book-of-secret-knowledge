# Reproducible experiments — Ripple Miner historical-colony v0.4

## Environment and reproducibility

All local checks ran in the executing Linux development container, Python 3.13.5, Node 22.16.0, with 5 logical CPUs reported to Python. **No Dell, Samsung, ASIC, external pool or mining cloud capacity was measured.**

Commands:

```
python -m unittest discover -s tests -q
python experiments/compare_historical.py
```

Original suites were run from reconstructed archive roots with their original commands, **after restoring dependencies/data**. The isolated extracted models passed: Mycelium 12/12, 17/17, 24/24; Charlie Forest 78/78; MUSHROOM 64/64; Ring v4 38/38.

The new suite contains **33 passing tests** including controller-started actual hashing submitted to a local difficulty-eased verifying Stratum V1 pool under `policy=historical`; accepted test shares exist but have **zero real monetary value**.

## Three-policy measured comparison

Equivalent inputs for every measured run: **two actual OS CPU processes**, 20 batches of 50,000 contiguous nonces (1,000,000 SHA256d attempts), unchanged `scan_nonces()`, identical 76-byte header prefix, local SQLite `WorkMap`, same executing host. Three rounds with rotated execution order. Startup/process creation is included in each timed run. Real pool networking is excluded.

Median observed throughput:

- Conventional round robin: **1,652,510.32 H/s**.
- Existing adaptive EWMA policy: **1,620,654.71 H/s**.
- Historical Mycelium/Forest admission: **1,656,413.82 H/s**.

Difference versus round robin: **+0.2362%** on this short test; insufficient repeated evidence for a stable improvement. The policy is retained as a separately selectable experiment, **not promoted as a financial or speed optimization**. Full nine trials and actual wall times are in `experiments/historical_results.json`. Check actual JSON if rerunning; values will change with hardware and load.

## Controlled ablation coverage

Existing v0.3 tests: ordinary/adaptive worker dispatch, transactional ownership, remote verification, duplicate detection, interruption/reclaim and local Stratum. New tests isolate physical budget cap, adjacency growth, idle retirement, nonce claims, remote slot enrollment and E2E pool submission.

Not yet run: full factorial ring-vs-forest routing, MUSHROOM neuron ablation attached to mining, genome selection under hardware telemetry, sustained thermal/power measurement, real cloud-latency experiment, real pool stale rates, or energy-per-accepted-share.

Historical source ablations document ecological model results (recurrent vs static/spikes_off/links_off) and specialist assumptions. They are **not equivalent to mining results**.

## Evidence classification

- **Source-recovered:** archived equations, functions, tests, immutable file hashes.
- **Measured:** actual CPU hashing throughput, local process execution, run wall times, process-generated pool submissions.
- **Simulated:** original forest ecology and optical/MUSHROOM experiments; low-difficulty local pool network.
- **Calculated only:** financial expected values using user-supplied estimates, no Bitcoin payout.
- **Unverified:** live ASIC, production cloud job, actual Bitcoin pool credit, physical electricity/temperature on user's devices.