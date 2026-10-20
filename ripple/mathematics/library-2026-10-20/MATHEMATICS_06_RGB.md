# Ripple RGB Mathematics v0.1 — exact signal semantics and operational equations

**Classification:** [S] extracted from preserved Ripple source; [D] analytically derived; [N] newly engineered extension; [E] actually run/tested. This is **one tested mathematical extension** within the historical Ripple research program, **not** a conversion of every archived Ripple family or evidence of general artificial intelligence. Times are simulated model seconds, not sensor timestamps or AC frequencies. The input is display-encoded **sRGB** unless otherwise noted, not physical spectra.

## 1. Preserved source, unchanged [S]

- Reference `reference/ripple_core_reference.js`, archived JavaScript kernel SHA-256 `d75d4208e92f19623b127615bd52b4002e85d2c0a59b76471764b55a24294210`.
- Reference `reference/original_ripple_LOCKED.py`, inherited source-equivalent Python port SHA-256 `7f2f611cd8f1717c3d3dcae745dbd41efc37e24315d93878231db52eaf614f77`.
- Reference `reference/charlie_v2_LOCKED.py`, Charlie conductance source SHA-256 `bf96fc4dae90eeee65e3f895207c6c5714f736b1b9dbf09569e1c24a8b440f77`.
- `reference/TEN_LAWS_TESTABLE_SPEC.md` is an **unchanged** older Kokoro mathematical-operator specification, not a fully implemented physics of the Higher Laws.
- The JS/Python v0.1 sources were compared by actually computing 180 identical timed samples in their respective runtimes; output states agreed within `2e-12` on every checked field.

Original v0.1 source [S]:

\[
D=2R+1.2G-1.4B,\quad \tau_v\frac{du}{dt}=-u+D,\quad \tau_v=0.5.
\]

Adaptive threshold, reset, refractory (0.1 model seconds), events, and firing-rate filter are preserved *inside each frozen neuron*. We do not replace `D` with a learnable matrix.

## 2. An exact mathematical limitation and lossless coordinate response [D, E]

For `A=(0.6,0,0)` and `B=(0,1,0)`, the original scalar `D_A=D_B=1.2`; the original neuron cannot distinguish these as long as its initial state and subsequent scalar drive are the same. A single scalar is a rank-one projection of 3D RGB, with a two-dimensional null space.

To preserve all three sRGB dimensions while expressing meaningful differences, decode encoded components \(c\) to linear light \(L(c)\):

\[
L(c)=\begin{cases} c/12.92,&c\le 0.04045\\ ((c+.055)/1.055)^{2.4},&c>0.04045.\end{cases}
\]

For linear components \(r,g,b\), compute the *new engineered invertible basis*:

\[
Y=0.2126r+0.7152g+0.0722b,\quad p=r-g,\quad q=b-(r+g)/2.
\]

The inverse follows exactly from the coefficient sum 1. With \(m=(r+g)/2\):

\[
m=Y-\tfrac12(0.2126-0.7152)p-0.0722q,\\
r=m+p/2,\quad g=m-p/2,\quad b=m+q.
\]

The 3×3 linear transformation is full-rank; this is **not a newly discovered color science law**, just a useful invertible basis combining established luminance with chosen opponent-style coordinates. Numerical verification [E]: max componentwise inverse error was `2.50e-16` across 2,000 seeded independent input samples.

**Important:** The single scalar D is still processed by the original neuron. The new math adds independent signal dimensions rather than editing the old weights.

## 3. Temporal contrast and signed events [N, E]

With \(Y_k\) the decoded luminance, numerical floor \(\epsilon=0.002\) and gain scale \(s=0.35\):

\[
\ell_k=\log\left(\frac{Y_k+\epsilon}{Y_{k-1}+\epsilon}\right),\quad
\ell^+_k=\max(0,\ell_k),\quad\ell^-_k=\max(0,-\ell_k).
\]

The first sample initializes the previous luminance so its synthetic temporal change is zero. Each positive/negative feature is normalized and clipped to [0,1] *only when it enters* an inherited Ripple v0.1 numeric slot. The **unclipped** signed log contrast and an explicit saturation flag remain in telemetry. This is an engineering contrast rule on RGB-derived luminance. It does not recreate the exact per-channel log-contrast gate from archived Delta v3.0.

## 4. Two timescales, not a new fictitious neuron [D, N, E]

\[
f_{k+1}=f_k+(1-e^{-\Delta t/\tau_f})(Y_k-f_k),\quad
s_{k+1}=s_k+(1-e^{-\Delta t/\tau_s})(Y_k-s_k),\quad \tau_f=0.12,\tau_s=1.2,
\]

and \(z_k=f_k-s_k\). Under a continuous-time small-signal approximation, the corresponding transfer function is

\[
H(j\omega)=\frac{1}{1+j\omega\tau_f}-\frac{1}{1+j\omega\tau_s}.
\]

Because \(H(0)=0\) and high-frequency gain also tends to zero, this is a band-pass-like *difference of low-pass filters*. It is not an optical frequency detector by itself. Positive/negative \(z\) are routed to separate frozen Ripple neurons, preserving their sign until input-slot encoding. Actual filtered states influence neuron voltages.

## 5. Nine authentic Ripple instances and one authentic Charlie [S, N, E]

One exact original input path + four signed pairs:

1. `original`: raw encoded RGB to one unchanged Ripple v0.1 unit (control).
2. `temporal_on` / `temporal_off`: positive and negative relative luminance changes.
3. `rg_plus` / `rg_minus`: positive and negative \(p=r-g\).
4. `bg_plus` / `bg_minus`: positive and negative \(q=b-(r+g)/2\).
5. `scale_plus` / `scale_minus`: positive and negative \(z=f-s\).

The derived channels are **typed mathematical features**, not claims that those virtual slots contain actual red light. Each routed value goes to the frozen source neuron's first numerical slot. The source's spike timing, membrane and homeostasis *actually execute*; all states are individually logged. The four signed readouts are differences in original neuron **drives**, not an invented trained readout:

\[
O_k=\tfrac12[D_k^{(+)}-D_k^{(-)}].
\]

A new, causal cross-kernel link uses *prior-tick* original Ripple membrane states. For the four distinct opponent/temporal/scale pairs \(P\):

\[
q_{k+1}=\frac{1}{4}\sum_{(a,b)\in P}(u_a[k]-u_b[k]).
\]

On the next tick, pass \(\max(q_k,0)\) and \(\max(-q_k,0)\) into **existing** Charlie v2 excitatory and inhibitory drive slots, then execute Charlie's own conductance differential equation. The state-dependent transfer is delayed one complete tick. This link is disabled as a true ablation if requested; the frozen Ripple/Charlie mathematical kernels do not change. Signed channels are clipped **only at the last input-slot boundary** when magnitude exceeds one. A separate future stage may transmit native typed signed voltages directly, with source-specific units and calibration; this release does not silently bypass the original API.

## 6. Innovation / Higher Laws mathematical cross-reference

The archived Kokoro higher-law document uses **provisional names** and explicitly classifies each mapping as an engineering analogy, not an independently established law of nature. Two ideas are made operational here:

- **Consequential Echo**: the two nonzero-memory filters carry past observations into *future original-neuron states*; the Charlie link carries previous-tick Ripple voltage evidence into future conductance.
- **The Body's Truth**: a modest, explicitly *empirical numerical discrepancy indicator*: \(v_{k+1}=0.97v_k+0.03(Y_k-Y_{k-1})^2\) and \(S_k=(Y_k-Y_{k-1})^2/\max(v_k,10^{-6})\). Crossing `S>4` makes a logged `novelty_alarm`. **This is NOT a chi-square-calibrated normalized innovation statistic**, no likelihood model is estimated, and no inference of physical sensor reliability is justified.

Other archived Kokoro operators remain **mathematical design candidates**, not decorative installed components: Bayesian probability update, longer-run action consistency, controlled causal intervention, held-out error change, actual physical simulation-to-reality loss, measured energy budget, information gain for experiment choice, and sample-age freshness. Their implementations should be enabled only when a real data/task interface justifies the equation.

## 7. Experimental results [E] — what actually happened

- The 21 new Python tests passed, including **one actual Node.js vs Python 180-tick source parity test**; three local HTTP control tests, frozen-source SHA checks, sign routing, zero-change control, source-state effect, knockout, and snapshot continuity.
- Across five purposely constructed red-versus-green color pairs, the original scalar D collided exactly to numerical tolerance, but the extended opponent readout differed in all five cases. The numeric differences were recorded in `results/study.json`.
- Four synthetic input sequences (80 steps each) compared full channels against original-only control in `results/study.json`. `gray` produced zero opponent and temporal change; `chromatic_collision` had original-drive range zero but opponent-readout range >0. Do not compare total spikes as a skill metric when the two cases contain different numbers of neurons.
- The true Charlie source's inhibitory conductance increases one step after a negative Ripple-channel state; removing the link removes that effect. Original source bytes are preserved.
- This demonstrates an **information-preserving representation and a causally connected numerical channel system**. It has not established intelligence, downstream task accuracy gains, stable high-order recurrent networks, physical sensor behavior, Android APK operation, or Dell machine performance.

## 8. Source research and standards

- **Historic Ripple source**: included frozen JS/Python v0.1 and Charlie v2, with SHA-256.
- **Historic Ripple atlas**: `Ripple_Mathematical_Atlas_107_Archives_Executable_v1.zip` and its `RIPPLE_MATHEMATICAL_ATLAS.md`; prior source survey was 107 archives, 101 byte-distinct. The current build is a narrow implementation based on those results, not a 107-engine monolith.
- **Historic Kokoro**: `TEN_LAWS_TESTABLE_SPEC.md` included unchanged, with its explicit provisional-canon caveat.
- **W3C CSS Color Module 4**, sRGB transfer curve and linear-light representation, https://www.w3.org/TR/css-color-4/ .
- **W3C WCAG relative luminance**, https://www.w3.org/WAI/WCAG21/Understanding/relative-luminance.html .
- **EPFL Neuronal Dynamics**, LIF dynamics/filter equivalence and adaptations, https://neuronaldynamics.epfl.ch/online/Ch1.S3.html .

### Local GUI verification [E]

Headless Chromium clicked the running interface, changed the three RGB sliders, ran an 80-step sequence, rendered 9 source-neuron rows and the Charlie conductance state, and produced desktop/mobile screenshots without page-script errors. **The sandbox blocks direct Chromium navigation to local HTTP**, so this UI test used a clearly marked **test-only Python-to-local-server transport bridge**. The app server was exercised separately by direct HTTP integration tests. Neither route establishes a physical phone/Dell deployment. See `results/browser_check.json`.

## 9. Next mathematical experiments — specific, not silently implemented

1. Preserve and transmit **typed signed channel values** between different Ripple kernels without saturation; compare information loss with the existing legal API.
2. Add the original Delta v3 log-contrast processor, Daughter v3.1 cascade and Mycelium threshold controller as *isolated and explicitly clocked original-source branches*; verify JavaScript port equivalence before coupling.
3. Build a mathematical **Colony queue scheduling** workload on actual emitted events; measure throughput, work conservation and finite resource cost, not planted cells.
4. Study whether real **Ripple Lab finite-volume transport** is appropriate for finite computational credits. Do not treat arbitrary evidence or membrane voltage as mass-conserved without derivation.
5. Use the **Ripple Repair finite-field/checkpoint** methods to protect durable recorded states and prove byte restoration; do not label a numerical redraw 'regeneration'.
6. Use held-out tasks (time-coded stimulus classification, delayed signal prediction, queue scheduling), controls and ablations to evaluate functional gain; keep outcomes of failed candidates.

### Reproduce

```text
python -m unittest discover -s tests -v
python experiments.py --out results/new_study.json
python ripple_rgb_math.py --fixture chromatic_collision --steps 80 --output results/new_trace.json
python server.py --port 8774
```

The Python layer requires only the standard library; Node.js is needed for the archived JS/Python reference parity test. Local browser `http://127.0.0.1:8774` controls computations through the Python server. The parent historical projects are not modified or replaced.
