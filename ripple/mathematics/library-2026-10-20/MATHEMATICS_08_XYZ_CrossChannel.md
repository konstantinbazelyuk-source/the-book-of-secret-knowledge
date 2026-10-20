# Ripple XYZ Cross-Channel Mathematical Memory v0.2

## Evidence boundary

This is a **source-preserving software extension** to Ripple Memory Wave Mathematics v0.1, which itself preserves the original Ripple v0.1 and Charlie v2 conductance models. No conventional LLM, unrelated generic neuron, botanical growth model, or nonfunctional 3D geometry replaces those models.

XYZ means **three numerical coordinates chosen and typed explicitly**. The default XYZ *does not* mean physical depth, calibrated camera location or magnetic-field location. The archived MUSHROOM v3 uses X/Y camera tile and Z optical Gaussian scale; the archived Lumina/Kokoro motor and geometric vision use actual authored 3D mesh/joint coordinates and camera projections; the archived FieldSphere coordinates are designed positions for magnetic sensor acquisition, without validated physical installation. These are separate mathematical coordinate semantics.

## 1. Authentic inputs

Run the unchanged ancestor `RippleRGBMathematics.step(encoded_rgb)` and the real `RipplePointSystem` event detector. Preserve exact model timestep k and original `time_model_s`. Each source result contains neuron membrane potential, conductance, drive, generated event counts, signed temporal and opponent readouts, and the encrypted landmark-event ledger.

Default 3D vector:

\[
\mathbf p_k=(x_k,y_k,z_k)=(r_{temporal_signed,k},\ r_{rg_signed,k},\ r_{bg_signed,k})\in\mathbb R^3.
\]

Here the components are **dimensionless numerical outputs of real Ripple model updates**, and `t_k` is a separate numerical time parameter. No value is manufactured if the required inherited channel is unavailable.

Alternative typed axes:

- `neuron_xyz`: (original Ripple membrane potential, original Charlie conductance-neuron membrane potential, Ripple fast-minus-slow signed response);
- `color_xyz`: (linear-light Y, linear-light R−G, B−(R+G)/2), an invertible transform of linear sRGB, NOT physical XYZ tristimulus or physical 3D geometry;
- `scale_xyz`: (signed R−G, signed blue opponency, fast-minus-slow response);
- `delay_xyz`: a single Ripple signal embedded as (s[k], s[k−lag], s[k−2lag]); initial `2lag` samples have no complete delayed coordinates and are **omitted**, not replaced with fake zeros.

The separate incoming RGB and original locked drive `D=2R+1.2G−1.4B` remain available in the parent trace. The unchanged ancestor's nine filtered Ripple channels and delayed Charlie conductance response continue to execute. This creates a 3D *state-space trajectory* without replacing the neurons themselves.

## 2. Trajectory mathematics

Recorded episode `P={ (k_i,t_i,p_i,L_i,spikes_i) }` consists of finite successive vectors with strictly increasing sample indices and references `L_i` to original point-event hashes. A late-confirmed extremum references its **actual confirmed tick** plus its authenticated event object containing `point_step`, so it is not silently shifted forward in time.

Arc length, net displacement, and approximate mean speed:

\[
L=\sum_{i=1}^{n-1}\|p_{i+1}-p_i\|_2,\qquad
R=\|p_n-p_1\|_2,\quad \bar v=L/(t_n-t_1).
\]

Area-vector accumulator around first point (oriented polygonal surface, not physical area):

\[
\mathbf A=\frac12\sum_{i=2}^{n-1}(p_i-p_1)\times(p_{i+1}-p_1).
\]

Signed triple product of **three consecutive displacement vectors**, sensitive to 3D handedness:

\[
V_{path}=\frac16\sum_i \Delta p_i\cdot (\Delta p_{i+1}\times\Delta p_{i+2}).
\]

This diagnostic is algebraic. It is not a true enclosed physical volume or a biological memory property.

Lagged correlation for chosen axes X,Y:

\[
\rho_{XY}(\ell)=\operatorname{corr}(X_{k+\ell},Y_k).
\]

These reflect observed time relationships in the software, not causal effects. Undefined correlation is `null` when variance is zero; no division by fabricated noise.

## 3. Complete trajectory matching

Two 3D episodes in the same coordinate convention can be compared with a bounded **dependent multivariate dynamic time warping** recurrence:

\[
C_{ij}=\|p_i-q_j\|_2 + \min(C_{i-1,j},C_{i,j-1},C_{i-1,j-1}),
\qquad d=C_{nm}/\max(n,m).
\]

The Sakoe–Chiba-style warping band is `max(|n-m|, ceil(.35 max(n,m)))`. Baselines: independent DTW on each axis separately; marginal means-only distance discarding time-order and cross-channel pairing. A different coordinate definition or delay value has infinite mismatch distance rather than spuriously matching incomparable measurements. This is an engineering application of established multivariate time-series matching, not a new mathematical theorem. See:

- Shokoohi-Yekta et al., *Generalizing DTW to the multi-dimensional case requires an adaptive approach* (2017), https://pmc.ncbi.nlm.nih.gov/articles/PMC5668684/
- Shifaz, Pelletier, Petitjean & Webb, *Elastic similarity and distance measures for multivariate time series*, 2023, https://doi.org/10.1007/s10115-023-01835-4
- Casdagli, Eubank, Farmer & Gibson, *State space reconstruction in the presence of noise*, 1991, https://doi.org/10.1016/0167-2789(91)90222-U

The time-delay XYZ coordinate is an application of delay embedding, **not a claim** that these synthetic data satisfy Takens' generic smooth/noiseless hypotheses.

## 4. Encrypted memory remains operational

At every source tick, the unmodified parent encrypts each accepted fluctuation landmark in an AES-256-GCM ledger. At each episode boundary (16 to 300 source samples), the new engine stores the full XYZ vectors, time indexes, model spike counts, and hashes of relevant original event records in **a third AES-256-GCM ledger**. The preserved wave-memory engine also encrypts its original one-dimensional wave episodes separately. Each ledger uses fresh scrypt key derivation parameters and authenticated nonce/chain construction from the preserved source.

Recovery requires correct authentication of *all three* ledgers, agreement of memory and event counts, and all stored XYZ landmark hashes to match an actual authenticated original point event confirmed at the same tick. No physical sensor recording or public encryption key is inferred from the fluctuating signal itself. The passphrase is user-selected; mathematical fluctuation is not an encryption key.

**Storage boundary:** Plaintext results returned to the localhost UI for exploration are not themselves encrypted. A user must export the encrypted session to retain a protected durable copy. UI controls can reset unsaved data. Session passphrase is never written to project test files.

## 5. Independent code and actual controls

- `xyz_memory.py`: imports/executes preserved Ripple v0.1, Charlie v2, multichannel and cipher source. Converts only existing numerical data to typed 3D vector samples; calculates path metrics and trajectory retrieval; authenticates cross-ledger references.
- `server.py` and `index.html`: HTTP inputs actually change running source neuron calculations, accumulate XYZ samples, rotate *only the display projection*, select mathematical modes, select stored waves, search and export/import encrypted records.
- `tests/`: direct mathematical identities, timing, linked source states, refusal of bad input and incomplete/tampered ledgers, real HTTP flow, origin rejection.
- `run_study.py`: a preregistered controlled deterministic study using the previous release's actual synthetic inputs.
- `reference/`: byte-identical selected historical source documents and code for MUSHROOM XYZ, Kokoro Lumina/Geometric Vision/Motor, FieldSphere, Ring, and Perception–Action Loop. These are **read-only mathematical references**, not fully invoked 3D geometry/sensor systems.

## 6. What the evidence does and does not establish

`results/study.json` records 20 actual original-neuron software simulation executions (5 coordinate selections × 4 source fixtures × 128 steps), 15 cross-stimulus distance comparisons, and a mathematically constructed control pair.

Control pair: a forward planar loop and reversed planar loop have **the same mean coordinate per axis** (marginal baseline 0), but opposite oriented area (`+1` vs `-1` in Z in the full loop representation) and joint 3D DTW `0.565685...`. This shows a causal mathematical difference due to ordering under declared conditions, **not learned intelligence or future generalization**.

Outstanding: real sensor measurements, meaningful action-policy learning, automatic reconstruction after memory failure, multi-worker sparse graph coupling using old MUSHROOM/Ring kernels, physical Android and Dell installation / sustained benchmarks, GPU tests, and trained perceptual semantics. Different coordinate conventions are *supported* as separate adapters; there is no hidden equivalence between spatial meters, color features, and membrane state.
