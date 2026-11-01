# Ripple Cybernetic Mycelium v0.3 — Mathematical Improvement Laboratory

**Status:** reproducible software-only numerical experiments with mathematically defined work, plus a separately measured Node process-time microbenchmark. Original Ripple kernel and v0.2 remain untouched. No physical sensor, real-time robotic control, LLM integration, fungal cognition or new AI model is claimed.

## Start immediately

Open `Ripple-Mycelium-Mathematics-Lab-v0.3.html` in a modern browser. It is standalone; it makes no API requests. You can run simulated neuron activity and explore **720 executed colony trials** by changing controls. The on-page data is not an LLM prediction.

To reproduce locally (Node.js 20+, no npm dependency):

```bash
node --test tests/verification.test.js
node src/feedback_sweep.js
node src/colony_sweep.js
node src/expanded_sweep.js
node src/sensitivity.js
node src/learning_baseline.js
```

Optionally regenerate the Explorer and charts:

```bash
python build_explorer.py
python make_charts.py  # matplotlib + numpy required
python tests/check_browser.py  # playwright + chromium required, optional
```

## What changed from v0.2

- Preserved exact original math as immutable reference, with automated byte comparison.
- Added analytically inverted threshold targeting and tested nine controller policies. Best tested hybrid achieved **0.039405** simulated average 10-second-window target-rate error vs. original **0.2**. This is a synthetic advantage, not a measured electrical signal or proof of stability for every input.
- Replaced fixed capacity assumption in a new optional colony with a blend of analytic LIF event-rate prediction and observed rate. The fixed v0.2 controller remains selectable as a comparison, not overwritten.
- Added actual **learning** (partitioned logistic gradients + central SGD), **product** (exact integer-cents aggregation), and **study** (duplicate-aware inverse-variance synthesis of *synthetic* measurements). All parts have independent serial checks.
- Ran 324 controller trajectories, 144 initial specialist trials, 720 topology/control variants, and 432 specialist-cost/link-delay sensitivity trials. Some profiles overlap, so counts are executed trials rather than independent empirical observations.
- Preserved losses: PID/PI feedback and blind-specialist routing can be worse than simpler alternatives. Under equal specialist costs, conventional generalists won some workloads.

## Results at a glance

| Experiment | Result | Evidence level |
|---|---|---|
| Constant-input firing inverse | Exact algebra, independently checked against long-run numerical firing | Mathematical / simulated |
| Original mean firing error | 0.200 events/model-s | Simulated |
| Optional fast hybrid mean firing error | 0.039405 events/model-s | Simulated |
| 111-job balanced, capacity-specialist/affinity/tree | 111/111 complete, 3.05s p95, 1010 simulated worker-seconds | Simulated, **assumed expert advantage** |
| Same balanced, capacity-general/affinity/tree | 111/111 complete, 4.50s p95, 1135 simulated worker-seconds | Simulated, same assumptions |
| Same balanced under expert parity | Fixed four generalists p95 .90s; capacity-specialists 1.45s | **Negative simulated result** |
| Synthetic learning-heavy, matched update count | 95% holdout accuracy, conventional serial SGD also 95% | Real executed statistical math on synthetic data |
| One-process computation overhead illustration | Last-run median 4.26ms virtual-colony emulation vs. 0.073ms direct SGD; *different bookkeeping, not a parallel speed comparison* | Host wall-clock measured (9 trials) |
| New regression tests | 24/24 passed | Executed Node tests |
| Archived v0.2 regression | 17/17 passed | Executed Node tests |
| Browser preview | Desktop + 390px mobile functional, no errors or horizontal overflow | Executed Chromium tests (content injection) |

The simulation's artificial specialist pulse-cost ratios (match=1, generalist=2, mismatch=3) are **not measured human expertise, CPU processing time or product learning ability**. They are hypotheses to be calibrated with real data. When every role costs one event, the specialist advantage is absent. The top ranking is specific to the enumerated experimental search space, not universally optimal.

## Research documents

- `docs/MATHEMATICS.md`: equations, derivation, controller validity conditions, population math and domain kernels.
- `docs/VARIANT_LEDGER.md`: preserved, selected, conditional and explicitly ineffective designs.
- `docs/SOURCES.md`: research literature and original user-source provenance.
- `data/`: raw machine-readable trials and actual validation logs; do not substitute reported rankings for these files.
- `charts/`: regenerated plots plus visual browser verification artifacts.

## Integrity and safety

All computation is deterministic, local, non-networked, and side-effect-free. No original neuron source was rewritten, no v0.2 code was changed, and no GitHub upload or production service modification occurred. The agent cannot change the assistant's own model weights, obtain biological electrical signals, or validate real scientific claims from the synthetic study observations. Nothing in this simulation grants real device/tool execution permissions.

## License

The generated experimental source and reports are offered under CC0-1.0 (see `LICENSE.txt`). External scientific works linked as sources have their own copyright. Open publication does not establish novelty or patent clearance.
