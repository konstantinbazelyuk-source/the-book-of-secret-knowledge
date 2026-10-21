# Executed performance and ablation evidence

The reproducible benchmark script is `experiments/run_isolated.py`. Each of three rounds measures **600,000 actual SHA-256d attempts**, on the same Linux environment with three admitted CPU worker slots. It includes process start, Node original neuron verification, hierarchical orchestration, processing and teardown. Trials are isolated into separate OS processes; one early experimental run stalled, was discarded, and the isolation method was corrected. No GPU/ASIC/power meter was used.

| Configuration | Median H/s | Change vs conventional |
| --- | ---: | ---: |
| Conventional process pool | 534,198 | baseline |
| Replicating Mycelium, no mutation, neuron gate active | 364,686 | -31.7% |
| Replicating Mycelium, mutation and neuron gate active | 350,731 | -34.3% |
| Replicating Mycelium, mutation but neuron gate disabled | 372,295 | -30.3% |

Recorded individual trial results: `experiments/replication_isolated_results.json`. **Negative results are retained.** There is no evidence the colony's growth currently beats a simpler scheduler for local Bitcoin hashing, and any financial optimization should favor the measured higher net value. Wider workloads, longer sustained trials and calibrated energy readings remain necessary.

The separate native SHA256d kernel benchmark in `experiments/native_hash_results.json` contains three same-process trials of 1,000,000 hashes each:

- Python SHA-256d scanner: median **1,007,709 H/s**.
- Native OpenSSL scanner: median **1,646,916 H/s**, an observed **1.63×** acceleration.

This is a measured CPU implementation effect, **not** a colony or ASIC breakthrough; it does not establish economic viability at contemporary Bitcoin difficulty. Native build currently works on Linux; a compatible Windows native binary was not built. No pricing/electricity/payout data were fabricated.

A standard browser UI can display verified hashrates and pool submissions, but neither a calculated payout field nor an accepted share from the synthetic easy local pool represents an actual BTC credit.