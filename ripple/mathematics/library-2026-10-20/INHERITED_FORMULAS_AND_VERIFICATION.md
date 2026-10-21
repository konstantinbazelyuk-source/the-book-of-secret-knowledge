# Ripple Interference–Neuron Alpha v1.4: mathematical contract

**Evidence classes:** ESTABLISHED SCIENCE (textbook laws), MATHEMATICALLY VERIFIED (numerical identity), SIMULATED (synthetic photon/neuron data), PROPOSED (optional neural wiring), NOT MEASURED (no actual light or biological neurons).

## Connection to previous Ripple research
- `reference/ripple_core_reference_LOCKED.js` is the **byte-identical** original v0.1 LIF implementation archived in Mycelium v0.3. SHA-256 `d75d4208e92f19623b127615bd52b4002e85d2c0a59b76471764b55a24294210`. No coefficients, integrators, rate estimators, or threshold rules changed.
- The archived 56-formula mathematical study motivated physically typed interfaces: optional optics; statistical photodetection; LIF spike coding. This project does not assert that the 56 relationships constitute 56 novel physics laws.
- Earlier optical reconstruction, hybrid threshold control, inherited color weights, and colony diffusion remain separate and are **not automatically added** to this physical experiment. Photon light waves have actual wavelengths; Ripple's RGB channels remain software-assigned, not wavelength-resolving sensors.

## 1. Reference geometry and exact intensity equation
Reference settings: monochromatic 532 nm, two equal transmitting slits of width `a=0.050 mm`, center distance `d=0.300 mm`, screen at `L=1.8 m`, thin-screen scalar far-field approximation, matched polarization, no measured data.

For screen coordinate `x`, set `sin θ=x/sqrt(x²+L²)`, `β=πa sinθ/λ`, and `δ=2πd sinθ/λ+φ`. Define `sinc β = sinβ/β` with limiting value 1 at β=0.

**Finite slit + partial coherence** (relative scale):

`I(x)=0.5 * sinc(β)^2 * [1+V cos(δ)]`, `0≤V≤1`.

For equal coherent paths `V=1`, this is equivalent to adding complex fields before squaring:

`A1=0.5 sinc(β) exp(+iδ/2)`, `A2=0.5 sinc(β) exp(-iδ/2)`, `I=|A1+A2|²`.

For `V=0`, interference vanishes while single-slit diffraction remains: `I=.5 sinc(β)^2`. `d` cancels; hence these data contain no information about `d` when the envelope's other parameters are fixed. **Cannot infer slit separation from such observations.**

Bright point-slit fringes: `d sinθ=mλ`; paraxial fringe pitch approximately `Δx=λL/d = 3.192 mm`. Finite slit diffraction modifies the heights and exact locations of local fringe maxima; the point-slit ideal is not silently asserted for finite apertures. First envelope zero near `x=L tan(arcsin(λ/a))`.

Experimental Fresnel number `a²/(λL)≈0.00261`; scalar far-field is a reasonable **mathematical approximation for this idealized setup**, not a certificate of a manufactured optical assembly.

**Independent numerical check:** Wave formula and direct phasor superposition disagreed by at most `3.33e-16` across 1201 sample positions. The `d sinθ=mλ` point-slit maxima and envelope null have dedicated automated tests. This validates implementation consistency, not real hardware.

## 2. Electromagnetic-field relationship and limits
For an ideal monochromatic plane wave in free space with **known, calibrated time-averaged irradiance** `I_phys` (W/m²), field *amplitudes* obey:

`I_phys = 0.5*c*epsilon0*E_peak²`; `B_peak=E_peak/c`.

Therefore `E_peak=sqrt(2 I_phys/(c epsilon0))` and `B_peak=E_peak/c` **conditionally**. `src/physics.py` calculates this for an illustrative assumed 100 W/m². It does NOT measure instantaneous optical E(t), optical B(t), phase, vector polarization, or any photon wavefunction. An RGB camera alone lacks the spectral, calibrated irradiance, polarization, and phase information needed to infer these generally. The use of color gene weights in Ripple does not change this physical limitation.

Photon energy at wavelength λ is `E_photon=h*c/λ`. Energy is not intensity; expected counts require a detector efficiency, collection area, integration time, and background model.

## 3. Particle-like detection simulation
Two separate explicit models are used:

1. **Conditioned total photons**: sample screen indices from multinomial `(N,p_i)` with `p_i = I_i/sum(I)`. Every simulated detection lands at a single location. This is an ideal *probability-pattern Monte Carlo*, not a physical single-photon source/detector experiment.
2. **Fixed exposure bins**: use independent `n_i~Poisson(scale*I_i+dark)`, with programmed dark=2 and scales 18, 150, 1500 counts per full-intensity sample. The estimate `(n_i-dark)/scale` is clipped to `[0,1]` and such clipping biases signals. No sensor was calibrated.

The conditional photon total-variation means in 24 trials at N=(250,2500,25000,250000) were 0.18840, 0.05957, 0.01891, 0.00611. This supports statistical convergence. Random samples cannot support certainty about a single photon's path or arrival site.

## 4. Two-core neuronal interpretation (one original formula, separate opponent copies)
The baseline is one **unchanged** Ripple LIF reading intensity: `x=[I,0,0]`; it produces ordinary spikes but no explicit negative-event label.

The proposed **paired optical-contrast core** makes two *separate original LIF instances*, one ON and one OFF, driven by the signed log-intensity difference:

`c_t=log(observed_t+0.03)-log(observed_(t−1)+0.03)`;

`x_ON=clip(4 max(c_t,0),0,1)`;

`x_OFF=clip(4 max(-c_t,0),0,1)`.

For each sample, advance each core using four legal `dt=0.2 model second` steps. A signed vote is ON if ON spikes exceed OFF spikes, OFF if vice versa, else no change. This is an ON/OFF *functional analogy* to retinal pathways, not an anatomical model or a claim about biological development.

Original kernel state is independent for each clone. Its exact crossing times, adaptive rate estimate, reset and refractory duration remain intact. Fixed threshold and original adaptive feedback are both tested. One LIF versus two LIF requires different computation costs; no speed advantage is claimed.

The physically motivated statistical pre-gate estimates the variance of `c_t` via the **first-order delta method**, given assumed independently Poisson detector counts:

`σ²_c ≈ (scale*I_t+dark)/(scale² (I_t+0.03)²) + (scale*I_(t−1)+dark)/(scale² (I_(t−1)+0.03)²)`.

The proposed guard accepts `|c_t|>max(0.34,2σ_c)` and then provides full ON or OFF drive to the two locked neurons. `0.34` and 2 sigma are design choices, **not a statistically calibrated hypothesis test** (especially at low counts, clipping, and correlated frames). `I_t` in this variance equation is the observed photon-count estimate, **not the hidden clean model**; detector scale and dark count are supplied by the simulation. This gate is non-oracular but assumes a known detector calibration.

## 5. Real comparison against a non-neural arithmetic baseline
The 72 synthetic scenes use three visibility values (1,0.5,0), three Poisson-count scales (18,150,1500), eight seeds each, 121 scan samples, for `72*120=8640` scored consecutive changes. Truth labels are changes in the **known ideal synthetic** intensity exceeding ±0.34 log units. This truth is used *only for evaluation*.

**Fixed-threshold run (composite over all scenes):**

| Method | Truth-change directional recall | False alarm rate on quiet steps | Overall accuracy |
| --- | ---: | ---: | ---: |
| Single LIF, change in per-bin spike count | 25.04% | 53.24% | 43.82% |
| Twin unfiltered ON/OFF LIF | 85.21% | 71.66% | 36.04% |
| Twin 2σ-gated ON/OFF LIF | 46.24% | 2.88% | 90.23% |
| Plain arithmetic 0.34 contrast | 74.62% | 21.54% | 77.94% |
| **Identical 2σ arithmetic gate, no LIF** | **46.24%** | **2.88%** | **90.23%** |

**Critical negative result:** noise-gated LIF **exactly matches** its corresponding pure arithmetic decision rule on these frames. This is NOT an intelligence, precision, or computational advantage provided by spiking. At scale=18 the guarded variant detects **zero** truth-change events, while at scale=1500 directional recall rises to ~94.62% with ~0.76% false alarms. This is a strong sensitivity to detector photon rate. The ungated ON/OFF pair detects many changes but falsely signals under low count and incoherent scenes.

**Additional limitation:** all 1170 labeled changes in this particular thresholded test occur for coherent V=1 scenes; V=.5 and V=0 have zero target changes, so their change-recall values are **undefined**, not zero. They do contribute quiet-step false alarm measurements. We should test a broader synthetic geometry/phase/dynamic visibility distribution before selecting a production change-detector threshold.

Original adaptive LIF was separately tested with the same input; its output differed but did not establish superiority.

## 6. Inference of geometry from synthetic photons
Under **known** λ, a, L, V=1, φ=0, use the established multinomial likelihood `logL(d)=sum_i n_i log p_i(d)` with `p_i` normalized finite-slit intensity. Search d=0.18–0.42 mm in 0.0005 mm steps. On 40 held-out photon trials per budget, mean absolute simulated separation errors:

- 250 hits: 1.2625 µm
- 2500 hits: 0.3375 µm
- 25000 hits: 0.0875 µm

Grid quantization, known parameters, artificial data, and the fact that the true d is on the candidate grid materially simplify this experiment. A physical unknown-source inference would need nuisance-parameter fitting and systematic-error calibration. The visibility-zero likelihood is exactly flat in d and MUST return **not identifiable** instead of guessing.

## 7. Revisions and evidence boundaries
- Rejected: adding slit **intensities** rather than **complex fields** for coherent light (predicts no fringes).
- Rejected: mapping signed optical field values directly into Ripple RGB intensity; it requires a known optical phase reference and specialized detector. Use only intensity/contrast readouts.
- Rejected: labeling a single collected photon as having passed a specific slit from its screen coordinate.
- Rejected: calling the ON/OFF pair a biological neuron or a trainable intelligent model.
- Rejected: promoting the 2σ-gated spiking decision as superior to identical arithmetic gating, since output equality disproves added performance in the given study.
- Recorded browser bug: mislabeled photon-count display identifier; fixed and retested.

## Scientific references (equations and scope, not laboratory observations)
1. OpenStax University Physics v3, Double-Slit Diffraction: https://openstax.org/books/university-physics-volume-3/pages/4-3-double-slit-diffraction
2. OpenStax University Physics v3, Quantum wave functions: https://openstax.org/books/university-physics-volume-3/pages/7-1-wave-functions
3. OpenStax University Physics v2, Energy in electromagnetic waves: https://openstax.org/books/university-physics-volume-2/pages/16-3-energy-carried-by-electromagnetic-waves
4. EPFL Neuronal Dynamics, Leaky Integrate-and-Fire: https://neuronaldynamics.epfl.ch/online/Ch1.S3.html
5. NCBI review of ON/OFF signaling: https://pmc.ncbi.nlm.nih.gov/articles/PMC10016624/
6. NIST Single-Photon Sources and Detectors Dictionary (dark counts, shot noise): https://nvlpubs.nist.gov/nistpubs/ir/2023/NIST.IR.8486.pdf
