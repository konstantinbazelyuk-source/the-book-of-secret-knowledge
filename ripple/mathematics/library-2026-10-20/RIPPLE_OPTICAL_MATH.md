# Ripple Neuron — Samsung optical-mathematical reconstruction v0.4

## Determination based on the original source

The original Raspberry Pi Pico was an implementation target, **not a variable or mathematical assumption in the neuron's dynamical equations**. The original v0.1 source implements a leaky integrate-and-fire-like *software* dynamical system:

```
a = [2.0, +1.2, -1.4]
D = a dot x, x = [red, green, blue] normalized to [0,1]
tau_v * du/dt = -u + D; tau_v = 0.5 s
When threshold is crossed: produce event, reset u=0, 0.1 s refractory
Feedback target: 1 event per second (default)
Rate estimator time constant: 5 seconds
Threshold learning gain: 0.08
```

The weights `[2,1.2,-1.4]` are original model design parameters. There is no evidence they were discovered experimentally from a Raspberry Pi or derived from optical photon physics.

## Optical transformation (reconstructed from captured light)

A smartphone camera photosensor converts incident light into photocharges and the camera processing pipeline converts these signals into RGB image pixels. Model pixel averages in one stable setup as:

```
p(t) ≈ d + M x(t) + epsilon(t)
```

`p(t)` = measured RGB camera pixels in the center region, `d` = dark-reference RGB, `M` = 3×3 empirical response matrix from three source references, `x(t)` = estimated amplitudes of those **same references**, and epsilon = error (sensor noise, calibration mismatch, exposure/white-balance effects, nonlinearity). `x` does NOT represent absolute light intensity or wavelength-separated spectrum.

From the original model:

```
x = M^-1 (p-d)                           (reject poor/unstable calibrations)
D = a^T M^-1 (p-d)                       (within linear valid range)
w^T = a^T M^-1; b = -w^T d
D_Samsung = w_R * R_pixel + w_G * G_pixel + w_B * B_pixel + b
```

The app also applies physical input boundaries `x ∈ [0,1]`; once values clip, the affine `D_Samsung` representation alone is no longer sufficient, so the app continues using the decoded/clamped inputs for the original neuron calculation. The neuron **code remains unchanged**.

There are no phone-specific numeric values for `w` or `b` prior to real calibration on the user's device. Even knowing that the phone has a 50 MP main camera cannot determine this response matrix. It must be empirically established and revisited whenever optical conditions or camera processing change.

## How to obtain your real coefficients

1. Deploy this program as an HTTPS web app and open it in Android Chrome. Choose **Phone camera**, grant permission.
2. Keep the camera, light source and distances fixed. Use repeatable R/G/B reference illumination at fixed brightness; avoid clipping, automatic illumination changes and the camera's flash. Keep ambient lighting as stable as possible.
3. Record **Dark**, **Red**, **Green**, **Blue** references using the four buttons. The calibrated 3×3 inverse is rejected if singular, extremely dim or numerically ill-conditioned. Samples with high drift/saturation are rejected.
4. Read **Phone-specific optical equation**. Tap **Export calibration** to save an auditable JSON report of the measured reference data, selected stream resolution/frame rate when reported, and calculated coefficients.
5. Enable **Use calibrated decoder** to apply measured inputs to original Ripple neuron. Run trials, export event-rate data, and check calibration stability and repeatability under a controlled light sequence.

## Samsung-specific hardware boundary

Current user-agent model: `SM-A176U`, consistent with Samsung Galaxy A17 5G. Samsung describes a 50 MP wide/main camera, 5 MP ultrawide, and 2 MP macro. The app requests an environmental rear-facing camera video stream at 640×480/15 FPS nominal for predictable, low-power sampling, and reports **actual** browser-selected stream settings where available. The number of megapixels alone does not reveal photoelectrical channel sensitivities, raw response curves, or achievable Camera2 control capabilities. These require measurement or device API inspection.

Android camera2 has optional or device-dependent advanced controls for autoexposure, white-balance locking, and RAW sensor access; a browser PWA does not promise control of these. The current app operates on **processed 8-bit RGB images**, not raw sensor spectral measurements. A native camera2/CameraX implementation would be a more controlled path for quantitative experiments.

## Validation as built

- Locked original model body preserved byte-for-byte. Source provenance in `SOURCE_PROVENANCE.json`.
- Numerical original 120-second experiment reproduces 60–80 s rates: **0.95 Hz adaptive** and **3.40 Hz fixed**.
- 600 synthetic RGB cross-talk test cases verify `a dot x == w dot p + b` within `1e-10` in valid nonclipped range.
- Singular color-reference calibration is rejected.
- Chromium GUI testing covers displaying a derived optical equation and downloading its JSON report (using synthetic, not user, references).
- Browser synthetic-video test verifies processing a camera-like RGB stream into the original mathematical neuron.

**Outstanding physical verification:** No A17 camera frames have been supplied or remotely read in this session. There are no measured Samsung-specific coefficients, measured photon flux, real sensor spectral response, hardware frame-time measurements, or independently verified threshold stability under real-world phone illumination yet. Those should be measured on-device, after which the data can be analyzed and the model revised if necessary.

## Provenance

Original Ripple Neuron v0.1 as contained in `original-simulator.html`; v0.4 app is an additive extension of v0.3 preserving the original model, visual structure and behavior. CC0-1.0 original code license. All calculations local to the app.
