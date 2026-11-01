# Package index · Ripple Cybernetic Mycelium v0.2

**Open first:** `Ripple-Cybernetic-Mycelium-v0.2.html` to explore the colony visually, or `README.md` for exact commands and verification status.

- `docs/DESIGN_FUSION.md` — ten conceptual redrafts, 72 model configurations, selected fusion mathematics, decisions and limits.
- `src/ripple_core_reference.js` — byte-identical original v0.1 mathematical neuron kernel.
- `src/colony_variants.js`, `src/sweep.js` — independent deterministic colony simulation and sweep.
- `src/parallel_worker.js`, `src/parallel_colony.js`, `src/cpu_task.js` — actual Node.js worker threads, bounded growth, job ownership and verified work.
- `src/bench_threads.js` — measured parallel execution benchmark (5 trials/configuration).
- `src/bench_crossover.js` — measured thread crossover test across three task sizes, including optional cost-aware heuristic (3 trials/configuration).
- `tests/test_v2.js` — 17 unit/integration checks, including worker crashes.
- `baseline_v0.1/` — original v0.1 numerical colony sources, simulator, test script and original Ripple HTML, all preserved independently.
- `data/variant_sweep.csv` and `.json` — 288 simulated architecture/scenario trial results.
- `data/fused_burst_trace.json` — the actual browser default's controller-equivalent numerical trace (see qualification below).
- `data/thread_benchmark.json`, `data/thread_benchmark_summary.json` — real measurement samples, resource reports and summary.
- `data/CPU_intensity_crossover.json` — 36 real measured runs, with three repetitions at three task sizes over four thread configurations.
- `data/v2_tests.txt` — complete test status log; `data/crossover_console.txt`, `data/benchmark_console.txt` — runtime consoles.
- `charts/` — model/benchmark graphs and verified browser screenshots including 390px mobile check.
- `build_explorer.py`, `make_charts.py` — fully local generator scripts; no network.
- `SHA256SUMS.txt` — per-file integrity manifest for every file except the manifest itself.

The browser default and `data/fused_burst_trace.json` both use **fused/steal/tree**. All 288 variants are stored independently in the sweep files.
