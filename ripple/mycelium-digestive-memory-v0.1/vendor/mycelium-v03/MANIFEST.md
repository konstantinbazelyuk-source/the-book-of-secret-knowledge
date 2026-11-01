# Artifact manifest — v0.3, local only

## Entry points

- `Ripple-Mycelium-Mathematics-Lab-v0.3.html`: tested self-contained offline browser explorer. Browser calculations use the unchanged core followed by optional feedback wrappers. Colony comparisons inspect recorded executed simulation trials.
- `README.md`: scope, reproducing, interpretation, limitations.
- `docs/MATHEMATICS.md`: full equations, objective and feasibility conditions.
- `docs/VARIANT_LEDGER.md`: positive, negative, and conditional findings including ineffective types.
- `docs/SOURCES.md`: original user-source and research literature traceability.

## Executable source

- `src/ripple_core_reference.js`: EXACT unchanged model.
- `baseline_v0.2/ripple_core_reference.js`: archived byte-equality verifier input.
- `baseline_v0.2/colony_variants.js`: earlier v0.2 deterministic colony preserved for comparison, not invoked as the specialized v0.3 engine.
- `src/feedback_sweep.js`: eight proposed variants plus original; 324 trajectories.
- `src/specialist_math.js`: independently checkable arithmetic for three domains.
- `src/specialist_colony.js`: virtual colony with task integrity, cloned cores, route algorithms and alternate growth policies.
- `src/colony_sweep.js`, `src/expanded_sweep.js`, `src/sensitivity.js`, `src/learning_baseline.js`: experiment runners.
- `tests/verification.test.js`: 24 passing checks.
- `tests/check_browser.py`: optional desktop and mobile browser checks using Playwright.
- `build_explorer.py`, `make_charts.py`: regenerate presentation.

## Evidence

- `data/feedback_trials.json`: 324 scored neurodynamic trajectories.
- `data/specialist_trials.json`: 144 preliminary policy/profile trials.
- `data/expanded_colony_trials.json`: 720 policy/topology/neuron/profile trials.
- `data/service_sensitivity.json`: 432 service-time-assumption/link-cost stress trials.
- `data/learning_verification.json`: actual heldout scores and nine wall-clock runs comparing emulation with direct computation (not work-equivalent).
- `data/verification.tap`: v0.3 executable test result, 24/24 passing.
- `data/v1_regression.log`, `data/v2_regression.log`: archived v0.1 / v0.2 tests, 12/12 and 17/17.
- `data/browser_verification.log`: no JS page errors, no horizontal mobile overflow.
- `charts/`: actual data plot outputs and browser-rendered screenshots.

## Limits

No physically calibrated results, source provenance claims about actual research facts, durable worker processes, automatic model changes to ChatGPT, commits, deployments, external agent permissions, or network API integrations. The original v0.2 itself remains at its prior location and has not been edited.

## SHA256SUMS

`SHA256SUMS.txt` lists hashes of every package file except itself. The ZIP is checked for CRC and verified by extracting and rerunning tests.
