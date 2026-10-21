# Execution Results & False-Positive Controls

**Date:** 2026-10-20. All numbers below are from executed software on synthetic normalized-sRGB fixtures. Model seconds are not wall-clock sensor timestamps. A change in membrane state is a computational intervention effect, not a claim of general intelligence.

## Test totals

- New integration suite: **21 passed**.
- Inherited XYZ suite: **19 passed**.
- Inherited wave-memory suite: **17 passed**.
- Inherited fluctuation-cipher suite: **31 passed**.
- **88 total passing tests** across the source chain in this session.
- Exact immediate-parent file comparison: **94/94 original ZIP members identical**; original ZIP SHA256 is recorded in `results/source_copy_integrity.json`.
- Controlled synthetic study: **16 runs**, four source fixtures × four ablation modes, 80 steps each, with 128-step source training each run.
- Extra cross-pattern transfer: **3 runs**, trained solely on sinusoid and tested on other fixtures.
- Chromium interface: desktop/mobile controls connected to real Python server using test-only transport bridge; no browser page errors. Not a physical device installation.

## Main comparison

The row reports the enabled-memory variant versus the same-fixture alpha-zero/no-feedback comparison. The forecasts are on synthetic repeated signals; a match is not necessarily a correct prediction. MAE is per RGB component on matched ticks only. Charlie values are dimensionless simulated conductance states.

| Synthetic signal | Matched / 80 | Memory forecast RGB MAE | Previous-input persistence MAE | Δ final original Ripple membrane | Δ final Charlie inhibition |
|---|---:|---:|---:|---:|---:|
| sinusoid | 54 | 0.004259 | 0.025883 | +0.229384 | +0.000682 |
| pulse | 12 | 0.000000 | 0.000000 | +0.000000 | +0.000000 |
| chromatic_collision | 17 | 0.009020 | 0.018039 | -0.014594 | -0.000918 |
| gray | 0 | N/A | N/A | +0.000000 | +0.000000 |

The positive memory interventions are genuine because the external and effective RGB triplets differ on accepted divergent inputs, and the **original inherited Ripple/Charlie state** changes. However, none of this establishes an out-of-distribution performance benefit. Constant gray can still receive feedback around a deliberately perturbed test tick when trained on gray; the unchanged final membrane after 80 steps is an observed null endpoint, not proof that no intermediate effect happened.

## Independently trained waveform transfer (negative control)

Training used only 128 sinusoidal synthetic samples and the test signal was a different 80-sample fixture. The final dual-space/motion-gated version reported:

| Unseen signal family | Accepted feedback matches / 80 | Input alterations |
|---|---:|---:|
| pulse | 0 | 0 |
| chromatic_collision | 0 | 0 |
| gray | 0 | 0 |

**Important engineering revision:** The first signal-XYZ-only version sometimes accepted unrelated stationary signals (6 pulse and 10 gray ticks in this transfer). After this unwanted effect was observed, a separate invertible color-state comparison and a minimum temporal-motion requirement were implemented. These new gates rejected those cross-pattern cases under the stated thresholds. **This is a post-hoc correction; it is not an independently confirmed generalization result.** Other unrelated signals may still collide and will need further adversarial testing.

## Outputs for replication

- `results/new_tests.log`, `results/inherited_xyz_tests.log`, `results/inherited_wave_tests.log`, `results/inherited_cipher_tests.log`.
- `results/predeclared.json` and `results/controlled_study.json` (first formal deterministic protocol; later false-positive corrections documented above).
- `results/cross_pattern_transfer.json` (additional OOD transfer), `results/browser_smoke.json` and both UI screenshots.
- `results/source_copy_integrity.json` and original locked-neuron source SHA checks.

## Engineering status

**Implemented:** The full source chain is executed without rewriting it, a typed two-space memory query uses original recorded XYZ episodes, predictions are computed from past-only information, and they causally alter the original neuron input through a bounded gate. Training archive encryption is executable.

**Not yet implemented:** Real camera/ECG I/O, integration of all 28 historical families into one live process, stateful worker crash recovery, learned policy discovery beyond nearest analog retrieval, Android APK, Dell installer, and hardware validation.