# Samsung optical mathematics and engineering assessment (v0.3–v0.5)

Date: **2026-10-15**. Sources: local releases `Ripple-Samsung-Android-v0.3-Complete.zip`, `Ripple-Samsung-Optical-Reconstruction-v0.4.zip`, `Ripple-Samsung-Engineering-v0.5-Complete.zip`. User's Galaxy model observed as `SM-A176U`; this is a source-based Android adaptation, **not** a phone-hardware benchmark.

## The question of hardware specificity

The v0.1 Ripple neuron is an ordinary first-order model with an adaptive event threshold. Its ODE and event rule are **not derived from the Raspberry Pi or Pico electronics**. Changing platforms does not change the mathematical LIF kernel. What changes is how a physical light measurement becomes a normalized model input.

The original proposed `AS7341` multispectral path and Samsung processed RGB camera path provide different observables. A camera's three processed RGB channels do not reconstruct an arbitrary spectrum or the phase of an optical carrier.

### Locked neuron drive and dynamics

```math
a = [2, 1.2, -1.4]^T
D = a^T x
tau_v du/dt = -u + D
```

`x` is a dimensionless normalized vector. The positive R/G and negative B coefficients represent the original selected software excitation and inhibition. They are not calibrated action spectra.

## v0.4 source-calibrated optical bridge

For a **fixed camera pipeline, illumination reference and geometry**, posit the linear response approximation:

```math
p = d + M x + epsilon
x_hat = clip(M^(-1) (p-d), 0,1)
D_Samsung = a^T x_hat
```

- `p`: measured mean processed RGB pixel channels in the sampled region.
- `d`: dark-image reference under the same settings.
- `M`: 3 × 3 empirical response matrix with columns from independently obtained R/G/B reference illuminations.
- `x`: relative amplitudes of **those three reference illuminations**, not unique physical photon spectra.
- `epsilon`: noise, clipping, motion, environmental light, nonlinear transfer and drift.

When `M` is invertible, numerically well-conditioned, the input model is linear and `x_hat` is **not clipped**, derive:

```math
w^T = a^T M^(-1)
b = -w^T d
D_Samsung = w^T p + b
```

With clipping or nonlinearity, the affine form is no longer equivalent; use decoded constrained input in the original model and report residuals. Avoid unstable matrix inversion in production by checking rank/condition and using an appropriate numerical solver where necessary.

The original phone-core coefficients `a` are known. Numerical phone-camera `M, d, w, b` **are not known until measured on the actual device**; camera megapixel count and device model cannot determine them.

### Calibration and independent validation

1. Record repeated dark, R, G and B reference observations under stabilized exposure, white balance, distance and lighting. Record timestamps, channel means, frame size and actual acquisition settings if exposed by Android/Chrome.
2. Fit `M` and `d`. Reject near-singular, drifting or saturated calibrations, and save repeatability/uncertainty.
3. Independently test unseen 25/50/75% intensities, combinations of colored sources and new background conditions. Measure pixel residual error, recovered relative-source amplitude error, and `D` prediction error.
4. Compare calibrated and uncalibrated bridges using held-out data, not the four calibration references.
5. For physical irradiance, spectrum or light waveform claims, compare against a calibrated reference instrument with traceable units. Camera PNG/JPEG or browser-video RGB does not by itself provide absolute spectral radiant power.

v0.4 mathematical synthetic checks: **600** RGB cross-talk cases confirmed equivalence of `a^T x` and `w^T p+b` within `1e-10` in the declared unclipped linear regime. Those were generated test matrices, not Samsung measurements.

## v0.5 optical signal encoding study

Instead of changing the locked numerical neuron, optional adapters produce alternative drives. Explicit alternatives:

```text
Original:        D = 2 R + 1.2 G - 1.4 B
Positive-color:  D = 1.2 R + 0.9 G + 0.7 B
Luminance proxy: D = 3 (0.2126 R + 0.7152 G + 0.0722 B)
```

These compare different *functional objectives*: original blue inhibition, broad positive-channel stimulus and weighted intensity proxy. Normalized processed camera RGB is not physically calibrated photometry; luminance coefficients are a display-space approximation and must be interpreted with color-space transformation in mind.

### Executed numerical study results

| Synthetic trial class | Original | Candidate | Interpretation |
|---|---:|---:|---|
| Nine scenarios × 120 model seconds, mean time-average absolute rate-estimate error | 0.2743 events/s | 0.159478 positive; 0.1773 luminance | Candidate more closely held the **chosen** 1/s target under selected scenes; not evidence of better hue detection. |
| 15 gain × estimator-time-constant controller combinations, four scenarios each | baseline gain .08, tauR 5: 0.1372 events/s | lowest time-average error gain .32, tauR 10: 0.0857 | Different transient vs final-window error; original default retained. |
| 250 deterministic noise seeds per encoder, 500 total runs | 0.0083 events/s final-window mean error; max 0.0667 | positive-color 0.0003; max 0.0333 | Artificial noise trials, scenario-specific. |
| Synthetic nonlinear 9-level camera holdout | exact fitted 4 refs | intermediate-intensity RMSE 0.2000, vs linear control 0.0000 | Four calibration colors insufficient to establish response linearity. |
| 600 v0.4 linear optical cross-talk cases | mathematical identity | equivalence within `1e-10` | Algebra verified, no real Samsung response measured. |

Original regression calculation at 60–80 s of the 120 s simulation: adaptive **0.95 model events/s** vs fixed-threshold **3.40 model events/s**. The value concerns simulated event counts, not external electrical/spectral phenomena.

### Reproducibility and cost

The v0.5 package contains `engineering-lab.html`, `engineering-engine.js`, test scripts, source provenance and `results/engineering-evidence.json`. The development host recorded a median **203.067 ms** for a batch of 27 × 120-second numerical scenarios over 12 runs on Linux/x64, Node 22.16, with five logical CPUs reported. It is **not** an Android timing, thermal or power benchmark.

Unmeasured phone metrics: actual color response matrix, exposure and white-balance stability, frame jitter, end-to-end sampling latency, camera/CPU energy, thermal throttling, sustained operation and physical spectral validity.

## Core mathematical upgrade options — candidates, not replacements

- **Hardware adapter:** native Camera2/CameraX (where supported) to test exposure/white-balance and RAW capture instead of only browser-processed RGB; empirically calibrate each path.
- **Robust system identification:** fit response curves with multiple intensity/color holdouts and uncertainty; account for temporal drift and nonlinear tone mapping.
- **Feedback:** compare original fixed gain with analytically feasible feed-forward threshold, bounded anti-windup, and alternative estimators on independent lighting disturbances.
- **Information objective:** measure hue/contrast separability, mutual-information surrogate, false-event rate, detection delay and resource use alongside target event-rate loss; a candidate winner can change when the objective changes.
- **Adaptive optical channels:** run separate spectrally meaningful sensors or multispectral hardware where genuine wavelength specificity is required.

None of these proposed upgrades modifies the original Ripple source by inclusion in this document. Promotion requires an executed test, source diff, reproducible settings and an appropriate comparator.
