# Ripple Genetic-Weights & Grammar Forest — Alpha v1.7

A **runnable, reproducible research Alpha** extending the original Ripple family with bounded digital genetic mutations, nonstandard *classical* evidence-weight transformations, a diversity archive, and compositional program-library expansion. Not quantum computing, an autonomous mind, or a physically verified optical sensor.

## Reproducible release contents

- `sources/`: untouched v0.1 neuron, v0.7 two-bit signal codec, v1.4 optical physics, and v1.6 decoder, grammar, engine and fixture generator copies. The v1.2 sensory-gene specification is included as a reference.
- `src/study.py`: reproducible 256-mutation genotype search, independent development set, fresh-seed results, seven weighting phenotypes and negative-control ablations.
- `src/composition.mjs`: directly executable finite semantic composition library; runs original LIF neuron events as a gating signal and compares to pure serial arithmetic.
- `src/generate_fresh.py`, `src/create_novel.py`: regenerate *synthetic* reserved cases without modifying earlier programs (requires NumPy).
- `src/run_locked_controls.mjs`: executes exact copied v1.6 solver on new seeds as conventional + Ripple-gated comparison.
- `data/`: trial fixtures, scores, genome genealogy, composition records, source baselines, and browser checks.
- `Ripple-Genetic-Weights-Alpha-v1.7.html`: offline saved-results explorer, not an arbitrary code executor.
- `docs/`: equations, requirements, failure ledger, cloud instructions.

## Local tests and regeneration

Requires Node.js 20+ and Python 3.11+ with NumPy. No network access or third-party AI API is needed to run. From extracted ZIP root:

```bash
node --test tests/test_composition.mjs
python -m unittest discover -s tests -p 'test_*.py' -v
node src/run_locked_controls.mjs
python src/study.py
node src/composition.mjs
python src/build_lab.py
python src/plots.py
# Optional: python tests/browser_check.py (Playwright + Chromium installed)
```

To independently regenerate the reserved optical fixture set (rather than use included copies):

```bash
python src/generate_fresh.py
python src/create_novel.py
```

Do **not** regenerate new seeds after reviewing held-out results and then represent that as an untouched holdout. The archived results freeze seed selection and report what was tried.

## Key outcomes, with limits

- **540 synthetic optical-code cases** for genetic policy examination: training seeds 111/222, development seeds 333/444, brand-new reserved seeds 777/888 (180 each).
- **256 bounded genetic mutation evaluations**, with seven representational modes and a map of distinct quality niches.
- **1,910 new semantic mappings** from 80 permitted simple functions, increasing vocabulary from 328 to 2,238. None is an invented primitive; all are closed compositions of approved software functions.
- **108 intentionally composition-oriented new tasks**, compared with an unchanged-grammar control and with a serial execution control.
- No claimed speedup, quantum effect, unsupervised reasoning, consciousness, independent knowledge discovery, or real camera data.

## Public research referenced (methodological, not proof of Ripple)

- DreamCoder (Ellis et al., PLDI 2021): https://doi.org/10.1145/3453483.3454080
- HyperNetworks (Ha et al.): https://arxiv.org/abs/1609.09106
- Deep Complex Networks (Trabelsi et al.): https://arxiv.org/abs/1705.09792
- MAP-Elites (Mouret & Clune): https://arxiv.org/abs/1504.04909

This code doesn't import research-project code; formulas and ideas were independently implemented. Archived content retains original license and third-party notices.

## Boundaries

No GitHub project, user app, game engine or third-party cloud service was modified. The included workflow is `workflow_dispatch` only. To run outside the local machine, the repository owner must review and install it and remain responsible for quota/billing. No API key is required.
