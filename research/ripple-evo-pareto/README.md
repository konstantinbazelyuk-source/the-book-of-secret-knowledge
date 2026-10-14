# Ripple EvoPareto v1.3 — Ground-only evolutionary controller research

**Actual code and repeatable experiments, not a physically validated robot or a general intelligence.**

This revision researches alternate leg-control policies for the previously approved SpiderScan 8-leg, 24-axis **digital** motor simulation. It preserves all prior approved equations and sources exactly, including the original RGB leaky integrate-and-fire neuron. It never writes motor or flight commands.

## Advances over Alpha v1.2

1. Replace single weighted-loss optimization with independent competing objectives: simulated toe RMSE ↓, commanded-motion proxy ↑, rate-limit hits ↓, and support-proxy loss ↓. This is an NSGA-II-*inspired* nondominated sorting and crowding-diversity search. It does not import external genetic-algorithm code.
2. Preserve both precision and throughput candidates rather than assuming a single best solution. Candidates are selected from the **training** Pareto front only. Held-out conditions are evaluated once independently.
3. Add a hard **simulation** feasibility gate (no IK failures; commanded proxy at least 75% of v1.2 baseline; at most five support-proxy lost frames per scenario). This is **not physical safety clearance**.
4. Report and reject holdout failure instead of calling a faster but unstable simulation "superior." Every policy has `hardware_deployment_authorized=false`.
5. Add controlled feedback-gain ablation and provenance hashes. A nonzero neuron feedback gain can improve simulated precision at the expense of commanded motion; there is no evidence of cognition or real learning by neurons.

## Exact preserved source SHA-256

- `legacy/ripple_optical_agent_LOCKED.py`: `7f2f611cd8f1717c3d3dcae745dbd41efc37e24315d93878231db52eaf614f77`
- `legacy/approved_kinematics_v06.py`: `aef18eba0520dde2e80a80d9c1e5f774bf4c355d60d879404108d21a881a4561`
- `legacy/digital_motor_v11_LOCKED.py`: `cce5ce28199475d8f9b063c8eb5861c5e8de02da67a1bb37df12b6d54dbad8a4`
- `ripple_evo/evolution.py` (prior v1.2): `64a2c1aa2c198efd37566d81c139eafd0cb79a8823ead77e75691394a2234ed1`

## Run (Python 3.11+, standard library for the simulation)

```bash
python -m unittest discover -s tests -v
python -m ripple_evo.pareto --seed 20261013 --population 18 --generations 6 --out results/pareto_seed_20261013.json
python cloud/verify_cloud.py
```

Plots in `results/` are generated from executed software experiments. Matplotlib is required only to regenerate plots; it is **not** needed to run the simulation.

## Representative complete run

- 126 distinct candidates evaluated over 6 generations.
- Training: 6 synthetic motor regimes; holdout: 16 independently seeded synthetic regimes.
- Precision: 4.330444 mm mean simulated toe error, 25.452409 mm/s commanded-speed proxy; passes simulated holdout gate.
- Original baseline: 6.664937 mm simulated error, 33.928542 mm/s commanded-speed proxy.
- Aggressive throughput: 53.983333 mm/s commanded-speed proxy, but 327 support-proxy-loss frames across 16 scenarios and **fails** held-out gate. **Not promoted.**
- Within the precision genome, gain=0 produces 4.545669 mm toe error / 27.381667 mm/s proxy; gain=0.15246 produces 4.330444 mm / 25.452409 mm/s. This is evidence of a specific simulated feedback effect, not motor intelligence.

These numbers are not obtained from physical sensors, and their apparent decimal precision arises from calculations, not instrument resolution. See `docs/RESEARCH_PRIOR_ART_AND_LIMITS.md` for scientific, patent and FBI research sources and limitations.

## Cloud

`cloud/verify_cloud.py` performs a fresh full comparison and immutable-source tests. A GitHub Actions workflow is supplied in the research branch. A workflow file does not itself prove cloud operation; **only a completed runner log and its artifact do**.

## Next engineering conditions before real robot

Measure actual joint geometry and servo torque/rate; use an instrumented model with foot contact/friction and independent position sensing; calibrate scanner imagery; demonstrate emergency stop; only then consider a physical trial, separately approved. No patent license or hardware certification is implied.