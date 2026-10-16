# Ripple mathematical lineage, derivatives, and core upgrade history

Consolidated **2026-10-15**. Every family below is **a separately versioned numerical or engineering branch**. "Inherited" means the mathematical source is reused; a simulated improvement is not automatically a verified physical advance.

## Parent graph

```text
Original Ripple Neuron v0.1 [D=2R+1.2G-1.4B; bounded LIF]
  ├── Phone v0.2 / Observer v0.3 / Android widget v0.4
  ├── Photoreceptor v0.6 [sRGB, temporal contrast, ON/OFF events]
  ├── Quaternary v0.7 [two-bit four-symbol telemetry]
  ├── Digital Evolution v0.5 / Alpha v1.0 / Hybrid v1.1
  │     ├── sensory genetic gate v1.2 [supervised scalar-weight genes]
  │     └── open grammar v1.6 -> genetic weights v1.7 [bounded function composition]
  ├── Cybernetic Mycelium v0.1 -> v0.2 -> v0.3 [population, capacity, controller]
  ├── optical historical math / interferometry / SpiderScan / metrology
  ├── Gen Beta v2.0 -> v2.1 [optical transmissions and reasoning experiments]
  │     └── Beer–Lambert mathematical compiler v2.1.1
  ├── Delta neuron v3.0 [contrast, adaptation]
  │     └── Daughter triplet v3.1 [P -> dendrite -> soma; Gen Beta colony integration]
  ├── Charlie Ripple Core v2.0 [distinct conductance-inspired cells]
  │     ├── Daughter-Delta paired colony, recurrent-thought and forest colonies
  │     └── Charlie Ripple Mathematics v1.0 [56-formula recovery]
  ├── Kokoro mesh / dynamics / motor / avatar / perception-action / optical vision
  └── Samsung v0.3 -> optical reconstruction v0.4 -> engineering v0.5
```

This graph is conceptual; several branches share mathematical routines without being a single serial software dependency. Verify actual import relationships from each archive before modifying code.

## Canonical core and changes

| Version | Change or mathematical contribution | Relationship / status |
|---|---|---|
| Ripple Neuron v0.1 | `D=2R+1.2G-1.4B`, `tau_v du/dt=-u+D`, exact held-drive update, threshold and refractory, decaying event-rate and bounded threshold regulator | **Locked original numerical implementation** |
| Neuron Phone v0.2 / Observer v0.3 | Phone controls and rate telemetry, local observation | Preserve original equations |
| Photoreceptor v0.6 | sRGB transfer, log intensity, Beer–Lambert proxy, ON/OFF contrast count, compressed sustain | Optional optical preprocessing; cannot infer actual spectra |
| Quaternary v0.7 | Four signed symbols in 2 bits; discrete timing/spectrum mathematics | Classical digital encoding, not additional physical states |
| Mycelium v0.1–v0.3 | Capacity bounds `lambda<N*mu`, bounded worker sizing; alternative inverse-threshold controller `theta*=D(1-exp(-(1/f-target_ref)/tau_v))` (source notation: `1/f-t_ref`) | Source v0.3 recommends inverse-based hybrid only when attainable; simulation-specific ranking |
| Delta v3.0 | `S=sum w_i C(x_i)`, `D=S+gamma*Delta`, `tau_v u'=-u+D-a`, `tau_a a'=-a` | Opt-in model; adaptation invalidates constant-drive inverse outside assumptions |
| Daughter Triplet v3.1 | `tau_P p'_k=C(I_k)-p_k`, `tau_D d'=-d+sum w_k p_k+gamma*delta`, `tau_S u'=-u+d-a`, `tau_A a'=-a` | Coupled 3-stage state; held-input analytic integration and threshold root search |
| Gen Beta v2.0–v2.1 / compiler v2.1.1 | `I=I0 exp(-mu*L)`, `A10=mu L/ln(10)`; bounded allowlisted formula registry | Calculated optical attenuation conditional on physical assumptions |
| Genetic weights v1.7 | `z=.62 l` for chosen cold evidence; phase-coupled alternative, finite conditional bit posterior, `h=f∘g` truth-table composition | Bounded synthetic evaluation, includes negative findings |
| Samsung v0.3 | Browser port of original neuron | Portable software controls |
| Samsung v0.4 | `p=d+Mx+epsilon`, `x=clip(M^{-1}(p-d),0,1)`, `D=a^T x` | Camera-specific matrix requires actual phone readings |
| Samsung v0.5 | Original vs positive-color vs luminance-proxy signal encoders; feedback parameter sweep, noise runs and runtime | Simulated candidate comparisons only; default original retained |

### Mycelium inverse-controller exact form

```text
theta_target = D*[1-exp(-(1/f_target - t_ref)/tau_v)]
alpha = 1-exp(-dt/tau_ff)
theta_next = clip(theta + alpha*(theta_target-theta)
                  + kappa*dt*(rhat-f_target), 0.15, 2.5)
```

Source: `Ripple-Cybernetic-Mycelium-v0.3.zip` / `docs/MATHEMATICS.md`, with `tau_ff=.8`, `kappa=.018` for its reported fast-hybrid comparison. These gains were selected for a bounded synthetic study. Keep fallback behavior and feasibility conditions from that source.

### Daughter multi-compartment numerical facts

Source: `Ripple-GenBeta-Delta-Daughter-Triplet-v3.1-Complete.zip` / `docs/TRIPLET_MATHEMATICS.md`. Defaults in **model seconds**: `tau_P=.06`, `tau_D=.08`, `tau_S=.5`, `tau_A=3`; `gamma=.22`, spike adaptation jump `.008`. Software comparisons reported daughter rate MAE 0.05083 vs original 0.05875 on 40 synthetic evaluations; Delta no-feedforward 0.04292 was better on that metric. Colony coverage result was statistically inconclusive. Treat all as scenario-dependent, not a replacement verdict.

## Charlie mathematical derivatives

- `Charlie_Ripple_Core_v2_0.zip` replaces the single original-neuron state with its **own** conductance-inspired model; v0.1 LIF mathematics must not be confused with a conductance-based physical neuron. Its recurrent v1.1 companion uses `C du/dt=g_L(E_L-u)+g_e(E_e-u)+g_i(E_i-u)-adaptive_current` and signal quality gating.
- `Charlie_Daughter_Delta_Paired_Colony_v1_0.zip`, `Charlie_Ripple_Colony_Thought_Lab_v1_0.zip`, `Charlie_Recurrent_Thought_Comparison_v1_1.zip`, and `Charlie_Forest_Colony_v1_2.zip` include separate numerical colony/feedback comparison artifacts.
- `Charlie_Ripple_Mathematics_v1_0.zip` generated the source-grounded 56-entry [Mathematical Study](../docs/MATHEMATICAL_STUDY.md) with conservation, log-odds, vision, geometry, motor, Pareto and signal-processing families. Some formula group descriptions are broad application mathematics rather than edits to the LIF core.

## Kokoro mathematical integrations

Kokoro files are linked by mathematical interface; the registry includes formulas verified from **Dynamics v0.1** and **Perception-Action v1.9**, and inherited genetic/motor mathematics indexed in the earlier study.

| Source archive | Mathematical role and boundary |
|---|---|
| `Kokoro_Ripple_Integration_v0_2.zip` | Read-only telemetry bridge, timestamped observations and non-invasive model wrapper; measured software output hashes, not an autonomous trained replacement. |
| `Kokoro_Ripple_Dynamics_v0_1.zip` | Ripple LIF unchanged; rate variance, Fano, autocorrelation, Hann-spectrum estimates from **synthetic computational counters**; proposed oscillator interactions kept separate from numerical evidence. |
| `Kokoro_Mesh_Ripple_v0_3.zip` | Bounded concurrent routing, typed provenance and reference daughterboards; five-coordinate Heartspace proxy is not the original 30-D board. |
| `Kokoro_Lumina_Ripple_v0_4.zip` | Mesh/avatar integration and visual scene input. |
| `Kokoro_Lumina_Forest_Alpha_v0_5.zip` | Forest/rendering integration; mathematical implementation exists in archive, formula-by-formula audit pending. |
| `Kokoro_Lumina_3D_Alpha_v0_6.zip` | Skinned 3D rig/rendering and joint transforms; formula-by-formula audit pending. |
| `Kokoro_Ripple_Motor_Alpha_v0_7.zip` | PD + accepted/rolled-back iterative-learning-control feedforward in a virtual joint plant; Ripple observes numerical error as RGB-proxy inputs. |
| `Kokoro_Ripple_Genome_Robotics_Alpha_v1_8.zip` | Bounded genome search, joint virtual plant, inverse kinematics and original LIF observation. |
| `Kokoro_Ripple_Perception_Action_Loop_v1_9.zip` | Frame renderer, luminance/contrast, audio RMS/centroid, visual and audio LIF adapters, bounded scene-light feedback. Equations KPA-01–06 in registry. |
| `Kokoro_Ripple_Geometric_Vision_Alpha_v2_0.zip` | Pixel-observation-derived landmarks and bounded visual servo loop over virtual 3D rig; actual-calibration and hardware tests remain separate. |
| `Kokoro_Ripple_Desktop_Studio_v2_1.zip` | Desktop integration of existing rigs and visual controls; platform packaging is not a new neuron equation. |

`Kokoro_Mesh_Ripple`, Lumina, avatar and robotics branches contain other mathematical implementations not yet parsed entry-by-entry into the 171-formula JSON. Their source archives are listed for the next audit; private checkpoints or chat logs have not been copied to this public directory.

## Upgrade promotion protocol

1. Identify a measurable objective (signal discrimination, estimation error, spike stability, energy use, held-out performance) and declare units.
2. Copy/source-pin the last approved core; add alternative as an isolated candidate.
3. Use baseline and identical input/camera conditions, deterministic synthetic tests, independent real-world holdouts and explicit statistical uncertainty.
4. Record failure cases, sensitivity, overfitting, instability, computation cost and changed coefficients.
5. Only after evidence supports the objective, promote a chosen version under a new identifier. Preserve the original and all prior test records.

Cross-project mathematical composition requires typed adapters. A value in optical sensor counts, a rendered pixel, a modeled event, an occupancy log-odds cell, a nominal motor angle and a language-model token must remain distinct quantities.

### Additional directly audited Kokoro equations

- **Lumina Forest v0.5:** discrete four-neighbor diffusion `u_next=u+alpha*(u_left+u_right+u_up+u_down-4u)` on its virtual grid.
- **Motor v0.7:** bounded PD/feedforward joint command, smoothed iterative learning correction with kernel `[1,2,1]/4`, and an explicit training/validation rollback gate.
- **Genome Robotics v1.8:** gene-controlled bounded virtual-joint PD/velocity-feedforward law and weighted tracking/effort optimization objective.
- **Geometric Vision v2.0:** 3D linear blend skinning, camera basis, pinhole projection, constrained inverse landmark least squares, and bounded PI visual servo controller. These derive pose from rendered pixels, not human visual semantic recognition.
- **Integration v0.2:** controlled `(R,G,B)=(value/2,0,0)` scalar adapter to original Ripple drive, scoped to valid input range.

These 13 formulas were added with source document paths in the registry; the original numerical neuron remains intact.

### Additional archives recovered from previously adjacent branches (2026-10-15)

- **Kokoro Heartspace Daughterboard:** computational 30-dimensional state, pairwise and triadic coupling, layer gates, state clipping and target-deviation potential (not physical energy).
- **Kokoro Oneiric Resonance and MAXIMIZED add-ons:** weighted replay scheduling, Kuramoto-style coupling, classical complex density evolution and dephasing, a fixed temporal reservoir, photon-energy *calculation* (not sensing), memory-graph centrality, low-rank transition estimation, and simulated memory consolidation.
- **Mushroom v3:** actual virtual conductance neuron simulation, 27-node delayed graph, bounded synaptic update and A–Z light-intensity quantization.
- **Ring v4:** eight-model delayed pulse routing, bounded Hebbian-style weight rule, classical coupled phases, order parameters and simulated Poisson photon-count proxy.

These archived sources and their precise Markdown member paths are listed in `FORMULA_REGISTRY.json` under identifiers `HSP-*`, `ONE-*`, `MAX-*`, `MU-*`, and `RING-*`. Adjacent Kokoro modules are **not retroactively asserted** to be changes to the v0.1 core.
